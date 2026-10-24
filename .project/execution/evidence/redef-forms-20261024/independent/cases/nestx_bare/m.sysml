package M {
    private import ScalarValues::*;
    calc def Dbl { in a : Real; return r : Real = a * 2; }
    part def Host {
        attribute x : Real default 1.0;
        attribute y : Real default 3.0;
        calc d : Dbl { in a = x; }
    }
    part def Outer { attribute q : Real default 4.0; part inner : Host; }
    part o : Outer { :>> inner.x = q * 2; }
}
