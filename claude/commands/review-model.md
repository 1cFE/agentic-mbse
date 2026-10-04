---
name: review-model
description: Review a design document against project requirements, architecture decisions, and SysML conventions
skills: [sysml-conventions, model-validation, project-structure, requirements-tracking]
allowed-tools: [Read, Grep, Glob, Bash, Task, Write, Edit, AskUserQuestion]
user-invocable: true
---

# Review Model

Use the assigned scope and “Review Brief and Context Limits” in `modeling_project/MODELING_PROCESS.md`. For a focused question, read only the supplied entry sections and primary evidence within the brief’s budget; return missing evidence before expanding. Apply the broader checks below only to claims in scope. Save a short finding in the existing work record or requested evidence path; a separate report is useful for a substantive assessment.

Independently challenge a design where an architectural or integration risk warrants it. Read the relevant requirements, design, and primary evidence within the assigned scope; a substantive review can use `work/active/{WI-XXX}_{name}/review.md`.

Run this critique when requested or triggered by the canonical process. Use a fresh non-author context without inherited author conversation. One reviewer owns the assessment and may consult a specialist for a concrete uncertainty.

## Examine the Design's Meaning

Start with the intended outcome and supported use, then inspect the proposed design. Focus on consequential questions:

- Do the physical structure, operating assumptions, and analysis describe the same system?
- Are relevant quantities and interfaces owned consistently, including downstream effects?
- Do the cited sources and chosen approximations support the intended use?
- Would the proposed checks expose the likely failure, or only confirm the author's chosen representation?

Apply relevant project requirements, architecture decisions, and conventions. Use existing tooling evidence for mechanical checks; do not repeat it without a reason. Research or prototype results demonstrate only what they actually exercised.

## Report What Matters

Keep findings specific: issue, location/evidence, consequence, and suggested resolution. Distinguish material defects and unresolved premises from optional improvements. The owner or coordinator dispositions findings under existing decision authority; route reserved choices to the owner.

Use the existing review metadata:

```yaml
---
Verdict: pass | concerns | fail
Created: <YYYY-MM-DD>
Related Artifacts:
  Design: ./design.md
  Spec: ./spec.md
---
```

Include the verdict, evidence boundaries, findings and dispositions, and any necessary next step. A failure needs a concrete correction or unresolved decision. Recheck material repairs and their affected dependencies; do not restart the entire review for an objectively verified minor edit. This review establishes design readiness, not implementation completion.
