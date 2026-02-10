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

import yaml

from agentic_mbse.pm.parser import (
    parse_architecture,
    parse_backlog,
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
    GoalInput,
    ImpactResult,
    InsightEntry,
    InsightInput,
    InsightStatus,
    OperationResult,
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

# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


def _next_id(prefix: str, existing_ids: list[str]) -> str:
    """Given a prefix ('DI', 'PR', etc.) and list of existing IDs, return next sequential ID."""
    if not existing_ids:
        return f"{prefix}-001"
    nums = []
    pattern = re.compile(rf"^{re.escape(prefix)}-(\d+)$")
    for eid in existing_ids:
        m = pattern.match(eid)
        if m:
            nums.append(int(m.group(1)))
    if not nums:
        return f"{prefix}-001"
    return f"{prefix}-{max(nums) + 1:03d}"


def _update_frontmatter_fields(path: Path, updates: dict[str, str]) -> None:
    """Update specific fields in a file's YAML frontmatter, preserving the body and unknown fields."""
    content = path.read_text(encoding="utf-8")
    lines = content.split("\n")

    if not lines or lines[0].strip() != "---":
        raise ValueError(f"No opening frontmatter delimiter in {path}")

    closing_idx = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
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
            parts.append(
                f"| {sa.id} | {sa.name} | {scale_val} | {priority_val} | {status_val} | {notes} |"
            )
        parts.append("")

    return "\n".join(parts)


def _write_backlog(path: Path, data: BacklogData) -> None:
    """Write complete BACKLOG.md: YAML frontmatter + rendered body."""
    raw = data.model_dump(mode="json")
    yaml_text = yaml.dump(raw, default_flow_style=False, sort_keys=False, allow_unicode=True)
    body = _render_backlog_body(data)
    path.write_text(f"---\n{yaml_text}---\n{body}", encoding="utf-8")


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
    """Format a markdown table data row."""
    return "| " + " | ".join(columns) + " |"


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


def _append_table_row(path: Path, section_heading: str, row: str) -> None:
    """Append a row to a markdown table under a given section heading."""
    content = path.read_text(encoding="utf-8")
    lines = content.split("\n")

    # Find section heading
    section_start = None
    for i, line in enumerate(lines):
        if line.strip() == section_heading:
            section_start = i
            break

    if section_start is None:
        raise ValueError(f"Section heading '{section_heading}' not found in {path}")

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

    if last_table_line is None:
        raise ValueError(f"No table found under '{section_heading}' in {path}")

    # Insert after the last table line
    lines.insert(last_table_line + 1, row)
    path.write_text("\n".join(lines), encoding="utf-8")


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
    existing_ids = [e.id for e in result.data]
    new_id = _next_id("DI", existing_ids)

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
        warnings=result.warnings,
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
    existing_ids = [e.id for e in result.data]
    new_id = _next_id("PR", existing_ids)

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

    return OperationResult(
        success=True,
        message=f"Added requirement {new_id}: {requirement}",
        ids_assigned={"PR": new_id},
        files_modified=[str(req_path)],
        warnings=result.warnings,
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
    existing_ids = [e.id for e in result.data]
    new_id = _next_id("AD", existing_ids)

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
        warnings=result.warnings,
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
    existing_ids = [e.id for e in result.data]
    new_id = _next_id("SV", existing_ids)

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

    return OperationResult(
        success=True,
        message=f"Added verification {new_id}: {description}",
        ids_assigned={"SV": new_id},
        files_modified=[str(val_path)],
        warnings=result.warnings,
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
    existing_ids = [e.id for e in k_result.data]

    # Build all entries in memory first
    entries: list[InsightEntry] = []
    ids_assigned: dict[str, str] = {}
    all_ids = list(existing_ids)
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
                    warnings=k_result.warnings,
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
        warnings=k_result.warnings,
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
    existing_g = [e.id for e in o_result.data.goals]
    existing_aq = [e.id for e in o_result.data.questions]

    ids_assigned: dict[str, str] = {}
    files_modified: list[str] = []

    if goals:
        all_g_ids = list(existing_g)
        for g in goals:
            for name, val in [("goal", g.goal), ("priority", g.priority), ("source", g.source)]:
                if not val or not val.strip():
                    return OperationResult(
                        success=False,
                        message=f"Goal '{g.goal}': required field '{name}' is empty",
                        warnings=o_result.warnings,
                    )
            new_id = _next_id("G", all_g_ids)
            all_g_ids.append(new_id)
            row = _format_table_row(
                [
                    new_id,
                    g.goal.strip(),
                    g.priority.strip(),
                    g.status.strip(),
                    g.source.strip(),
                    g.traced_requirements.strip(),
                ]
            )
            _append_table_row(overview_path, "## Goals Registry", row)
            ids_assigned[new_id] = g.goal
        files_modified.append(str(overview_path))

    if questions:
        all_aq_ids = list(existing_aq)
        for q in questions:
            for name, val in [("question", q.question), ("source", q.source)]:
                if not val or not val.strip():
                    return OperationResult(
                        success=False,
                        message=f"Question '{q.question}': required field '{name}' is empty",
                        warnings=o_result.warnings,
                    )
            new_id = _next_id("AQ", all_aq_ids)
            all_aq_ids.append(new_id)
            row = _format_table_row(
                [
                    new_id,
                    q.question.strip(),
                    q.implies.strip(),
                    q.source.strip(),
                    q.status.strip(),
                ]
            )
            _append_table_row(overview_path, "## Analysis Questions", row)
            ids_assigned[new_id] = q.question
        if str(overview_path) not in files_modified:
            files_modified.append(str(overview_path))

    id_list = ", ".join(ids_assigned.keys())
    return OperationResult(
        success=True,
        message=f"Registered intent: {id_list}",
        ids_assigned=ids_assigned,
        files_modified=files_modified,
        warnings=o_result.warnings,
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
    b_result = parse_backlog(backlog_path)
    data = b_result.data

    # Collect all WI-XXX IDs
    all_ids: list[str] = []
    for ep in data.epics:
        for item in ep.items:
            all_ids.append(item.id)
    for sa in data.standalone:
        all_ids.append(sa.id)

    new_id = _next_id("WI", all_ids)

    if epic:
        # Find the epic
        target_epic = None
        for ep in data.epics:
            if ep.name == epic:
                target_epic = ep
                break
        if target_epic is None:
            return OperationResult(
                success=False,
                message=f"Epic '{epic}' not found in BACKLOG.md",
                warnings=b_result.warnings,
            )
        target_epic.items.append(
            WorkItemEntry(
                id=new_id,
                name=name.strip(),
                scale=item_scale,
                status=WorkItemStatus.BACKLOG,
            )
        )
    else:
        data.standalone.append(
            StandaloneEntry(
                id=new_id,
                name=name.strip(),
                scale=item_scale,
                priority=item_priority,
                status=WorkItemStatus.BACKLOG,
            )
        )

    _write_backlog(backlog_path, data)

    return OperationResult(
        success=True,
        message=f"Added work item {new_id}: {name}",
        ids_assigned={"WI": new_id},
        files_modified=[str(backlog_path)],
        warnings=b_result.warnings,
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

    # Validate item exists in BACKLOG.md
    backlog_path = project_root / "work" / "BACKLOG.md"
    b_result = parse_backlog(backlog_path)
    data = b_result.data

    found = False
    for ep in data.epics:
        for item in ep.items:
            if item.id == wi_id:
                item.status = WorkItemStatus.COMPLETED
                item.completed = datetime.date.today().isoformat()
                found = True
                break
        if found:
            break
    if not found:
        for sa in data.standalone:
            if sa.id == wi_id:
                sa.status = WorkItemStatus.COMPLETED
                sa.completed = datetime.date.today().isoformat()
                found = True
                break

    if not found:
        return OperationResult(
            success=False,
            message=f"{wi_id} not found in BACKLOG.md",
            warnings=b_result.warnings,
        )

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
    _write_backlog(backlog_path, data)
    files_modified.append(str(backlog_path))

    return OperationResult(
        success=True,
        message=f"Closed {wi_id}. Archived to {dest_path.relative_to(project_root)}",
        files_modified=files_modified,
        warnings=b_result.warnings,
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
    content = val_path.read_text(encoding="utf-8")
    lines = content.split("\n")

    # Find and update the row
    found = False
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cells = [c.strip() for c in stripped.split("|")]
        # Remove empty leading/trailing from split
        if cells and cells[0] == "":
            cells = cells[1:]
        if cells and cells[-1] == "":
            cells = cells[:-1]

        if len(cells) >= 9 and cells[0] == sv_id:
            # Update the Status column (index 8)
            cells[8] = new_status.value
            lines[i] = "| " + " | ".join(cells) + " |"
            found = True
            break

    if not found:
        return OperationResult(
            success=False,
            message=f"{sv_id} not found in VALIDATION_MATRIX.md",
        )

    val_path.write_text("\n".join(lines), encoding="utf-8")

    return OperationResult(
        success=True,
        message=f"Updated {sv_id} status to {new_status.value}",
        files_modified=[str(val_path)],
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
    """Supersede a domain insight (D4.4 workflows.md § 6.1).

    Marks the old insight as superseded, creates a new insight that supersedes it,
    queries the traceability matrix for affected elements, and generates an impact
    report to knowledge/research/impacts/.

    Args:
        project_root: Project root directory
        old_id: ID of the insight to supersede (e.g., "DI-003")
        new_insight: Dictionary with fields for the new insight (title, source,
                     context, model_implications, analysis_implications, rationale)
        reason: Reason for supersession (used in impact report)

    Returns:
        OperationResult with success status, new DI-XXX ID, and impact report path
    """
    # Validate old_id format
    if not re.match(r"^DI-\d+$", old_id):
        return OperationResult(
            success=False,
            message=f"Invalid old_id '{old_id}', expected DI-XXX pattern",
        )

    # Validate new_insight required fields
    required_fields = ["title", "source", "context", "model_implications", "analysis_implications"]
    for field in required_fields:
        if field not in new_insight or not new_insight[field].strip():
            return OperationResult(
                success=False,
                message=f"Required field '{field}' missing or empty in new_insight",
            )

    knowledge_path = project_root / "knowledge" / "KNOWLEDGE.md"
    k_result = parse_knowledge(knowledge_path)

    # Find the old insight
    old_entry = None
    for entry in k_result.data:
        if entry.id == old_id:
            old_entry = entry
            break

    if old_entry is None:
        return OperationResult(
            success=False,
            message=f"Insight {old_id} not found in KNOWLEDGE.md",
            warnings=k_result.warnings,
        )

    if old_entry.status == InsightStatus.SUPERSEDED:
        return OperationResult(
            success=False,
            message=f"Insight {old_id} is already superseded by {old_entry.superseded_by}",
            warnings=k_result.warnings,
        )

    # Assign new DI-XXX ID
    existing_ids = [e.id for e in k_result.data]
    new_id = _next_id("DI", existing_ids)

    # Update old entry
    old_entry.status = InsightStatus.SUPERSEDED
    old_entry.superseded_by = new_id

    # Create new entry
    new_entry = InsightEntry(
        id=new_id,
        title=new_insight["title"].strip(),
        source=new_insight["source"].strip(),
        rationale=new_insight.get("rationale", "").strip() or None,
        context=new_insight["context"].strip(),
        model_implications=new_insight["model_implications"].strip(),
        analysis_implications=new_insight["analysis_implications"].strip(),
        status=InsightStatus.CAPTURED,
        supersedes=old_id,
    )

    # Regenerate KNOWLEDGE.md with updated and new entries
    entries_by_id = {e.id: e for e in k_result.data}
    entries_by_id[old_id] = old_entry  # Update old entry
    entries_by_id[new_id] = new_entry  # Add new entry

    # Sort by DI-XXX numeric part
    def _sort_key(entry: InsightEntry) -> int:
        m = re.match(r"DI-(\d+)", entry.id)
        return int(m.group(1)) if m else 0

    sorted_entries = sorted(entries_by_id.values(), key=_sort_key)

    # Regenerate file content
    lines = []
    if knowledge_path.exists():
        content = knowledge_path.read_text(encoding="utf-8")
        # Preserve everything before the first DI-XXX section
        m = re.search(r"^### DI-\d+:", content, re.MULTILINE)
        if m:
            lines.append(content[: m.start()].rstrip())
        else:
            lines.append(content.rstrip())

    # Append all DI-XXX entries
    for entry in sorted_entries:
        lines.append(_format_insight_entry(entry))

    knowledge_path.write_text("\n\n".join(lines) + "\n", encoding="utf-8")

    # Query traceability matrix for impact
    impact = impact_query(project_root, query_id=old_id)

    # Generate impact report
    impacts_dir = project_root / "knowledge" / "research" / "impacts"
    impacts_dir.mkdir(parents=True, exist_ok=True)
    impact_file = impacts_dir / f"{old_id}_superseded.md"

    today = datetime.datetime.now().strftime("%Y-%m-%d")
    report_lines = [
        f"# Impact Report: {old_id} Superseded",
        "",
        f"**Date**: {today}",
        f"**Superseded by**: {new_id}",
        f"**Reason**: {reason}",
        "",
        "## Old Insight",
        "",
        f"**{old_entry.title}**",
        "",
        f"- **Source**: {old_entry.source}",
        f"- **Context**: {old_entry.context}",
        "",
        "## New Insight",
        "",
        f"**{new_entry.title}**",
        "",
        f"- **Source**: {new_entry.source}",
        f"- **Context**: {new_entry.context}",
        "",
        "## Affected Model Elements",
        "",
    ]

    if impact.affected_elements:
        report_lines.append("| Element | File | Requirement | Knowledge |")
        report_lines.append("|---------|------|-------------|-----------|")
        for elem in impact.affected_elements:
            report_lines.append(
                f"| {elem.element} | {elem.file or 'N/A'} | {elem.requirement or 'N/A'} | {elem.knowledge} |"
            )
    else:
        report_lines.append("*No model elements traced to this insight.*")

    report_lines.extend(["", "## Affected Work Items", ""])

    if impact.affected_work_items:
        for item in impact.affected_work_items:
            report_lines.append(f"- {item}")
    else:
        report_lines.append("*No work items traced to this insight.*")

    report_lines.extend(
        [
            "",
            "## Recommended Action",
            "",
            f"Review affected model elements and consider creating a work item to update "
            f"assumptions based on {new_id}.",
        ]
    )

    impact_file.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    return OperationResult(
        success=True,
        message=f"Superseded {old_id} with {new_id}. Impact report: {impact_file.relative_to(project_root)}",
        ids_assigned={"DI": new_id},
        files_modified=[str(knowledge_path), str(impact_file)],
        warnings=k_result.warnings + impact.warnings,
    )
