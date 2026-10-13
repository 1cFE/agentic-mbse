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

### Widget Coil Note
- **Type**: url
- **Location**: knowledge/sources/widget_coil_note/
- **Use for**: Synthetic winding-pack geometry; exercises the index writer.
- **Validation**: Compare against the fixture page itself.
- **Caveat**: A test fixture.

#### Extended Metadata
- **Source URL**: http://127.0.0.1:8000/utf8.html
- **Source ID**: 99d8ff05c9631996c0d62b5c3ac53be01bcbdc92d76e9a18ad95096080336bed
- **Raw SHA256**: 99d8ff05c9631996c0d62b5c3ac53be01bcbdc92d76e9a18ad95096080336bed
- **Raw Artifact SHA256**: 17a9d6515507487f7b2509a58186f7b692c8f5eb84c42feb3baafd3a7f5d9eb9
- **Extracted Path**: knowledge/sources/widget_coil_note/
- **Extract SHA256**: 2e139b97b5e2558ca00fd80b805f764b5cb9e548e1dd2c8bc423a5276a59082c
- **Date Added**: 2026-10-12

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
