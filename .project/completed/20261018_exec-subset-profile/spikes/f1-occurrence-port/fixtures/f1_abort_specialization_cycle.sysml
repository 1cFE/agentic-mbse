package f1k {
    private import ScalarValues::*;
    part def A :> B { attribute p : Real = 1.0; }
    part def B :> A;
    part x : A;
}
