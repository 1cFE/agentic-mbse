    part def Host {
        attribute a : Real = 3.0;
        attribute b : Real = 5.0;
        calc ct : ConditionalTest {
            in x = a;
            in y = b;
        }
        attribute d : Real = ct.diff;
    }
    part host : Host;
