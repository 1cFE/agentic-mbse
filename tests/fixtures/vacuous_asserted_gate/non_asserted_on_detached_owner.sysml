package vacuous_non_asserted {
    private import ScalarValues::*;

    // A bare `constraint` states a condition without asking anyone to enforce it, so an
    // owner nobody instantiates says nothing about it. No advisory.
    part def Detached {
        attribute value : Real = 5.0;
        constraint plain_gate {
            value > 0.0
        }
    }

    part def Live {
        attribute reading : Real = 3.0;
        assert constraint reached_gate {
            reading > 0.0
        }
    }

    part the_live : Live;
}
