# Site account reconciliation (plan Phase 9)

**Status:** final. Phase 9 ran at agentic-mbse `6f66acd6`; Phase 10 re-ran the scan at the final implementation revision `9b123cf3` (§ Final rescan, at the end). The counts below hold at both.

## What was reconciled

- **Scanner:** `scripts/subset_profile/scan_sites.py`, revision `scan_sites/1`. It is the prototype `02-inventory.py` with its recognized forms unchanged, run on `git archive` exports of `src/`. Forms and blind spots: `tests/fixtures/subset_profile/inventory/scanner.toml`.
- **Account:** `tests/fixtures/subset_profile/inventory/site_account.csv`, one row per scanned site.
- **Trees:** sysml-codegen `b5663c07e987a892e27d21e68cec40d0656574ee`; agentic-mbse `6f66acd6944cbd50fcf11794088ef1ccf4cc7374` (`src/` identical to `755d0186`).

## Result

`scan_sites.py --agentic-rev HEAD --reconcile site_account.csv`: **0 unaccounted, 0 orphan, exit 0** (`site-reconcile-phase9.log`).

| Tree | Recorded (prototype) | Now | Difference |
|---|---|---|---|
| sysml-codegen `b5663c07` | 441 | 441 | 0 |
| agentic-mbse | 59 (at `d546a00f`) | 61 | +2 |
| Total | 500 | 502 | +2 |

## Every count difference, by site ID

The hardened scanner was first run at the prototype's own revisions (codegen `b5663c07`, agentic-mbse `d546a00f`). It produced the prototype's 500 site IDs exactly, with the same lines in the same order (`site-scan-prototype-rev.log`; the ID set equals `02-sites.baseline`). So every difference below is a change in the agentic-mbse tree, not in the scanner.

Added (2), both by Item 1:

| Site ID | Cause |
|---|---|
| `agentic_mbse/sysml/reference_use.py::_invocations::shared-evidence::EXPRESSION_DEPTH_EXHAUSTED::1` | Phase 3 added `invocation_uses`, whose walk raises the same depth-exhaustion code as the reference walk. |
| `agentic_mbse/sysml/subset_extraction.py::_conditionals::shared-evidence::EXPRESSION_DEPTH_EXHAUSTED::1` | Phase 4 added the conditional walk in the subset extraction, with the same depth guard. |

Removed: none. Every one of the 59 prototype agentic-mbse sites keeps its ID; line numbers moved in `reference_use.py` (Phase 3's edit), which the IDs do not include.

Item 1's other new modules (`occurrence_extraction.py`, `subset_profile.py`, `fact_refs.py`, `occurrence_facts.py`, `subset_facts.py`, `invocation_allowlist.py`) raise only builtin or local exception classes (`ValueError`, `TypeError`, `RecordError`), or return failures as data. The scanner does not recognize agentic-mbse builtin raises at all (blind spot `unrecognized-exception-class-or-helper`), so they add no sites.

## The account, by disposition and role

| | in scope | handled elsewhere | explicit follow-up | Total |
|---|---|---|---|---|
| sysml-codegen | 19 | 354 | 68 | 441 |
| agentic-mbse | 25 | 22 | 14 | 61 |
| **Total** | **44** | **376** | **82** | **502** |

| Role | Sites | Where they go |
|---|---|---|
| internal_invariant | 155 | all handled elsewhere; each cites its guard (a `file.py:line`, or "no caller under src/" for a test-only accessor) |
| snapshot_integrity | 95 | handled elsewhere (codegen snapshot route, codec, source admission; executable_profile's fact-payload checks) |
| public_capability | 91 | 44 in scope, 37 explicit follow-up, 10 handled elsewhere (codegen output-naming collisions) |
| environment | 58 | handled elsewhere |
| unknown | 45 | all explicit follow-up |
| relay_plumbing | 43 | handled elsewhere (the originating site carries the refusal) |
| malformed_input | 15 | handled elsewhere |

The 44 in-scope sites join 17 matrix rows (`matrix.md` lists each row's sites). One site is the raise site of three rows: `sysml_codegen/elaboration/elaborate.py:1939` (`_collect_bound_members`) records the binding classifier's codes for ES-003, ES-012 and SELF-BINDING; the two unresolved-bound sites in `occurrence.py` serve ES-004 and PUSH-DOWN-HIER-PROFILE-MULTIPLICITY-SHAPE.

Matrix rows with no joined site: `no_raise_site` for ES-010, CALC-USAGE-BARE-RESULT-DROP, G1, G2, L6-LIBRARY-ALIAS-SOURCE and the four advisory PUSH-DOWN rows; `not_located` for ES-011, PUSH-DOWN-EXPR-PROFILE-CHAIN-SEGMENTS, PUSH-DOWN-HIER-PROFILE-UNSUPPORTED-RHS, PUSH-DOWN-AGG-PROFILE-SUM-SHAPE and PUSH-DOWN-AGG-PROFILE-LITERAL-SHAPE, each with its reason in the row.

## How the rows were inspected

- The prototype's `02-classification.csv` (65 code keys) was a seed only. Every site was re-read at its line in the exported trees by one of seven reviewers, split by source file, against the same written rules (`role` and `disposition` vocabularies; no `SI_EVIDENCE_INCOMPLETE` site in scope by code alone; an internal invariant needs a cited guard; unknown before a guess).
- Each row's first evidence pointer is the site itself (`file.py:line` at the scanned revision). In-scope rows add the probe whose observed message matches the site, where one exists.
- Spot check, ten rows across roles, read against the cited code: `occurrence.py:826` (ES-004, ordered), `elaborate.py:2345` (ES-009), `elaborate.py:2074` (follow-up: a quantity-typed referenced feature is refused as `SI_EDGE_DANGLING`), `elaborated_pipeline.py:424` (relay), `occurrence.py:946` (unknown), `elaborate.py:1612` (malformed input), `cli/__init__.py:224` (output-naming collision, handled by codegen), `predicate_compiler.py:326` (follow-up: a predicate leaf that is not a Python identifier), `executable_profile.py:414` (fact-payload check), `envelope.py:239` (environment). All ten agree with the code.

## Judgment calls recorded for the owner

- **Codegen naming collisions** (10 sites: duplicate output paths, module/channel/entry-point/parameter/alias name collisions, predicate name safety) are `public_capability` reachable by valid models, and `handled_elsewhere` with owner sysml-codegen: they are codegen-specific rendering checks, not shared capability rules. Item 2's per-site codes decide whether any of them belongs in the contract.
- **`elaborate.py:2345` (ES-009) and `occurrence.py:180` (ES-002)** are in scope, but each site's condition is wider than its row: any empty owner-address target, and any owner kind outside part usage / part def / package. The row names the probe-observed shape; the wider reach is in each note.
- **ES-005, ES-006 and INDEXED-REFERENCE** are joined at their agentic-mbse raise sites (`reference_use.py:443`, `:514`, `:702`) and codegen's inventory refusal (`expression_evidence.py:210`); codegen's mapping site (`elaborated_pipeline.py:424`) is a relay. `reference_use.py:514` raises for any unresolved reference, not only a conditional's branch; the contract refuses only a positively recognized conditional there.
- **PUSH-DOWN-EXPR-PROFILE-UNSUPPORTED-OPERATOR** joins `extraction/calc_compat_renderer.py:115` and `:120`, which codegen catches and turns into a `MANUAL_REQUIRED` stub (`expression_compiler.py:291`), not a user-facing refusal.
- **37 public-capability follow-ups** are valid-model refusals no matrix row covers. Notable: an `inout` or non-attribute `out` calc parameter (`elaborate.py:1860`, `:1872`); a quantity-typed referenced feature (`elaborate.py:2074`, as `SI_EDGE_DANGLING`); untyped or multiply-typed calc usages (`elaborate.py:1677`); a scalar reference with several targets (`elaborate.py:2350`, `:2483`); `null`/`*` literal bindings (`elaborate.py:2669`); calc def parameters typed outside ScalarValues (`extractor.py:315`, `:329`); a calc def expression reaching outside its def (`expression_compiler.py:221`, as `SI_EDGE_DANGLING`); expressions past the 100-level depth limit (six agentic-mbse sites). They go to the R3 proposal for a destination.

## Final rescan (plan Phase 10)

`scan_sites.py --agentic-rev 9b123cf3 --reconcile site_account.csv` at the final implementation revision `9b123cf323e5dfc2af56ebf9144cec86d1eeac9b`: **0 unaccounted, 0 orphan, exit 0** (`site-reconcile-final.log`; scan output `site-scan-final.csv`). The scan is identical to Phase 9's, site for site and line for line: `src/` did not change between `6f66acd6` and `9b123cf3`. Final counts: **sysml-codegen 441 (recorded 441), agentic-mbse 61 (recorded 59, +2 itemized above), total 502.** The account's header now names the final scan identity.
