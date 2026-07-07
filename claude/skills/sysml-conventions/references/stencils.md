# SysML Code Stencils & Pattern Index

## Code Stencils

### Part Definition

```sysml
part def 'Component Name' {
    doc /*
    Description.

    **Source**: Authority document
    **Reference**: path/to/source
    **Last Updated**: YYYY-MM-DD
    */

    attribute mass : Real;
    attribute material : String;

    port input_port : ~'Port Type';
    port output_port : 'Port Type';
}
```

### Calc Definition

```sysml
calc def 'Calculation Name' {
    doc /*
    Description of calculation.

    **Source**: Reference document, Section X.Y
    **Reference**: path/to/source
    **Last Updated**: YYYY-MM-DD
    */

    in attribute input_a : Real;
    in attribute input_b : Real;
    return result : Real = input_a * input_b;   // inline expression -> auto-implemented
}
```

### Constraint Definition

```sysml
constraint def 'Constraint Name' {
    doc /*
    Description of constraint.

    **Source**: Requirement PR-XXX
    **Reference**: modeling_project/REQUIREMENTS.md
    **Last Updated**: YYYY-MM-DD
    */

    in attribute measured : Real;
    in attribute limit : Real;

    measured <= limit
}
```

### Connection Definition

```sysml
connection def 'Connection Name' {
    doc /*
    Description of connection type.

    **Source**: Interface specification
    **Reference**: path/to/source
    **Last Updated**: YYYY-MM-DD
    */

    end source_port : 'Port Type';
    end target_port : ~'Port Type';
}
```

## Pattern Documentation Index

All pattern docs are in the agentic-mbse `docs/patterns/` directory. Agents have read permissions via `.claude/settings.json`.

| Pattern Doc | Covers |
|-------------|--------|
| `definitions-usages.md` | Definition vs Usage distinction, decision tree |
| `expose-pattern.md` | EXPOSE pattern details, anti-patterns, EXPOSE surfacing |
| `plant-idiom.md` | Cross-part calc wiring: chains, retyping, sibling disambiguation |
| `adr002-calculations.md` | Calculation architecture, expression taxonomy, no-loops rule |
| `doc-comments.md` | Documentation standards, citation formats |
| `conditionals.md` | Conditional expression syntax |
| `constraints.md` | Constraint syntax and prefixes |
| `cross-file-binding.md` | Cross-file imports and bindings |
| `semantic-operators.md` | `=` vs `default :=` vs `:>>` vs `:>` |
| `syntax-reference.md` | 10 syntax patterns quick reference |
| `package-naming.md` | Multi-file organization, unique names |
| `mbse-concepts.md` | Allocation, interfaces, cost patterns |
| `common-mistakes.md` | Anti-patterns to avoid |
