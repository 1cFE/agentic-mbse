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

        calc demand : RequiredPumpFlow {
            in inflow = basin.design_inflow;
            in allowed_rise_rate = basin.allowed_rise_rate;
            in basin_area = basin.area;
        }

        attribute required_flow : Real = demand.required_flow;

        part pump : DrainPump {
            attribute sizing_margin : Real = 1.2;

            calc sizing : PumpSizing {
                in required_flow = demand.required_flow;
                in margin = sizing_margin;
            }

            :>> installed_flow_capacity = sizing.capacity;
        }
    }
}
