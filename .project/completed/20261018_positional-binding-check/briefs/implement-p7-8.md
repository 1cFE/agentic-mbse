Implement **Phases 7 and 8** of `.project/active/positional-binding-check/plan.md` (EXEC-SUBSET-CONTRACT Item 4), then stop and report. Phases 1–6 are done; read their implementation notes.

Same rules as `briefs/implement-p1-3.md` (owner boundary, read-only sibling repos via `git archive`, never stage the six unrelated working-tree edits, no repo-wide `ruff format`, Item 1 modules unchanged, tick and annotate, outcome-led commits ending `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`).

Specifics:
- **Codegen conformance evidence (I8):** another agent is actively working in `~/src/sysml-codegen` (its checkout is at `8396cb23`, not `b5663c07`). Do not run anything inside that checkout. Export sysml-codegen at `origin/main` (record the commit) and at `b5663c07` into scratch dirs and run `tests/conformance/test_self_binding_guidance_contract.py` from those exports against this branch's guidance, with the imported agentic-mbse path recorded and proven to be this checkout. Report both results. If the test reads `.claude/` on disk, record what it saw.
- The draft upstream finding about codegen's by-name wiring (native -7 vs generated 7) is written in this repo only, as a draft for the owner to route; do not file anything in sysml-codegen.
- Guidance edits: say which side to rename for self-binding (the definition's parameter), qualify "Order does not matter" by context, and keep every phrase/link/pattern codegen's conformance test enforces.
- Final repository checks per the plan's green definition, compared with the Phase 1 baseline.

Finish with per-phase outcome, the conformance results at both codegen revisions, final check numbers, and the ARTIFACT line (plan.md).
