"""Tests for QualityCheckResult migration.

Validates that new structured_issues field works alongside legacy issues.
"""

from agentic_mbse.validation.common import QualityCheckResult
from agentic_mbse.sysml.types import Severity, ValidationCode, ValidationIssue


def test_quality_check_result_has_structured_issues():
    """QualityCheckResult has structured_issues field.

    Input: QualityCheckResult with default values
    Output: structured_issues is empty list
    """
    result = QualityCheckResult(
        level=2,
        level_name="Structural Completeness",
        success=True,
    )

    assert hasattr(result, "structured_issues")
    assert result.structured_issues == []


def test_add_issue_populates_both_lists():
    """add_issue() adds to both structured_issues and legacy issues.

    Input: QualityCheckResult with add_issue() call
    Output: Issue in both lists, legacy issues has string representation
    """
    result = QualityCheckResult(
        level=2,
        level_name="Structural Completeness",
        success=True,
    )

    issue = ValidationIssue(
        level=2,
        severity=Severity.ERROR,
        code=ValidationCode.UNBOUND_INPUT,
        message="Input 'p_fusion' has no binding",
        element_name="net_electric",
        location="physics.sysml:42",
    )

    result.add_issue(issue)

    # Check structured_issues
    assert len(result.structured_issues) == 1
    assert result.structured_issues[0].code == ValidationCode.UNBOUND_INPUT

    # Check legacy issues (backward compatibility)
    assert len(result.issues) == 1
    assert "p_fusion" in result.issues[0]
    assert "physics.sysml:42" in result.issues[0]


def test_legacy_issues_still_work():
    """Direct issues.append() still works for backward compatibility.

    Input: QualityCheckResult with direct issues.append()
    Output: Issue in issues list, structured_issues unchanged
    """
    result = QualityCheckResult(
        level=2,
        level_name="Structural Completeness",
        success=True,
    )

    result.issues.append("ERROR: Legacy issue format")

    assert len(result.issues) == 1
    assert result.issues[0] == "ERROR: Legacy issue format"
    assert len(result.structured_issues) == 0  # Not affected


def test_issue_count_includes_all_issues():
    """issue_count property counts both legacy and structured issues.

    Input: QualityCheckResult with both issue types
    Output: issue_count reflects total
    """
    result = QualityCheckResult(
        level=2,
        level_name="Structural Completeness",
        success=True,
    )

    # Add structured issue
    issue = ValidationIssue(
        level=2,
        severity=Severity.ERROR,
        code=ValidationCode.UNBOUND_INPUT,
        message="Structured issue",
    )
    result.add_issue(issue)

    # issue_count should reflect issues list (which add_issue populates)
    assert result.issue_count == 1


def test_add_issue_warning_format():
    """add_issue() formats WARNING issues correctly.

    Input: ValidationIssue with WARNING severity
    Output: Legacy string starts with WARN:
    """
    result = QualityCheckResult(
        level=2,
        level_name="Structural Completeness",
        success=True,
    )

    issue = ValidationIssue(
        level=2,
        severity=Severity.WARNING,
        code=ValidationCode.LITERAL_BINDING,
        message="Bound to literal value",
        element_name="pump_load",
        location="blanket.sysml:55",
    )

    result.add_issue(issue)

    assert len(result.issues) == 1
    assert result.issues[0].startswith("WARN:")
    assert "blanket.sysml:55" in result.issues[0]


def test_multiple_add_issue_calls():
    """Multiple add_issue() calls accumulate correctly.

    Input: Multiple ValidationIssue additions
    Output: Both lists grow accordingly
    """
    result = QualityCheckResult(
        level=2,
        level_name="Structural Completeness",
        success=True,
    )

    issues = [
        ValidationIssue(
            level=2,
            severity=Severity.ERROR,
            code=ValidationCode.UNBOUND_INPUT,
            message="Issue 1",
        ),
        ValidationIssue(
            level=2,
            severity=Severity.WARNING,
            code=ValidationCode.LITERAL_BINDING,
            message="Issue 2",
        ),
        ValidationIssue(
            level=2,
            severity=Severity.ERROR,
            code=ValidationCode.UNDEFINED_BINDING,
            message="Issue 3",
        ),
    ]

    for issue in issues:
        result.add_issue(issue)

    assert len(result.structured_issues) == 3
    assert len(result.issues) == 3
    assert result.issue_count == 3
