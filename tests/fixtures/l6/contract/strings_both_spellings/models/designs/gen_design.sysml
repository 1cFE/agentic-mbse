package gd {
    // Both String spellings inside designs/: `attribute s : String = ".."` is an
    // AttributeUsage; the shorthand `:>> s = ".."` parses as a ReferenceUsage.
    private import ScalarValues::*;
    part def Gen {
        attribute fuel : String = "none";
        attribute label : String = "plant";
        attribute rate : Real = 2.0;
    }
    part gen : Gen { :>> fuel = "diesel"; :>> rate = 3.0; }
}
