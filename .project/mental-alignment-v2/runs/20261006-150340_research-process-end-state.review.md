# Review — 20261006-150340_research-process-end-state.md

artifact: /home/reid/1cfe/agentic-mbse/.project/mental-alignment-v2/runs/20261006-150340_research-process-end-state.md
question: "yes, we need this capability in agentic-mbse. can you run /_my_mental_model_v2 for what the end-state agentic-mbse research process will look like?"
reviewed against: /home/reid/.claude/skills/_my_mental_model_v2/design_synthesis.md, /home/reid/.claude/skills/_my_mental_model_v2/feedback/synthesis.md (no project-local feedback)

## Findings

1. The end state, which is what the question asks about, first appears at line 115 of 177. Lines 40-113 describe two repos as they are today, and the walk through one request comes last (lines 141-151). A reader who stops after the third section has the current-state inventory and not the end state. (cites: prompt "Important stuff up front", "An explainer, not a dossier", "A concrete thread: do not postpone the best example until after the reference material")

2. The concrete example is not used as a thread. The real request `REQ-036-01` is shown once at lines 58-66 as an illustration of a field list. The end-state walk (lines 143-149) then switches to an abstract `REQ-<n>` and "a quantity", so the one real example never carries the explanation. (cites: prompt "A concrete thread")

3. The section on what fusion-tea built (lines 52-105) piles up detail after the point has landed. Examples are the 900 s timeout, the `.staging/<uuid>/` path, the `:86-140` and `:234-247` line ranges, the full five-step registration ladder, the `retire` and `verify` verbs with `RETIRED.jsonl`, and the complete precedence table. Several of these do not feed the end-state model. This section is also the longest in the document. (cites: prompt "Editorial selection", "Produce the shortest artifact"; feedback "Detail continues after the point lands")

4. The body counts things without naming them, and the counts contradict each other.
   - The TLDR (line 25) says acquisition is "three scripts and one command". The heading at line 52 says "one command and two scripts".
   - The TLDR says "exactly one of four outcomes" and never names the four. They appear only at lines 77-83.
   - The heading at line 115 says "two hooks made optional" without naming them.
   (cites: feedback "Count standing in for the members"; prompt "Exact names and definitions")

5. The TLDR cannot be read alone, although the prompt says it is for "a reader who sees nothing else". It uses terms the document defines late or never.
   - `WRAP-SPLIT` and "Item 5" are not explained anywhere.
   - "Research seam" is used as if known.
   - "ARIES hold-out screen" appears in the TLDR. "Hold-out" and "fail-closed" are never explained in plain words.
   - `/run-goal` is only described at line 109.
   The body also leans on undefined project-internal labels: "product-lens smell 1" (lines 136, 156), "`epic-F1`" (line 121), "Item 2" (line 136), and `trail.md` with its `### T-00N scope` entries (line 143). (cites: prompt "Clear on one reading", "Write for an intelligent reader who lacks the source context", "# TLDR"; prompt rule to define unfamiliar terms)

6. The reason to care (traceability under agent operation) is not in the TLDR. It sits in the third paragraph of the first section (line 36), and the failure it prevents is described only in the abstract: "a number in the model with no path back to a file". The TLDR gives mechanism and a boundary rule without saying what goes wrong without them. (cites: prompt "Important stuff up front: the strongest available reason to believe or care"; feedback "Opening with no reason to care")

7. Several sections open without carrying forward from the one before.
   - "Where `/run-goal` plugs in" (line 107) starts cold after the acquisition section.
   - "The end state" (line 115) opens with "This section is the intended design" rather than the result of the previous section.
   - The two current-state sections each open with a "This is current code in/of..." label. The first one does end on the gap it hands to the next section (line 50).
   - The earlier sections also do not set up the end-state table at lines 127-137, which lists nine moves, most of them not introduced before. (cites: prompt "A connected explanation"; feedback "Sections do not lead into each other")

8. Several headings name a topic or use a coined phrase and state no claim.
   - "Where `/run-goal` plugs in" (107)
   - "The end-state walk, for one request" (141)
   - "What moves where" (125)
   - "bounded by construction" (56)
   - "one write door" (87)
   - "the boundary made operational" (105)
   Within the text, "consumer-shaped fields" (159) and "smell-1 situation" (156) are further coined or internal terms. (cites: prompt "A heading states the section's real claim rather than naming a topic... or introducing a coined label"; feedback "Heading that names what is present", "Abstraction performing a verb")

9. The walk overclaims what is unchanged. Line 151 says "Nothing in this walk is new behaviour" and that steps 3-5 are fusion-tea's scripts under new names. The same walk's step 4 says the registry hold-out-checks "if the target configured a guard", which the table at line 132 lists as a new `HoldoutGuard` protocol with a default no-op. The CLI names `agentic-mbse research ...` are also new. The sentence therefore contradicts the document's own design table. (cites: prompt "state whether each claim describes current code, intended design, an owner decision, or your inference", "Preserve contradictions"; prompt "Use the right scope")

10. The status label is missing on the section about `/run-goal`. Lines 111-112 state a mapping from return class to task outcome, as fact attributed to "the goal layer's reading". The appendix (line 165) labels the same mapping an inference that the runbook leaves open. The reader of the main narrative gets the stronger claim. (cites: prompt "state whether each claim describes current code, intended design, an owner decision, or your inference")

11. A possible conflict with the central rule is left unaddressed. Lines 33 and 87-89 present `register` as "the one write door into `knowledge/`" and "write the index by hand" as forbidden. Line 47 says `agentic-mbse extract --save-source` already writes sources, and line 46 says `/manage-sources` hand-edits the index. Judgment covers `/manage-sources` (line 156). It does not mention `extract --save-source` as a second write path, and the section at line 40 calls the shipped reading stage "complete". (cites: prompt "Preserve contradictions, missing evidence, and uncertainty instead of quietly resolving them"; feedback "Use the right scope" rule in prompt)

12. Visual cues are given for only two sections, but the prompt asks for them as section-level render guidance. The end-state walk (line 141, a seven-step sequence) and the return-class table (lines 77-83) carry none. The one dropdown candidate is in the Appendix and is not tied to a section. (cites: prompt "Section-level source pointers and visual cues... Mark short optional explanations as dropdown candidates")
