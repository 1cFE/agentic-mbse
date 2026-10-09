# Native Claude and Codex skills

## Requirements and decisions

- [NEED] Implement the native-support changes described in the owner-provided research summary on a new Git branch/worktree and test-install into `/home/reid/agentic-mbse-target`.
- [INHERITED] Inventory and feasibility evidence: ../../research/20260907-162310_native-claude-codex-skills.md. This is agent research, not owner-originated settled scope.
- [INFERRED] Ship all 15 workflows and ten supporting bundles from `skills/`, with `.agents/skills/` canonical installs and relative Claude aliases; provide explicit copy mode and Claude/Codex/both selection (default both).
- [INFERRED] Render five native expert roles from shared source; keep runtime tool mappings in small adapters. Preserve fresh stage/audit contexts, returned blockers, and owner-held decisions.
- [INFERRED] Track each managed file and alias in a neutral manifest; import legacy hashes; preserve skipped baselines, owner additions, configs, and customized legacy commands; never write through destination symlinks.
- [AGENT] Retain workflow names and existing implicit invocation. Keep extraction providers and inactive hook registration unchanged. Linux client versions from research are the smoke-test baseline, not a cross-platform certification.
- [AGENT] Existing contradictory `syside check` guidance remains outside this migration; validation behavior is unchanged. Permission guidance moves to the runtime adapters because the referenced guidance is absent from toolkit-awareness.

## Plan

- [x] Consolidate installer and lifecycle handling; expose runtime/copy selection.
- [x] Migrate shared skills, native roles/adapters, templates, and documentation.
- [x] Validate lifecycle regressions, source/wheel packaging, and existing suite.
- [x] Install into the requested fake repository; verify native discovery and supporting utilities; record behavior-test limits.

## Validation notes

The final full suite passed 1,926 tests (one skipped, five deselected). Changed-code Ruff and targeted mypy passed. Wheel tests compare every skill, agent, and adapter resource with source. Native catalog discovery passed with 25 Codex entries, 18 Claude invocable entries, and all five Claude expert roles. Both bundled utilities executed successfully from the installed target.

## Native role discovery correction

[AGENT] Explicit native role registrations are appended without replacing existing settings, comments, or roles. A process-configured `sysml-expert` spawned and read its bundled index. The subsequent project-configured probe returned `unknown agent_type`; inspection of Codex configuration layers showed that this new target was untrusted and its entire project config was disabled. A command-line trust override did not enable the project layer. The earlier error therefore does not prove that standalone roles are unsupported. The final nested probe passed with a private temporary trusted Codex home: root → fresh default stage → installed syside-expert → bundled documentation read. Personal trust settings remain unchanged.

## Audit remediation — 2026-09-08

[NEED] Address the owner-supplied audit findings that are valid and explain disagreements. The detailed source is `audit.md` (F-A–F-K) and its product-lens companion.

[AGENT] All eleven code/documentation findings are accepted. A separate retroactive `spec.md` is unnecessary because this plan already carries provenance-graded requirements, as allowed by the project workflow rules. These choices retain their existing grades. The `status` name and pre-existing validation-policy conflict remain as previously scoped.

- [x] F-A/F-B: list the actual bundle inventory and label symlinks accurately.
- [x] F-C/F-D/F-E: correct coordination, ownership, and file pointers in CLAUDE.md.
- [x] F-F/F-G: report per-client legacy divergence and prune only unchanged, tracked retired bundle resources.
- [x] F-H/F-I/F-J/F-K: remove unused constants, test adapter routing and prompt decisions, and let the installer own its action dictionary.
- [x] Run targeted and full checks, refresh the fake install, and record dispositions without changing the independent audit verdict.

Remediation validation: 1,944 full-suite tests and 115 focused tests passed; changed-file Ruff/format and targeted mypy passed. The rebuilt wheel refreshed the requested fake repo, and live native discovery passed. Findings and limits are recorded in `remediation.md`; independent re-review remains pending.
