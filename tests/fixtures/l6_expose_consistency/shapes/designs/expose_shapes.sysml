package ExposeShapesDesign {
    public import ScalarValues::*;
    public import ExposeShapesLibrary::*;

    // Shape A: EXPOSE on a part definition, instantiated so C4 stays quiet.
    part def ExposingModule {
        calc module_calc : ScaleCalc { in value = 3.0; }
        attribute module_result : Real = module_calc.scaled;
    }
    part module_instance : ExposingModule;

    // Shape B: EXPOSE on a part usage (the v2_expose_pattern.sysml shape).
    part expose_test_part {
        calc my_calc : ScaleCalc { in value = 10.0; }
        attribute exposed_output : Real = my_calc.scaled;
    }

    // Part-headed sibling chain: the head is a sibling part whose definition exposes a calc output.
    part relay_part {
        part sub_module : ExposingModule;
        attribute relayed : Real = sub_module.module_result;
    }
}
