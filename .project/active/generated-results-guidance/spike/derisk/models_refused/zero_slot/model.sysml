package ZeroSlot {
    private import ScalarValues::*;
    private import NumericalFunctions::sum;
    part def X { attribute v : Real = 2.0; }
    part def Holder {
        attribute base : Real = 1.0;
        part x : X[0];
        attribute total : Real = sum(x.v);
        attribute plus : Real = total + base;
        attribute free : Real = base * 3.0;
    }
    part holder : Holder;
}
