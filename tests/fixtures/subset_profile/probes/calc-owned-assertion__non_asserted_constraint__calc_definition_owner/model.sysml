package fx {
    private import ScalarValues::*;
    calc def Eff2 {
        in a : Real; in b : Real;
        constraint f1 { a > 0.0 }
        return r : Real = a * b;
    }
    part def Site {
        attribute ea : Real = 0.97;
        attribute eb : Real = 0.99;
        calc path : Eff2 { in a = ea; in b = eb; }
    }
    part site : Site;
}
