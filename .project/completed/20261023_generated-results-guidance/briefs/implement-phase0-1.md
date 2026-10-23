Implement Phases 0 and 1 of .project/active/generated-results-guidance/plan.md (EXEC-SUBSET-CONTRACT Item 5, rescoped), then stop and report. Read the plan, design.md and spike/RESULTS.md first.

- Phase 0: create sysml-codegen's `native-generated-compare` branch from origin/main in /home/reid/src/subset-conformance/sysml-codegen (its current branch subset-profile-screen is merged; switch away from it, don't delete it; if the working tree has untracked files, leave them). Record base failure IDs for both suites, toolchain revisions, the simkit-lane smoke check, and the "before" byte-identity snapshot, exactly as the plan says.
- Phase 1 is a hard gate. Run the probes for B1-gaps, B2 (multiplicity dependence including [0]), B3 (effective-usage scope on a dc3-shaped redefinition model) and B4 (value redefined two levels out). Record each result with the exact command and output. If any bet fails, stop and report the failure plainly with what it means for the design; do not redesign or work around it.
- Check off the plan's checkboxes as you finish them, with short implementation notes. Commit in each repo per the plan (explicit paths, never `git add -A`; commit messages end with the two attribution lines below). No pushes, PRs or merges.

Commit trailer lines:
Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_015D7Mj6qmraD8g52Zjas4eJ

Owner-reserved, do not decide: RG-1 (what the generator accepts/refuses/builds), RG-2 (String / dropped result-expression guidance), RG-3 (pushes, merges, PRs, ADRs). Never edit dc3 or TEAx.
