package f1p {
    // P-6: rack_a's usage view holds two declarations in the `servers` slot, Rack::servers
    // and its redefinition Hall::racks::servers. The effective one is the redefinition
    // ([1]), and it is not the larger UUID, so a port that skips effective-declaration
    // selection and keeps the larger one instantiates Rack::servers ([2]) instead.
    part def Server;
    part def Rack { part servers : Server[2]; }
    part def Hall {
        part racks : Rack[2] { part :>> servers : Server[1]; }
        part rack_a : Rack :> racks;
    }
    part hall : Hall;
}
