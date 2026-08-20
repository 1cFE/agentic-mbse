package QualifiedLocalLib {
    private import ScalarValues::*;

    // F-2 regression source (self-binding-replacement Phase 1, from spike
    // s4a_qual_one_occ): a qualified right-hand side whose bare leaf name
    // equals the input parameter's own name is NOT a self-named binding. The
    // referent is the owner's attribute — a different element from the calc's
    // parameter — so C1 must compare referent identity, never names.
    calc def AvailabilityCalc {
        in attribute availability : Real;
        out attribute derated : Real = availability * 0.9;
    }

    // Definition-qualified (the spike shape): the calc sits inside the part
    // def and qualifies by that def's own name; exactly one occurrence exists.
    part def QualifiedPlant {
        attribute availability : Real = 0.85;

        calc avail_calc : AvailabilityCalc {
            in availability = QualifiedPlant::availability;
        }
    }
}
