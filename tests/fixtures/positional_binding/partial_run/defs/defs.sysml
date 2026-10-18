// Part of fixture partial_run/ (expectations in partial_run/expect.txt and partial_run/designs/expect.txt).
package Defs {
    private import ScalarValues::*;
    calc def Sub { in a : Real; in b : Real; return r : Real = a - b; }
    constraint def Le { in x : Real; in lim : Real; x <= lim }
}
