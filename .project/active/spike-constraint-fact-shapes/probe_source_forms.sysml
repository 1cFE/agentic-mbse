package ConstraintFactShapeProbe {
    private import ScalarValues::*;

    constraint def WithinLimit {
        in attribute observed : Real;
        in attribute limit : Real default 10.0;
        observed <= limit
    }

    requirement def LimitRequirement {
        subject checked : ProbePart;
        assume constraint positive_limit {
            checked.limit > 0.0
        }
        require constraint below_limit {
            checked.observed_value <= checked.limit
        }
    }

    part def ProbePart {
        attribute observed_value : Real = 5.0;
        attribute limit : Real = 10.0;
        part sensor {
            attribute reading : Real = 4.0;
        }

        assert constraint inline_owner_reference {
            observed_value <= limit
        }

        assert constraint typed_feature_chain_and_literal : WithinLimit {
            in observed = sensor.reading;
            in limit = 12.0;
        }

        assert constraint typed_omitted_default : WithinLimit {
            in observed = observed_value;
        }

        assert constraint {
            observed_value >= 0.0
        }

        constraint named_usage : WithinLimit;

        assert named_usage {
            in :>> observed = observed_value;
            in :>> limit = 12.0;
        }

        assert not constraint negated_inline {
            observed_value > limit
        }
    }

    calc def ProbeCalculation {
        in attribute observed : Real;
        assert constraint calc_owned {
            observed >= 0.0
        }
        out attribute doubled : Real = observed * 2.0;
    }

    part direct_usage {
        attribute observed : Real = 3.0;
        assert constraint direct_owned {
            observed >= 0.0
        }
    }

    part def BaseProbe {
        attribute base_value : Real;
        assert constraint inherited_limit {
            base_value >= 0.0
        }
    }

    part def DerivedProbe :> BaseProbe {
        attribute :>> base_value = 2.0;
    }

    part retyped_usage : BaseProbe {
        attribute :>> base_value = 3.0;
    }

    part sample : ProbePart;
    satisfy requirement satisfied_limit : LimitRequirement by sample;
}
