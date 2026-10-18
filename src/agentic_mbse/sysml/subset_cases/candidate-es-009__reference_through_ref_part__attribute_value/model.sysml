package fx {
    private import ScalarValues::*;
    part def Fac { attribute area : Real = 10.0; }
    part def Site { ref part facility : Fac; attribute double : Real = 2.0 * facility.area; }
    part site : Site;
}
