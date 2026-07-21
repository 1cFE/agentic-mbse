"""CLI handlers for 'agentic-mbse pm' subcommands.

Registers nested argparse sub-subcommands for all PM operations
(D4.4 AP-7). Each handler finds the project root, extracts arguments,
calls the corresponding operations.py function, and returns an exit code.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from pydantic import BaseModel

from agentic_mbse.pm.types import ParseWarning
from agentic_mbse.validation import EXIT_FAILURE, EXIT_SUCCESS

EXIT_USAGE = 2


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def find_project_root() -> Path | None:
    """Walk up from CWD to find a project root.

    Looks for work/BACKLOG.md (primary) or .claude/ (fallback).
    Returns None if neither found.
    """
    from agentic_mbse.cli import find_project_root as _find

    return _find()


def _print_warnings(warnings: list[ParseWarning]) -> None:
    """Print parser warnings to stderr."""
    for w in warnings:
        print(f"Warning: {w.file}: {w.message}", file=sys.stderr)


def _parse_json_arg(value: str, label: str) -> tuple[dict | list | None, str | None]:
    """Parse a JSON string argument.

    Returns (parsed_value, None) on success, or (None, error_message) on failure.
    """
    try:
        return json.loads(value), None
    except json.JSONDecodeError as e:
        return None, f"Invalid JSON for {label}: {e}"


def _validate_json_list(
    raw_json: str, label: str, model_cls: type[BaseModel]
) -> tuple[list | None, int | None]:
    """Parse JSON string, validate as list of Pydantic models.

    Returns (validated_list, None) on success, or (None, exit_code) on failure.
    """
    parsed, err = _parse_json_arg(raw_json, label)
    if err is not None:
        print(f"Error: {err}", file=sys.stderr)
        return None, EXIT_USAGE
    if not isinstance(parsed, list):
        print(f"Error: {label} must be a JSON array", file=sys.stderr)
        return None, EXIT_USAGE
    try:
        validated = [model_cls.model_validate(item) for item in parsed]
    except Exception as e:
        print(f"Error: Invalid {label} data: {e}", file=sys.stderr)
        return None, EXIT_USAGE
    return validated, None


def _dispatch(args: argparse.Namespace, fn, **kwargs) -> int:
    """Common dispatch: find root, call operation, handle result."""
    project_root = find_project_root()
    if project_root is None:
        print(
            "Error: Not inside a project (no work/BACKLOG.md found)",
            file=sys.stderr,
        )
        return EXIT_FAILURE

    result = fn(project_root, **kwargs)
    _print_warnings(result.warnings)
    print(result.message)
    return EXIT_SUCCESS if result.success else EXIT_FAILURE


# ---------------------------------------------------------------------------
# Lazy operation imports — thin wrappers to avoid importing PM at module load
# ---------------------------------------------------------------------------


def _op_close_item(project_root, wi_id):
    from agentic_mbse.pm.operations import close_item

    return close_item(project_root, wi_id)


def _op_add_insight(project_root, **kwargs):
    from agentic_mbse.pm.operations import add_insight

    return add_insight(project_root, **kwargs)


def _op_save_research(project_root, **kwargs):
    from agentic_mbse.pm.operations import save_research

    return save_research(project_root, **kwargs)


def _op_promote_requirement(project_root, **kwargs):
    from agentic_mbse.pm.operations import promote_requirement

    return promote_requirement(project_root, **kwargs)


def _op_register_decision(project_root, **kwargs):
    from agentic_mbse.pm.operations import register_decision

    return register_decision(project_root, **kwargs)


def _op_update_validation(project_root, **kwargs):
    from agentic_mbse.pm.operations import update_validation

    return update_validation(project_root, **kwargs)


def _op_add_item(project_root, **kwargs):
    from agentic_mbse.pm.operations import add_item

    return add_item(project_root, **kwargs)


def _op_add_epic(project_root, **kwargs):
    from agentic_mbse.pm.operations import add_epic

    return add_epic(project_root, **kwargs)


def _op_add_validation(project_root, **kwargs):
    from agentic_mbse.pm.operations import add_validation

    return add_validation(project_root, **kwargs)


def _op_trace_element(project_root, **kwargs):
    from agentic_mbse.pm.operations import trace_element

    return trace_element(project_root, **kwargs)


def _op_impact_query(project_root, **kwargs):
    from agentic_mbse.pm.operations import impact_query

    return impact_query(project_root, **kwargs)


def _op_approve_research(project_root, **kwargs):
    from agentic_mbse.pm.operations import approve_research

    return approve_research(project_root, **kwargs)


def _op_register_intent(project_root, **kwargs):
    from agentic_mbse.pm.operations import register_intent

    return register_intent(project_root, **kwargs)


def _op_supersede_insight(project_root, **kwargs):
    from agentic_mbse.pm.operations import supersede_insight

    return supersede_insight(project_root, **kwargs)


# ---------------------------------------------------------------------------
# Dispatch handlers — simple (non-JSON) operations
# ---------------------------------------------------------------------------


def cmd_pm_no_operation(args: argparse.Namespace) -> int:
    """Handle bare 'agentic-mbse pm' with no operation."""
    print(
        "Error: No operation specified. Run 'agentic-mbse pm --help' for available operations.",
        file=sys.stderr,
    )
    return EXIT_USAGE


def cmd_pm_close_item(args: argparse.Namespace) -> int:
    project_root = find_project_root()
    if project_root is None:
        print(
            "Error: Not inside a project (no work/BACKLOG.md found)",
            file=sys.stderr,
        )
        return EXIT_FAILURE

    result = _op_close_item(project_root, args.wi_id)
    _print_warnings(result.warnings)
    print(result.message)
    return EXIT_SUCCESS if result.success else EXIT_FAILURE


def cmd_pm_add_insight(args: argparse.Namespace) -> int:
    return _dispatch(
        args,
        _op_add_insight,
        title=args.title,
        source=args.source,
        context=args.context,
        model_implications=args.model_implications,
        analysis_implications=args.analysis_implications,
        rationale=args.rationale,
    )


def cmd_pm_save_research(args: argparse.Namespace) -> int:
    content_path = Path(args.content_file)
    if not content_path.exists():
        print(f"Error: Content file not found: {content_path}", file=sys.stderr)
        return EXIT_USAGE

    content = content_path.read_text(encoding="utf-8")
    return _dispatch(args, _op_save_research, topic=args.topic, content=content)


def cmd_pm_trace_element(args: argparse.Namespace) -> int:
    return _dispatch(
        args,
        _op_trace_element,
        element=args.element,
        file=args.file,
        type=args.type,
        knowledge=args.knowledge,
        requirement=args.requirement,
        source_type=args.source_type or "",
        source_document=args.source_doc or "",
        source_location=args.source_location or "",
        confidence=args.confidence or "",
        assumptions=args.assumptions or "",
    )


def cmd_pm_promote_requirement(args: argparse.Namespace) -> int:
    return _dispatch(
        args,
        _op_promote_requirement,
        requirement=args.requirement,
        source=args.source,
        enforcement=args.enforcement,
        validation_method=args.validation_method,
    )


def cmd_pm_impact_query(args: argparse.Namespace) -> int:
    project_root = find_project_root()
    if project_root is None:
        print(
            "Error: Not inside a project (no work/BACKLOG.md found)",
            file=sys.stderr,
        )
        return EXIT_FAILURE

    result = _op_impact_query(project_root, query_id=args.query_id)
    _print_warnings(result.warnings)

    if not result.affected_elements:
        print(f"No traced elements found for {result.query_id}")
    else:
        print(f"Impact analysis for {result.query_id}:")
        print(f"  Affected elements: {len(result.affected_elements)}")
        for elem in result.affected_elements:
            print(f"    - {elem.element} ({elem.file})")
    return EXIT_SUCCESS


def cmd_pm_register_decision(args: argparse.Namespace) -> int:
    return _dispatch(
        args,
        _op_register_decision,
        title=args.title,
        decision=args.decision,
        rationale=args.rationale,
    )


def cmd_pm_update_validation(args: argparse.Namespace) -> int:
    return _dispatch(
        args,
        _op_update_validation,
        sv_id=args.sv_id,
        status=args.status,
    )


def cmd_pm_add_item(args: argparse.Namespace) -> int:
    return _dispatch(
        args,
        _op_add_item,
        name=args.name,
        scale=args.scale,
        priority=args.priority,
        epic=args.epic,
        goal=args.goal,
    )


def cmd_pm_add_epic(args: argparse.Namespace) -> int:
    return _dispatch(
        args,
        _op_add_epic,
        name=args.name,
        priority=args.priority,
        file=args.file,
        goal=args.goal,
    )


def cmd_pm_add_validation(args: argparse.Namespace) -> int:
    return _dispatch(
        args,
        _op_add_validation,
        description=args.description,
        type=args.type,
        mechanism=args.mechanism,
        expected=args.expected,
        tolerance=args.tolerance,
        source=args.source or "",
        test=args.test or "",
    )


# ---------------------------------------------------------------------------
# Dispatch handlers — JSON argument operations
# ---------------------------------------------------------------------------


def cmd_pm_approve_research(args: argparse.Namespace) -> int:
    from agentic_mbse.pm.types import InsightInput

    insights, err = _validate_json_list(args.insights, "--insights", InsightInput)
    if err is not None:
        return err

    return _dispatch(
        args,
        _op_approve_research,
        pending_file=args.file,
        insights=insights,
    )


def cmd_pm_register_intent(args: argparse.Namespace) -> int:
    from agentic_mbse.pm.types import GoalInput, QuestionInput

    if args.goals is None and args.questions is None:
        print(
            "Error: At least one of --goals or --questions is required",
            file=sys.stderr,
        )
        return EXIT_USAGE

    goals = None
    questions = None

    if args.goals is not None:
        goals, err = _validate_json_list(args.goals, "--goals", GoalInput)
        if err is not None:
            return err

    if args.questions is not None:
        questions, err = _validate_json_list(args.questions, "--questions", QuestionInput)
        if err is not None:
            return err

    return _dispatch(
        args,
        _op_register_intent,
        goals=goals,
        questions=questions,
    )


def cmd_pm_supersede_insight(args: argparse.Namespace) -> int:
    parsed, err = _parse_json_arg(args.new_insight, "--new-insight")
    if err is not None:
        print(f"Error: {err}", file=sys.stderr)
        return EXIT_USAGE
    if not isinstance(parsed, dict):
        print("Error: --new-insight must be a JSON object", file=sys.stderr)
        return EXIT_USAGE

    project_root = find_project_root()
    if project_root is None:
        print(
            "Error: Not inside a project (no work/BACKLOG.md found)",
            file=sys.stderr,
        )
        return EXIT_FAILURE

    try:
        result = _op_supersede_insight(
            project_root,
            old_id=args.old_id,
            new_insight=parsed,
            reason=args.reason,
        )
        _print_warnings(result.warnings)
        print(result.message)
        return EXIT_SUCCESS if result.success else EXIT_FAILURE
    except NotImplementedError as e:
        print(f"Error: {e}", file=sys.stderr)
        return EXIT_FAILURE


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------


def register_pm_subcommands(subparsers: argparse._SubParsersAction) -> None:
    """Register the 'pm' subcommand group with all operation sub-subcommands."""
    pm_parser = subparsers.add_parser(
        "pm",
        help="Project management operations",
        description=(
            "Deterministic project management operations. "
            "Each operation reads structured files, validates inputs, "
            "and writes atomically."
        ),
    )
    pm_parser.set_defaults(func=cmd_pm_no_operation)
    pm_subs = pm_parser.add_subparsers(dest="operation")

    # -- close-item --
    p = pm_subs.add_parser("close-item", help="Archive a completed work item")
    p.add_argument("wi_id", metavar="WI-XXX", help="Work item ID to close (e.g. WI-001)")
    p.set_defaults(func=cmd_pm_close_item)

    # -- add-insight --
    p = pm_subs.add_parser("add-insight", help="Register a domain insight (DI-XXX)")
    p.add_argument("--title", required=True, help="Insight title")
    p.add_argument("--source", required=True, help="Source document or reference")
    p.add_argument("--context", required=True, help="Context explaining the insight")
    p.add_argument("--model-implications", required=True, help="How this affects the model")
    p.add_argument("--analysis-implications", required=True, help="How this affects analysis")
    p.add_argument("--rationale", default=None, help="Optional rationale")
    p.set_defaults(func=cmd_pm_add_insight)

    # -- save-research --
    p = pm_subs.add_parser("save-research", help="Save a research document to pending/")
    p.add_argument("--topic", required=True, help="Research topic (kebab-case)")
    p.add_argument("--content-file", required=True, help="Path to file with research content")
    p.set_defaults(func=cmd_pm_save_research)

    # -- trace-element --
    p = pm_subs.add_parser("trace-element", help="Add a traceability entry")
    p.add_argument("--element", required=True, help="Element name")
    p.add_argument("--file", required=True, help="Source file path")
    p.add_argument("--type", required=True, help="Element type (part, port, connection, etc.)")
    p.add_argument(
        "--knowledge", action="append", default=None, help="Knowledge ID (DI-XXX), repeatable"
    )
    p.add_argument(
        "--requirement", action="append", default=None, help="Requirement ID (PR-XXX), repeatable"
    )
    p.add_argument("--source-type", default=None, help="Source type")
    p.add_argument("--source-doc", default=None, help="Source document name")
    p.add_argument("--source-location", default=None, help="Source location")
    p.add_argument("--confidence", default=None, help="Confidence level")
    p.add_argument("--assumptions", default=None, help="Assumptions")
    p.set_defaults(func=cmd_pm_trace_element)

    # -- promote-requirement --
    p = pm_subs.add_parser("promote-requirement", help="Add a requirement to REQUIREMENTS.md")
    p.add_argument("--requirement", required=True, help="Requirement text")
    p.add_argument("--source", required=True, help="Source ID (DI-XXX, etc.)")
    p.add_argument("--enforcement", required=True, help="Enforcement method")
    p.add_argument("--validation-method", required=True, help="Validation method")
    p.set_defaults(func=cmd_pm_promote_requirement)

    # -- impact-query --
    p = pm_subs.add_parser("impact-query", help="Query traceability for impact of a change")
    p.add_argument("query_id", metavar="ID", help="DI-XXX or PR-XXX to query")
    p.set_defaults(func=cmd_pm_impact_query)

    # -- register-decision --
    p = pm_subs.add_parser("register-decision", help="Register an architectural decision")
    p.add_argument("--title", required=True, help="Decision title")
    p.add_argument("--decision", required=True, help="Decision text")
    p.add_argument("--rationale", required=True, help="Rationale for the decision")
    p.set_defaults(func=cmd_pm_register_decision)

    # -- update-validation --
    p = pm_subs.add_parser("update-validation", help="Update status of a verification entry")
    p.add_argument("sv_id", metavar="SV-XXX", help="Verification ID (e.g. SV-001)")
    p.add_argument("--status", required=True, help="New status (passing, failing, pending)")
    p.set_defaults(func=cmd_pm_update_validation)

    # -- add-item --
    p = pm_subs.add_parser("add-item", help="Add a work item to BACKLOG.md")
    p.add_argument("--name", required=True, help="Work item name")
    p.add_argument(
        "--scale",
        required=True,
        choices=["trivial", "standard"],
        help="Work item scale",
    )
    p.add_argument(
        "--priority",
        required=True,
        choices=["P0", "P1", "P2", "P3"],
        help="Priority level",
    )
    p.add_argument("--epic", default=None, help="Epic name to add item under")
    p.add_argument("--goal", default=None, help="Goal ID (G-XXX) to associate")
    p.set_defaults(func=cmd_pm_add_item)

    # -- add-epic --
    p = pm_subs.add_parser("add-epic", help="Register an existing epic file in BACKLOG.md")
    p.add_argument("--name", required=True, help="Epic name")
    p.add_argument(
        "--priority",
        required=True,
        choices=["P0", "P1", "P2", "P3"],
        help="Priority level",
    )
    p.add_argument("--file", required=True, help="Epic file path inside work/")
    p.add_argument("--goal", default=None, help="Goal ID (G-XXX) to associate")
    p.set_defaults(func=cmd_pm_add_epic)

    # -- add-validation --
    p = pm_subs.add_parser(
        "add-validation", help="Add a verification entry to VALIDATION_MATRIX.md"
    )
    p.add_argument("--description", required=True, help="Verification description")
    p.add_argument(
        "--type",
        required=True,
        help="Verification type (reasonableness, baseline, physical, relationship, rollup)",
    )
    p.add_argument(
        "--mechanism", required=True, help="Verification mechanism (model, test, manual)"
    )
    p.add_argument("--expected", required=True, help="Expected value")
    p.add_argument("--tolerance", required=True, help="Tolerance")
    p.add_argument("--source", default=None, help="Source reference")
    p.add_argument("--test", default=None, help="Test reference")
    p.set_defaults(func=cmd_pm_add_validation)

    # -- approve-research --
    p = pm_subs.add_parser("approve-research", help="Approve a research file and extract insights")
    p.add_argument("file", help="Path to pending research file")
    p.add_argument("--insights", required=True, help="JSON array of InsightInput objects")
    p.set_defaults(func=cmd_pm_approve_research)

    # -- register-intent --
    p = pm_subs.add_parser("register-intent", help="Register goals and/or analysis questions")
    p.add_argument("--goals", default=None, help="JSON array of GoalInput objects")
    p.add_argument("--questions", default=None, help="JSON array of QuestionInput objects")
    p.set_defaults(func=cmd_pm_register_intent)

    # -- supersede-insight --
    p = pm_subs.add_parser("supersede-insight", help="Supersede a domain insight (stub)")
    p.add_argument("old_id", metavar="DI-XXX", help="ID of insight to supersede")
    p.add_argument("--new-insight", required=True, help="JSON object with new insight data")
    p.add_argument("--reason", required=True, help="Reason for supersession")
    p.set_defaults(func=cmd_pm_supersede_insight)
