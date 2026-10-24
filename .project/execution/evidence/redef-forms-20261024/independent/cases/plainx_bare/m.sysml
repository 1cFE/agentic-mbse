package M {
    private import ScalarValues::*;
    calc def Dbl { in a : Real; return r : Real = a * 2; }
    part def P { attribute x : Real default 1.0; attribute y : Real default 3.0; }
    part sys {
        part p : P { :>> x = y * 2; }
        calc d : Dbl { in a = p.x; }
    }
}
