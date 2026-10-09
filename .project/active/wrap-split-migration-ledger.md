# WRAP-SPLIT migration ledger

Item 2 owns this file; Item 1 created it for its own rows. Each row records consumer-specific text that leaves agentic-mbse-installed files, where it was, its fusion-tea home, and the evidence. The owner applies every fusion-tea change; fusion-tea must hold each destination before the agentic-mbse change that removes the text merges.

## Item 1 — native-skill-distribution

| Text | Was in (fusion-tea) | New fusion-tea home | Evidence |
|---|---|---|---|
| The `.codex-test` worktree paragraph ("For this worktree, use `.agentic-mbse/patterns/` … Use `.codex-test/run` for toolkit/Python commands …") | `.agentic-mbse/codex.md:11`, a tool-owned file a re-init replaces with no prompt (it matches its manifest hash) | `AGENTS.md`, appended verbatim under a heading naming its source | `native-skill-distribution/evidence/fusion-tea-target-owned.patch`; rehearsal confirmations (`evidence/rehearsal/*-confirm.txt`) |
| The pattern-location note ("Pattern references such as `[patterns/plant-idiom.md]` name files in this worktree's `.agentic-mbse/patterns/` directory …") | `modeling_project/MODELING_GUIDE.md:276`, tool-owned and replaced with no prompt | `AGENTS.md`, appended verbatim | same patch and rehearsal |
| The two MR-7 paragraphs | `modeling_project/MODELING_PROCESS.md:17` and `:34` | Stay in place. The file differs from its manifest hash, so a re-init prompts for it; runbook step 4 keeps it (answer `s`). Item 2 lands the general section | rehearsal confirmations; `native-skill-distribution/evidence/fusion-tea-runbook.md` step 4 |

**Facts the pattern-note row carries (design D10).**

- After the re-init, Codex reads two conflicting instructions: the shipped guide says to locate pattern docs with the `get_docs_dir()` resolver, and `AGENTS.md` says to use `.agentic-mbse/patterns/`.
- That worktree copy equals `main`'s `docs/patterns/` today (its 14 manifest hashes match `8f43a09`), but no installer refreshes it any more.
- The note's stated reason, that the copy "is versioned separately from the pinned executable runtime", ends at runbook step 1, when the pin moves to the merged SHA and the resolver then points at same-version docs.
- **Owner choice, does not block Item 1:** after step 1, keep the note, drop it, or copy it into `CLAUDE.md`. It is fusion-tea's own text.
