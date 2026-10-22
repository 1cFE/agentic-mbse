package Packs {
    private import ScalarValues::*;
    private import NumericalFunctions::sum;
    calc def Double { in x : Real; return y : Real = x * 2.0; }
    part def Cell {
        attribute capacity : Real = 3.2;
        calc d : Double { in x = capacity; }
    }
    part def Pack {
        attribute cell_count : Integer default := 2;
        part cells : Cell[cell_count];
        attribute total : Real = sum(cells.capacity);
    }
    part pack : Pack { :>> cell_count = 3; }
}
