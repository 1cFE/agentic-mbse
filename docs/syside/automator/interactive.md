<div id="interactive-version" class="section">

<span id="automator-interactive"></span>

# Interactive Version<a href="#interactive-version" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

The interactive version of Syside Automator provides a command-driven interface for engaging directly with SysML v2 models through a terminal.

Such approach enables quick inspection, validation and modification of the model using structured commands, eliminating the need to create and execute Python scripts for simple and quick use-cases.

**Learn about:**

- <a href="#interactive-error-checking" class="reference internal"><span class="std std-ref">Checking for Errors</span></a>: Quickly identify errors in the model

- <a href="#interactive-part-counting" class="reference internal"><span class="std std-ref">Counting Parts</span></a>: Run short scripts rather than full Python scripts

- <a href="#interactive-complex-commands" class="reference internal"><span class="std std-ref">Complex Commands</span></a>: Forming more complex commands interactively

------------------------------------------------------------------------

**Example Model**: copy this model into your <span class="pre">`example_model.sysml`</span> file to test out the features of Syside Interactive, or use your own model:

<div class="highlight-sysml notranslate">

<div class="highlight">

    package 'Part Tree Example' {
        part def Electrical;
        part def Mechanical;

        part Automobile {
            part 'Drive Train' {
                part Battery : Electrical;
                part Motor : Electrical;
            }

            part Chassis {
                part Suspension : Mechanical;
                part Body : Mechanical;
            }
        }
    }

</div>

</div>

<div id="checking-for-errors" class="section">

<span id="interactive-error-checking"></span>

## Checking for Errors<a href="#checking-for-errors" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

In <a href="/automator/first_example.md" class="reference internal"><span class="std std-ref">First Example</span></a>, we showcased how to check the model for errors using <span class="pre">`syside`</span>` `<span class="pre">`check`</span>. One other option is simply to try and load the model, since <a href="/python/v0.8.4/syside//README.md" class="apiref reference external"><span class="pre"><code class="sourceCode python">load_model</code></span></a> will automatically check the model for errors and report them.

To demonstrate this, remove the line <span class="pre">`part`</span>` `<span class="pre">`def`</span>` `<span class="pre">`Electrical;`</span> from the model, and try loading the model by running the following command:

<div class="highlight-bash notranslate">

<div class="highlight">

    python -m syside interactive example_model.sysml

</div>

</div>

This will automatically check the model for any errors. You should get an output similar to the following:

<div class="highlight-text notranslate">

<div class="highlight">

    example_model.sysml:7:26: error (reference-error): No Type named 'Electrical' found.
    7 |           part Battery : Electrical;
      |                          ^^^^^^^^^^

    example_model.sysml:8:24: error (reference-error): No Type named 'Electrical' found.
    8 |           part Motor : Electrical;
      |                        ^^^^^^^^^^

</div>

</div>

</div>

<div id="counting-parts" class="section">

<span id="interactive-part-counting"></span>

## Counting Parts<a href="#counting-parts" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

One advantage of the interactive version is the ability to run simple scripts that do not warrant a full Python script. For example, we can count the number of parts in the model by running the following command:

<div class="highlight-python notranslate">

<div class="highlight">

    >>> len(list(model.nodes(syside.PartUsage)))
    7

</div>

</div>

We see that it correctly counted the 7 parts in the model. Similarly, we can count the number of part definitions by running a slightly different command:

<div class="highlight-python notranslate">

<div class="highlight">

    >>> len(list(model.nodes(syside.PartDefinition)))
    2

</div>

</div>

You could also use the same idea to count <a href="/python/v0.8.4/syside/ActionUsage.md" class="apiref reference external"><span class="pre"><code class="sourceCode python">ActionUsage</code></span></a>, etc.

</div>

<div id="complex-commands" class="section">

<span id="interactive-complex-commands"></span>

## Complex Commands<a href="#complex-commands" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

Interactive mode works the same way as the Python API, so you can use the same functions and methods. However, sometimes you might need more than a single line of code to do something.

For example, we can list all the part definitions in the model by running the following command:

<div class="highlight-python notranslate">

<div class="highlight">

    >>> for element in model.nodes(syside.PartDefinition):
    ...     print(element.name if element.name else "anonymous")

    Electrical
    Mechanical

</div>

</div>

The interactive version will recognize when an extra line of code is needed (in this case - to define the for loop) and will prompt you to continue. To complete this loop, simply press <span class="kbd kbd docutils literal notranslate">Enter</span> after inputting an empty line.

Once you are done using the interactive mode, you can exit by typing <span class="pre">`exit`</span> and pressing <span class="kbd kbd docutils literal notranslate">Enter</span>.

</div>

</div>
