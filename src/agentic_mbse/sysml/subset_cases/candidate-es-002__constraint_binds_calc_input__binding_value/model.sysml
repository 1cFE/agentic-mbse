package fx {
    private import ScalarValues::*;
    calc def Twice { in v : Real; return r : Real = 2.0 * v; }
    constraint def Pos { in q : Real; q > 0.0 }
    part def Site {
        attribute x : Real = 1.0;
        calc t : Twice { in v = x; }
        assert constraint g : Pos { in q = t.v; }
    }
    part site : Site;
}
