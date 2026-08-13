package vacuous_detached {
    private import ScalarValues::*;

    // `Detached` is typed by no part usage anywhere in the model, so its asserted gate can
    // never be checked. The advisory names it. `Live` is typed, so it stays silent.
    part def Detached {
        attribute value : Real = 5.0;
        assert constraint vacuous_gate {
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
