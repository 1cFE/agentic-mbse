// Item-4 (PIPELINE-TRUTH) owned fixture.
// Exercises subtype-aware ConstraintUsage enumeration and the RequirementUsage
// exclusion at the adapter choke point. Carries one of each shape the decision
// table cares about: an assert (AssertConstraintUsage), a plain ConstraintUsage,
// and a requirement (RequirementUsage) that the drop report must exclude.
package Item4Constraints {
    private import ScalarValues::*;

    part def Widget {
        attribute cost : Real = 50.0;
        attribute budget : Real = 100.0;

        // AssertConstraintUsage — a dropped executable predicate; must be reported.
        assert constraint affordable {
            cost <= budget
        }

        // plain ConstraintUsage — already visible to an exact-type query; reported.
        constraint positive_cost {
            cost > 0.0
        }
    }

    // RequirementUsage — requirement-side, NOT a dropped predicate; must be excluded.
    requirement def BudgetRequirement {
        subject widget : Widget;
    }
    requirement widget_budget : BudgetRequirement;
}
