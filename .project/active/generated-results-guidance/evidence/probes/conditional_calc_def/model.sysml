// The conditional as docs/patterns/conditionals.md "In Calc Definitions" teaches it, used from a part.
package CondCalcDef {
    private import ScalarValues::*;
    calc def ConditionalTest {
        in attribute x : Real;
        in attribute y : Real;
        return attribute diff : Real = if x > y? x - y else y - x;
    }
    part def Site {
        attribute p : Real = 5.0;
        attribute q : Real = 3.0;
        calc c : ConditionalTest { in x = p; in y = q; }
        attribute d : Real = c.diff;
    }
    part site : Site;
}
