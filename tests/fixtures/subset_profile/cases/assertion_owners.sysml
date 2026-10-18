package ao {
    // Assertion owner kinds and forms (sysml-codegen elaborate.py:759-787; constraint
    // forms from constraint_extraction._classify).
    private import ScalarValues::*;
    constraint def Positive { in q : Real; q > 0.0 }
    calc def Checked {
        in v : Real;
        assert constraint inDef { v > 0.0 }                           // asserted, calc-def owner
        constraint plainInDef { v < 10.0 }                            // not asserted, calc-def owner
        return r : Real = v;
    }
    part def P {
        attribute x : Real = 1.0;
        assert constraint inPart { x > 0.0 }                          // asserted, part-def owner
        assert constraint { x < 5.0 }                                 // anonymous
        assert constraint typed : Positive { in q = x; }              // asserted, definition-typed
        calc c : Checked {
            in v = x;
            assert constraint inUsage { v > 0.0 }                     // asserted, calc-usage owner
        }
    }
    part p : P;
}
