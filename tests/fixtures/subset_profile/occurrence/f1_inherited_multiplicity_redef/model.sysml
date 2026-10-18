package f1c {
    private import ScalarValues::*;
    part def Rack { attribute p : Real = 1.0; }
    part def Site { part racks : Rack[2]; }
    part def BigSite :> Site { part :>> racks { attribute q : Real = 2.0; } }
    part site : BigSite;
}
