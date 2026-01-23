<div id="type-checking" class="section">

# Type Checking<a href="#type-checking" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

This simple Python script shows off Syside’s type checking capabilities. In the provided example model, there are six packages:

- <span class="pre">`Non-Conforming`</span>` `<span class="pre">`Types`</span>` `<span class="pre">`1`</span>

- <span class="pre">`Non-Conforming`</span>` `<span class="pre">`Types`</span>` `<span class="pre">`2`</span>

- <span class="pre">`Conforming`</span>` `<span class="pre">`Types`</span>` `<span class="pre">`1`</span>

- <span class="pre">`Collect`</span>

- <span class="pre">`Select`</span>

- <span class="pre">`Arrays`</span>

In the first package, the <span class="pre">`a`</span> attribute is a <span class="pre">`Boolean`</span> and the <span class="pre">`b`</span> attribute is defined to be a <span class="pre">`String`</span>. However, we are assigning <span class="pre">`a`</span> to <span class="pre">`b`</span>, which is not allowed because <span class="pre">`Boolean`</span> does not conform to <span class="pre">`String`</span>.

In the second package, the <span class="pre">`b`</span> attribute is defined to be a <span class="pre">`Positive`</span>. However, we are assigning a value of <span class="pre">`-42`</span> to it, which is inferred to be an <span class="pre">`Integer`</span> and thus is not conformant to <span class="pre">`Positive`</span>. The <span class="pre">`a`</span> attribute is defined and assigned correctly.

The third package is allowed because both attributes are <span class="pre">`Positive`</span> and conform to the <span class="pre">`ScalarValues::Positive`</span> type.

The fourth package <span class="pre">`Collect`</span> shows type inference working on standard <span class="pre">`collect`</span> function. In both cases, the feature values are inferred to return types <span class="pre">`A`</span>, thus only attribute <span class="pre">`b`</span> is diagnosed with an invalid type.

Similarly to the previous package, <span class="pre">`Select`</span> shows type inference correctly identifying that the expression of <span class="pre">`a`</span> selects only <span class="pre">`Positive`</span> values, and thus it is not an error to assign the result to <span class="pre">`a`</span>. Expression of <span class="pre">`b`</span> does no such checking, therefore it if inferred to return <span class="pre">`Integer`</span> values from the negative range lower bound which is diagnosed as a type error when being assigned to <span class="pre">`Positive`</span>.

The last package <span class="pre">`Arrays`</span> shows inference working on owned argument features, and collection and array indexing correctly inferring the return type to be <span class="pre">`Arrays::array::elements`</span> which conforms to <span class="pre">`Positive`</span>, hence no type errors. Note that because <span class="pre">`operator`</span>` `<span class="pre">`#`</span> is statically ambiguous, this inference only works by explicitly calling <span class="pre">`CollectionFunctions::'#'`</span> and <span class="pre">`CollectionFunctions::'array#'`</span> functions. The ambiguity stems from the operator handling single ordered collections and arrays differently to all other sequences, of which the multiplicity cannot be statically known in all cases since everything is both a sequence and a single value at the same time in SysML v2.

Most other standard library functions that are definitions of operator functions, or operate on sequences, are also treated as special functions by the type inference to reduce the boilerplate needed to satisfy the type checker.

<div id="concepts-used" class="section">

## Concepts Used<a href="#concepts-used" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

This example only uses the <span class="pre">`load_model`</span> function.

</div>

<div id="example-model" class="section">

## Example Model<a href="#example-model" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

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

## Example Script<a href="#example-script" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

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

## Output<a href="#output" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

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

## Download<a href="#download" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

Download this example <a href="/examples/type_checking.zip" class="reference external">here</a>.

</div>

</div>
