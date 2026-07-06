package RescueLib {
    private import ScalarValues::*;

    // C1 negative-of-the-negative (Item 12): the same self-named `in throughput =
    // throughput` binding, but the owner exposes a real producer
    // (`attribute throughput = source_calc.throughput`), so the name resolves to a
    // channel. Item 10's rescue handles it -> C1 must NOT fire.
    calc def SourceCalc {
        in attribute raw : Real;
        out attribute throughput : Real = raw * 1.5;
    }

    calc def SinkCalc {
        in attribute throughput : Real;
        out attribute result : Real = throughput * 2.0;
    }

    part def RescuePlant {
        attribute raw_flow : Real = 4.0;

        calc source_calc : SourceCalc {
            in raw = raw_flow;
        }

        // Producer: exposes the upstream calc output under the name `throughput`.
        attribute throughput : Real = source_calc.throughput;

        calc sink_calc : SinkCalc {
            in throughput = throughput;
        }
    }
}
