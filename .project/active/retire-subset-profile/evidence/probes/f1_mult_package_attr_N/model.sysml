package probe_f1 {
    private import ScalarValues::*;
    attribute N : Integer = 3;
    calc def Scale { in x : Real; return r : Real = x * 2.0; }
    part def Child {
        attribute mass : Real = 1.5;
        calc doubled : Scale { in x = mass; }
    }
    part def Host { part kids : Child[N]; }
    part host : Host;
}
