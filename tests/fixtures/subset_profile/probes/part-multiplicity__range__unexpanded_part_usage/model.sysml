package fx {
    private import ScalarValues::*;
    calc def Twice { in v : Real; return r : Real = 2.0 * v; }
    part def Server { attribute power : Real = 100.0; calc t : Twice { in v = power; } }
    part def Rack { part servers : Server[1..4]; }
    part def Meter { attribute load : Real = 5.0; calc m : Twice { in v = load; } }
    part meter : Meter;
}
