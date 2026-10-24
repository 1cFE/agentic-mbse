"""The project's execution target: whether it targets generated code.

A project says in its committed `pyproject.toml` how it runs:
`[tool.agentic-mbse] execution-target = "generated" | "native"`, or leaves it unset.

- `generated` marks a project that targets generated code. The modelling workflow reads it to
  decide when to run `sysml-codegen check` (`MODELING_PROCESS.md`, "Generated code").
- `native` marks a project that does not run generated code.

L6 reports the target and changes no result for it (ADR 0006). A broken setting is
`L6_SETTING_INVALID` and stops L6 under every target.
"""

from __future__ import annotations

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


UNSET_NOTE = (
    "execution-target is not set. Under [tool.agentic-mbse] in pyproject.toml, set "
    'execution-target = "generated" if the project targets generated code (the modelling '
    'workflow then runs sysml-codegen check), or "native" if it does not. agentic-mbse init '
    "--execution-target=generated|native writes it."
)
