package fx {
    private import ScalarValues::*;
    calc def Twice { in v : Real; return r : Real = 2.0 * v; }
    part def Psu { attribute efficiency : Real default 0.9; calc t : Twice { in v = efficiency; } }
    part def Server { part psu : Psu; }
    part def Rack { part servers : Server[2]; }
    part def ItSystem { part racks : Rack[2]; }
    part def Facility { part it_system : ItSystem; }
    part facility : Facility {
        part :>> it_system {
            part rack_1 : Rack :> racks {
                part server_1 : Server :> servers { part :>> psu { :>> efficiency = 0.95; } }
                part server_2 : Server :> servers { part :>> psu { :>> efficiency = 0.95; } }
            }
            part rack_2 : Rack :> racks {
                part server_1 : Server :> servers { part :>> psu { :>> efficiency = 0.95; } }
                part server_2 : Server :> servers { part :>> psu { :>> efficiency = 0.95; } }
            }
        }
    }
}
