// Two calc defs with one simple name, Twice, in two packages, with different bodies.
// The model means a.r = 2 * 1.0 = 2.0 and b.r = 3 * 1.0 = 3.0.
package LibA {
    private import ScalarValues::*;
    calc def Twice { in v : Real; return r : Real = 2.0 * v; }
}
package LibB {
    private import ScalarValues::*;
    calc def Twice { in v : Real; return r : Real = 3.0 * v; }
}
package Plant {
    private import ScalarValues::*;
    part def Site {
        attribute x : Real = 1.0;
        calc a : LibA::Twice { in v = x; }
        calc b : LibB::Twice { in v = x; }
        attribute ra : Real = a.r;
        attribute rb : Real = b.r;
    }
    part site : Site;
}
