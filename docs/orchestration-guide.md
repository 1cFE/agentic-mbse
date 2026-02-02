# Comment System Orchestration Guide

**NOTE**: The scripts and hooks in this repository are **examples** demonstrating orchestration patterns. They may require customization for your specific workflow. Production deployments should adapt these examples to your infrastructure and testing requirements.

This guide demonstrates how to integrate the comment system into human-agent collaboration workflows.

## Overview

The comment system supports several orchestration patterns:

1. **Human Review Loop** - Humans add comments, agents address them
2. **Agent-Agent Review** - One agent reviews another's work via comments
3. **Ralph Loop Integration** - Ralph addresses open comments before implementing tasks
4. **Git Hook Integration** - Automatic reconciliation and validation
5. **Continuous Feedback** - Iterative review cycles with decision capture

## Quick Start

### Check Open Comments

```bash
# Check all open comments in project
./scripts/check_open_comments.sh

# Check open comments on specific file
./scripts/check_open_comments.sh PLAN.md
```

**Output:** JSON array of open threads (suitable for agent consumption)

### Agent-Agent Review Workflow

```bash
# Agent 2 reviews Agent 1's work
./scripts/agent_review_workflow.sh PLAN.md plan_v1.md "Review for completeness"
```

**Demonstrates:** REQ-2 (Agent-Agent Review) and AC-2 (source file unchanged, sidecar contains threads)

## Git Hooks

### Post-Commit Hook (Automatic Reconciliation)

**Installation:**

```bash
ln -s ../../claude/hooks/post-commit-reconcile.sh .git/hooks/post-commit
```

**Configuration:**

```bash
# Warn if > 5 orphaned comments after commit (default: 0)
git config comment-system.orphan-threshold 5

# Fail commit if orphans detected (default: false)
git config comment-system.fail-on-orphans true
```

**Behavior:**
- Runs `comment reconcile --all` after every commit
- Reports orphaned comment count (AC-3)
- Optionally fails if orphan count exceeds threshold (REQ-4)

### Pre-Commit Hook (Block Unresolved Comments)

**Installation:**

```bash
ln -s ../../claude/hooks/pre-commit-check-comments.sh .git/hooks/pre-commit
```

**Configuration:**

```bash
# Block commits with unresolved comments on staged files (default: false)
git config comment-system.block-on-unresolved true
```

**Behavior:**
- Checks staged files for open comments
- Blocks commit if unresolved comments found (AC-5)
- Lists files with open comments

**Override (one-time):**

```bash
git commit --no-verify
```

## Workflow Patterns

### Pattern 1: Human Review Loop (REQ-1)

```bash
# 1. Human adds comment
comment add PLAN.md -L 42:45 "This section needs more detail"

# 2. Agent queries open comments
COMMENTS=$(comment list --json --status=open)

# 3. Agent addresses comment and resolves
# (Via MCP tool or manual resolution)
comment resolve THREAD_ID --decision="Added detailed implementation steps"

# 4. Human verifies resolution
comment show THREAD_ID
```

### Pattern 2: Agent-Agent Review (REQ-2, AC-2)

```bash
# 1. Agent 1 generates artifact (already done, e.g., plan_v1.md)

# 2. Agent 2 reviews using comment_add tool
# (Simulated with CLI for demo)
./scripts/agent_review_workflow.sh PLAN.md plan_v1.md "Review for completeness"

# 3. Human reviews Agent 2's comments
comment list PLAN.md --status=open

# 4. Human filters/prioritizes

# 5. Agent 1 addresses remaining comments
comment reply THREAD_ID "Updated section 3 based on feedback"
comment resolve THREAD_ID --decision="Section 3 expanded with examples"
```

### Pattern 3: Ralph Loop Integration (REQ-3, AC-4)

```bash
# Ralph's workflow (simplified)
# 1. Ralph reads specs and picks task

# 2. Before implementing, check for open comments on files to be touched
COMMENTS=$(comment list --json --status=open --all)

# 3. If open comments exist on files Ralph will modify, address them first
if [ "$(echo $COMMENTS | jq length)" -gt 0 ]; then
    echo "Addressing open comments before proceeding..."
    # Ralph resolves comments as part of task
fi

# 4. Ralph implements task

# 5. Ralph includes comment resolutions in commit message
git commit -m "Task X: Implement feature Y

Resolved comments:
- THREAD_ID: [decision summary]
"
```

### Pattern 4: Continuous Feedback (REQ-5, AC-6)

```bash
# Iteration 1: Draft
agent generate_draft SPEC.md
human comment add draft.md -L 10:20 "Needs more examples"

# Iteration 2: Revise
agent address_comments draft.md
agent comment resolve THREAD_ID --decision="Added 3 examples"

# Iteration 3: Final
agent finalize draft.md
human verify_all_resolved

# Generate decision log for future reference
comment decisions  # Creates DECISIONS.md

# All decisions from resolved threads now captured
git add DECISIONS.md
git commit -m "Finalize draft with decision log"
```

## Exit Codes

All scripts follow consistent exit code conventions:

- **0**: Success
- **1**: User error (invalid arguments, file not found)
- **2**: System error (missing dependencies, git repo issues)

## Environment Variables

### NO_COLOR

Disable ANSI color codes in output:

```bash
NO_COLOR=1 comment list --all
```

### CI/CD Integration

For continuous integration:

```bash
# Check for unresolved comments (non-blocking)
if [ "$(comment list --json --status=open --all | jq length)" -gt 0 ]; then
    echo "Warning: Unresolved comments found"
fi

# Reconcile comments after merge
comment reconcile --all

# Generate decision log
comment decisions
git add DECISIONS.md
git commit -m "Update decision log [skip ci]" || true
```

## Idempotency (CON-2)

All scripts are idempotent and safe to re-run:

- `check_open_comments.sh`: Read-only query
- `agent_review_workflow.sh`: Creates single comment per run (safe to run multiple times)
- Git hooks: Use atomic operations, safe on retry

## Performance Considerations

- **Reconciliation**: ~50-100ms per thread with fuzzy matching
- **Project-wide queries**: < 1s for typical projects (< 1000 threads)
- **Git hooks**: Add ~100-500ms to commit time (depending on project size)

## Troubleshooting

### Git hook not running

Check symlink exists:

```bash
ls -l .git/hooks/post-commit
```

Should show: `.git/hooks/post-commit -> ../../claude/hooks/post-commit-reconcile.sh`

### Comment CLI not found in hooks

Ensure `comment` is in PATH or update hooks to use absolute path:

```bash
# In git hook, replace 'comment' with:
$(which comment)
```

### Hook fails on missing jq

Install jq for JSON parsing:

```bash
# Ubuntu/Debian
apt-get install jq

# macOS
brew install jq
```

## References

- [CLI Interface Specification](../specs/cli-interface.md)
- [MCP Tools Specification](../specs/mcp-tools.md)
- [Decision Log Specification](../specs/decision-log.md)
- [Orchestration Patterns Specification](../specs/orchestration.md)
