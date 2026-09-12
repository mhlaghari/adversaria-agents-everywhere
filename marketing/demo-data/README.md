# Demo meetings (synthetic)

Seven fictional-but-realistic meetings for demos, screenshots, and the launch
video: a client pilot arc (Meridian Health), product/design work (Atlas), a
standup, a 1:1, an investor catch-up, and a launch-marketing sync. Recurring
attendees (Sarah Chen, Omar Farouk, Priya Nair, David Park, Lina Aziz, James
Whitfield) so the Knowledge Graph and people dossiers demo well.

Action items are spread deliberately so the To-dos triage board shows every
lane: 3 overdue, 2 due today, several this week / later, 2 undated, 7 done.
Transcript turns carry real timings, so Insights renders too.

## Refresh the dates

Dues and meeting dates are generated **relative to today**. If the files are
older than a few days, regenerate before importing:

```bash
python3 generate.py
```

## Import into the app

In Adversaria: sidebar **Import** button → **Adversaria bundle (.json)** → pick
one file. Repeat per file (7 total). Meetings appear in the sidebar; To-dos,
Weekly, Graph, and Ask pick them up immediately.

## Caveats

- **No dedupe on import:** importing the same bundle twice creates a duplicate
  meeting — import each file once.
- **The app re-summarizes imports:** within a few minutes of import, the app's
  LLM queue rewrites each meeting's summary into its native section format and
  may re-title it. This is expected (and renders better than the raw bundle
  markdown); action items, attendees, tags, dates, and transcripts are
  untouched.

- **Second Brain sync:** if the Obsidian vault sync is enabled in Settings,
  imported demo meetings export to your vault like real ones. Deleting the
  meetings in-app removes their vault notes again (orphan sweep).
- The Weekly Briefing prose is written by the local LLM from these summaries —
  it will read like a real week, which is the point.
- Delete the demo meetings before showing real personal data, or record demos
  in a separate user account.
