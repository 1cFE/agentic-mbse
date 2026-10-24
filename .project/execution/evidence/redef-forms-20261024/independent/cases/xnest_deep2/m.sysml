package M {
    private import ScalarValues::*;
    calc def Dbl { in a : Real; return r : Real = a * 2; }
    part def Host {
        attribute x : Real default 1.0;
        calc d : Dbl { in a = x; }
    }
    part def Mid { part inner : Host; }
    part def Outer { part mid : Mid; }
    part o : Outer { :>> mid.inner.x = 5.0; }
}
