package orphan {
    // No generator root reaches Orphan: it is a definition nobody instantiates. Its String
    // value is still omitted (B6), and gets no L6_DESIGN_ATTR_UNEXTRACTABLE.
    private import ScalarValues::*;
    part def Orphan {
        attribute label : String = "never instantiated";
    }
    attribute def Tag {
        attribute name : String = "tag";
    }
}
