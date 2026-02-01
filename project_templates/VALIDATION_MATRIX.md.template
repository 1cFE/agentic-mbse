# Validation Matrix

Verification criteria for the integrated system — checks that go beyond individual work items. Each entry defines what to verify, how to verify it, and what constitutes success.

## Verification Types

| Type | What it checks |
|------|---------------|
| reasonableness | Output is in expected ballpark (order-of-magnitude sanity) |
| baseline | Output matches a reference implementation or known-good value |
| physical | Conservation laws or physical constraints hold |
| relationship | Input/output vary in expected direction (sensitivity) |
| rollup | Aggregations are internally consistent |

## Verification Mechanisms

| Mechanism | How the check runs |
|-----------|--------------------|
| model | Verifiable by model inspection or `agentic-mbse validate` |
| test | Verifiable by pytest (may include codegen + simulation) |
| manual | Requires human judgment |

## Verification Registry

| ID | Description | Type | Mechanism | Expected | Tolerance | Source | Test | Status |
|----|-------------|------|-----------|----------|-----------|--------|------|--------|

<!-- Add rows as verification criteria are established. Example:
     | SV-001 | Total capital cost ballpark | reasonableness | test | $3B-$15B | range | engineering judgment | test_capital_cost_range | pending |
     | SV-002 | Energy balance conservation | physical | test | sum = total | ±0.1% | physics | test_energy_balance | pending | -->
