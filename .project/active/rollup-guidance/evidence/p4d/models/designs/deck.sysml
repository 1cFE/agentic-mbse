package DeckDesign {
    private import ScalarValues::*;
    private import NumericalFunctions::sum;
    private import RollupExample::*;

    part def Deck :> 'Costed Item' {
        part panel : Panel[4];
        part caster : Caster[4];
        attribute panel_capital : Real = sum(panel.capital_cost);
        attribute caster_capital : Real = sum(caster.capital_cost);
        :>> capital_cost = panel_capital + caster_capital;
    }

    part deck : Deck;
}
