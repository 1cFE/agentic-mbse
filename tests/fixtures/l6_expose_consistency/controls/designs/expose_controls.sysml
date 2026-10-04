package ExposeControlsDesign {
    public import ScalarValues::*;
    public import ExposeControlsLibrary::*;

    part producer {
        calc producer_calc : ScaleCalc { in value = 4.0; }
    }

    // Invalid target: head is a calc-bearing part that is not a sibling.
    part remote_reader {
        attribute remote : Real = producer.producer_calc.scaled;
    }

    // Invalid target: head is a sibling item usage, not a calc or part usage.
    part item_head_reader {
        item payload : Payload;
        attribute payload_mass : Real = payload.mass;
    }

    // Arithmetic over a calc output: derived, not EXPOSE.
    part derived_part {
        calc d_calc : ScaleCalc { in value = 1.0; }
        attribute derated : Real = d_calc.scaled * 0.95;
    }

    part controls {
        attribute powered : Real = 2.0 ^ 3.0;   // unsupported operator
        attribute missing : Real;               // absent value
        attribute divzero : Real = 1.0 / 0.0;   // unextractable static default
    }
}
