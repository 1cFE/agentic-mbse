package M {
    private import ScalarValues::*;
    calc def Dbl { in a : Real; return r : Real = a * 2; }
    part def Wheel { attribute w : Real default 1.0; calc d : Dbl { in a = w; } }
    part def Car {
        attribute n : Integer default 2;
        part wheels : Wheel[n];
    }
    part c : Car { :>> n = 3; }
}
