# Autocompact Memory System — Spec Sheet

## Overview

Automatically captures conversation metadata before autocompaction, enabling selective post-hoc review and memory extraction.

## Components

| Component | Path | Type |
|-----------|------|------|
| PreCompact Hook | `.claude/hooks/precompact-capture.sh` | Bash script |
| Review Skill | `.claude/commands/review-compact.md` | Claude command |
| Hook Config | `.claude/settings.json` | JSON config |
| Output Directory | `.project/compacts/` | Storage |

## Workflow

```
[Context fills up]
        │
        ▼
[PreCompact hook fires]
        │
        ▼
[Metadata file created: {timestamp}-autocompact.md]
        │
        ▼
[Autocompaction proceeds]
        │
        ▼
[User runs /review-compact when ready]
        │
        ▼
[Memory file created: {timestamp}-memory.md]
[Metadata file updated with summary + link]
```

## File Formats

### Metadata File (`{timestamp}-autocompact.md`)

**Before review:**
```markdown
# Autocompact Capture

**Status:** pending
**Timestamp:** 2025-12-25T08:15:00-05:00
**Session ID:** abc123

## Transcript

\`\`\`
/home/user/.claude/projects/.../session-id.jsonl
\`\`\`

## First Message

> The first user message (truncated to 500 chars)...

## Memory

_Not yet reviewed. Run `/review-compact` to process._
```

**After review:**
```markdown
# Autocompact Capture

**Status:** reviewed
**Timestamp:** 2025-12-25T08:15:00-05:00
**Session ID:** abc123

## Transcript

\`\`\`
/home/user/.claude/projects/.../session-id.jsonl
\`\`\`

## First Message

> The first user message...

## Summary

Brief 1-2 sentence description of what the conversation was about.

## Memory

[20251225_081500-memory.md](./20251225_081500-memory.md)
```

### Memory File (`{timestamp}-memory.md`)

```markdown
# Memory: {Brief Title}

## Goal
What was the user trying to accomplish?

## Learnings
- Key insight 1
- Key insight 2

## Open Questions / Issues
- Unresolved item 1
- Unresolved item 2

## Confidence Level
High/Medium/Low — brief explanation

## Key Files
- path/to/file1.ts
- path/to/file2.ts
```

---

# Test Verification Criteria

## Test Procedure

1. Start a new Claude Code conversation in this project
2. Generate enough context to trigger autocompaction (ask for verbose explanations, read many files, etc.)
3. Wait for autocompaction to occur (status bar shows "Context Left Until Auto-Compact: 0%")
4. Return to this conversation for verification

## Verification Checklist

### ✅ Hook Execution

- [ ] **Metadata file exists** in `.project/compacts/`
  ```bash
  ls -la .project/compacts/*-autocompact.md
  ```

- [ ] **Filename format correct**: `{YYYYMMDD_HHMMSS}-autocompact.md`

- [ ] **Only triggered on auto** (not manual `/compact`)

### ✅ Metadata Content

- [ ] **Status is "pending"**
  ```bash
  grep "Status:" .project/compacts/*-autocompact.md
  ```

- [ ] **Transcript path is valid** and file exists
  ```bash
  # Extract path from metadata and check it exists
  ```

- [ ] **First message captured** (non-empty, recognizable)

- [ ] **Session ID present**

### ✅ /review-compact Skill

- [ ] **Skill is discoverable**: `/review-compact` appears in available commands

- [ ] **Default behavior works**: Running `/review-compact` with no args finds the pending file

- [ ] **Memory file created**: `{timestamp}-memory.md` exists after review

- [ ] **Metadata updated**: Status changed to "reviewed", summary added, memory link added

- [ ] **Memory content complete**: Has goal, learnings, questions, confidence sections

### ✅ Edge Cases

- [ ] **Multiple pending files**: `/review-compact` picks most recent

- [ ] **Explicit path works**: `/review-compact .project/compacts/specific-file.md`

- [ ] **No pending files**: Informative message when nothing to review

---

## Quick Verification Commands

```bash
# Check if any captures exist
ls .project/compacts/

# Count pending captures
grep -l "pending" .project/compacts/*-autocompact.md 2>/dev/null | wc -l

# View most recent capture
cat "$(ls -t .project/compacts/*-autocompact.md | head -1)"

# Check transcript exists for a capture
TRANSCRIPT=$(grep -A1 "## Transcript" .project/compacts/*-autocompact.md | grep "^/" | head -1)
ls -la "$TRANSCRIPT"
```

---

## Troubleshooting

| Issue | Possible Cause | Fix |
|-------|---------------|-----|
| No metadata file created | Hook not registered | Check `.claude/settings.json` |
| Hook error on stderr | Missing `jq` | Install jq: `apt install jq` |
| Empty first message | Transcript format changed | Check jq query in hook |
| `/review-compact` not found | Command not in `.claude/commands/` | Verify file exists |
