package AttrRedefExpr {
    private import ScalarValues::*;

    // Base carries the inherited attribute a design variant redefines.
    part def 'Base Plant' {
        attribute gain : Real = 1.0;
    }

    // NEGATIVE FIXTURE (C7 fires exactly once):
    // an `attribute :>>` redefinition carrying an EXPRESSION rhs. Codegen's
    // redefinition scan (hierarchy_resolver._extract_single_redefinition) reads
    // only ReferenceUsage members, so this AttributeUsage redefinition is silently
    // dropped at extraction — its override never reaches the pipeline. C7 must WARN.
    part variant : 'Base Plant' {
        attribute :>> gain = 2.0 * 3.0;
    }
}
