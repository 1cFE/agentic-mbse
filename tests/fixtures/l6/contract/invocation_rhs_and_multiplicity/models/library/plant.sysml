package fx {
    // UNSUPPORTED-RHS: NumericalFunctions::product at an attribute value is the
    // invocation-callable refusal. MULTIPLICITY-SHAPE: `servers : Server[*]` expanded under a
    // root is part-multiplicity/unresolved_bound.
    private import ScalarValues::*;
    calc def Twice { in v : Real; return r : Real = 2.0 * v; }
    part def Server { attribute power : Real; }
    part def Rack { part servers : Server[*]; }
    part rack : Rack {
        part s1 : Server :> servers { :>> power = 100.0; }
        part s2 : Server :> servers { :>> power = 120.0; }
    }
    part def Site {
        attribute a : Real = 0.9;
        attribute b : Real = 0.8;
        attribute eff : Real = NumericalFunctions::product((a, b));
        calc t : Twice { in v = a; }
    }
    part site : Site;
}
