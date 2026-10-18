# Visualize V2 — Instruction File

Produce exactly one standalone HTML explanation from the approved synthesis. Write only to the assigned output path and never overwrite an existing file.

## Purpose

Preserve the synthesis's mental model and teaching sequence while adding the source-grounded detail and visual explanation it deliberately left out. Follow its source pointers. If a pointer is missing or disagrees with the synthesis, expose the gap or disagreement instead of inventing facts or choosing a side.

Read the project-local synthesis and HTML feedback named in the brief when those files exist. Do not read shared feedback.

## Reading experience

Design one coherent page for an intelligent reader without source context. Make the answer and reason to care visible early. Use diagrams, examples, tables, navigation, or progressive disclosure where they make the explanation easier to follow. Give every visual a clear job, consistent encoding, readable labels, and a nearby text explanation. Do not add a visual form merely to satisfy a catalog.

The result must add content, not just layout. For each main section, be able to name the detail or relationship the HTML adds beyond the synthesis.

Keep meaningful uncertainty and source disagreements visible in reader-facing language. Omit internal provenance grades and owner-versus-agent authority labels.

## Outcome qualities

- **Important stuff up front.** Do not assume the reader finishes the page. If they stop at any point, they should already have consumed the most important information available for understanding the subject.
- **One explanatory spine.** Preserve and strengthen the synthesis's central model. Do not turn its requested coverage, repositories, evidence, or chronology into the page's section structure.
- **A concrete thread.** Carry the synthesis's strongest example through the page, or place it immediately after the high-level model and before deeper detail. Do not bury the example behind reference material.
- **A connected page.** Use working references to later sections when a concept appears before its full explanation. Keep the main story visible without opening disclosures, and provide persistent navigation when the page is long enough to need it.
- **Real transitions.** Make each section follow from the one before it and explain why the next idea matters. Layout cannot substitute for a narrative connection between adjacent sections.
- **Clear on one reading.** Assume no source context, define unfamiliar terms, and make every heading and sentence understandable without rereading. Headings state real claims rather than merely naming topics.
- **Concrete detail.** Begin from the exact names, definitions, invariants, and governing truths already stated in the synthesis; the HTML must not be the first place they appear. Expand them into the source-grounded particulars that make them easier to inspect. A category gets its members; a data model gets its fields and shapes; a flow gets its steps, labels, states, and outcomes; a comparison gets its axes and values. Include relevant code shapes and meaningful real numbers.
- **Aggressive subtraction.** Add only detail that improves the explanation, a visual, or the chosen example. Once a point has landed, stop. Put useful reference material in an appendix or disclosure and omit detail that merely proves more research was done.
- **Faithful distinctions.** Preserve the synthesis's claims and distinguish current behavior, intended design, measurements, uncertainty, and source disagreement. Do not invent facts or rationale.
- **Self-contained visuals.** Every visual has one clear explanatory job and can be understood without chat context. Put labels on the visual where they are needed, use the same visual encoding consistently, and explain its parts and reading order in nearby body text rather than hiding essential meaning in a caption.
- **Substantive expansion.** Every main section adds inspectable content or a clearer relationship beyond the synthesis. Restyling the same words does not count.

## Output shape

- **Checkpoint:** Include the question and date from metadata plus the synthesis's `# Judgment` section. Omit internal evidence lists, source paths, context policy, search limits, and provenance grades.
- **Plain document:** Omit the question, date, and judgment entirely. The coordinator returns the judgment in conversation.

Ignore any trailing `# Renders` bookkeeping. Do not duplicate content under either shape.

## Hard constraints

- Produce self-contained static HTML and CSS. Use no scripts, event handlers, forms, iframes, objects, embeds, remote URLs, external images, fonts, stylesheets, or fetches. Relative repository links are allowed.
- Summarize source material in your own words. Do not paste source text wholesale or expose credential-like material.
- Use semantic headings in a sensible order, real text rather than text baked into images, readable contrast, and a linear reading order that works without the visual layout.
- Give each diagram a text equivalent so color, position, and shape are not the only carriers of meaning.

Before finishing, inspect the source for prohibited content and confirm that the page satisfies these outcome qualities and the assigned shape.

Return only the output path, one or two lines naming the detail layer you added, and any hard constraint you could not meet. On failure, return `FAILURE:` and the reason.
