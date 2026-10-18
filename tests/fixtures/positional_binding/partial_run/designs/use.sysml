// Part of fixture partial_run/ (expectations in partial_run/expect.txt and partial_run/designs/expect.txt).
package Use {
    private import Defs::*;
    part q {
        calc c : Sub { in b = 3; in a = 10; }
        constraint k : Le { in lim = 5; in x = 3; }
    }
}
