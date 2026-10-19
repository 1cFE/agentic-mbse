package plant {
    doc /* Design side: every Appendix B site has an element to reach (Item 3 Phase 7). */
    private import ScalarValues::*;
    private import NumericalFunctions::*;
    private import lib::*;

    part def Plant {
        attribute a : Real = 1.0;
        attribute b : Real = 2.0;
        calc t : Total2 { in x1 = a; in x2 = b; }
        attribute exposed = t.r;
        attribute scaled : Real = a * 2.0;
        attribute unset : Real;
    }

    part plant : Plant;
    part site : Site;
}
