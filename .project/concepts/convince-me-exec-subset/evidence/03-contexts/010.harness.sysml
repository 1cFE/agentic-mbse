    // Fixture: a calc gives the generator something to emit, so we can see whether `material` survives.
    calc def Double { in x : Real; out y : Real = x * 2.0; }
    part c : 'Component Name' {
        :>> mass = 12.5;
        :>> material = "steel";
        calc d : Double { in x = mass; }
        attribute doubled : Real = d.y;
    }
