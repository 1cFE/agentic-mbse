package QualifiedLocalDesign {
    private import QualifiedLocalLib::*;

    part qualified_plant : QualifiedPlant;

    // Usage-qualified (the published D-6 teaching shape): the qualifier names
    // the enclosing part usage that owns the attribute.
    part station {
        attribute availability : Real = 0.7;

        calc station_calc : AvailabilityCalc {
            in availability = station::availability;
        }
    }
}
