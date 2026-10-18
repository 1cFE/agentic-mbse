# Claim 2: the generator's refusal surface can be enumerated and guarded

**Proposed control:** an inventory guard fails on unclassified additions using the scanner's recognized diagnostic patterns. Additional behavioral tests and review are needed for omissions, unrecognized patterns and public reachability.

**Verdict: feasibility demonstrated for the scanner's recognized patterns; not proof that every publicly reachable refusal has been enumerated.**

- The scanner enumerates 500 candidate sites: 441 in codegen and 59 in agentic-mbse, including constructors and forwarding/plumbing sites. Reachability and distinct public outcomes remain to be established.
- The scanner reports a literal origin for all 34 recognized code-enum member names in this run.
- The planted recognized new-site, new-code and computed-code controls fail the guard.
- Gap 1: it cannot see silent omissions (control D).
- Gap 2: 137 free-text sites and 130 builtin sites carry no stable code. They can be enumerated, but only per site.

## Provenance

- sysml-codegen `b5663c07e987a892e27d21e68cec40d0656574ee`, clean tree, not edited.
- agentic-mbse `d546a00f3b26ff20aa023c8e090d7ca764a09619`; `src/` clean (the dirty files are `.project/` only).
- Run on 2026-10-15T13:52Z. Python 3.12, stdlib `ast` only, so no SysIDE or license is needed.
- Mutations ran on copies in `/tmp/claude-1000/-home-reid-src-agentic-mbse/8cecfa0f-3dca-4be9-bcbc-86b4acc4ae95/scratchpad/c2/{newsite,newcode,dynamic,silent,shifted}`.

## Commands (cwd = this folder)

```bash
CG=/home/reid/src/sysml-codegen/src; AM=/home/reid/src/agentic-mbse/src
python3 -I 02-inventory.py $CG $AM 02-inventory.csv > 02-inventory.log
python3 -I 02-inventory-test.py $CG $AM --write-baseline     # record the prototype site set (not owner-reviewed)
python3 -I 02-inventory-test.py $CG $AM > 02-test-clean.log  # PASS, exit 0
python3 -I 02-inventory-test.py <scratch copy> $AM            # controls, see logs
(cd /home/reid/src/sysml-codegen && uv run --extra dev pytest tests/conformance/test_diagnostic_provenance_sites.py tests/conformance/test_ast_dispatch_invariant.py -q)
```

## Files

| File | What it is |
|---|---|
| `02-inventory.py` | AST enumerator. It derives fixed-code subclasses and code-forwarding factories automatically (fixpoint). It also resolves helper-returned and table-mapped codes. |
| `02-inventory.log`, `02-inventory.csv` | 500 sites, with totals per channel and per code, and the non-literal site list. |
| `02-classification.csv` | Draft classification: 65 keys, each marked shared-rule candidate, codegen-specific, internal invariant or environmental, with an uncertainty flag. |
| `02-sites.baseline`, `02-dynamic-exemptions.csv` | The prototype site baseline and 6 draft exemptions, each with a reason. |
| `02-inventory-test.py` | The guard, rules R1–R4. |
| `02-test-clean.log` | PASS. |
| `02-control-new-site.log` | Control A (existing code, new site) fails with R2. Control B (new enum member) fails with R1 and R2. |
| `02-control-dynamic.log` | Control C (computed code) fails with R3 and R2. |
| `02-control-blindspot.log` | Control D: a silent omission PASSES, which is the blind spot. Control E: shifting lines by 40 PASSES, so the guard doesn't churn on line moves. |
| `02-existing-codegen-guards.log` | codegen's own partial versions of this pattern: 14 passed. |

## Totals (from `02-inventory.log`)

| Channel | Sites |
|---|---|
| coded (literal ElaborationCode/ReadinessCode/SemanticEvidenceCode) | 126 |
| coded-fixed (subclass fixes its code) | 24 |
| shared-evidence (agentic-mbse SemanticEvidenceError) | 24 |
| shared-profile (`executable_profile` string reasons) | 29 |
| coded-relay / plumbing / helper-returned / table-mapped | 15 / 7 / 1 / 1 |
| coded-DYNAMIC (the falsifier) | 6, all exempted with a reason |
| free-text (codegen exception, no code) | 137 |
| builtin (candidate raises; public-boundary normalization and reachability need per-path analysis) | 130 |

## Findings

- **The pattern already works in codegen.** `test_diagnostic_provenance_sites.py` enumerates raise sites for 4 guarded codes by AST, and `test_ast_dispatch_invariant.py` fails on unaudited dispatch sites. Both pass. The end state widens an existing, working technique; it doesn't invent one.
- **Weak point 1: six non-literal codes.** One is snapshot replay, which is validated by enum construction. Five are in agentic-mbse `executable_profile.py:542,597,660,711,813`, where reason strings are built at run time (`f'block_{operator}'`, `reason`, `derived`). Correction after audit: `executable_profile.REASON_CODES` already enumerates 27 permitted reasons, and `EligibilityDiagnostic.__post_init__` rejects unknown reasons. These five sites expose a scanner-resolution limitation. Map their possible emissions to the existing vocabulary and test it; conversion to an enum is not required.
- **Weak point 2: code-free sites.** 137 free-text sites, 35 of them `CodeGenerationError` and 20 `PredicateCompileError` (the generation preflight), have no stable code. Classification has to be per site, or those raises need codes.
- **Weak point 3: builtin raises need classification, not an automatic invariant label.** 67 of the 130 have refusal-like wording ("invalid", "cannot", "must"). Treating them as internal invariants is unproven per site, as the epic's principle 4 warns.
- **Weak point 4: silent omissions are invisible.** Control D shows this. Dropping String metadata (ES-010) can never be caught by a raise inventory. It needs the differential and behavioral tests from Claim 1.
- **The classification is a draft.** It was written by this agent, not owner-reviewed. The baseline marks the current tree as "reviewed" by construction.

## Audit clarification (2026-10-15)

The raw inventory/logs and dynamic-exemption CSV are historical prototype outputs. Their “DEBT” descriptions do not override the existing enforced reason vocabulary. The 137 free-text and 130 builtin sites require review by semantic role, including malformed input, environment and snapshot handling; not all require new stable codes or an unreachable-input proof. The manually authored baseline/classification is not an independent review.
