# Judge pack — 04-meridian-security-review

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
- David has questionnaire answers for a week
- On-site processing story holds up
- Three open threads: single sign-on, audit logging, written statement on data boundaries
- Azure AD used across org for single sign-on
- Compliance requires exportable audit logs (monthly minimum) showing who accessed patient records and when
- Board specifically requests written statement that nothing leaves clinic LAN
- SOC 2 readiness summary contains data-boundary statement as "honest sentence" for partnership

### Decisions Made
- Documents to be delivered by Wednesday
- Pilot unblocked next week

### Action Items
- Me: Confirm protocol details in audit-log spec
- Me: Write up audit log format and retention for compliance sign-off
- David: Get two documents by Wednesday
- David: Set up staging tenant access for team in parallel after documents

### Follow-ups Needed
None mentioned


## Candidate B

Partnership Pilot Unblocking Next Steps

### Key Topics Discussed
- The questionnaire answers have been received for a week.
- The on-site processing story holds up.
- Three open threads: single sign-on, audit logging, and a written statement on data boundaries.
- David's organization uses Azure AD across the org.
- If the app can do SSO against it, that closes the account-sprawl concern from compliance.
- Compliance requires exportable logs at a minimum monthly, and who accessed which patient record and when.
- A written statement is needed that nothing leaves the clinic LAN, as the board specifically requires.

### Decisions Made
None mentioned

### Action Items
- Me: Provide two documents by Wednesday.
- David: Set up staging tenant access for your team in parallel.

### Follow-ups Needed
- Unblock pilot start next week


## Candidate C

{
  "title": "Data and Compliance Review",
  "attendees": [
    "Me"
  ],
  "sections": [
    "Key Topics Discussed",
    "Decisions Made",
    "Action Items",
    "Follow-ups Needed"
  ]
}


## Candidate D

### Key Topics Discussed  
- Facts: Me: David, questionnaire answers for a week. Them: mostly green, three open threads (SSO, audit logs, data-boundary).  
- Explicit decisions: Take in order, confirm protocol details in audit-log spec. Include honest sentence in SOC 2 summary.  
- Tasks: Write up format/retention, set up staging tenant access.  
- Names: David, Azure AD, compliance team, clinic's board.  
- Documents: By Wednesday, pilot unblocked next week.  

### Decisions Made  
- Facts: Take in order, confirm protocol details in audit-log spec. Include honest sentence in SOC 2 summary.  

### Action Items  
- Tasks: Write up format/retention, set up staging tenant access.  
- Owners: David, Azure AD, compliance team, clinic's board.  

### Follow-ups Needed  
- None mentioned.
