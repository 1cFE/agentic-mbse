# Design: D1.4 — `cmd_init()` Rewiring

**Status:** Complete
**Owner:** Reid Westwood
**Created:** 2026-02-01
**Updated:** 2026-02-01
**Branch:** revamp-architecture
**Commit:** 2d20c43

## Overview

Rewire `cmd_init()` and `replicate_setup.sh` to produce the new 4-directory structure (`knowledge/`, `project/`, `work/`, `data/`) with all templates at their correct destinations, reconcile component lists, update the traceability CSV schema, and update documentation.

## Related Artifacts

- **Spec:** `.project/active/cmd-init-rewiring/spec.md`
- **Epic:** `.project/backlog/epic_architecture-structure.md`
- **Delta Checklist:** `.project/concepts/architecture-redesign/delta-checklist.md` (§§ 1.4, 1.5)
- **Frontmatter Schemas:** `.project/concepts/architecture-redesign/frontmatter-schemas.md`

---

## Research Findings

### Current `cmd_init()` Structure (`cli/__init__.py`)

The function follows a clear section pattern (lines 472–913):

1. **Resolve target, check prerequisites** (472–516)
2. **Detect modified files, prompt user** (518–563)
3. **Create `.gitignore`** (565–629)
4. **Create `SOURCE_INDEX.md`** (631–656)
5. **Install commands** (658–684)
6. **Install agents** (with path substitution) (686–733)
7. **Install skills** (735–751)
8. **Install hooks** (752–781)
9. **Create `modeling_pm/` structure** (783–789) ← REPLACE
10. **Create `tests/models/`** (791–793)
11. **Install user-owned templates** (795–808)
12. **Install tool-owned templates** (809–831)
13. **Create `.claude/settings.json`** (833–858)
14. **Update `.gitignore` for dev mode** (860–863)
15. **Save tool hashes** (865–871)
16. **Print summary** (873–913)

### Key Patterns (Reuse)

- **User-owned file pattern** (`cli/__init__.py:567–569`): Check `exists() and not args.force` → skip or create. Used for `.gitignore`, `SOURCE_INDEX.md`, `.claude/settings.json`, and all `USER_OWNED_TEMPLATES`. The CSV install should follow this exact pattern.
- **Template installation** (`cli/__init__.py:797–808`): Loop over `USER_OWNED_TEMPLATES`, copy from `templates_dir / template_name` to `target / dest_path`, creating parent dirs. Already handles the pattern we need.
- **Hash tracking** (`cli/__init__.py:670–674`): Tool-owned files get content hashes stored in `.tool-hashes.json`. User-owned templates don't get tracked (they're skipped on re-init anyway).
- **Path substitution for agents** (`cli/__init__.py:720–723`): Only agents with `{SYSML_DOCS_PATH}` or `{SYSIDE_DOCS_PATH}` placeholders need substitution. Currently `kerml-expert.md`, `sysml-expert.md`, `syside-expert.md` use placeholders. `python-debugger.md` and `sysmlv2-validator.md` do not — but they still go through the special agent path that does `content.replace()` (harmless no-op on files without placeholders).

### `replicate_setup.sh` Structure

Functions: `check_prerequisites()`, `install_claude_components()`, `create_settings_json()`, `create_project_structure()`, `create_overview_md()`, `create_source_index()`, `print_summary()`, `main()`.

Current component divergence:
- **Agents installed** (`replicate_setup.sh:62`): `python-debugger.md`, `sysmlv2-doc-analyzer.md` — missing 4 agents
- **Skills installed** (`replicate_setup.sh:71–74`): only `python-debugger` — missing 2 skills
- `create_overview_md()` writes hardcoded coffee-maker content (130 lines) — to be deleted per spec

### `sysmlv2-doc-analyzer.md` Deprecation Status

**Finding:** The file lives in `claude/agents/deprecated/sysmlv2-doc-analyzer.md` and has an explicit deprecation banner:

> **DEPRECATED:** This agent is deprecated. Use specialized agents instead: kerml-expert, sysml-expert, syside-expert, sysmlv2-validator.

The delta checklist § 3A.4 marks this as `[EVALUATE]` for Epic 3A — "Decide: restore from deprecated/ to agents/, or confirm deprecation is intentional and remove from architecture."

This conflicts with the spec's FR-7 which says to add it to `MBSE_AGENTS`. See [Design Decision DD-1](#dd-1-sysmlv2-doc-analyzer-agent) below.

### Traceability Matrix CSV

Current schema (`project_templates/data/traceability_matrix.csv`):
```
Element,Type,Source_Type,Source_Document,Source_Location,Implementation_Location,Status,Confidence,Assumptions,Date_Created
```

D1.3-approved target schema:
```
Element,File,Type,Knowledge,Requirement,Source_Type,Source_Document,Source_Location,Confidence,Assumptions,Last_Verified
```

Changes: add `File`, `Knowledge`, `Requirement`; remove `Implementation_Location`, `Status`, `Date_Created`; rename `Date_Created` → `Last_Verified`.

### Template Files Verification

All 15 templates exist in `project_templates/`:
- 6 new from D1.1: `KNOWLEDGE.md.template`, `ARCHITECTURE.md.template`, `REQUIREMENTS.md.template`, `VALIDATION_MATRIX.md.template`, `EPIC_GUIDE.md.template`, `epic_template.md.template`
- 5 revised from D1.2: `OVERVIEW.md.template`, `BACKLOG.md.template`, `MODELING_GUIDE.md.template`, `MODELING_PROCESS.md.template`, `README.md.template`
- 4 unchanged: `RAW_LEARNINGS.md.template`, `conftest.py.template`, `test_models_example.py.template`, `LOCAL_GUIDE.md.template` (removed from install)

---

## Design Decisions

### DD-1: `sysmlv2-doc-analyzer` Agent

**Context:** The spec's FR-7 says to add `sysmlv2-doc-analyzer.md` to `MBSE_AGENTS`. However, the agent file lives in `claude/agents/deprecated/` with an explicit deprecation notice. The delta checklist § 3A.4 marks this as an `[EVALUATE]` item for Epic 3A, not D1.4.

**Options:**

1. **Do not add to `MBSE_AGENTS`; remove from `replicate_setup.sh`** — Both files converge on the 5 non-deprecated agents. The deprecated agent stays in `deprecated/` for Epic 3A to evaluate.

2. **Move from `deprecated/` to `agents/` and add to `MBSE_AGENTS`** — Restores the agent. Requires stripping the deprecation banner. Preempts the Epic 3A evaluation.

3. **Add to `MBSE_AGENTS` but leave in `deprecated/` subfolder** — Would require changing the agent install logic to look in subdirectories, adding complexity for a deprecated file.

**Recommendation:** Option 1. The agent is explicitly deprecated. The 4 specialized replacements (`kerml-expert`, `sysml-expert`, `syside-expert`, `sysmlv2-validator`) are already in `MBSE_AGENTS` and cover its functionality. Adding a deprecated agent to the production install list contradicts its deprecation status. The reconciliation intent (bringing both files to the same component set) is better served by removing it from `replicate_setup.sh` than adding it to `cmd_init()`. Epic 3A can decide whether to restore it.

**Decision:** Option 1 approved. Do not add to `MBSE_AGENTS`. Remove from `replicate_setup.sh`. Both files converge on the 5 non-deprecated agents. Epic 3A evaluates the deprecated agent separately.

### DD-2: `epic_template.md.template` Installation

**Context:** The spec's FR-12 (inferred) said this template should NOT be installed by `cmd_init()` — it would stay in `project_templates/` as a source template only.

**User correction:** `epic_template.md.template` is the same kind of artifact as `EPIC_GUIDE.md` — a tool-owned reference file. Users may create epics manually (AP-5: toolkit, not pipeline), and having the structural template visible in the project is self-documenting. The PM engine won't parse it (it globs for `epic-*.md`, not `epic_template.md`).

**Decision:** Add to `TOOL_OWNED_TEMPLATES` with destination `work/backlog/epic_template.md`. Drop spec FR-12 special-casing.

---

## Proposed Design

This is a mechanical rewiring — no new abstractions, no new functions, no new modules. Every change maps to an existing code pattern in `cmd_init()`.

### Change 1: Directory Structure (`cli/__init__.py:783–789`)

**Current code:**
```python
# === Create modeling_pm/ structure ===
modeling_pm_dir = target / "modeling_pm"
modeling_pm_dir.mkdir(parents=True, exist_ok=True)
(modeling_pm_dir / "backlog").mkdir(exist_ok=True)
(modeling_pm_dir / "active").mkdir(exist_ok=True)
(modeling_pm_dir / "research").mkdir(exist_ok=True)
(modeling_pm_dir / "learnings").mkdir(exist_ok=True)
```

**Replace with:**
```python
# === Create project structure (4-directory architecture) ===
for subdir in [
    "knowledge",
    "knowledge/research/pending",
    "knowledge/research/approved",
    "knowledge/research/impacts",
    "knowledge/sources",
    "project",
    "project/intent",
    "work",
    "work/backlog",
    "work/active",
    "work/completed",
    "work/analysis",
    "work/learnings",
    "data",
    "models/library",
    "models/designs",
]:
    (target / subdir).mkdir(parents=True, exist_ok=True)
```

**Rationale:** Loop is cleaner than 16 individual calls. `parents=True` on each handles any ordering. `exist_ok=True` maintains idempotency. `models/library` and `models/designs` match the information-architecture.md § 2 file tree (lines 138–143) and close the divergence with `replicate_setup.sh` which already creates `models/library`.

### Change 2: Template Lists (`cli/__init__.py:54–67`)

**`USER_OWNED_TEMPLATES`** — replace entire list:

```python
USER_OWNED_TEMPLATES = [
    ("README.md.template", "README.md"),
    ("OVERVIEW.md.template", "project/OVERVIEW.md"),
    ("BACKLOG.md.template", "work/BACKLOG.md"),
    ("RAW_LEARNINGS.md.template", "work/learnings/RAW_LEARNINGS.md"),
    ("KNOWLEDGE.md.template", "knowledge/KNOWLEDGE.md"),
    ("ARCHITECTURE.md.template", "project/ARCHITECTURE.md"),
    ("REQUIREMENTS.md.template", "project/REQUIREMENTS.md"),
    ("VALIDATION_MATRIX.md.template", "project/VALIDATION_MATRIX.md"),
    ("test_models_example.py.template", "tests/models/test_example.py"),
    ("conftest.py.template", "tests/conftest.py"),
]
```

Removed: `LOCAL_GUIDE.md.template` (per D1.3 MERGE+DELETE decision).

**`TOOL_OWNED_TEMPLATES`** — replace entire list:

```python
TOOL_OWNED_TEMPLATES = [
    ("MODELING_GUIDE.md.template", "project/MODELING_GUIDE.md"),
    ("MODELING_PROCESS.md.template", "project/MODELING_PROCESS.md"),
    ("EPIC_GUIDE.md.template", "work/EPIC_GUIDE.md"),
    ("epic_template.md.template", "work/backlog/epic_template.md"),
]
```

### Change 3: `MBSE_AGENTS` List (`cli/__init__.py:31–37`)

No change. Per DD-1, the 5 non-deprecated agents remain as-is. `sysmlv2-doc-analyzer.md` stays in `deprecated/` for Epic 3A evaluation.

### Change 4: `DEV_MODE_GITIGNORE_PATHS` (`cli/__init__.py:73–82`)

Replace entire list:

```python
DEV_MODE_GITIGNORE_PATHS = [
    "# Tool-owned files (managed by agentic-mbse init --dev)",
    ".claude/commands/",
    ".claude/agents/",
    ".claude/skills/",
    ".claude/hooks/",
    ".claude/.tool-hashes.json",
    "project/MODELING_GUIDE.md",
    "project/MODELING_PROCESS.md",
    "work/EPIC_GUIDE.md",
    "work/backlog/epic_template.md",
]
```

### Change 5: SOURCE_INDEX.md Location (`cli/__init__.py:631–656`)

Change `source_index_path` from `target / "SOURCE_INDEX.md"` to `target / "knowledge" / "SOURCE_INDEX.md"`. The `knowledge/` directory is already created in Change 1. The rest of the logic (existence check, template copy, fallback) stays identical.

Also update the summary output reference from `"SOURCE_INDEX.md"` to `"knowledge/SOURCE_INDEX.md"`.

### Change 6: Traceability Matrix CSV Installation (`cli/__init__.py`)

Add a new section after the user-owned templates loop (after line ~808), following the same user-owned pattern:

```python
# === Install traceability matrix CSV (USER-OWNED) ===
csv_src = templates_dir / "data" / "traceability_matrix.csv"
csv_dst = target / "data" / "traceability_matrix.csv"
if csv_dst.exists() and not args.force:
    skipped.append("data/traceability_matrix.csv")
elif csv_src.exists():
    shutil.copy(csv_src, csv_dst)
    created.append("data/traceability_matrix.csv")
```

The `data/` directory already exists from Change 1. No hash tracking needed (user-owned).

### Change 7: CSV Template Schema Update (`project_templates/data/traceability_matrix.csv`)

Replace the single header line with:

```
Element,File,Type,Knowledge,Requirement,Source_Type,Source_Document,Source_Location,Confidence,Assumptions,Last_Verified
```

### Change 8: `cmd_init()` Docstring (`cli/__init__.py:473–489`)

Update the docstring to describe the new structure:

```python
"""Initialize project with agentic-mbse configuration.

Creates:
- .gitignore (standard Python ignores including .env) [user-owned]
- knowledge/SOURCE_INDEX.md (domain knowledge discovery) [user-owned]
- knowledge/KNOWLEDGE.md (domain insight registry) [user-owned]
- project/ structure (OVERVIEW, ARCHITECTURE, REQUIREMENTS, etc.) [mixed]
- work/ structure (BACKLOG, EPIC_GUIDE, epic template, active, completed, etc.) [mixed]
- data/traceability_matrix.csv (element traceability) [user-owned]
- .claude/commands/ with MBSE commands [tool-owned]
- .claude/agents/ with AI agents [tool-owned]
- .claude/skills/ with skills [tool-owned]
- .claude/hooks/ with hooks [tool-owned]
- .claude/settings.json with read permissions [user-owned]
- tests/ structure with example test files [user-owned]

File ownership behavior:
- Tool-owned files are always updated (to get latest versions)
- User-owned files are skipped if they exist (preserves customizations)

Use --force to overwrite ALL files including user-owned ones.
"""
```

### Change 9: `replicate_setup.sh` — Full Rewrite of Key Functions

#### `install_claude_components()` — Agent Loop

Replace the 2-agent loop (`scripts/replicate_setup.sh:62–68`):

```bash
# Agents - copy with placeholder substitution
for agent in python-debugger.md kerml-expert.md sysml-expert.md \
             syside-expert.md sysmlv2-validator.md; do
    sed -e "s|{SYSML_DOCS_PATH}|$DOCS_PATH/sysmlv2|g" \
        -e "s|{SYSIDE_DOCS_PATH}|$DOCS_PATH/syside|g" \
        "$REPO_ROOT/claude/agents/$agent" > "$REPO_ROOT/.claude/agents/$agent"
    log_created ".claude/agents/$agent (with path substitution)"
done
```

Per DD-1, `sysmlv2-doc-analyzer.md` is removed from the loop (deprecated). The sed substitution is harmless on agents without placeholders (`python-debugger.md`, `sysmlv2-validator.md`).

#### `install_claude_components()` — Skills Loop

Replace the single-skill block (`scripts/replicate_setup.sh:71–74`):

```bash
# Skills - recursive copy
for skill in python-debugger record-learning toolkit-awareness; do
    if [[ -d "$REPO_ROOT/claude/skills/$skill" ]]; then
        cp -r "$REPO_ROOT/claude/skills/$skill" "$REPO_ROOT/.claude/skills/"
        log_created ".claude/skills/$skill/"
    fi
done
```

#### `create_project_structure()` — Directory Creation and Templates

Replace entire function (`scripts/replicate_setup.sh:107–128`):

```bash
create_project_structure() {
    # Create 4-directory structure
    mkdir -p "$REPO_ROOT/knowledge/research/pending"
    mkdir -p "$REPO_ROOT/knowledge/research/approved"
    mkdir -p "$REPO_ROOT/knowledge/research/impacts"
    mkdir -p "$REPO_ROOT/knowledge/sources"
    mkdir -p "$REPO_ROOT/project/intent"
    mkdir -p "$REPO_ROOT/work/backlog"
    mkdir -p "$REPO_ROOT/work/active"
    mkdir -p "$REPO_ROOT/work/completed"
    mkdir -p "$REPO_ROOT/work/analysis"
    mkdir -p "$REPO_ROOT/work/learnings"
    mkdir -p "$REPO_ROOT/data"
    mkdir -p "$REPO_ROOT/models/library"
    mkdir -p "$REPO_ROOT/models/designs"
    mkdir -p "$REPO_ROOT/tests/models"

    log_created "knowledge/{research/{pending,approved,impacts},sources}/"
    log_created "project/intent/"
    log_created "work/{backlog,active,completed,analysis,learnings}/"
    log_created "data/"
    log_created "models/{library,designs}/"
    log_created "tests/models/"

    # Tool-owned templates
    cp "$REPO_ROOT/project_templates/MODELING_GUIDE.md.template" \
       "$REPO_ROOT/project/MODELING_GUIDE.md"
    log_created "project/MODELING_GUIDE.md"

    cp "$REPO_ROOT/project_templates/MODELING_PROCESS.md.template" \
       "$REPO_ROOT/project/MODELING_PROCESS.md"
    log_created "project/MODELING_PROCESS.md"

    cp "$REPO_ROOT/project_templates/EPIC_GUIDE.md.template" \
       "$REPO_ROOT/work/EPIC_GUIDE.md"
    log_created "work/EPIC_GUIDE.md"

    cp "$REPO_ROOT/project_templates/epic_template.md.template" \
       "$REPO_ROOT/work/backlog/epic_template.md"
    log_created "work/backlog/epic_template.md"

    # User-owned templates
    cp "$REPO_ROOT/project_templates/OVERVIEW.md.template" \
       "$REPO_ROOT/project/OVERVIEW.md"
    log_created "project/OVERVIEW.md"

    cp "$REPO_ROOT/project_templates/BACKLOG.md.template" \
       "$REPO_ROOT/work/BACKLOG.md"
    log_created "work/BACKLOG.md"

    cp "$REPO_ROOT/project_templates/RAW_LEARNINGS.md.template" \
       "$REPO_ROOT/work/learnings/RAW_LEARNINGS.md"
    log_created "work/learnings/RAW_LEARNINGS.md"

    cp "$REPO_ROOT/project_templates/KNOWLEDGE.md.template" \
       "$REPO_ROOT/knowledge/KNOWLEDGE.md"
    log_created "knowledge/KNOWLEDGE.md"

    cp "$REPO_ROOT/project_templates/ARCHITECTURE.md.template" \
       "$REPO_ROOT/project/ARCHITECTURE.md"
    log_created "project/ARCHITECTURE.md"

    cp "$REPO_ROOT/project_templates/REQUIREMENTS.md.template" \
       "$REPO_ROOT/project/REQUIREMENTS.md"
    log_created "project/REQUIREMENTS.md"

    cp "$REPO_ROOT/project_templates/VALIDATION_MATRIX.md.template" \
       "$REPO_ROOT/project/VALIDATION_MATRIX.md"
    log_created "project/VALIDATION_MATRIX.md"

    # Data templates
    cp "$REPO_ROOT/project_templates/data/traceability_matrix.csv" \
       "$REPO_ROOT/data/traceability_matrix.csv"
    log_created "data/traceability_matrix.csv"
}
```

#### Delete `create_overview_md()` function

Remove the entire function (`scripts/replicate_setup.sh:130–206`). OVERVIEW.md is now copied from template in `create_project_structure()`.

#### `create_source_index()` — New Path

```bash
create_source_index() {
    cp "$REPO_ROOT/SOURCE_INDEX.md.template" "$REPO_ROOT/knowledge/SOURCE_INDEX.md"
    log_created "knowledge/SOURCE_INDEX.md (from template)"
}
```

#### `print_summary()` — Updated Paths

```bash
print_summary() {
    echo ""
    echo "================================"
    echo "Setup complete!"
    echo "================================"
    echo ""
    echo "Next steps:"
    echo "  1. Review project/OVERVIEW.md for the project template"
    echo "  2. Run /spec-model to start modeling"
    echo "  3. Or run /onboard for interactive configuration"
    echo ""
    echo "To update after code changes, re-run:"
    echo "  ./scripts/replicate_setup.sh"
}
```

#### `main()` — Remove `create_overview_md` Call

The `main()` function calls `create_overview_md` via `create_project_structure()`. After the rewrite, `create_project_structure()` handles OVERVIEW.md via template copy, and `create_overview_md()` is deleted. No change needed in `main()` itself.

### Change 10: CLAUDE.md Updates

#### Context B description (`CLAUDE.md:26`)

```markdown
- **Project management**: `knowledge/`, `project/`, `work/`, `data/` directories
```

(Was: `modeling_pm/` directory)

#### Claude Integration agents list (`CLAUDE.md:122`)

Update to list actual non-deprecated agents:

```markdown
- **agents/**: Specialized agents (`python-debugger.md`, `kerml-expert.md`, `sysml-expert.md`, `syside-expert.md`, `sysmlv2-validator.md`)
```

#### Project Templates section (`CLAUDE.md:126–134`)

Replace the template list:

```markdown
Templates installed by `init` command to bootstrap new MBSE projects:

**User-owned** (created once, preserved on re-init):
- `README.md.template` → `README.md`
- `OVERVIEW.md.template` → `project/OVERVIEW.md`
- `BACKLOG.md.template` → `work/BACKLOG.md`
- `KNOWLEDGE.md.template` → `knowledge/KNOWLEDGE.md`
- `ARCHITECTURE.md.template` → `project/ARCHITECTURE.md`
- `REQUIREMENTS.md.template` → `project/REQUIREMENTS.md`
- `VALIDATION_MATRIX.md.template` → `project/VALIDATION_MATRIX.md`
- `RAW_LEARNINGS.md.template` → `work/learnings/RAW_LEARNINGS.md`

**Tool-owned** (updated on every re-init):
- `MODELING_GUIDE.md.template` → `project/MODELING_GUIDE.md`
- `MODELING_PROCESS.md.template` → `project/MODELING_PROCESS.md`
- `EPIC_GUIDE.md.template` → `work/EPIC_GUIDE.md`
- `epic_template.md.template` → `work/backlog/epic_template.md`

**Data templates** (user-owned):
- `data/traceability_matrix.csv` → `data/traceability_matrix.csv`
```

#### Directory Clarification table (`CLAUDE.md:171–176`)

Replace:

```markdown
| Directory | Context | Purpose | Committed to Git |
|-----------|---------|---------|------------------|
| `.project/` | A (developing agentic-mbse) | Specs, designs, backlog for the Python library | Yes |
| `knowledge/` | B (target repo) | Domain insights, research, source index | No (created by init) |
| `project/` | B (target repo) | Architecture, requirements, overview, guides | No (created by init) |
| `work/` | B (target repo) | Backlog, active/completed work items, learnings | No (created by init) |
| `data/` | B (target repo) | Traceability matrix and structured data | No (created by init) |
| `claude/commands/` | B (shipped to target repos) | MBSE workflow commands users run | Yes |
| `tests/` | A (developing agentic-mbse) | pytest tests for Python code | Yes |
```

#### Init File Ownership examples (`CLAUDE.md:197`)

Update example file names:

```markdown
| **User-owned** | Create once, skip on re-init (preserve customizations) | `knowledge/SOURCE_INDEX.md`, `project/OVERVIEW.md`, `work/BACKLOG.md`, `README.md`, `.gitignore`, `.claude/settings.json` |
| **Tool-owned** | Always update on re-init (get latest versions) | Commands, agents, skills, hooks, `project/MODELING_GUIDE.md`, `project/MODELING_PROCESS.md`, `work/EPIC_GUIDE.md`, `work/backlog/epic_template.md` |
```

### Change 11: `docs/source-index.md` Update

Two locations reference the file path (not file content) and need the `knowledge/` prefix:

1. **Line 3**: `"a markdown file (`SOURCE_INDEX.md`)"` → `"a markdown file (`knowledge/SOURCE_INDEX.md`)"` — this describes where the file lives in the project
2. **Line 59**: `"Commands read `SOURCE_INDEX.md` at startup"` → `"Commands read `knowledge/SOURCE_INDEX.md` at startup"` — runtime file path

Lines that do NOT need updating:
- Lines 11–21 (format example inside a code block — shows file content, not file location)
- Line 69 ("Commands create template if missing" — refers to the behavior, not the path)
- Lines 85–131 (example content blocks — show what's inside the file)

---

## Potential Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| Tests fail immediately after code changes | Expected | D1.7 updates tests. The code changes are correct; the tests assert old paths. Run tests to confirm only path-related assertions fail, not import/syntax errors. |
| `replicate_setup.sh` and `cmd_init()` drift again | Medium | The CLAUDE.md "Change Coordination" section already warns about this. The reconciliation in this deliverable sets a clean baseline. |
| Users with old `modeling_pm/` structure confused by new dirs appearing alongside | Low | Documented in spec as acceptable. Migration is D1.6. |
| `sysmlv2-doc-analyzer.md` decision deferred → Epic 3A forgets | Low | The delta checklist § 3A.4 tracks it explicitly. |

---

## Integration Strategy

This change is purely structural rewiring — no new abstractions, no API changes, no behavioral changes. The existing `cmd_init()` flow is preserved exactly; only the constants and a few path variables change.

**What this complements:** D1.1/D1.2 (templates that exist but aren't wired in yet).
**What this enables:** D1.7 (test updates), D1.6 (fusion-tea migration), and all of Epics 2–4.
**What it replaces:** The `modeling_pm/` directory structure in init output.

---

## Validation Approach

### Pre-implementation Check
- Run `uv run pytest tests/test_cli.py` to establish baseline (all tests should pass)

### Post-implementation Checks

1. **Smoke test on fresh directory:**
   ```bash
   tmp=$(mktemp -d)
   uv run agentic-mbse init "$tmp"
   # Verify: knowledge/, project/, work/, data/, models/ exist with subdirs
   # Verify: knowledge/SOURCE_INDEX.md, knowledge/KNOWLEDGE.md exist
   # Verify: project/OVERVIEW.md, project/ARCHITECTURE.md, etc. exist
   # Verify: work/BACKLOG.md, work/EPIC_GUIDE.md, work/backlog/epic_template.md exist
   # Verify: data/traceability_matrix.csv exists with correct header
   # Verify: NO modeling_pm/ directory
   ```

2. **Dev mode smoke test:**
   ```bash
   tmp=$(mktemp -d)
   uv run agentic-mbse init --dev "$tmp"
   # Verify: .claude/commands/*.md are symlinks
   # Verify: project/MODELING_GUIDE.md is symlink
   # Verify: work/EPIC_GUIDE.md is symlink
   # Verify: .gitignore contains new paths
   ```

3. **Idempotency test:**
   ```bash
   uv run agentic-mbse init "$tmp"
   uv run agentic-mbse init "$tmp"
   # Second run should succeed, skip user-owned files
   ```

4. **`replicate_setup.sh` test:**
   ```bash
   ./scripts/replicate_setup.sh
   # Verify same directory structure as cmd_init
   ```

5. **Existing test suite** (expect path-related failures — D1.7 fixes them):
   ```bash
   uv run pytest tests/test_cli.py -v 2>&1 | grep -E "PASSED|FAILED"
   # Confirm failures are only path-assertion failures, not crashes
   ```

---

## File Change Summary

| File | Type | Changes |
|------|------|---------|
| `src/agentic_mbse/cli/__init__.py` | REVISE | Constants (3 lists + gitignore paths), directory creation block, SOURCE_INDEX.md path, add CSV install section, docstring |
| `scripts/replicate_setup.sh` | REVISE | Agent/skill loops, `create_project_structure()` rewrite, delete `create_overview_md()`, `create_source_index()` path, `print_summary()` paths |
| `project_templates/data/traceability_matrix.csv` | REVISE | Header line (1 line) |
| `CLAUDE.md` | REVISE | ~5 sections with path/description updates |
| `docs/source-index.md` | REVISE | ~3 path references |

**No new files. No deleted files. No new functions or classes.**

---

**Next Step:** After approval → `/_my_plan` or `/_my_implement`
