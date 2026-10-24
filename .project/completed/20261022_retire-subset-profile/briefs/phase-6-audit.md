# Brief: Phase 6 audit (fresh reviewer)

You audit the retirement of the copied generator rules across two branches. You did not write any of it. Be skeptical: verify by running and reading, not by trusting the implementation notes. Do not edit code; write your findings to `/home/reid/src/subset-conformance/agentic-mbse/.project/active/retire-subset-profile/audit.md` and commit only that file (subject leading with the verdict, ending `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`).

Read first: `spec.md` (requirements R1-R9, decisions D-a to D-e, acceptance), `plan.md` with its implementation notes, and the design rationale (sysml-codegen `.project/active/subset-profile-screen/architecture-review/03-challenge.md`, and ADR 0004 in agentic-mbse `.project/adr/`).

Branches:
- agentic-mbse `/home/reid/src/subset-conformance/agentic-mbse`, branch `retire-subset-profile`, base `e268357f` (`git diff e268357f...HEAD`).
- sysml-codegen `/home/reid/src/subset-conformance/sysml-codegen`, branch `subset-profile-screen`; this audit covers commits after `529830cf` (`git log 529830cf..HEAD`). Earlier 2b work was audited separately.

Check, at least:
1. Every requirement R1-R9 and acceptance line: met, with the evidence you ran. Run both suites yourself (`uv run pytest tests/` in agentic-mbse; in sysml-codegen the same command its `.project/active/subset-profile-screen/plan.md` Phase 9 used). Compare with `evidence/baseline.md` and `evidence/suite-baseline-agentic.md`. Re-run the byte manifest and refusal-record comparison if you can find the commands; otherwise say so.
2. Nothing the generator accepts or refuses changed (RG-1). Look specifically at the stored-answer edits in sysml-codegen (the 154 moved cases, the witnesses moved into stored answers, 16 dropped): could any dropped or moved thing hide a generator regression that the tests used to catch?
3. Code quality: dead code left behind (for example `reference_use.invocation_uses` / `InvocationUse` reported as now unused), stale names, comments describing removed things, shims, half-renames, docstrings that still describe the copy, unused fixtures, the new `sysml/element_refs.py` and `execution_target.fold()` for clarity and naming.
4. User-facing text: README, CLAUDE.md, L6 title and messages, `init` prompts, `validate --help`, the shipped skills and templates, guidance in `MODELING_GUIDE.md.template` and `docs/patterns/`. Is anything misleading about what L6 or `validate` says regarding generation? (The dc3 incident happened partly because L6 was titled "Pipeline Readiness" and read as a generation answer; L6 is now titled "Architecture & Codegen Conventions": judge whether that repeats the problem.) Do the guidance examples match `evidence/probes.md` and `evidence/guidance-examples/`?
5. Records: ADR 0004/0005, P-0004/P-0005, the epic, BACKLOG, CURRENT_WORK: accurate to what was built, provenance grades per `/home/reid/src/agentic-mbse/.claude/rules/capture-fidelity.md`, stale statements.
6. sysml-codegen leftovers: the refusal site account's `rule` and `matrix_row` columns still hold the copy's rule IDs; `[SUBSET-SCREEN-SNAPSHOT-CARRIAGE]` in its backlog is moot; docs (`CLAUDE.md`, `docs/architecture/`) mention of the screen.
7. The generator behaviour found during Phase 2: a part count given by an attribute with a `default` that a usage or specializing def redefines passes `check` but `generate` builds the default count, silently (`evidence/guidance-examples/m_attr*`). Confirm it reproduces, and confirm a backlog row exists in sysml-codegen; if not, list it as a finding (the fix itself is the owner's, RG-1).

Write `audit.md`: verdict (Certify / Needs Work), then findings ranked blocker / should-fix / note, each with file:line, what is wrong, and the concrete fix. Plain sentences, one line per paragraph. Report the verdict and the findings list in under 400 words.
