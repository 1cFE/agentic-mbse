package gl {
    // The same two spellings outside designs/.
    private import ScalarValues::*;
    part def Gen {
        attribute fuel : String = "none";
        attribute label : String = "library";
        attribute rate : Real = 2.0;
    }
    part gen : Gen { :>> fuel = "hydrogen"; :>> rate = 3.0; }
}
