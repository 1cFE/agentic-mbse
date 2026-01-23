# SysML v2 Patterns

This directory contains reusable pattern documentation for SysML v2 modeling.

## Purpose

Patterns provide definitive syntax references and usage guidance for common SysML v2 constructs. The `modeling_pm/MODELING_GUIDE.md` provides quick-reference examples and links to these detailed pattern documents.

## Available Patterns

| Pattern | Description |
|---------|-------------|
| [definitions-usages.md](definitions-usages.md) | Core principle: separating reusable definitions from specific usages |
| [expose-pattern.md](expose-pattern.md) | EXPOSE pattern for cross-file access to calc outputs |
| [adr002-calculations.md](adr002-calculations.md) | Calculation architecture: calc defs in library, values in designs |
| [doc-comments.md](doc-comments.md) | Documentation standards and citation patterns |
| [conditionals.md](conditionals.md) | Conditional expression syntax (`if COND? VALUE else VALUE`) |
| [constraints.md](constraints.md) | Constraint syntax with assert/require/assume prefixes |
| [cross-file-binding.md](cross-file-binding.md) | Cross-file imports and attribute binding |
| [semantic-operators.md](semantic-operators.md) | `=` vs `default :=` vs `:>>` vs `:>` - critical for correct AST generation |
| [syntax-reference.md](syntax-reference.md) | Quick reference for common SysML v2 syntax patterns |
| [mbse-concepts.md](mbse-concepts.md) | Higher-level MBSE patterns: allocation, constraints, cost, interfaces |
| [package-naming.md](package-naming.md) | Package naming rules and multi-file organization |
| [common-mistakes.md](common-mistakes.md) | Anti-patterns and corrections for SysML v2 modeling |

## Adding New Patterns

When adding a new pattern document:

1. Create `{pattern-name}.md` in this directory
2. Include: syntax rules, examples, common mistakes, and verification notes
3. Update the MODELING_GUIDE.md.template to reference the new pattern
4. Add the pattern to the table above
