package RetypeLib {
    private import ScalarValues::*;

    // C4 negative-of-the-negative (Item 12): both calc-bearing part defs are
    // instantiated, IfeDriver via Facility.driver and HifDriver via a retype
    // (`part :>> driver : HifDriver`). A retyped usage's `.types` includes the
    // retype target, so C4 must NOT fire on either def.
    calc def IfeCalc {
        in attribute p : Real;
        out attribute ife_out : Real = p * 2.0;
    }

    calc def HifCalc {
        in attribute q : Real;
        out attribute hif_out : Real = q * 3.0;
    }

    part def IfeDriver {
        attribute power : Real = 10.0;

        calc ife_calc : IfeCalc {
            in p = power;
        }
    }

    part def HifDriver :> IfeDriver {
        attribute torque : Real = 20.0;

        calc hif_calc : HifCalc {
            in q = torque;
        }
    }

    part def Facility {
        part driver : IfeDriver;
    }

    part def Variant :> Facility {
        part :>> driver : HifDriver;
    }
}
