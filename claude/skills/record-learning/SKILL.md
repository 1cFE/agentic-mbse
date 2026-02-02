---
name: record-learning
description: >
  Capture and record learnings, discoveries, and insights from modeling sessions.
  Use when: you discover a pattern, solve a tricky problem, find a workaround,
  learn something about SysML syntax, resolve a confusing error, or identify
  a best practice worth remembering.
  Triggers: "record this", "capture learning", "I learned", "worth remembering",
  "let's document this", "record what we discovered"
allowed-tools: Read, Write, AskUserQuestion
user-invocable: true
---

# Record Learning

Capture learnings from the current modeling session for future reference.

## When to Use

Invoke this skill when you:
- Resolve a parse error and discover the correct syntax
- Find an import that wasn't obvious
- Discover behavior that differs from expectations
- Identify a pattern worth codifying
- Learn something that would help future sessions

## Scope: Process Learnings vs Domain Insights

This skill captures **process/tooling learnings** — discoveries about how to use the tools and language correctly. These are distinct from **domain insights**, which capture what the domain teaches us.

| | Process Learnings (this skill) | Domain Insights (`add-insight`) |
|---|---|---|
| **What** | SysML syntax, parser behavior, import patterns, workflow patterns | Domain facts, parameter values, design constraints from sources |
| **Where** | `work/learnings/RAW_LEARNINGS.md` | `knowledge/KNOWLEDGE.md` (as DI-XXX) |
| **Format** | Append-only, timestamped entries | Structured DI-XXX entities with status tracking |
| **Consumer** | Future modeling sessions, retrospectives | Model requirements, design decisions, traceability |

### Cross-Suggestion

When a learning has domain implications, **also suggest creating a DI-XXX entry**. Example: "This SysML limitation means we need a different modeling approach for thermal components" is both a process learning (SysML limitation) and a domain insight (modeling approach change). Record the process learning here, then suggest: "This also has domain implications — consider capturing a DI-XXX via `add-insight`."

## Process

### If User-Invoked (`/record-learning`)

1. **Reflect on conversation**: Review the recent conversation for:
   - Problems that were encountered and resolved
   - Syntax corrections made
   - Import patterns discovered
   - Workarounds implemented
   - Insights about SysML or the modeling process

2. **Identify learning candidates**: For each potential learning, determine:
   - Is this reusable (would help in other projects)?
   - Is this specific enough to be actionable?
   - Is this novel (not already in MODELING_GUIDE)?

3. **Present to user**: Show 1-5 learning candidates with:
   - Category
   - Brief summary
   - Why it's worth recording

4. **Get confirmation**: Use AskUserQuestion to let user approve/reject each

5. **Record approved learnings**: Append to `work/learnings/RAW_LEARNINGS.md`

### If Agent-Invoked (via Skill tool)

1. **Reflect on what was discovered**: Even if you know what you learned, explicitly
   articulate the problem, solution, and generalization. Reflection improves comprehension.

2. **Determine category**: Import Pattern | Syntax Gotcha | Error Interpretation | Workaround | Best Practice

3. **Present to user for approval**: Use AskUserQuestion to confirm:
   - "I discovered something that might be worth recording:"
   - Category and summary
   - "Should I record this learning?"

4. **If approved**: Record to `work/learnings/RAW_LEARNINGS.md`

5. **If rejected**: Acknowledge and continue without recording

## Learning Categories

| Category | When to Use |
|----------|-------------|
| **Import Pattern** | Missing imports, stdlib function access, qualified name issues |
| **Syntax Gotcha** | Valid-looking syntax that doesn't parse, SysML quirks |
| **Error Interpretation** | Parser errors and their actual meanings |
| **Workaround** | Alternative approaches when direct approach fails |
| **Best Practice** | Preferred patterns over alternatives |

## Entry Format

Append entries to `work/learnings/RAW_LEARNINGS.md` using this format:

```markdown
---

## {YYYY-MM-DDTHH:MM:SS±HH:MM}

**Category**: {category}
**Severity**: {Critical | Important | Nice-to-know}
**Source**: {project name} modeling session

### Problem
{What was attempted and what went wrong}

### Solution
```sysml
{Working code or approach}
```

### Generalization
{The broader principle - what should be remembered}

### Verification Status
- [ ] Parser tested
- [ ] Doc verified
- [ ] Formalized to pattern doc

---
```

## Example Recording

After discovering that `sum()` requires an explicit import:

```markdown
---

## 2026-01-15T16:30:00-05:00

**Category**: Import Pattern
**Severity**: Critical
**Source**: fusion-tea modeling session

### Problem
Tried to use `sum(collection)` for cost aggregation but got unresolved reference error.

### Solution
```sysml
private import NumericalFunctions::sum;
attribute total : Real = sum(costs);
```

### Generalization
All stdlib functions need explicit imports. Cannot use qualified names directly
in expressions without an import statement.

### Verification Status
- [x] Parser tested
- [ ] Doc verified
- [ ] Formalized to pattern doc

---
```

## File Location

- **Learnings file**: `work/learnings/RAW_LEARNINGS.md`
- **Create if missing**: Initialize with header template

## Guidelines

- **Be specific**: Include actual code that works
- **Be general**: Extract the principle, not just the fix
- **Be brief**: One learning per entry, not a dissertation
- **Verify**: Run `uv run agentic-mbse validate` on code examples before recording
- **Don't over-record**: Only genuinely reusable insights, not typo fixes
