package M {
    private import ScalarValues::*;
    calc def Dbl { in a : Real; return r : Real = a * 2; }
    part def Host {
        attribute x : Real;
        attribute y : Real default 3.0;
        calc d : Dbl { in a = x; }
    }
    part h : Host { redefines x = 5.0; }
}
