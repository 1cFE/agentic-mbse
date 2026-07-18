# Implementation Plan: Orchestrate Modeling

**Status:** Complete
**Created:** 2026-07-18
**Last Updated:** 2026-07-18

## Source Documents

- **Spec:** `.project/active/orchestrate-modeling/spec.md`
- **Design:** `.project/active/orchestrate-modeling/design.md`
- **Design review:** `.project/active/orchestrate-modeling/design-review.md`

## Implementation Strategy

**Phasing Rationale:** Prove the broken epic entry path first. Then establish one flow contract before
writing the prompt that depends on it. Add the orchestrator only after those foundations work, and
finish by proving every supported installation path. See the design's
[integration strategy](design.md#integration-strategy).

**Critical Path:** Supported epic registration → canonical Standard/Epic flow → prompt-led
orchestration and tabletop proof → installation and regression.

**First Proof Point:** Starting with an empty `BACKLOG.md`, register an existing epic file, add its
first Standard items through PM commands, and rediscover the resulting state through the parser. If
this requires a direct backlog edit, stop and revise the design before Phase 3.

**Overall Validation Approach:**

- Start every phase with failing tests or contract assertions.
- Use automated tests for deterministic state, prompt contracts, and installation behavior.
- Use tabletop scenarios for judgment-led routing that static tests cannot prove.
- Run focused checks after each phase and the normal suite and Ruff after integration.

---

## Phase 1: Prove Epic Registration and Orientation

### Goal

Provide the smallest supported mutation path needed to start an epic from an empty backlog. This
collapses the main feasibility risk before the orchestrator prompt exists. See
[D3](design.md#key-decisions), [required invariants](design.md#required-invariants), and the
[first-proof-point handoff](design.md#next-stage-handoff).

### Assumption Under Test

The current backlog schema and parse/render path can register an already-written epic and its first
Standard items without direct edits or a new state type.

### Test Stencil (Write This First)

```python
def test_register_epic_then_add_items_to_empty_backlog(tmp_path):
    root, epic_file = empty_project_with_epic_file(tmp_path)
    result = add_epic(root, name="Thermal model", priority="P1", file=epic_file)
    assert result.success
    assert add_item(root, name="Radiator", scale="standard", priority="P1",
                    epic="Thermal model").success
    parsed = parse_backlog(root / "work" / "BACKLOG.md")
    assert parsed.data.epics[0].items[0].name == "Radiator"
```

### Changes Required

**See the design for:** the interface and rejection rules in
[Implementation Notes](design.md#implementation-notes), the writer constraint in
[Required Invariants](design.md#required-invariants), and inconsistent-record risk in
[Potential Risks](design.md#potential-risks).

**Specific file changes:**

- [x] `tests/test_pm_operations.py:906` — write operation tests first for empty and populated
  backlogs, parser round-trip, duplicate names, missing epic files, and invalid priorities.
- [x] `tests/test_pm_cli.py:206` — write CLI success/failure and parser-dispatch tests for
  `pm add-epic` before registering the command.
- [x] `src/agentic_mbse/pm/operations.py:863` — add the narrow operation beside `add_item`, using
  the existing parser and atomic backlog writer.
- [x] `src/agentic_mbse/pm/__init__.py:19` — export the new operation through the public PM surface.
- [x] `src/agentic_mbse/cli/pm_cli.py:298` and `:412` — add the handler and parser with required
  `--name`, `--priority`, and `--file`, plus optional `--goal`.
- [x] `claude/commands/backlog.md:25` — replace nonexistent PM calls with `add-epic` and `add-item`,
  including all arguments the real CLI requires.
- [x] `claude/commands/status.md:54` — correct epic decomposition registration to use the same
  supported PM commands.

### Validation

**Automated:**

- [x] `uv run pytest tests/test_pm_operations.py -k 'AddEpic or AddItem'` passes.
- [x] `uv run pytest tests/test_pm_cli.py` passes.
- [x] `uv run ruff check src/agentic_mbse/pm src/agentic_mbse/cli tests/test_pm_operations.py tests/test_pm_cli.py` passes.

**Manual:**

- [x] In a temporary initialized project, create an epic file and run `agentic-mbse pm add-epic`,
  followed by two `pm add-item --epic ...` calls.
- [x] Confirm `/status` or the PM status command can orient from the resulting files with no manual
  `BACKLOG.md` edit.
- [x] Confirm duplicate-name and missing-file commands fail without changing the backlog.

**What We Know Works After This Phase:** A fresh epic can enter the normal PM state path, receive
Standard items, and be resumed from durable project state.

---

## Phase 2: Establish the Canonical Modeling Flow

### Goal

Make the tool-owned modeling process the single complete command-level flow and reconcile the touched
commands with it. This gives the future orchestrator a stable map rather than duplicated routing rules.
See [D1](design.md#key-decisions) and [Component Overview](design.md#component-overview).

### Assumption Under Test

Small documentation changes can make the existing stages coherent without changing their artifact
contracts or building another pipeline abstraction.

### Test Stencil (Write This First)

```python
def test_canonical_flow_covers_both_routes_and_finish_boundary():
    flow = read_repo_file("project_templates/MODELING_PROCESS.md.template")
    assert "Standard" in flow and "Epic" in flow
    assert "research" in flow and "review-model" in flow
    assert "audit-models" in flow
    assert "close" in flow and "owner" in flow.lower()
    assert "Levels 4-8" not in read_repo_file("claude/commands/plan-model.md")
```

### Changes Required

**See the design for:** the route in [Architecture](design.md#architecture), local ownership rules in
[D1](design.md#key-decisions), and drift controls in [Potential Risks](design.md#potential-risks).

**Specific file changes:**

- [x] `tests/test_modeling_command_contracts.py` (new) — write focused documentation contract tests
  first for both routes, optional stages, mandatory audit, owner-held close, and stale touched facts.
- [x] `project_templates/MODELING_PROCESS.md.template:1` — add the concise canonical command flow
  above the existing detailed modeling methodology.
- [x] `project_templates/EPIC_GUIDE.md.template:11` — align the Standard finish boundary, epic
  integration audit, and PM command references with the canonical flow.
- [x] `claude/commands/plan-model.md:111` and `claude/commands/implement-model.md` — keep only accurate
  local predecessor/successor facts and correct the six-level validation language.
- [x] `claude/commands/audit-models.md:81` — add explicit epic scope covering epic success criteria,
  every item audit, and cross-item integration obligations.
- [x] `project_templates/README.md.template:55` — replace `/backlog clear` with the supported close
  path and correct its flow summary for new projects only.

### Validation

**Automated:**

- [x] `uv run pytest tests/test_modeling_command_contracts.py -k flow` passes.
- [x] `rg -n 'Levels 4-8|/backlog clear|pm add-to-backlog'` reports no stale occurrence on the
  touched command/template surfaces.

**Manual:**

- [x] Read the canonical map once as a new operator and identify the entry, optional stages, Epic
  branch, audit boundary, and owner-held close without consulting another flow document.
- [x] Confirm the tool-owned process will update existing initialized projects, while the README
  correction is correctly described as new-project-only.

**What We Know Works After This Phase:** Stage agents and users have one coherent route map, and epic
completion has an explicit independent integration-audit contract.

---

## Phase 3: Add and Tabletop the Thin Orchestrator

### Goal

Add `/orchestrate-modeling` as a judgment-led Task coordinator over the proven PM and documentation
surfaces. See [Core Concept](design.md#core-concept), [D2, D4, and D5](design.md#key-decisions), and
[Required Invariants](design.md#required-invariants).

### Assumption Under Test

A self-contained prompt overlay can suppress routine stage interactivity, preserve alignment through
fresh Task launches, and route Standard and Epic work without an encoded state machine.

### Test Stencil (Write This First)

```python
def test_orchestrator_declares_safety_contracts():
    command = read_repo_file("claude/commands/orchestrate-modeling.md")
    assert command.count("planned owner checkpoint") == 1
    assert "work/orchestration/" in command
    assert "self-contained" in command and "fresh Task" in command
    assert "owner-reserved" in command and "premise" in command
    assert "two unsuccessful" in command and "no material progress" in command
```

### Changes Required

**See the design for:** stage handoffs and decision policy in [Architecture](design.md#architecture),
alignment contents in [D5](design.md#key-decisions), bounded repair in [D4](design.md#key-decisions),
and the context discipline in [Implementation Notes](design.md#implementation-notes).

**Specific file changes:**

- [x] `tests/test_modeling_command_contracts.py` — write command assertions first for one alignment,
  pre-stage brief persistence, fresh non-interactive Tasks, decision tiers, bounded repair, separate
  audit context, both routes, and owner-held close.
- [x] `claude/commands/orchestrate-modeling.md` (new) — implement the thin command using the canonical
  flow and existing stage commands; include `Task` in frontmatter and avoid stage reimplementation.
- [x] Review the prompt for prohibited complexity: no shell/Python orchestration helper, run database,
  Task session IDs, fixed transition table, or automatic archive action.

### Validation

**Automated:**

- [x] `uv run pytest tests/test_modeling_command_contracts.py` passes.
- [x] `rg -n 'orchestrate-stage|session.?id|run database|state table' claude/commands/orchestrate-modeling.md`
  finds no copied runtime mechanism.

**Manual tabletop:**

- [x] Walk a fresh standalone objective through alignment, spec, design, plan, implementation, and
  positive independent audit.
- [x] Walk a two-item dependency epic from an empty backlog, including serial scheduling and the final
  epic integration audit.
- [x] Exercise crash-after-alignment resume, a returned question with fresh relaunch, a reserved gate,
  a premise conflict, and an interrupted run.
- [x] Exercise two unsuccessful repair/audit rounds for the same finding and one no-progress round;
  confirm dependent work parks and the owner receives the evidence.

**What We Know Works After This Phase:** The command has the required safety and autonomy contracts,
and the designed routes remain understandable under representative failure and resume scenarios.

---

## Phase 4: Register, Install, and Regress

### Goal

Ship the command through normal init, standalone command installation, development replication, and
hash protection. See [Component Overview](design.md#component-overview) and
[Validation Approach](design.md#validation-approach).

### Assumption Under Test

The existing command manifest is sufficient for all Python-managed installation behavior, and one
parity assertion can keep the separate development replication list synchronized.

### Test Stencil (Write This First)

```python
def test_orchestrator_is_available_through_every_install_surface(tmp_path):
    assert "orchestrate-modeling.md" in listed_commands()
    assert normal_init(tmp_path).joinpath(
        ".claude/commands/orchestrate-modeling.md").is_file()
    assert dev_init(tmp_path).joinpath(
        ".claude/commands/orchestrate-modeling.md").is_symlink()
    assert command_manifest() == replication_script_manifest()
```

### Changes Required

**See the design for:** the installation requirement in [Implementation Notes](design.md#implementation-notes)
and expected coverage in [Validation Approach](design.md#validation-approach).

**Specific file changes:**

- [x] `tests/test_cli.py:238` and `:390` — add failing tests first for list output, normal copy, dev
  symlink, modification/hash protection, and command-manifest parity.
- [x] `src/agentic_mbse/cli/__init__.py:18` — add the command to `MBSE_COMMANDS`.
- [x] `scripts/replicate_setup.sh:55` — add the same command to the development replication list.
- [x] Run the complete tabletop checklist against the installed command, not only its source file.

### Validation

**Automated:**

- [x] `uv run pytest tests/test_cli.py tests/test_pm_cli.py tests/test_pm_operations.py tests/test_modeling_command_contracts.py` passes.
- [x] `uv run pytest tests/` passes: 1,504 passed, 1 skipped, 33 slow tests deselected. The
  separately started slow run was stopped at the owner's request and is outside this feature scope.
- [x] Feature-touched Python files pass `ruff check`. The repository-wide check still reports 131
  pre-existing findings outside this feature.
- [x] New and previously formatted touched Python files pass `ruff format --check`. The repository-wide
  check still identifies 62 pre-existing files for formatting.

**Manual:**

- [x] `uv run agentic-mbse install-commands --list` shows `orchestrate-modeling.md`.
- [x] Normal and `--dev` initialization in temporary projects produce the expected file and symlink.
- [x] Modifying an installed copy is detected or protected consistently with other tool-owned commands.

**What We Know Works After This Phase:** The orchestrator is discoverable and installed through every
supported path, with deterministic behavior covered by the normal regression checks.

---

## Environment Setup

- Use `uv run` for project commands as required by `CLAUDE.md`.
- Preserve unrelated working-tree changes.
- Use temporary initialized projects for manual installation and PM checks.

## Risk Management

See [Potential Risks](design.md#potential-risks) for the full analysis.

- **Phase 1:** Treat inability to complete the empty-backlog proof without direct edits as a design
  failure, not an implementation workaround.
- **Phase 2:** Keep the complete flow in one tool-owned document; other surfaces state only local facts.
- **Phase 3:** Separate deterministic prompt contracts from agent-judgment tabletop evidence. Default
  Epic execution to serial unless both dependencies and write surfaces are independent.
- **Phase 4:** Enforce manifest parity in a kept test so future commands do not drift across installers.

## Implementation Notes

_Fill this section during implementation. Check off each phase as it completes and record actual
changes, validation results, issues, and justified deviations._

### Phase 1 Completion

**Completed:** 2026-07-18T09:16:10-07:00
**Actual Changes:** Added `pm add-epic`, public exports, CLI registration, real backlog/status command
calls, and operation/dispatch tests. The operation validates priority, uniqueness, file existence, and
containment under `work/`, then uses the existing backlog parser/writer.
**Validation:** 111 PM operation/CLI tests passed; focused Ruff passed. A temporary initialized project
registered an epic and two items, rediscovered them through `status --json`, and rejected duplicate and
missing-file registrations without direct backlog edits.
**Issues / Deviations:** The first manual status run exposed that a newly registered epic must be
declared `draft`, not `active`, until derived state advances. The implementation and test expectation
were corrected to avoid a declared/derived status warning. No design change was required.

### Phase 2 Completion

**Completed:** 2026-07-18T09:19:11-07:00
**Actual Changes:** Added the canonical command-level Standard/Epic map to the tool-owned modeling
process, aligned the Epic guide and local stage boundaries, added explicit Epic audit obligations, and
removed stale PM commands, close wording, and validation-level references.
**Validation:** Four kept documentation contract tests passed; Ruff passed after its import-order fix;
the stale-reference scan and `git diff --check` were clean. A manual read identified every route and
finish boundary from the canonical section alone.
**Issues / Deviations:** None. The README correction remains new-project-only as designed; existing
projects receive the tool-owned process update on re-init.

### Phase 3 Completion

**Completed:** 2026-07-18T09:23:46-07:00
**Actual Changes:** Added the Task-only `/orchestrate-modeling` command with one Align checkpoint,
immutable pre-stage alignment brief, self-contained fresh launches, Standard/Epic/Trivial routing,
three decision tiers, resume guidance, independent audits, and bounded repair.
**Validation:** Eight command/document contract tests passed; the prohibited-runtime scan and
`git diff --check` were clean. Tabletop walks covered a fresh Standard item, a serial two-item Epic,
crash and interruption resume, fresh relaunch after a question, reserved and premise gates, and both
audit-repair stop conditions.
**Issues / Deviations:** Added an explicit Trivial route because orientation can classify work as
Trivial; it delegates the existing `/quick-model` command and does not broaden tracked Standard/Epic
scope. No orchestration runtime or state subsystem was added.

### Phase 4 Completion

**Completed:** 2026-07-18T09:46:00-07:00
**Actual Changes:** Registered `orchestrate-modeling.md` in both installation manifests and added kept
tests for listing, normal copy, dev symlinks, hash protection, and manifest parity.
**Validation:** The 202-test feature suite and 1,504-test normal repository suite passed. Live temporary
normal and dev projects received a regular command file and source symlink respectively, and the normal
copy was hash-tracked. Feature-touched Python files pass Ruff lint.
**Issues / Deviations:** The repository-wide Ruff checks remain red on pre-existing debt (131 lint
findings and 62 formatting candidates). The 33 slow corpus/PDF tests were started separately and stopped
at the owner's request; they are unrelated to this command feature.

---

**Status:** Complete
