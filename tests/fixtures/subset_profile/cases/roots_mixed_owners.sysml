package roots {
    // Generator root rule (sysml-codegen occurrence.py:916-923): a part usage is a root when
    // its semantic owner is neither a part def nor a part usage.
    part def Engine;
    part def Car { part engine : Engine; }        // owned by a part def: not a root
    part car : Car { part spare : Engine; }       // car is a root; spare is owned by a part usage
    part fleet : Car;                             // package-level: a root
    package depot { part reserve : Engine; }      // nested package: a root
    item def Crate { part tag : Engine; }         // owned by an item def, not a part def: a root
    part def Template { part site : Car; }        // never instantiated: not a root
}
