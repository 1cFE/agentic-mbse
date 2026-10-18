package cd {
    // Conditionals in the positions the generator inventories, and one beneath arithmetic.
    private import ScalarValues::*;
    calc def Pick { in a : Real; in b : Real; return r : Real = if a < b ? a else b; }
    part def P {
        attribute x : Real = 1.0;
        attribute y : Real = 2.0;
        attribute chosen : Real = if x < y ? x else y;
        attribute nested : Real = 2.0 * (if x < y ? x else y);
        calc k : Pick { in a = if x < y ? x else y; in b = y; }
        attribute plain : Real = x + y;
    }
    part p : P;
}
