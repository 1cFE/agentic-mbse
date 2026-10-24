// Copy of .project/concepts/convince-me-exec-subset/evidence/04-fixtures/gen_byname/model.sysml (prototype generator fixture).
// Native SysIDE 0.8.4 plant.result per 04-eval.log: 7.0; generated/TEAx: 7.0.
package PositionalByName {
    private import ScalarValues::*;

    calc def Sub {
        doc /* r = a - b */
        in a : Real;
        in b : Real;
        return r : Real = a - b;
    }

    part def Plant {
        doc /* Reversed declaration order, explicit by-name redefinition. */
        attribute big : Real = 10.0;
        attribute small : Real = 3.0;
        calc diff : Sub {
            in :>> b = small;
            in :>> a = big;
        }
        attribute result : Real = diff.r;
    }

    part plant : Plant;
}
