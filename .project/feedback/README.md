# How to Record Feedback

Entries go in `ENTRIES.md`, in this directory. This file is the rules; that file is the log. `ENTRIES.md` is user data, so `init-project.sh --force` refreshes this file and never touches that one.

The owner asks in prose — "record your learnings as feedback." Nothing else triggers it. No command reads the entries back; the file exists so the owner can fix the pack target upstream, and once fixed the entry is dead.

## The entry

Append to the end of `ENTRIES.md`. Never rewrite an existing entry. One entry per pack target — feedback that applies to two targets is written as two entries.

```markdown
## [_my_spec] 2026-08-25

**Wrong:** I listed every constraint the owner mentioned as a `[NEED]` requirement.
**Right:** Only constraints the owner stated as requirements are `[NEED]`. Ones I derived are `[INFERRED]`.
**Learning:** Grade a requirement by who originated it, not by how load-bearing it looks. An inference that turns out to be important is still an inference.
```

- **The tag** is the bare name of the pack target, in brackets: `_my_spec`, `_my_mental_model`, `working-voice`. No folder path, no `.md` extension. Names are unique across commands, skills, and rules.
- **The date** is today, ISO format.
- **Wrong and Right** are the specific case: what you produced, and what the corrected version was. Not a transcript of the exchange, and not a quote of the owner.
- **Learning** is the generalization, and writing it is your job, now, while you still hold the context. Specific enough to act on, general enough to apply past the case that produced it.
- **No body line starts with `## [`.** That sequence marks the start of an entry.

## Reading entries back

Nothing reads this file automatically. To pull every entry for one target:

```bash
awk -v t='[_my_spec]' '/^## \[/{k=($2==t)} k' ENTRIES.md
```

The bracketed tag is the second whitespace-separated token on the heading line. Keep it there — that is what makes selection a one-liner instead of a parser.
