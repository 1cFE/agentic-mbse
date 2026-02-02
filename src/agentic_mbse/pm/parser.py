"""PM file parsers.

All 8 public parse functions and shared helpers for extracting typed data
from structured project files (YAML frontmatter, markdown tables,
heading-based sections, CSV).
"""

from __future__ import annotations

import csv
import datetime
import re
from pathlib import Path
from typing import Any

import yaml

from agentic_mbse.pm.types import (
    AnalysisQuestionEntry,
    BacklogData,
    DecisionEntry,
    DecisionStatus,
    EpicEntry,
    EpicStatus,
    GoalEntry,
    InsightEntry,
    InsightStatus,
    OverviewData,
    ParseResult,
    ParseWarning,
    Priority,
    RequirementEntry,
    StandaloneEntry,
    TraceabilityEntry,
    ValidationEntry,
    VerificationMechanism,
    VerificationStatus,
    VerificationType,
    WorkItemEntry,
    WorkItemScale,
    WorkItemStatus,
)

# ---------------------------------------------------------------------------
# Shared helpers (private)
# ---------------------------------------------------------------------------


def _warn(warnings: list[ParseWarning], file: str, location: str, message: str) -> None:
    """Append a warning to the list."""
    warnings.append(ParseWarning(file=str(file), location=location, message=message))


def _strip_html_comments(text: str) -> str:
    """Remove all HTML comments (<!-- ... -->) from text, including multi-line."""
    return re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)


def _parse_markdown_table(
    text: str,
    section_heading: str | None,
    file_path: str,
    warnings: list[ParseWarning],
) -> list[dict[str, str]]:
    """Extract rows from a markdown table, optionally under a specific heading.

    ``text`` must be the file body AFTER frontmatter stripping and HTML comment
    removal.  Callers that use ``parse_frontmatter`` get the body naturally
    (content after the closing ``---``).  ``---`` horizontal rules in the body
    are treated as section terminators.

    Returns a list of dicts mapping column-name -> cell-value for each data row.
    """
    # Scope to section if heading given
    if section_heading is not None:
        pattern = re.compile(r"^" + re.escape(section_heading) + r"\s*$", re.MULTILINE)
        m = pattern.search(text)
        if m is None:
            return []
        start = m.end()
        # Find next ## heading or end
        next_section = re.search(r"^##\s", text[start:], re.MULTILINE)
        if next_section:
            text = text[start : start + next_section.start()]
        else:
            text = text[start:]

    rows: list[dict[str, str]] = []
    lines = text.split("\n")
    headers: list[str] = []
    in_table = False

    for line in lines:
        stripped = line.strip()

        # Stop at next heading or horizontal rule
        if in_table:
            if re.match(r"^#{1,6}\s", stripped):
                break
            if re.match(r"^-{3,}\s*$", stripped):
                break

        if not stripped.startswith("|"):
            if in_table and stripped:
                # Non-empty, non-table line after table started — table ended
                break
            continue

        cells = [c.strip() for c in stripped.split("|")]
        # Remove empty leading/trailing from split
        if cells and cells[0] == "":
            cells = cells[1:]
        if cells and cells[-1] == "":
            cells = cells[:-1]

        if not headers:
            # First | line is the header
            headers = cells
            in_table = True
            continue

        # Check for separator row
        if all(re.match(r"^-+$", c.strip()) for c in cells):
            continue

        # Data row — map to header names
        row: dict[str, str] = {}
        for i, h in enumerate(headers):
            row[h] = cells[i] if i < len(cells) else ""
        rows.append(row)

    return rows


def _parse_heading_sections(
    text: str,
    heading_pattern: str,
    field_pattern: str,
    file_path: str,
    warnings: list[ParseWarning],
) -> list[tuple[str, str, dict[str, str]]]:
    """Split text into sections by heading regex, parse field lines in each.

    Returns list of (id, title, fields_dict) tuples.  Field names in the dict
    are the bold-marker text as-is (e.g. "Source", "Model implications").
    """
    # Strip HTML comments first
    text = _strip_html_comments(text)

    heading_re = re.compile(heading_pattern, re.MULTILINE)
    field_re = re.compile(field_pattern)

    matches = list(heading_re.finditer(text))
    if not matches:
        return []

    results: list[tuple[str, str, dict[str, str]]] = []

    for idx, match in enumerate(matches):
        entry_id = match.group(1)
        title = match.group(2).strip()

        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        section_text = text[start:end]

        fields: dict[str, str] = {}
        current_key: str | None = None

        for line in section_text.split("\n"):
            # Stop at next heading of any level
            if re.match(r"^#{1,6}\s", line.strip()):
                break

            fm = field_re.match(line)
            if fm:
                current_key = fm.group(1).strip()
                fields[current_key] = fm.group(2).strip()
            elif current_key is not None and line.strip():
                # Multi-line continuation
                fields[current_key] += " " + line.strip()

        results.append((entry_id, title, fields))

    return results


# ---------------------------------------------------------------------------
# Public parse functions
# ---------------------------------------------------------------------------


def parse_frontmatter(path: Path) -> ParseResult[dict[str, Any]]:
    """Extract YAML frontmatter from a markdown file (FR-2).

    Returns the parsed dict and any warnings.  Handles missing files,
    empty files, missing delimiters, and malformed YAML gracefully.
    """
    warns: list[ParseWarning] = []
    fp = str(path)

    try:
        content = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        _warn(warns, fp, "file", f"File not found: {path}")
        return ParseResult(data={}, warnings=warns)

    if not content.strip():
        return ParseResult(data={}, warnings=warns)

    lines = content.split("\n")
    if lines[0].strip() != "---":
        _warn(warns, fp, "line 1", "No opening frontmatter delimiter (---)")
        return ParseResult(data={}, warnings=warns)

    # Find closing ---
    closing_idx = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            closing_idx = i
            break

    if closing_idx is None:
        _warn(warns, fp, "frontmatter", "No closing frontmatter delimiter (---)")
        return ParseResult(data={}, warnings=warns)

    yaml_text = "\n".join(lines[1:closing_idx])
    try:
        data = yaml.safe_load(yaml_text)
    except yaml.YAMLError as e:
        _warn(warns, fp, "frontmatter", f"Malformed YAML: {e}")
        return ParseResult(data={}, warnings=warns)

    if data is None:
        return ParseResult(data={}, warnings=warns)

    if not isinstance(data, dict):
        _warn(warns, fp, "frontmatter", "Frontmatter is not a mapping")
        return ParseResult(data={}, warnings=warns)

    # Normalize YAML-coerced types: dates, booleans -> strings
    for key, value in data.items():
        if isinstance(value, (datetime.date, datetime.datetime)):
            data[key] = str(value)
        elif isinstance(value, bool):
            data[key] = str(value)

    return ParseResult(data=data, warnings=warns)


def parse_backlog(path: Path) -> ParseResult[BacklogData]:
    """Parse BACKLOG.md YAML frontmatter into typed BacklogData (FR-3)."""
    fm_result = parse_frontmatter(path)
    warns = list(fm_result.warnings)
    fp = str(path)
    raw = fm_result.data

    epics: list[EpicEntry] = []
    standalone: list[StandaloneEntry] = []

    # Parse epics
    raw_epics = raw.get("epics", [])
    if not isinstance(raw_epics, list):
        _warn(warns, fp, "epics", "Expected a list for 'epics'")
        raw_epics = []

    for i, epic_dict in enumerate(raw_epics):
        if not isinstance(epic_dict, dict):
            _warn(warns, fp, f"epics[{i}]", "Expected a mapping for epic entry")
            continue

        # Validate required fields
        name = epic_dict.get("name")
        if not name:
            _warn(warns, fp, f"epics[{i}]", "Missing required field 'name'")
            continue

        try:
            priority = Priority(epic_dict.get("priority", ""))
        except ValueError:
            _warn(
                warns,
                fp,
                f"epics[{i}]",
                f"Invalid priority '{epic_dict.get('priority')}', "
                f"expected one of: {', '.join(p.value for p in Priority)}",
            )
            continue

        try:
            status = EpicStatus(epic_dict.get("status", ""))
        except ValueError:
            _warn(
                warns,
                fp,
                f"epics[{i}]",
                f"Invalid status '{epic_dict.get('status')}', "
                f"expected one of: {', '.join(s.value for s in EpicStatus)}",
            )
            continue

        file_path = epic_dict.get("file", "")
        if not file_path:
            _warn(warns, fp, f"epics[{i}]", "Missing required field 'file'")
            continue

        goal = epic_dict.get("goal")
        if goal is not None:
            goal = str(goal)

        # Parse items
        items: list[WorkItemEntry] = []
        raw_items = epic_dict.get("items", [])
        if not isinstance(raw_items, list):
            _warn(warns, fp, f"epics[{i}].items", "Expected a list")
            raw_items = []

        for j, item_dict in enumerate(raw_items):
            if not isinstance(item_dict, dict):
                _warn(warns, fp, f"epics[{i}].items[{j}]", "Expected a mapping")
                continue

            item_id = str(item_dict.get("id", ""))
            if not re.match(r"^WI-\d+$", item_id):
                _warn(
                    warns,
                    fp,
                    f"epics[{i}].items[{j}]",
                    f"Invalid id '{item_id}', expected WI-XXX pattern",
                )
                continue

            try:
                item_scale = WorkItemScale(item_dict.get("scale", ""))
            except ValueError:
                _warn(
                    warns,
                    fp,
                    f"epics[{i}].items[{j}]",
                    f"Invalid scale '{item_dict.get('scale')}'",
                )
                continue

            try:
                item_status = WorkItemStatus(item_dict.get("status", ""))
            except ValueError:
                _warn(
                    warns,
                    fp,
                    f"epics[{i}].items[{j}]",
                    f"Invalid status '{item_dict.get('status')}'",
                )
                continue

            item_completed = item_dict.get("completed")
            if item_completed is not None:
                item_completed = str(item_completed)

            if item_status == WorkItemStatus.COMPLETED and not item_completed:
                _warn(
                    warns,
                    fp,
                    f"epics[{i}].items[{j}]",
                    f"Item '{item_id}' has status=completed but no completed date",
                )

            items.append(
                WorkItemEntry(
                    id=item_id,
                    name=str(item_dict.get("name", "")),
                    scale=item_scale,
                    status=item_status,
                    completed=item_completed,
                )
            )

        epics.append(
            EpicEntry(
                name=str(name),
                goal=goal,
                priority=priority,
                status=status,
                file=str(file_path),
                items=items,
            )
        )

    # Parse standalone
    raw_standalone = raw.get("standalone", [])
    if not isinstance(raw_standalone, list):
        _warn(warns, fp, "standalone", "Expected a list for 'standalone'")
        raw_standalone = []

    for i, sa_dict in enumerate(raw_standalone):
        if not isinstance(sa_dict, dict):
            _warn(warns, fp, f"standalone[{i}]", "Expected a mapping")
            continue

        sa_id = str(sa_dict.get("id", ""))
        if not re.match(r"^WI-\d+$", sa_id):
            _warn(
                warns,
                fp,
                f"standalone[{i}]",
                f"Invalid id '{sa_id}', expected WI-XXX pattern",
            )
            continue

        try:
            sa_scale = WorkItemScale(sa_dict.get("scale", ""))
        except ValueError:
            _warn(
                warns,
                fp,
                f"standalone[{i}]",
                f"Invalid scale '{sa_dict.get('scale')}'",
            )
            continue

        try:
            sa_priority = Priority(sa_dict.get("priority", ""))
        except ValueError:
            _warn(
                warns,
                fp,
                f"standalone[{i}]",
                f"Invalid priority '{sa_dict.get('priority')}'",
            )
            continue

        try:
            sa_status = WorkItemStatus(sa_dict.get("status", ""))
        except ValueError:
            _warn(
                warns,
                fp,
                f"standalone[{i}]",
                f"Invalid status '{sa_dict.get('status')}'",
            )
            continue

        sa_completed = sa_dict.get("completed")
        if sa_completed is not None:
            sa_completed = str(sa_completed)

        if sa_status == WorkItemStatus.COMPLETED and not sa_completed:
            _warn(
                warns,
                fp,
                f"standalone[{i}]",
                f"Item '{sa_id}' has status=completed but no completed date",
            )

        standalone.append(
            StandaloneEntry(
                id=sa_id,
                name=str(sa_dict.get("name", "")),
                scale=sa_scale,
                priority=sa_priority,
                status=sa_status,
                completed=sa_completed,
            )
        )

    return ParseResult(data=BacklogData(epics=epics, standalone=standalone), warnings=warns)


def parse_requirements(path: Path) -> ParseResult[list[RequirementEntry]]:
    """Parse REQUIREMENTS.md table into typed RequirementEntry list (FR-4)."""
    warns: list[ParseWarning] = []
    fp = str(path)

    try:
        content = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        _warn(warns, fp, "file", f"File not found: {path}")
        return ParseResult(data=[], warnings=warns)

    if not content.strip():
        return ParseResult(data=[], warnings=warns)

    content = _strip_html_comments(content)
    rows = _parse_markdown_table(content, "## Requirements", fp, warns)

    entries: list[RequirementEntry] = []
    for i, row in enumerate(rows):
        row_id = row.get("ID", "").strip()
        if not re.match(r"^PR-\d+$", row_id):
            _warn(
                warns,
                fp,
                f"row {i}",
                f"Invalid ID '{row_id}', expected PR-XXX pattern",
            )
            continue
        entries.append(
            RequirementEntry(
                id=row_id,
                requirement=row.get("Requirement", "").strip(),
                source=row.get("Source", "").strip(),
                enforcement=row.get("Enforcement", "").strip(),
                validation_method=row.get("Validation Method", "").strip(),
            )
        )

    return ParseResult(data=entries, warnings=warns)


def parse_validation_matrix(path: Path) -> ParseResult[list[ValidationEntry]]:
    """Parse VALIDATION_MATRIX.md table into typed ValidationEntry list (FR-5)."""
    warns: list[ParseWarning] = []
    fp = str(path)

    try:
        content = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        _warn(warns, fp, "file", f"File not found: {path}")
        return ParseResult(data=[], warnings=warns)

    if not content.strip():
        return ParseResult(data=[], warnings=warns)

    content = _strip_html_comments(content)
    rows = _parse_markdown_table(content, "## Verification Registry", fp, warns)

    entries: list[ValidationEntry] = []
    for i, row in enumerate(rows):
        row_id = row.get("ID", "").strip()
        if not re.match(r"^SV-\d+$", row_id):
            _warn(
                warns,
                fp,
                f"row {i}",
                f"Invalid ID '{row_id}', expected SV-XXX pattern",
            )
            continue

        try:
            vtype = VerificationType(row.get("Type", "").strip())
        except ValueError:
            _warn(
                warns,
                fp,
                f"row {i}",
                f"Invalid Type '{row.get('Type', '')}', "
                f"expected one of: {', '.join(v.value for v in VerificationType)}",
            )
            continue

        try:
            mechanism = VerificationMechanism(row.get("Mechanism", "").strip())
        except ValueError:
            _warn(
                warns,
                fp,
                f"row {i}",
                f"Invalid Mechanism '{row.get('Mechanism', '')}', "
                f"expected one of: {', '.join(v.value for v in VerificationMechanism)}",
            )
            continue

        try:
            vstatus = VerificationStatus(row.get("Status", "").strip())
        except ValueError:
            _warn(
                warns,
                fp,
                f"row {i}",
                f"Invalid Status '{row.get('Status', '')}', "
                f"expected one of: {', '.join(v.value for v in VerificationStatus)}",
            )
            continue

        entries.append(
            ValidationEntry(
                id=row_id,
                description=row.get("Description", "").strip(),
                type=vtype,
                mechanism=mechanism,
                expected=row.get("Expected", "").strip(),
                tolerance=row.get("Tolerance", "").strip(),
                source=row.get("Source", "").strip(),
                test=row.get("Test", "").strip(),
                status=vstatus,
            )
        )

    return ParseResult(data=entries, warnings=warns)


def parse_knowledge(path: Path) -> ParseResult[list[InsightEntry]]:
    """Parse KNOWLEDGE.md DI-XXX sections into typed InsightEntry list (FR-6)."""
    warns: list[ParseWarning] = []
    fp = str(path)

    try:
        content = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        _warn(warns, fp, "file", f"File not found: {path}")
        return ParseResult(data=[], warnings=warns)

    if not content.strip():
        return ParseResult(data=[], warnings=warns)

    sections = _parse_heading_sections(
        content,
        heading_pattern=r"^### (DI-\d+):\s*(.+)",
        field_pattern=r"^-\s+\*\*(.+?)\*\*:\s*(.+)",
        file_path=fp,
        warnings=warns,
    )

    entries: list[InsightEntry] = []
    for entry_id, title, fields in sections:
        # Validate status
        status_str = fields.get("Status", "").strip().lower()
        try:
            status = InsightStatus(status_str)
        except ValueError:
            _warn(
                warns,
                fp,
                entry_id,
                f"Invalid Status '{status_str}', "
                f"expected one of: {', '.join(s.value for s in InsightStatus)}",
            )
            continue

        # Check required fields and warn if missing
        required = ["Source", "Context", "Model implications", "Analysis implications"]
        for req in required:
            if not fields.get(req, "").strip():
                _warn(warns, fp, entry_id, f"Missing required field '{req}'")

        entries.append(
            InsightEntry(
                id=entry_id,
                title=title,
                source=fields.get("Source", "").strip(),
                rationale=fields.get("Rationale", "").strip() or None,
                context=fields.get("Context", "").strip(),
                model_implications=fields.get("Model implications", "").strip(),
                analysis_implications=fields.get("Analysis implications", "").strip(),
                status=status,
                superseded_by=fields.get("Superseded-by", "").strip() or None,
                supersedes=fields.get("Supersedes", "").strip() or None,
            )
        )

    return ParseResult(data=entries, warnings=warns)


def parse_architecture(path: Path) -> ParseResult[list[DecisionEntry]]:
    """Parse ARCHITECTURE.md AD-XXX sections into typed DecisionEntry list (FR-7)."""
    warns: list[ParseWarning] = []
    fp = str(path)

    try:
        content = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        _warn(warns, fp, "file", f"File not found: {path}")
        return ParseResult(data=[], warnings=warns)

    if not content.strip():
        return ParseResult(data=[], warnings=warns)

    # Scope to ## Key Decisions section
    m = re.search(r"^## Key Decisions\s*$", content, re.MULTILINE)
    if m is None:
        return ParseResult(data=[], warnings=warns)

    start = m.end()
    next_section = re.search(r"^## ", content[start:], re.MULTILINE)
    if next_section:
        section_text = content[start : start + next_section.start()]
    else:
        section_text = content[start:]

    sections = _parse_heading_sections(
        section_text,
        heading_pattern=r"^### (AD-\d+):\s*(.+)",
        field_pattern=r"^\*\*(.+?)\*\*:\s*(.+)",
        file_path=fp,
        warnings=warns,
    )

    entries: list[DecisionEntry] = []
    for entry_id, title, fields in sections:
        status_str = fields.get("Status", "").strip().lower()
        try:
            status = DecisionStatus(status_str)
        except ValueError:
            _warn(
                warns,
                fp,
                entry_id,
                f"Invalid Status '{status_str}', "
                f"expected one of: {', '.join(s.value for s in DecisionStatus)}",
            )
            continue

        required = ["Decision", "Rationale", "Date"]
        for req in required:
            if not fields.get(req, "").strip():
                _warn(warns, fp, entry_id, f"Missing required field '{req}'")

        entries.append(
            DecisionEntry(
                id=entry_id,
                title=title,
                decision=fields.get("Decision", "").strip(),
                rationale=fields.get("Rationale", "").strip(),
                date=fields.get("Date", "").strip(),
                status=status,
            )
        )

    return ParseResult(data=entries, warnings=warns)


def parse_overview(path: Path) -> ParseResult[OverviewData]:
    """Parse OVERVIEW.md goals and questions tables into typed OverviewData (FR-8)."""
    warns: list[ParseWarning] = []
    fp = str(path)

    try:
        content = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        _warn(warns, fp, "file", f"File not found: {path}")
        return ParseResult(data=OverviewData(), warnings=warns)

    if not content.strip():
        return ParseResult(data=OverviewData(), warnings=warns)

    content = _strip_html_comments(content)

    # Parse goals
    goal_rows = _parse_markdown_table(content, "## Goals Registry", fp, warns)
    goals: list[GoalEntry] = []
    for i, row in enumerate(goal_rows):
        row_id = row.get("ID", "").strip()
        if not re.match(r"^G-\d+$", row_id):
            _warn(
                warns,
                fp,
                f"goals row {i}",
                f"Invalid ID '{row_id}', expected G-XXX pattern",
            )
            continue
        goals.append(
            GoalEntry(
                id=row_id,
                goal=row.get("Goal", "").strip(),
                priority=row.get("Priority", "").strip(),
                status=row.get("Status", "").strip(),
                source=row.get("Source", "").strip(),
                traced_requirements=row.get("Traced Requirements", "").strip(),
            )
        )

    # Parse questions
    question_rows = _parse_markdown_table(content, "## Analysis Questions", fp, warns)
    questions: list[AnalysisQuestionEntry] = []
    for i, row in enumerate(question_rows):
        row_id = row.get("ID", "").strip()
        if not re.match(r"^AQ-\d+$", row_id):
            _warn(
                warns,
                fp,
                f"questions row {i}",
                f"Invalid ID '{row_id}', expected AQ-XXX pattern",
            )
            continue
        questions.append(
            AnalysisQuestionEntry(
                id=row_id,
                question=row.get("Question", "").strip(),
                implies=row.get("Implies", "").strip(),
                source=row.get("Source", "").strip(),
                status=row.get("Status", "").strip(),
            )
        )

    return ParseResult(data=OverviewData(goals=goals, questions=questions), warnings=warns)


def parse_traceability(path: Path) -> ParseResult[list[TraceabilityEntry]]:
    """Parse traceability_matrix.csv into typed TraceabilityEntry list (FR-9)."""
    warns: list[ParseWarning] = []
    fp = str(path)

    try:
        f = path.open(encoding="utf-8", newline="")
    except FileNotFoundError:
        _warn(warns, fp, "file", f"File not found: {path}")
        return ParseResult(data=[], warnings=warns)

    with f:
        content = f.read()

    if not content.strip():
        return ParseResult(data=[], warnings=warns)

    # Re-open for DictReader
    lines = content.splitlines()
    reader = csv.DictReader(lines)

    if reader.fieldnames is None:
        _warn(warns, fp, "header", "No header row found")
        return ParseResult(data=[], warnings=warns)

    # Build case-insensitive header mapping
    header_map: dict[str, str] = {}
    for name in reader.fieldnames:
        header_map[name.strip().lower()] = name.strip()

    expected_cols = [
        "element",
        "file",
        "type",
        "knowledge",
        "requirement",
        "source_type",
        "source_document",
        "source_location",
        "confidence",
        "assumptions",
        "last_verified",
    ]
    for col in expected_cols:
        if col not in header_map:
            _warn(warns, fp, "header", f"Missing expected column '{col}'")

    def _split_multi(val: str) -> list[str]:
        return [x.strip() for x in val.split(",") if x.strip()]

    entries: list[TraceabilityEntry] = []
    for i, row in enumerate(reader):
        # Normalize row keys
        norm_row: dict[str, str] = {}
        for k, v in row.items():
            if k is not None:
                norm_row[k.strip().lower()] = (v or "").strip()

        entries.append(
            TraceabilityEntry(
                element=norm_row.get("element", ""),
                file=norm_row.get("file", ""),
                type=norm_row.get("type", ""),
                knowledge=_split_multi(norm_row.get("knowledge", "")),
                requirement=_split_multi(norm_row.get("requirement", "")),
                source_type=norm_row.get("source_type", ""),
                source_document=norm_row.get("source_document", ""),
                source_location=norm_row.get("source_location", ""),
                confidence=norm_row.get("confidence", ""),
                assumptions=norm_row.get("assumptions", ""),
                last_verified=norm_row.get("last_verified", ""),
            )
        )

    return ParseResult(data=entries, warnings=warns)
