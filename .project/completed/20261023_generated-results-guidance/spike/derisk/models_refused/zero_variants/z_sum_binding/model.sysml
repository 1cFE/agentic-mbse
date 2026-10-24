package Z2 {
    private import ScalarValues::*;
    private import NumericalFunctions::sum;
    calc def Id { in a : Real; return r : Real = a; }
    part def X { attribute v : Real = 2.0; }
    part def Holder { part x : X[0]; calc c : Id { in a = sum(x.v); } }
    part holder : Holder;
}
