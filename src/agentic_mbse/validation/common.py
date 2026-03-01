"""
Common utilities for SysML quality checks

Provides result dataclasses, file discovery, model loading, and output formatting
for all quality check levels.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

from agentic_mbse.sysml.syside_adapter import SysideAdapter

if TYPE_CHECKING:
    from agentic_mbse.sysml.types import ValidationIssue

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
    structured_issues: list["ValidationIssue"] = field(default_factory=list)

    @property
    def issue_count(self) -> int:
        return len(self.issues)

    @property
    def warning_count(self) -> int:
        return len(self.warnings)

    def add_issue(self, issue: "ValidationIssue") -> None:
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

    @property
    def overall_success(self) -> bool:
        return self.failed == 0


# ===== File Discovery =====


def discover_sysml_files(base_path: str, pattern: str = "**/*.sysml") -> list[Path]:
    """
    Discover all SysML files recursively

    Reuses pattern from test_sysml_parsing.py:82-100

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

    Raises:
        Exception: If model loading fails catastrophically
    """
    # Use try_load_model to get model even with errors
    model, diagnostics = SysideAdapter.load_model(files)
    return model, diagnostics


# ===== Output Formatting =====


def print_header(title: str, level: int) -> None:
    """Print formatted section header"""
    print(f"\n{'='*60}")
    print(f"Level {level}: {title}")
    print("=" * 60)


def print_result(result: QualityCheckResult) -> None:
    """
    Print formatted quality check result

    Reuses output formatting conventions from existing scripts
    """
    symbol = "✅" if result.success else "❌"
    print(f"\n{symbol} Level {result.level}: {result.level_name}")

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


# ===== Element Analysis Helpers =====


def get_qualified_name(element: Any) -> str:
    """Get qualified name of element for error reporting"""
    try:
        return (
            str(element.qualified_name)
            if hasattr(element, "qualified_name")
            else str(element)
        )
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
