# HTML Feedback — Shared

These are patterns from real renders. Each entry quotes what the owner rejected and what they asked for instead. The reviewer reads this file. The render agent does not.

Every entry has a heading that names the pattern, a direction (`Avoid.` or `Prefer.`), a line telling you what to do, the quoted forms, and a `From:` line. Quotes are verbatim. Some entries carry no `Good:` line, because the owner rejected something without writing a replacement.

The owner promotes entries outside a run, in the pack repo. Move a generalized rule into `visualize.md`. Leave an instance here. Either way, delete the entry from the project-local file. No agent writes to this file during a run.

A render's headings and prose carry the same patterns a synthesis does, and the synthesis entries cover those. Here you will find the patterns that belong to a rendered page.

## Main-flow heading behind a closed dropdown

Avoid. Never collapse a heading that is part of the main flow.

- Bad: all 16 sections behind `<details>`, none open, with 2 diagrams in 121 KB. The reader got no skimmable story and had to open every section to find a visual.
- From: 2026-08-25, HTML render

## Caption carrying the fact that decodes the figure

Avoid. Often the reader needs one fact to decode a chart. Put that fact in the body next to the chart, or on the chart itself. Keep it out of the caption.

- Bad: `the model applies the minimum-draw acceptance curve at every draw` buried in a caption paragraph. It was the fact that resolved the chart, and the owner could not decode the chart.
- Good: a short reading guide in the body next to the chart — what each line is, in the order a reader should look — with the lines labeled on the chart itself, and the caption kept to one or two sentences.
- From: 2026-09-01, HTML render

## Dropdown summary line written as a double clause

Avoid. Write a summary line the way you write a heading: a bare noun phrase, or one dead-simple claim.

- Bad: colon-joined double clauses and counts in the summary lines. No individual summary was quoted in the feedback.
- From: 2026-09-01, HTML render

## Structural heading turned into a claim

Avoid. Leave `TLDR`, `Judgment`, and `Appendix` as plain names. Go straight from the heading into the content, and write no sentence introducing it.

- Bad: `Five points carry the whole answer` as the heading over the TLDR box
- Good: `TLDR`
- From: 2026-08-25, HTML render

## Concept left for the reader to scroll for

Avoid. Where a concept first appears, name the section that breaks it down, and link to that section. Make every section reference a working link. Do not write a bare section number in prose.

- Bad: the runner protocol mentioned in the narrative, leaving the reader to scroll for the section that explains it.
- Good: `The runner protocol is the second new piece — section 5 covers the envelope, the outcomes, and the timeout.` with `section 5` as a working in-page link.
- From: 2026-08-25, HTML render
