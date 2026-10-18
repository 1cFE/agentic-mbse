# Product-lens ledger: ARXIV-EXTRACTION

## 2026-10-18 · design review of `design.md`

**Lens source:** the lens script (`~/.claude/scripts/product-lens.md`) could not be read in this session (permission denied), so no lens subagent ran. The reviewer derived the point independently from the sources below. Treat this entry as a reviewer derivation, not a lens run.

**Sources:** owner goal as relayed by the orchestrator `[OWNER]` and recorded in `spec.md` Problem `[NEED]`; spec `R1`–`R5`; `spec_review.md` Resolutions. No `.project/product/` ledger and no `.project/adr/` exist in this worktree.

**Point (derived):** a consumer runs `extract` with Pandoc on PATH and no workarounds, and gets the right paper, its figures on disk, and nothing but the paper. When the shortcut does not fire or falls back, the consumer can see why.

**Design's point:** matches (design.md "The Point" states the same test).

**Findings:**
- DO (owner `[NEED]`): no citation substitution. Covered by D1/D2 and Invariants 4–5. Disposition: met.
- DO (owner `[NEED]`): no missing figures. Covered by D7/D8 for both routes. Disposition: met, with one gap: the PDF route's image base URL is not pinned down (see design review M2).
- DO (owner `[NEED]`): no arXiv chrome. Covered by D4. Disposition: met on the primary path. A double failure on the web route (article conversion fails, trafilatura short) still reaches `_fallback_pandoc` over the whole page (see design review m5). Lower authority edge, visible disposition only.
- DON'T (owner reserved): settle the default-on gate. Design keeps it provisional and a one-line flip (D10). Disposition: respected.
- DON'T (owner reserved): remove or rename public `PipelineConfig` fields or CLI flags. Design only adds (Invariant 9). Disposition: respected.

**Structural smells:** consumer compensating for a producer guarantee: not fired (the work removes consumer compensation). Invariant ownership moved without saying so: not fired (image persistence and identity ownership moves are stated in D3, D2).

**Gate:** CLEAR.
