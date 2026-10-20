"""
Common utilities for SysML quality checks

Provides result dataclasses, file discovery, model loading, and output formatting
for all quality check levels.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from agentic_mbse.errors import SemanticEvidenceError
from agentic_mbse.sysml.syside_adapter import SysideAdapter
from agentic_mbse.sysml.types import Severity, ValidationCode, ValidationIssue
from agentic_mbse.validation.positional_check import is_pinned_positional_warning
from agentic_mbse.validation.session import active_session

# ===== Result Dataclasses =====


@dataclass
class QualityCheckResult:
    """Base result class for all quality checks"""

    level: int  # 1-6
    level_name: str  # "Syntax Validation", "Structural Completeness", etc.
    success: bool
    file_path: Path | None = None
    issues: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    metrics: dict = field(default_factory=dict)
    structured_issues: list[ValidationIssue] = field(default_factory=list)
    # Results the level folds into a summary instead of listing as issues (L6 under native).
    summarized: list[ValidationIssue] = field(default_factory=list)
    # A qualifier the run's final line must carry when it passes (empty for none).
    pass_note: str = ""
    # The level's full structured result for the JSON report (L6's subset profile), or None.
    report_detail: dict[str, Any] | None = None

    @property
    def issue_count(self) -> int:
        return len(self.issues)

    @property
    def warning_count(self) -> int:
        return len(self.warnings)

    def add_issue(self, issue: ValidationIssue) -> None:
        """Add a structured issue and also populate legacy issues list.

        This method provides forward compatibility for new code while
        maintaining backward compatibility with code that reads result.issues.

        Args:
            issue: Structured ValidationIssue with full context
        """
        self.structured_issues.append(issue)
        self.issues.append(str(issue))  # Backward compatibility


@dataclass
class AggregatedResult:
    """Aggregated results from multiple quality checks"""

    results: list[QualityCheckResult]
    total_checks: int
    passed: int
    failed: int
    constraint_extractions: int  # the run session's real extractions (design I10)
    wall_time_s: float

    @property
    def overall_success(self) -> bool:
        return self.failed == 0

    @property
    def pinned_note(self) -> str:
        """The note for the pinned positional warnings across every level run, or "" if none."""
        pinned = sum(pinned_positional_warnings(result) for result in self.results)
        return pinned_note(pinned) if pinned else ""

    @property
    def pass_notes(self) -> list[str]:
        """What a passing run's final line must say: the pinned note, then each level's note."""
        notes = [self.pinned_note] if self.pinned_note else []
        return notes + [result.pass_note for result in self.results if result.pass_note]


def check_error_issue(
    check: str, subject: str, error: Exception, location: str = ""
) -> ValidationIssue:
    """`L6_CHECK_ERROR`: `check` could not inspect `subject` because it raised `error` (design D4)."""
    return ValidationIssue(
        level=6,
        severity=Severity.ERROR,
        code=ValidationCode.L6_CHECK_ERROR,
        message=f"{check} could not inspect {subject}: {type(error).__name__}: {error}",
        element_name=subject,
        location=location,
        reason_code=type(error).__name__,
    )


def check_unverified_issue(
    check: str, subject: str, error: SemanticEvidenceError, location: str = ""
) -> ValidationIssue:
    """`L6_CHECK_UNVERIFIED`: a shared walker that `check` called declined `subject` (D15, I1)."""
    return ValidationIssue(
        level=6,
        severity=Severity.WARNING,
        code=ValidationCode.L6_CHECK_UNVERIFIED,
        message=f"{check} could not inspect {subject}: {error}",
        element_name=subject,
        location=location,
        suggestion=(
            "The check says nothing about this element; this is neither a model defect "
            "nor a crash of the check"
        ),
        reason_code=error.code.value,
    )


# ===== File Discovery =====


def discover_sysml_files(base_path: str, pattern: str = "**/*.sysml") -> list[Path]:
    """
    Discover all SysML files recursively

    Args:
        base_path: Root directory to search
        pattern: Glob pattern for matching files

    Returns:
        Sorted list of Path objects
    """
    path = Path(base_path)
    if not path.exists():
        raise ValueError(f"Path does not exist: {base_path}")

    files = sorted(path.glob(pattern))
    return [f for f in files if f.is_file()]


# ===== Model Loading =====


def load_sysml_model(files: list[Path]) -> tuple[Any, Any]:
    """
    Load SysML model from files using syside library

    Args:
        files: List of .sysml file paths

    Returns:
        (model, diagnostics) tuple

    Inside a `ValidationSession` (the runner's run), the same file list is loaded once and
    shared by every level (design D14).

    Raises:
        Exception: If model loading fails catastrophically
    """
    session = active_session()
    if session is not None:
        return session.load(files)
    # Use try_load_model to get model even with errors
    model, diagnostics = SysideAdapter.load_model(files)
    return model, diagnostics


# ===== Output Formatting =====


def print_header(title: str, level: int) -> None:
    """Print formatted section header"""
    print(f"\n{'=' * 60}")
    print(f"Level {level}: {title}")
    print("=" * 60)


def print_result(result: QualityCheckResult) -> None:
    """
    Print formatted quality check result

    Reuses output formatting conventions from existing scripts
    """
    symbol = "✅" if result.success else "❌"
    print(f"\n{symbol} Level {result.level}: {result.level_name}{_pinned_note(result)}")

    # Print metrics if present
    if result.metrics:
        for key, value in result.metrics.items():
            print(f"   {key}: {value}")

    # Print issues (paginated)
    if result.issues:
        print(f"\n   Issues found: {len(result.issues)}")
        for issue in result.issues[:5]:
            print(f"   - {issue}")
        if len(result.issues) > 5:
            print(f"   ... and {len(result.issues) - 5} more")

    # Print warnings
    if result.warnings:
        print(f"\n   Warnings: {len(result.warnings)}")
        for warning in result.warnings[:3]:
            print(f"   ⚠️  {warning}")
        if len(result.warnings) > 3:
            print(f"   ... and {len(result.warnings) - 3} more")


def pinned_positional_warnings(result: QualityCheckResult) -> int:
    """How many of the level's issues are pinned positional warnings (design D1)."""
    return sum(1 for issue in result.structured_issues if is_pinned_positional_warning(issue))


def pinned_note(pinned: int) -> str:
    """What a pass that rests on pinned positional warnings must say about them."""
    return f"{pinned} pinned positional warnings; not a value or route-parity check"


def _pinned_note(result: QualityCheckResult) -> str:
    """The header's note when a level passes with pinned positional warnings."""
    pinned = pinned_positional_warnings(result)
    if not (result.success and pinned):
        return ""
    return f" ({pinned_note(pinned)})"


# ===== Element Analysis Helpers =====


def get_qualified_name(element: Any) -> str:
    """Get qualified name of element for error reporting"""
    try:
        return str(element.qualified_name) if hasattr(element, "qualified_name") else str(element)
    except Exception:
        return f"<unnamed {type(element).__name__}>"


def get_element_location(element: Any) -> str:
    """Get file:line location of element"""
    try:
        doc = element.document
        cst = element.cst_node
        if doc and cst:
            url = doc.url
            # Extract line number from cst_node
            # syside uses start_point.line (0-indexed)
            if hasattr(cst, "start_point") and cst.start_point:
                return f"{url}:{cst.start_point.line + 1}"
            # Fallback: try range.start.line (older API)
            elif hasattr(cst, "range") and cst.range:
                return f"{url}:{cst.range.start.line + 1}"  # type: ignore
    except Exception:
        pass
    return "<unknown location>"


# ===== Exit Codes =====

EXIT_SUCCESS = 0
EXIT_FAILURE = 1
