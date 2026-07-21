package OperatorFidelityProbe {
    private import ScalarValues::*;
    private import ISQ::*;
    private import SI::*;

    part def Probe {
        attribute base : Real = 2.0;
        attribute exp_value : Real = 3.0;

        assert constraint caret_form {
            base ^ exp_value >= 1.0
        }

        assert constraint power_form {
            base ** exp_value >= 1.0
        }

        assert constraint unary_minus_form {
            -base <= 0.0
        }

        assert constraint unsupported_form {
            if base > 0.0 ? true else false
        }
    }
}
