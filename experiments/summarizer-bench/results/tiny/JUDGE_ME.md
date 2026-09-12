# Judge pack — tiny

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

{
  "title": "Launch of New Product",
  "attendees": [
    "Me",
    "Them"
  ],
  "sections": [
    {
      "key_topics_discussed": [
        "launch the first week of August"
      ]
    },
    {
      "decisions_made": "None mentioned"
    },
    {
      "action_items": [
        {
          "owner": "Me",
          "task": "rewrite the hero copy"
        }
      ]
    },
    {
      "follow-ups_needed": "None mentioned"
    }
  }
}
