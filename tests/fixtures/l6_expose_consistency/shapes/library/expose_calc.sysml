package ExposeShapesLibrary {
    public import ScalarValues::*;
    calc def ScaleCalc {
        in attribute value : Real;
        out attribute scaled : Real = value * 2.0;
    }
}
