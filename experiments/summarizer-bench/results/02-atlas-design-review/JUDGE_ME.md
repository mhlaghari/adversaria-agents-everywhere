# Judge pack — 02-atlas-design-review

Blind evaluation: candidates are labeled with letters only (mapping in
labels.json — DO NOT open it until you have scored). Paste everything below,
plus the transcript file, into your judge LLM.

---

You are judging meeting summaries against their source transcript. Score each
candidate 1-10 on: COVERAGE (key content captured), FAITHFULNESS (nothing
invented — verify names/numbers/decisions against the transcript; hallucination
caps the score at 4), ACTION ITEMS (each real task captured with the right
owner, no fake ones), STRUCTURE (clean sections). Then give an OVERALL 1-10 and
a one-line verdict per candidate. Judge strictly and independently.

TRANSCRIPT: see accompanying file `transcript.txt`.


## Candidate A

### v2 onboarding flow  
### Key Topics Discussed  
- The v2 onboarding flow is discussed, with three steps before the product.  
- The content being cut from the flow is moved into empty states.  
- The empty project screen shows three starter templates.  

### Decisions Made  
- We agreed to implement a three-step flow.  
- Omar will add drop-off analytics on step two before shipping.  

### Action Items  
- The Figma file will be updated with the three-step flow so Omar can scope the build.  
- The event spec will be added to the Figma file as part of the handoff.  

### Follow-ups Needed  
- Omar will write the event spec into the Figma file so it's part of the handoff.


## Candidate B

### Key Topics Discussed  
- **Facts**: Drop-off issue from v1 is attributed to the tour, which is seven steps before the product. Proposed three-step flow: workspace name, invite, first project. Empty states show three starter templates. Copy needs a real writing pass. Figma updated with three-step flow by Friday. Step two should be instrumented properly. Omar should add drop-off analytics before shipping, not after. Event spec written into Figma for handoff.  

### Decisions Made  
- **Action Items**:  
  - Omar should add drop-off analytics before shipping, not after.  
  - Figma updated with three-step flow by Friday.  
  - Step two should be instrumented properly.  

### Follow-ups Needed  
- **Action Items**:  
  - Ensure step two is properly instrumented.  
  - Implement drop-off analytics before shipping.


## Candidate C

### Key Topics Discussed
- Analytics show 1/3 new users drop off before creating anything
- Tour has 7 steps before touching product
- Proposal cuts tour to 3 steps: workspace name, invite, first project
- Tour content moves to empty project screen as starter templates

### Decisions Made
- Cut tour from 7 steps to 3 steps (workspace name, invite, first project)
- Move tour content to empty project screen as starter templates

### Action Items
- Me: Take copy for empty states (short, verb-first, one line each)
- Them: Update Figma with 3-step flow by Friday
- Them: Write event spec into Figma for handoff

### Follow-ups Needed
None mentioned


## Candidate D

### v2 onboarding flow review

### Key Topics Discussed
- v2 onboarding flow review
- v1 drop-off: analytics show one-third of new users lose before creating anything
- Current feature tour has seven steps before product touch
- Proposal to reduce feature tour to three steps: workspace name, invite, first project
- Feature tour content cut moves to empty states
- Empty project screen shows three starter templates (clickable) instead of a wizard
- Placeholder text for empty states requires real writing pass (short, verb-first, one line each)

### Decisions Made
- Commit to having Omar add drop-off analytics on step two before shipping, not after

### Action Items
- Me: take copy for empty states
- Them: update Figma with three-step flow by Friday
- Them: write event spec into Figma file for handoff

### Follow-ups Needed
- Update Figma with three-step flow by Friday
- Write event spec into Figma file for handoff
