# Design: PDF Skill Deployment — Docling MCP Setup in Init

**Status:** Draft
**Owner:** Reid Westwood
**Created:** 2026-02-06 18:09 UTC
**Branch:** pdf-extract
**Commit:** 73a20d5

## Overview

Integrate the Docling MCP server setup into `agentic-mbse init` so that the pdf-analysis skill's 3-tier extraction pipeline works out of the box. The system detects hardware resources, classifies a tier (constrained/moderate/comfortable), configures the MCP server appropriately, and installs a tier-adapted version of the skill prompt.

## Related Artifacts

- **Spec:** `.project/active/pdf-skill-deployment/spec.md`
- **Setup script:** `.project/active/pdf-skill/setup-docling.sh`
- **Skill source:** `claude/skills/pdf-analysis/`
- **Init implementation:** `src/agentic_mbse/cli/__init__.py`
- **Replication script:** `scripts/replicate_setup.sh`

## Research Findings

### Init Flow Order (cli/__init__.py:550-1009)

The `cmd_init()` function follows this sequence:
1. Resolve path, check dev mode (lines 573-588)
2. Load hashes, detect modifications (lines 597-622)
3. Prompt user for modified files (lines 624-645)
4. Create `.gitignore` (lines 647-711)
5. Create `knowledge/SOURCE_INDEX.md` (lines 713-739)
6. Install commands (lines 741-767) — with hash tracking
7. Install agents (lines 769-816) — with `{SYSML_DOCS_PATH}` substitution
8. **Install skills** (lines 818-833) — directory copy/symlink, no content transform
9. Install hooks (lines 835-864)
10. Create project structure + templates (lines 866-936)
11. Create `.claude/settings.json` (lines 938-963)
12. Save hashes, print summary (lines 965-1009)

### Skill Installation Pattern (cli/__init__.py:818-833)

Skills use `_install_directory()` (line 475-499) which does a full directory copy or symlink. **No content transformation occurs** — unlike agents which get `{PLACEHOLDER}` substitution. This means the pdf-analysis skill currently installs with a static SKILL.md regardless of system capabilities.

### Agent Placeholder Pattern (cli/__init__.py:800-806)

Agents read file content, replace placeholders, and write the result:
```python
content = src.read_text()
content = content.replace("{SYSML_DOCS_PATH}", f"{docs_path}/sysmlv2")
content = content.replace("{SYSIDE_DOCS_PATH}", f"{docs_path}/syside")
dst.write_text(content)
```

This is the precedent for content-aware installation.

### Setup Script Analysis (.project/active/pdf-skill/setup-docling.sh)

The existing bash script handles the full pipeline:
- Environment detection: RAM via `/proc/meminfo`, GPU via `nvidia-smi`, cores via `nproc` (lines 36-66)
- Tier classification: constrained ≤8GB, moderate 9-16GB (or GPU bump), comfortable 17GB+ (lines 68-87)
- Prerequisite checks: `uv`, `uvx`, `claude`, Python ≥3.10 (lines 94-125)
- Wrapper creation: `~/.local/bin/docling-mcp-wrapper.sh` with tier-tuned env vars (lines 169-209)
- Launch test: 30s wait with 120s timeout (lines 215-242)
- Registration: `claude mcp add --scope user --transport stdio docling` (lines 248-256)
- Environment report: `~/.docling-mcp-env.md` with tier info (lines 262-318)

The script accepts `--force` to remove and re-register.

### Subprocess Usage in Init

Only one subprocess call exists currently: `_get_git_commit()` at line 311 uses `subprocess.run()`. The Docling setup follows the same pattern — call an external script via subprocess.

### Existing Argparse for Init (cli/__init__.py:1105-1124)

Current flags: `path` (positional, optional), `--force`, `--dev`. Adding `--no-docling` follows the same pattern.

### Bundled Resource Packaging (pyproject.toml:46-54)

Resources are wheel-bundled via `force-include`:
```toml
"claude" = "agentic_mbse_data/claude"
"docs" = "agentic_mbse_data/docs"
"project_templates" = "agentic_mbse_data/project_templates"
```

The setup script needs to be added here.

### replicate_setup.sh Structure (scripts/replicate_setup.sh)

Five ordered functions called from `main()` (line 210-222):
1. `check_prerequisites`
2. `install_claude_components` — commands, agents (with sed substitution), skills (recursive copy), hooks
3. `create_settings_json`
4. `create_project_structure`
5. `create_source_index`

Docling setup would be a new function called from `main()`.

## Proposed Design

### High-Level Architecture

```
agentic-mbse init [--no-docling] [--force] [--dev] [path]
       │
       ├── (existing flow: commands, agents, hooks, templates, settings)
       │
       ├── Install pdf-analysis skill ←── modified: post-install SKILL.md transform
       │       │
       │       └── If docling enabled:
       │               │
       │               ├── Run setup-docling.sh as subprocess
       │               │     ├── Detect system → tier classification
       │               │     ├── Create ~/.local/bin/docling-mcp-wrapper.sh
       │               │     ├── Test MCP server launch
       │               │     ├── Register with claude mcp add --scope user
       │               │     └── Write ~/.docling-mcp-env.md
       │               │
       │               └── Read tier from setup output → patch SKILL.md with tier content
       │
       └── If --no-docling:
               └── Patch SKILL.md to remove Tier 2 sections
```

### Component 1: CLI Flag — `--no-docling`

**Location:** `src/agentic_mbse/cli/__init__.py:1119` (after `--dev` arg)

Add a new argument to the init parser:

```python
init_parser.add_argument(
    "--no-docling",
    action="store_true",
    help="Skip Docling MCP server setup (pdf-analysis skill will use Tier 1 + Tier 3 only)",
)
```

**Access in cmd_init:** `args.no_docling` (argparse converts hyphens to underscores)

### Component 2: Bundle Setup Script

**Source location:** Move `.project/active/pdf-skill/setup-docling.sh` → `scripts/setup-docling.sh`

This keeps it alongside `scripts/replicate_setup.sh`. The script is NOT part of `claude/` (it's not a skill, agent, or command) — it's an infrastructure script.

**Wheel packaging — `pyproject.toml` force-include:**

```toml
"scripts/setup-docling.sh" = "agentic_mbse_data/scripts/setup-docling.sh"
```

**Retrieval helper — `cli/__init__.py`:**

```python
def get_scripts_dir() -> Path:
    """Get path to bundled scripts directory."""
    return _get_data_root() / "scripts"
```

This follows the exact pattern of `get_commands_dir()`, `get_agents_dir()`, etc. (lines 130-157).

### Component 3: Setup Script Modifications

The existing `setup-docling.sh` needs two changes:

**3a. Output the tier to stdout for the caller to capture.**

Add a machine-readable output line at the very end of the script (after the summary):

```bash
# Machine-readable tier output (last line, for callers to parse)
echo "DOCLING_TIER=$TIER"
```

This lets `cmd_init()` capture the tier without parsing the human-readable output.

**3b. Accept `--force` from the caller.**

Already supported (line 27-30). `cmd_init()` passes `--force` when `args.force` is True.

### Component 4: Docling Setup Call in cmd_init()

**Location:** After skills install (line 833), before hooks install (line 835).

Rationale: Skills are installed first (including the pdf-analysis directory), then the Docling setup runs, then we post-process the SKILL.md based on the tier result. This order means the skill directory exists when we need to patch it.

```python
# === Setup Docling MCP (default, opt-out with --no-docling) ===
docling_tier = None  # None means no-docling; "constrained"/"moderate"/"comfortable" otherwise

if not getattr(args, "no_docling", False):
    setup_script = get_scripts_dir() / "setup-docling.sh"
    if setup_script.exists():
        print("\nSetting up Docling MCP server...")
        print("  (This may take a few minutes on first run — downloading ~500MB of models)")
        try:
            cmd = ["bash", str(setup_script)]
            if args.force:
                cmd.append("--force")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600,  # 10 minutes for first-run model download
            )
            # Parse tier from last line: "DOCLING_TIER=constrained"
            for line in reversed(result.stdout.splitlines()):
                if line.startswith("DOCLING_TIER="):
                    docling_tier = line.split("=", 1)[1].strip()
                    break
            if result.returncode == 0:
                print(f"  Docling MCP configured (tier: {docling_tier})")
                created.append(f"Docling MCP (tier: {docling_tier})")
            else:
                # Setup failed — fall back to no-docling skill variant
                print(f"\n  Warning: Docling setup failed (exit {result.returncode})",
                      file=sys.stderr)
                if result.stderr:
                    # Show last few lines of error
                    for errline in result.stderr.strip().splitlines()[-3:]:
                        print(f"    {errline}", file=sys.stderr)
                print("  pdf-analysis skill will use Tier 1 + Tier 3 only.", file=sys.stderr)
                docling_tier = None
        except subprocess.TimeoutExpired:
            print("\n  Warning: Docling setup timed out (>10 min)", file=sys.stderr)
            print("  pdf-analysis skill will use Tier 1 + Tier 3 only.", file=sys.stderr)
            docling_tier = None
        except Exception as e:
            print(f"\n  Warning: Docling setup error: {e}", file=sys.stderr)
            docling_tier = None
    else:
        print("  Warning: Docling setup script not found — skipping", file=sys.stderr)
else:
    print("\nSkipping Docling MCP setup (--no-docling)")
```

**Key decisions:**
- `capture_output=True` — we need to parse the tier from stdout; the script's progress messages go to stderr (via the `info()`, `ok()`, `warn()` helpers which write to stderr in the script). **Note:** The current script writes to stdout. We need to redirect its progress output to stderr so `capture_output=True` captures only the tier line on stdout. See Component 3 modification.

**Revised Component 3 detail:** Change the setup script's output helpers to write to stderr:

```bash
info()  { echo -e "${BLUE}[INFO]${NC} $*" >&2; }
ok()    { echo -e "${GREEN}[OK]${NC} $*" >&2; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $*" >&2; }
err()   { echo -e "${RED}[ERROR]${NC} $*" >&2; }
```

And keep the final `DOCLING_TIER=...` line on stdout. This cleanly separates machine-readable output from human-readable progress.

Actually, a simpler approach: don't capture output. Let the script's progress print directly to the user's terminal, and have the script write the tier to a known file instead.

**Revised approach — write tier to `~/.docling-mcp-env.md` (which already exists):**

The setup script already generates `~/.docling-mcp-env.md` with `Tier: **constrained**`. Rather than parsing stdout, `cmd_init()` reads the environment report after the subprocess completes:

```python
result = subprocess.run(cmd, timeout=600)
if result.returncode == 0:
    docling_tier = _read_docling_tier()  # Parse from ~/.docling-mcp-env.md
```

```python
def _read_docling_tier() -> str | None:
    """Read Docling tier from environment report."""
    env_report = Path.home() / ".docling-mcp-env.md"
    if not env_report.exists():
        return None
    for line in env_report.read_text().splitlines():
        if line.startswith("- Tier: **"):
            # Parse "- Tier: **constrained**" → "constrained"
            return line.split("**")[1]
    return None
```

This is cleaner: no stdout/stderr juggling, the environment report is already being generated, and we just read it after the fact.

### Component 5: Adaptive SKILL.md — Post-Install Patching

After the skill directory is installed and the tier is known, patch the SKILL.md.

**Approach:** Use conditional content blocks in the source SKILL.md with marker comments, then strip/retain sections during install.

**Source SKILL.md markers:**

```markdown
<!-- DOCLING_START -->
### Tier 2: Docling MCP (High-Fidelity Tables)
...all Tier 2 content...
<!-- DOCLING_END -->

<!-- TIER_HINT_START -->
**System tier: {DOCLING_TIER} — Max {MAX_PAGES} pages per Docling call.**
<!-- TIER_HINT_END -->
```

**Post-install processing function:**

```python
def _patch_skill_for_tier(
    skill_dir: Path,
    docling_tier: str | None,
) -> None:
    """Patch pdf-analysis SKILL.md based on Docling tier.

    Args:
        skill_dir: Path to installed .claude/skills/pdf-analysis/
        docling_tier: "constrained", "moderate", "comfortable", or None (no docling)
    """
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return

    content = skill_md.read_text()

    if docling_tier is None:
        # Remove everything between DOCLING markers (inclusive)
        content = re.sub(
            r"<!-- DOCLING_START -->.*?<!-- DOCLING_END -->\n*",
            "",
            content,
            flags=re.DOTALL,
        )
        # Remove tier hint block
        content = re.sub(
            r"<!-- TIER_HINT_START -->.*?<!-- TIER_HINT_END -->\n*",
            "",
            content,
            flags=re.DOTALL,
        )
        # Update description to reflect 2-tier pipeline
        content = content.replace(
            "(pymupdf4llm → Docling MCP → image fallback)",
            "(pymupdf4llm → image fallback)",
        )
        content = content.replace("3-tier", "2-tier")
    else:
        # Keep Docling sections, substitute tier placeholders
        max_pages = {"constrained": "1", "moderate": "5", "comfortable": "20"}
        content = content.replace("{DOCLING_TIER}", docling_tier)
        content = content.replace("{MAX_PAGES}", max_pages.get(docling_tier, "1"))
        # Strip marker comments (they served their purpose)
        for marker in ["DOCLING_START", "DOCLING_END", "TIER_HINT_START", "TIER_HINT_END"]:
            content = content.replace(f"<!-- {marker} -->\n", "")

    skill_md.write_text(content)

    # Also patch references/extraction-details.md with same logic
    details_md = skill_dir / "references" / "extraction-details.md"
    if details_md.exists():
        details_content = details_md.read_text()
        if docling_tier is None:
            details_content = re.sub(
                r"<!-- DOCLING_START -->.*?<!-- DOCLING_END -->\n*",
                "",
                details_content,
                flags=re.DOTALL,
            )
        else:
            for marker in ["DOCLING_START", "DOCLING_END"]:
                details_content = details_content.replace(f"<!-- {marker} -->\n", "")
        details_md.write_text(details_content)
```

**Called from cmd_init(), after both skill install and Docling setup:**

```python
# === Post-process pdf-analysis skill for tier ===
pdf_skill_dst = skills_dir / "pdf-analysis"
if pdf_skill_dst.exists():
    _patch_skill_for_tier(pdf_skill_dst, docling_tier)
```

**Dev mode consideration:** In dev mode, skills are symlinked. We MUST NOT modify symlinked files (that would change the source). Instead, for dev mode: break the symlink for SKILL.md only (copy the file, then patch it), or skip patching entirely (dev mode users are in the agentic-mbse repo and can manage their own Docling setup).

Recommendation: **Skip patching in dev mode.** Dev mode users are developers of agentic-mbse itself; they know what's available. The replicate_setup.sh can handle its own logic.

```python
if pdf_skill_dst.exists() and not is_dev_mode:
    _patch_skill_for_tier(pdf_skill_dst, docling_tier)
```

### Component 6: Source SKILL.md with Markers

The source `claude/skills/pdf-analysis/SKILL.md` needs marker comments added around Docling-specific content. This is the template that gets installed and then patched.

**Changes to SKILL.md:**

1. Wrap lines 38-53 (Tier 2 section) with `<!-- DOCLING_START -->` / `<!-- DOCLING_END -->`
2. Add a tier hint block after the pipeline intro (line 20)
3. Wrap the Tier 2 row in the "When to Skip Tiers" table

**Changes to references/extraction-details.md:**

1. Wrap lines 32-77 (Docling MCP Details section) with `<!-- DOCLING_START -->` / `<!-- DOCLING_END -->`

### Component 7: YAML Frontmatter Description Adaptation

The SKILL.md YAML frontmatter `description` field also mentions the 3-tier pipeline:

```yaml
description: >
  ...Provides a 3-tier extraction pipeline
  (pymupdf4llm → Docling MCP → image fallback)...
```

The `_patch_skill_for_tier()` function already handles this via the string replacement:
```python
content = content.replace(
    "(pymupdf4llm → Docling MCP → image fallback)",
    "(pymupdf4llm → image fallback)",
)
content = content.replace("3-tier", "2-tier")
```

This ensures Claude Code's skill triggering description accurately reflects what's available.

### Component 8: replicate_setup.sh Updates

**Add a new function** `setup_docling_mcp()` and call it from `main()`:

```bash
setup_docling_mcp() {
    if [[ "${NO_DOCLING:-false}" == "true" ]]; then
        echo -e "${YELLOW}.${NC} Docling MCP setup skipped (NO_DOCLING=true)"
        return
    fi

    local setup_script="$REPO_ROOT/scripts/setup-docling.sh"
    if [[ ! -f "$setup_script" ]]; then
        echo -e "${YELLOW}Warning:${NC} Docling setup script not found at $setup_script"
        return
    fi

    echo ""
    echo "Setting up Docling MCP server..."

    if bash "$setup_script"; then
        log_created "Docling MCP server (see ~/.docling-mcp-env.md)"
    else
        echo -e "${YELLOW}Warning:${NC} Docling MCP setup failed — pdf-analysis will use Tier 1 + 3 only"
    fi
}
```

**Call site:** In `main()` (line 217), after `install_claude_components`:

```bash
main() {
    cd "$REPO_ROOT"
    echo "Replicating agentic-mbse setup in $REPO_ROOT"
    echo ""
    check_prerequisites
    install_claude_components
    setup_docling_mcp          # NEW
    create_settings_json
    create_project_structure
    create_source_index
    print_summary
}
```

**Skill patching in replicate_setup.sh:** Not needed in dev mode (see Component 5 reasoning). The replicate_setup.sh is a dev-mode tool.

### Component 9: pyproject.toml Bundling

Add the setup script to the wheel build:

```toml
[tool.hatch.build.targets.wheel.force-include]
"claude" = "agentic_mbse_data/claude"
"docs" = "agentic_mbse_data/docs"
"project_templates" = "agentic_mbse_data/project_templates"
"SOURCE_INDEX.md.template" = "agentic_mbse_data/SOURCE_INDEX.md.template"
"scripts/setup-docling.sh" = "agentic_mbse_data/scripts/setup-docling.sh"
```

And in sdist:

```toml
[tool.hatch.build.targets.sdist]
include = [
    "src/",
    "claude/",
    "docs/",
    "project_templates/",
    "scripts/setup-docling.sh",
    "SOURCE_INDEX.md.template",
    "tests/",
    "README.md",
    "pyproject.toml",
]
```

### Component 10: pymupdf4llm Availability Check

After the Docling setup (or skip), check whether pymupdf4llm is importable and print guidance:

```python
# === Check pymupdf4llm availability (needed for Tier 1 + Tier 3) ===
try:
    subprocess.run(
        [sys.executable, "-c", "import pymupdf4llm"],
        capture_output=True,
        timeout=10,
    )
except (subprocess.CalledProcessError, subprocess.TimeoutExpired, Exception):
    print("\n  Note: pymupdf4llm not found. PDF extraction (Tier 1 + 3) requires it.")
    print("  Install with: uv add agentic-mbse[extract]")
```

This is guidance only — not a hard failure.

## Data Flow Summary

```
User runs: agentic-mbse init
  │
  ├── [existing steps: commands, agents install]
  │
  ├── Install skills (including pdf-analysis directory)
  │     └── _install_directory() copies full skill dir
  │
  ├── If NOT --no-docling:
  │     ├── subprocess.run(["bash", "setup-docling.sh"])
  │     │     ├── Detect RAM/GPU/cores → classify tier
  │     │     ├── Create ~/.local/bin/docling-mcp-wrapper.sh
  │     │     ├── Test server launch (up to 120s)
  │     │     ├── Register: claude mcp add --scope user
  │     │     └── Write ~/.docling-mcp-env.md
  │     │
  │     ├── _read_docling_tier() → parse tier from env report
  │     └── _patch_skill_for_tier(pdf_skill_dir, tier)
  │           ├── Substitute {DOCLING_TIER} and {MAX_PAGES}
  │           └── Strip marker comments
  │
  ├── If --no-docling:
  │     └── _patch_skill_for_tier(pdf_skill_dir, None)
  │           ├── Remove <!-- DOCLING_START -->...<!-- DOCLING_END --> blocks
  │           ├── Update "3-tier" → "2-tier" in description
  │           └── Remove mcp__docling references from YAML description
  │
  ├── Check pymupdf4llm availability (guidance message)
  │
  └── [existing steps: hooks, templates, settings.json, summary]
```

## File Changes Summary

| File | Change Type | Description |
|------|-------------|-------------|
| `src/agentic_mbse/cli/__init__.py` | Modify | Add `--no-docling` flag, Docling setup subprocess call, `_read_docling_tier()`, `_patch_skill_for_tier()`, `get_scripts_dir()`, pymupdf4llm check |
| `scripts/setup-docling.sh` | New (move from `.project/active/pdf-skill/`) | Bundled setup script |
| `scripts/replicate_setup.sh` | Modify | Add `setup_docling_mcp()` function, call from `main()` |
| `claude/skills/pdf-analysis/SKILL.md` | Modify | Add `<!-- DOCLING_START/END -->` markers around Tier 2 content, add `{DOCLING_TIER}` and `{MAX_PAGES}` placeholders |
| `claude/skills/pdf-analysis/references/extraction-details.md` | Modify | Add `<!-- DOCLING_START/END -->` markers around Docling MCP Details section |
| `pyproject.toml` | Modify | Add `scripts/setup-docling.sh` to wheel and sdist includes |

## Potential Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Setup script timeout on first run (500MB model download) | Medium | Low | 10-minute timeout, graceful fallback to no-docling skill |
| OOM during launch test on constrained systems | Medium | Low | Script already handles OOM detection; init falls back to 2-tier |
| `claude` CLI not in PATH (e.g., non-standard install) | Low | Low | Warn and continue; skill works at Tier 1 + 3 |
| Setup script fails on macOS (`/proc/meminfo` is Linux-only) | High on macOS | Medium | Known limitation; document in help text. Future: add macOS `sysctl` support |
| Re-init patches already-patched SKILL.md | Low | Low | `_install_directory()` always replaces the full directory from source before patching, so each init starts fresh |
| Dev mode symlink + patching conflict | None | N/A | Skip patching in dev mode entirely |

## Integration Strategy

This feature integrates into the existing init flow with minimal disruption:

- **Additive to cmd_init():** New code goes between skills install and hooks install — no changes to existing steps
- **Follows existing patterns:** `get_scripts_dir()` mirrors other `get_*_dir()` helpers; subprocess follows `_get_git_commit()` pattern; skill patching follows agent substitution pattern
- **Graceful degradation:** Every failure path falls back to a working 2-tier skill — init never fails due to Docling
- **Backward compatible:** `--no-docling` is opt-out; existing users who don't pass it get Docling automatically

## Validation Approach

### Automated Tests

Add to `tests/test_cli.py`:

1. **Test `--no-docling` flag parses correctly** — verify `args.no_docling` is set
2. **Test `_read_docling_tier()` parsing** — create a mock `~/.docling-mcp-env.md` with each tier, verify correct parsing
3. **Test `_patch_skill_for_tier()` with no-docling** — verify Docling sections removed, "2-tier" in description
4. **Test `_patch_skill_for_tier()` with each tier** — verify placeholders substituted, markers stripped
5. **Test init with `--no-docling` end-to-end** — verify installed SKILL.md has no `mcp__docling__` references

### Manual Verification

1. Run `agentic-mbse init` on a test directory → verify `/mcp` shows `docling: connected`
2. Run `agentic-mbse init --no-docling` → verify SKILL.md contains only Tier 1 + 3
3. Run `agentic-mbse init` twice → verify no duplicate MCP registrations
4. Check `~/.docling-mcp-env.md` contains correct tier classification
5. Invoke `/pdf-analysis` skill → verify it works with the installed tier

---

**Next Step:** After approval → `/_my_plan` or `/_my_implement`
