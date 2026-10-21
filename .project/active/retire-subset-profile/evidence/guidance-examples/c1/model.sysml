package P {
    private import ScalarValues::*;
    calc def PowerCalculation {
        in attribute voltage_in : Real;
        in attribute current_in : Real;
        out attribute power : Real = voltage_in * current_in;
    }
    part def 'Heater' {
        attribute voltage : Real;
        attribute current : Real;
        calc power_calc : PowerCalculation { in voltage_in = voltage; in current_in = current; }
        attribute power : Real = power_calc.power;

        assert constraint ReasonablePower {
            doc /* Output power must be reasonable */
            power > 0 and power < 1e9
        }
    }
    part heater : 'Heater' { :>> voltage = 230.0; :>> current = 4.0; }
}
