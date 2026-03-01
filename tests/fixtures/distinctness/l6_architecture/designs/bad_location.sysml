// ADR-002 V1 VIOLATION: calc def in designs/ instead of library/
package DesignPkg {
    import ScalarValues::*;

    // VIOLATION: Should be in library/, not designs/
    calc def BadLocationCalc {
        in x : Real;
        return y : Real = x * 2.0;
    }

    part def System {
        doc /* System with calc usage */
        attribute input_val : Real = 5.0;

        calc bad_calc : BadLocationCalc {
            in x = input_val;
        }
    }

    part system : System;
}
