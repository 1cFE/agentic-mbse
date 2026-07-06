package TrapLib {
    private import ScalarValues::*;

    // C1 negative-of-the-negative (Item 12): the self-named binding `in
    // availability = availability` alongside a same-named `attribute availability
    // = 0.70`. Pre-Items-9/10 this was "the trap"; Item 9's rescue made the plant
    // design-attribute idiom (a self-named binding with a covering outer attribute,
    // even a bare literal) a SUPPORTED shape. So C1 must NOT fire here — the outer
    // attribute covers the name. The true dead-end (no covering feature at all)
    // lives in self_named_deadend. Mirror of sysml-codegen's self_named_binding_trap
    // (unquoted names to isolate the C1 signal).
    calc def AvailabilityCalc {
        in attribute availability : Real;
        out attribute derated : Real = availability * 0.9;
    }

    part def TrapPlant {
        attribute availability : Real = 0.70;

        calc avail_calc : AvailabilityCalc {
            in availability = availability;
        }
    }
}
