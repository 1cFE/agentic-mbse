# Design: Learning Feedback Loop

**Status**: Implemented
**Owner**: Reid Westwood
**Created**: 2026-01-15
**Last Updated**: 2026-01-15
**Branch**: 1cfe_dev
**Commit**: f92a62a

## Overview

Design for capturing modeling learnings during Claude Code sessions, supporting two use cases:
1. **User-triggered**: User invokes `/record-learning` mid-conversation to trigger reflection
2. **Agent-initiated**: Agent proactively invokes the skill when it discovers something worth recording

## Related Artifacts

- Research: `project/research/20260113-150000_progressive-disclosure-architecture.md` (Part 3)
- Project: `CLAUDE.md` - Plugin architecture context

---

## Research Findings

### Claude Code Skills Architecture

**Skills are NOT scripts**. They are markdown files that get loaded into Claude's context window.

| Aspect | How It Works |
|--------|--------------|
| **Structure** | Directory with `SKILL.md` + optional supporting files |
| **Loading** | YAML frontmatter `description` triggers discovery |
| **Execution** | Markdown content becomes instructions in context |
| **Invocation** | User via `/skill-name` OR agent via `Skill` tool |

### Skill Discovery & Invocation

1. **At startup**: Claude loads only `name` and `description` of all skills (lightweight)
2. **When relevant**: Claude asks permission to load full skill content
3. **User invocation**: `/skill-name` explicitly loads the skill
4. **Agent invocation**: Claude calls `Skill` tool programmatically

**Key insight**: Skills can be proactively invoked by agents via the `Skill` tool. This enables agent-initiated learning recording without embedding "checkpoint stanzas" in commands.

### YAML Frontmatter Structure

```yaml
---
name: skill-name                          # Required. Lowercase, hyphens/numbers only
description: What this does and when...   # Required. Claude uses this to discover skill
allowed-tools: Read, Write, Grep          # Optional. Tools available during skill
user-invocable: true                      # Optional. Show in slash menu (default: true)
---
```

The `description` is critical—it contains trigger keywords that help Claude recognize when to use the skill.

---

## Proposed Design

### Single Skill: `record-learning`

**File**: `.claude/skills/record-learning/SKILL.md`

One skill handles both use cases:
- **User types `/record-learning`** → Skill loads → Claude reflects on conversation → Presents learnings → Records approved ones
- **Agent discovers something** → Invokes `Skill` tool → Skill guides recording → Notifies user

### Skill Structure

```
.claude/skills/record-learning/
├── SKILL.md              # Main skill definition and instructions
└── templates/
    └── entry.md          # Learning entry template (optional)
```

### SKILL.md Content

```yaml
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

5. **Record approved learnings**: Append to `project/learnings/RAW_LEARNINGS.md`

### If Agent-Invoked (via Skill tool)

1. **Reflect on what was discovered**: Even if you know what you learned, explicitly
   articulate the problem, solution, and generalization. Reflection improves comprehension.

2. **Determine category**: Import Pattern | Syntax Gotcha | Error Interpretation | Workaround | Best Practice

3. **Present to user for approval**: Use AskUserQuestion to confirm:
   - "I discovered something that might be worth recording:"
   - Category and summary
   - "Should I record this learning?"

4. **If approved**: Record to `project/learnings/RAW_LEARNINGS.md`

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

Append entries to `project/learnings/RAW_LEARNINGS.md` using this format:

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

- **Learnings file**: `project/learnings/RAW_LEARNINGS.md`
- **Create if missing**: Initialize with header template

## Guidelines

- **Be specific**: Include actual code that works
- **Be general**: Extract the principle, not just the fix
- **Be brief**: One learning per entry, not a dissertation
- **Verify**: Run `syside check` on code examples before recording
- **Don't over-record**: Only genuinely reusable insights, not typo fixes
```

### Directory Structure Created by Init

```
project/learnings/
├── RAW_LEARNINGS.md      # Append-only capture file
└── .gitkeep              # Ensure directory exists
```

### RAW_LEARNINGS.md Initial Content

```markdown
# Raw Learnings

Append-only log of modeling discoveries captured via `/record-learning`.

## How This Works

- **User-triggered**: Run `/record-learning` anytime to reflect on session and capture insights
- **Agent-initiated**: Agents may record learnings when they discover something noteworthy

## Review Process

Periodically review entries:
1. Verify correctness (run `syside check` on code examples)
2. Cross-reference with SysML v2 spec if applicable
3. Formalize valuable learnings into `docs/patterns/` documentation
4. Update MODELING_GUIDE.md Pattern Documentation Index

---
```

---

## Implementation Changes

### 1. Create Skill

**File**: `claude/skills/record-learning/SKILL.md`

Content as shown above.

### 2. Update `cmd_init()`

**File**: `src/agentic_mbse/cli/__init__.py`

Changes:
1. Add `record-learning` to `MBSE_SKILLS` list
2. Create `project/learnings/` directory during init
3. Create initial `RAW_LEARNINGS.md` (user-owned, skip if exists)

**File ownership**:
| File | Ownership | Behavior |
|------|-----------|----------|
| `project/learnings/RAW_LEARNINGS.md` | User-owned | Create once, preserve |
| `record-learning/SKILL.md` | Tool-owned | Update on re-init |

### 3. Encourage Proactive Usage

Add to `project/MODELING_GUIDE.md` footer or `CLAUDE.md`:

```markdown
## Learning Capture

When you discover something worth remembering—a syntax pattern, import requirement,
error interpretation, or workaround—use `/record-learning` to capture it.

Agents may also proactively record learnings when they resolve non-trivial issues.
```

---

## Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    MODELING SESSION                              │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┴─────────────────────┐
        │                                           │
        ▼                                           ▼
┌───────────────────────┐               ┌───────────────────────┐
│   USER-TRIGGERED      │               │   AGENT-INITIATED     │
│                       │               │                       │
│   /record-learning    │               │   Agent discovers     │
│                       │               │   something →         │
│   • Full conversation │               │   invokes Skill tool  │
│     context           │               │                       │
│   • Reflects, presents│               │   • Reflects on       │
│     candidates        │               │     discovery         │
│   • User approves     │               │   • Presents to user  │
│                       │               │   • User approves     │
└───────────┬───────────┘               └───────────┬───────────┘
            │                                       │
            └───────────────┬───────────────────────┘
                            │
                            ▼
             ┌──────────────────────────┐
             │ record-learning SKILL    │
             │ (loaded into context)    │
             │                          │
             │ • Provides format        │
             │ • Guides categorization  │
             │ • Specifies file location│
             └──────────────┬───────────┘
                            │
                            ▼
             ┌──────────────────────────┐
             │ project/learnings/       │
             │ RAW_LEARNINGS.md         │
             │ (append-only)            │
             └──────────────────────────┘
                            │
                            ▼
             ┌──────────────────────────┐
             │ Human Review Process     │
             │ • Verify correctness     │
             │ • Formalize to patterns  │
             │ → docs/patterns/*.md     │
             └──────────────────────────┘
```

---

## Why This Design

| Requirement | How Addressed |
|-------------|---------------|
| User can trigger reflection mid-conversation | `/record-learning` - skill has full conversation context when user invokes |
| Agent can initiate recording | Agent invokes `Skill` tool when it recognizes a learning moment |
| No "learning slop" | **User approval required for ALL recordings** - both paths present to user first |
| Reflection improves comprehension | Both paths explicitly reflect before presenting (not just "I know what I learned") |
| Simple implementation | One skill file, no Python scripts |
| Future-proof | Skills → slash commands merge coming; skill already works both ways |

---

## Potential Risks

| Risk | Mitigation |
|------|------------|
| Agents over-record | User approval required before any recording; user can veto |
| Learnings become stale | Human review process documented in file header |
| Entries are incorrect | Verification status checklist in each entry |
| User fatigue from approval prompts | Skill instructions guide agents to only propose genuinely reusable insights |

---

## Validation Approach

1. **Functional**: `/record-learning` reflects on conversation and captures learnings
2. **Integration**: Init command creates learnings directory and installs skill
3. **Format**: Entries follow template and are parseable
4. **Agent invocation**: Test that an agent can invoke skill via Skill tool

---

## Files to Create/Modify

| File | Action | Type |
|------|--------|------|
| `claude/skills/record-learning/SKILL.md` | Create | Tool-owned |
| `project_templates/RAW_LEARNINGS.md.template` | Create | User-owned template |
| `src/agentic_mbse/cli/__init__.py` | Modify | Add skill + learnings dir |

---

## Next Steps

After approval:
1. Create `claude/skills/record-learning/SKILL.md`
2. Create `project_templates/RAW_LEARNINGS.md.template`
3. Update `cmd_init()` to install skill and create learnings directory
4. Test both invocation paths (user and agent)

---

**Related Commands:**
- After design approval → `/_my_implement`
