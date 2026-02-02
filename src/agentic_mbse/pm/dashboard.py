"""Dashboard generator — renders project state as plain markdown.

Composes D4.1 parsers and D4.2 state derivation into a single markdown
dashboard. All renderers are pure functions with no I/O.
"""

from __future__ import annotations

from pathlib import Path

from agentic_mbse.pm.parser import parse_requirements, parse_validation_matrix
from agentic_mbse.pm.state import derive_project_state
from agentic_mbse.pm.types import (
    DashboardResult,
    DerivedWorkItemState,
    ParseWarning,
    ProjectState,
    RequirementEntry,
    ValidationEntry,
    VerificationStatus,
    WorkItemStatus,
)

# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


def _format_date(date_str: str | None) -> str | None:
    """Reformat YYYYMMDD to YYYY-MM-DD. Returns None if invalid."""
    if not date_str or len(date_str) != 8:
        return None
    return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"


def _format_item_status(item: DerivedWorkItemState) -> str:
    """Format item state+stage into a display string."""
    if item.state == WorkItemStatus.COMPLETED:
        date = _format_date(item.completed_date)
        return f"completed {date}" if date else "completed"
    if item.state == WorkItemStatus.ACTIVE and item.stage:
        return f"active:{item.stage.value}"
    return str(item.state.value)


def _format_item_line(name: str, status_str: str, completed: bool, pad_width: int) -> str:
    """Format a single work item line with checkbox and dot-leader alignment."""
    checkbox = "[x]" if completed else "[ ]"
    dots_needed = max(2, pad_width - len(name))
    dots = " " + "." * dots_needed + " "
    return f"  {checkbox} {name}{dots}{status_str}"


def _has_file_not_found(warnings: list[ParseWarning], path: str) -> bool:
    """Check whether warnings contain a 'File not found' for the given path."""
    return any(w.message.startswith("File not found") and path in w.file for w in warnings)


# ---------------------------------------------------------------------------
# Private renderers
# ---------------------------------------------------------------------------


def _render_header(project_root: Path) -> str:
    """Render the project header line."""
    return f"## Project: {project_root.name}\n"


def _render_work_items(state: ProjectState) -> str:
    """Render the Work Items section from derived project state."""
    lines: list[str] = ["### Work Items"]

    has_content = bool(state.epics) or bool(state.standalone)
    if not has_content:
        lines.append("No work items.")
        return "\n".join(lines) + "\n"

    for epic in state.epics:
        lines.append(f"Epic: {epic.name}  [{epic.done}/{epic.total} done]")
        if epic.items:
            max_name_len = max(len(item.name) for item in epic.items)
            for item in epic.items:
                status_str = _format_item_status(item)
                completed = item.state == WorkItemStatus.COMPLETED
                lines.append(_format_item_line(item.name, status_str, completed, max_name_len))

    if state.standalone:
        lines.append("Standalone:")
        max_name_len = max(len(item.name) for item in state.standalone)
        for item in state.standalone:
            status_str = _format_item_status(item)
            completed = item.state == WorkItemStatus.COMPLETED
            lines.append(_format_item_line(item.name, status_str, completed, max_name_len))

    return "\n".join(lines) + "\n"


def _render_requirements(entries: list[RequirementEntry], has_file: bool) -> str:
    """Render the Project Rules section from parsed requirements."""
    lines: list[str] = ["### Project Rules (REQUIREMENTS.md)"]

    if not has_file:
        lines.append("No requirements file found.")
        return "\n".join(lines) + "\n"

    total = len(entries)
    with_validation = sum(1 for e in entries if e.validation_method.strip() not in ("", "-"))
    enforceable = sum(1 for e in entries if e.enforcement.strip() not in ("", "-"))
    lines.append(
        f"Total: {total} | With validation method: {with_validation} | Machine-enforceable: {enforceable}"
    )
    return "\n".join(lines) + "\n"


def _render_validation(entries: list[ValidationEntry], has_file: bool) -> str:
    """Render the Validation Status section from parsed validation matrix."""
    lines: list[str] = ["### Validation Status (VALIDATION_MATRIX.md)"]

    if not has_file:
        lines.append("No validation matrix found.")
        return "\n".join(lines) + "\n"

    passing = sum(1 for e in entries if e.status == VerificationStatus.PASSING)
    failing = sum(1 for e in entries if e.status == VerificationStatus.FAILING)
    pending = sum(1 for e in entries if e.status == VerificationStatus.PENDING)
    total = len(entries)

    lines.append(f"Total: {total} | Passing: {passing} | Failing: {failing} | Pending: {pending}")

    for e in entries:
        if e.status == VerificationStatus.FAILING:
            lines.append(f"Failing: {e.id} ({e.description})")

    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def generate_dashboard(project_root: Path) -> DashboardResult:
    """Generate a plain-markdown dashboard for the given project.

    Orchestrates state derivation, requirements parsing, and validation
    matrix parsing, then renders all sections into a single markdown string.
    All warnings from sub-operations are accumulated in the result.
    """
    warnings: list[ParseWarning] = []

    # 1. Derive project state
    state_result = derive_project_state(project_root)
    warnings.extend(state_result.warnings)

    # 2. Parse requirements
    req_path = project_root / "modeling_project" / "REQUIREMENTS.md"
    req_result = parse_requirements(req_path)
    warnings.extend(req_result.warnings)
    req_has_file = not _has_file_not_found(req_result.warnings, str(req_path))

    # 3. Parse validation matrix
    val_path = project_root / "modeling_project" / "VALIDATION_MATRIX.md"
    val_result = parse_validation_matrix(val_path)
    warnings.extend(val_result.warnings)
    val_has_file = not _has_file_not_found(val_result.warnings, str(val_path))

    # 4. Render sections
    sections = [
        _render_header(project_root),
        _render_work_items(state_result.data),
        _render_requirements(req_result.data, req_has_file),
        _render_validation(val_result.data, val_has_file),
    ]

    markdown = "\n".join(sections)
    return DashboardResult(markdown=markdown, warnings=warnings)
