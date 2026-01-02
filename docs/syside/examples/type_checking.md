<div id="type-checking" class="section">

# Type Checking[](#type-checking "Link to this heading")

This simple Python script shows off Syside’s type checking capabilities. In the provided example model, there are six packages:

  - `Non-Conforming Types 1`

  - `Non-Conforming Types 2`

  - `Conforming Types 1`

  - `Collect`

  - `Select`

  - `Arrays`

In the first package, the `a` attribute is a `Boolean` and the `b` attribute is defined to be a `String`. However, we are assigning `a` to `b`, which is not allowed because `Boolean` does not conform to `String`.

In the second package, the `b` attribute is defined to be a `Positive`. However, we are assigning a value of `-42` to it, which is inferred to be an `Integer` and thus is not conformant to `Positive`. The `a` attribute is defined and assigned correctly.

The third package is allowed because both attributes are `Positive` and conform to the `ScalarValues::Positive` type.

The fourth package `Collect` shows type inference working on standard `collect` function. In both cases, the feature values are inferred to return types `A`, thus only attribute `b` is diagnosed with an invalid type.

Similarly to the previous package, `Select` shows type inference correctly identifying that the expression of `a` selects only `Positive` values, and thus it is not an error to assign the result to `a`. Expression of `b` does no such checking, therefore it if inferred to return `Integer` values from the negative range lower bound which is diagnosed as a type error when being assigned to `Positive`.

The last package `Arrays` shows inference working on owned argument features, and collection and array indexing correctly inferring the return type to be `Arrays::array::elements` which conforms to `Positive`, hence no type errors. Note that because `operator #` is statically ambiguous, this inference only works by explicitly calling `CollectionFunctions::'#'` and `CollectionFunctions::'array#'` functions. The ambiguity stems from the operator handling single ordered collections and arrays differently to all other sequences, of which the multiplicity cannot be statically known in all cases since everything is both a sequence and a single value at the same time in SysML v2.

Most other standard library functions that are definitions of operator functions, or operate on sequences, are also treated as special functions by the type inference to reduce the boilerplate needed to satisfy the type checker.

<div class="admonition note">

Note

Before running this example, make sure you have activated the Syside license by running `syside-license check` according to the instructions in the [<span class="std std-ref">License Activation</span>](/v0.8.1/automator/install.md) section.

</div>

<div id="concepts-used" class="section">

## Concepts Used[](#concepts-used "Link to this heading")

This example only uses the `load_model` function.

</div>

<div id="example-model" class="section">

## Example Model[](#example-model "Link to this heading")

<div class="highlight-sysml notranslate">

<div class="highlight">

    package 'Non-Conforming Types 1' {
        private import ScalarValues::*;
    
        attribute a : Boolean = true;
        attribute b : String = a;
    }
    
    package 'Non-Conforming Types 2' {
        private import ScalarValues::*;
    
        attribute a : Positive = 42;
        attribute b : Positive = -42;
    }
    
    package 'Conforming Types 1' {
        private import ScalarValues::*;
    
        attribute a : Positive = 42 + 0;
        attribute b : Positive = a;
    }
    
    package Collect {
        private import ControlFunctions::collect;
        private import ScalarValues::Positive;
    
        attribute def A { attribute value : Positive; }
        attribute def B;
    
        attribute a : A [*] = (1..10)->collect { in attribute x : Positive; new A(x) };
        attribute b : B [*] = (1..10)->collect { in attribute x : Positive; new A(x) };
    }
    
    package Select {
        private import ControlFunctions::select;
        private import ScalarValues::*;
    
        attribute a : Positive [*] = (-1..10)->select { in attribute x : Integer; x istype Positive };
        attribute b : Positive [*] = (-1..10)->select { true };
    }
    
    package Arrays {
        private import Collections::Array;
        private import ScalarValues::*;
    
        attribute array : Array {
            :>> elements : Positive;
        }
    
        attribute a : Positive = array->CollectionFunctions::'#'(1);
        attribute b : Positive = array->CollectionFunctions::'array#'(1);
    }

</div>

</div>

</div>

<div id="example-script" class="section">

## Example Script[](#example-script "Link to this heading")

<div class="highlight-python notranslate">

<div class="highlight">

    import pathlib
    import syside
    
    MODEL = "example_model.sysml"
    EXAMPLE_DIR = pathlib.Path(__file__).parent
    MODEL_FILE_PATH = EXAMPLE_DIR / MODEL
    
    
    def main() -> None:
        (_, diagnostics) = syside.try_load_model([MODEL_FILE_PATH])
    
        # Convert diagnostics to use relative paths
        relative_diagnostics = str(diagnostics).replace(str(EXAMPLE_DIR) + "/", "")
        print(relative_diagnostics)
    
    
    if __name__ == "__main__":
        main()

</div>

</div>

</div>

<div id="output" class="section">

## Output[](#output "Link to this heading")

<div class="highlight-text notranslate">

<div class="highlight">

    example_model.sysml:5:28: error (type-error): 'Non-Conforming Types 1'::a does not conform to ScalarValues::String
    example_model.sysml:12:30: error (type-error): ScalarValues::Integer does not conform to ScalarValues::Positive
    example_model.sysml:30:27: error (type-error): Collect::A does not conform to Collect::B
    example_model.sysml:38:34: error (type-error): ScalarValues::Integer does not conform to ScalarValues::Positive

</div>

</div>

</div>

<div id="download" class="section">

## Download[](#download "Link to this heading")

Download this example [here](/v0.8.1/examples/type_checking.zip).

</div>

</div>
