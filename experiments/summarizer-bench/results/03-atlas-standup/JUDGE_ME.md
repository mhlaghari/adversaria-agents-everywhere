# Judge pack — 03-atlas-standup

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

### Sync-retry Bug Fix and Component Audit Update

**Attendees:**
- Me
- Omar
- Sarah

### Key Topics Discussed
- Sync-retry bug root cause: backoff resets on every reconnect, causing flaky networks to hammer the server. Fix is a persisted backoff window.
- Component audit completed with forty-two components and a dozen candidates for deletion. Sarah needs a second pair of eyes before removals.
- Settings search ready for beta, target for release this sprint to gather feedback before launch build.
- Beta group reported no major blockers on the last drop.
- Keyboard shortcuts documentation requested by two people, indicating power user adoption (a positive sign).
- Shortcuts sheet to be folded into help panel during empty-state work.

### Decisions Made
None mentioned

### Action Items
- Omar: Have sync-retry bug fix in review today
- Sarah: Get a second pair of eyes before starting component removals
- Sarah: Send component audit to Me for review this week
- Me: Get settings search out this sprint for feedback before launch build
- Them: Fold shortcuts sheet into help panel when doing empty-state work

### Follow-ups Needed
None mentioned


## Candidate B

{
  "title": "Sync-Reset and Beta Enhancements",
  "attendees": [
    "Me",
    "Omar",
    "Sarah"
  ],
  "sections": [
    "Key Topics Discussed",
    "Decisions Made",
    "Action Items",
    "Follow-ups Needed"
  ]
}


## Candidate C

### Key Topics Discussed
- Omar root-caused sync-retry bug
- Backoff resets on every reconnect → flaky networks hammer server
- Component audit done (42 components, 12 candidates for deletion)
- Two people asked for keyboard shortcuts documentation → indicating power users
- Settings search ready for beta
- Beta group: no major blockers on last drop
- Priorities: retry fix first, then analytics on onboarding step two after Figma lands

### Decisions Made
None mentioned

### Action Items
- Omar will review the fix for persisted backoff window today
- Me will review Sarah's component audit this week
- Sarah will fold keyboard shortcuts sheet into help panel during empty-state work

### Follow-ups Needed
- Sarah needs second pair of eyes before deletion


## Candidate D

### Key Topics Discussed  
- **Facts**: Sync-retry bug is root-caused, with backoff resets causing flaky networks. Fix is a persisted backoff window to be reviewed.  
- **Decision**: Review the audit in the next week.  
- **Task**: Send the audit to Me for review.  
- **Task**: Review settings search for beta by week.  
- **Name**: Sarah, Omar, Me, Figma.  
- **Task**: Fold shortcuts sheet into help panel.  
- **Priorities**: Retry fix first, analytics onboarding once Figma lands.  

### Decisions Made  
- **Review**: Audit in the next week.  

### Action Items  
- **Task**: Review settings search for beta by week.  
- **Task**: Fold shortcuts sheet into help panel.  

### Follow-ups Needed  
- **None mentioned**.
