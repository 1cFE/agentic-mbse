package Packs {
    private import ScalarValues::*;
    calc def Double { in x : Real; return y : Real = x * 2.0; }
    part def Cell {
        attribute capacity : Real = 3.2;
        calc d : Double { in x = capacity; }
    }
    part def Pack {
        attribute cell_count : Integer default := 2;
        part cells : Cell[cell_count];
    }
    part pack : Pack { :>> cell_count = 3; }
}
