# Vendor Note Draft — SysIDE self-named-binding recursion (evaluation-time)

**Status:** DRAFT (F1, UPSTREAM-FINDINGS Item 12). Not sent. Do not contact Sensmetry
from this note — this records the finding for a future vendor report.

**Date:** 2026-07-06
**Source finding:** UPSTREAM-FINDINGS Item 8 (plant-fixtures), WI-014 toy fixture.

## The finding

A self-named binding — a calc input bound to a same-named reference, `in P = P`, where the
reference resolves to the calc's own input parameter — sends SysIDE into recursion **at
expression-evaluation time**, not at extraction time.

The distinction is the whole point of the note:

- **Extraction is finite and degenerate.** Parsing and structural extraction of the
  self-named shape terminate cleanly. The Item-8 probe ran extraction under `timeout 150`
  and exited 0 — no hang, no stack overflow. The extracted model is well-formed; the
  binding simply resolves the RHS to the calc's own parameter (a self-reference).
- **Evaluation is where the recursion lives.** The non-termination surfaces only when
  SysIDE is asked to *evaluate* the expression — the self-reference makes the value depend
  on itself, and the evaluator recurses.

So a tool that only extracts structure (as agentic-mbse's validators and codegen's
extractor do) never trips the recursion; a tool that evaluates expressions does. This is a
SysIDE evaluation-engine behavior, not a parser/extraction defect.

## Why it matters for us

agentic-mbse now catches the *modeling* error before it reaches any evaluator: the L2
self-named-binding check (Item 12, C1) FAILs a `in P = P` binding when the owning part has
no feature named `P` to cover it — a true dead-end. The covered cases (a same-named
attribute, an inherited attribute, or a sibling calc output) are the supported plant idiom
and are left alone. So our surface no longer produces the shape that would trip an
evaluator downstream.

## What a full vendor report would need (not done here)

- A minimal reproducer isolating the evaluation-time recursion (the WI-014 toy is the
  starting point).
- The exact SysIDE version and evaluation entry point that recurses.
- Expected behavior: a cycle/self-reference diagnostic instead of unbounded recursion.
- Coordination with Sensmetry.

## Trap coverage cross-reference (RAW_LEARNINGS)

The self-named-binding trap is mechanism **D** in the fusion-tea RAW_LEARNINGS traps
(SC-5). It is covered on the modeling side by check C1 (see the Item-12 close-out
traceability table in sysml-codegen).
