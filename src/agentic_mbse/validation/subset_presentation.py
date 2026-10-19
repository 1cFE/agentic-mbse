"""How L6 shows the subset contract's result under an execution target (Item 3 design D8-D13).

The contract decides what is true; this module decides only how loud it is. It reads the
contract's result and the legacy checks' issues and returns what L6 prints and records:

- `issues`: shown, in D13 order (check errors, then ERROR, then WARNING; within a tier the
  legacy issues in check order, then contract findings refused, unverified, unconfirmed,
  excluded, omitted, each in the contract's own order).
- `summarized`: the results `native` folds into its one INFO summary line (D5).
- `metrics`: the verdict, coverage and scope lines, plus the native summary line.
- `pass_note`: what a passing run's final line must add.
- `profile`: the JSON report's full record of the run (`validate-report/v1`).

No outcome logic lives here (I3): every severity comes from `display(category, target)`.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any
from uuid import UUID

from agentic_mbse.sysml.fact_refs import SafeLocation
from agentic_mbse.sysml.subset_coverage import (
    FOLLOW_UP_SITES,
    NO_RULE_FAMILIES,
    SUBSET_COVERAGE_VERSION,
)
from agentic_mbse.sysml.subset_profile import (
    ALWAYS_UNCONFIRMED_CONTEXTS,
    PACKAGED_RULES,
    SUBSET_PROFILE_VERSION,
    Outcome,
    RuleRecords,
    SubsetFinding,
    SubsetProfileResult,
    UnverifiedCheck,
    Verdict,
)
from agentic_mbse.sysml.types import Severity, ValidationCode, ValidationIssue

from .execution_target import LEGACY_CATEGORY, Category, Display, Target, display

#: The rule whose subjects replace the legacy String error (design D10).
STRING_RULE = "string-value-omission"

#: The qualifier the final line carries when the run says nothing about generated output.
NOT_ESTABLISHED = "generated compatibility not established"

UNSET_NOTE = (
    "generator findings are shown as warnings because execution-target is not set. Add "
    'execution-target = "generated" or "native" under [tool.agentic-mbse] in pyproject.toml, '
    "or run agentic-mbse init --execution-target=generated|native."
)

_CODE = {
    Outcome.REFUSED: ValidationCode.L6_SUBSET_REFUSED,
    Outcome.UNCONFIRMED: ValidationCode.L6_SUBSET_UNCONFIRMED,
    Outcome.EXCLUDED: ValidationCode.L6_SUBSET_EXCLUDED,
    Outcome.OMITTED: ValidationCode.L6_SUBSET_OMITTED,
}
_CATEGORY = {
    Outcome.REFUSED: Category.REFUSED,
    Outcome.UNCONFIRMED: Category.UNCONFIRMED,
    Outcome.EXCLUDED: Category.EXCLUDED,
    Outcome.OMITTED: Category.OMITTED,
    Outcome.ADMITTED: Category.ADMITTED,
}
# D13: the order contract results print in within a severity tier. Unverified sits between
# refused and unconfirmed; the unassessed count follows the findings.
_REFUSED, _UNVERIFIED, _UNCONFIRMED, _EXCLUDED, _OMITTED, _UNASSESSED = range(6)
_RANK = {
    Outcome.REFUSED: _REFUSED,
    Outcome.UNCONFIRMED: _UNCONFIRMED,
    Outcome.EXCLUDED: _EXCLUDED,
    Outcome.OMITTED: _OMITTED,
}
_SEVERITY = {Display.ERROR: Severity.ERROR, Display.WARNING: Severity.WARNING}


@dataclass
class Presentation:
    issues: list[ValidationIssue] = field(default_factory=list)
    summarized: list[ValidationIssue] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)
    pass_note: str = ""
    profile: dict[str, Any] = field(default_factory=dict)


def string_subjects(result: SubsetProfileResult | None) -> frozenset[UUID] | None:
    """The String-valued features the contract reports omitted, or None if it did not run (D10)."""
    if result is None:
        return None
    return frozenset(f.subject.element_id for f in result.findings if f.rule_id == STRING_RULE)


def shadowed_by(result: SubsetProfileResult) -> dict[int, SubsetFinding]:
    """Finding index → the refused finding of another rule on the same declaration (D9)."""
    refused: dict[UUID, list[SubsetFinding]] = {}
    for finding in result.findings:
        if finding.outcome is Outcome.REFUSED:
            refused.setdefault(finding.subject.element_id, []).append(finding)
    shadows: dict[int, SubsetFinding] = {}
    for index, finding in enumerate(result.findings):
        others = [
            f for f in refused.get(finding.subject.element_id, ()) if f.rule_id != finding.rule_id
        ]
        if others:
            shadows[index] = others[0]
    return shadows


def _where(location: SafeLocation | None) -> str:
    if location is None or location.file is None:
        return ""
    return location.file if location.line is None else f"{location.file}:{location.line}"


def _subject(finding: SubsetFinding) -> str:
    if finding.subject.qualified_name:
        return finding.subject.qualified_name
    return f"anonymous {finding.subject.kind} at {_where(finding.location) or 'unknown location'}"


def _finding_message(finding: SubsetFinding, shadow: SubsetFinding | None, version: str) -> str:
    message = (
        f"{finding.outcome.value} ({version}): {finding.rule_id}/{finding.shape_id} in "
        f"{finding.context_id.value}: {finding.reason}: {_subject(finding)}"
    )
    if finding.outcome is Outcome.UNCONFIRMED:
        message += "; no generator probe has observed this"
        if finding.context_id in ALWAYS_UNCONFIRMED_CONTEXTS:
            message += f"; context {finding.context_id.value} is unconfirmed by design"
    if shadow is not None:
        message += (
            f"; shadowed by refused {shadow.rule_id}/{shadow.shape_id} on the same declaration"
        )
    return message


def _unverified_message(check: UnverifiedCheck, version: str) -> str:
    context = check.context_id.value if check.context_id else "no context"
    subject = check.subject.qualified_name if check.subject and check.subject.qualified_name else ""
    tail = f": {subject}" if subject else ""
    return f"unverified ({version}): {check.rule_id} in {context}: {check.cause.value}{tail}: {check.detail}"


def _shown(issue: ValidationIssue, shown: Display) -> ValidationIssue:
    return issue.model_copy(update={"severity": _SEVERITY[shown]})


def _info(issue: ValidationIssue) -> ValidationIssue:
    return issue.model_copy(update={"severity": Severity.INFO})


def _counts(result: SubsetProfileResult) -> dict[Outcome, int]:
    return dict(result.counts.by_outcome)


def _verdict_line(result: SubsetProfileResult | None) -> str:
    if result is None:
        return "not computed (see L6_CHECK_ERROR)"
    counts = _counts(result)
    refused, unconfirmed = counts.get(Outcome.REFUSED, 0), counts.get(Outcome.UNCONFIRMED, 0)
    unverified, unassessed = result.counts.unverified, result.counts.unassessed_constraints
    tail = f"{unassessed} unassessed constraints; not a generation check"
    match result.verdict:
        case Verdict.REFUSED_INCOMPLETE:
            head = (
                f"refused_incomplete: {refused} refused, then incomplete: {unverified} unverified"
            )
        case Verdict.CLEAR:
            head = (
                f"clear: no refusals found by the implemented rules; {refused} refused; "
                f"{unverified} unverified"
            )
        case Verdict.UNCONFIRMED:
            head = f"unconfirmed: {unconfirmed} unconfirmed; {refused} refused; {unverified} unverified"
        case _:
            head = f"{result.verdict.value}: {refused} refused; {unverified} unverified"
    return f"{head}; {tail}"


def _coverage_line() -> str:
    families = ", ".join(NO_RULE_FAMILIES)
    return (
        f"no rule yet for {families}, and {len(FOLLOW_UP_SITES)} follow-up sites; "
        "a clear verdict says nothing about these"
    )


def _scope_line(result: SubsetProfileResult | None) -> str:
    if result is None:
        return "not computed (see L6_CHECK_ERROR)"
    scope = result.scope
    if scope.roots_available:
        narrowed = "narrowed" if scope.narrowed else "not narrowed"
        roots = (
            f"roots used {len(scope.roots_used)} of {len(scope.generator_root_ids)} ({narrowed})"
        )
    else:
        roots = "roots not available"
    missing = ", ".join(kind.value for kind in scope.not_enumerated) or "none"
    return (
        f"executable profile {result.executable_profile_version}; {roots}; "
        f"fact kinds not enumerated: {missing}"
    )


def _rule_suggestion(rules: RuleRecords) -> dict[str, tuple[str, str]]:
    return {rule.rule_id: (rule.remedy, rule.semantic_limits) for rule in rules.rules}


def _legacy_category(issue: ValidationIssue) -> Category:
    if issue.code is ValidationCode.L6_CHECK_ERROR:
        return Category.CHECK_FAILURE
    return LEGACY_CATEGORY.get(issue.code, Category.LEGACY_KEPT)


def _location_detail(location: SafeLocation | None) -> dict[str, Any] | None:
    if location is None:
        return None
    return {"file": location.file, "line": location.line, "qualified_name": location.qualified_name}


def present(
    target: Target,
    result: SubsetProfileResult | None,
    legacy: Sequence[ValidationIssue],
    rules: RuleRecords = PACKAGED_RULES,
) -> Presentation:
    """Render the contract `result` (None when it failed) and the `legacy` issues under `target`.

    `legacy` is every issue the legacy checks and the contract's own failure produced, in check
    order. Check failures (`L6_CHECK_ERROR`) are ERROR under every target and print first.
    """
    out = Presentation()
    version = result.subset_profile_version if result else SUBSET_PROFILE_VERSION
    suggestions = _rule_suggestion(rules)

    # Each shown issue carries (tier, group, rank, position) for D13 ordering.
    ranked: list[tuple[tuple[int, int, int, int], ValidationIssue]] = []
    legacy_summarized = 0
    for position, issue in enumerate(legacy):
        shown = display(_legacy_category(issue), target)
        if shown is Display.NATIVE_SUMMARY:
            out.summarized.append(_info(issue))
            legacy_summarized += 1
            continue
        if shown is not Display.BASE:
            issue = _shown(issue, shown)
        ranked.append(((_tier(issue), 0, 0, position), issue))

    findings_detail: list[dict[str, Any]] = []
    unverified_detail: list[dict[str, Any]] = []
    summary = dict.fromkeys(_CODE, 0)
    if result is not None:
        shadows = shadowed_by(result)
        for index, finding in enumerate(result.findings):
            shown = display(_CATEGORY[finding.outcome], target)
            shadow = shadows.get(index)
            remedy, limits = suggestions[finding.rule_id]
            findings_detail.append(_finding_detail(finding, shadow, shown, remedy, limits))
            if shown is Display.COUNT_ONLY:
                continue
            issue = ValidationIssue(
                level=6,
                severity=Severity.INFO,
                code=_CODE[finding.outcome],
                message=_finding_message(finding, shadow, version),
                element_name=finding.subject.qualified_name or "",
                location=_where(finding.location),
                suggestion=f"{remedy} Semantic limits: {limits}",
                reason_code=finding.reason,
            )
            if shown is Display.NATIVE_SUMMARY:
                out.summarized.append(issue)
                summary[finding.outcome] += 1
                continue
            issue = _shown(issue, shown)
            ranked.append(((_tier(issue), 1, _RANK[finding.outcome], index), issue))

        shown_unverified = display(Category.UNVERIFIED, target)
        for index, check in enumerate(result.unverified):
            unverified_detail.append(_unverified_detail(check, shown_unverified))
            if target is Target.NATIVE:
                continue  # one aggregated WARNING below (D5)
            issue = ValidationIssue(
                level=6,
                severity=_SEVERITY[shown_unverified],
                code=ValidationCode.L6_SUBSET_UNVERIFIED,
                message=_unverified_message(check, version),
                element_name=(check.subject.qualified_name if check.subject else None) or "",
                location=_where(check.subject),
                suggestion=(
                    "The check could not run on this site, so the verdict is incomplete until "
                    "it can; every unverified check is listed in --json-report"
                ),
                reason_code=str(check.cause.value),
            )
            ranked.append(((_tier(issue), 1, _UNVERIFIED, index), issue))
        if target is Target.NATIVE and result.unverified:
            issue = ValidationIssue(
                level=6,
                severity=_SEVERITY[shown_unverified],
                code=ValidationCode.L6_SUBSET_UNVERIFIED,
                message=(
                    f"unverified ({version}): {len(result.unverified)} subset checks could not "
                    "run; each is listed in --json-report"
                ),
            )
            ranked.append(((_tier(issue), 1, _UNVERIFIED, 0), issue))

        unassessed = result.counts.unassessed_constraints
        if unassessed:
            shown = display(Category.UNASSESSED, target)
            issue = ValidationIssue(
                level=6,
                severity=Severity.INFO,
                code=ValidationCode.L6_SUBSET_UNASSESSED,
                message=(
                    f"unassessed ({version}): {unassessed} constraints the executable profile "
                    "could not assess; the constraint-predicate rule says nothing about them"
                ),
                suggestion="Rewrite each as a numerical statement the executable profile assesses",
            )
            if shown is Display.NATIVE_SUMMARY:
                out.summarized.append(issue)
            else:
                ranked.append(((_tier(issue), 1, _UNASSESSED, 0), _shown(issue, shown)))

    out.issues = [issue for _, issue in sorted(ranked, key=lambda item: item[0])]

    key = f"Generator subset ({version}, {SUBSET_COVERAGE_VERSION})"
    if target is Target.UNSET:
        out.metrics["Execution target note"] = UNSET_NOTE
    out.metrics[key] = _verdict_line(result)
    out.metrics["Coverage limit"] = _coverage_line()
    out.metrics["Generator subset scope"] = _scope_line(result)
    if target is Target.NATIVE:
        out.metrics["Generator-only findings (native: INFO summary)"] = _native_summary(
            result, summary, legacy_summarized
        )

    verdict = None if result is None else result.verdict
    if target is Target.UNSET or (target is Target.GENERATED and verdict is not Verdict.REFUSED):
        out.pass_note = NOT_ESTABLISHED

    out.profile = {
        "subset_profile_version": version,
        "executable_profile_version": result.executable_profile_version if result else None,
        "coverage": {
            "version": SUBSET_COVERAGE_VERSION,
            "no_rule_families": list(NO_RULE_FAMILIES),
            "follow_up_sites": list(FOLLOW_UP_SITES),
        },
        "scope": _scope_detail(result),
        "verdict": None if verdict is None else verdict.value,
        "counts": _counts_detail(result),
        "findings": findings_detail,
        "unverified": unverified_detail,
        "check_errors": [
            issue.model_dump(mode="json")
            for issue in legacy
            if issue.code is ValidationCode.L6_CHECK_ERROR
        ],
    }
    return out


def _tier(issue: ValidationIssue) -> int:
    if issue.code is ValidationCode.L6_CHECK_ERROR:
        return 0
    return {Severity.ERROR: 1, Severity.WARNING: 2}.get(issue.severity, 3)


def _native_summary(
    result: SubsetProfileResult | None, summary: dict[Outcome, int], legacy: int
) -> str:
    if result is None:
        return f"not computed (see L6_CHECK_ERROR); {legacy} legacy; all listed in --json-report"
    unassessed = result.counts.unassessed_constraints
    return (
        f"{summary[Outcome.REFUSED]} refused, {summary[Outcome.UNCONFIRMED]} unconfirmed, "
        f"{summary[Outcome.OMITTED]} omitted, {summary[Outcome.EXCLUDED]} excluded, "
        f"{unassessed} unassessed constraints, {legacy} legacy; all listed in --json-report"
    )


def _finding_detail(
    finding: SubsetFinding,
    shadow: SubsetFinding | None,
    shown: Display,
    remedy: str,
    limits: str,
) -> dict[str, Any]:
    return {
        "rule_id": finding.rule_id,
        "shape_id": finding.shape_id,
        "context_id": finding.context_id.value,
        "outcome": finding.outcome.value,
        "reason": finding.reason,
        "detail_reasons": list(finding.detail_reasons),
        "subject": {
            "qualified_name": finding.subject.qualified_name,
            "element_id": str(finding.subject.element_id),
            "kind": finding.subject.kind,
        },
        "location": _location_detail(finding.location),
        "occurrence_count": finding.occurrence_count,
        "remedy": remedy,
        "semantic_limits": limits,
        "display": shown.value,
        "shadowed_by": None
        if shadow is None
        else {
            "rule_id": shadow.rule_id,
            "shape_id": shadow.shape_id,
            "element_id": str(shadow.subject.element_id),
        },
    }


def _unverified_detail(check: UnverifiedCheck, shown: Display) -> dict[str, Any]:
    return {
        "rule_id": check.rule_id,
        "context_id": None if check.context_id is None else check.context_id.value,
        "subject": _location_detail(check.subject),
        "cause": str(check.cause.value),
        "detail": check.detail,
        "display": shown.value,
    }


def _scope_detail(result: SubsetProfileResult | None) -> dict[str, Any] | None:
    if result is None:
        return None
    scope = result.scope
    return {
        "roots_available": scope.roots_available,
        "generator_root_ids": [str(root) for root in scope.generator_root_ids],
        "roots_used": [str(root) for root in scope.roots_used],
        "narrowed": scope.narrowed,
        "enumerated": [kind.value for kind in scope.enumerated],
        "not_enumerated": [kind.value for kind in scope.not_enumerated],
    }


def _counts_detail(result: SubsetProfileResult | None) -> dict[str, Any] | None:
    if result is None:
        return None
    counts = result.counts
    return {
        "declarations": counts.declarations,
        "occurrences": counts.occurrences,
        "by_outcome": {outcome.value: n for outcome, n in counts.by_outcome},
        "unverified": counts.unverified,
        "unassessed_constraints": counts.unassessed_constraints,
    }
