package ExposeControlsLibrary {
    public import ScalarValues::*;
    calc def ScaleCalc {
        in attribute value : Real;
        out attribute scaled : Real = value * 2.0;
    }
    item def Payload {
        attribute mass : Real = 1.0;
    }
}
