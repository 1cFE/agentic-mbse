package TestDesign {
    import ScalarValues::*;
    private import Library::PowerCalc;

    part def System {
        doc /* System part with calc usage */
        calc power : PowerCalc {
            // p_input intentionally NOT bound - triggers L2 unbound input
        }
    }

    part system : System;
}
