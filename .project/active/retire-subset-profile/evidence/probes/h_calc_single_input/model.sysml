package probe_h {
    private import ScalarValues::*;
    calc def Scale { in x : Real; return r : Real = x * 2.0; }
    part def Host {
        attribute load : Real = 3.0;
        calc doubled : Scale { in x = load; }
    }
    part host : Host;
}
