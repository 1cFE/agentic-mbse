    part def Host {
        attribute x : Real = 3.0;
        calc mc : MyCalculation {
            in input_param = x;
        }
        attribute r : Real = mc.result;
    }
    part host : Host;
