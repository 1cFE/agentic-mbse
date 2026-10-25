package CartDesign {
    private import ScalarValues::*;
    private import RollupExample::*;

    part def Cart :> 'Costed Item' {
        part deck_assembly : Deck;
        part frame_assembly : Frame;
        attribute deck_capital : Real = deck_assembly.capital_cost;
        attribute frame_capital : Real = frame_assembly.capital_cost;
        :>> capital_cost = deck_capital + frame_capital;
    }

    part cart : Cart;
}
