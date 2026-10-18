package lib {
    // Definitions for the document-order test; plant.sysml instantiates them.
    private import ScalarValues::*;
    calc def Total { in xs : Real[0..*] ordered nonunique; return r : Real = NumericalFunctions::sum(xs); }
    part def Server { attribute power : Real = 100.0; }
    part def Rack { part servers : Server[1..4]; }
    part def Site {
        attribute a : Real = 1.0;
        attribute b : Real = 2.0;
        attribute label : String = "north";
        calc t : Total { in xs = (a, b); }
    }
}
