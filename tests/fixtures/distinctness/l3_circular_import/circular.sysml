// Two packages with circular imports.
// L3 should detect this once Import element support is available in syside.
package PkgA {
    import PkgB::*;
    part def PartA;
}

package PkgB {
    import PkgA::*;
    part def PartB;
}
