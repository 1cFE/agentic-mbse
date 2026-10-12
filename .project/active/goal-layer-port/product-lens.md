# Product-Lens Ledger: goal-layer-port

Epic: WRAP-SPLIT (Item 2). Epic gate at entry: CLEAR (epic-F1 FIXED 2026-10-08 by owner ruling; epic-F2..F4 FIXED; epic smell 1 ESCALATED to the Item 2 and Item 3 designs at AGENT grade). The epic file's ledger stays the source of truth for epic findings. Append-only; a changed gate is a new dated block.

The checker was a fresh general-purpose agent. It could not read `~/.claude/scripts/product-lens.md` or its pack copy (permission denied), so it used the fallback method in its brief: re-derive the point, state a falsifier, check both directions, grade findings by source authority.

```
## spec — 2026-10-11 — rev .project/active/goal-layer-port/spec.md (untracked; goal-layer-port @ 941ce4a)
Epic: WRAP-SPLIT
- epic-F1: FIXED — authority: owner ([OWNER-VERBATIM] 2026-10-06) — the research seam is Item 5. Spec respects it (Non-Goals; interim research wording).
- epic-F2: FIXED — authority: INHERITED (CLAUDE.md Change Coordination) — Item 1 made replicate_setup.sh a thin init wrapper; the spec only touches cmd_init.
- epic-F3: FIXED — authority: INHERITED — Item 3's sysml-codegen ownership work; does not bear on this item.
- epic-F4: FIXED — authority: INHERITED — the README init list belongs to Item 4; the spec defers it there and keeps CLAUDE.md accurate.
- smell 1: ESCALATED — authority: AGENT — the shipped decision record vs fusion-tea's live ADRs. Carried to design (Open Questions, "Decision record: home and authority"); SC10 checks grade and commit. Still open for design.
Point (re-derived): agentic-mbse ships general, domain-agnostic capability that a target gets from `init`. Here that means a working goal layer with nothing pointing at fusion-tea, plus the design-choice principle placed at the right level of agentic-mbse's existing enforcement system. fusion-tea moves onto the installed copies, loses nothing, and keeps its MR-7 enforcement intact after re-init.   [source: research § Research Question (owner-verbatim); Align :12 (OWNER-VERBATIM 2026-10-11); epic header :19,:22 and SC :65-66 (OWNER); README.md:3, docs/source-index.md:7 (INHERITED); harness concept :198 (OWNER); Align :7 (AGENT, owner did not object)]
Falsifier: (A) A fresh target cannot ground a goal, or installed text cites fusion-tea or MR-7 as authority, or the rule sits outside the levels where modelers and reviewers act. (B) After re-init, fusion-tea has lost an instruction, or its MR-7 enforcement depends again on a preserved hand-edit of a tool-owned file.
Findings:
- spec-F1 [DO] The spec drops half of an inherited owner criterion. The epic says "fusion-tea's MR-7 enforcement is intact after re-init" (epic :66 [OWNER]), inherited by every item spec (:74); the Align record overrides only the "MR-7 unchanged" clause. Known Requirements carried only the no-loss criterion, and SC8 did not walk the enforcement chain on the re-initialized copy (CLAUDE.md:5 → MR-7 → shipped rule → Process Selection trigger → goal-template and runbook pointers). — epic :66 (OWNER) — disposition: proposed — add it as [INHERITED: epic, OWNER] with "unchanged" struck per Align :12, and extend SC8 to walk that chain.
- spec-F2 [DO] SC8 and the loss-free requirement accepted any "outcome the design names" for fusion-tea's own runbook and templates, which lets a design keep fusion-tea's modified local copies (skip at the prompt, or preserved non-interactively). That rebuilds the hazard the Problem describes and leaves two runbooks kept in step by hand. — Align :7 "fusion-tea can move to the installed copies" (AGENT, owner did not object); epic :40, :64 (INHERITED) — disposition: proposed — SC8 states the end state (installed, manifest-matched copies; fusion-only text in fusion-owned homes); any kept local fork is surfaced to the owner.
- spec-F3 [DO] The MR-7 obligation list claimed "each general obligation MR-7 states" but left out general sentences: a parameter leaving the public interface or becoming a calculated binding must be called out (REQUIREMENTS.md:101); defaults, mode switches and multipliers must not hide automatic adequacy (:101); test varying demand with hardware fixed where the interface allows (:105); unknown compliance is not completed remediation (:105); swapping one hidden fixed choice for another does not fix it (:107); the scope limit that no acausal solver is required (:96). Without the scope limit the shipped rule over-reaches. — fusion-tea REQUIREMENTS.md:96-107 (INHERITED, AGENT ratified 2026-09-20) — disposition: proposed — add them, or label the list a summary and name SC6's crosswalk as the completeness check.
- spec-F4 [DO] Grade hygiene: (a) "This is the pattern the owner refers to" is an ungraded agent reading of the owner's quote, and the Open Questions read "patterns" as docs/patterns/; mark it [INFERRED]. (b) Ratified [AGENT] items sat under the heading "From the owner". — capture-fidelity law 1; Align :12 (OWNER-VERBATIM) — disposition: proposed — re-grade the wording only.
Smell fired: two hand-synchronized copies (spec-F2: the shipped runbook vs a retained fusion-tea fork); grade inflation (spec-F4, minor). Not fired: MR-7 vs the shipped rule as two copies, because the spec moves MR-7's general sentences out; SC5(f) as a test that selects the implementation, because it pins outcomes the SC requires and leaves the rule's home open.
Checked and clean: Problem matches the owner's ask and the Align direction; SC2's grep covers the epic list and more; SC4 dry run excludes fusion-tea; SC7 keeps MR-7's authority line and owner quote; Non-Goals respect the Item 3, 4 and 5 boundaries; the pattern-location line is consistent with CURRENT_WORK (8a35c4d0f) and Item 1's ledger rows; the owner's timing rule for destinations is met by the merge-order requirement; "just do it yourself" is carried; the research seam and the result → outcome table are deferred per the ratified Align decision.
Gate: DISPOSED — spec-F1 (owner-grade omission, not a contradiction) and spec-F2, F3, F4 need visible dispositions before design.
```

```
## spec — 2026-10-11 — rev .project/active/goal-layer-port/spec.md (after dispositions)
Resolves:
- spec-F1: FIXED — authority: owner (epic :66 [OWNER], amended by Align :12 OWNER-VERBATIM) — basis: Known Requirements add "[INHERITED: epic success criterion :66, OWNER; amended by the Align record] fusion-tea's MR-7 enforcement is intact after re-init"; SC8 now walks the chain CLAUDE.md:5 → MR-7 → shipped rule → Process Selection trigger, and goal template/runbook/run-goal → shipped rule, on the re-initialized copy, with nothing resting on a kept tool-owned edit.
- spec-F2: FIXED — authority: AGENT (Align :7, owner did not object) — basis: SC8 states the end state (runbook and templates are installed, manifest-matched copies; the goal skills are the installed bundles or the design names the epic integration step that switches them); the loss-free requirement says a kept local fork is surfaced to the owner.
- spec-F3: FIXED — authority: INHERITED (MR-7 :96-107, AGENT ratified) — basis: the six missing obligations are added to the list, which is now labelled a summary with SC6's crosswalk as the completeness check.
- spec-F4: FIXED — authority: capture-fidelity — basis: the "patterns" reading is marked [INFERRED] and notes SC5 checks both readings; the Known Requirements heading now reads "Owner-stated, inherited from upstream artifacts, or ratified by the owner".
- smell 1: ESCALATED — authority: AGENT — basis: unchanged; the decision record's home and authority stay a design question.
Gate: CLEAR
```

```
## spec — 2026-10-11 — rev .project/active/goal-layer-port/spec.md (spec-review resolutions applied; no re-run)
- spec-F4(a): basis amended — authority: AGENT (orchestrator call on spec-review L2-1) — the "patterns" reading stays [INFERRED], but the spec now maps the nearest existing pattern, Equality intent (docs/patterns/constraints.md:46-69, sysml-conventions:200-211), as the rule's sibling and checks the relation in SC5(h), instead of noting that SC5 covers both readings.
- spec-F3: basis unchanged; the summary also now says design works from MR-7's text, and "not automatically violations" and "a calculation or binding" are restored to MR-7's force (spec-review L1-1).
- No finding reopened: the review's resolutions narrow nothing the point requires. The trigger keeps MR-7's own enforcement scope (orchestrator call L3-3), so fusion-tea's enforcement chain in SC8 is unchanged.
Gate: CLEAR
```
