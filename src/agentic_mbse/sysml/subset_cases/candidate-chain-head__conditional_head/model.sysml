package fx {
    private import ScalarValues::*;
    part def Wheel { attribute r : Real = 1.0; }
    part def Site {
        part w : Wheel;
        part v : Wheel;
        attribute t : Real = (if true ? w else v).r;
    }
    part site : Site;
}
