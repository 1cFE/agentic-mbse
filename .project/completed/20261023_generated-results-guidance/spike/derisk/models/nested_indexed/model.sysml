package NestedIndexed {
    private import ScalarValues::*;
    calc def Double { in x : Real; return y : Real = x * 2.0; }
    part def Cell {
        attribute capacity : Real = 1.5;
        calc d : Double { in x = capacity; }
    }
    part def Module { part cells : Cell[3]; }
    part def Pack { part modules : Module[2]; }
    part pack : Pack;
}
