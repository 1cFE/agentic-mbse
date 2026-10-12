package Drainage {
    private import ScalarValues::Real;

    calc def RequiredPumpFlow {
        doc /* Flow the pump must remove so the basin level rises no faster than allowed. */
        in inflow : Real;
        in allowed_rise_rate : Real;
        in basin_area : Real;
        return required_flow : Real = inflow - allowed_rise_rate * basin_area;
    }

    part def SumpBasin {
        doc /* A collection basin fed by storm inflow. */
        attribute area : Real;
        attribute design_inflow : Real;
        attribute allowed_rise_rate : Real;
    }

    part def DrainPump {
        doc /* A drain pump with a rated installed flow capacity. */
        attribute installed_flow_capacity : Real;
    }
}
