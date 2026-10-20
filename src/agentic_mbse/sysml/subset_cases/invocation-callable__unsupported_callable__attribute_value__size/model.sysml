package fx {
    private import ScalarValues::*;
    part def Site {
        attribute a : Real = 0.9;
        attribute b : Real = 0.8;
        attribute n : Real = SequenceFunctions::size((a, b));
    }
    part site : Site;
}
