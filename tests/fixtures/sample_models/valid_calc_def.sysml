package TestPackage {
    import ScalarValues::*;

    calc def TestCalculation {
        doc /* A simple test calculation definition */
        in x : Real;
        in y : Real;
        return result : Real = x + y;
    }
}
