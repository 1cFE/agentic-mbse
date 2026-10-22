package OneSlot {
    private import ScalarValues::*;
    calc def Double { in x : Real; return y : Real = x * 2.0; }
    part def Cell {
        attribute capacity : Real = 2.5;
        calc d : Double { in x = capacity; }
    }
    part def Pack {
        part cell : Cell[1];
        attribute total : Real = cell.capacity * 2.0;
    }
    part pack : Pack;
}
