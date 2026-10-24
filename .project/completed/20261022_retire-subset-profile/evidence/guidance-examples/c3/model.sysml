package P {
    private import ScalarValues::*;
    private import ISQ::*;
    private import SI::*;
    calc def Dummy { in x : Real; return y : Real = x * 2.0; }
    part def CorrectConstraint {
        attribute temperature_k : Real;  // [K]
        attribute q : Real = 1.0;
        calc d : Dummy { in x = q; }

        assert constraint TempLimit {  // Executes: the assert family is the enforcement opt-in
            doc /* Operating temperature must not exceed limit */
            temperature_k < 1000.0
        }
    }
    part p : CorrectConstraint { :>> temperature_k = 900.0; }
}
