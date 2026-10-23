# Documentation Standards

Standards for documenting SysML v2 model elements with doc comments, citations, and traceability.

## When to Use This Document

Reference this document when:
- Writing doc comments for definitions
- Citing sources for data and equations
- Establishing traceability to requirements
- Documenting assumptions and limitations

## Quick Reference

Every `part def`, `calc def`, `constraint def` requires a doc comment:

<!-- @tool-example -->
```sysml
part def 'Component Type' {
    doc /*
    Description of component.

    **Source**: Reference document
    **Reference**: path/to/source.pdf
    **Last Updated**: YYYY-MM-DD
    */
}
```

---

## Full Doc Comment Template

<!-- @tool-example -->
```sysml
part def 'Component Type' {
    doc /*
    [1. DESCRIPTION]
    Brief description of what this component represents

    [2. SOURCE/CITATION]
    **Source**: Document or standard this is based on
    **Reference**: path/to/source/document.pdf
    **Section**: Relevant section number

    [3. KEY DATA/RATIONALE]
    Key parameters and why they were chosen

    [4. ASSUMPTIONS/LIMITATIONS]
    **Assumptions**:
    - List assumptions made
    **Limitations**:
    - List known limitations

    [5. VALIDATION STATUS]
    **Validated**: How this was validated
    **Confidence**: High/Medium/Low

    [6. LAST UPDATED]
    **Last Updated**: YYYY-MM-DD
    */

    // ... element definition
}
```

---

## Required Documentation

### Major Elements (Required)

- All `part def`, `attribute def`, `calc def`, `constraint def`
- Requirements
- Key usages (especially top-level design instances)

### Attributes (Recommended)

```sysml
attribute major_radius : Length {
    doc /* Major radius of the torus, measured from center to tube centerline */
}
```

---

## Citation Patterns

### Physical Laws (No External Citation)

For well-known physical laws, a brief description is sufficient:

```sysml
constraint EnergyConservation {
    doc /* First law of thermodynamics - energy is conserved */
    P_in == P_out + P_stored
}
```

### Literature Citation

For data from papers, reports, or standards:

<!-- @tool-example -->
```sysml
calc def 'Empirical Scaling' {
    doc /*
    Empirical scaling law for system behavior

    **Citation**: Author et al. (Year)
    "Paper Title", Journal Name, Volume(Issue), Pages
    **DOI**: 10.xxxx/xxxxx
    **Local Copy**: data/documents/paper.pdf
    **Equation**: (7) on page 42
    */
    in x : Real;
    return y : Real = 0.5 * x;
}
```

### Codebase-Derived

For algorithms extracted from existing code:

<!-- @tool-example -->
```sysml
calc def 'Algorithm Implementation' {
    doc /*
    Algorithm description

    **Source**: Reference codebase
    **File**: path/to/source/file.py
    **Lines**: 14-72
    **Original References**: List original papers if applicable
    */
    in x : Real;
    return y : Real = 2.0 * x;
}
```

### Engineering Standards

For data from standards:

<!-- @tool-example -->
```sysml
part def 'Standard Component' {
    doc /*
    Component per industry standard

    **Standard**: ISO/ASME/IEEE XXXX-YYYY
    **Section**: 4.2.1
    **Table**: Table 3 - Material Properties
    */
}
```

---

## Minimal Documentation

For simple elements where full template is overkill:

<!-- @tool-example -->
```sysml
attribute efficiency : Real {
    doc /* Conversion efficiency, typical range 0.85-0.95 */
}

constraint PositiveMass {
    doc /* Physical constraint: mass must be positive */
    mass > 0
}
```

---

## Documentation in Designs vs Library

### Library (More Detail)

Definitions need comprehensive documentation:

<!-- @tool-example -->
```sysml
// library/components.sysml
part def 'Heat Exchanger' {
    doc /*
    Shell-and-tube heat exchanger for thermal transfer

    **Source**: Perry's Chemical Engineers' Handbook, 9th Ed.
    **Section**: Chapter 11 - Heat Transfer Equipment
    **Assumptions**:
    - Counter-current flow
    - Negligible heat loss to environment
    **Validated**: Cross-checked with vendor data
    **Last Updated**: 2026-01-15
    */
    // ...
}
```

### Designs (Less Detail)

Usages can have lighter documentation:

```sysml
// designs/plant/thermal.sysml
part primary_exchanger : 'Heat Exchanger' {
    doc /* Primary coolant heat exchanger - rated for 500 MW thermal */
    // ...
}
```

---

## Common Mistakes

### Missing doc comment entirely

<!-- @tool-example -->
```sysml
// BAD: No documentation
part def 'Component' {
    attribute property : Real;
}

// GOOD: Documented
part def 'Documented Component' {
    doc /* Component description with source */
    attribute property : Real;
}
```

### Missing source/reference

<!-- @tool-example -->
```sysml
// BAD: No traceability
calc def 'Scaling Law' {
    doc /* Calculates scaling factor */
    // Where does this formula come from?
    in x : Real;
    return factor : Real = 0.8 * x;
}

// GOOD: Traceable
calc def 'Traced Scaling Law' {
    doc /*
    Calculates scaling factor per empirical correlation

    **Source**: Smith et al. (2020), "Scaling Analysis"
    **Equation**: (12) on page 8
    */
    in x : Real;
    return factor : Real = 0.8 * x;
}
```

### Outdated documentation

<!-- @tool-example -->
```sysml
// BAD: No update date, may be stale
part def 'Component' {
    doc /* Component description */
}

// GOOD: Dated for freshness tracking
part def 'Dated Component' {
    doc /*
    Component description

    **Last Updated**: 2026-01-15
    */
}
```

---

## Validation Checklist

```markdown
Documentation Review:
- [ ] All definitions have doc comments
- [ ] Sources cited for data and equations
- [ ] Assumptions explicitly listed
- [ ] Confidence level indicated where relevant
- [ ] Last updated date present
- [ ] Local copies of references available (if applicable)
```

---

## Related Patterns

- [definitions-usages.md](definitions-usages.md) - What requires documentation
- [common-mistakes.md](common-mistakes.md) - Documentation anti-patterns
- [syntax-reference.md](syntax-reference.md) - Doc comment syntax

---

## Verification

Documentation is validated during model review, not by parser. However, the `doc /* */` syntax is verified:

**Test command:**
```bash
syside check <file.sysml>
```

---

*Last Updated: 2026-01-15*
