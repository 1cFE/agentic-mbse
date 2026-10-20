package fx {
    private import ScalarValues::*;
    item def Fuel { attribute density : Real; }
    part def Site {
        item fuel : Fuel { :>> density = 0.8; }
        attribute y : Real = 2.0 * fuel.density;
    }
    part site : Site;
}
