package templates {
    private import lib::*;
    private import ScalarValues::*;
    part def Spare {
        part site : Site;
        attribute ceiling : Real = ScalarFunctions::max(1.0, 2.0);
        assert constraint positive { ceiling > 0.0 }
    }
}
