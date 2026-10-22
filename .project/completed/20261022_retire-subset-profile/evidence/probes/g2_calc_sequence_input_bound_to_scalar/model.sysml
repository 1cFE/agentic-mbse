package probe_g2 {
    private import ScalarValues::*;
    calc def Total { in x : Real[0..*] ordered nonunique; return r : Real = 1.0; }
    part def Host {
        attribute load : Real = 3.0;
        calc total : Total { in x = load; }
    }
    part host : Host;
}
