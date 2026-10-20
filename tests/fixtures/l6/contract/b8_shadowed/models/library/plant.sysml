package fx {
    private import ScalarValues::*;
    calc def Eff2 { in a : Real; in b : Real; return r : Real = a * b; }
    part def Site {
        attribute ea : Real = 0.97;
        attribute eb : Real = 0.99;
        attribute enabled : Boolean = true;
        calc path : Eff2 {
            in a = ea;
            in b = eb;
            assert constraint f1 { enabled }
        }
    }
    part site : Site;
}
