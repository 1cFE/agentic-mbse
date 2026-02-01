package UnextractableDesignTest {
    import ScalarValues::*;
    part def Component {
        attribute length : Real;
        attribute width : Real;
        attribute area : Real = length * width;
    }
    part design_instance : Component {
        attribute length : Real = 10.0;
        attribute width : Real = 5.0;
        attribute area : Real = length * width;
    }
}
