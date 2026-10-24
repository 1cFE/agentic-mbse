package MyPackage {
    private import ScalarValues::*;
    calc def MyCalculation {
        in attribute input_param : Real;  // [units] - Description

        attribute intermediate : Real = input_param * 2.0;  // Optional

        out attribute result : Real = intermediate * 1.5;  // [units] - Description
    }
}
package MyDesign {
    private import ScalarValues::*;
    private import MyPackage::MyCalculation;

    part my_component {
        // Input parameter
        attribute my_input : Real = 50.0;

        // Create calc instance
        calc my_calc : MyCalculation {
            // Bind input
            in input_param = my_component::my_input;
        }

        // Access output (optional)
        attribute my_result : Real = my_calc.result;

        // Check the result on the part, not inside the calc def
        assert constraint Reasonable {
            doc /* Description of constraint */
            my_result > 0 and my_result < 1000
        }
    }
}
