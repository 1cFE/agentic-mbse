package OrphanLib {
    private import ScalarValues::*;

    // C4 negative fixture (Item 12): a calc-bearing part def that no usage
    // instantiates. Its template calc `the_calc` is dropped at extraction -> L6
    // FAIL. (Binding uses a distinct name `a_val` so the C1 self-named check does
    // not also fire.)
    calc def SomeCalc {
        in attribute a : Real;
        out attribute b : Real = a * 2;
    }

    part def OrphanCalcHolder {
        attribute a_val : Real = 3.0;

        calc the_calc : SomeCalc {
            in a = a_val;
        }
    }
}
