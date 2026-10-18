package PositionalByName {
    private import ScalarValues::*;

    calc def Sub {
        doc /* r = a - b */
        in a : Real;
        in b : Real;
        return r : Real = a - b;
    }

    part def Plant {
        doc /* Reversed declaration order, explicit by-name redefinition. */
        attribute big : Real = 10.0;
        attribute small : Real = 3.0;
        calc diff : Sub {
            in :>> b = small;
            in :>> a = big;
        }
        attribute result : Real = diff.r;
    }

    part plant : Plant;
}
