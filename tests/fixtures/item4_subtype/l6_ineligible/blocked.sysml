// CONSTRAINT-EXEC Item 3 owned fixture.
// A deterministic blocked-construct case: the predicate body carries a feature chain
// (`sensor.reading`), which the executable profile blocks (block_feature_chain) regardless of
// how the chain's leaf type resolves. Reused by both the item4_subtype L6 WARN test and the
// item12 C3 test — one fixture, one guaranteed-blocked shape.
package L6Ineligible {
    private import ScalarValues::*;

    part def Sensor {
        attribute reading : Real = 5.0;
    }

    part def Widget {
        sensor : Sensor;
        attribute limit : Real = 10.0;

        assert constraint chained_limit {
            sensor.reading <= limit
        }
    }
}
