package fx {
    private import ScalarValues::*;
    constraint def Dom { in e : Real; e > 0.0 and e <= 1.0 }
    calc def Eff2 { in a : Real; in b : Real; return r : Real = a * b; }
    part def Site {
        attribute ea : Real = 0.97;
        attribute eb : Real = 0.99;
        calc path : Eff2 { in a = ea; in b = eb; }
        assert constraint f1 : Dom { in e = ea; }
    }
    part site : Site;
}
