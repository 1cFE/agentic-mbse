# Source Index

This file tells MBSE commands where to find domain knowledge sources.
Commands read this file to discover what references are available for research and validation.

## Primary Sources

<!-- Add your domain sources below. Each source should have: -->
<!-- - **Type**: codebase | documentation | database | reference -->
<!-- - **Location**: Absolute or relative path, or URL -->
<!-- - **Use for**: What questions this source answers -->
<!-- - **Validation**: How it's used for validation (or N/A) -->

<!--
### Reference Implementation
- **Type**: codebase
- **Location**: /path/to/reference/code
- **Use for**: Understanding existing calculations, extracting parameters, formula verification
- **Validation**: Compare model outputs against this codebase calculations

### Technical Documentation
- **Type**: documentation
- **Location**: data/documents/technical_spec.pdf
- **Use for**: Physics formulas, design constraints, material properties
- **Validation**: N/A (reference only)

### Standards Database
- **Type**: database
- **Location**: https://standards.example.com/api
- **Use for**: Industry standards, safety requirements
- **Validation**: N/A
-->

(No primary sources configured yet - commands will ask for references as needed)

## How This File Is Used

MBSE commands (design-model, plan-model, implement-model, audit-models) read this file to:

1. **Discover** what reference sources exist for your domain
2. **Research** by exploring codebase sources and reading documentation
3. **Validate** by comparing model outputs against baseline sources

If this file is empty or missing, commands will:
- Ask you about relevant references
- Use web search for general information
- Proceed without baseline validation

## Adding New Sources

To add a source:
1. Add a new `### Source Name` heading under `## Primary Sources`
2. Include all four fields: Type, Location, Use for, Validation
3. Remove the commented examples above once you have real sources
4. Changes take effect on the next command run
