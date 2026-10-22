package probe_g {
    private import ScalarValues::*;
    calc def Total { in x : Real[0..*] ordered nonunique; return r : Real = 1.0; }
    part def Host {
        attribute loads : Real[3] = (1.0, 2.0, 3.0);
        calc total : Total { in x = loads; }
    }
    part host : Host;
}
