package PackageA {
    import PackageB::*;
    calc def CalcA { in x : Real; return y : Real = x; }
}

package PackageB {
    import PackageA::*;
    calc def CalcB { in a : Real; return b : Real = a; }
}
