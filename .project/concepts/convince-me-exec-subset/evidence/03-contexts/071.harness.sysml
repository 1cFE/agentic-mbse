    part def Host {
        attribute v : Real = 10.0;
        attribute i : Real = 2.0;
        calc pc : PowerCalculation {
            in voltage = v;
            in current = i;
        }
        attribute p : Real = pc.power;
    }
    part host : Host;
