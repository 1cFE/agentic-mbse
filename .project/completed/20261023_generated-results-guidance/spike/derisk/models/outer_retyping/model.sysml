package OuterRetyping {
    private import ScalarValues::*;
    part def Inner {
        attribute k : Real default 1.0;
        attribute tripled : Real = k * 3.0;
    }
    part def HotInner :> Inner { attribute :>> k = 7.0; }
    part def Middle { part inner : Inner; }
    part def HotMiddle :> Middle { part :>> inner : HotInner; }
    part def Outer { part middle : Middle; }
    part outer : Outer {
        part :>> middle : HotMiddle;
    }
}
