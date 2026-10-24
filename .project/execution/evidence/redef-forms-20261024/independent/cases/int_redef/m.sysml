package M {
    private import ScalarValues::*;
    calc def Dbl { in a : Real; return r : Real = a * 2; }
    part def IHost {
        attribute n : Integer default 1;
        calc d : Dbl { in a = n; }
    }
    part h : IHost { redefines n = 4; }
}
