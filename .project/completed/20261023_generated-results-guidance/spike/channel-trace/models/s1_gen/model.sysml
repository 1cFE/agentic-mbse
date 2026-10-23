package probe_gen {
    private import ScalarValues::*;
    private import NumericalFunctions::sum;
    constraint def Positive { in v : Real; v > 0.0 }
    calc def Scale { in x : Real; return r : Real = x * 2.0; }
    part def Cell { attribute capacity : Real = 2.5; }
    part def Pack {
        attribute cell_count : Integer = 3;
        part cells : Cell[cell_count];
        attribute total : Real = sum(cells.capacity);
    }
    part def Host {
        attribute load : Real = 3.0;
        calc doubled : Scale { in x = load; }
        attribute doubled_load : Real = doubled.r;
        part pack : Pack;
        attribute pack_total : Real = pack.total;
        assert constraint load_positive : Positive { in v = load; }
        attribute neg_load : Real = 0.0 - load;
        assert constraint load_negative : Positive { in v = neg_load; }
    }
    part host : Host;
}
