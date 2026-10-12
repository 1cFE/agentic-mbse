# Dry runs O2a and O2b: fresh agent, installed files only

Run by a subagent of the orchestrator on 2026-10-12. Both dry runs pass. O2a (criterion 2) took one request end to end to `REGISTERED` through the installed `research-acquire` skill. O2b (criterion 7) ran five `/manage-sources` calls, and each one did what it should through the CLI alone. Six `claude -p` sessions cost $1.07 in total. No agent asked a blocking question, refused, or touched a registry file directly.

`<scratch>` below is `/tmp/claude-1000/-home-reid-1cfe-agentic-mbse/581ef20b-ac97-4a85-951d-c6d180acd020/scratchpad/seam-dry-run`, outside any git repository.

## Toolkit: the wheel

- `uv build /home/reid/1cfe/agentic-mbse-research-seam --wheel` at `d49d119` gave `agentic_mbse-0.1.3-py3-none-any.whl`.
- `unzip -l` lists all twelve modules of `agentic_mbse/research/`, `agentic_mbse_data/docs/research-seam.md`, `agentic_mbse_data/skills/research-acquire/SKILL.md` and `agentic_mbse_data/skills/manage-sources/SKILL.md` (`setup-checks.txt`).
- The worktree's HEAD moved to `5e70d26` during the run. The two new commits (`cd5548e`, `5e70d26`) touch only `.project/` files, so the wheel matches every shipped file at the new HEAD too.

## Install and isolation

The method follows `.project/completed/20261012_goal-layer-port/evidence/dry-run/install.md`.

- **Install.** `uv venv <scratch>/venv --python 3.12`, then `uv pip install "<wheel>[web]"` with the GitLab extra index. That installed `agentic-mbse==0.1.3` from the wheel file, `syside==0.8.4`, `trafilatura==2.3.1` and `pymupdf4llm==1.28.2`.
- **Targets.** Two fresh directories, `<scratch>/o2a-target` and `<scratch>/o2b-target`. Each was `git init`ed, then `agentic-mbse init <target> --assistant claude < /dev/null` ran with `PATH` and `VIRTUAL_ENV` pointing at the scratch venv (rc 0). The init state was committed as `f536f15` in each scratch repo.
- **Agent.** Each call ran in the target with the same `PATH` and `VIRTUAL_ENV`, `SYSIDE_LICENSE_KEY` taken from the environment and never written to a file, and `claude -p "<prompt>" --setting-sources project,local --permission-mode acceptEdits --allowedTools "Bash Read Write Edit Glob Grep Skill WebSearch WebFetch" --output-format stream-json --verbose --max-budget-usd 10`.
- **What the agent could see.** The init line of every stream lists no `_my_*` command and none of the owner's user-level skills. It shows no MCP servers, only built-in plugins, and a new, empty memory path. The skills are the target's installed skills plus Claude Code built-ins. The agents are the target's installed expert roles plus built-ins. Model `claude-opus-5-5`, Claude Code 2.1.296.
- **No fusion-tea code on any path.** `PATH` has no fusion-tea entry and `PYTHONPATH` is empty. From the target, `uv run python -c 'import agentic_mbse; …'` resolves to the scratch venv. The venv's site-packages hold no fusion-tea module.

## Setup checks (both targets, identical)

| Check | Result | Evidence |
|---|---|---|
| `knowledge/research/requests/runs/` and `negatives/` exist | yes | `ls -d` lists both (`setup-checks.txt`) |
| `.gitignore` holds the two lines | yes | `.gitignore:59: knowledge/.staging/`, `.gitignore:60: knowledge/.registry.lock` |
| `install-commands --list` names `research-acquire` | yes | line 17, `  - research-acquire`, under "Workflows (18)" |
| Installed skills match the worktree source | yes | `diff -rq .claude/skills/{research-acquire,manage-sources}` against `skills/` is empty |
| Fresh registry is clean | yes | `agentic-mbse research verify` → `0 fault(s), 0 legacy entry(ies)`, rc 0 |

## O2a, criterion 2: one request end to end — PASS

- **Pre-check.** `agentic-mbse extract https://en.wikipedia.org/wiki/Copper --save-source --output <scratch>/precheck --budget 0` returned rc 0 (`ok … 191,029 chars, backend: trafilatura`). The output has `| Thermal conductivity | 401 W/(m⋅K) |`. No swap was needed.
- **Request.** `knowledge/research/requests/REQ-001-01.json` holds the specified fields (`o2a-request.json`). They match the installed skill's request section (`.claude/skills/research-acquire/SKILL.md:44-66`) and the code's `REQUIRED_REQUEST_FIELDS` (`agentic_mbse/research/seam.py:37-44`). No mismatch.
- **Prompt.** `Follow the research-acquire skill on knowledge/research/requests/REQ-001-01.json.`
- **What the agent did.** It loaded the skill and read `.agentic-mbse/claude.md`. It grepped the project's instructions for a quarantine rule (rule 4), ran `open`, logged one search, ran WebSearch and WebFetch for triage, logged the page as a keeper, registered it, and closed. It used 1 of 2 searches and 1 of 1 captures. It closed with `--adequacy limit_reached`, then committed its work in the scratch repo (`add5dba`), as `SKILL.md:170` tells it to.

| Pass condition | Result | Evidence |
|---|---|---|
| Newest `runs/REQ-001-01/*/return.json` has class `REGISTERED` | PASS | Only run `20261012T211447786845`; `o2a-return.json`: `"class": "REGISTERED"`, `registered: [{"slug": "copper_wikipedia", "pre_existing": false}]`, `queued: []` |
| A source directory exists under `knowledge/sources/` | PASS | `knowledge/sources/copper_wikipedia/` with `raw.html`, `output.md`, `metrics.json` |
| `knowledge/MANIFEST.jsonl` has its row | PASS | `o2a-manifest-row.jsonl`: `"slug": "copper_wikipedia"`, `"source_kind": "url"`, `raw_sha256 0df720b4…`, `extract_sha256 7762a999…` |
| `knowledge/SOURCE_INDEX.md` has its block | PASS | `o2a-index-block.md`: `### Copper - Wikipedia`, Type `url`, Location `knowledge/sources/copper_wikipedia/`, Use for, Validation, Caveat, Extended Metadata |
| The run directory has a receipt | PASS | `receipts/20261012T211509-001.json` (`o2a-receipt.json`): `"outcome": "registered"`, `"triage": "keeper"`, `"captured": true` |
| `agentic-mbse research verify` exits 0 | PASS | Run by me after the session: `0 fault(s), 0 legacy entry(ies)`, rc 0. `research sources` → `registered url Copper - Wikipedia — knowledge/sources/copper_wikipedia/` |
| `git status --porcelain` shows neither `.staging` nor `.registry.lock` | PASS | Plain porcelain is empty. `--ignored` shows `!! knowledge/.registry.lock`. `.staging/` exists empty, and `git check-ignore -v` names `.gitignore:59`. The agent's own `git status --short` before its commit listed only `SOURCE_INDEX.md`, `MANIFEST.jsonl`, `runs/` and `sources/`, and its `git add knowledge/` left the lock out (`o2a-git-log.txt`) |
| Transcript shows `open`, `log`, `register`, `close`; no direct index or manifest edits | PASS | Bash calls: `research open …` (exit 0), `research log … --search`, `research log … --candidate … --triage keeper` + `research register --url https://en.wikipedia.org/wiki/Copper … --run $R` (exit 0), `research close $R --adequacy limit_reached`. The stream has zero Write, Edit, MultiEdit or NotebookEdit calls and no Read of the index or manifest |

Cost $0.29, 12 turns, 41 s, result `success`. The session used `claude-opus-5-5` plus `claude-haiku-5-5`, likely for WebFetch's summary.

## O2b, criterion 7: `/manage-sources` by hand — PASS

**Fixtures.** `docs/widget_note.pdf` was made with pymupdf and holds the text "Widget Note: the widget's rated load is 12 kN.". It was committed as `10a7275`. `<scratch>/ref-code/widget_controller.py` sits outside the target. I committed the scratch repo after each call, so `o2b-git-log.txt` shows each call's file changes on their own. Call 3 changed nothing, so it has no commit.

**Prompt wording.** Calls 1 to 3 use the specified wording. Calls 4 and 5 add "I confirm the removal." because the skill's remove path asks for a confirmation (`manage-sources/SKILL.md:101`).

| Call | Prompt (after `/manage-sources`) | CLI call the agent made | Result | Evidence |
|---|---|---|---|---|
| 1 | Add the PDF `docs/widget_note.pdf`, title "Widget Note", with use-for, validation and caveat; it can be captured | `research register --local-pdf docs/widget_note.pdf --title "Widget Note" --use-for … --validation … --caveat …` → `"outcome": "registered"`, slug `widget_note` | PASS | Manifest row (`o2b-1-manifest-row.jsonl`): `source_kind local_pdf`, `origin_path docs/widget_note.pdf`, `raw_sha256` = `raw_artifact_sha256` = `a65c2164…`, `extract_sha256 eab71d8c…`. Directory `knowledge/sources/widget_note/`. Raw copy `knowledge/raw/widget_note.pdf`, with the same sha256 as `docs/widget_note.pdf`. Index block `o2b-1-index-block.md`. `sources` → `registered local_pdf Widget Note — knowledge/sources/widget_note/`. `verify` rc 0 |
| 2 | Add the codebase at `<scratch>/ref-code`, title "Reference Code", type codebase, validation N/A; it cannot be captured | `ls -la <scratch>/ref-code`, then `research add-entry --title "Reference Code" --type codebase --location "<scratch>/ref-code" --use-for … --validation "N/A"` → `"outcome": "added"` | PASS | Block `o2b-2-index-block.md`: Location is the absolute path exactly as given. The manifest still has one row, with no `ref-code`. `sources` → `hand-curated codebase Reference Code — <scratch>/ref-code`. `verify` rc 0 |
| 3 | List all sources | `research sources` only | PASS | The agent's reply table: `\| 1 \| registered \| local_pdf \| Widget Note \|` and `\| 2 \| hand-curated \| codebase \| Reference Code \|`, plus "None are unregistered". Working tree unchanged |
| 4 | Remove "Widget Note"; reason "dry-run cleanup" | `research retire --slug widget_note --reason "dry-run cleanup"` → `retired widget_note`, with the removed manifest row, source dir, raw copy and index block listed | PASS | `knowledge/RETIRED.jsonl` gained one line (`o2b-4-retired.jsonl`): `"slug": "widget_note"`, `"reason": "dry-run cleanup"`, `index_block_sha256`, the full row. The manifest is empty, `knowledge/sources/` and `knowledge/raw/` are empty, and the block is gone (grep count 0). `docs/widget_note.pdf` is untouched. `verify` rc 0 |
| 5 | Remove "Reference Code" | `research remove-entry --title "Reference Code"` → `"outcome": "removed"` | PASS | The block is gone and `sources` prints nothing. `verify` rc 0. `<scratch>/ref-code` is untouched. The index is back to blob `a545f09`, the same as the init state: `git diff f536f15 HEAD -- knowledge/SOURCE_INDEX.md` is empty |

**No direct edits — PASS.** None of the five streams has a Write, Edit, MultiEdit or NotebookEdit call. No Bash call redirects, copies, moves or deletes into `SOURCE_INDEX.md`, `MANIFEST.jsonl`, `RETIRED.jsonl` or `knowledge/sources/`. Across all six streams the agents used only these tools: Bash 18 times, Read 4 (all `.agentic-mbse/claude.md`), Grep 1 (for `ref-code` under `.claude/`), plus Skill, ToolSearch, WebSearch and WebFetch once each, all in O2a. Each index change in `o2b-git-log.txt` matches its call's CLI output.

**Not exercised.** The skill's "Edit a hand-curated entry" (`add-entry --replace`) and "Resolve a queued candidate" paths were not run. Criterion 7 does not name them.

## Costs

| Stream | Result | Cost (USD) | Turns | Seconds |
|---|---|---|---|---|
| `o2a-research-acquire.jsonl` | success | 0.2892 | 12 | 41.1 |
| `o2b-1-add-pdf.jsonl` | success | 0.1766 | 5 | 22.0 |
| `o2b-2-add-codebase.jsonl` | success | 0.1590 | 4 | 11.8 |
| `o2b-3-list.jsonl` | success | 0.1363 | 3 | 7.9 |
| `o2b-4-remove-pdf.jsonl` | success | 0.1515 | 4 | 10.2 |
| `o2b-5-remove-codebase.jsonl` | success | 0.1619 | 6 | 11.6 |
| **Total** | | **1.0746** | | |

No stream recorded a permission denial.

## Observations

None of these failed a check. They are recorded for the audit.

- **Init's read permissions were ignored in every session.** Each `claude -p` printed `Ignoring 3 permissions.allow entries from .claude/settings.json: this workspace has not been trusted` (`o2a.stderr.txt`, `o2b.stderr.txt`). Those are init's Read, Grep and Glob grants for the packaged docs directory. No agent read the docs directory, so nothing here depended on them. A headless run in a target nobody has opened interactively gets none of init's permission grants. This is Claude Code's trust rule, not a toolkit defect.
- **`runs/` and `negatives/` are empty directories with no placeholder file,** so git does not track them, and a clone of the init commit will not have them. `open` created `runs/REQ-001-01/<ts>/` on demand, so O2a did not depend on the directory existing. Whether `close` writes a negative into a missing `negatives/` was not tested here.
- **`limit_reached` stays `null` when the capture limit is spent exactly.** The agent used 1 of 1 captures and closed with `--adequacy limit_reached`, but `return.json` has `"limit_reached": null`. This is the code's design. `_limit_reached` (`agentic_mbse/research/seam.py:366-377`) reports `max_captures` only after a `register` call is refused at the cap, and `--adequacy` affects only a filed negative (`seam.py:268-276`). `research-acquire/SKILL.md:162` ("Use `--adequacy limit_reached` if you stopped because of a declared limit") does not say the flag is inert on a `REGISTERED` run. A reader could expect it to show up in the return.
- **Raw copies land in different places for the two capture kinds.** A URL capture keeps its raw copy inside the source directory as `raw.html`, and no `knowledge/raw/` entry appears. A local PDF also gets `knowledge/raw/<slug>.pdf`. `retire` removed that copy, as its help says.
- **`research sources` prints nothing for an empty index** (rc 0). Both agents read that correctly as "no entries". `manage-sources/SKILL.md:40` says it prints one line per entry, which is consistent with printing nothing.
- **There is no question tool in `-p` mode.** The session's tool list has no `AskUserQuestion`, yet `manage-sources` routes choices through "the host question interface" (`SKILL.md:42`, `:54`, `:101`). The prompts carried every detail, so no agent needed to ask. Call 2 ended with a text offer to add read permissions for `<scratch>/ref-code`, as `SKILL.md:95` says to, and left `.claude/settings.json` unchanged.
- **Small variance.** Call 4's agent did not read `.agentic-mbse/claude.md` first; the other five sessions did. The O2a agent committed its own run (`SKILL.md:170`). The O2b agents did not commit. Calls 1 and 4 said the changes were uncommitted.

## Files

- `README.md`: this record.
- `setup-checks.txt`: wheel contents, install lines, the per-target setup checks and the pre-check output.
- `o2a-research-acquire.jsonl`: the O2a stream. `o2a-request.json`, `o2a-return.json`, `o2a-receipt.json`, `o2a-manifest-row.jsonl` and `o2a-index-block.md` are copied from the target. `o2a-git-log.txt` is the scratch repo's history with stats. `o2a.stderr.txt` is the session's stderr.
- `o2b-1-add-pdf.jsonl` through `o2b-5-remove-codebase.jsonl`: one stream per call. `o2b-1-manifest-row.jsonl`, `o2b-1-index-block.md`, `o2b-2-index-block.md` and `o2b-4-retired.jsonl` are the state after the matching call. `o2b-git-log.txt` holds the per-call commits. `o2b.stderr.txt` holds the five sessions' stderr.
