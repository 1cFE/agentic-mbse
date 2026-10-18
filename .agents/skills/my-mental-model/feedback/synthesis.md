# Synthesis Feedback — Shared

These are patterns from real runs. Each entry quotes the line the owner rejected and the line they replaced it with. The reviewer reads this file. The synthesis agent does not.

Every entry has a heading that names the pattern, a direction (`Avoid.` or `Prefer.`), a line telling you what to do, the quoted lines, and a `From:` line. Quotes are verbatim. Some entries carry no `Good:` line, because the owner rejected something without writing a replacement.

The owner promotes entries outside a run, in the pack repo. Move a generalized rule into `design_synthesis.md`. Leave an instance here. Either way, delete the entry from the project-local file. No agent writes to this file during a run.

You will find headings covered twice below, and those two entries tell you opposite things. Both correct the same failure: the reader cannot understand the heading. One kind of heading says nothing at all. The other packs in so much that nobody can parse it. Fix one and you can overshoot into the other.

## Abstraction performing a verb

Avoid. Give the verb to whoever or whatever does the thing, the way an engineer would say it out loud. The owner called this "the exact Claude-ish voice I can't stand", and added that "the write-up is riddled with it". So sweep the whole document when you find one. If you fix only the line you were shown, the others stay.

- Bad: `stored energy decides the check`
- Bad: `the dominant lever is`
- Bad: `premises bend`
- Good: `whether the check passes depends on how much energy the store holds`
- From: 2026-08-30, synthesis

## Heading that stacks counts and coined terms

Avoid. This kind of heading is too dense to read once and understand. It sounds specific and gives the reader nothing they can use at that point in the document. The owner put it this way: "IF YOU REMEMBER ONE THING... 'JUST SAY THE THING'". Each correction below says what the section is about in the fewest plain words.

- Bad: `2 · One energy state under four linear constraints out-earns every other model tested`
- Good: `Our simplified linear model` — the owner: "that's it."
- Bad: `2.1 The energy balance is exact because LoFi has no standing loss — and real losses are the to-add piece` — "the to-add piece" called out as Claude-ish
- Good: `2.1 Losses are not included in this model`
- Bad: `2.2 The cap, the taper, and the floor are fitted objects encoded as envelopes that always err safe` — "dense, confusing, and hard to follow"
- Good: `2.2 The fitted terms err on the conservative side`
- From: 2026-09-01, synthesis

## Heading that names what is present

Avoid. This kind of heading is too vague to say anything. Name the consequence or the decision instead. Test it: if the heading would sit just as well above a different section, or a different system, it says nothing. Each correction below states a fact you can find inside that section.

- Bad: `The API exposes eight route groups for submitting, watching, and downloading jobs`
- Good: `Every route uses one read rule: the owner, anyone if the job is shared, or an admin`
- Bad: `The worker invokes the runner with two arguments and reads back one envelope`
- Good: `A missing or malformed envelope counts as unknown, which is not the same as a failure`
- Bad: `One environment flag switches the whole service between the cloud and a laptop`
- Good: `One flag rather than two, so authentication-off and cloud storage cannot be combined`
- Bad: `Spike 1 ran five phases and stopped`
- Good: `Spike 1 never ran email or teardown, and its container held no MATLAB at all`
- Bad: `A job can end in six ways, and only two of them re-run`
- Good: `A declared failure never retries; an unexplained exit retries once`
- From: 2026-08-25, HTML render

## Count standing in for the members

Avoid. Name the members. If you give only a count, the reader still has to ask which ones you mean.

- Bad: `3. The design reuses what the spikes proved and invents only two things` — which two?
- Good: `3. Only the job table and the runner protocol are new`
- Bad: `6. Four proof obligations remain, and MATLAB in Docker is the first` — which four?
- Good: `6. MATLAB in Docker, memory, worker kill, and the runner protocol are all untested`
- Bad: `Seven mechanisms are proven, four are composed, and two are invented`
- Good: `Only the job table and the runner protocol have no evidence behind them`
- Bad: `It sorts every mechanism into three groups and treats only the third group as design work.`
- Good: `Every mechanism is either proven by a spike, borrowed from elsewhere in the workspace, or new. Only the job table and the runner protocol are new.`
- From: 2026-08-24 synthesis; 2026-08-25 HTML render

## Thought compressed into a fragment

Avoid. Cut any thought that will not stand alone as a complete sentence. Do not compress it into a phrase.

- Bad: `The boundary to the simulation program. A written command line, and a written way of reporting what happened.`
- Bad: `The physics, and the verdict on whether the request was valid.`
- Bad: `Owns — the one fact nothing else may hold`
- Bad: `Two programs, one job table, two new boundaries.`
- Good: `The API and the worker talk only through one SQLite job table.`
- From: 2026-08-24, synthesis

## Document as its own subject

Avoid. Delete the sentence on sight. Do not rewrite it into a better version of itself.

- Bad: `Five points carry the whole answer. Five points and ten supporting facts sit in this box. Every section below it expands one of them.`
- Good: delete both sentences. The box is visible.
- From: 2026-08-25, HTML render

## Opening with no reason to care

Prefer. Establish why the subject exists and why the reader should care. Facts should support that motivation, not replace it.

- Bad: `A hardware engineer describes a plant once, in a model, and gets a runnable calculator out of it. The model holds the components, their attributes, and the formulas between them. The generated Python computes outcomes from design parameters: cost, net power, and the levelised cost of electricity (LCOE).` — the owner: "this is SO DRY. ... its purely descriptive: <fact>. <fact>. <fact>." and "in this first section, the only thing that touches on WHY (/ why is this intersting) is the comparison to 1costinFE"
- Good: no replacement prose was given. The owner asked: "START WITH WHY. What is the motivating problem? Why is this important? Why does this exist? Why is the problem solved the way it is? Why is our solution a good one? Why should anyone care?" They also warned: "let's not overindex on this and clutter the whole write-up."
- From: 2026-09-05, synthesis

## Structure presented as an inventory

Prefer. When a component split or other structure matters to understanding, explain why that structure exists before listing its members. Do not manufacture a why for every fact.

- Bad: `The model holds the components, their attributes, and the formulas between them.` — this says what is present without explaining why the system needs that structure.
- Good: no replacement prose was given. The owner wanted the explanation to answer: "Why is this needed? (design iterations in a hardware-centric modeling language, but we need a way to evaluate the model; our goal is "studies": varying engineering design decisions are parameters to observe the effects; therefore, we decided we wanted standalone python to be the target) What are the core problems to be solved? (parsing and interpreting the model; wiring the models (definitions versus instances); symbolic conversions; supporting functional blocks not represented in SysMLv2. e.g. in the future, could substitute a numerical package. (the hand calcs))"
- From: 2026-09-05, synthesis

## Repetitive sentence structure

Avoid. A run of same-shaped sentences makes the writing repetitive and bland. Vary sentence structure to make it more interesting to read.

- Bad: the opening quoted above — the owner: "there is zero variance to the writing. it's like every sentence has the same pattern and rythm"
- Good: no replacement prose was given. The owner asked: "writing becomes too repetitive and bland. try to vary sentence structure to make it more interesting to read"
- From: 2026-09-05, synthesis

## Clause the reader already has

Avoid. Cut it. The reader already has it if an earlier sentence said it, or if the layout shows it.

- Bad: `The concept defines done as these six criteria, and each one carries a grade.` — grading was already explained and the chips are visible
- Bad: `as the table below shows`
- Bad: `each with its source`
- Good: `The concept defines done as six criteria.`
- From: 2026-08-25, HTML render

## Negative clause added for rhythm

Avoid. Negate only when the absence is the finding. When it is, write the negation as its own sentence and say what follows from it.

- Bad: `The API exposes eight route groups, and none of them executes anything`
- Good: `Every route uses one read rule: the owner, anyone if the job is shared, or an admin`
- Bad: `The synthesis inspected the spike code and nothing else`
- Good: `The synthesis read app.py in full, plus the browser page, the tests, and the two container files`
- Bad: `A client sends a bearer token and nothing else.`
- Good: `Every client authenticates the same way, which is why adding the browser page cost no API change.`
- Good, where the absence is the finding: `The API holds no simulation code, so redeploying it cannot kill a job in flight.`
- From: 2026-08-25, HTML render

## Definition section headlined by a run result

Avoid. Say what the thing is first. Put measurements from runs after that, and label them as measurements so a reader can tell the two apart.

- Bad: the section defining the proposed model was headlined `out-earns every other model tested` and mixed run measurements into the definition prose, so a reader could not tell whether a sentence described what the model is or what the runs measured.
- Good: `Our simplified linear model`, with the measurements after it and labeled as measurements.
- From: 2026-09-01, synthesis

## Material that maps to no item in the owner's outline

Avoid. The owner's outline decides what the synthesis covers. Before you write, match every section you plan against an item in their outline. Leave out anything that matches nothing, or ask the owner about it first.

- Bad: against a six-item outline, the synthesis added a model-comparison and value-results thread — a money table, named baselines, AUD figures — in experiment-internal vocabulary (model nicknames, study names) that meant nothing to a reader who had not run the studies. The owner deleted the whole thread on review.
- From: 2026-09-01, synthesis
