---
id: 0001
title: agentic-mbse owns the executable-subset capability contract and its occurrence summary
date: 2026-10-18
owner: Reid Westwood
status: superseded
amended_by: []
superseded_by: 0004
provenance: "[AGENT] (ratified by owner, 2026-10-18)"
seams: [agentic-mbse, sysml-codegen, l6, guidance]
supersedes: null
promoted_to: null
---

## Decision

agentic-mbse owns the declared executable-subset contract (the versioned, evidence-backed record of the generator's refusals, `sysml/subset_profile_rules.toml`, and the pure evaluator `sysml/subset_profile.py`) and the neutral facts it needs, including a summary of the occurrences the generator instantiates (`sysml/occurrence_extraction.py`); sysml-codegen owns the behavior the contract describes, its diagnostic-code mapping, output facts and rendering, and L6 and guidance consume the contract. The occurrence summary and codegen's own occurrence index are held together by end condition (ii): codegen keeps its index, and EXEC-SUBSET-CONTRACT Item 2 adds a permanent parity test in codegen CI. The owner chose Option A with end condition (ii) on 2026-10-18 (reply "A (ii)"; recommendation in `.project/active/exec-subset-profile/design.md` § R1).

## Why

- L6 and guidance must consume the contract without importing codegen. sysml-codegen already depends on agentic-mbse, so the reverse import would be a cycle (codegen ADR 0007).
- Separate implementations of one decision drift. On dc3's baseline, L6 reported B7 and B8 and missed B1-B6, which the generator refused one run at a time.
- Codegen ADR 0007 places model facts in agentic-mbse, and occurrence reach (which part usages the generator instantiates) is a model fact. Three refusals depend on it: binding sources (ES-003/ES-012), part multiplicity (ES-004) and blocked predicates (ES-007).
- A pure decision layer keeps capability refusals distinct from evidence failures, and versions the decisions separately from the facts.
- Spike F1 measured the summary port against codegen `b5663c07` (72 of 72 cases), and Item 1's parity run matched 73 of 73. Parity on exact evidence, not exclusive location, is what keeps a second reader honest; end condition (ii) makes that parity permanent where codegen changes.

## Invariants established

1. The contract reports any outcome other than `unconfirmed` only with retained evidence: a probe of the pinned generator whose observed code matches, or a corpus citation for `admitted`.
2. Pairs without evidence report `unconfirmed`; missing facts report `unverified`; only verdict `CLEAR` is clean, and `CLEAR` is relative to the implemented rules: it does not mean the model will generate (refusal families without a rule, such as deep-qualified wiring, are listed in the matrix).
3. No agentic-mbse module imports sysml-codegen; `SI_*` codes appear only as evidence.
4. The invocation allowlist (`sysml/invocation_allowlist.py`) is the one capability decision reached from the fact layer; changing it changes `SUBSET_PROFILE_VERSION`.
5. Ground truth is the pinned generator until EXEC-SUBSET-CONTRACT Item 2. After Item 2 it is Item 2's independent corpus: elaboration with the contract screen bypassed.
6. The occurrence summary and codegen's occurrence index are held together by end condition (ii): a permanent parity test in codegen CI, added by Item 2. Until it exists, the recorded parity run (`scripts/subset_profile/occurrence_parity.py compare --all`) at each pinned codegen revision is the check.

## Rejected alternatives

- Codegen-owned policy: rejected because L6 and guidance could not consume it without a reverse dependency.
- Decisions in the fact layer: rejected because they would be indistinguishable from evidence failures and blind to context.
- Per-consumer implementations: rejected because the decisions drift.
- No port, with instantiation contexts left `unconfirmed` (Option A′): rejected because it leaves dc3 B2, B3 and B8 undecided until Item 2.
- End condition (i), codegen swaps onto the shared module and deletes its copy: not chosen; the owner chose (ii).
