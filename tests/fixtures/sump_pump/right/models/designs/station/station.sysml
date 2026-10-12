package Station {
    private import ScalarValues::Real;
    private import SI::*;
    private import Drainage::*;

    part station {
        doc /* Illustrative pumping station. Values are fixture inputs, not sourced data. */

        part basin : SumpBasin {
            :>> area = 12.0 [m^2];
            :>> design_inflow = 0.30 [m^3/s];
            :>> allowed_rise_rate = 0.005 [m/s];
        }

        part pump : DrainPump {
            :>> installed_flow_capacity = 0.25 [m^3/s];
        }

        calc demand : RequiredPumpFlow {
            in inflow = basin.design_inflow;
            in allowed_rise_rate = basin.allowed_rise_rate;
            in basin_area = basin.area;
        }

        attribute required_flow : Real = demand.required_flow;

        assert constraint pump_fit : CapacityCoversDemand {
            in installed = pump.installed_flow_capacity;
            in required = required_flow;
        }
    }
}
