package fx {
    private import ScalarValues::*;
    part def Server { attribute power : Real; }
    part def Rack { part servers : Server[*]; }
    part rack : Rack {
        part s1 : Server :> servers { :>> power = 100.0; }
    }
    part def Spare {
        attribute load : Real = 5.0;
        attribute enabled : Boolean = true;
        assert constraint c { enabled }
    }
}
