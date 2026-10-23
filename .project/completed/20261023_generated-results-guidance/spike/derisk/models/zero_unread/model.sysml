package ZeroUnread {
    private import ScalarValues::*;
    part def X {
        attribute v : Real = 2.0;
        attribute w : Real = v * 2.0;
    }
    part def Holder {
        attribute base : Real = 1.0;
        part x : X[2];
        attribute free : Real = base * 3.0;
    }
    part holder : Holder {
        part :>> x[0];
    }
}
