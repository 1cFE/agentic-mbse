"""The project's execution target and the severity policy it selects (Item 3 design D2).

A project says in its committed `pyproject.toml` how it runs:
`[tool.agentic-mbse] execution-target = "generated" | "native"`, or leaves it unset. The target
decides only how loud an L6 result is, never what is true. `display(category, target)` is the
whole policy: one table, tested cell by cell. Check failures and setting errors are ERROR in
every column (invariant I2).
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from agentic_mbse.project_root import find_project_root
from agentic_mbse.project_settings import (
    TARGET_KEY,
    SettingsDefect,
    SettingsFault,
    read_toolkit_table,
)
from agentic_mbse.sysml.types import ValidationCode


class Target(StrEnum):
    UNSET = "unset"
    GENERATED = "generated"
    NATIVE = "native"


# The values a project may write; unset is the absence of the key.
ALLOWED_VALUES = (Target.GENERATED.value, Target.NATIVE.value)


@dataclass(frozen=True)
class FromFile:
    path: Path


@dataclass(frozen=True)
class FromOverride:
    """`--execution-target` was given; what the file said, if there was one."""

    file_path: Path | None
    file_value: str | None


@dataclass(frozen=True)
class Unset:
    """No target: `looked_at` is the file read, or None when no project root was found."""

    looked_at: Path | None


TargetSource = FromFile | FromOverride | Unset


@dataclass(frozen=True)
class TargetResolution:
    target: Target
    source: TargetSource
    root: Path | None


class TargetFault(StrEnum):
    SETTINGS = "settings"  # the toolkit table itself is broken; see `settings_fault`
    INVALID_VALUE = "invalid_value"


@dataclass(frozen=True)
class TargetSettingError:
    path: Path
    fault: TargetFault
    settings_fault: SettingsFault | None
    detail: str


def resolve_target(
    models_path: Path, override: Target | None
) -> TargetResolution | TargetSettingError:
    """The target for a run over `models_path`, read from its project root's `pyproject.toml`.

    `override` is `--execution-target` (GENERATED or NATIVE). A broken file is an error even
    with an override: the file is the project's committed statement, and a broken one is a
    configuration error, not a reason to fall back (design D3).
    """
    if override is Target.UNSET:
        raise ValueError("the override is generated or native; unset is no override")
    root = find_project_root(start=models_path)
    if root is None:
        if override is not None:
            return TargetResolution(override, FromOverride(None, None), None)
        return TargetResolution(Target.UNSET, Unset(None), None)

    table = read_toolkit_table(root)
    if isinstance(table, SettingsDefect):
        return TargetSettingError(table.path, TargetFault.SETTINGS, table.fault, table.detail)
    if TARGET_KEY in table.table:
        value = table.table[TARGET_KEY]
        if not isinstance(value, str) or value not in ALLOWED_VALUES:
            return TargetSettingError(
                table.path,
                TargetFault.INVALID_VALUE,
                None,
                f"{table.path}: {TARGET_KEY} = {value!r} is not allowed; allowed values are "
                f"{' and '.join(map(repr, ALLOWED_VALUES))}",
            )
        file_value: str | None = value
    else:
        file_value = None

    if override is not None:
        return TargetResolution(override, FromOverride(table.path, file_value), root)
    if file_value is not None:
        return TargetResolution(Target(file_value), FromFile(table.path), root)
    return TargetResolution(Target.UNSET, Unset(table.path), root)


def describe_target(resolution: TargetResolution) -> str:
    """The `Execution target` metric: the target in effect and where it came from."""
    source = resolution.source
    match source:
        case FromFile(path):
            origin = f"from {path}"
        case FromOverride(None, _):
            origin = "override --execution-target; no project root above models"
        case FromOverride(path, None):
            origin = f"override --execution-target; {path} sets none"
        case FromOverride(_, value):
            origin = f"override --execution-target; file says {value}"
        case Unset(None):
            origin = "no project root above models; pass --execution-target"
        case Unset(path):
            origin = f"no {TARGET_KEY} in {path}"
    return f"{resolution.target.value} ({origin})"


class Category(StrEnum):
    """What kind of result an L6 issue is; with the target, it decides how the issue is shown."""

    REFUSED = "refused"
    UNCONFIRMED = "unconfirmed"
    EXCLUDED = "excluded"
    OMITTED = "omitted"
    ADMITTED = "admitted"
    UNVERIFIED = "unverified"
    UNASSESSED = "unassessed"
    ADVISORY = "advisory"
    ADVISORY_UNVERIFIED = "advisory_unverified"
    LEGACY_OWN_APPLICABILITY = "legacy_own_applicability"
    LEGACY_KEPT = "legacy_kept"
    LEGACY_GENERATOR_ONLY = "legacy_generator_only"
    CHECK_FAILURE = "check_failure"
    CHECK_UNVERIFIED = "check_unverified"
    SETTING_INVALID = "setting_invalid"


class Display(StrEnum):
    ERROR = "error"
    WARNING = "warning"
    NATIVE_SUMMARY = "native_summary"  # folded into native's one INFO summary line
    COUNT_ONLY = "count_only"
    BASE = "base"  # the legacy check's own severity


_W, _E, _S, _C, _B = (
    Display.WARNING,
    Display.ERROR,
    Display.NATIVE_SUMMARY,
    Display.COUNT_ONLY,
    Display.BASE,
)

# design.md "The severity table": (unset, generated, native) per category.
_TABLE: Mapping[Category, tuple[Display, Display, Display]] = {
    Category.REFUSED: (_W, _E, _S),
    Category.UNCONFIRMED: (_W, _W, _S),
    Category.EXCLUDED: (_W, _W, _S),
    Category.OMITTED: (_W, _W, _S),
    Category.ADMITTED: (_C, _C, _C),
    Category.UNVERIFIED: (_W, _E, _W),
    Category.UNASSESSED: (_W, _W, _S),
    Category.ADVISORY: (_W, _W, _S),
    Category.ADVISORY_UNVERIFIED: (_W, _W, _W),
    Category.LEGACY_OWN_APPLICABILITY: (_B, _B, _B),
    Category.LEGACY_KEPT: (_B, _B, _B),
    Category.LEGACY_GENERATOR_ONLY: (_B, _B, _S),
    Category.CHECK_FAILURE: (_E, _E, _E),
    Category.CHECK_UNVERIFIED: (_W, _W, _W),
    Category.SETTING_INVALID: (_E, _E, _E),
}
_COLUMN = {Target.UNSET: 0, Target.GENERATED: 1, Target.NATIVE: 2}


def display(category: Category, target: Target) -> Display:
    """How a result of `category` is shown under `target`."""
    return _TABLE[category][_COLUMN[target]]


# Each of the 17 codes the legacy L6 checks emit (design Appendix A). A code is
# LEGACY_GENERATOR_ONLY only together with its row in the legacy-check audit's "Lowered under
# native" table (`evidence/legacy-l6-audit.md`) and `tests/fixtures/l6/native_lowered.toml`;
# a test keeps the three equal. Four have that evidence (Item 3 Phase 8).
LEGACY_CATEGORY: Mapping[ValidationCode, Category] = {
    ValidationCode.V1_CALC_DEF_LOCATION: Category.LEGACY_OWN_APPLICABILITY,
    ValidationCode.V2_DYNAMIC_EXPRESSION: Category.LEGACY_OWN_APPLICABILITY,
    ValidationCode.V4_UNSUPPORTED_OPERATOR: Category.LEGACY_OWN_APPLICABILITY,
    ValidationCode.V4_STATIC_FUNCTION_INVOCATION: Category.LEGACY_KEPT,
    ValidationCode.L6_MISSING_QUALIFIED_NAME: Category.LEGACY_GENERATOR_ONLY,
    ValidationCode.L6_INVALID_QUALIFIED_NAME: Category.LEGACY_KEPT,
    ValidationCode.L6_CALC_DEF_NO_OUTPUT: Category.LEGACY_KEPT,
    ValidationCode.L6_CALC_DEF_NO_DIRECTION: Category.LEGACY_KEPT,
    ValidationCode.L6_INVALID_BINDING_FORMAT: Category.LEGACY_KEPT,
    ValidationCode.L6_DESIGN_ATTR_INCOMPLETE: Category.LEGACY_KEPT,
    ValidationCode.L6_DESIGN_ATTR_UNEXTRACTABLE: Category.LEGACY_KEPT,
    ValidationCode.L6_ANONYMOUS_RETURN: Category.LEGACY_GENERATOR_ONLY,
    ValidationCode.L6_BODY_ASSIGNMENT_IMPL_LOSS: Category.LEGACY_GENERATOR_ONLY,
    ValidationCode.L6_CONSTRAINT_MALFORMED_NUMERICAL: Category.LEGACY_KEPT,
    ValidationCode.L6_CONSTRAINT_NON_NUMERICAL: Category.LEGACY_KEPT,
    ValidationCode.L6_CALC_DEF_NO_INSTANTIATION: Category.LEGACY_GENERATOR_ONLY,
    ValidationCode.L6_ATTR_REDEF_EXPR_DROPPED: Category.LEGACY_KEPT,
}


def lowered_under_native(categories: Mapping[ValidationCode, Category]) -> frozenset[str]:
    """The legacy codes whose severity `native` lowers into the summary."""
    return frozenset(
        code.value
        for code, category in categories.items()
        if display(category, Target.NATIVE) is Display.NATIVE_SUMMARY
    )
