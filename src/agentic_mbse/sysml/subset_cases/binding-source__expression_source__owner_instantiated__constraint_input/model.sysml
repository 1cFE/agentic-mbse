package fx {
    private import ScalarValues::*;
    calc def Total { in xs : Real[0..*] ordered nonunique; return r : Real = NumericalFunctions::sum(xs); }
    constraint def Pos { in q : Real; q > 0.0 }
    part def Site {
        attribute a : Real = 1.0;
        attribute b : Real = 2.0;
        assert constraint g : Pos { in q = a * b; }
    }
    part site : Site;
}
