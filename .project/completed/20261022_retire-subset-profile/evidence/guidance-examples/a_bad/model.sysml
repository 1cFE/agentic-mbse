package Heaters {
    private import ScalarValues::*;

    constraint def Positive { in amount : Real; amount > 0.0 }

    calc def PowerCalc {
        in voltage_in : Real;
        in current_in : Real;
        return power : Real = voltage_in * current_in;
        assert constraint power_ok : Positive { in amount = power; }
    }

    part def Heater {
        attribute voltage : Real = 230.0;
        attribute current : Real = 4.0;
        calc power_calc : PowerCalc {
            in voltage_in = voltage;
            in current_in = current;
        }
        attribute power : Real = power_calc.power;
    }

    part heater : Heater;
}
