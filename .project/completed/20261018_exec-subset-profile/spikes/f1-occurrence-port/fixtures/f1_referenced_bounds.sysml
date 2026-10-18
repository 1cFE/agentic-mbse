package f1d {
    private import ScalarValues::*;
    part def Rack { attribute p : Real = 1.0; }
    part def Site { attribute n : Integer default 2; part racks : Rack[n]; }
    part def BigSite :> Site { attribute :>> n default 4; }
    part site : BigSite;
    part small : Site;
    part tuned : Site { attribute :>> n default 3; }
    attribute m : Integer = 5;
    part pkgracks : Rack[m];
    part def Hall { attribute k : Integer; part racks : Rack[k]; }
    part hall : Hall;
}
