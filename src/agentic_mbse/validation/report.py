"""The `validate --json-report` file: every level's full result, untruncated (Item 3 design D6).

Schema `validate-report/v1`. One file per run, levels in run order, written after the run,
including crashed levels. Each level carries its structured issues (with how each is shown),
the issue strings that have no structured form (`unstructured`), its warnings, the results it
folded into a summary, and L6's full subset profile. The text output keeps its truncation.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

import agentic_mbse
from agentic_mbse.sysml.types import ValidationCode, ValidationIssue
from agentic_mbse.validation.common import AggregatedResult, QualityCheckResult

REPORT_SCHEMA = "validate-report/v1"


def _issue(issue: ValidationIssue) -> dict[str, Any]:
    return {**issue.model_dump(mode="json"), "display": issue.severity.value}


def unstructured_issues(result: QualityCheckResult) -> list[str]:
    """`issues` minus each structured issue's string, as a multiset, in `issues` order.

    `add_issue` appends `str(issue)` for every structured issue, so what remains is exactly
    what a level appended as a bare string.
    """
    structured = Counter(str(issue) for issue in result.structured_issues)
    remaining: list[str] = []
    for text in result.issues:
        if structured[text]:
            structured[text] -= 1
        else:
            remaining.append(text)
    if structured.total():
        raise ValueError(
            f"Level {result.level}: structured issues missing from issues: {sorted(structured)}"
        )
    return remaining


def level_status(result: QualityCheckResult) -> str:
    if any(issue.code == ValidationCode.LEVEL_CRASHED for issue in result.structured_issues):
        return "crashed"
    return "passed" if result.success else "failed"


def _level(result: QualityCheckResult) -> dict[str, Any]:
    return {
        "level": result.level,
        "name": result.level_name,
        "status": level_status(result),
        "metrics": result.metrics,
        "issues": [_issue(issue) for issue in result.structured_issues],
        "unstructured": unstructured_issues(result),
        "warnings": result.warnings,
        "summarized": [_issue(issue) for issue in result.summarized],
        "profile": result.report_detail,
    }


def build_report(
    aggregated: AggregatedResult, command: dict[str, Any], exit_code: int
) -> dict[str, Any]:
    """The report for one finished run. `command` records path, mode, level and target override."""
    return {
        "schema": REPORT_SCHEMA,
        "agentic_mbse": {
            "version": agentic_mbse.__version__,
            "source": str(Path(agentic_mbse.__file__).resolve().parent),
        },
        "command": command,
        "run_info": {
            "constraint_extractions": aggregated.constraint_extractions,
            "wall_time_s": round(aggregated.wall_time_s, 3),
        },
        "overall_success": aggregated.overall_success,
        "exit_code": exit_code,
        "pass_notes": aggregated.pass_notes,
        "levels": [_level(result) for result in aggregated.results],
    }


def write_report(path: Path, report: dict[str, Any]) -> None:
    """Write `report` to `path` as indented JSON. Raises OSError if the file cannot be written."""
    path.write_text(json.dumps(report, indent=2, default=str) + "\n", encoding="utf-8")
