package ConstraintTypeUnitProbe {
    private import ScalarValues::*;
    private import ISQ::*;
    private import SI::*;

    enum def Color { red; blue; }
    enum def Mode { on; off; }

    attribute def DerivedReal :> Real;
    alias RealAlias for Real;

    part def TypeMatrix {
        attribute color : Color = Color::red;
        attribute mode : Mode = Mode::on;
        attribute integer_value : Integer = 1;
        attribute second_integer : Integer = 2;
        attribute real_value : Real = 1.0;
        attribute boolean_value : Boolean = true;
        attribute second_boolean : Boolean = false;
        attribute string_value : String = "a";
        attribute second_string : String = "b";
        attribute derived_value : DerivedReal;
        attribute alias_value : RealAlias = 1.0;
        attribute length_value : LengthValue = 1 [m];
        attribute mass_value : MassValue = 1 [kg];

        assert constraint enum_own { color == Color::red }
        assert constraint enum_incompatible { color == Mode::on }
        assert constraint integer_real { integer_value == real_value }
        assert constraint integer_integer { integer_value == second_integer }
        assert constraint boolean_boolean { boolean_value == second_boolean }
        assert constraint string_string { string_value == second_string }
        assert constraint quantity_same_unit { 1 [m] == 2 [m] }
        assert constraint quantity_convertible_unit { 1 [m] == 100 [cm] }
        assert constraint quantity_incompatible_dimension { 1 [m] == 1 [kg] }
        assert constraint unit_bearing_arithmetic { 1 [m] + 1 [m] == 2 [m] }
        assert constraint unitless_dimensioned { 1.0 == 1 [m] }
        assert constraint quantity_feature_unknown_unit { length_value == 1 [m] }
        assert constraint unresolved_operand { missing_value == 1.0 }
        assert constraint inherited_alias_type { derived_value == alias_value }

        assert constraint compound_boolean {
            (color == Color::red and integer_value <= real_value) or
            not (length_value == 0 [m])
        }
    }
}
