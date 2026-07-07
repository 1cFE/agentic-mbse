package ConstraintLib {
    private import ScalarValues::*;

    // C3 negative fixture (Item 12): a model carrying a constraint usage.
    // Constraints are not executable and are dropped at extraction, so L6 WARNs
    // (see modeling-assumptions §8). WARN, not FAIL.
    part def Widget {
        attribute measured : Real = 5.0;
        attribute limit : Real = 10.0;

        constraint within_limit {
            measured <= limit
        }
    }
}
