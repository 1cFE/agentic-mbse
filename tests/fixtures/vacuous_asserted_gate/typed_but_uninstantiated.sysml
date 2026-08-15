package vacuous_containment {
    private import ScalarValues::*;

    // `Typed` IS typed by a part usage (`Parent::child`), so the structural trigger stays
    // silent here even though `Parent` is never instantiated and codegen's occurrence
    // index still grades the gate vacuous. Silence is the correct answer: the trigger set
    // is a subset of codegen's, never a superset.
    part def Typed {
        attribute value : Real = 5.0;
        assert constraint nested_vacuous_gate {
            value > 0.0
        }
    }

    part def Parent {
        part child : Typed;
    }

    part def Live {
        attribute reading : Real = 3.0;
        assert constraint reached_gate {
            reading > 0.0
        }
    }

    part the_live : Live;
}
