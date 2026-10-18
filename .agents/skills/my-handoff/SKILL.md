---
name: my-handoff
description: Write a handoff document to the OS temp directory so a fresh agent can continue the work. Use when ending a session and the next agent needs focus, context references, key discoveries, and suggested skills.
---

Generated from `claude-pack/commands/_my_handoff.md`. This is a command-derived Codex skill. Rebuild it instead of editing it by hand.

# Handoff

Write a handoff document so a fresh agent can pick up where this session left off.

## Instructions

1. Choose a path in the OS temp directory: `${TMPDIR:-/tmp}/handoff-$(date +%Y%m%d-%H%M%S).md`. Do not save inside the workspace.
2. Write the document with these sections:
   - **Focus** — if `User-provided arguments are supplied when this skill is invoked.` is given, treat it as the next session's focus and tailor the rest accordingly. Otherwise summarize what the next session should pick up.
   - **Context** — brief situation summary. Reference PRDs, plans, ADRs, issues, commits, and diffs by path or URL instead of restating their contents.
   - **Key Discoveries** — non-obvious learnings from this conversation (gotchas, dead ends, validated assumptions) that aren't already captured in those artifacts.
   - **Suggested Skills** — slash commands the next agent should likely invoke (e.g. ``my-project-find``, ``my-plan``), one line of reasoning each.
   - **Open Questions** — anything unresolved or awaiting user input.
   - Mark each substantive claim by status — **verified this session** vs **carried** (from
     prior docs or another agent, not re-checked here) — so the next agent knows what to
     trust and what to re-verify.
3. Redact secrets before writing: API keys, tokens, passwords, PII, customer data. Replace with `[REDACTED]`.
4. Print the absolute path of the file you wrote so the user can share it.
5. Pause when you are done writing and wait for further instruction. Writing the handoff is the whole job. If the user listed what comes next alongside the request, that belongs in the Focus section — do not go and do it.

User-provided arguments are supplied when this skill is invoked.

