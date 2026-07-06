package AnonReturnLib {
    private import ScalarValues::*;

    // C2a negative fixture (Item 12): an anonymous `return` (no declared name).
    // syside synthesizes the name `result` but leaves declared_name empty, so
    // codegen derives no output channel (mirrors codegen V8). L6 FAIL.
    calc def AnonReturn {
        in attribute x : Real;
        return : Real = x * 2;
    }
}
