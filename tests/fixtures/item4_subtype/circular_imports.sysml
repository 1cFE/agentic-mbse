// Item-4 (PIPELINE-TRUTH) owned fixture: a genuine circular package import.
// PkgOne imports PkgTwo and vice-versa. Level 3 must build a non-empty
// dependency graph AND flag the cycle — the first time that check can fail.
package PkgOne {
    import PkgTwo::*;
    part def ThingOne;
}

package PkgTwo {
    import PkgOne::*;
    part def ThingTwo;
}
