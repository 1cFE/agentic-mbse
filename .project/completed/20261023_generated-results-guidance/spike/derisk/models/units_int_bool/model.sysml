package UnitsIntBool {
    private import ScalarValues::*;
    private import SI::*;
    part def Box {
        attribute mass : Real = 2.0 [kg];
        attribute double_mass : Real = mass * 2.0;
        attribute grams : Real = 500.0 [g];
        attribute double_grams : Real = grams * 2.0;
        attribute n : Integer = 3;
        attribute n2 : Integer = n * 2;
        attribute ratio : Real = 1.5;
        attribute heavy : Boolean = ratio > 1.0;
    }
    part box : Box;
}
