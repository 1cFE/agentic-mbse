package SplitDesign {
    private import ScalarValues::*;
    private import SplitLib::*;
    part def Cart {
        part motor : Motor { attribute :>> power = 4.0; }
        attribute cart_power : Real = motor.boosted * 2.0;
    }
    part cart : Cart;
}
