package Witness {
    private import ScalarValues::*;
    attribute n : Natural = 1;
    part def Cell {
        attribute capacity : Real = 2.0;
    }
    part def Pack {
        part cells : Cell[n..2];
    }
    part pack : Pack;
}
