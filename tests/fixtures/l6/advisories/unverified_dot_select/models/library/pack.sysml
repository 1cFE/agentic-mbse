package fx {
    private import ScalarValues::*;
    private import NumericalFunctions::*;
    private import SequenceFunctions::*;
    private import ControlFunctions::*;
    part def Cell { attribute mass : Real = 2.0; attribute ok : Boolean = true; }
    part def Pack {
        part cells : Cell[3];
        attribute mass : Real = 1.0;
        attribute total : Real = sum(cells.?{ in c : Cell; c.ok }.mass);
    }
    part pack : Pack;
}
