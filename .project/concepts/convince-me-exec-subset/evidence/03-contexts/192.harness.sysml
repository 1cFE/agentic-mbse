    part def Host {
        attribute t : Real = 500.0;
        calc cc : CorrectConstraint {
            in temperature = t;
        }
    }
    part host : Host;
