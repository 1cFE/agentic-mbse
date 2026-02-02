package ValidDesignTest {
    import ScalarValues::*;
    part def Component {
        attribute length : Real;
        attribute width : Real;
    }
    part design_instance : Component {
        attribute length : Real = 10.0;
        attribute width : Real = 5.0;
    }
}
