// An assert on a part that the model's own values violate, the form MODELING_GUIDE.md.template
// limit 1 recommends. load_negative is violated; doubled_load is still an output.
package AssertVerdict {
    private import ScalarValues::*;
    constraint def Positive { in v : Real; v > 0.0 }
    calc def Scale { in x : Real; return r : Real = x * 2.0; }
    part def Host {
        attribute load : Real = 3.0;
        calc doubled : Scale { in x = load; }
        attribute doubled_load : Real = doubled.r;
        attribute neg_load : Real = 0.0 - load;
        assert constraint load_positive : Positive { in v = load; }
        assert constraint load_negative : Positive { in v = neg_load; }
    }
    part host : Host;
}
