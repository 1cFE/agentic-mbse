# DRAFT — sysml-codegen ADR 0012 amendment (for EXEC-SUBSET-CONTRACT Item 2 to file)

> **Filing time decided (2026-10-18, [AGENT] ratified by owner):** file in sysml-codegen when Item 1 merges, not at Item 2 start, so codegen's record matches reality from day one. The entry must state that the CI parity gate lands in Item 2 and that until then the guard is agentic-mbse's parity test against stored codegen outputs.
>
> **Status: ready-to-file draft. Not filed.** Item 1 writes nothing into sysml-codegen. Item 2 (or the owner, earlier) files it in sysml-codegen with the commands below. Source: design Appendix B.2, with the owner's end condition filled in.

## Commands (run in sysml-codegen, by Item 2)

```bash
cd ~/src/sysml-codegen
.project/scripts/adr.sh new occurrence-summary-shared-with-agentic --title "Occurrence summary has a second reviewed owner in agentic-mbse, held by a parity test"
# fill the new entry's body from the section below, then:
.project/scripts/adr.sh amend 0012 <new-id>
.project/scripts/adr.sh index
```

Frontmatter to set in the new entry: `provenance: "[AGENT] (ratified by owner, 2026-10-18)"`, `seams: [elaboration, agentic-mbse]`.

## Entry body

### Decision

ADR 0012's invariant "Raw parser reads for declaration discrimination, slot construction, and multiplicity retain their narrow codegen ownership" is amended. These reads now have two reviewed owners. Codegen keeps them for elaboration. agentic-mbse's `occurrence_extraction` performs the same reads for the shared executable-subset contract, through its own reviewed accessors. The two are held together by end condition (ii): codegen keeps its occurrence index, and a permanent parity test in codegen CI compares agentic-mbse's occurrence summary with codegen's own occurrence index on a shared seed and fails on any difference. Every other 0012 invariant is unchanged.

### Why

L6 and the shared contract need instantiation facts, and agentic-mbse cannot import codegen (ADR 0007). Spike F1 (agentic-mbse `exec-subset-profile`, 2026-10-15) showed a summary port matching codegen `b5663c07` on 72 of 72 cases; Item 1's recorded parity run matched 73 of 73 (34 seed fixtures, 37 v6 corpus fixtures, both dc3 trees). 0012's concern, that a weaker alternate read could drop evidence, is answered by parity on exact evidence (ADR 0004), not by exclusive location. The owner chose end condition (ii) over (i) (codegen swapping onto the shared module): codegen keeps its elaboration code, and the parity test makes drift fail in codegen CI where the change is made.

### Invariants established

- Until EXEC-SUBSET-CONTRACT Item 2 lands the codegen CI parity test, the guard is agentic-mbse's parity test against stored codegen oracle outputs (`tests/test_sysml/test_occurrence_parity.py`); codegen changes are caught on re-capture, not on every codegen commit.

- agentic-mbse's occurrence summary and codegen's occurrence index agree on the parity seed at every codegen commit; the CI parity test is the gate.
- A change to codegen's declaration discrimination, slot construction or multiplicity reading that changes occurrence facts is not complete until agentic-mbse's summary matches or the contract is re-pinned.

### Rejected alternatives

- Keeping exclusive codegen ownership (option A′): rejected because it leaves the contract unable to decide instantiation-dependent refusals until a single move.
- End condition (i), codegen swaps onto the shared module and deletes its copy: not chosen by the owner (2026-10-18).
