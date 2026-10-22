package Packs {
    private import ScalarValues::*;
    private import NumericalFunctions::sum;
    calc def TotalCapacity {
        in capacities : Real[0..*] ordered nonunique;
        return total : Real = sum(capacities);
    }
    part def Cell { attribute capacity : Real = 3.2; }
    part def Pack {
        part cells : Cell[3];
        calc total_calc : TotalCapacity { in capacities = cells.capacity; }
        attribute total_capacity : Real = total_calc.total;
    }
    part pack : Pack;
}
