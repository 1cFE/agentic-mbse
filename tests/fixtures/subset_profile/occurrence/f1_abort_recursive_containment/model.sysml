package f1i {
    private import ScalarValues::*;
    part def A { attribute p : Real = 1.0; part b : B; }
    part def B { part a : A; }
    part x : A;
}
