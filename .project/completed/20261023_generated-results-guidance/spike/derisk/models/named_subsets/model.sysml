package NamedSubsets {
    private import ScalarValues::*;
    private import NumericalFunctions::sum;
    calc def Double { in x : Real; return y : Real = x * 2.0; }
    part def Rack {
        attribute capacity : Real default 2.0;
        calc d : Double { in x = capacity; }
    }
    part def Room {
        part racks : Rack[2];
        part rack_1 : Rack :> racks;
        part rack_2 : Rack :> racks { attribute :>> capacity = 4.0; }
        attribute named_total : Real = rack_1.capacity + rack_2.capacity;
        attribute rack_sum : Real = sum(racks.capacity);
    }
    part room : Room;
}
