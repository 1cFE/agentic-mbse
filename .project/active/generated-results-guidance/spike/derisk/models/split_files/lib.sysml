package SplitLib {
    private import ScalarValues::*;
    calc def Triple { in x : Real; return y : Real = x * 3.0; }
    part def Motor {
        attribute power : Real default 2.0;
        calc t : Triple { in x = power; }
        attribute boosted : Real = power + 1.0;
    }
}
