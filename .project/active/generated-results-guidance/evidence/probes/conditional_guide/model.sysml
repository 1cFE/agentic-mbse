// The conditional exactly as MODELING_GUIDE.md.template "Key Syntax Patterns" and
// docs/patterns/conditionals.md "Basic Conditional" teach it, on a part.
package CondGuide {
    private import ScalarValues::*;
    part def Site {
        attribute x : Real = 5.0;
        attribute y : Real = 3.0;
        attribute diff : Real = if x > y? x - y else y - x;
    }
    part site : Site;
}
