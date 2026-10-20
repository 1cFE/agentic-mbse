package fx {
    private import ScalarValues::*;
    part ac_facility { attribute area : Real = 10.0; }
    part site { part facility :> ac_facility; attribute double : Real = 2.0 * facility.area; }
}
