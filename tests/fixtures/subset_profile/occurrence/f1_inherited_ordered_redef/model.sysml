package f1a {
    private import ScalarValues::*;
    part def Rack { attribute p : Real = 1.0; }
    part def Site { part racks : Rack[2] ordered; }
    part def BigSite :> Site { part :>> racks; }
    part site : BigSite;
}
