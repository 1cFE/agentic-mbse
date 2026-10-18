// Fixture: dc3/dc3_serial_path_swap
// Source: dc3 60b44d5 models/designs/ac_coupled/ac_facility.sysml:225-233 (calc rack_1_server_1_efficiency :
// 'Serial Path 8'), reduced, with lines 226-227 swapped; 'Serial Path 8' from
// models/library/analyses/energy/path_efficiency.sysml:109 (D22). The quoted def name also exercises B4.
// finding: dc3_serial_path_swap::facility::rack_1_server_1_efficiency | eta_02_in | dc3_serial_path_swap::'Serial Path 8'::eta_01_in
// finding: dc3_serial_path_swap::facility::rack_1_server_1_efficiency | eta_01_in | dc3_serial_path_swap::'Serial Path 8'::eta_02_in
// unverifiable: none
package dc3_serial_path_swap {
    private import ScalarValues::*;
    calc def 'Serial Path 8' {
        in eta_01_in : Real;
        in eta_02_in : Real;
        in eta_03_in : Real;
        in eta_04_in : Real;
        in eta_05_in : Real;
        in eta_06_in : Real;
        in eta_07_in : Real;
        in eta_08_in : Real;
        out attribute path_efficiency : Real = eta_01_in * eta_02_in * eta_03_in * eta_04_in * eta_05_in * eta_06_in * eta_07_in * eta_08_in;
    }
    part facility {
        attribute e1 : Real = 0.99;
        attribute e2 : Real = 0.98;
        attribute e3 : Real = 0.97;
        attribute e4 : Real = 0.96;
        attribute e5 : Real = 0.95;
        attribute e6 : Real = 0.94;
        attribute e7 : Real = 0.93;
        attribute e8 : Real = 0.92;
        calc rack_1_server_1_efficiency : 'Serial Path 8' {
            in eta_02_in = e2;
            in eta_01_in = e1;
            in eta_03_in = e3;
            in eta_04_in = e4;
            in eta_05_in = e5;
            in eta_06_in = e6;
            in eta_07_in = e7;
            in eta_08_in = e8;
        }
    }
}
