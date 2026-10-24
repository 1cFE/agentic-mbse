package OuterRedefinition {
    private import ScalarValues::*;
    part def Inner {
        attribute k : Real default 1.0;
        attribute tripled : Real = k * 3.0;
    }
    part def Middle { part inner : Inner; }
    part def Outer { part middle : Middle; }
    part outer : Outer {
        part :>> middle {
            part :>> inner {
                attribute :>> k = 7.0;
            }
        }
    }
}
