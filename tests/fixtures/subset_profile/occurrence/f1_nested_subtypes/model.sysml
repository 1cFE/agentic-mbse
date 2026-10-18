package f1g {
    private import ScalarValues::*;
    calc def Twice { in v : Real; return r : Real = 2.0 * v; }
    part def Server { attribute w : Real default 1.0; calc t : Twice { in v = w; } }
    part def GpuServer :> Server { attribute :>> w default 3.0; }
    part def Rack { part servers : Server[2]; }
    part def GpuRack :> Rack { part :>> servers : GpuServer[3]; }
    part def Hall { part racks : Rack[2]; part gpu : GpuRack; }
    part hall : Hall;
    part spare : Server;
    part def Unused { part s : Server[4]; }
}
