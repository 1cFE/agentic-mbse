# Spec: Specialized Documentation Agents

**Status:** Complete
**Owner:** Reid Westwood
**Created:** 2026-01-13
**Complexity:** MEDIUM
**Epic:** `.project/backlog/epic_documentation-discoverability.md` (P0-3)

---

## Business Goals

### Why This Matters

The current monolithic `sysmlv2-doc-analyzer` agent fails to help users discover standard library functions and other documentation because:

1. **Single corpus, many domains**: One agent tries to search KerML specs, SysML specs, and syside docs - often missing the right source
2. **No parallel research**: Task-model commands can only spawn one doc agent at a time
3. **KerML gap**: The agent doesn't even include the KerML spec in its search paths (where `sum`, `size`, etc. are defined)
4. **No validation capability**: When users ask "does this work?", there's no way to actually test the syntax

Splitting into specialized agents enables:
- **Focused expertise**: Each agent knows exactly where to search
- **Parallel research**: Spawn `kerml-expert` + `sysml-expert` simultaneously for comprehensive answers
- **Better coverage**: No documentation source is missed
- **Validation**: Dedicated agent can run `syside check` to verify syntax

### Success Criteria

- [ ] User can find `NumericalFunctions::sum` by asking kerml-expert
- [ ] User can get modeling patterns from sysml-expert
- [ ] User can get parser/tooling help from syside-expert
- [ ] User can validate syntax with sysmlv2-validator
- [ ] task-model commands can spawn multiple experts in parallel
- [ ] No agent ever says "X doesn't exist" - only "I couldn't find X in my corpus"

### Priority

P0 - This completes the documentation discoverability solution. INDEX.md infrastructure is done; agents need to use it effectively.

---

## Problem Statement

### Current State

`claude/agents/sysmlv2-doc-analyzer.md` is a monolithic agent that:

- Searches `{SYSML_DOCS_PATH}/*/full_document.md` (Parts 2, 3, guides)
- Searches `{SYSIDE_DOCS_PATH}/api/`
- Does NOT search KerML spec (where standard library is defined)
- Does NOT use INDEX.md files (new infrastructure)
- Has no validation capability

**Result**: Users spend hours searching for functions that exist but the agent can't find.

### Desired Outcome

Four specialized agents, each with:
- Focused documentation corpus
- INDEX.md-first search strategy
- "Never claim doesn't exist" rule
- Clear triggering conditions

| Agent | Corpus | Triggers On |
|-------|--------|-------------|
| `kerml-expert` | KerML spec + INDEX.md | Standard library, type system, language semantics |
| `sysml-expert` | SysML Parts 1-3 + INDEX.md | Modeling constructs, requirements, patterns |
| `syside-expert` | syside docs | Parser, automator, evaluation, tooling |
| `sysmlv2-validator` | syside CLI | Syntax validation, "does this work?" |

---

## Scope

### In Scope

1. **Create 4 new agent files** in `claude/agents/`:
   - `kerml-expert.md`
   - `sysml-expert.md`
   - `syside-expert.md`
   - `sysmlv2-validator.md`

2. **Each agent MUST include**:
   - Clear `description` for Task tool routing
   - Focused corpus with specific paths
   - INDEX.md-first search strategy (where applicable)
   - "Never claim doesn't exist" rule
   - Response format guidelines
   - Example queries it handles

3. **Update task-model commands** to reference specialized agents:
   - `design-model.md`
   - `implement-model.md`
   - `plan-model.md`
   - `spec-model.md`

4. **Deprecate old agent**:
   - Mark `sysmlv2-doc-analyzer.md` as deprecated
   - Keep for reference but remove from active use

### Out of Scope

- Changes to INDEX.md format or generation scripts
- Adding new documentation sources
- Vector search or embedding infrastructure
- Automatic agent routing (user/command chooses which agent)

### Edge Cases & Considerations

- **Cross-cutting questions**: "How do I use sum in a part definition?" needs both KerML (where sum is) and SysML (part patterns). Task-model commands should spawn both agents in parallel.
- **Ambiguous queries**: If unclear which agent to use, prefer spawning multiple. Better to get overlapping results than miss the answer.
- **Validation + research**: User asks "why doesn't my sum work?" - spawn both validator (check syntax) and kerml-expert (check import pattern).

---

## Requirements

### Functional Requirements

#### All Documentation Agents (kerml-expert, sysml-expert, syside-expert)

1. **FR-1**: Agent MUST read INDEX.md first to understand document structure before searching
2. **FR-2**: Agent MUST use targeted `Read` with offset/limit based on INDEX.md line numbers
3. **FR-3**: Agent MUST NEVER say "[X] doesn't exist in SysML v2" - only "I couldn't find [X] in my documentation corpus"
4. **FR-4**: Agent MUST cite source documents with section/line references in responses
5. **FR-5**: Agent MUST have a clear `description` field for Task tool routing
6. **FR-6**: Agent SHOULD search multiple terms/variants before concluding something isn't found

#### kerml-expert

7. **FR-7**: Agent MUST search `{SYSML_DOCS_PATH}/SysML_KerMLSpec/` corpus
8. **FR-8**: Agent MUST read `SysML_KerMLSpec/INDEX.md` for navigation
9. **FR-9**: Agent SHOULD check section 9.4 (Function Library) for function queries
10. **FR-10**: Agent SHOULD suggest import patterns when describing functions
11. **FR-11**: Agent description MUST mention: standard library, type system, language semantics, KerML

#### sysml-expert

12. **FR-12**: Agent MUST search Parts 1, 2, 3 specs: `SysML_Spec_v2_Part{1,2,3}/`
13. **FR-13**: Agent MUST read INDEX.md files for each spec
14. **FR-14**: Agent SHOULD prioritize Part 1 for language constructs, Part 2 for semantics, Part 3 for API
15. **FR-15**: Agent description MUST mention: modeling patterns, constructs, requirements, SysML

#### syside-expert

16. **FR-16**: Agent MUST search `{SYSIDE_DOCS_PATH}/` including api/, automator/ subdirectories
17. **FR-17**: Agent MAY use grep-based search (syside docs don't have INDEX.md)
18. **FR-18**: Agent description MUST mention: parser, evaluation, tooling, syside, automator

#### sysmlv2-validator

19. **FR-19**: Agent MUST be able to write temp files with SysML snippets
20. **FR-20**: Agent MUST run `syside check <file>` to validate syntax
21. **FR-21**: Agent MUST interpret common errors and suggest fixes:
    - "No Type named X" → suggest import statement
    - Parse errors → identify syntax issue
    - Resolution errors → explain what's missing
22. **FR-22**: Agent SHOULD clean up temp files after validation
23. **FR-23**: Agent MUST have tools: `Bash`, `Write`, `Read`
24. **FR-24**: Agent description MUST mention: validation, syntax check, "does this work"

#### Task-Model Command Updates

25. **FR-25**: Commands MUST reference specialized agents instead of `sysmlv2-doc-analyzer`
26. **FR-26**: Commands SHOULD spawn multiple agents in parallel for comprehensive research
27. **FR-27**: Commands MUST provide example prompts for each specialized agent

---

## Acceptance Criteria

### Core Functionality

- [ ] `kerml-expert` can answer "What functions are in NumericalFunctions?" by reading INDEX.md section 9.4.7
- [ ] `sysml-expert` can answer "How do I model a requirement constraint?" from Parts 1-3
- [ ] `syside-expert` can answer "How do I use the automator to evaluate expressions?"
- [ ] `sysmlv2-validator` can validate a snippet and report "No Type named 'sum' found"
- [ ] `sysmlv2-validator` suggests `private import NumericalFunctions::sum;` for the above error

### Agent Quality

- [ ] All agents have clear `description` fields that enable Task tool routing
- [ ] All documentation agents use INDEX.md-first strategy
- [ ] All agents include "never claim doesn't exist" rule
- [ ] All agents cite sources in responses

### Integration

- [ ] `design-model.md` updated with specialized agent examples
- [ ] `implement-model.md` updated with specialized agent examples
- [ ] `sysmlv2-doc-analyzer.md` marked as deprecated
- [ ] Parallel agent spawning works (single message, multiple Task calls)

---

## Technical Notes

### Agent File Structure

Each agent file follows the standard frontmatter format:

```markdown
---
name: agent-name
description: One-line description for Task tool routing. Include key trigger words.
tools: Read, Grep, Glob
---

[System prompt content]
```

### INDEX.md-First Search Strategy

```markdown
## Search Strategy

### Phase 1: Index Navigation

1. Read INDEX.md to understand document structure
2. Grep INDEX.md for relevant section summaries
3. Note line numbers for promising sections

### Phase 2: Targeted Reading

For each relevant section found:
1. Use `Read` with offset/limit based on INDEX.md line numbers
2. Read ~200-300 lines centered on the section
3. Extract relevant information

### Phase 3: Synthesis

1. Combine findings from multiple sections
2. Cite sources with file:line references
3. Provide actionable guidance
```

### Parallel Agent Usage Pattern

Task-model commands should demonstrate parallel spawning:

```python
# Spawn multiple agents in a SINGLE message for parallel execution
Task(
    description="Find sum function definition",
    prompt="What is the signature of the sum function and how do I import it?",
    subagent_type="kerml-expert"
)
Task(
    description="Find sum usage patterns",
    prompt="Show me examples of using aggregate functions in part definitions",
    subagent_type="sysml-expert"
)
```

### Validator Workflow

```python
# sysmlv2-validator process
1. Write snippet to temp file:
   Write("/tmp/validate_snippet.sysml", user_code)

2. Run validation:
   Bash("syside check /tmp/validate_snippet.sysml")

3. Interpret results:
   - Success → "Syntax is valid"
   - "No Type named X" → "Add: private import Package::X;"
   - Parse error → Identify line and issue

4. Clean up:
   Bash("rm /tmp/validate_snippet.sysml")
```

### Common Error Interpretations (for validator)

| Error Pattern | Interpretation | Suggested Fix |
|--------------|----------------|---------------|
| `No Type named 'sum'` | Missing import | `private import NumericalFunctions::sum;` |
| `No Type named 'size'` | Missing import | `private import SequenceFunctions::size;` |
| `No Type named 'Real'` | Missing import | `private import ScalarValues::Real;` |
| `Syntax error at line N` | Parse failure | Check syntax at line N |
| `Cannot resolve reference` | Import or spelling issue | Verify package/name spelling |

---

## Agent Descriptions (for Task tool)

These descriptions appear in the `description` frontmatter field and are used by the Task tool for routing:

### kerml-expert
```
KerML language expert. Use for standard library functions (sum, size, collect, etc.),
type system questions, language semantics, and KerML specification lookups.
Has access to KerML spec with INDEX.md navigation.
```

### sysml-expert
```
SysML v2 modeling expert. Use for modeling patterns, part/attribute/port definitions,
requirements modeling, constraint patterns, and SysML specification lookups.
Has access to SysML Parts 1-3 specs with INDEX.md navigation.
```

### syside-expert
```
SysIDE tooling expert. Use for parser usage, expression evaluation, automator workflows,
syside Python API, and tooling integration questions.
Has access to syside documentation.
```

### sysmlv2-validator
```
SysML v2 syntax validator. Use to check if code is valid, debug parse errors,
or verify snippets work. Runs actual syside parser and interprets errors.
Can suggest imports for "No Type named X" errors.
```

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_documentation-discoverability.md`
- **Research:** `.project/research/20260112-064217_sysmlv2-agent-discoverability-failure.md`
- **Chunking Research:** `project/research/20260112-222249_chunking-indexing-strategy.md`
- **Current Agent:** `claude/agents/sysmlv2-doc-analyzer.md` (to be deprecated)
- **Task-Model Commands:** `claude/commands/{design,implement,plan,spec}-model.md`

---

## Design Decisions

1. **Agent naming**: Use `-expert` suffix (e.g., `kerml-expert`) - shorter and clearer than `-doc-analyzer`

2. **Validator temp file location**: Use `/tmp/` - standard, no project pollution

3. **Deprecation strategy**: Move `sysmlv2-doc-analyzer.md` to `claude/agents/deprecated/` folder

---

**Next Steps:** After approval, proceed to implementation (create agent files, update commands)
