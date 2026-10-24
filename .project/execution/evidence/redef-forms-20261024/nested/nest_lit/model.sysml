package nest_lit {
    private import ScalarValues::*;
    calc def Twice { in v : Real; return r : Real = 2.0 * v; }
    part def Inner { attribute x : Real default 1.0; }
    part def Host {
        attribute q : Real = 8.0;
        part inner : Inner;
        calc t : Twice { in v = inner.x; }
    }
    part h : Host { :>> inner.x = 5.0; }
}
