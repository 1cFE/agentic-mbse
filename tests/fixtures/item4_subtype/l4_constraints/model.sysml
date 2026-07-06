// Item-4 level-4 fixture: one assert + one plain constraint + one requirement.
// After the row-6 fix, analyze_constraints counts the assert and the plain
// (total 2) and excludes the requirement.
package L4Constraints {
    private import ScalarValues::*;
    part def Widget {
        attribute cost : Real = 50.0;
        attribute budget : Real = 100.0;
        assert constraint affordable { cost <= budget }
        constraint positive_cost { cost > 0.0 }
    }
    requirement def BudgetReq { subject w : Widget; }
    requirement widget_req : BudgetReq;
}
