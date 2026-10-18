package bk {
    // One calc usage binding each of the generator's binding-source classes
    // (sysml-codegen elaborate.py:2130-2196, binding_source.py:87-89).
    private import ScalarValues::*;
    calc def F {
        in lit : Real; in src : Real; in me : Real; in idx : Real; in cidx : Real;
        in tup : Real[2]; in unit : ISQ::LengthValue;
        return r : Real = lit;
    }
    part def Q { attribute v : Real = 1.0; }
    part def P {
        attribute x : Real = 1.0;
        part qs : Q[2] ordered;
        attribute xs : Real[2] ordered nonunique = (1.0, 2.0);
        calc f : F {
            in lit = 2.0;
            in src = x;
            in me = me;
            in idx = xs#(1);     // an IndexExpression is not a reference metatype: expression
            in cidx = qs#(1).v;  // a chain with an indexed head: indexed
            in tup = (x, x);
            in unit = 3.0 [SI::m];
        }
    }
    part p : P;
}
