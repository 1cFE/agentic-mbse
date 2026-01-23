---
date: 2026-01-12T22:22:49+00:00
researcher: Claude
topic: "Chunking and Indexing Strategy for SysML v2 Specifications"
tags: [research, documentation, chunking, indexing, rag, agents]
status: complete
last_updated: 2026-01-12
---

# Research: Chunking and Indexing Strategy for SysML v2 Specifications

**Date**: 2026-01-12
**Researcher**: Claude
**Research Type**: Architecture / Tool Evaluation / Strategy

## Research Questions

a) What are the best known methods for document chunking and indexing for AI agent retrieval?
b) How do the tools mentioned in the spec (Chonkie, md2chunks, LlamaIndex, Faiss) compare?
c) What subagent architecture could effectively navigate multi-document technical specs?
d) Is the indexing strategy in the epic sound, or should we rethink it?

## Summary

- **Chunking strategy**: Hierarchical markdown splitting with breadcrumb context is the right approach for technical specs. The spec's vision is sound, but needs refinement on implementation details.
- **Tool recommendation**: **LangChain's MarkdownHeaderTextSplitter** is the simplest path - it does exactly what we need (header-aware splitting with breadcrumb metadata) without extra dependencies.
- **Chonkie/md2chunks evaluation**: Both have gaps - Chonkie doesn't propagate header context automatically, md2chunks is unmaintained (2 stars). Neither is ideal out-of-box.
- **Subagent architecture**: A two-tier approach (routing agent + specialized agents) is recommended, but can be implemented incrementally starting with improved prompts.
- **Epic critique**: The core strategy is correct, but P0-2 (Standard Library Quick Reference) should be the FIRST priority - it solves the immediate problem without complex infrastructure.
- **Key insight**: For grep-based retrieval (Claude Code's approach), we don't need vector embeddings. We need better **indexes** (human-readable TOC files) and **larger chunks** (512-1024 tokens).

---

## Detailed Findings

### 1. Best Practices for Technical Document Chunking

#### 1.1 Chunking Strategies Comparison

| Strategy | Best For | SysML Spec Fit |
|----------|----------|----------------|
| **Header-based (Hierarchical)** | Structured docs with clear sections | **Excellent** - specs have deep header hierarchies |
| **Semantic (embedding-based)** | Unstructured text | Poor - adds complexity without benefit for structured docs |
| **Fixed-size token** | General text | Poor - breaks mid-section, loses context |
| **Recursive character** | Large sections needing subdivision | Good secondary pass for oversized sections |

**Recommendation**: Header-based as primary, recursive as secondary for sections exceeding target size.

#### 1.2 Optimal Chunk Sizes

From research on retrieval methods:

| Retrieval Type | Optimal Size | Our Use Case |
|---------------|--------------|--------------|
| Grep/keyword | 512-1024 tokens | **Primary** - Claude Code uses grep |
| Vector/semantic | 256-512 tokens | Future enhancement |
| Hierarchical parent | 1024-2048 tokens | Context expansion |
| Hierarchical child | 128-256 tokens | Fine-grained matching |

**For our grep-based workflow**: Larger chunks (512-1024) work better because each grep match includes more context. The spec's target of 256-512 tokens is optimized for vector search - we should increase to 512-1024 for grep-primary retrieval.

#### 1.3 Context Preservation: The Breadcrumb Pattern

The spec correctly identifies breadcrumb context as critical. State-of-the-art approaches:

**Option A: Prepend breadcrumb to chunk content**
```markdown
[SysML KerML Spec > 9. Standard Library > 9.2 Numerical Functions]

The NumericalFunctions package provides mathematical operations...
```
- Pros: Searchable, no special handling needed
- Cons: Increases chunk size, redundant text

**Option B: YAML frontmatter metadata**
```yaml
---
source: SysML_KerMLSpec
section: "9.2"
breadcrumb: ["9. Standard Library", "9.2 Numerical Functions"]
parent_summary: "Standard library definitions for mathematical types and operations"
---
The NumericalFunctions package provides mathematical operations...
```
- Pros: Structured, machine-parseable, can be filtered
- Cons: Requires parser support in retrieval

**Recommendation**: Use **Option A** (prepended breadcrumb) for grep-friendliness, plus Option B metadata for future extensibility.

#### 1.4 Code Block and Table Handling

Critical for SysML specs which contain both extensively:

- **Code blocks**: Must be atomic. Never split mid-block. Keep with preceding explanation.
- **Tables**: Must be atomic. Include table caption/header with every table chunk.
- **Cross-references**: Store section→chunk mapping for "see Section X" resolution.

---

### 2. Tool Evaluation

#### 2.1 Chonkie

**What it does well:**
- Lightweight (9.7MB)
- Multiple chunking strategies (recursive, token, semantic, code, table)
- `TableChunker` preserves table headers
- `CodeChunker` uses AST for code-aware splitting
- Active development, good documentation

**What it's missing:**
- **No automatic breadcrumb propagation** - `RecursiveChunker` splits on headers but doesn't capture parent hierarchy in chunk metadata
- **No frontmatter output** - Chunks are dataclass objects, need post-processing
- Must use `MarkdownChef` + multiple chunkers for mixed content

**Verdict**: Good foundation, but requires custom wrapper to add breadcrumb context.

#### 2.2 md2chunks

**What it does:**
- Context-enriched markdown chunking
- LlamaIndex-inspired TextNode structure
- Stores header hierarchy in metadata

**Limitations:**
- **Not on PyPI** - requires cloning repo
- **2 stars, 2 contributors** - effectively unmaintained
- Minimal documentation
- `main.py` is a stub

**Verdict**: Not suitable for production use. Concept is right, implementation is immature.

#### 2.3 LangChain MarkdownHeaderTextSplitter

**What it does:**
```python
from langchain_text_splitters import MarkdownHeaderTextSplitter

headers_to_split_on = [
    ("#", "Header 1"),
    ("##", "Header 2"),
    ("###", "Header 3"),
]
splitter = MarkdownHeaderTextSplitter(headers_to_split_on)
splits = splitter.split_text(markdown_doc)

# Result: Document objects with breadcrumb metadata
# Document(page_content='Content here...',
#          metadata={'Header 1': 'Spec', 'Header 2': 'Standard Lib', 'Header 3': 'Numerical'})
```

**Strengths:**
- **Built-in breadcrumb propagation** via metadata dict
- Well-documented, widely used
- Options: `strip_headers`, `return_each_line`
- Can chain with `RecursiveCharacterTextSplitter` for oversized sections

**Weaknesses:**
- Doesn't preserve code blocks automatically (need `MarkdownTextSplitter` variant)
- Part of larger LangChain ecosystem (heavier dependency)

**Verdict**: **Best fit for our needs**. Header hierarchy metadata is exactly what we need.

#### 2.4 LlamaIndex

**Relevant components:**
- `MarkdownNodeParser` - splits on headers, tracks path
- `HierarchicalNodeParser` - parent-child relationships
- `AutoMergingRetriever` - small-to-big retrieval
- `SimpleVectorStore` - JSON file persistence

**Strengths:**
- Most sophisticated hierarchy handling
- Built-in small-to-big retrieval
- Multi-document routing (`SubQuestionQueryEngine`)
- File-based persistence (no database needed)

**Weaknesses:**
- Heavy framework - overkill for grep-based retrieval
- Designed around vector search, not keyword search
- Learning curve for custom integration

**Verdict**: Good for future vector-enhanced retrieval. Overkill for current grep-based approach.

#### 2.5 Tool Recommendation Summary

| Need | Best Tool | Rationale |
|------|-----------|-----------|
| **Quick win (now)** | LangChain MarkdownHeaderTextSplitter | Does exactly what we need, minimal code |
| **Custom solution** | Python + regex | Full control, no dependencies, can optimize for grep |
| **Future vector search** | LlamaIndex | Best hierarchy handling for embedding-based retrieval |
| **Don't use** | md2chunks | Unmaintained |
| **Consider later** | Chonkie | Good for code/table handling if needed |

---

### 3. Subagent Architecture

#### 3.1 Current State

Single agent (`sysmlv2-doc-analyzer`) handles all SysML questions:
- Tools: Read, Grep, Glob
- Strategy: Grep first, then targeted Read with offset/limit
- Corpus: `{SYSML_DOCS_PATH}/*/full_document.md`, `{SYSIDE_DOCS_PATH}/api/`

**Problems:**
1. No standard library in corpus (the root cause of the `sum` failure)
2. Agent says "doesn't exist" when it can't find something
3. Single agent handles too many query types
4. No validation capability (can't test if code works)

#### 3.2 Proposed Architecture (from Epic P2-1)

| Agent | Purpose | Corpus |
|-------|---------|--------|
| `sysmlv2-concepts` | Language semantics, modeling patterns | Specs, guides |
| `sysmlv2-library` | Standard library lookup | .kerml files, quick ref |
| `sysmlv2-validator` | Syntax validation | syside CLI |
| `sysmlv2-examples` | Working code examples | Test files |

**My assessment**: This is the right direction, but **premature optimization**. We should:

1. **Phase 1**: Fix the corpus (add KerML spec ✓, add standard library reference)
2. **Phase 2**: Fix the prompts (check reference first, never say "doesn't exist")
3. **Phase 3**: Add validation agent (test snippets with syside)
4. **Phase 4**: Split into specialists (only if Phase 1-3 insufficient)

#### 3.3 Recommended Two-Tier Architecture

If we do split agents, use a **router pattern**:

```
User Query
    ↓
┌─────────────────────────┐
│  Router (Main Agent)    │ ← Uses keyword matching + LLM to route
│  "What kind of query?"  │
└─────────────────────────┘
    ↓
┌───────────────────────────────────────────────────────────────────┐
│ Library Query?     │ Pattern Query?   │ Validation Query?         │
│     ↓              │      ↓           │      ↓                    │
│ sysmlv2-library    │ sysmlv2-concepts │ sysmlv2-validator         │
│ (Quick ref +       │ (Specs, guides,  │ (syside CLI,              │
│  .kerml files)     │  examples)       │  error interpretation)    │
└───────────────────────────────────────────────────────────────────┘
```

**Routing heuristics:**
- Contains function name (sum, size, collect) → library agent
- Contains "how do I model", "pattern for" → concepts agent
- Contains "does this work", "error", "validate" → validator agent

#### 3.4 Index-First Architecture (Alternative)

Rather than multiple agents, use **structured indexes** that one agent can navigate:

```
docs/sysmlv2/
├── MASTER_INDEX.md           ← Entry point for all queries
│   ├── Which spec for what
│   ├── Standard library summary
│   └── Links to section indexes
├── STANDARD_LIBRARY_REFERENCE.md  ← Quick lookup for functions
├── SysML_KerMLSpec/
│   ├── INDEX.md              ← Section-level TOC with summaries
│   └── full_document.md
├── SysML_Spec_v2_Part1/
│   ├── INDEX.md
│   └── full_document.md
└── ...
```

**Agent strategy update:**
1. Read `MASTER_INDEX.md` first (always)
2. For function queries, check `STANDARD_LIBRARY_REFERENCE.md`
3. Use section indexes to navigate to relevant chunks
4. Read targeted sections with offset/limit

**This is lower implementation cost** than multiple agents and may be equally effective.

---

### 4. Critique of the Epic's Indexing Strategy

#### 4.1 What the Epic Gets Right

1. **Root cause analysis is correct**: The failure was a corpus/indexing problem, not an agent strategy problem
2. **Quick reference first**: Creating `STANDARD_LIBRARY_REFERENCE.md` is the right immediate fix
3. **Breadcrumb/stack pattern**: The frontmatter schema is well-designed
4. **Multi-tier index concept**: Document → Section → Chunk navigation is sound
5. **"Never say doesn't exist"**: Critical prompt fix

#### 4.2 What Should Be Reconsidered

**Issue 1: Chunk size targets (256-512 tokens)**

The spec targets 256-512 tokens, which is optimized for vector/embedding search. For grep-based retrieval:
- **Larger chunks are better** (512-1024 tokens)
- Each grep match returns one location - want more context per match
- Smaller chunks mean more files to search through

**Recommendation**: Target 512-1024 tokens for grep-primary retrieval. Can add smaller child chunks later for vector search.

**Issue 2: Over-engineering the chunking pipeline**

The spec describes:
- Markdown Chunker
- Frontmatter Generator
- Index Generator
- Vector Search Foundation

This is a lot of infrastructure. Simpler alternative:

```python
# All we really need for Phase 1
from langchain_text_splitters import MarkdownHeaderTextSplitter

splitter = MarkdownHeaderTextSplitter([("#", "h1"), ("##", "h2"), ("###", "h3")])
chunks = splitter.split_text(full_document)

# Write chunks with breadcrumb as markdown files
for i, chunk in enumerate(chunks):
    breadcrumb = " > ".join(chunk.metadata.values())
    with open(f"chunks/{i:03d}.md", "w") as f:
        f.write(f"[{breadcrumb}]\n\n{chunk.page_content}")
```

**Recommendation**: Start with 50 lines of Python, not a full chunking framework.

**Issue 3: P0-2 (Quick Reference) should be P0-0**

The epic lists PDF extraction (P0-1) before Quick Reference (P0-2). But:
- PDF extraction is done ✓
- Quick Reference solves the immediate user problem
- Quick Reference can be created **manually in 1-2 hours** from .kerml files
- The chunking infrastructure helps future discoverability, but doesn't solve the `sum` problem directly

**Recommendation**: Create `STANDARD_LIBRARY_REFERENCE.md` FIRST. It's the minimum viable fix.

**Issue 4: Deferred vector search may never be needed**

The spec designs for "future vector search integration" but:
- Claude Code uses grep, not vector search
- Structured technical docs with clear hierarchies work well with keyword search
- Vector search adds complexity (embeddings, storage, similarity thresholds)
- Anthropic's own research shows grep-based retrieval works well for structured content

**Recommendation**: Design for keyword search first. Only add vector search if grep proves insufficient.

**Issue 5: Section consolidation rules unclear**

The spec notes "very short sections" as an edge case but doesn't define consolidation rules:
- When to merge with siblings?
- When to merge with parent?
- Minimum chunk size?

**Recommendation**: Define explicit rules:
- Sections < 100 tokens: merge with next sibling
- If no sibling: merge with parent
- Maximum depth: 4 levels of hierarchy (beyond that, flatten)

#### 4.3 Suggested Epic Revisions

**Priority reorder:**

| Original | Revised | Rationale |
|----------|---------|-----------|
| P0-1: Extract PDFs | P0-0 ✓ DONE | Already complete |
| P0-2: Quick Reference | **P0-1** | Immediate user fix |
| P0-3: Update Prompts | P0-2 | Quick win after reference exists |
| P1-1: Auto-generate index | P1-1 | Same priority |
| P1-2: Validation Agent | **P0-3** | High impact, low effort |
| P1-3: .kerml to corpus | P1-2 | After quick ref |
| P2-1: Split agents | P2-1 or **DROP** | May not be needed |
| P2-2: PDF chunking | **P1-3** | Simpler than thought |
| P3-1: Coverage dashboard | P3-1 | Nice to have |

**New item to add:**

> **P0-0.5: Create MASTER_INDEX.md**
> Single entry-point file that tells the agent which document to search for what. This is the "routing layer" without agent splitting.

---

### 5. Recommended Implementation Path

#### Phase 1: Quick Wins (1 day)

1. **Create STANDARD_LIBRARY_REFERENCE.md manually**
   - Read NumericalFunctions.kerml, SequenceFunctions.kerml, ControlFunctions.kerml
   - Document function signatures, imports, examples
   - This solves the immediate `sum` problem

2. **Create MASTER_INDEX.md**
   - Document routing guide (which spec for what)
   - Section summaries
   - Links to key sections

3. **Update sysmlv2-doc-analyzer prompt**
   - Check STANDARD_LIBRARY_REFERENCE.md first for function queries
   - Check MASTER_INDEX.md for routing
   - Never say "doesn't exist"

#### Phase 2: Basic Chunking (1-2 days)

4. **Create simple chunk script**
   - Use LangChain MarkdownHeaderTextSplitter
   - Output: markdown files with breadcrumb headers
   - Target: 512-1024 tokens per chunk

5. **Create section indexes**
   - One INDEX.md per spec document
   - Section number, title, summary, chunk file link
   - Agent uses to navigate

6. **Add sysmlv2-validator agent**
   - Test snippets with `syside check`
   - Interpret errors, suggest imports
   - High impact for user experience

#### Phase 3: Automation (optional, 1-2 days)

7. **Script to auto-generate reference from .kerml**
   - Parse function definitions
   - Generate markdown tables
   - Run on syside updates

8. **Script to auto-generate section indexes**
   - From chunk files
   - Include token counts, key terms

#### Phase 4: Evaluate and Iterate

9. Test with real user queries
10. If grep retrieval insufficient, evaluate vector search
11. If single agent overloaded, consider splitting

---

## Architecture Insights

### Why Grep-First Makes Sense for Technical Specs

1. **Structured documents have predictable terminology**: SysML specs use consistent terms like "PartDefinition", "AttributeUsage". Keyword search works.

2. **Hierarchical organization aids navigation**: Section 7.3.2 is always about the same topic. Good indexes make navigation deterministic.

3. **Vector search excels at semantic similarity, not structure**: "How do I add numbers?" might not match "NumericalFunctions::sum" semantically, but keywords work.

4. **Grep is transparent and debuggable**: When agent fails, you can see exactly what it searched. Vector similarity is a black box.

5. **No embedding infrastructure needed**: Simpler system, fewer failure modes.

### When to Add Vector Search Later

Consider vector search if:
- Users frequently ask questions using non-standard terminology
- Grep returns too many results to filter effectively
- Semantic clustering would help (finding "similar" patterns)
- Performance becomes an issue with very large document sets

---

## Feasibility Assessment

### Can we build a general chunking solution?

**Yes, but with caveats:**

- **General markdown chunker**: Straightforward with LangChain or custom script
- **Breadcrumb metadata**: Easy to implement
- **Index generation**: Simple script

**Where it gets spec-specific:**
- Summary generation: Manual or LLM-based (expensive, variable quality)
- Optimal chunk boundaries: Depends on document structure
- Cross-reference handling: Spec-specific syntax

**Recommendation**: Build general chunker + index generator. Keep summary/cross-reference handling manual for now.

### Should we customize for KerML specifically?

**Argument for customization:**
- KerML spec has predictable structure (Chapters, Sections, Clauses)
- Standard library definitions follow consistent patterns
- We know exactly what users need (function signatures, imports)

**Argument for generalization:**
- We have 4+ specs to process (KerML, Part1, Part2, Part3)
- Future specs will have similar structure
- One-time investment enables scale

**Verdict**: Build general solution, but **start with KerML as the test case**. If it works for KerML, it works for others.

---

## Open Questions

1. **Should we copy .kerml files into docs/ or reference them in syside package?**
   - Copying: version-controlled, always available
   - Referencing: stays in sync with syside updates

2. **What's the right summary granularity?**
   - Per-section summaries are labor-intensive
   - Could generate with LLM (quality varies)
   - Could skip summaries initially, add based on need

3. **How do we handle spec updates?**
   - PDFs rarely change
   - syside library might change on version updates
   - Need re-chunking process

4. **Is LangChain acceptable as a dependency?**
   - Alternative: 50 lines of custom Python
   - LangChain is mature but large

---

## Recommendations Summary

| Recommendation | Priority | Effort |
|----------------|----------|--------|
| Create STANDARD_LIBRARY_REFERENCE.md manually | **P0** | 2 hours |
| Create MASTER_INDEX.md routing guide | P0 | 1 hour |
| Update agent prompt (check reference first, never "doesn't exist") | P0 | 30 min |
| Add sysmlv2-validator agent | P0 | 4 hours |
| Build simple chunker with LangChain or custom Python | P1 | 4-8 hours |
| Create section-level INDEX.md files | P1 | 2-4 hours |
| Script to auto-generate library reference | P2 | 4-6 hours |
| Evaluate agent splitting vs single agent with better routing | P2 | After Phase 2 |
| Add vector search | P3 | Only if grep insufficient |

---

## Conclusion

The epic's core strategy is sound: the problem is corpus/indexing, not agent architecture. The recommended changes are:

1. **Prioritize the quick reference** - It directly solves the user problem
2. **Increase chunk size** - 512-1024 tokens for grep-based retrieval
3. **Start simple** - LangChain splitter or 50 lines of Python, not a framework
4. **Add routing index** - MASTER_INDEX.md before agent splitting
5. **Defer vector search** - Grep works for structured technical docs
6. **Build general, test specific** - Generic chunker, KerML as first test case

The fusion-tea team's hours of searching for `sum` should never happen again. The fix is simple: a reference file and a prompt update. The chunking infrastructure is valuable for long-term maintainability, but it's not the critical path to solving the immediate problem.

---

## Code References

- Epic: `.project/backlog/epic_documentation-discoverability.md`
- Spec: `.project/active/markdown-chunker-indexer/spec.md`
- Plan: `.project/active/extract-missing-pdf-specs/plan.md`
- Research: `.project/research/20260112-064217_sysmlv2-agent-discoverability-failure.md`
- Agent: `claude/agents/sysmlv2-doc-analyzer.md`
- Standard library source: `.venv/lib/python3.12/site-packages/syside/sysml.library/Kernel Libraries/`

---

**Prepared for**: agentic-mbse development team
**Action requested**: Review recommendations, approve revised priority order, begin Phase 1 implementation
