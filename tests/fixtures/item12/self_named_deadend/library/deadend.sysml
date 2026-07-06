package DeadEndLib {
    private import ScalarValues::*;

    // C1 negative fixture (Item 12): a true self-named dead-end. The calc input
    // `gain` is bound `in gain = gain`, but the owning part carries NO feature
    // named `gain` — no attribute, no sibling calc output. The reference resolves
    // to the calc's own parameter, so the intended value has nowhere to come from
    // -> L2 FAIL. Contrast self_named_trap, whose owner DOES carry a same-named
    // `attribute availability` (the plant design-attribute idiom Item 9 rescues),
    // so the trap now correctly does NOT fire — this dead-end is C1's real target.
    calc def GainCalc {
        in attribute gain : Real;
        out attribute scaled : Real = gain * 2.0;
    }

    part def DeadEndPlant {
        calc gain_calc : GainCalc {
            in gain = gain;
        }
    }
}
