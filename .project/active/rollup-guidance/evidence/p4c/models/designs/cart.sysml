package CartDesign {
    private import ScalarValues::*;
    private import RollupExample::*;

    part cart : 'Costed Item' {
        part deck_assembly : Deck;
        part frame_assembly : Frame;
        :>> capital_cost = deck_assembly.capital_cost + frame_assembly.capital_cost;
    }
}
