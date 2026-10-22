// min as agents/kerml-expert.md teaches it (private import NumericalFunctions::*), on a part.
package MinAttr {
    private import ScalarValues::*;
    private import NumericalFunctions::*;
    part def Site {
        attribute a : Real = 5.0;
        attribute b : Real = 3.0;
        attribute low : Real = min(a, b);
    }
    part site : Site;
}
