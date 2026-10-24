package M {
    private import ScalarValues::*;
    calc def Dbl { in a : Real; return r : Real = a * 2; }
    part def P { attribute x : Real default 1.0; }
    part sys {
        part p : P { :>> x default 5.0; }
        calc d : Dbl { in a = p.x; }
    }
}
