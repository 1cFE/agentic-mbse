// Item-4 (PIPELINE-TRUTH) owned fixture: an acyclic package import.
// PkgApp imports PkgLib but not vice-versa. Level 3 must build a non-empty
// dependency graph and report NO cycle (silent-on-clean).
package PkgLib {
    part def Base;
}

package PkgApp {
    import PkgLib::*;
    part def App :> PkgLib::Base;
}
