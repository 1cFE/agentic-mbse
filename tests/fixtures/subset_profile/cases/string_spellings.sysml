package ss {
    // Both String spellings: `attribute s : String = ".."` is an AttributeUsage, and the
    // shorthand `:>> s = ".."` parses as a ReferenceUsage.
    private import ScalarValues::*;
    part def Gen {
        attribute fuel : String;
        attribute label : String = "plant";                           // attribute_declaration
        attribute rate : Real default 2.0;                            // numeric sibling
    }
    part gen : Gen { :>> fuel = "diesel"; :>> rate = 3.0; }           // redefinition_shorthand
}
