# Model Architecture

Structural decisions about how the domain is decomposed into model packages. These are the architectural choices that shape the model ecosystem — decisions that outlive any single work item and that new work must respect.

---

## Domain Decomposition

<!-- How is the physical system decomposed into model packages?
     What are the subsystem boundaries?
     What's shared (library/) vs. configuration-specific (designs/)?

     This section is prose — describe the high-level structure
     and the reasoning behind it. -->

---

## Package Organization

| Package | Purpose | Domain Scope | Dependencies |
|---------|---------|--------------|--------------|

<!-- Add rows as packages are created. Example:
     | library/foundation/ | Base types, units, materials | Cross-cutting | None |
     | library/calculations/ | Shared calc defs | Cross-cutting | foundation/ |
     | designs/{config}/ | Specific configuration | Full system | All library packages | -->

---

## Key Decisions

<!-- Decision format reference:

### AD-XXX: [Title]
**Decision**: [What was decided]
**Rationale**: [Why — what evidence or reasoning supports this]
**Date**: YYYY-MM-DD
**Status**: active | revised | superseded

-->
