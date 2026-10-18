# Audit: Positional-binding hazard and check (EXEC-SUBSET-CONTRACT Item 4)

**Verdict:** Certify
**Audited:** 2026-10-18
**Branch:** `positional-binding-check` (base `ccd57d83`)
**Commit:** `9765c47e` (implementation `4ab5a33b`..`73be541e`; `src/` unchanged since `b2bb99bb`, the revision the tree reproduction ran at)

**How this audit was done.** Static read only. Every `uv run` and Python command needed approval this session and was refused, so I ran no tests, no `validate`, and no SysIDE probes. Each conclusion below comes from reading the code, the tests, the fixtures and the evidence logs. Test results quoted here are the implementer's recorded results, marked as such. The repository checks are the orchestrator's to run.

---

## The Point

In SysML v2, an input on a calculation or constraint usage written without `:>>` or `redefines` (`in b = 3;`) binds to the definition's parameter at the same position, not to the parameter with the same name (KerML 8.3.3.3.4, `checkFeatureParameterRedefinition`). An author who writes correctly named inputs out of order gets a silent swap. The model is valid and nothing warns. For `calc def Sub { in a; in b; return r = a - b; }` with `a = 10, b = 3`, the reversed usage gives -7 in native SysIDE 0.8.4 and 7 through sysml-codegen `b5663c07` with TEAx, so a passing generated run says nothing about native correctness. fusion-tea `f96ad312` has 125 such mismatches whose value effect is unknown; dc3 has none. The knowledge sat in sysml-codegen since July and never reached authors.

Item 4 adds one L2 check under owner decision D1 (`[AGENT] (ratified by owner, 2026-10-15)`): new mismatches block; explicitly pinned legacy mismatches warn until migration; a pin certifies neither native values nor agreement between routes. It also ships the fixtures that prove the check, a hazard register entry and guidance edits. It must not change how either route binds (R4-2), edit fusion-tea (R4-3), or touch sysml-codegen or Item 2 (owner boundary).

## Summary

The check does what the spec asks. The rule reads SysIDE's resolved redefinitions and their implied/explicit mark, never name sets; pins change severity only for an exact (owner, input, target) identity; inspection failures and broken pin lists fail closed. The fusion-tea pin list is built from the prototype's log alone, and the recorded reproduction matches all 125 identities with no difference. I found no blocker. The most important advisory item is a probable gap in the "unresolved reference never reads clean" rule: a calc or constraint usage that subsets (`:>`) an unresolved feature is not checked for a placeholder target. I could not confirm it by running SysIDE.

## Product Judgment

**Yes, this is the right piece of work.** It closes the gap the epic names: authors now get a blocking error for the swap, a register entry explaining it, and guidance that teaches the by-name and definition-order forms. It stays inside its boundaries: no binding change, nothing written in fusion-tea, sysml-codegen or Item 2 (the reproduction checks each sibling's HEAD and status before and after, `evidence/run-trees.md` "Siblings"), and fusion-tea is described as "125 mismatches, value effect unknown", never clean.

The product-lens audit block (appended to `product-lens.md`, Gate: OPEN) found no owner contradiction and no open BLOCK. Earlier design-stage findings F2–F4 are resolved in the code and docs; I checked F2 against `semantic-hazards.md:109`. Its three carried findings are re-checked against the code below (Advisory 2, 3, 4). Its fourth (close must rewrite `.project/active/` citations) is a close step, listed under Certification.

No product-drift smell fired. The one special category, the pinned WARNING, changes only the L2 pass rule, and its user-visible meaning is stated in the message, the L2 header and the register.

## Blockers

None.

## Advisory

Ranked by importance. "Should-fix" items are worth doing before the PR; "minor" items are at the implementer's discretion.

1. **Should-fix: a usage that subsets an unresolved feature probably reads as clean.** `_explicit_targets` (`src/agentic_mbse/sysml/parameter_redefinition_extraction.py:168-178`) checks an owner's explicit `Redefinition`, `FeatureTyping` and `Subclassification` targets for SysIDE's placeholder. It does not check `Subsetting` or `ReferenceSubsetting`, and `Subsetting` is not in the adapter's closed type map. KerML's rule applies to every direct supertype, and a subsetted feature is one, so `calc c :> missing_calc { in b = 3; in a = 10; }` inherits its parameters through that subsetting. If `missing_calc` does not resolve, `c`'s inputs get no implied redefinition, read as `new_parameter`, and nothing fails. L1 does not catch it either, because L1 reads only parser diagnostics. **Impact:** a swapped model with a typo in a subsetting reference passes L2. The register's generic limit ("an unresolved reference of another shape could still read as clean", `docs/patterns/semantic-hazards.md:102`) covers it in words, but this shape is a predictable one. **Change:** add a learning test for an owner with an unresolved `:>` and `subsets` target, then add `Subsetting` (checked after `Redefinition`, which is a subtype) to the owner's placeholder check. **Not verified by execution.**

2. **Should-fix: the run's last line says "All quality checks passed!" when L2 passed only because of pinned warnings.** `runner.py:155-156` prints the green line and `validate` exits 0. The "(N pinned positional warnings; not a value or route-parity check)" note appears only on the L2 header line (`validation/common.py:155-160`). The spec's Pol-4 asks for the note in the L2 summary, so the criterion is met as written. **Impact:** a reader who looks only at the end of the output, or a script that reads only the exit code, gets an unqualified pass, which is close to what D1's third sentence warns against. **Change:** carry the pinned count into the run summary line. (Product-lens audit-F1.)

3. **Should-fix: the `out_before_in` fixture has a stale header and no test.** The header (`tests/fixtures/positional_binding/l1/out_before_in.sysml:5`) still says "Design expectation: `validate` rejects this model at L1", which Phase 1 showed is false. No test references the fixture. The register states its observed result ("level 2 reports it as two positional findings", `semantic-hazards.md:42`), but nothing pins that claim. **Impact:** the register cites a behavior no test protects, and the header misleads the next reader. **Change:** rewrite the header to the observed result (L1 passes; L2 gives `a → O::o`, `b → O::a`), and add a test asserting it, labelled as current behavior pending the owner's Det-6 decision.

4. **Minor: the blocking error prints a ready-to-paste pin entry without saying pins are for legacy mismatches only.** `positional_check.py:242-246` ends every unpinned ERROR with the five fields in TOML form. Design D15 chose this so legacy entries can be copied exactly, and the register says new mismatches are repaired, not pinned. The message itself does not. Since pin integrity rests on review alone (R4-1), copying the fields becomes the shortest path for a new mismatch. **Change:** add "pin only a mismatch that existed at the list's recorded_against revision" to the message. (Product-lens audit-F2.)

5. **Minor: an owner sweep that silently returns nothing gives a clean L2.** By design, zero inspected inputs is not an issue (design "Issues and metrics"), and only the reproduction script treats it as a failure. A SysIDE change that makes the sweeps return nothing would therefore pass every target repo. The register's Limits do not mention it. **Change:** name it in the register's Limits. (Product-lens audit-F3; design-F6.)

6. **Minor: the register's "not flagged" text implies something checks special-parameter positions.** `semantic-hazards.md:97` says subject, actor and stakeholder inputs are not flagged because "their own position is SysIDE's subject-position check". `validate` does not surface that SysIDE diagnostic (it is in `diagnostics.sema`; see the `VALIDATE-SEMA-DIAGNOSTICS` follow-up). **Change:** say that `validate` does not currently report it.

7. **Minor: under `$HOME`, the project root is usually found.** `find_project_root` (`src/agentic_mbse/project_root.py:29`) treats any `.claude/` directory as a marker, and every Claude Code user has `~/.claude/`. So for an unmarked tree under the home directory, discovery looks at `~/positional-pins.toml` instead of reporting "no project root". This is pre-existing marker behavior, and the metric prints the path looked at, so it is visible. Worth one sentence in the register's "Where the list is found".

8. **Minor: small duplication with Item 1.** `_direction` (`parameter_redefinition_extraction.py:149-155`) repeats `subset_extraction._is_bound_input`'s direction parsing, and `_READ_ERRORS` restates the exceptions `safe_location` catches. Both are short and commented. No change needed unless Item 1's reading changes.

## Findings Detail

### Plan completion

All eight phases are ticked with implementation notes, and the deliverables each phase names exist in the tree. No TODO, FIXME or broad `except Exception` was added under `src/`, `tests/` or `scripts/` (grep of the branch diff). No agentic-mbse code or test imports sysml-codegen; only the evidence script `evidence/cross-route/eval_generated.py` does, run from dc3's venv against exported revisions.

Deviations are recorded and justified in the plan notes. The ones that matter for review:
- **"Not judged" pins (Phase 4).** A pin whose owner or input failed inspection is neither stale nor out of scope (`validation/positional_binding.py:235-245`). I checked that this cannot produce a clean pass: a pin is "not judged" only when a matching `L2_CHECK_UNVERIFIABLE` ERROR exists, or the owner sweep failed, which is itself an ERROR. It is documented in the register (`semantic-hazards.md:137`).
- **`check` and `render` moved to `positional_check.py`** to keep the decision module free of SysIDE and the filesystem (I6). Sound.
- **The fact sort key drops the element id** after the implementer found anonymous owners ordered at random. Sound, and pinned by a repeated-load test (per notes).
- **No re-install in this checkout for the codegen conformance run.** Reasoned in the notes; both install modes were run on scratch exports.

### Spec conformance

**Detection**
- Det-1, 17 prototype cases with exact identity sets: met. Fixtures under `tests/fixtures/positional_binding/prototype/` carry `// finding:` headers; `tests/test_validation/test_positional_binding.py:161` asserts set equality per fixture. `evidence/phase3-prototype-comparison.md` compares with `04-detector-fixtures.log`.
- Det-2, naive control fails the 9 marked cases: met (`test_positional_binding.py:226`).
- Det-3, spelling fixtures: met. The rule flags `b` in the mixed spelling because `b`'s own redefinitions are all implied (`positional_binding.py:176-203`); another input's `:>>` cannot exempt it. The reversed deliberate rename has only explicit redefinitions (R1b), so step 3 returns `explicit`.
- Det-4, requirement and case fixtures: met. Special-role inputs are excluded first (`positional_binding.py:180`); an ordinary input landing on a special slot gets `POSITIONAL_SPECIAL_SLOT` (`:194-196`).
- Det-5, dc3 shapes: met (`tests/fixtures/positional_binding/dc3/`, each citing dc3 `60b44d5`).
- Det-6, shapes near the old heuristic: **met with recorded limit.** `inherit_def_extends` must pass (`test_positional_binding.py:184`), `usage_extra_inputs` and `def_adds_first_input` have headers. The `out_before_in` row's design expectation did not hold; the plan surfaced it and left it open for the owner (Advisory 3).
- Det-7, multiple types: met (`prototype/multiple_types.sysml`, `types/multiple_types_with_rename.sysml`; D7's second branch has no observed SysIDE case and is covered by pure tests).
- Det-8, existing fixtures: met. `evidence/existing-fixture-scan.md` reports no positional finding and justifies 11 unverifiable results on partial loads that no test uses.

**Policy (D1)**
- Pol-1: met (`test_positional_binding_policy.py:102-188`). Only `(L2_POSITIONAL_BINDING, WARNING)` is exempt from L2's pass rule (`positional_check.py:71-73`, `level2_structure.py:469`), and `render` emits WARNING only for a pinned finding (`positional_check.py:251`).
- Pol-2: met. A missing, unreadable, non-UTF-8, directory, malformed or headerless list is `PinListInvalid` with its own reason code, and the check runs as if there were no list (`positional_pins.py:158-171`; `positional_check.py:98-99`). Parsing is closed at every level, rejects TOML datetimes, booleans as integers, duplicate identities, absolute paths, `..` and backslashes (`positional_pins.py:174-293`). One gap too small to grade: a whitespace-only `revision` is accepted.
- Pol-3, partial scope: met (`test_positional_binding_policy.py:253-272`; scope by file existence under the pin root, `positional_check.py:113-121`).
- Pol-4: met for the L2 summary and the register (`test_shipped_text.py:147` imports `PINNED_DISCLAIMER`; policy test `:102-111`). See Advisory 2 for the run-level line.
- Pol-5: met per the implementer's recorded run (existing L2 tests and `test_integration_regression.py` pass; no existing expectation changed). A pinned warning beside a `LITERAL_BINDING` warning still fails (`test_positional_binding_policy.py:442`).

**Root-only discovery.** `discover` looks only at `<project root>/positional-pins.toml` (`positional_pins.py:143-155`); tests cover a file below the root and in a parent of the root (`test_positional_pins.py:77, 365`). See Advisory 7.

**Inspection failures**
- Insp-1: met. Seams inject a raising owner sweep, `owned_features` read and `heritage` read; a pin on the affected input changes nothing (`test_positional_binding_policy.py:328-382`).
- Insp-2: met. No shape-based heuristic is carried over; failures come only from raising reads or placeholder targets. The placeholder test covers explicit typing, supertype and redefinition targets only (Advisory 1).
- Insp-3: met. `Positional inputs inspected` is a metric; the reproduction fails a tree with zero (Advisory 5 for the library-level consequence).

**Consumer baselines**
- Base-1, reference from the prototype log: met. `scripts/positional_binding/build_reference.py` reads only `04-detector-tree-fusion-tea.log` (committed before this branch, `0683ee07`), asserts 125 entries, 125 identities and 9 files, and a test rebuilds and byte-compares the committed TOML. The log has 125 finding lines and the TOML 125 pins (counted).
- Base-2, reproduction: met per `evidence/run-trees.md` (27 of 27 checks). The comparison parses identities out of the production check's messages and compares them with the log-built file, itemizing added, missing and changed-target (`run_trees.py:140-150, 247-265`). The run used `b2bb99bb`; `src/` has not changed since. fusion-tea's L2 already fails without the check (340 other warnings), recorded for the owner's R4-3 call.
- Base-3, slow test: met. It skips with the missing variable's name (`test_positional_binding_trees.py:37-39`); the evidence records that it ran.
- Base-4, mutation and stale: met per `run-trees.md` ("Mutation and stale").

**Cross-route**
- XR-1: met (`test_positional_binding_native_values.py`, per the implementer's run: 7, -7, 7, 7; mixed gives no value).
- XR-2: met (`evidence/cross-route/eval_generated.log`: codegen `b5663c07`, TEAx `8d877460`, generated 7 and 7, checkouts unchanged).

**Register and guidance**
- Reg-1: met. I checked the register's KerML claims against the spec text (`docs/sysmlv2/SysML_KerMLSpec/full_document.md:5227-5237`): positions count directed features excluding the result, and the explicit-redefinition exemption applies only to invocation expressions. The register correctly marks SysIDE's behavior (an explicit input gets no implied redefinition) as going further than the text. The actor/stakeholder position claim is backed by learning-findings R2 and `test_r2_an_actor_or_stakeholder_also_counts_toward_positions`. Cross-route divergence is claimed for calc usages only. See Advisory 6 for one misleading phrase.
- Reg-2: met. `plant-idiom.md` qualifies "Order does not matter" by its actual context, D-5 now says to rename the definition's parameter, and the four guidance surfaces link the register. No `@pinned` block or `@authoritative` marker changed. The guidance is accurate: renaming only the usage's input really does leave it bound by position, and the new check would flag it.
- Reg-3: met for fenced examples (`test_positional_examples.py` loads each marked fence, asserts L1 passes, the exact positional findings and no `L2_SELF_NAMED_BINDING` on `expect="none"`). Inline code fragments such as `in :>> radius_in = radius;` are not tested, which the design's fence-marker approach allows.
- Reg-4: met. `evidence/upstream-codegen-finding.md` is marked DRAFT, UNFILED and proposes no binding change.

**Repository checks**
- Repo-1: **met with recorded limit, not verified here.** The criterion says pytest, mypy and ruff "pass"; the evidence shows them equal to the `ccd57d83` baseline (6 environment test failures, 97 mypy errors, 118 ruff errors, all pre-existing; `evidence/repository-checks.md`). I could not run them.

**Non-goals respected.** No action, state or output parameters are scanned; nothing orders subject/actor/stakeholder; no binding change; no fusion-tea pin list or edit.

### Design conformance

The implementation follows the design: fact and extraction split (D1, D2), owner sweeps (D5), placeholder failures (D19), one finding per target (D6), D7, D8, D9, D20, strict TOML (D10), root-only discovery (D11), pin root (D12), scope by file (D13), its own error codes (D14), and the I1 success rule. Every deviation is recorded in the plan notes (see Plan completion). I6 holds: `positional_binding.py` imports only pure types and `pathlib`'s pure paths. I5 holds by construction: findings, stale, out-of-scope and not-judged pins and failures are each sorted by keys with no element id.

The subsetting gap (Advisory 1) is a gap in D19 as designed, not a deviation from it.

### Code integrity

**Detection probes I attempted on paper** (none run):
- Mixed spelling, explicit rename, `redefines` keyword, anonymous input, anonymous owner, subject/actor/stakeholder, multiple types, inheritance through a parameterless subdefinition and through a redefined subpart: the rule handles each as the spec states (above).
- Unresolved owner type, supertype or `:>>`: owner failure (`extraction.py:197-221`); unresolved input `:>> zz`: input failure (`:299-309`). An unresolved supertype on a definition `D` used by a resolved usage `c : D` leaves `c` looking clean, but `D` is itself swept and fails, so L2 still fails.
- Unresolved `:>` subsetting: probably reads clean (Advisory 1).
- An explicit cross-rename (`in b redefines a = 3; in a redefines b = 10;`) is not flagged. That is the spec's rule (an explicit redefinition states the author's chosen target), not a defect.

**Failure honesty.** `_READ_ERRORS` (`extraction.py:82`) includes `TypeError`, `ValueError`, `AttributeError` and `RuntimeError`, so a programming error inside a read becomes an unverifiable ERROR rather than a crash. It still fails L2, so nothing reads clean. `_direction` uses `getattr(..., None)`, so a feature without a `direction` attribute is treated as not an input; that matches SysIDE's meaning of a missing direction. No other silent fallback found.

**Vocabularies.** `Origin`, `ParameterRole`, `Direction`, `RedefinitionFailureCause`, `FindingReason`, `InputOutcome`, `StaleReason` and `PinListDefect` are closed enums; the adapter's type map stays closed.

---

## Certification

**Checked:** the spec, design rev 1, plan and align brief; every new `src/` module and the changes to L2, the runner, `common.py`, the CLI, the adapter and `types.py`; the pin parser and discovery; the reference builder and the reproduction's comparison code; the policy, fixture, pin and example test outlines; the register against the KerML text; the guidance diffs; the reproduction, repository-check and cross-route evidence; the product-lens audit block.

**Marked:** spec success criteria verified above as met (all except Det-6 and Repo-1, which stay unchecked). Plan phases were already ticked by the implementer and I found nothing to untick. The epic heading is not marked, because two spec criteria remain open.

**Close obligations:** rewrite the register's `.project/active/positional-binding-check/...` citations (`semantic-hazards.md:42, 56, 142, 145`) to the archive path, or `tests/test_shipped_text.py`'s path test fails; list the draft upstream finding, D21's observation and the owner items from the plan in `CURRENT_WORK.md`.

**Not checked:**
- I ran nothing: no pytest, mypy, ruff, `validate`, slow tree tests or SysIDE probes. Every test outcome quoted is the implementer's recorded result.
- Advisory 1 is reasoned from the code and the KerML text, not reproduced.
- I did not read every test body; I read test names, the key assertions cited above, and the fixture list.
- I did not re-derive the 125 identities or the outcome counts; I checked that the comparison is independent and read its recorded result.
- I did not read sysml-codegen's conformance test or re-run it; `evidence/codegen-conformance.md` is the implementer's record.
- I did not check whether fusion-tea or dc3 contain any calc or constraint usage that subsets another feature (the read was refused).
