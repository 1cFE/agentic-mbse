package f1e {
    private import ScalarValues::*;
    calc def Twice { in v : Real; return r : Real = 2.0 * v; }
    part def Rack { attribute p : Real = 1.0; calc t : Twice { in v = p; } }
    part def Row { part racks : Rack[0]; }
    part row : Row;
    part def Hall { part a : Rack[1..3]; part b : Rack[*]; part c : Rack[2] ordered; part d : Rack[0..1]; }
    part hall : Hall;
}
