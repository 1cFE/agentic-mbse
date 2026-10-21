package probe_a {
    private import ScalarValues::*;
    constraint def Positive { in v : Real; v > 0.0 }
    calc def Scale { in x : Real; return r : Real = x * 2.0; }
    part def Host {
        attribute load : Real = 3.0;
        calc doubled : Scale {
            in x = load;
            assert constraint load_positive : Positive { in v = load; }
        }
    }
    part host : Host;
}
