package Z4 {
    private import ScalarValues::*;
    private import NumericalFunctions::sum;
    calc def Id { in a : Real; return r : Real = a; }
    part def X { attribute v : Real = 2.0; }
    part def Holder { part x : X[0]; attribute one : Real = 1.0; assert constraint pos { sum(x.v) >= 0.0 } }
    part holder : Holder;
}
