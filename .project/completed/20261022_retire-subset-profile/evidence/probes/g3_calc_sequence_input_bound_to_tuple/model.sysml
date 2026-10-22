package probe_g3 {
    private import ScalarValues::*;
    calc def Total { in x : Real[0..*] ordered nonunique; return r : Real = 1.0; }
    part def Host {
        attribute a : Real = 1.0;
        attribute b : Real = 2.0;
        calc total : Total { in x = (a, b); }
    }
    part host : Host;
}
