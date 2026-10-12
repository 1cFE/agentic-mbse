# Implementation Plan: Port the research acquisition seam, and bring `/manage-sources` under its rules

**Status:** Implementation in progress (P1, P2 complete)
**Created:** 2026-10-12
**Last Updated:** 2026-10-12
**Work item:** `WRAP-SPLIT` Item 5, branch `research-seam-port`, worktree `/home/reid/1cfe/agentic-mbse-research-seam`

## Source Documents

- **Spec:** `spec.md` (criteria 1–9 are cited below as "criterion *n*").
- **Design:** `design.md`, revised after review. D1–D18, I1–I8 and Appendices A–D are cited by number. Component details, exact texts and the test assignments (Appendix B) live there, not here.
- **Review:** `design-review.md`. M1–M5 and A1–A18 are applied in the design (see its Resolutions).
- **Align:** `briefs/align.md`. **O1 baseline:** `evidence/o1-baseline.md`.
- **Code to port:** `.orchestrate-logs/fusion-tea-snapshot/` (fusion-tea `0a833b9f7`, current as of `c42ed1d8a`). Read-only. Cited below as "snapshot".

## The Point

A target brings an outside source into `knowledge/` through one checked door, with proof it is there, using only what `agentic-mbse init` installs. [OWNER-VERBATIM] 2026-10-06: "yes, we need this capability in agentic-mbse."

A user managing sources by hand goes through the same door. [OWNER-VERBATIM] 2026-10-09, on `/manage-sources`: "MORE useful as a general skill which allows direct user management while it folows and enforces the rules".

[INHERITED: epic, owner no-loss 2026-10-06] fusion-tea switches over with no data migration and no lost instruction. Its 123 manifest rows, 61 run directories and one bounded negative are read as they are.

Why now: the installed `run-goal` (Item 2) delegates every acquisition to this seam. Without it, an installed goal layer points at a procedure no other target has.

So the work is checked against more than the design. fusion-tea's live data must still read the same (O1). A fresh target with no fusion-tea code must be able to acquire a source and curate by hand (O2a, O2b).

## Implementation Strategy

**Phasing rationale.** The phases are the design's Next-Stage Handoff, P1–P6. The order follows "copy, then split" (design § Implementation Notes): pin the on-disk shapes first, then move code module by module under those pins, leaves before the ladders that use them.

- **P1** freezes every byte-level expectation from the snapshot and lands the support modules.
- **P2** moves the riskiest code: the register ladder, capture, and commit/rollback. The hook is a no-op stub.
- **P3** adds the hook's fail-closed paths while the ladder is fresh.
- **P4** finishes the registry (hand-curated entries, `retire`, `verify`). That unlocks the first check against real data, O1 parity.
- **P5** adds the seam bookkeeper, the CLI and `init`: the surfaces a target touches.
- **P6** is text: skills, docs, templates, and their contract tests.

**How the golden tests land (I1).** The brief asks for the I1 golden tests before the first code moves. The design asks for each to land in the phase that moves its code, before that code. This plan does both. P1 derives every golden expectation from the snapshot once and freezes it as test data. Each later phase opens by adding the golden tests for the code it moves, reading that frozen data. No expectation is ever computed from ported code.

**Critical path.** P1 golden data → P2 ladder → P3 hook → P4 `verify` → **Orchestrator: O1 parity** → P5 CLI → P6 skills → **Orchestrator: O1 rest, O2a, O2b** → `/_my_audit`.

**First proof point.** End of P1: the package's insertion bytes at `## How Sources Are Used` equal the snapshot's for the same inputs, and a keyed batch block equals the snapshot's Zotero block. The first proof against real data is O1 parity, right after P4.

**Biggest risks** (full list: design § Potential Risks):

- **The new parser reads fusion-tea's index differently (bet B1).** O1 parity runs right after P4, before the CLI and skills are built on the parser.
- **A fresh target breaks where fusion-tea never did** (no manifest, the shipped index's other anchor and its commented examples). Every behaviour test builds its tree from the shipped template with no manifest file, from P1 on (D18).
- **P6's template edit silently changes what earlier byte tests mean.** The golden fixtures rule below keeps byte tests off the live template.
- **Effort.** Design estimate P1–P6 is 18.5h, plus O1 1.5h and O2 1.5h.

## Conventions for every phase

**Exit check.** The same for every phase. Run from the worktree root.

- [ ] `uv run pytest tests/` shows no new failures: 0 failed and 0 errors; 1 skipped and 1 xfailed, as in the baseline; passed at least 2,217 and rising with new tests; deselected rising only by new `slow` tests. Baseline: `.orchestrate-logs/baseline-pytest.txt` (2,217 passed, 1 skipped, 1 xfailed, 5 deselected at `ac5fb1a`, under `uv sync --all-extras`).
- [ ] `uv run pytest tests/test_research -m ""` passes, so the ported `slow` tests run too.
- [ ] `uv run ruff check src/ tests/` reports at most 118 findings (`.orchestrate-logs/baseline-ruff.txt`), none in a file this item adds or edits.
- [ ] `uv run mypy src/` reports at most 88 errors (`.orchestrate-logs/baseline-mypy.txt`), none in a file this item adds or edits. No baseline finding sits in a file this item edits, so any finding there is new.
- [ ] One commit for the phase, with a subject that leads with what changed (for example "Add research package support modules and golden shape tests").

**Commit when resumed.** An implement stage started fresh commits itself. A resumed one cannot. It writes `.orchestrate-logs/commit-steps/P<n>.md` with the commit subject and body, the exact `git add` path list and the exit-check output, and the orchestrator commits.

**Boundaries.**

- Do not edit `src/agentic_mbse/cli/installation.py`; Item 3's branch edits it. `pyproject.toml` and `scripts/replicate_setup.sh` also stay unchanged (Appendix A).
- Stages read fusion-tea only through the snapshot. They never touch fusion-tea, `~/.claude/`, anything outside this worktree, or `claude -p`. Steps marked **Orchestrator** are not stage work.
- Do not change ladder order or messages while splitting. The behaviour changes are exactly the design's Behaviour Changes table.
- Typing per design § Implementation Notes "mypy and ruff". Run `uv run ruff format` on new files only.
- The worktree root has a `knowledge/` directory (`KNOWLEDGE.md`, `SOURCE_INDEX.md`). `default_paths()` is cwd-relative, so a test that forgets to inject paths writes there. The conftest session check (P1) catches it.

**Golden fixtures rule.** Byte-level golden tests read frozen inputs and expected outputs from `tests/test_research/golden/`, never the live template, so P6's template edit cannot move them. Behaviour tests build their tree from the live shipped template (`get_template_path()`, which reads `SOURCE_INDEX.md.template` at the repo root) with no manifest file (D18). Round-trip tests compare a tree against its own before-bytes. Both stay meaningful when the template changes.

---

## Phase 1: Support modules, `__main__`, and the golden data

### Goal

Freeze the byte-level expectations and land the modules everything else stands on, before any ladder code moves.

### Assumption under test

The snapshot's on-disk shapes (index insertion bytes, the Zotero batch block, receipt key order, manifest rollback) can be reproduced by small typed modules that name no consumer. The shipped index, with its other anchor, its commented examples and no manifest, works with them.

### Test stencil (write first)

Function names are the implementer's; the design leaves them open.

```python
# tests/test_research/test_golden_shapes.py
GOLDEN = Path(__file__).parent / "golden"

@pytest.mark.parametrize("case", ["anchor_how_sources", "anchor_how_this_file", "eof_newline", "eof_no_newline"])
def test_insertion_bytes(case, tmp_path):
    index = tmp_path / "SOURCE_INDEX.md"
    index.write_bytes((GOLDEN / f"index/{case}.before.md").read_bytes())
    insert_block(index, (GOLDEN / "index/block.md").read_text())
    assert index.read_bytes() == (GOLDEN / f"index/{case}.after.md").read_bytes()

def test_keyed_batch_block_equals_the_snapshot_block():
    block = render_batch_block(**BATCH_INPUTS, key_label="Zotero Key", key_display="5428393:ABCD1234")
    assert block == (GOLDEN / "index/batch_block.md").read_text()
```

### Changes

**Golden data, first of all.**

- [x] Write a scratch derivation script at `.orchestrate-logs/golden/derive.py` (gitignored; keep it as provenance). It imports the snapshot's scripts by path. `pyzotero` is not installed here, so put a stub module in `sys.modules` first (`dotenv` is installed; `holdout_guard` reads its protocol lazily). Fix the date, because blocks and rows carry `date.today()`.
- [x] Derive and save: a fixed request and its key (`research_seam.request_key`, `:70-83`); the index before and after one `append_source_index_entry` at `## How Sources Are Used`, for a seam block and a batch block (`zotero_ingest.py:225-350`, with `SOURCE_INDEX_PATH` patched); the Zotero batch block for fixed inputs; the key order of a receipt (`source_registry.py:1217-1229`), of `url`, `local_pdf` and Zotero manifest rows (`:667-686` with each source's `row_extras`), and of a return and a negative (run the snapshot's `close` on a temp run directory).
- [x] Copy the outputs into `tests/test_research/golden/`. Add the cases the snapshot cannot produce from the design's stated bytes (Architecture § Insertion bytes): insertion before `## How This File Is Used`, and the end-of-file fallback with and without a trailing newline. The docstring of `test_golden_shapes.py` names the snapshot function each expectation came from.

**Tests, by Appendix B row.**

- [x] `__init__.py`: move.
- [x] `conftest.py`, agentic-mbse half: shipped-template tree with no manifest, `local_site`, pymupdf `generated_pdf`, `run_dir`, `FakeGuard` and a recording variant (used in P4), plus the session check that the suite creates nothing under the repo root's `knowledge/` (design Implementation Notes "Test fixtures", review A13).
- [x] `fixtures/web/`: move `utf8.html`, `latin1.html`, `marker.html`. Replace `marker.html`'s sealed-paper token with a neutral token the fake guard bars.
- [x] `test_golden_shapes.py` (new, I1), P1 cases: insertion bytes at both anchors and both fallback forms; the keyed batch block equals the snapshot's Zotero block; receipt key order.
- [x] `test_index_writer.py`: move, rewritten for both anchors, the end-of-file fallback (replacing "missing anchor raises"), comment masking and the keyed batch block. Add the D10 block ends (the next heading outside a comment, or a line opening a comment) and Location normalization (Architecture § Locations and titles).
- [x] `test_zotero_path_contract.py`, first half: batch-block field order and values, with a neutral key. Keyed dedupe waits for P2.
- [x] `test_manifest.py` (new): `test_load_manifest_rows_returns_every_row` and `test_truncate_manifest_restores_recorded_byte_length` move here, plus append. Add the absent-aware rollback: rolling back to a "no manifest" mark removes the file (I3; Research Findings on `zotero_lib.py:111-114`).
- [x] `test_sources.py` (new): `KeyedFileSource.__post_init__` refusals for `kind`, `key_field` and `key` (design § The keyed kind, review A9); `slugify`; URL normalization.
- [x] `test_main_module.py` (new): `python -m agentic_mbse --help` exits 0 (D13).
- [x] `test_no_consumer_names.py` (new, I8): the criterion-5 pattern over `src/agentic_mbse/research/`. P6 adds the skill and guide.

**Code.**

- [x] `src/agentic_mbse/__main__.py` (D13).
- [x] `research/__init__.py`: exports only the D2 names that exist so far. The list is complete at P3.
- [x] `research/paths.py`, `research/manifest.py`, `research/sources.py`: per Component Overview, D6, D8.
- [x] `research/runs.py`: per Component Overview. The receipt writer takes the receipt fields as keyword arguments and builds the dict in the snapshot's order, so P1 pins receipt key order without `register.py`.
- [x] `research/index.py`: the parser (D10; masking keeps offsets, per Implementation Notes), the anchor rule and insertion bytes (D9), seam and batch block rendering, cut and replace, Location normalization and title matching. `add_entry`, `remove_entry` and `list_entries` wait for P4.

**Satisfies:** D6, D8, D9, D10, D13, D18 (fixtures); I1 (P1 cases), I3 (manifest half), I8 (package half).

### Validation

- [x] Exit check.
- [x] Manual: `uv run python -m agentic_mbse extract --help` prints the `extract` usage.

**What we know works after P1:** the package writes index blocks byte-identical to the snapshot's at either anchor, appends correctly at end of file, keeps receipt key order, and rolls back a manifest that did not exist.

### Implementation Notes

#### Phase 1 Completion

**Completed:** 2026-10-12.

**Exit check.**

- `uv run pytest tests/`: 2,325 passed, 1 skipped, 1 xfailed, 5 deselected, 0 failed (baseline 2,217 passed; 108 new).
- `uv run pytest tests/test_research -m ""`: 108 passed. No `slow` test lands in P1.
- `uv run ruff check src/ tests/`: 118 findings, the baseline; none in a new file.
- `uv run mypy src/`: 88 errors in 18 files, the baseline; none in a new file.
- Manual: `uv run python -m agentic_mbse extract --help` prints the `extract` usage. `test_main_module.py` now checks this too.

**What changed.**

- Golden data in `tests/test_research/golden/`, derived once by `.orchestrate-logs/golden/derive.py` (gitignored, kept as provenance) with the clock fixed at 2026-10-12T09:30:00Z. The script stubs `pyzotero` in `sys.modules`; nothing was installed. It derives more than the plan listed, so later phases read frozen data instead of recomputing:
  - `index/`: the seam block (url and local_pdf), the batch block, both inserted at `## How Sources Are Used`, plus the three design-derived cases (other anchor, end of file with and without a final newline). `anchor_how_this_file.before.md` is the shipped template frozen as of today, so P6's template edit cannot move it.
  - `manifest/{url,local_pdf,keyed}.jsonl`: the snapshot's rows as the bytes it appends, not just key order. Inputs in `manifest/inputs.json`.
  - `receipts/`: two receipts in one run (a registration, then a pre-capture hold-out refusal), with the snapshot's file names and bytes.
  - `seam.json` (request and key) and `seam/`: a bounded-negative run (`run.json`, `run.jsonl`, `process_log.md`, `return.json`, and the negative) and a registered run's `return.json`. Paths in them are relative, from a `knowledge/research/requests` home.
- `src/agentic_mbse/__main__.py`: runs `agentic_mbse.cli.main`.
- `src/agentic_mbse/research/`:
  - `paths.py`: `RegistryPaths(knowledge_dir)` derives the eight paths and `project_root`; `default_paths()`, `registry_lock`, and `sweep_stale_staging(paths, older_than_s=…)`. The age is the caller's: register passes `4 * CAPTURE_TIMEOUT_S` in P2.
  - `manifest.py`: `load_manifest_rows`, `first_matching_row`, `append_manifest_row`, `mark_manifest` / `roll_back_manifest` (a mark of `None` length means "no manifest", and rollback removes the file), `write_manifest_without`.
  - `sources.py`: the three source kinds, `SourceMetadata`, `slugify`, `normalize_url`. `index_profile` is `"seam"` or `"batch"`.
  - `runs.py`: the run-directory names, `Receipt` (TypedDict), `write_receipt(run_dir, *, …, at)` building the dict in the snapshot's order, `read_receipts`, `is_run_dir`, `read_run_meta`, `run_limits`, `append_run_log`, `read_run_log`.
  - `index.py`: `parse_index(text, project_root=…)` → `IndexBlock(start, end, text, title, type, location, slug)`; `normalize_location`; `blocks_titled`; `with_block_inserted` (pure) and `insert_block` (file); `without_block`; `with_block_replaced`; `render_seam_block`; `render_batch_block`.
  - `__init__.py`: the seven D2 names that exist so far.
- Tests in `tests/test_research/`: `conftest.py`, `fixtures/web/` (the marker token is now `sealed-widget-07`), `test_golden_shapes.py`, `test_index_writer.py`, `test_zotero_path_contract.py` (first half), `test_manifest.py`, `test_sources.py`, `test_main_module.py`, `test_no_consumer_names.py`, and `test_runs.py`. The last is not in the plan; it covers the run-log and receipt functions, which have no other caller until P2 and P5.
- The key tests were mutation-checked: dropping one newline from the insertion fails the three anchor goldens; removing the comment boundary fails the A4 case; unmasking comments fails five parser tests; a test writing `knowledge/.registry.lock` at the repo root fails the session check.

**Deviations and decisions** (snapshot vs. this code; none changes a byte fusion-tea writes or reads).

- The clock is an argument. `write_receipt` takes `at: datetime`, and both renderers take `added: date`, so the goldens pin file names and bytes. The callers (P2) pass `datetime.now(timezone.utc)` and `date.today()`.
- `render_seam_block(source_kind, origin)` replaces the snapshot's two optional origin fields: the label follows the kind (`url` → Source URL, `local_pdf` → Origin Path). Its Raw SHA256 line is written from `source_id`, which equals the raw digest in every snapshot call. "Requires source_url or origin_path" became "requires an origin".
- The batch block always has a key line. The snapshot's keyless batch block had no caller left (local PDFs use the seam profile), so `test_local_pdf_block_omits_zotero_key` was not moved.
- A Location's slug is its first path segment under `knowledge/sources/`, with or without a trailing `/`. The snapshot's regex required the slash. Every Location the registry writes has it, so fusion-tea's index parses the same (O1 checks this); a hand-written `knowledge/sources/x` is now seen by `verify` and `retire`.
- The anchor rule keeps the snapshot's prefix match (a line starting with either heading) and skips comments. An anchor on the file's first line now counts; the snapshot needed a newline before it.
- The end-of-file fallback adds no leading newline to an empty file. The design says to add one "if the file does not end with one"; an empty file has no last line to separate from. No golden case covers an empty index, and P2 refuses a missing one.
- `KeyedFileSource` also refuses a blank `kind` or `key_field`, besides the design's three refusals. Same caller error, same `ValueError`.
- The staging sweep counts an entry it cannot stat as fresh on any `OSError`, as the snapshot does. P1 had narrowed this to `FileNotFoundError`, an unlisted behaviour change that let a permission error crash a registration; the orchestrator had it restored in P2, with a regression test.
- Not handled: a `<!--` inside inline code opens a comment for the parser. No shipped or fusion-tea index has one.

**For the next phases.**

- P2: keep each commit rung a module-level name in `register.py`. Importing `append_manifest_row` and `insert_block` into `register.py` makes them patchable there. Use `mark_manifest`/`roll_back_manifest` for the fresh-target rollback. The golden manifest rows carry `date_extracted` 2026-10-12, so the row builder should take the date as `render_*` does, or the test compares key order only. `capture.py` has no `capture_target` on sources: use `source.url` for a `UrlSource` and `staged_input` otherwise. Add the "nothing written" helper to `conftest.py` (accepts an absent or empty manifest and staging). `generated_pdf` is drawn with pymupdf and not yet exercised by capture.
- P3: `knowledge_tree.root.parent` is `tmp_path / "project"`, its own directory, so a test's `pyproject.toml` there never meets run directories in `tmp_path`.
- P4: `IndexBlock.location` is already normalized and `slug` set. Entry labels, `add_entry`, `remove_entry`, `list_entries` and a baseline-writing tree fixture are still to come. Guards: `FakeGuard`, `RecordingGuard`, `NO_GUARD` and `SEALED_TOKEN` are in `conftest.py`; import them with `from tests.test_research.conftest import …`, as `tests/test_sysml` does.
- P5: the seam goldens are under `golden/seam*`. `runs.py` has no `SeamError`: `seam.py` checks `is_run_dir` and raises its own error.

---

## Phase 2: Capture and the register ladder, with a no-op guard

### Goal

Move the ladder, capture, commit and rollback (the code that writes four files or nothing) under the P1 pins.

### Assumption under test

The ladder splits across `capture.py` and `register.py` with order, messages, receipts and rollback unchanged. The two new refusals (missing index, missing web extra) land before any capture is spent.

### Test stencil (write first)

```python
# tests/test_research/test_rollback.py (moved; rung names point into register.py)
def test_a_failed_commit_on_a_fresh_target_leaves_no_manifest(knowledge_tree, local_site, monkeypatch):
    assert not knowledge_tree.manifest.exists()              # a fresh target has none
    before = knowledge_tree.index.read_bytes()
    monkeypatch.setattr(register_module, RUNGS["after_manifest_append"], boom)
    with pytest.raises(RegistrationError):
        register(UrlSource(url=local_site.url("utf8.html")), METADATA, paths=knowledge_tree.paths)
    assert not knowledge_tree.manifest.exists()
    assert knowledge_tree.index.read_bytes() == before
```

### Changes

**Tests first, by Appendix B row.**

- [x] `test_golden_shapes.py`: manifest-row key order for `url`, `local_pdf` and keyed rows, against the P1 golden data.
- [x] Move `test_register_url_chain.py`, `test_register_pdf_chain.py`, `test_duplicate.py`, `test_staging_concurrency.py` and `test_rollback.py`. Update imports and rung names; `zotero_key` absence assertions read "no key field". `test_rollback.py` gains the no-manifest case (I3).
- [x] Move `test_receipts.py`. The pre-capture refusal passes `guard=FakeGuard(...)` and uses its term. Add I2: every returned outcome writes exactly one receipt; a raised `RegistrationError` or `subprocess.TimeoutExpired` writes none (review M5).
- [x] `test_zotero_path_contract.py`, second half: keyed dedupe with a neutral key. Old rows carrying the key field and no `source_kind` match before any fetch (I5).
- [x] New cases in the chain files: a URL `register` without the web extra refuses `precondition_failed`, reason starting `URL capture needs the web extra:`, no capture spent (D14). A missing `SOURCE_INDEX.md` refuses `precondition_failed`, reason starting `source index missing:`, before capture (Behaviour Changes).
- [x] `test_capture.py` (new): with `subprocess.run` patched to record argv, the extractor command starts `[sys.executable, "-m", "agentic_mbse", "extract"]` and never carries `--index` or `--summarize` (D13, I7).

**Code.**

- [x] `research/holdout.py`, minimal: the two protocols (design § Exact wording) and the no-op guard. In P2, `register(..., guard=None)` uses the no-op guard; P3 replaces that default.
- [x] `research/capture.py`: per Component Overview. Import `check_web_deps` lazily (Implementation Notes "Hook loading").
- [x] `research/register.py`: the ladder in the design's order (Architecture § register ladder); each rung a module-level function (Implementation Notes "Rollback tests"); `_spent_a_capture` ported exactly (Implementation Notes "Copy, then split").
- [x] `research/__init__.py`: add the register-side D2 names.

**Satisfies:** D6, D13, D14; I1 (row key orders), I2, I3, I5, I7; criterion 3 for `registered`, `duplicate`, `capture_failed`, `precondition_failed` and `limit_reached`.

### Validation

- [x] Exit check. The URL-chain tests need the `web` extra (`uv sync --all-extras`). They must run, not skip.

**What we know works after P2:** a URL or a local PDF registers end to end through the real extractor; refusals write nothing; a failed commit leaves the four artifacts byte-identical, or absent if they were absent; receipts match the snapshot's.

### Implementation Notes

#### Phase 2 Completion

**Completed:** 2026-10-12.

**Exit check.**

- `uv run pytest tests/`: 2,383 passed, 1 skipped, 1 xfailed, 13 deselected, 0 failed (P1 2,325 passed; 58 new). Deselected rose from 5 to 13 by the eight `slow` tests in `tests/test_research`.
- `uv run pytest tests/test_research -m ""`: 174 passed, the eight `slow` tests included. The URL-chain tests ran under the `web` extra; none skipped.
- `uv run ruff check src/ tests/`: 118 findings, the baseline; none in a file this item adds or edits.
- `uv run mypy src/`: 88 errors in 18 files, the baseline; none in a research file.

**What changed.**

- `research/holdout.py`, minimal: the `HoldoutMatch` and `HoldoutGuard` protocols (design § Exact wording) and `NO_HOLDOUT_GUARD`. `register(..., guard=None)` uses `NO_HOLDOUT_GUARD` until P3.
- `research/capture.py`: `capture(source, staging, *, budget) -> Captured | CaptureFailure`, `extractor_command` (`[sys.executable, "-m", "agentic_mbse", "extract", target, "--save-source", "--output", staging, "--budget", budget]`), `web_capture_available()` (imports `check_web_deps` lazily), `sha256_of`, and the snapshot's flattening and raw-artifact read-off. `CAPTURE_TIMEOUT_S`, `EXTRACT_OUTPUT` and `STAGED_INPUT_DIR` live here. A `CaptureFailure` carries the reason; `register` turns it into `capture_failed`, so `capture.py` never imports `register.py`.
- `research/register.py`: `register`, `RegistrationResult` (with an `Outcome` literal), `RegistrationError`, `manifest_row` (public, so the golden test builds rows with it), `DEFAULT_BUDGET`, `STALE_STAGING_AGE_S` and a `Triage` literal. The ladder is the design's order: sweep, metadata, input file, index exists, hold-out on input path, identity and title, pre-fetch dedupe, `max_captures`, web extra for URLs, capture, hold-out on extract and raw artifact, dedupe on `source_id`, commit. `_spent_a_capture` is the snapshot's, unchanged.
- The commit rungs are module-level names in `register.py`: `_rename_into_sources`, then `append_manifest_row` and `insert_block`, imported there from `manifest.py` and `index.py`. The snapshot's one-line wrappers around those two were not ported. The rollback uses `mark_manifest`/`roll_back_manifest`, so a fresh target's manifest is removed, not truncated.
- The two new refusals: `source index missing: <index path>` and `URL capture needs the web extra: install agentic-mbse[web]`, both `precondition_failed`, both before any capture. Tests simulate a missing extra with `sys.modules["trafilatura"] = None`, which makes the real `check_web_deps` fail.
- `research/__init__.py`: adds `register`, `RegistrationResult`, `RegistrationError` (ten D2 names).
- `research/sources.py`: `UrlSource.kind` and `LocalPdfSource.kind` are typed `Literal["url"]` and `Literal["local_pdf"]`, so `register` passes the kind to `render_seam_block` without a cast.
- `research/paths.py`: the orchestrator's correction. `_modified_at` catches `OSError` again, as the snapshot does; Phase 1's note is amended.
- Tests: `test_register_url_chain.py`, `test_register_pdf_chain.py`, `test_duplicate.py`, `test_staging_concurrency.py`, `test_rollback.py` and `test_receipts.py` moved; `test_zotero_path_contract.py` gained its second half; `test_capture.py` is new; `test_golden_shapes.py` gained the manifest rows. `conftest.py` gained `registry_state` (index and manifest bytes, or None when absent, plus source and raw entries) and `assert_nothing_written` (a fresh tree: no source, raw copy or staging entry, an absent or empty manifest, and the index still the live template byte for byte). "Zotero key absent" assertions became "the row's fields equal the golden row's fields, in order".
- Tests beyond the plan's list: the `OSError` sweep regression (mutation-checked: it fails with `FileNotFoundError`); the capture-count quirk pinned on its own; every-outcome-one-receipt over all six outcomes in one run; triage recorded; a slow local-PDF rollback that the raw copy is removed; a slow keyed registration end to end (batch block, key line, key as slug suffix, row fields); a batch caller needs only a title; the block lands before the shipped template's anchor.
- Manifest goldens compare the appended bytes, not only key order, because `manifest_row` takes its date as an argument.

**Deviations and decisions** (none changes a byte fusion-tea writes or reads).

- `test_same_bytes_at_a_different_url_is_a_duplicate` never reached the check it names in the snapshot. Its alias `./utf8.html` normalizes to the first URL (`posixpath.normpath`), so the pre-fetch URL check caught it. The alias is now `utf8.html?alias=1`: normalization keeps the query and the fixture server ignores it, so the source-id dedupe after capture is what refuses it, and the test asserts that reason.
- `_commit` reads `date.today()` once and hands it to the row and the block. The snapshot read it in each writer, so a commit straddling midnight could carry two dates.
- Ported tests that checked "the reason mentions the field" now check the exact snapshot message.
- Two snapshot comments were wrong and are not ported as written. The `_spent_a_capture` comment said only a post-capture duplicate or hold-out hit carries a source id. In fact a pre-fetch duplicate of a row with a `source_id` carries one (the quirk the design keeps), and a post-capture hold-out hit carries none, so it does not count against `max_captures`. The code is unchanged; the new comment says what it does.

**For the next phases.**

- P3: every guard call is in `_input_identity_holdout_hit` and `_post_capture_refusal`, and every read of a match is in `_holdout_refusal`; the wrapper goes around those. A2's post-capture fault must carry `captured.source_id`, and `_spent_a_capture` must then count a `precondition_failed` with a source id; leave the post-capture hold-out hit uncounted, as the snapshot does. Replace `NO_HOLDOUT_GUARD` as the default with `load_holdout_guard(paths.project_root)`. `FakeGuard(terms=(SEALED_TOKEN,))` already drives the receipts test.
- P4: in test modules, get the `register` module with `importlib.import_module("agentic_mbse.research.register")`. The package attribute `register` is the function (D1's module name and D2's function name collide), so `from agentic_mbse.research import register as module` returns the function. `retire` is not a D2 name, so `agentic_mbse.research.retire` stays the module. `assert_nothing_written` compares against the live template, so it suits fresh trees only; round trips use `registry_state`.
- P5: the CLI's `register` prints the snapshot's fields (`source_registry.py:1336-1346`); `RegistrationResult` keeps the snapshot's field names. `DEFAULT_BUDGET` and `Triage` are in `register.py` for the flags.

---

## Phase 3: The hold-out hook

### Goal

Load the target's guard from `pyproject.toml`, and fail closed on every fault, including an unknown config key.

### Assumption under test

Bet B2 (three checks express a target's hold-out rule) and D3–D5: a guard named by file path loads like fusion-tea's module, and no load or call fault lets a registration through.

### Test stencil (write first)

```python
# tests/test_research/test_hook_config.py
@pytest.mark.parametrize("line", ['holdout_guard = "guard.py"', 'holdout-guard = ""', "holdout-guard = 3", 'holdout-guard = "missing.py"'])
def test_a_misconfigured_guard_refuses_with_a_receipt(line, knowledge_tree, generated_pdf, run_dir):
    (knowledge_tree.root.parent / "pyproject.toml").write_text(f"[tool.agentic-mbse.research]\n{line}\n")
    result = register(LocalPdfSource(path=generated_pdf), METADATA, paths=knowledge_tree.paths, run_dir=run_dir)
    assert result.outcome == "precondition_failed"
    assert result.reason.startswith("hold-out guard unavailable:")
    assert len(read_receipts(run_dir)) == 1
```

### Changes

**Tests first, by Appendix B row.**

- [ ] `test_holdout.py`, agentic-mbse half: move the fake-guard cases (content, URL, title, input path, no waiver flag). Add: no config registers; a missing file, a missing function, a raising guard and an unknown config key each refuse `precondition_failed` with a receipt; a post-capture fault carries the captured `source_id` and counts as captured (review A2).
- [ ] `test_hook_config.py` (new): an absent or empty table gives the no-op guard; every D4 fault gives the failing guard; config is read from `<knowledge dir>/../pyproject.toml`, so a test tree never loads the cwd's guard (D5); a guard using dataclasses with postponed annotations loads, and a failed load leaves no private module in `sys.modules` (review A3); a guard importing a sibling module fails closed.
- [ ] Public API: `agentic_mbse.research.__all__` equals the thirteen D2 names exactly.

**Code.**

- [ ] `research/holdout.py`, complete per Component Overview and Architecture § The hook: `load_holdout_guard`, the failing guard, and one wrapper around every guard call and every read of a returned match.
- [ ] `research/register.py`: `guard=None` now means `load_holdout_guard(paths.project_root)`. Every guard call goes through the wrapper.
- [ ] `research/__init__.py`: add `HoldoutGuard`, `HoldoutMatch`, `load_holdout_guard`. D2 is complete.

**Satisfies:** D2, D3, D4, D5; I4 (register half); criterion 3 for `holdout_hit` through a test-supplied hook.

### Validation

- [ ] Exit check.

**What we know works after P3:** a target with no guard registers freely. A target whose guard is broken, incomplete, raising or misspelled refuses every registration, with a receipt and a reason that names the guard.

### Implementation Notes

_To fill during implementation._

---

## Phase 4: Hand-curated entries, `sources`, `retire`, `verify`

### Goal

Finish the registry: guarded hand-curated writes for `/manage-sources`, removal, and drift reporting that sees an index block with no row.

### Assumption under test

The comment-aware parser and Location normalization read a real index as the old parser did (bet B1; O1 checks it right after this phase). A `register` then `retire` leaves the index and manifest byte-identical at each anchor and at the fallback.

### Test stencil (write first)

```python
# tests/test_research/test_golden_shapes.py
@pytest.mark.parametrize("case", ["anchor_how_sources", "anchor_how_this_file", "eof_newline"])
def test_register_then_retire_restores_the_registry(case, tree_with_one_registration, local_site):
    tree = tree_with_one_registration(case)                   # manifest exists before the round trip
    before = (tree.index.read_bytes(), tree.manifest.read_bytes())
    result = register(UrlSource(url=local_site.url("latin1.html")), METADATA, paths=tree.paths, guard=NO_GUARD)
    retire(result.slug, "round trip", paths=tree.paths, guard=NO_GUARD)
    assert (tree.index.read_bytes(), tree.manifest.read_bytes()) == before
```

### Changes

**Tests first, by Appendix B row.**

- [ ] `test_golden_shapes.py`: the bytes a hand-curated `add-entry` writes; register-then-retire round trips at each anchor and at the fallback (I1). Start each round trip from a tree with one earlier registration so the manifest exists before it. On a fresh tree the manifest ends empty rather than absent, which the "nothing written" helper accepts (design Implementation Notes "Test fixtures").
- [ ] `test_retire.py`: move with the fake guard barring a path and a term. A recording fake guard asserts the calls `check_input_path(Path(slug))`, then `check_input_path(Path("knowledge/sources") / slug)` with that literal path, then `scan_terms(slug)` (Implementation Notes "`retire`'s guard calls"). Add: a guard fault refuses `retire` (I4). The two CLI tests (`test_cli_prints_the_removal_and_the_retired_line`, `test_cli_refusal_exits_nonzero_with_the_reason`) wait for P5.
- [ ] `test_verify.py`: move. Add `block_without_row` (`legacy` when its directory is in `orphan_source_dirs`, `fault` otherwise; D12), hand-curated entries not reported, commented blocks ignored, and `format_finding` reproducing the snapshot's line (`source_registry.py:1304`).
- [ ] `test_entries.py` (new; Appendix B "New in agentic-mbse"): `sources` labels; `add-entry`, `--replace` and `remove-entry` refusals for a duplicate, a missing and an ambiguous title and for a normalized `./knowledge/sources/…` Location; guard hits and guard faults (review M1); removing a hand-placed entry above the template's commented examples leaves the examples and the placeholder line byte for byte (review A4). Refusals write nothing (I2).

**Code.**

- [ ] `research/index.py`: `add_entry` (guarded per D11), `remove_entry` and `list_entries`, each a read-modify-write under `registry_lock`.
- [ ] `research/retire.py`: per Component Overview; rungs module-level; guard calls as pinned above, under the lock and before the slug pattern check.
- [ ] `research/verify.py`: per Component Overview and D12; keep `row_without_block`'s raw-text substring check (Implementation Notes). Keep `VerifyReport.has_faults`, and add `format_finding(finding) -> str` here, so the P5 CLI and the orchestrator's O1 call print the same bytes.

**Satisfies:** D10, D11, D12; I1 (entry bytes, round trips), I2 (retire and entry refusals), I3 (retire half), I4 (retire and add-entry); criterion 3 for `retire` and `verify`.

### Validation

- [ ] Exit check.

**What we know works after P4:** every registry write in the package holds the lock and passes the guard, and `verify` reports the missing direction (an index block with no row), classed against the baseline.

### Implementation Notes

_To fill during implementation._

---

## Orchestrator: O1 parity, early (after P4 commits, before P5 starts)

The CLI lands in P5, so this run calls `verify.py` through Python. It runs now so that a parser mismatch (B1) surfaces before the CLI and the skills are built on the parser. The command differs from Appendix D O1 step 3 only in how `verify` is invoked; the pass rule is the same.

- [ ] In the fusion-tea worktree `/home/reid/1cfe/fusion-tea-research-seam` (branch `research-seam-port`), install this branch editable into the worktree's own environment, never into the main checkout's: `uv pip install --reinstall --no-deps -e /home/reid/1cfe/agentic-mbse-research-seam`. Run everything with `uv run --no-sync`.
- [ ] O1 step 2: add the hook table (design § Exact wording) to the worktree's `pyproject.toml` (review M4).
- [ ] O1 step 3, Python form, from the worktree root:

  ```bash
  uv run --no-sync python scripts/source_registry.py verify > old.txt; echo $?
  uv run --no-sync python -c "import sys; from agentic_mbse.research import default_paths; from agentic_mbse.research.verify import verify, format_finding; r = verify(default_paths()); print('\n'.join(format_finding(f) for f in r.findings)); sys.exit(1 if r.has_faults else 0)" > new.txt; echo $?
  ```

- [ ] Pass (Appendix D O1 step 3): every finding line of `old.txt` is in `new.txt`; the only extra lines are two `legacy block_without_row` lines, for `knowledge/sources/iter_cryoplant_iter_org` and `knowledge/sources/eu_demo_rw_tf_coil_conductor_dematte_bruzzone`; both commands exit 0. Record both outputs and exit codes in `evidence/o1-parity.md`.
- [ ] On a mismatch, B1 is false. Stop before P5 and take the differing lines to the owner; the design names the remedy as a migration or a compatibility rule. Do not adjust the pass rule to fit.

---

## Phase 5: Seam bookkeeping, the CLI, and `init`

### Goal

Port `open | log | close`, put all nine subcommands behind one thin CLI, and make `init` prepare a target for them.

### Assumption under test

The request key and class precedence survive the move unchanged; a changed key would silently reopen fusion-tea's recorded negative. The project-root rule (D15) holds for every subcommand.

### Test stencil (write first)

```python
# tests/test_research/test_golden_shapes.py
def test_request_key_matches_the_snapshot():
    golden = json.loads((GOLDEN / "seam.json").read_text())
    assert request_key(golden["request"]) == golden["request_key"]

# tests/test_research/test_research_cli.py
def test_outside_a_project_root_refuses_in_one_line(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)                               # no knowledge/ here
    assert main(["research", "verify"]) != 0
    assert len(capsys.readouterr().err.strip().splitlines()) == 1
```

### Changes

**Tests first, by Appendix B row.**

- [ ] `test_golden_shapes.py`: request key; return and negative key order. I1 is complete.
- [ ] Move `test_negative.py`, `test_return_contract.py` and `test_triage_queue.py`. Update imports; the triage CLI tests go through `agentic-mbse research log`.
- [ ] `test_research_cli.py` (new): the root check (D15); exit codes for each subcommand, including `open` on a malformed request (2) and on a request a negative answers (3); one-line errors for `RegistrationError`, `RetirementError`, a capture timeout and `SeamError` (Behaviour Changes); `register` prints the snapshot's JSON fields (`source_registry.py:1336-1346`); `verify` prints through `format_finding`; `add-entry`/`remove-entry` output and exit codes and the `sources` line (Architecture § CLI surface). The two CLI tests deferred from `test_retire.py` land here.
- [ ] `tests/test_cli.py`: `TestDirectoryStructure` (`:861`) adds `knowledge/research/requests/runs` and `knowledge/research/requests/negatives`. New init tests: a fresh `.gitignore` has both ignore lines under the header; re-init appends missing lines to an existing `.gitignore`, once; a symlinked `.gitignore` is left alone with a message (Implementation Notes "Init"; criterion 1).

**Code.**

- [ ] `research/seam.py`: per Component Overview. Reads receipts and the run log only through `runs.py`; never imports the registry modules (Architecture, first bullet).
- [ ] `cli/research_cli.py`: `register_research_subcommands`; the scripts' flags; the root check; output and exit codes (Architecture § CLI surface).
- [ ] `cli/__init__.py`: wire `register_research_subcommands` beside `register_pm_subcommands` (`:798-800`); the two directories in the list near `:500`; the ignore lines in the fresh `.gitignore` (`:392-457`) and an append helper modelled on `_update_gitignore_for_dev_mode` (`:278-291`), reported under Updated; the `cmd_init` docstring.

**Satisfies:** D15; I1 (complete), I7 (class from receipts and run log only); criterion 1 (directories and ignore lines); criterion 3 (four classes).

### Validation

- [ ] Exit check.
- [ ] Manual: `uv run agentic-mbse research --help` lists `open`, `log`, `close`, `register`, `retire`, `verify`, `sources`, `add-entry`, `remove-entry`.
- [ ] Manual: from the worktree root, `uv run agentic-mbse research verify` exits 0 and `uv run agentic-mbse research sources` lists no commented example as an entry. Both are read-only; `git status` shows no change under `knowledge/`.

**What we know works after P5:** a target initialised from this branch has the request directories and the ignore lines, and every seam and registry action is one CLI call with a one-line error and a stable exit code.

### Implementation Notes

_To fill during implementation._

---

## Phase 6: Skills, docs, templates, contract tests

### Goal

Ship the procedure and make every shipped instruction point at the CLI: the new `research-acquire` skill and guide, `/manage-sources` rewritten, the `run-goal` relabel and the class-to-outcome table.

### Assumption under test

Bet B4: after this phase no shipped skill tells anyone to edit the registry files by hand. Criterion 5: no consumer name in the shipped skill, guide or package.

### Test stencil (write first)

```python
# tests/test_research/test_shipped_contracts.py
def test_run_goal_names_the_installed_seam():
    text = (REPO_ROOT / "skills/run-goal/SKILL.md").read_text()
    assert "research-acquire" in text and "agentic-mbse research" in text
    assert "Use the research procedure the project's instructions name" not in text

def test_the_runbook_maps_every_seam_class():
    runbook = (REPO_ROOT / "project_templates/GOAL_RUNBOOK.md.template").read_text()
    for row in ("| `REGISTERED` | `COMPLETE` |", "| `OPERATOR_QUEUE` | `OWNER_GATE` |", "| `BLOCKER` | `PREREQUISITE` |", "| `BOUNDED_NEGATIVE` | `BOUNDED_NEGATIVE` |"):
        assert row in runbook
```

### Changes

**Tests first, by Appendix B row.**

- [ ] `test_command_contract.py`: move, rewritten for `skills/research-acquire/SKILL.md` and `docs/research-seam.md`. The skill calls `agentic-mbse research open | log | register | close` and never names a registry file as something to edit. The guide covers the four classes, the three operator actions and the blind spot. The upstream-filings test becomes "the guide names the capture gaps". The skill's outcome table carries the seam-repair line (review A1). The `.gitignore` negation test is dropped.
- [ ] `test_shipped_contracts.py` (new): `manage-sources` calls `research sources`, `register`, `add-entry`, `remove-entry` and `retire` and states its never-edit rule; `run-goal` and the runbook as in the stencil (criterion 8).
- [ ] `test_no_consumer_names.py`: extend I8 to `skills/research-acquire/` and `docs/research-seam.md`.
- [ ] `install-commands --list` names `research-acquire`, and a fresh `init` installs it (criterion 1). Put these beside the existing install tests in `tests/test_cli.py` or `tests/test_installation.py`.

**Text.** Use the design's exact wording where it gives one.

- [ ] `skills/research-acquire/SKILL.md` (new): from the snapshot's `research-acquire.md`, per the last paragraph of Component Overview.
- [ ] `docs/research-seam.md` (new): operator guide, hook guide and § Decisions (D17). The hook guide says a guard must import on its own and that its relative paths resolve against the project root (Implementation Notes "Hook loading"). Keep the Nb3Sn request and the EPFL preprint, labelled as examples. The BLOCKER example names a fault logged after `open` (Align). Drop the closed `PM-APPROVE-RESEARCH-EMPTY-INSIGHTS` bullet (A15). Say that re-registering a retired title reuses its slug and `verify` reports it (Non-Goals).
- [ ] `skills/manage-sources/SKILL.md`: rewrite to the shape in Component Overview.
- [ ] `skills/run-goal/SKILL.md:66,68` and `project_templates/GOAL_RUNBOOK.md.template:289`: the exact texts (D16).
- [ ] `docs/source-index.md` (§ Source Types exact text; File Format; Command Behavior steps 1 and 4) and `skills/source-traceability/SKILL.md:55-76`, which mirrors it.
- [ ] `SOURCE_INDEX.md.template` at the repo root: the type comment, the placeholder line as a comment, and "Adding New Sources" (Appendix A).
- [ ] `skills/onboard/SKILL.md:59,63` and `skills/toolkit-awareness/SKILL.md` (Integration Strategy).
- [ ] `.project/active/wrap-split-migration-ledger.md`: the Item 5 section with the Appendix C rows.

**Satisfies:** D16, D17; I6, I8; criteria 1 (skill installed and listed), 5 and 8; the text half of criterion 7.

### Validation

- [ ] Exit check.
- [ ] `uv run pytest tests/test_goal_layer.py` passes. Its `SC2` pattern (`tests/test_goal_layer.py:33-37`) scans `run-goal` and the runbook, so the new text must not name `holdout`, `research_seam` or `source_registry`.
- [ ] `tests/test_research` passes after the template edit. The placeholder line becoming a comment changes where D10 ends a block, and the behaviour tests use the live template.
- [ ] Manual: `grep -riE "fusion-tea|MR-[0-9]|\baries\b|zotero|\.project/" skills/research-acquire docs/research-seam.md src/agentic_mbse/research` prints nothing (criterion 5's own evidence).
- [ ] Manual: `grep -rn "SOURCE_INDEX.md\|MANIFEST.jsonl\|RETIRED.jsonl" skills/` shows no hit that tells anyone to edit the file (I6, B4).

**What we know works after P6:** `init` from this branch installs a target that can acquire and curate sources with shipped files alone. Criteria 1, 3, 5, 8 and 9 are met in this repo.

### Implementation Notes

_To fill during implementation._

---

## After P6: orchestrator steps

### O1, the rest (Appendix D O1, fusion-tea branch)

- [ ] Step 3 again, in the CLI form Appendix D writes (`uv run --no-sync agentic-mbse research verify > new.txt; echo $?`). Its finding lines must equal the early run's.
- [ ] Step 4: the duplicates and the guard, each refusing before any fetch; `git status` shows only the `pyproject.toml` change.
- [ ] Step 5: the rest of Appendix A, with its re-greps, import checks, research and Zotero suites, and the Appendix C homes. Evidence in `evidence/o1-parity.md` (criteria 4 and 6).

### O2, dry runs from a built wheel (Appendix D O2)

- [ ] Build the wheel from this branch (`uv build`) and set up the scratch target as Appendix D says, with the GitLab extra index so `syside==0.8.4` resolves (A17).
- [ ] O2a, criterion 2: request `REQ-001-01`, with the URL pre-check and its named fallback. Evidence in `evidence/o2a-dry-run.md`.
- [ ] O2b, criterion 7: the five `/manage-sources` calls and their CLI checks. Evidence in `evidence/o2b-dry-run.md`.

Then `/_my_audit`, which Align kept because the port runs against live registry data. The run stops before `close` and `pre_pr` (Align).

### O3, post-merge (listed, not scheduled)

Owner-paced, after the owner merges this branch: move fusion-tea's pin and re-init, per Appendix D O3. Not part of this plan's execution.

---

## Spec criteria: where each is met

| Criterion | Met in | Evidence |
|---|---|---|
| 1. Install, list, directories, ignore lines | P5 (directories, ignore lines), P6 (skill listed) | `tests/test_cli.py`, P6 install test |
| 2. End to end in a fresh target | after P6 | O2a |
| 3. Ported tests: four classes, six outcomes, `retire`, `verify` | P2–P5 | `uv run pytest tests/test_research -m ""` |
| 4. Parity on fusion-tea data | after P4 (early), after P6 | O1 steps 3–4 |
| 5. No consumer names | P1 (package), P6 (skill, guide) | `test_no_consumer_names.py` |
| 6. fusion-tea after the port | after P6 | O1 step 5 |
| 7. `/manage-sources` by hand | P4 (functions), P5 (CLI), P6 (skill) | O2b |
| 8. `run-goal` relabel and mapping | P6 | `test_shipped_contracts.py` |
| 9. Suite, ruff, mypy | every phase | exit check |

---

**Next step:** `/_my_implement` P1.
