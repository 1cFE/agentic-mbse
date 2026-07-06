package FormulaComputedLibrary {
    private import ScalarValues::Real;

    // Minimal calc def so the DynamicPart consumer below has a real calc output
    // to (illegally) reference inside arithmetic. Its own output expression is a
    // calc-def-internal derived expression, exempt from V2 by C6a.
    calc def ScaleCalc {
        in attribute value : Real;
        out attribute result : Real = value * 2.0;
    }
}
