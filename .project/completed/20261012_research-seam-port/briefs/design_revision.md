# Brief: design revision after review — research-seam-port

Sent by resuming the design session. Review: `design-review.md` (APPROVE WITH CHANGES). This is the only revision round, and there is no second full review. The orchestrator checks each fix against its one-line description.

Edit `design.md` in place. Then fill the review's "Resolutions" section in `design-review.md` with one line per item you act on: the id, what changed, and where. Do not commit. Start no background tasks. End with `ARTIFACT: .project/active/research-seam-port/design.md`.

## Apply: must-fix

Apply M1–M5 as the review states them. For M5, take the first option: a raised `RegistrationError` or `subprocess.TimeoutExpired` writes no receipt and propagates, as today, and I2 covers returned outcomes. This is a port, so don't add a receipt.

## Apply: major advisories

The orchestrator is folding these into the design now, because they sharpen the contract the plan builds on.

- **A1.** Add the class consequence to the Behaviour Changes table. A broken guard, a missing web extra and a missing index return `precondition_failed`, which `close` queues, so they surface as `OPERATOR_QUEUE` → `OWNER_GATE`. Keep `close`'s computation unchanged. Have the skill and guide say that a queued candidate whose reason names the guard, the web extra or the index is a seam repair, not a source the owner must obtain.
- **A4.** Define where a block ends under D10, and add the `test_entries` case the review names.
- **A5.** Make the golden tests byte-level, as the review says: manifest key order, exact insertion bytes for both anchors and for the end-of-file fallback, and a register-then-retire round trip that restores `SOURCE_INDEX.md` byte for byte.
- **A6.** Add the ambiguity and normalization rule for `add-entry`, `--replace` and `remove-entry`.
- **A10.** Move `__main__.py` into P1, and split P1 into support modules plus golden tests, then the register ladder plus chain tests. Renumber the phases.
- **A11, A12, A14 (O1).** Use the orchestrator facts below.
- **A13.** Close the three test-split gaps as the review states them.

## Minor advisories

Apply A2, A3, A7, A8, A9, A15, A16, A17 and A18 where each is a one-line change to the design. Otherwise list them under Next-Stage Handoff for the plan. For A16, the spec now word-bounds the term: criterion 5's grep is `grep -iE "fusion-tea|MR-[0-9]|\baries\b|zotero|\.project/"` (corrected 2026-10-12). I8 and its test use that pattern.

## Orchestrator facts ([AGENT], verified 2026-10-12 in fusion-tea worktree `/home/reid/1cfe/fusion-tea-research-seam`, branch `research-seam-port` cut from fusion-tea `c42ed1d8a`)

- **Snapshot is current.** The seam files are unchanged between `0a833b9f7` and `c42ed1d8a`.
- **O1 step 1 has already run, before any change.** See `evidence/o1-baseline.md`. The old `verify` exits 0 with three `legacy` findings. The index has no `<!--`. Exactly two index blocks point into `knowledge/sources/` with no manifest row: ITER Cryoplant (`iter_cryoplant_iter_org/`) and Demattè & Bruzzone (`eu_demo_rw_tf_coil_conductor_dematte_bruzzone/`). Both directories are in the baseline's `orphan_source_dirs`. The spec's criterion 4 is corrected to name both.
- **A14 resolution.** D12 classes `block_without_row` as `legacy` when the block's Location directory is in the baseline's `orphan_source_dirs`, and as `fault` otherwise. fusion-tea's `verify` therefore still exits 0. State that in D12, and make O1's pass condition two `legacy block_without_row` lines, for those two directories. O1 step 1's comparison: finding lines only, plus the exit code before and after. The old script runs with fusion-tea's interpreter: `uv run --no-sync python scripts/source_registry.py verify` in the worktree, or the main checkout's `.venv/bin/python`.
- **A12, the other two Zotero scripts.**
  - `scripts/zotero_group_download.py` imports only `GROUP_ID, connect, download_pdf, find_pdf_attachment, load_api_key, tag_extracted` from `zotero_lib`.
  - `scripts/test_zotero_write_access.py` imports only `connect, load_api_key, GROUP_ID`.
  - Neither imports a name the design deletes, so the thirteen-name API is enough.
- **A12, callers of the deleted names.** Outside the two scripts and `tests/research/`:
  - `RegistryPaths`, `default_paths`, `load_manifest_rows`, `truncate_manifest` and `append_manifest_entry` have no caller except `zotero_lib.py` itself.
  - `append_source_index_entry`, `SEAM_ANCHOR` and `resolve_slug` occur only in `zotero_ingest.py`.
  - `slugify` and `EXTRACT_OUTPUT` also occur in `exploration/` scripts. No file under `exploration/` imports from `zotero_lib` or `zotero_ingest`, so those are their own definitions.
- **A12, live references to the deleted files.** Instruction files referencing `research_seam.py`, `source_registry.py`, the operator guide or the local command: `CLAUDE.md:11` (rewritten by the design) and the guide itself (deleted). The other hits are historical records, which stay as they are: `modeling_project/VALIDATION_MATRIX.md:63` (SV-037 evidence), `work/active/WI-045_primary-loop-and-cycle/spec.md:99`, and goal-trail evidence and briefs under `work/orchestration/goals/`. No `AGENTS.md` hit. Say in Appendix A that historical records keep their references, because git history holds the deleted scripts.

## Keep

The architecture and D1–D18 stand. Don't widen scope beyond these items, and keep the design about as short as it is.
