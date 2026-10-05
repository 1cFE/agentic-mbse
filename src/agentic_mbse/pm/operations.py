"""PM operations — deterministic mutations of structured project files.

Each public function takes a project_root Path and operation-specific
parameters, validates inputs using existing parsers, computes changes
in memory, then writes atomically. Returns OperationResult for mutations
or ImpactResult/DashboardResult for queries.
"""

from __future__ import annotations

import csv
import datetime
import re
import shutil
from pathlib import Path
from typing import Any, TypeVar

import yaml

from agentic_mbse.pm.parser import (
    _escape_table_cell,
    _parse_backlog_mapping,
    _split_table_row,
    _strip_html_comments,
    parse_architecture,
    parse_frontmatter,
    parse_knowledge,
    parse_overview,
    parse_requirements,
    parse_traceability,
    parse_validation_matrix,
)
from agentic_mbse.pm.types import (
    BacklogData,
    DecisionEntry,
    DecisionStatus,
    EpicEntry,
    EpicStatus,
    GoalInput,
    ImpactResult,
    InsightEntry,
    InsightInput,
    InsightStatus,
    OperationResult,
    ParseResult,
    ParseWarning,
    Priority,
    QuestionInput,
    StandaloneEntry,
    TraceabilityEntry,
    VerificationMechanism,
    VerificationStatus,
    VerificationType,
    WorkItemEntry,
    WorkItemScale,
    WorkItemStatus,
)

T = TypeVar("T")

# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


def _id_pattern(prefix: str) -> re.Pattern[str]:
    """Return the regex for one ``PREFIX-NNN`` ID token; group 1 is its number.

    The only definition of how an ID is numbered.  The prefix must not follow a
    letter or digit, so ``MAG-001`` is not ``G-001``; a hyphen may precede it, so
    the joined range ``DI-001-DI-014`` names both ends.  Only the digit run must
    end, so ``SV-034a`` names SV 34.  ``PR-1`` and ``PR-001`` share number 1.
    """
    return re.compile(rf"(?<![A-Za-z0-9]){re.escape(prefix)}-(\d+)(?!\d)")


def _next_id(prefix: str, existing_ids: list[str]) -> str:
    """Given a prefix ('DI', 'PR', etc.) and list of existing IDs, return next sequential ID."""
    if not existing_ids:
        return f"{prefix}-001"
    nums = []
    pattern = _id_pattern(prefix)
    for eid in existing_ids:
        m = pattern.fullmatch(eid)
        if m:
            nums.append(int(m.group(1)))
    if not nums:
        return f"{prefix}-001"
    return f"{prefix}-{max(nums) + 1:03d}"


def _registry_ids(path: Path, prefix: str, parsed_ids: list[str]) -> ParseResult[list[str]]:
    """Return every ``prefix`` ID the registry file names, so ``_next_id`` never reuses one.

    The data is ``parsed_ids`` followed by every ``_id_pattern`` token in the file
    outside HTML comments, whether or not the parser accepted its record.  Each
    distinct number that no parsed ID holds gets one warning, located at its
    first spelling.  A missing file returns ``parsed_ids`` with no warning: the
    parser has already warned, and the operation creates the file.
    """
    try:
        content = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ParseResult(data=list(parsed_ids))

    pattern = _id_pattern(prefix)
    tokens = list(pattern.finditer(_strip_html_comments(content)))
    parsed_numbers = {int(m.group(1)) for m in map(pattern.fullmatch, parsed_ids) if m}
    reserved: dict[int, str] = {}  # unparsed number -> its first spelling
    for token in tokens:
        number = int(token.group(1))
        if number not in parsed_numbers:
            reserved.setdefault(number, token.group(0))

    warnings = [
        ParseWarning(
            file=str(path),
            location=spelling,
            message=f"{spelling} is named in {path.name} but is not a parsed record; "
            "its ID stays reserved",
        )
        for spelling in reserved.values()
    ]
    return ParseResult(data=[*parsed_ids, *(m.group(0) for m in tokens)], warnings=warnings)


def _single_match(matches: list[tuple[str, T]], what: str, where: str) -> tuple[str, T]:
    """Return the one ``(location, match)`` pair a targeted write may change.

    The only "exactly one" rule for writes that target an existing record.
    Raises ``ValueError`` when nothing matches ("not found") or several do,
    naming every location so the user can deduplicate by hand.
    """
    if not matches:
        raise ValueError(f"{what} not found in {where}")
    if len(matches) > 1:
        locations = ", ".join(location for location, _ in matches)
        raise ValueError(
            f"{what} appears {len(matches)} times in {where} ({locations}); "
            "deduplicate by hand, then retry"
        )
    return matches[0]


def _update_frontmatter_fields(path: Path, updates: dict[str, str]) -> None:
    """Update specific fields in a file's YAML frontmatter, preserving the body and unknown fields."""
    content = path.read_text(encoding="utf-8")
    lines = content.split("\n")

    if not lines or lines[0].strip() != "---":
        raise ValueError(f"No opening frontmatter delimiter in {path}")

    closing_idx = None
    for i in range(1, len(lines)):
        if lines[i].rstrip() == "---":
            closing_idx = i
            break

    if closing_idx is None:
        raise ValueError(f"No closing frontmatter delimiter in {path}")

    yaml_text = "\n".join(lines[1:closing_idx])
    data = yaml.safe_load(yaml_text) or {}
    data.update(updates)

    new_yaml = yaml.dump(data, default_flow_style=False, sort_keys=False, allow_unicode=True)
    body = "\n".join(lines[closing_idx + 1 :])
    path.write_text(f"---\n{new_yaml}---\n{body}", encoding="utf-8")


def _render_backlog_body(data: BacklogData) -> str:
    """Render BACKLOG.md markdown body from BacklogData."""
    if not data.epics and not data.standalone:
        return (
            "\n# Project Backlog\n\n"
            "No epics or work items yet. Use `/spec-model` to start a work item,\n"
            "or `/backlog` to manage the backlog.\n"
        )

    parts: list[str] = ["\n# Project Backlog\n"]

    for epic in data.epics:
        parts.append(f"## Epic: {epic.name}")
        meta_parts = []
        if epic.goal:
            meta_parts.append(f"**Goal**: {epic.goal}")
        meta_parts.append(
            f"**Priority**: {epic.priority.value if hasattr(epic.priority, 'value') else epic.priority}"
        )
        meta_parts.append(
            f"**Status**: {epic.status.value if hasattr(epic.status, 'value') else epic.status}"
        )
        parts.append(" | ".join(meta_parts))
        parts.append(f"**Epic file**: [{epic.file}]({epic.file})")
        parts.append("")

        if epic.items:
            parts.append("| ID | Item | Scale | Status | Notes |")
            parts.append("|------|------|-------|--------|-------|")
            for item in epic.items:
                scale_val = item.scale.value if hasattr(item.scale, "value") else item.scale
                status_val = item.status.value if hasattr(item.status, "value") else item.status
                notes = ""
                if item.completed:
                    notes = f"Completed {item.completed}"
                parts.append(f"| {item.id} | {item.name} | {scale_val} | {status_val} | {notes} |")
        parts.append("")

    if data.standalone:
        parts.append("## Standalone Items")
        parts.append("")
        parts.append("| ID | Item | Scale | Priority | Status | Notes |")
        parts.append("|------|------|-------|----------|--------|-------|")
        for sa in data.standalone:
            scale_val = sa.scale.value if hasattr(sa.scale, "value") else sa.scale
            priority_val = sa.priority.value if hasattr(sa.priority, "value") else sa.priority
            status_val = sa.status.value if hasattr(sa.status, "value") else sa.status
            notes = ""
            if sa.completed:
                notes = f"Completed {sa.completed}"
            parts.append(f"| {sa.id} | {sa.name} | {scale_val} | {priority_val} | {status_val} | {notes} |")
        parts.append("")

    return "\n".join(parts)


def _write_backlog(path: Path, document: dict[str, Any] | BacklogData) -> None:
    """Write complete BACKLOG.md: ``document`` as the YAML frontmatter + the body rendered from it.

    The body is rendered from the document's typed view, so a record the parser
    rejects stays in the frontmatter but is left out of the dashboard; the
    frontmatter is authoritative.  Operations pass the document ``_load_backlog``
    returned.  Only test fixtures pass a ``BacklogData``, which is dumped first.
    """
    if isinstance(document, BacklogData):
        document = document.model_dump(mode="json")
    yaml_text = yaml.dump(document, default_flow_style=False, sort_keys=False, allow_unicode=True)
    body = _render_backlog_body(_parse_backlog_mapping(document, str(path)).data)
    path.write_text(f"---\n{yaml_text}---\n{body}", encoding="utf-8")


def _load_backlog(path: Path) -> tuple[dict[str, Any], ParseResult[BacklogData]]:
    """Load BACKLOG.md's frontmatter as a document to edit and write back, with its typed view.

    Unreadable means any ``parse_frontmatter`` warning on an existing file,
    including a repeated key, since the document is read with ``unique_keys``.
    Such a document may hold less than the file, and writing it back would
    delete the rest, so every warning raises ``ValueError`` (R1); a warning the
    reader gains later will refuse writes too.  A missing file, or one with no
    frontmatter keys, starts from an empty ``BacklogData``, and the typed view
    carries the reader's "File not found" warning, as ``parse_backlog`` does.
    """
    loaded = parse_frontmatter(path, unique_keys=True)
    if loaded.warnings and path.exists():
        reasons = "; ".join(w.message for w in loaded.warnings)
        raise ValueError(
            f"{path.name} cannot be read whole, so writing it back could delete records. "
            f"Fix it by hand, then retry: {reasons}"
        )
    document = loaded.data or BacklogData().model_dump(mode="json")
    typed = _parse_backlog_mapping(document, str(path))
    return document, ParseResult(data=typed.data, warnings=[*loaded.warnings, *typed.warnings])


def _backlog_list(mapping: dict[str, Any], key: str, location: str) -> list[Any]:
    """Return the list under ``key`` that a new backlog entry is appended to.

    An absent or null key gets a new list, since replacing it discards nothing.
    Raises ``ValueError`` (R2) if the key holds anything else; ``location``
    names it the way the parser's warnings do.
    """
    if mapping.get(key) is None:
        mapping[key] = []
    entries = mapping[key]
    if not isinstance(entries, list):
        raise ValueError(
            f"'{location}' in BACKLOG.md is not a list, so appending to it would discard it. "
            "Fix it by hand, then retry."
        )
    return entries


def _entries_of(value: Any) -> list[Any]:
    """Return ``value`` if it is a list, else no entries: a lookup finds nothing in a non-list."""
    return value if isinstance(value, list) else []


def _raw_epics(document: dict[str, Any], name: str) -> list[tuple[str, dict[str, Any]]]:
    """Find the epic mappings named ``name`` in a backlog document, valid or not.

    Returns ``(location, mapping)`` pairs for ``_single_match``, each located
    ``epics[i]`` as in the parser's warnings.  A name matches as the parser
    reads it, so an epic with an empty name matches nothing.
    """
    return [
        (f"epics[{i}]", epic)
        for i, epic in enumerate(_entries_of(document.get("epics")))
        if isinstance(epic, dict) and epic.get("name") and str(epic["name"]) == name
    ]


def _raw_work_items(document: dict[str, Any], wi_id: str) -> list[tuple[str, dict[str, Any]]]:
    """Find the work-item mappings with ID ``wi_id`` in a backlog document, valid or not.

    Searches every epic's items, then the standalone list.  Returns ``(location,
    mapping)`` pairs for ``_single_match``, each located ``epics[i].items[j]`` or
    ``standalone[k]`` as in the parser's warnings.
    """
    located = [
        (f"epics[{i}].items[{j}]", item)
        for i, epic in enumerate(_entries_of(document.get("epics")))
        if isinstance(epic, dict)
        for j, item in enumerate(_entries_of(epic.get("items")))
    ]
    located += [
        (f"standalone[{k}]", item) for k, item in enumerate(_entries_of(document.get("standalone")))
    ]
    return [
        (location, item)
        for location, item in located
        if isinstance(item, dict) and str(item.get("id", "")) == wi_id
    ]


def _with_parse_warnings(location: str, warnings: list[ParseWarning]) -> str:
    """Return ``location`` followed by the parse warnings found there, for a refusal message.

    The warnings at an item's enclosing ``epics[i]`` count too, because an item
    is dropped with its epic.
    """
    epic_location = location.split(".", 1)[0]
    messages = [w.message for w in warnings if w.location in (location, epic_location)]
    return f"{location} ({'; '.join(messages)})" if messages else location


def _backlog_target(
    matches: list[tuple[str, dict[str, Any]]],
    what: str,
    *,
    parsed: bool,
    warnings: list[ParseWarning],
) -> tuple[str, dict[str, Any]]:
    """Return the one backlog mapping a write targets, refusing per R3 and R4.

    Raises ``ValueError`` unless exactly one mapping matches (``_single_match``)
    and the parser accepted it as a record.  ``parsed`` says whether the typed
    view holds ``what``; with one match that is exact, because the typed record
    can only have come from that mapping.  The R4 refusal quotes the parse
    ``warnings`` that rejected it.
    """
    location, target = _single_match(matches, what, "BACKLOG.md")
    if not parsed:
        raise ValueError(
            f"{what} is in BACKLOG.md at {_with_parse_warnings(location, warnings)} but is "
            "not a valid record. Fix it by hand, then retry."
        )
    return location, target


def _work_item_ids(data: BacklogData) -> list[str]:
    """Return the ID of every parsed work item: epic items first, then standalone."""
    return [item.id for epic in data.epics for item in epic.items] + [
        sa.id for sa in data.standalone
    ]


def _format_insight_entry(entry: InsightEntry) -> str:
    """Format a DI-XXX entry as markdown for KNOWLEDGE.md."""
    lines = [f"### {entry.id}: {entry.title}"]
    lines.append(f"- **Source**: {entry.source}")
    if entry.rationale:
        lines.append(f"- **Rationale**: {entry.rationale}")
    lines.append(f"- **Context**: {entry.context}")
    lines.append(f"- **Model implications**: {entry.model_implications}")
    lines.append(f"- **Analysis implications**: {entry.analysis_implications}")
    lines.append(
        f"- **Status**: {entry.status.value if hasattr(entry.status, 'value') else entry.status}"
    )
    if entry.superseded_by:
        lines.append(f"- **Superseded-by**: {entry.superseded_by}")
    if entry.supersedes:
        lines.append(f"- **Supersedes**: {entry.supersedes}")
    return "\n".join(lines) + "\n"


def _format_decision_entry(entry: DecisionEntry) -> str:
    """Format an AD-XXX entry as markdown for ARCHITECTURE.md."""
    lines = [f"### {entry.id}: {entry.title}"]
    lines.append(f"**Decision**: {entry.decision}")
    lines.append(f"**Rationale**: {entry.rationale}")
    lines.append(f"**Date**: {entry.date}")
    lines.append(
        f"**Status**: {entry.status.value if hasattr(entry.status, 'value') else entry.status}"
    )
    return "\n".join(lines) + "\n"


def _format_table_row(columns: list[str]) -> str:
    """Format a markdown table data row, escaping every cell with ``_escape_table_cell``.

    The space on each side of every delimiter keeps a value that ends in a
    backslash from escaping the next delimiter.  Raises ``ValueError`` for a
    value no row can carry.
    """
    return "| " + " | ".join(_escape_table_cell(c) for c in columns) + " |"


def _append_section(path: Path, text: str) -> None:
    """Append a markdown section to the end of a file."""
    if path.exists():
        content = path.read_text(encoding="utf-8")
        if content and not content.endswith("\n"):
            content += "\n"
        if content and not content.endswith("\n\n"):
            content += "\n"
        content += text
    else:
        content = text
    path.write_text(content, encoding="utf-8")


def _insert_table_row(text: str, section_heading: str, row: str) -> str:
    """Return ``text`` with ``row`` inserted after the last table line under ``section_heading``.

    Raises ``ValueError`` if the heading is missing, or if no table line comes
    before the next ``## `` heading.
    """
    lines = text.split("\n")

    # Find section heading
    section_start = None
    for i, line in enumerate(lines):
        if line.strip() == section_heading:
            section_start = i
            break

    if section_start is None:
        raise ValueError(f"Section heading '{section_heading}' not found")

    # Find the last table row in this section
    last_table_line = None
    for i in range(section_start + 1, len(lines)):
        stripped = lines[i].strip()
        if stripped.startswith("|"):
            last_table_line = i
        elif last_table_line is not None and stripped and not stripped.startswith("|"):
            # Non-empty, non-table line after table started
            break
        elif stripped.startswith("#") and last_table_line is not None:
            break
        elif re.match(r"##(\s|$)", stripped):
            # The next section starts before any table, so this section has none
            break

    if last_table_line is None:
        raise ValueError(f"No table found under '{section_heading}'")

    # Insert after the last table line
    lines.insert(last_table_line + 1, row)
    return "\n".join(lines)


def _append_table_row(path: Path, section_heading: str, row: str) -> None:
    """Append a row to a markdown table under a given section heading.

    Raises ``ValueError`` from ``_insert_table_row`` before writing anything.
    """
    content = path.read_text(encoding="utf-8")
    path.write_text(_insert_table_row(content, section_heading, row), encoding="utf-8")


def _raw_table_rows(text: str, section_heading: str, row_id: str) -> list[tuple[str, int]]:
    """Find the table rows under ``section_heading`` whose first cell is ``row_id``.

    Returns ``(location, line index)`` pairs for ``_single_match``; a location
    reads ``line N``, counting from 1.  The section runs from the first line
    that is ``section_heading`` to the next ``## `` heading, so it holds the
    table ``_parse_markdown_table`` reads.  HTML comments are blanked first, so
    a commented example row never matches, and every index is a line of ``text``.
    """
    rows: list[tuple[str, int]] = []
    in_section = False
    for i, line in enumerate(_strip_html_comments(text, keep_lines=True).split("\n")):
        stripped = line.strip()
        if not in_section:
            in_section = line.rstrip() == section_heading
        elif re.match(r"##\s", line):
            break
        elif stripped.startswith("|") and _split_table_row(stripped)[:1] == [row_id]:
            rows.append((f"line {i + 1}", i))
    return rows


def _append_csv_row(path: Path, row: dict[str, str]) -> None:
    """Append a row to a CSV file, using the existing header order."""
    csv_headers = [
        "Element",
        "File",
        "Type",
        "Knowledge",
        "Requirement",
        "Source_Type",
        "Source_Document",
        "Source_Location",
        "Confidence",
        "Assumptions",
        "Last_Verified",
    ]

    if not path.exists() or not path.read_text(encoding="utf-8").strip():
        # Create with headers
        with path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=csv_headers)
            writer.writeheader()
            writer.writerow(row)
    else:
        # Read existing headers
        with path.open(encoding="utf-8", newline="") as f:
            reader = csv.reader(f)
            existing_headers = next(reader, csv_headers)
            existing_headers = [h.strip() for h in existing_headers]

        with path.open("a", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=existing_headers)
            writer.writerow(row)


# ---------------------------------------------------------------------------
# Public operations — Phase 2: Simple append
# ---------------------------------------------------------------------------


def add_insight(
    project_root: Path,
    *,
    title: str,
    source: str,
    context: str,
    model_implications: str,
    analysis_implications: str,
    rationale: str | None = None,
) -> OperationResult:
    """Add a domain insight to KNOWLEDGE.md."""
    # Validate required fields
    for name, val in [
        ("title", title),
        ("source", source),
        ("context", context),
        ("model_implications", model_implications),
        ("analysis_implications", analysis_implications),
    ]:
        if not val or not val.strip():
            return OperationResult(success=False, message=f"Required field '{name}' is empty")

    knowledge_path = project_root / "knowledge" / "KNOWLEDGE.md"
    result = parse_knowledge(knowledge_path)
    taken = _registry_ids(knowledge_path, "DI", [e.id for e in result.data])
    new_id = _next_id("DI", taken.data)

    entry = InsightEntry(
        id=new_id,
        title=title.strip(),
        source=source.strip(),
        rationale=rationale.strip() if rationale else None,
        context=context.strip(),
        model_implications=model_implications.strip(),
        analysis_implications=analysis_implications.strip(),
        status=InsightStatus.CAPTURED,
    )

    text = _format_insight_entry(entry)
    _append_section(knowledge_path, text)

    return OperationResult(
        success=True,
        message=f"Added insight {new_id}: {title}",
        ids_assigned={"DI": new_id},
        files_modified=[str(knowledge_path)],
        warnings=[*result.warnings, *taken.warnings],
    )


def save_research(
    project_root: Path,
    *,
    topic: str,
    content: str,
) -> OperationResult:
    """Save a research document to knowledge/research/pending/."""
    if not topic or not topic.strip():
        return OperationResult(success=False, message="Required field 'topic' is empty")
    if not content or not content.strip():
        return OperationResult(success=False, message="Required field 'content' is empty")

    kebab = re.sub(r"[^a-z0-9]+", "-", topic.lower()).strip("-")
    now = datetime.datetime.now()
    filename = f"{now.strftime('%Y%m%d')}-{now.strftime('%H%M%S')}_{kebab}.md"

    pending_dir = project_root / "knowledge" / "research" / "pending"
    pending_dir.mkdir(parents=True, exist_ok=True)

    file_path = pending_dir / filename
    file_path.write_text(content, encoding="utf-8")

    return OperationResult(
        success=True,
        message=f"Saved research to {file_path.relative_to(project_root)}",
        files_modified=[str(file_path)],
    )


def promote_requirement(
    project_root: Path,
    *,
    requirement: str,
    source: str,
    enforcement: str,
    validation_method: str,
) -> OperationResult:
    """Add a requirement to REQUIREMENTS.md."""
    for name, val in [
        ("requirement", requirement),
        ("source", source),
        ("enforcement", enforcement),
        ("validation_method", validation_method),
    ]:
        if not val or not val.strip():
            return OperationResult(success=False, message=f"Required field '{name}' is empty")

    if not re.match(r"^(DI-\d+|G-\d+)$", source.strip()):
        return OperationResult(
            success=False,
            message=f"Source '{source}' must match DI-XXX or G-XXX pattern",
        )

    req_path = project_root / "modeling_project" / "REQUIREMENTS.md"
    result = parse_requirements(req_path)
    taken = _registry_ids(req_path, "PR", [e.id for e in result.data])
    warnings = [*result.warnings, *taken.warnings]
    new_id = _next_id("PR", taken.data)

    try:
        row = _format_table_row(
            [
                new_id,
                requirement.strip(),
                source.strip(),
                enforcement.strip(),
                validation_method.strip(),
            ]
        )
        _append_table_row(req_path, "## Requirements", row)
    except ValueError as e:
        return OperationResult(
            success=False,
            message=f"Requirement not added to {req_path.name}: {e}",
            warnings=warnings,
        )

    return OperationResult(
        success=True,
        message=f"Added requirement {new_id}: {requirement}",
        ids_assigned={"PR": new_id},
        files_modified=[str(req_path)],
        warnings=warnings,
    )


def register_decision(
    project_root: Path,
    *,
    title: str,
    decision: str,
    rationale: str,
) -> OperationResult:
    """Add an architectural decision to ARCHITECTURE.md."""
    for name, val in [("title", title), ("decision", decision), ("rationale", rationale)]:
        if not val or not val.strip():
            return OperationResult(success=False, message=f"Required field '{name}' is empty")

    arch_path = project_root / "modeling_project" / "ARCHITECTURE.md"
    result = parse_architecture(arch_path)
    taken = _registry_ids(arch_path, "AD", [e.id for e in result.data])
    new_id = _next_id("AD", taken.data)

    today = datetime.date.today().isoformat()
    entry = DecisionEntry(
        id=new_id,
        title=title.strip(),
        decision=decision.strip(),
        rationale=rationale.strip(),
        date=today,
        status=DecisionStatus.ACTIVE,
    )

    text = _format_decision_entry(entry)

    # Append under ## Key Decisions section
    content = arch_path.read_text(encoding="utf-8")
    m = re.search(r"^## Key Decisions\s*$", content, re.MULTILINE)
    if m is None:
        return OperationResult(
            success=False,
            message="'## Key Decisions' section not found in ARCHITECTURE.md",
        )

    # Find where to insert: after the section heading and any existing content
    insert_pos = len(content)
    # Look for next ## heading after Key Decisions
    next_section = re.search(r"^## ", content[m.end() :], re.MULTILINE)
    if next_section:
        insert_pos = m.end() + next_section.start()

    # Insert the entry before the next section (or at EOF)
    new_content = content[:insert_pos]
    if not new_content.endswith("\n\n"):
        if not new_content.endswith("\n"):
            new_content += "\n"
        new_content += "\n"
    new_content += text
    if insert_pos < len(content):
        new_content += "\n" + content[insert_pos:]

    arch_path.write_text(new_content, encoding="utf-8")

    return OperationResult(
        success=True,
        message=f"Added decision {new_id}: {title}",
        ids_assigned={"AD": new_id},
        files_modified=[str(arch_path)],
        warnings=[*result.warnings, *taken.warnings],
    )


def add_validation(
    project_root: Path,
    *,
    description: str,
    type: str,
    mechanism: str,
    expected: str,
    tolerance: str,
    source: str = "",
    test: str = "",
) -> OperationResult:
    """Add a verification entry to VALIDATION_MATRIX.md."""
    if not description or not description.strip():
        return OperationResult(success=False, message="Required field 'description' is empty")

    try:
        vtype = VerificationType(type)
    except ValueError:
        valid = ", ".join(v.value for v in VerificationType)
        return OperationResult(
            success=False, message=f"Invalid type '{type}', expected one of: {valid}"
        )

    try:
        vmech = VerificationMechanism(mechanism)
    except ValueError:
        valid = ", ".join(v.value for v in VerificationMechanism)
        return OperationResult(
            success=False, message=f"Invalid mechanism '{mechanism}', expected one of: {valid}"
        )

    val_path = project_root / "modeling_project" / "VALIDATION_MATRIX.md"
    result = parse_validation_matrix(val_path)
    taken = _registry_ids(val_path, "SV", [e.id for e in result.data])
    warnings = [*result.warnings, *taken.warnings]
    new_id = _next_id("SV", taken.data)

    try:
        row = _format_table_row(
            [
                new_id,
                description.strip(),
                vtype.value,
                vmech.value,
                expected.strip(),
                tolerance.strip(),
                source.strip(),
                test.strip(),
                VerificationStatus.PENDING.value,
            ]
        )
        _append_table_row(val_path, "## Verification Registry", row)
    except ValueError as e:
        return OperationResult(
            success=False,
            message=f"Verification not added to {val_path.name}: {e}",
            warnings=warnings,
        )

    return OperationResult(
        success=True,
        message=f"Added verification {new_id}: {description}",
        ids_assigned={"SV": new_id},
        files_modified=[str(val_path)],
        warnings=warnings,
    )


# ---------------------------------------------------------------------------
# Public operations — Phase 3: Cross-file and multi-file
# ---------------------------------------------------------------------------


def trace_element(
    project_root: Path,
    *,
    element: str,
    file: str,
    type: str,
    knowledge: list[str] | None = None,
    requirement: list[str] | None = None,
    source_type: str = "",
    source_document: str = "",
    source_location: str = "",
    confidence: str = "",
    assumptions: str = "",
    last_verified: str | None = None,
) -> OperationResult:
    """Add a traceability entry to traceability_matrix.csv."""
    if not element or not element.strip():
        return OperationResult(success=False, message="Required field 'element' is empty")
    if not file or not file.strip():
        return OperationResult(success=False, message="Required field 'file' is empty")

    warnings: list[ParseWarning] = []

    # Validate knowledge IDs exist
    if knowledge:
        k_path = project_root / "knowledge" / "KNOWLEDGE.md"
        k_result = parse_knowledge(k_path)
        warnings.extend(k_result.warnings)
        existing_di = {e.id for e in k_result.data}
        for kid in knowledge:
            if kid not in existing_di:
                return OperationResult(
                    success=False,
                    message=f"Knowledge ID '{kid}' not found in KNOWLEDGE.md",
                    warnings=warnings,
                )

    # Validate requirement IDs exist
    if requirement:
        r_path = project_root / "modeling_project" / "REQUIREMENTS.md"
        r_result = parse_requirements(r_path)
        warnings.extend(r_result.warnings)
        existing_pr = {e.id for e in r_result.data}
        for rid in requirement:
            if rid not in existing_pr:
                return OperationResult(
                    success=False,
                    message=f"Requirement ID '{rid}' not found in REQUIREMENTS.md",
                    warnings=warnings,
                )

    # Check for duplicates
    csv_path = project_root / "data" / "traceability_matrix.csv"
    t_result = parse_traceability(csv_path)
    warnings.extend(t_result.warnings)
    for entry in t_result.data:
        if entry.element == element.strip() and entry.file == file.strip():
            return OperationResult(
                success=False,
                message=f"Duplicate: element '{element}' + file '{file}' already exists in traceability matrix",
                warnings=warnings,
            )

    if last_verified is None:
        last_verified = datetime.date.today().isoformat()

    csv_path.parent.mkdir(parents=True, exist_ok=True)
    _append_csv_row(
        csv_path,
        {
            "Element": element.strip(),
            "File": file.strip(),
            "Type": type.strip(),
            "Knowledge": ",".join(knowledge) if knowledge else "",
            "Requirement": ",".join(requirement) if requirement else "",
            "Source_Type": source_type.strip(),
            "Source_Document": source_document.strip(),
            "Source_Location": source_location.strip(),
            "Confidence": confidence.strip(),
            "Assumptions": assumptions.strip(),
            "Last_Verified": last_verified,
        },
    )

    return OperationResult(
        success=True,
        message=f"Traced element '{element}' in {file}",
        files_modified=[str(csv_path)],
        warnings=warnings,
    )


def approve_research(
    project_root: Path,
    *,
    pending_file: str | Path,
    insights: list[InsightInput],
) -> OperationResult:
    """Approve a research file: extract insights to KNOWLEDGE.md and move to approved/."""
    pending_path = Path(pending_file)
    if not pending_path.is_absolute():
        pending_path = project_root / pending_path

    pending_dir = project_root / "knowledge" / "research" / "pending"
    try:
        pending_path.relative_to(pending_dir)
    except ValueError:
        return OperationResult(
            success=False,
            message=f"File '{pending_path}' is not in {pending_dir}",
        )

    if not pending_path.exists():
        return OperationResult(
            success=False,
            message=f"File not found: {pending_path}",
        )

    if not insights:
        return OperationResult(
            success=False,
            message="No insights provided",
        )

    # Parse existing knowledge for ID assignment
    k_path = project_root / "knowledge" / "KNOWLEDGE.md"
    k_result = parse_knowledge(k_path)
    taken = _registry_ids(k_path, "DI", [e.id for e in k_result.data])
    warnings = [*k_result.warnings, *taken.warnings]

    # Build all entries in memory first
    entries: list[InsightEntry] = []
    ids_assigned: dict[str, str] = {}
    all_ids = list(taken.data)
    for inp in insights:
        for name, val in [
            ("title", inp.title),
            ("source", inp.source),
            ("context", inp.context),
            ("model_implications", inp.model_implications),
            ("analysis_implications", inp.analysis_implications),
        ]:
            if not val or not val.strip():
                return OperationResult(
                    success=False,
                    message=f"Insight '{inp.title}': required field '{name}' is empty",
                    warnings=warnings,
                )

        new_id = _next_id("DI", all_ids)
        all_ids.append(new_id)
        ids_assigned[new_id] = inp.title
        entries.append(
            InsightEntry(
                id=new_id,
                title=inp.title.strip(),
                source=inp.source.strip(),
                rationale=inp.rationale.strip() if inp.rationale else None,
                context=inp.context.strip(),
                model_implications=inp.model_implications.strip(),
                analysis_implications=inp.analysis_implications.strip(),
                status=InsightStatus.CAPTURED,
            )
        )

    # Atomicity: append entries first, then move file
    for entry in entries:
        text = _format_insight_entry(entry)
        _append_section(k_path, text)

    approved_dir = project_root / "knowledge" / "research" / "approved"
    approved_dir.mkdir(parents=True, exist_ok=True)
    approved_path = approved_dir / pending_path.name
    shutil.move(str(pending_path), str(approved_path))

    id_list = ", ".join(ids_assigned.keys())
    return OperationResult(
        success=True,
        message=f"Approved research: {pending_path.name}. Created insights: {id_list}",
        ids_assigned={di_id: title for di_id, title in ids_assigned.items()},
        files_modified=[str(k_path), str(approved_path)],
        warnings=warnings,
    )


def register_intent(
    project_root: Path,
    *,
    goals: list[GoalInput] | None = None,
    questions: list[QuestionInput] | None = None,
) -> OperationResult:
    """Register goals and/or analysis questions in OVERVIEW.md."""
    if not goals and not questions:
        return OperationResult(success=False, message="At least one goal or question is required")

    overview_path = project_root / "modeling_project" / "OVERVIEW.md"
    o_result = parse_overview(overview_path)
    taken_g = _registry_ids(overview_path, "G", [e.id for e in o_result.data.goals])
    taken_aq = _registry_ids(overview_path, "AQ", [e.id for e in o_result.data.questions])
    warnings = [*o_result.warnings, *taken_g.warnings, *taken_aq.warnings]

    # Build every row before the one write, so a refused value writes nothing
    ids_assigned: dict[str, str] = {}

    goal_rows: list[str] = []
    all_g_ids = list(taken_g.data)
    for g in goals or []:
        for name, val in [("goal", g.goal), ("priority", g.priority), ("source", g.source)]:
            if not val or not val.strip():
                return OperationResult(
                    success=False,
                    message=f"Goal '{g.goal}': required field '{name}' is empty",
                    warnings=warnings,
                )
        new_id = _next_id("G", all_g_ids)
        all_g_ids.append(new_id)
        try:
            goal_rows.append(
                _format_table_row(
                    [
                        new_id,
                        g.goal.strip(),
                        g.priority.strip(),
                        g.status.strip(),
                        g.source.strip(),
                        g.traced_requirements.strip(),
                    ]
                )
            )
        except ValueError as e:
            return OperationResult(
                success=False, message=f"Goal '{g.goal}': {e}", warnings=warnings
            )
        ids_assigned[new_id] = g.goal

    question_rows: list[str] = []
    all_aq_ids = list(taken_aq.data)
    for q in questions or []:
        for name, val in [("question", q.question), ("source", q.source)]:
            if not val or not val.strip():
                return OperationResult(
                    success=False,
                    message=f"Question '{q.question}': required field '{name}' is empty",
                    warnings=warnings,
                )
        new_id = _next_id("AQ", all_aq_ids)
        all_aq_ids.append(new_id)
        try:
            question_rows.append(
                _format_table_row(
                    [
                        new_id,
                        q.question.strip(),
                        q.implies.strip(),
                        q.source.strip(),
                        q.status.strip(),
                    ]
                )
            )
        except ValueError as e:
            return OperationResult(
                success=False, message=f"Question '{q.question}': {e}", warnings=warnings
            )
        ids_assigned[new_id] = q.question

    text = overview_path.read_text(encoding="utf-8")
    try:
        for row in goal_rows:
            text = _insert_table_row(text, "## Goals Registry", row)
        for row in question_rows:
            text = _insert_table_row(text, "## Analysis Questions", row)
    except ValueError as e:
        return OperationResult(
            success=False,
            message=f"Intent not registered in {overview_path.name}: {e}",
            warnings=warnings,
        )
    overview_path.write_text(text, encoding="utf-8")

    id_list = ", ".join(ids_assigned.keys())
    return OperationResult(
        success=True,
        message=f"Registered intent: {id_list}",
        ids_assigned=ids_assigned,
        files_modified=[str(overview_path)],
        warnings=warnings,
    )


def impact_query(
    project_root: Path,
    *,
    query_id: str,
) -> ImpactResult:
    """Query the traceability matrix for elements affected by a DI-XXX or PR-XXX change."""
    if not re.match(r"^(DI-\d+|PR-\d+)$", query_id):
        return ImpactResult(
            query_id=query_id,
            warnings=[
                ParseWarning(
                    file="",
                    location="query_id",
                    message=f"Invalid query ID '{query_id}', expected DI-XXX or PR-XXX pattern",
                )
            ],
        )

    csv_path = project_root / "data" / "traceability_matrix.csv"
    if not csv_path.exists():
        return ImpactResult(
            query_id=query_id,
            warnings=[
                ParseWarning(
                    file=str(csv_path),
                    location="file",
                    message="Traceability matrix not found",
                )
            ],
        )

    t_result = parse_traceability(csv_path)
    warnings = list(t_result.warnings)

    affected: list[TraceabilityEntry] = []
    for entry in t_result.data:
        if query_id.startswith("DI-") and query_id in entry.knowledge:
            affected.append(entry)
        elif query_id.startswith("PR-") and query_id in entry.requirement:
            affected.append(entry)

    # TODO: Populate affected_work_items when a model→work-item mapping exists
    return ImpactResult(
        query_id=query_id,
        affected_elements=affected,
        affected_work_items=[],
        warnings=warnings,
    )


# ---------------------------------------------------------------------------
# Public operations — Phase 4: BACKLOG.md mutations
# ---------------------------------------------------------------------------


def add_epic(
    project_root: Path,
    *,
    name: str,
    priority: str,
    file: str,
    goal: str | None = None,
) -> OperationResult:
    """Register an existing epic file in BACKLOG.md."""
    epic_name = name.strip()
    if not epic_name:
        return OperationResult(success=False, message="Required field 'name' is empty")

    try:
        epic_priority = Priority(priority)
    except ValueError:
        valid = ", ".join(p.value for p in Priority)
        return OperationResult(
            success=False, message=f"Invalid priority '{priority}', expected one of: {valid}"
        )

    if not file or not file.strip():
        return OperationResult(success=False, message="Required field 'file' is empty")

    supplied_path = Path(file)
    epic_path = supplied_path if supplied_path.is_absolute() else project_root / supplied_path
    resolved_epic_path = epic_path.resolve()
    work_directory = (project_root / "work").resolve()
    try:
        backlog_relative_path = resolved_epic_path.relative_to(work_directory)
    except ValueError:
        return OperationResult(
            success=False,
            message=f"Epic file must be inside the project work directory: {file}",
        )

    if not resolved_epic_path.is_file():
        return OperationResult(success=False, message=f"Epic file does not exist: {file}")

    backlog_path = project_root / "work" / "BACKLOG.md"
    try:
        document, backlog = _load_backlog(backlog_path)
    except ValueError as e:
        return OperationResult(success=False, message=str(e))

    # Any epic mapping with this name blocks the add, valid or not (R5)
    existing = _raw_epics(document, epic_name)
    if existing:
        places = ", ".join(_with_parse_warnings(loc, backlog.warnings) for loc, _ in existing)
        return OperationResult(
            success=False,
            message=f"Epic '{epic_name}' already exists in BACKLOG.md at {places}",
            warnings=backlog.warnings,
        )

    try:
        epics = _backlog_list(document, "epics", "epics")
    except ValueError as e:
        return OperationResult(success=False, message=str(e), warnings=backlog.warnings)

    epics.append(
        EpicEntry(
            name=epic_name,
            goal=goal,
            priority=epic_priority,
            status=EpicStatus.DRAFT,
            file=backlog_relative_path.as_posix(),
        ).model_dump(mode="json")
    )
    _write_backlog(backlog_path, document)

    return OperationResult(
        success=True,
        message=f"Added epic: {epic_name}",
        files_modified=[str(backlog_path)],
        warnings=backlog.warnings,
    )


def add_item(
    project_root: Path,
    *,
    name: str,
    scale: str,
    priority: str,
    epic: str | None = None,
    goal: str | None = None,
) -> OperationResult:
    """Add a work item to BACKLOG.md."""
    if not name or not name.strip():
        return OperationResult(success=False, message="Required field 'name' is empty")

    try:
        item_scale = WorkItemScale(scale)
    except ValueError:
        valid = ", ".join(s.value for s in WorkItemScale)
        return OperationResult(
            success=False, message=f"Invalid scale '{scale}', expected one of: {valid}"
        )

    try:
        item_priority = Priority(priority)
    except ValueError:
        valid = ", ".join(p.value for p in Priority)
        return OperationResult(
            success=False, message=f"Invalid priority '{priority}', expected one of: {valid}"
        )

    backlog_path = project_root / "work" / "BACKLOG.md"
    try:
        document, backlog = _load_backlog(backlog_path)
    except ValueError as e:
        return OperationResult(success=False, message=str(e))

    taken = _registry_ids(backlog_path, "WI", _work_item_ids(backlog.data))
    warnings = [*backlog.warnings, *taken.warnings]
    new_id = _next_id("WI", taken.data)

    # Find the list the item goes in: the one epic named, or standalone
    try:
        if epic:
            location, target_epic = _backlog_target(
                _raw_epics(document, epic),
                f"Epic '{epic}'",
                parsed=any(ep.name == epic for ep in backlog.data.epics),
                warnings=backlog.warnings,
            )
            items = _backlog_list(target_epic, "items", f"{location}.items")
        else:
            items = _backlog_list(document, "standalone", "standalone")
    except ValueError as e:
        return OperationResult(success=False, message=str(e), warnings=warnings)

    entry: WorkItemEntry | StandaloneEntry
    if epic:
        entry = WorkItemEntry(
            id=new_id,
            name=name.strip(),
            scale=item_scale,
            status=WorkItemStatus.BACKLOG,
        )
    else:
        entry = StandaloneEntry(
            id=new_id,
            name=name.strip(),
            scale=item_scale,
            priority=item_priority,
            status=WorkItemStatus.BACKLOG,
        )
    items.append(entry.model_dump(mode="json"))

    _write_backlog(backlog_path, document)

    return OperationResult(
        success=True,
        message=f"Added work item {new_id}: {name}",
        ids_assigned={"WI": new_id},
        files_modified=[str(backlog_path)],
        warnings=warnings,
    )


def close_item(
    project_root: Path,
    wi_id: str,
) -> OperationResult:
    """Close a work item: update frontmatter, move to completed/, update BACKLOG.md."""
    from agentic_mbse.pm.state import resolve_work_item

    try:
        item_dir = resolve_work_item(project_root, wi_id)
    except ValueError as e:
        return OperationResult(success=False, message=str(e))

    # Normalize to WI-XXX format
    if wi_id.isdigit():
        wi_id = f"WI-{int(wi_id):03d}"

    # Validate it's in work/active/
    active_dir = project_root / "work" / "active"
    try:
        item_dir.relative_to(active_dir)
    except ValueError:
        return OperationResult(
            success=False,
            message=f"{wi_id} is not in work/active/ (found at {item_dir})",
        )

    # Validate item exists in BACKLOG.md, before any file changes
    backlog_path = project_root / "work" / "BACKLOG.md"
    try:
        document, backlog = _load_backlog(backlog_path)
    except ValueError as e:
        return OperationResult(success=False, message=str(e))

    try:
        _, target = _backlog_target(
            _raw_work_items(document, wi_id),
            wi_id,
            parsed=wi_id in _work_item_ids(backlog.data),
            warnings=backlog.warnings,
        )
    except ValueError as e:
        return OperationResult(success=False, message=str(e), warnings=backlog.warnings)

    today = datetime.date.today().isoformat()
    files_modified: list[str] = []

    # Step 1: Update frontmatter in files (while still in active/)
    spec_path = item_dir / "spec.md"
    if spec_path.exists():
        _update_frontmatter_fields(spec_path, {"Status": "completed", "Updated": today})
        files_modified.append(str(spec_path))

    design_path = item_dir / "design.md"
    if design_path.exists():
        _update_frontmatter_fields(design_path, {"Status": "complete", "Updated": today})
        files_modified.append(str(design_path))

    plan_path = item_dir / "plan.md"
    if plan_path.exists():
        _update_frontmatter_fields(plan_path, {"Status": "complete", "Updated": today})
        files_modified.append(str(plan_path))

    # Step 2: Move directory to completed/
    completed_dir = project_root / "work" / "completed"
    completed_dir.mkdir(parents=True, exist_ok=True)

    # Extract the name portion from the directory name (WI-XXX_name)
    dir_name = item_dir.name
    name_part = dir_name.split("_", 1)[1] if "_" in dir_name else dir_name
    today_compact = datetime.date.today().strftime("%Y%m%d")
    dest_name = f"{today_compact}_{wi_id}_{name_part}"
    dest_path = completed_dir / dest_name
    shutil.move(str(item_dir), str(dest_path))

    # Step 3: Write BACKLOG.md
    target["status"] = WorkItemStatus.COMPLETED.value
    target["completed"] = today
    _write_backlog(backlog_path, document)
    files_modified.append(str(backlog_path))

    return OperationResult(
        success=True,
        message=f"Closed {wi_id}. Archived to {dest_path.relative_to(project_root)}",
        files_modified=files_modified,
        warnings=backlog.warnings,
    )


def update_validation(
    project_root: Path,
    *,
    sv_id: str,
    status: str,
) -> OperationResult:
    """Update the status of a verification entry in VALIDATION_MATRIX.md."""
    if not re.match(r"^SV-\d+$", sv_id):
        return OperationResult(
            success=False, message=f"Invalid ID '{sv_id}', expected SV-XXX pattern"
        )

    try:
        new_status = VerificationStatus(status)
    except ValueError:
        valid = ", ".join(v.value for v in VerificationStatus)
        return OperationResult(
            success=False, message=f"Invalid status '{status}', expected one of: {valid}"
        )

    val_path = project_root / "modeling_project" / "VALIDATION_MATRIX.md"
    result = parse_validation_matrix(val_path)
    content = val_path.read_text(encoding="utf-8")

    try:
        _, index = _single_match(
            _raw_table_rows(content, "## Verification Registry", sv_id),
            sv_id,
            val_path.name,
        )
    except ValueError as e:
        return OperationResult(success=False, message=str(e), warnings=result.warnings)

    # Rewrite the file line only if the parser read it as this record, Status in cell 9
    lines = content.split("\n")
    cells = _split_table_row(lines[index].strip())
    entry = next((e for e in result.data if e.id == sv_id), None)
    if entry is None or cells[8:9] != [entry.status.value]:
        return OperationResult(
            success=False,
            message=(
                f"{sv_id}'s row in {val_path.name} does not parse as a record, so its Status "
                "cannot be updated. Fix the row by hand, then retry: a pipe inside a cell must "
                "be written as \\|, and an HTML comment must move out of the row."
            ),
            warnings=result.warnings,
        )

    cells[8] = new_status.value
    try:
        lines[index] = _format_table_row(cells)
    except ValueError:
        # Split and format are inverses; only a comment marker in the row stops it
        return OperationResult(
            success=False,
            message=(
                f"{sv_id}'s row in {val_path.name} holds an HTML comment marker, "
                "so it cannot be rewritten. Move the comment out of the row by hand, "
                "then retry."
            ),
            warnings=result.warnings,
        )

    val_path.write_text("\n".join(lines), encoding="utf-8")

    return OperationResult(
        success=True,
        message=f"Updated {sv_id} status to {new_status.value}",
        files_modified=[str(val_path)],
        warnings=result.warnings,
    )


# ---------------------------------------------------------------------------
# Public operations — Phase 5: Stubs and delegation
# ---------------------------------------------------------------------------


def get_status(project_root: Path):
    """Produce project status dashboard. Delegates to generate_dashboard() (D4.3)."""
    from agentic_mbse.pm.dashboard import generate_dashboard

    return generate_dashboard(project_root)


def supersede_insight(
    project_root: Path,
    *,
    old_id: str,
    new_insight: dict,
    reason: str,
) -> OperationResult:
    """Supersede a domain insight (not yet implemented).

    Full implementation would:
    1. Mark old DI-XXX as superseded in KNOWLEDGE.md (Status → superseded, add Superseded-by)
    2. Assign new DI-XXX ID, create new entry with Supersedes field
    3. Query traceability_matrix.csv for affected elements
    4. Produce impact report to knowledge/research/impacts/DI-XXX_superseded.md
    """
    # TODO: D4.4 stretch — implement full supersession flow per workflows.md § 6.1
    raise NotImplementedError(
        "supersede-insight is not yet implemented. "
        "See workflows.md § 6.1 for the full supersession flow."
    )
