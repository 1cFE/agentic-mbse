package fx {
    private import ScalarValues::*;
    part def Site {
        attribute a : Real = 0.9;
        attribute b : Real = 0.8;
        attribute eff : Real = NumericalFunctions::product((a, b));
    }
    part site : Site;
}
