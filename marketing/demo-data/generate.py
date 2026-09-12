#!/usr/bin/env python3
"""Generate synthetic Adversaria demo meetings as .adversaria.json bundles.

Dates are RELATIVE TO TODAY, so the set always demos well: some action items
overdue, some due today/this week, some later, some done. Re-run any time to
refresh the files, then import each via the app's Import button ->
"Adversaria bundle (.json)".

Usage:  python3 generate.py
"""

from __future__ import annotations

import json
from datetime import date, datetime, timedelta
from pathlib import Path

OUT = Path(__file__).parent
LOCAL_UTC_OFFSET_HOURS = 4  # GMT+4; recorded_at is stored in UTC


def recorded_at(days_ago: int, hour: int, minute: int = 0) -> str:
    d = date.today() - timedelta(days=days_ago)
    local = datetime(d.year, d.month, d.day, hour, minute)
    utc = local - timedelta(hours=LOCAL_UTC_OFFSET_HOURS)
    return utc.isoformat() + "+00:00"


def due(offset_days: int | None) -> str:
    if offset_days is None:
        return ""
    return (date.today() + timedelta(days=offset_days)).isoformat()


def timed_turns(turns: list[tuple[str, str]]) -> tuple[list[dict], float]:
    """Assign plausible start/end times from word counts (~2.4 words/sec)."""
    out = []
    t = 4.0
    for i, (speaker, text) in enumerate(turns):
        dur = max(3.5, len(text.split()) / 2.4)
        out.append(
            {
                "speaker": speaker,
                "text": text,
                "start": round(t, 2),
                "end": round(t + dur, 2),
            }
        )
        t += dur + (1.2 if i % 2 == 0 else 2.1)
    return out, round(t + 30.0, 1)


def bundle(m: dict) -> dict:
    turns, computed_dur = timed_turns(m["turns"])
    transcript = "\n".join(f"{s}: {t}" for s, t in m["turns"])
    return {
        "schema_version": 1,
        "meeting": {
            "title": m["title"],
            "recorded_at": m["recorded_at"],
            "duration_seconds": m.get("duration_seconds", computed_dur),
            "template_used": m.get("template", "general"),
            "transcript": transcript,
            "transcript_turns": turns,
            "summary": m["summary"].strip(),
            "attendees": m["attendees"],
            "user_notes": m.get("user_notes", ""),
            "link": m.get("link", ""),
            "tags": m["tags"],
            "action_items": [
                {
                    "ord": i,
                    "text": text,
                    "assignee": assignee,
                    "due": due(due_offset),
                    "done": done,
                }
                for i, (text, assignee, due_offset, done) in enumerate(m["actions"])
            ],
        },
    }


MEETINGS = [
    # ---------------------------------------------------------------- 1
    {
        "file": "01-meridian-kickoff",
        "title": "Meridian Health — patient-intake pilot kickoff",
        "recorded_at": recorded_at(17, 10),
        "template": "client-meeting",
        "attendees": ["Priya Nair", "David Park"],
        "tags": [
            {"label": "Client", "color": "blue"},
            {"label": "Kickoff", "color": "green"},
        ],
        "turns": [
            ("Me", "Thanks for making time, both of you. Goal today is to agree on the shape of the intake pilot: which clinics, what success looks like, and the privacy constraints."),
            ("Them", "From our side the driver is simple. The front-desk team spends about forty minutes per patient on intake paperwork, and half of it is retyping things the patient already told us."),
            ("Me", "Understood. Our proposal is to pilot the intake assistant in a limited setting first rather than a big-bang rollout. Two clinics, six weeks, then we review."),
            ("Them", "Two clinics works. Riverside and the Oakwood branch are the best candidates — motivated staff, similar patient volume."),
            ("Me", "On the privacy side, everything runs on-site. No patient audio or text leaves the clinic network, which should make David's review much easier."),
            ("Them", "That's the headline I needed. I'll still run the full security questionnaire, but on-site processing removes the biggest blocker we had with the last vendor."),
            ("Me", "For success metrics I'd suggest time-per-intake and staff satisfaction, measured in week one as a baseline and again in week six."),
            ("Them", "Add error rates on transferred data. That's what burned us before — fast but wrong is worse than slow."),
            ("Me", "Agreed, three metrics then. I'll draft the pilot scope document this week and send the security questionnaire answers along with it."),
            ("Them", "I'll get you the current intake workflow diagrams so your team sees what the desk staff actually do today. Warts and all."),
            ("Me", "Perfect. Let's reconvene once David has reviewed the questionnaire. Thanks, both."),
        ],
        "summary": """
### Overview
Kickoff for the Meridian Health patient-intake pilot. Agreed on a two-clinic,
six-week pilot (Riverside and Oakwood) with all processing on-site — no patient
data leaves the clinic network. Meridian's driver is intake time: roughly forty
minutes per patient, half of it re-entry.

### Key points
- Front-desk staff lose ~20 min/patient to retyping data patients already gave.
- On-site processing removes the privacy blocker that killed the previous vendor.
- Success metrics: time-per-intake, staff satisfaction, and data-transfer error
  rate, baselined in week one and re-measured in week six.

### Decisions
- Pilot limited to Riverside and Oakwood clinics, six weeks.
- All audio and text processing stays on the clinic network.
- Three success metrics, including error rate on transferred data.

### Action items
- Draft the pilot scope document (Hamza)
- Send security questionnaire answers (Hamza)
- Share clinic intake workflow diagrams (Priya)
""",
        "actions": [
            ("Draft the pilot scope document", "Me", -14, True),
            ("Send security questionnaire answers", "Me", -12, True),
            ("Share clinic intake workflow diagrams", "Priya Nair", -10, True),
        ],
    },
    # ---------------------------------------------------------------- 2
    {
        "file": "02-atlas-design-review",
        "title": "Atlas design review — onboarding flow v2",
        "recorded_at": recorded_at(10, 14),
        "attendees": ["Sarah Chen"],
        "tags": [
            {"label": "Design", "color": "purple"},
            {"label": "Atlas", "color": "blue"},
        ],
        "turns": [
            ("Me", "Let's go through the v2 onboarding flow. My main worry from v1 is drop-off — analytics show we lose a third of new users before they create anything."),
            ("Them", "Right, and I think the tour is the culprit. Seven steps before you touch the product. My proposal is cutting it to three: workspace name, invite, first project."),
            ("Me", "Three steps feels right. What happens to the feature tour content we cut?"),
            ("Them", "It moves into empty states. Instead of a wizard telling you about templates, the empty project screen shows three starter templates you can click."),
            ("Me", "I like that a lot — show, don't tell. Do we have copy for those empty states?"),
            ("Them", "Not yet. I mocked placeholder text but it needs a real writing pass. Short, verb-first, one line each."),
            ("Me", "I'll take the copy. Can you get the Figma updated with the three-step flow so Omar can scope the build?"),
            ("Them", "Yes, by Friday. One more thing — we should instrument step two properly this time. Last time we shipped onboarding changes blind."),
            ("Me", "Agreed. Let's have Omar add drop-off analytics on step two before we ship, not after."),
            ("Them", "I'll write the event spec into the Figma file so it's part of the handoff."),
        ],
        "summary": """
### Overview
Review of the Atlas onboarding v2 designs with Sarah. v1 loses about a third of
new users before first meaningful action; the seven-step tour is the prime
suspect. v2 cuts onboarding to three steps and moves teaching into empty states.

### Key points
- Onboarding shrinks from seven steps to three: workspace name, invite, first
  project.
- Cut tour content becomes clickable starter templates in empty states —
  show, don't tell.
- Step-two drop-off analytics must ship with the redesign, not after it.

### Decisions
- Adopt the three-step flow for onboarding v2.
- Replace the feature wizard with template-driven empty states.

### Action items
- Update the onboarding Figma with the 3-step flow (Sarah)
- Write empty-state copy for the three templates (Hamza)
- Instrument drop-off analytics on step 2 (Omar)
""",
        "actions": [
            ("Update onboarding Figma with the 3-step flow", "Sarah Chen", -7, True),
            ("Write empty-state copy for the three templates", "Me", -6, True),
            ("Instrument drop-off analytics on step 2", "Omar Farouk", -3, False),
        ],
    },
    # ---------------------------------------------------------------- 3
    {
        "file": "03-atlas-standup",
        "title": "Weekly standup — Atlas core",
        "recorded_at": recorded_at(8, 9, 30),
        "attendees": ["Omar Farouk", "Sarah Chen"],
        "tags": [{"label": "Standup", "color": "green"}],
        "turns": [
            ("Me", "Quick round. Omar, where are we on the sync-retry bug?"),
            ("Them", "Root-caused it yesterday. The backoff resets on every reconnect, so flaky networks hammer the server. Fix is a persisted backoff window — I'll have it in review today."),
            ("Me", "Good. That one's been generating most of our support email. Sarah?"),
            ("Them", "Component audit is done, forty-two components, a dozen candidates for deletion. I need a second pair of eyes before I start removing things."),
            ("Me", "Send it to me, I'll review this week. On my side, settings search is ready for beta — I want it out this sprint so we get feedback before the launch build."),
            ("Them", "Any blockers from the beta group on the last drop?"),
            ("Me", "Nothing major. Two people asked for keyboard shortcuts documentation, which is telling us they're becoming power users. Good sign."),
            ("Them", "I can fold a shortcuts sheet into the help panel when I do the empty-state work."),
            ("Me", "Nice. Priorities stand: retry fix first, then analytics on onboarding step two once the Figma lands."),
        ],
        "summary": """
### Overview
Weekly Atlas core standup. Sync-retry bug root-caused (backoff resets on
reconnect); fix in review today. Component audit finished with twelve deletion
candidates awaiting a second review. Settings search ships to beta this sprint.

### Key points
- Sync-retry fix: persisted backoff window, in review today — this bug drives
  most current support email.
- Component audit: 42 components, 12 deletion candidates.
- Beta group requesting keyboard-shortcut docs — power-user signal.

### Decisions
- Retry fix ships first; onboarding analytics follows the Figma handoff.

### Action items
- Fix sync-retry backoff bug (Omar)
- Ship settings search to beta (Hamza)
- Review Sarah's component audit (Hamza)
""",
        "actions": [
            ("Fix sync-retry backoff bug", "Omar Farouk", -5, True),
            ("Ship settings search to beta", "Me", -4, True),
            ("Review Sarah's component audit", "Me", None, False),
        ],
    },
    # ---------------------------------------------------------------- 4
    {
        "file": "04-meridian-security-review",
        "title": "Meridian Health — security & compliance review",
        "recorded_at": recorded_at(4, 11),
        "template": "client-meeting",
        "attendees": ["Priya Nair", "David Park"],
        "tags": [
            {"label": "Client", "color": "blue"},
            {"label": "Security", "color": "red"},
        ],
        "turns": [
            ("Me", "David, you've had the questionnaire answers for a week — where did we land?"),
            ("Them", "Mostly green. The on-site processing story holds up. Three open threads: single sign-on, audit logging, and a written statement on data boundaries."),
            ("Me", "Take them in order. For SSO, you're an Azure shop, right?"),
            ("Them", "Azure AD across the org. If your app can do SSO against it, that closes the account-sprawl concern from compliance."),
            ("Me", "We can integrate against Azure AD. I'll confirm the exact protocol details in the audit-log spec I owe you anyway."),
            ("Them", "On audit logs — compliance wants exportable logs, monthly at minimum. Who accessed which patient record and when."),
            ("Me", "Monthly export is straightforward. I'll write up the format and retention so your compliance team can sign off on paper rather than on a demo."),
            ("Them", "Last one is the data-boundary statement. We need it in writing that nothing leaves the clinic LAN — our board asks for that sentence specifically."),
            ("Me", "You'll have it in the SOC 2 readiness summary. It's an honest sentence for us, which is why this partnership works."),
            ("Them", "Then from my side we're nearly there. Get me those two documents and I'll set up staging tenant access for your team in parallel."),
            ("Me", "Deal. Documents by Wednesday, and we aim to unblock the pilot start next week."),
        ],
        "summary": """
### Overview
Security and compliance review for the Meridian pilot. Questionnaire came back
mostly green; three open threads — SSO, audit logging, and a written
data-boundary statement — are now the only blockers to the pilot start.

### Key points
- SSO must integrate with Meridian's org-wide Azure AD.
- Compliance requires exportable audit logs, monthly minimum: who accessed
  which record, when.
- The board wants the "nothing leaves the clinic LAN" guarantee in writing.

### Decisions
- SSO via Azure AD integration.
- Monthly audit-log export cadence.
- Data-boundary statement ships inside the SOC 2 readiness summary.

### Action items
- Send SOC 2 readiness summary (Hamza)
- Provide the audit-log export spec (Hamza)
- Set up staging tenant access (David)
""",
        "actions": [
            ("Send SOC 2 readiness summary", "Me", -2, False),
            ("Provide the audit-log export spec", "Me", -1, False),
            ("Set up staging tenant access", "David Park", 2, False),
        ],
    },
    # ---------------------------------------------------------------- 5
    {
        "file": "05-one-on-one-omar",
        "title": "1:1 — Omar (infra costs & hiring)",
        "recorded_at": recorded_at(3, 15),
        "template": "one-on-one",
        "attendees": ["Omar Farouk"],
        "tags": [{"label": "1:1", "color": "green"}],
        "turns": [
            ("Me", "Two topics from me: the CI bill and whether it's time to hire. What's on your list?"),
            ("Them", "Same two, honestly. The CI bill doubled since we added the integration suite. Eight hundred a month and climbing."),
            ("Me", "What's the alternative look like?"),
            ("Them", "A self-hosted runner on a single beefy box. My back-of-envelope says it pays for itself in three months, but I want to benchmark before we commit."),
            ("Me", "Do the benchmark this week — if the numbers hold, migrate before month end. Now, hiring."),
            ("Them", "I'm the bottleneck on backend work. Between infra, reviews, and the sync fixes, feature work is getting maybe a third of my week."),
            ("Me", "That matches what I see. I think we open a mid-level backend role rather than senior — someone you can grow, at a salary we can sustain."),
            ("Them", "Mid-level works if they're strong on databases. I can carry the architecture if they can own features end to end."),
            ("Me", "I'll write the job description tomorrow and route it through the usual channels. You'll do the technical screens."),
            ("Them", "Happy to. And thanks for moving on this before I burned out rather than after."),
        ],
        "summary": """
### Overview
1:1 with Omar covering infrastructure costs and hiring. CI spend has doubled to
~$800/month since the integration suite landed; a self-hosted runner likely
pays for itself in three months. Omar is the backend bottleneck — feature work
gets roughly a third of his week.

### Key points
- CI bill: ~$800/month and climbing; self-hosted runner is the candidate fix.
- Omar's split: infra + reviews + sync fixes crowd out feature work.
- Role shape: mid-level backend, strong on databases, grows under Omar.

### Decisions
- Benchmark the self-hosted runner this week; migrate before month end if the
  numbers hold.
- Open a mid-level backend engineering role.

### Action items
- Benchmark self-hosted runner costs (Omar)
- Write the backend role job description (Hamza)
""",
        "actions": [
            ("Benchmark self-hosted runner costs", "Omar Farouk", 0, False),
            ("Write the job description for the backend role", "Me", 1, False),
        ],
    },
    # ---------------------------------------------------------------- 6
    {
        "file": "06-investor-james",
        "title": "Investor catch-up — James Whitfield",
        "recorded_at": recorded_at(2, 17),
        "attendees": ["James Whitfield"],
        "tags": [{"label": "Investor", "color": "orange"}],
        "turns": [
            ("Me", "James, good to catch up. Quick shape of the last two months: beta is at forty active teams, retention is holding, and the Meridian pilot should start next week."),
            ("Them", "Forty teams from thirty-one last time — steady. What's your read on why retained users stay?"),
            ("Me", "The weekly digest, surprisingly. People who get value out of the Monday summary keep the habit. It's become our stickiest surface."),
            ("Them", "Then make it the wedge. On Meridian — is that revenue or a lighthouse?"),
            ("Me", "Lighthouse first, revenue second. Healthcare compliance is brutal to earn, but once earned it's a moat and a reference that closes the next five deals."),
            ("Them", "Agreed, as long as it doesn't eat the whole roadmap. What do you need from me?"),
            ("Me", "Two things. A monthly update cadence so these catch-ups compound, and intros to design-partner prospects in regulated spaces."),
            ("Them", "Done on both. Helios Legal and Cardinal Wealth are the two I'd start with — I'll make the intros this week, you follow up."),
            ("Me", "Perfect. First monthly update lands with July metrics next week."),
        ],
        "summary": """
### Overview
Catch-up with James Whitfield. Beta grew from 31 to 40 active teams with
retention holding; the weekly digest has emerged as the stickiest surface.
Meridian is positioned as lighthouse-first. James will intro two regulated-space
design-partner prospects: Helios Legal and Cardinal Wealth.

### Key points
- 40 active beta teams (up from 31); retention stable.
- The Monday digest drives habit — candidate wedge feature.
- Meridian framed as compliance moat + reference account, not near-term revenue.

### Decisions
- Move to a monthly written investor-update cadence.
- Pursue Helios Legal and Cardinal Wealth as design partners via James.

### Action items
- Send July metrics update (Hamza)
- Follow up on the Helios Legal intro (Hamza)
""",
        "actions": [
            ("Send July metrics update to James", "Me", 4, False),
            ("Follow up on the Helios Legal intro", "Me", 6, False),
        ],
    },
    # ---------------------------------------------------------------- 7
    {
        "file": "07-launch-marketing-sync",
        "title": "Atlas launch — marketing sync",
        "recorded_at": recorded_at(1, 12),
        "attendees": ["Lina Aziz"],
        "tags": [
            {"label": "Marketing", "color": "orange"},
            {"label": "Atlas", "color": "blue"},
        ],
        "turns": [
            ("Me", "Let's lock the launch sequence. My instinct is first week of August — the onboarding v2 work lands next week and I don't want to launch on the old flow."),
            ("Them", "First week of August works. It gives me two weeks for assets. The critical-path item is the demo video — everything else derives from it."),
            ("Me", "Then I record it this week. Ninety seconds, real product, no mockups."),
            ("Them", "Exactly. From that one recording I can cut the social clips, the landing-page loop, and the launch-post GIF."),
            ("Me", "What does the social calendar look like?"),
            ("Them", "Two weeks: teaser clips, a founder thread on why we built it, then the launch-day push. I'll draft the full calendar once I have the video."),
            ("Me", "Landing page — the hero copy still says 'organize your team's work'. It's true and it's forgettable."),
            ("Them", "Rewrite it around the digest, per the retention data. 'Your team's week, summarized every Monday' is the direction I'd test."),
            ("Me", "Take that direction. I'll rewrite the hero this week, you draft the calendar, and we review both on Monday."),
            ("Them", "One more — the Buildlog podcast slot came through for launch week. I booked it this morning."),
            ("Me", "Excellent. That's our third-party credibility beat sorted."),
        ],
        "summary": """
### Overview
Launch planning with Lina. Launch week set for the first week of August,
gated on onboarding v2 landing first. The demo video is the critical-path
asset — social clips, the landing loop, and the launch GIF all derive from it.
Buildlog podcast booked for launch week.

### Key points
- Demo video first; every other asset is cut from it.
- Two-week social arc: teasers → founder thread → launch-day push.
- Hero copy pivots to the digest ("your team's week, summarized every Monday")
  per the retention data.

### Decisions
- Launch week: first week of August.
- Demo video recorded before the landing-page refresh.
- Hero copy direction: lead with the weekly digest.

### Action items
- Record the product demo video (Hamza)
- Draft the launch-week social calendar (Lina)
- Refresh landing page hero copy (Hamza)
- Book podcast slot with Buildlog (Lina — done)
""",
        "actions": [
            ("Record the product demo video", "Me", 0, False),
            ("Draft the launch-week social calendar", "Lina Aziz", 3, False),
            ("Refresh landing page hero copy", "Me", None, False),
            ("Book podcast slot with Buildlog", "Lina Aziz", None, True),
        ],
    },
]


def main() -> None:
    for m in MEETINGS:
        path = OUT / f"{m['file']}.adversaria.json"
        path.write_text(json.dumps(bundle(m), indent=2, ensure_ascii=False) + "\n")
        print(f"wrote {path.name}")
    print(f"\n{len(MEETINGS)} bundles in {OUT}")


if __name__ == "__main__":
    main()
