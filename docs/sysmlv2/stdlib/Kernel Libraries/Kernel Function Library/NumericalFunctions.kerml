standard library package NumericalFunctions {
	doc
	/*
	 * This package defines abstract functions on Numerical values for general arithmetic and comparison operations.
	 */

	public import ScalarValues::*;
	private import ControlFunctions::reduce;
	
	abstract function isZero{ in x: NumericalValue[1]; return : Boolean; }
	abstract function isUnit{ in x : NumericalValue[1]; return : Boolean; }
	
	abstract function abs{ in x: NumericalValue[1]; return : NumericalValue[1]; }
		
	abstract function '+' specializes ScalarFunctions::'+' { in x: NumericalValue[1]; in y: NumericalValue[0..1]; return : NumericalValue[1]; }
	abstract function '-' specializes ScalarFunctions::'-' { in x: NumericalValue[1]; in y: NumericalValue[0..1]; return : NumericalValue[1]; }
	abstract function '*' specializes ScalarFunctions::'*' { in x: NumericalValue[1]; in y: NumericalValue[1]; return : NumericalValue[1]; }
	abstract function '/' specializes ScalarFunctions::'/' { in x: NumericalValue[1]; in y: NumericalValue[1]; return : NumericalValue[1]; }
	abstract function '**' specializes ScalarFunctions::'**' { in x: NumericalValue[1]; in y: NumericalValue[1]; return : NumericalValue[1]; }
	abstract function '^' specializes ScalarFunctions::'^' { in x: NumericalValue[1]; in y: NumericalValue[1]; return : NumericalValue[1]; }
	abstract function '%' specializes ScalarFunctions::'%' { in x: NumericalValue[1]; in y: NumericalValue[1]; return : NumericalValue[1]; }
	
	abstract function '<' specializes ScalarFunctions::'<' { in x: NumericalValue[1]; in y: NumericalValue[1]; return : Boolean[1]; }
	abstract function '>' specializes ScalarFunctions::'>' { in x: NumericalValue[1]; in y: NumericalValue[1]; return : Boolean[1]; }
	abstract function '<=' specializes ScalarFunctions::'<=' { in x: NumericalValue[1]; in y: NumericalValue[1]; return : Boolean[1]; }
	abstract function '>=' specializes ScalarFunctions::'>=' { in x: NumericalValue[1]; in y: NumericalValue[1]; return : Boolean[1]; }
	
	abstract function max specializes ScalarFunctions::max { in x: NumericalValue[1]; in y: NumericalValue[1]; return : NumericalValue[1]; }
	abstract function min specializes ScalarFunctions::min { in x: NumericalValue[1]; in y: NumericalValue[1]; return : NumericalValue[1]; }
	
	abstract function sum { in collection: NumericalValue[0..*]; return : NumericalValue[1]; }	
	abstract function product { in collection: NumericalValue[0..*]; return : NumericalValue[1]; }
	
	function sum0 { in collection: NumericalValue[0..*]; in zero: NumericalValue[1]; 
 		inv { isZero(zero) }		
        return : NumericalValue = collection->reduce '+' ?? zero;
	}
	
	function product1 { in collection: NumericalValue[0..*]; in one: NumericalValue[1]; 
		inv { isUnit(one) }		
        return : NumericalValue = collection->reduce '*' ?? one;
	}
}