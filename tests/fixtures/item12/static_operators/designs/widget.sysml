package StaticOpsDesign {
    private import ScalarValues::*;

    // C5 negative fixture (Item 12): design-scope static expressions.
    //  - `ok`      supported operators (+ - * /) only -> no finding (negative-of-negative)
    //  - `powered` power operator `^` -> V4_UNSUPPORTED_OPERATOR (ERROR); `^` was
    //              wrongly in the supported set, now removed (C5a). Literal operands
    //              isolate the operator signal (no design-attr ref -> no V2).
    //  - `rooted`  function invocation `sqrt(...)` -> V4_STATIC_FUNCTION_INVOCATION
    //              (WARN, C5b); literal arg isolates it (no V2 derived-expr ERROR).
    part def Widget {
        attribute ok : Real = 2.0 * 3.0 + 1.0;
        attribute powered : Real = 2.0 ^ 3.0;
        attribute rooted : Real = sqrt(2.0);
    }
}
