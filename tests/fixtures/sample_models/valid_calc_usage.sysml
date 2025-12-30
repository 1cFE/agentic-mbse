package TestDesign {
    import ScalarValues::*;
    import TestPackage::*;

    part def TestPart {
        attribute input_a : Real = 1.0;
        attribute input_b : Real = 2.0;

        calc test_calc : TestCalculation {
            in x = input_a;
            in y = input_b;
        }
    }

    part test_instance : TestPart;
}
