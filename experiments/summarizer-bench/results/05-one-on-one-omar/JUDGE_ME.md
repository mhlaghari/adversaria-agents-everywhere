# Judge pack — 05-one-on-one-omar

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

### Key Topics Discussed
- CI bill doubled since adding integration suite
- Current cost $800/month climbing
- Alternative is self-hosted runner on single beefy box
- Back-of-envelope calculation shows pays for itself in three months
- Feature work gets maybe 1/3 of "Them"'s week due to infra, reviews, and sync fixes

### Decisions Made
- Benchmark this week
- If numbers hold, migrate before month end

### Action Items
- Me: writes job description tomorrow and routes through usual channels
- Them: does technical screens

### Follow-ups Needed
None mentioned


## Candidate B

### Meeting Notes  

### title: CI Integration and Hiring Decisions  

### attendees: Me, Them  

### sections:  

#### Key Topics Discussed  
- The CI bill doubled since we added the integration suite. Eight hundred a month and climbing.  
- A self-hosted runner on a single beefy box. My back-of-envelope says it pays for itself in three months, but I want to benchmark before we commit.  

#### Decisions Made  
- We decided to open a mid-level backend role rather than senior — someone you can grow, at a salary we can sustain.  

#### Action Items  
- I'll write the job description tomorrow and route it through the usual channels.  

#### Follow-ups Needed  
- The CI bill is a follow-up needed.


## Candidate C

### Key Topics Discussed  
- **Facts**:  
  - CI bill doubled since integration suite added (800/month, climbing).  
  - Alternative: self-hosted runner on a single beefy box (3-month payback, benchmarking before commit).  

- **Explicit decisions**:  
  - Benchmark this week, migrate before month end.  
  - Open mid-level backend role instead of senior (salary sustainability).  

- **Tasks**:  
  - Write job description tomorrow.  
  - Route it through usual channels.  

- **Names**:  
  - CI bill, self-hosted runner, backend work, mid-level role, technical screens.


## Candidate D

### CI Bill and Hiring Discussion

**Key Topics Discussed**
- CI bill costs doubled since integration suite was added, now eight hundred per month and climbing.
- Feature work takes a third of the speaker's week due to infrastructure, code reviews, and sync fixes.

**Decisions Made**
- None mentioned

**Action Items**
- Me: Benchmark this week; if the numbers hold, migrate before month end.
- Them: Write job description tomorrow and route through usual channels.
- Me: Do technical screens.

**Follow-ups Needed**
- None mentioned
