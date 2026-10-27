package RollupExample {
    private import ScalarValues::*;
    private import NumericalFunctions::sum;

    abstract part def 'Costed Item' {
        attribute capital_cost : Real;
    }

    calc def UnitCost {
        in size_in : Real;
        in rate_in : Real;
        out attribute cost : Real = size_in * rate_in;
    }

    part def Panel :> 'Costed Item' {
        attribute area : Real;
        calc cost_model : UnitCost { in size_in = area; in rate_in = 12.0; }
        :>> capital_cost = cost_model.cost;
    }

    part def Caster :> 'Costed Item' {
        attribute load_rating : Real;
        calc cost_model : UnitCost { in size_in = load_rating; in rate_in = 0.75; }
        :>> capital_cost = cost_model.cost;
    }

    part def Rail :> 'Costed Item' {
        attribute length : Real;
        calc cost_model : UnitCost { in size_in = length; in rate_in = 25.0; }
        :>> capital_cost = cost_model.cost;
    }

    part def Brace :> 'Costed Item' {
        attribute brace_count : Real;
        calc cost_model : UnitCost { in size_in = brace_count; in rate_in = 5.0; }
        :>> capital_cost = cost_model.cost;
    }

    part def Deck :> 'Costed Item' {
        part panel : Panel[4];
        part caster : Caster[4];
        attribute panel_capital : Real = sum(panel.capital_cost);
        attribute caster_capital : Real = sum(caster.capital_cost);
        :>> capital_cost = panel_capital + caster_capital;
    }

    part def Frame :> 'Costed Item' {
        part rail : Rail;
        part brace : Brace;
        :>> capital_cost = rail.capital_cost + brace.capital_cost;
    }

    part def Cart :> 'Costed Item' {
        part deck_assembly : Deck;
        part frame_assembly : Frame;
        :>> capital_cost = deck_assembly.capital_cost + frame_assembly.capital_cost;
    }
}
