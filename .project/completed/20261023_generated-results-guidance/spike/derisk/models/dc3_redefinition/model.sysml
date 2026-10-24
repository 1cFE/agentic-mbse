package Dc3Redefinition {
    private import ScalarValues::*;
    calc def Double { in x : Real; return y : Real = x * 2.0; }
    part def Rack {
        attribute power : Real = 1.0;
        calc d : Double { in x = power; }
    }
    part def Electrical {
        attribute load : Real default 1.0;
        attribute scaled : Real = load * 2.0;
        part racks : Rack[1];
    }
    part def Facility {
        part electrical : Electrical;
        attribute facility_load : Real = electrical.load + 1.0;
    }
    part def 'Native Facility' :> Facility {
        part :>> electrical {
            attribute :>> load = 5.0;
            part :>> racks[3];
        }
    }
    part site : 'Native Facility';
}
