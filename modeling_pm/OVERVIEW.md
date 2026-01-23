# Project Overview

**Project**: Coffee Maker Test Model
**Purpose**: Dogfooding agentic-mbse with a simple test subject
**Start Date**: 2026-01-09
**Status**: Active

---

## What We're Building

SysMLv2 models of a simple drip coffee maker that enable:

1. **Formal Integration** - Connect behavior (brewing process), structure (components), and physics (heat transfer, fluid flow)
2. **Validation Framework** - Constraint-based checking against physical laws
3. **Design Exploration** - Parametric studies (capacity, brew time, temperature)
4. **Workflow Testing** - Exercise the full MBSE command workflow

**Reference Implementation**: N/A (test subject for workflow validation)
**Validation Baseline**: Common sense physics constraints

---

## System Description

A simple drip coffee maker with these components:

**Parts:**
- Water reservoir (capacity: configurable)
- Heating element (power: configurable)
- Pump (flow rate: configurable)
- Brew basket (filter holder)
- Carafe (output container)
- Control panel (on/off, brew button)

**Behaviors:**
- Fill reservoir -> Heat water -> Pump to brew basket -> Drip into carafe
- Temperature control (maintain brew temp ~195-205F)
- Auto-shutoff after brewing complete

**Why this subject:**
- Familiar to most people
- 5-7 components (right complexity for testing)
- Clear data flows (water, heat, control signals)
- Natural requirements (brew time, temperature, capacity)

---

## Technical Approach

For MBSE methodology, see [MODELING_PROCESS.md](MODELING_PROCESS.md).
For SysML syntax and patterns, see [MODELING_GUIDE.md](MODELING_GUIDE.md).

---

## Current Status

**Active Work Item**: Initial setup
**Status**: Ready to start modeling
**Next Up**: Run /spec-model to define first feature

---

## Getting Started

1. Run `/spec-model coffee-maker-structure` to define requirements
2. Run `/design-model coffee-maker-structure` to design the model
3. Run `/implement-model coffee-maker-structure` to create SysML files

---

**Last Updated**: 2026-01-09
