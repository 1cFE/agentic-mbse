package Packs {
    private import ScalarValues::*;
    private import NumericalFunctions::sum;
    calc def UsableCapacity {
        in total_capacity_in : Real;
        in dod_in : Real;
        return usable : Real = total_capacity_in * dod_in;
    }
    part def Cell { attribute capacity : Real = 3.2; }
    part def Pack {
        part cells : Cell[3];
        attribute total_capacity : Real = sum(cells.capacity);
        attribute depth_of_discharge : Real = 0.8;
        calc usable_calc : UsableCapacity {
            in total_capacity_in = total_capacity;
            in dod_in = depth_of_discharge;
        }
        attribute usable_capacity : Real = usable_calc.usable;
    }
    part pack : Pack;
}
