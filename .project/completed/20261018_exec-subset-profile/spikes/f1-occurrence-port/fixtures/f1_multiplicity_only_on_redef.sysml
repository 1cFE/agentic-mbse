package f1b {
    private import ScalarValues::*;
    part def Rack { attribute p : Real = 1.0; }
    part def Site { part racks : Rack; }
    part def BigSite :> Site { part :>> racks[3]; }
    part site : BigSite;
    part plain : Site;
}
