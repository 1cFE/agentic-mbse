package probe_extra {
    private import ScalarValues::*;
    private import NumericalFunctions::sum;
    private import SequenceFunctions::size;
    constraint def Positive { in v : Real; v > 0.0 }
    part def Cell { attribute capacity : Real default 2.5; }
    part def PackLit {
        part cells : Cell[3];
        attribute total : Real = sum(cells.capacity);
        attribute n : Integer = size(cells);
    }
    part def PackRedef {
        part cells : Cell[2];
        part extra :> cells { attribute :>> capacity := 4.0; }
        attribute total : Real = sum(cells.capacity);
    }
    part def Host {
        attribute load : Real = 3.0;
        part packlit : PackLit;
        part packredef : PackRedef;
        assert constraint load_positive : Positive { in v = load; }
        assert constraint load_negative : Positive { in v = -load; }
        assert constraint inline_neg { load < 0.0 }
        attribute pos_flag : Boolean = load > 0.0;
    }
    part host : Host;
}
