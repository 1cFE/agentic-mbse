package AttrRedefLiteral {
    private import ScalarValues::*;

    part def 'Base Plant' {
        attribute gain : Real = 1.0;
        attribute rate : Real = 1.0;
        attribute level : Real = 1.0;
    }

    // SILENT-ON-CLEAN: the three redefinition shapes C7 must NOT fire on.
    part variant : 'Base Plant' {
        // (b) bare `:>>` literal override — parses as ReferenceUsage, captured
        // (D1 mechanism b, the supported whole-plant value idiom).
        :>> gain = 7.0;

        // bare `:>>` expression — ReferenceUsage, captured as CHAIN/EXPRESSION, not
        // dropped. C7 scans only AttributeUsage, so this is out of its range anyway.
        :>> rate = 2.0 * 4.0;

        // (b') `attribute :>>` with a LITERAL rhs — an AttributeUsage, but C7 is
        // scoped to the expression case (prior-epic C7 boundary: expression-vs-literal).
        // The literal form is taught in semantic-operators.md (use the bare form),
        // not warned — so C7 stays silent here too.
        attribute :>> level = 5.0;
    }
}
