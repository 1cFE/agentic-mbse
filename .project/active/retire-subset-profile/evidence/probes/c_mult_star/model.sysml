package probe_c {
    private import ScalarValues::*;
    calc def Scale { in x : Real; return r : Real = x * 2.0; }
    part def Child {
        attribute mass : Real = 1.5;
        calc doubled : Scale { in x = mass; }
    }
    part def Host { part kids : Child[*]; }
    part host : Host;
}
