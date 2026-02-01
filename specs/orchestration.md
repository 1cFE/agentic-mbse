# Specification: Agent Orchestration Patterns

**Purpose:** Define standard workflows for integrating the comment system into human-agent collaboration loops.

## Requirements

**REQ-1: Human Review Loop**
- Human adds comments via CLI or VSCode
- Script queries unresolved comments via `comment list --json --status=open`
- Script passes comment data to agent via context
- Agent addresses comments and calls `comment_resolve` tool
- Human verifies resolutions, may reopen or add follow-ups

**REQ-2: Agent-Agent Review**
- Agent 1 generates artifact (plan, code, etc.)
- Agent 2 reviews using `comment_add` tool (no source modification)
- Human reviews Agent 2's comments, filters/prioritizes
- Agent 1 addresses remaining comments via `comment_reply` and `comment_resolve`

**REQ-3: Ralph Loop Integration**
- Ralph script reads specs, picks task, implements
- Before committing, Ralph calls `comment_list --all --status=open`
- If open comments exist on touched files, Ralph addresses them first
- Ralph resolves comments as part of commit (includes resolution in commit message)

**REQ-4: Git Hook Integration**
- Post-commit hook runs `comment reconcile --all --quiet`
- Hook reports orphaned comment count
- Hook fails commit if orphaned count > threshold (configurable)
- Optional: Pre-commit hook blocks if unresolved comments on staged files

**REQ-5: Continuous Feedback**
- Agent generates artifact in iterations (draft → review → final)
- Each iteration: human comments, agent revises, resolves comments
- Unresolved comments block merge/deployment
- `DECISIONS.md` captures rationale for future reference

## Acceptance Criteria

**AC-1:** Given bash script with `COMMENTS=$(comment list --json --status=open)`, when executed, then variable contains valid JSON array

**AC-2:** Given agent workflow where Agent 1 writes and Agent 2 reviews, when complete, then source file unchanged and sidecar contains review threads

**AC-3:** Given post-commit hook enabled, when commit introduces orphaned comment, then hook prints warning with orphan count

**AC-4:** Given Ralph loop with open comments on `PLAN.md`, when Ralph runs, then Ralph addresses comments before proceeding to implementation

**AC-5:** Given pre-commit hook configured, when attempting commit with unresolved comments on staged files, then commit is blocked with error message

**AC-6:** Given iteration workflow over 3 cycles, when complete, then DECISIONS.md contains decisions from all resolved threads

## Interfaces

**Inputs:**
- Orchestration script (bash, Python, Makefile)
- Agent conversation context
- Git hooks (pre-commit, post-commit)

**Outputs:**
- JSON data for agent consumption
- Exit codes for script control flow
- Git hook status (pass/fail)

**References:**
- `cli-interface.md`: `--json` output format
- `mcp-tools.md`: Agent tool calls
- `decision-log.md`: DECISIONS.md generation

## Constraints

**CON-1:** Orchestration MUST NOT require LLM for control flow
**CON-2:** All scripts MUST be idempotent (safe to re-run)
**CON-3:** Ralph loop MUST maintain deterministic behavior
**CON-4:** Git hooks MUST NOT break on missing git binary

## Out of Scope

- Workflow orchestration engine (use bash/make/Python)
- Agent-to-agent communication protocol (use shared sidecar files)
- Automatic comment prioritization (human decides)
- Comment approval/rejection workflow (resolve is binary)
- Integration with external issue trackers (Jira, Linear, etc.)
