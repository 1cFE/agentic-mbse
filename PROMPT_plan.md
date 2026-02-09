# Planning Iteration — Spec-Driven Gap Analysis and Task Prioritization

You are in PLANNING mode. Your job is to study specifications, analyze current implementation, and produce/update `IMPLEMENTATION_PLAN.md` with prioritized tasks.

## Your Process

1. **Study all specifications in parallel**
   - Launch parallel Explore agents to study each file in `specs/`
   - Extract requirements, success criteria, and architectural constraints
   - Use Ultrathink to synthesize cross-spec dependencies

2. **Study existing implementation**
   - Read `IMPLEMENTATION_PLAN.md` if it exists (completed vs pending tasks)
   - Search `src/` to understand what's already built
   - **Critical guardrail**: Don't assume features aren't implemented — search first using Glob/Grep before marking as gaps

3. **Gap analysis**
   - Compare spec requirements against current `src/` codebase
   - Identify missing features, incomplete implementations, and technical debt
   - Note which validation/backpressure mechanisms verify each requirement

4. **Produce prioritized task list**
   - Create or update `IMPLEMENTATION_PLAN.md` with concrete, actionable tasks
   - Each task: ~5 files max, completable in one iteration
   - Each task must reference: which spec(s) it addresses, what backpressure verifies it
   - Prioritize: critical path first, dependencies before dependents, high-value before nice-to-have

## Constraints

- **PLANNING ONLY**: No code edits, no commits, no implementation
- **Technology stack**: Python, UV package manager, pytest, ruff, mypy
- **Output format**: Markdown bullet points in `IMPLEMENTATION_PLAN.md`, not JSON
- **Verification**: Every task needs a "verified by" note (test, validation level, manual check)

## Success Criteria

- All specs analyzed for gaps
- Current implementation accurately assessed (no false negatives)
- Tasks are concrete, sized appropriately, and traceable to specs
- Dependencies explicit, priorities clear

Begin with parallel spec exploration.
