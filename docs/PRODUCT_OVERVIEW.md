# Adversaria — Product Overview

_A plain-language description of what this product is and everything it does.
Written 2026-07-27, describing **v0.3.65**. Intended as a self-contained source
document (e.g. for slide generation) — no code, no implementation detail._

**Product:** Adversaria · **Company:** Laghari Labs · **License:** Elastic License 2.0 (source-available; free to use and self-host)
**Platform:** macOS, Apple Silicon (shipping) · Windows (in progress)
**Site:** lagharilabs.com/adversaria · **Source:** github.com/LaghariLabs/adversaria
**Tagline:** *Meeting notes that organize themselves, on your Mac.*
**Positioning line:** *Nothing leaves your machine.*

---

## 1. What it is, in one paragraph

Adversaria is a meeting notetaker that runs entirely on your own computer. It
records the audio your machine is already playing and the microphone it's
already hearing, transcribes it, and writes structured notes — all on your
hardware, with no server, no bot joining the call, and nothing uploaded. It then
does the part most notetakers skip: it compiles every action item from every
meeting onto one board, writes your week for you, and builds a searchable graph
of the people and topics across your entire history.

The name is Latin — *adversaria*, "a notebook of jottings" — which is exactly
what it is: a private, always-available notebook for the meetings in your life.

---

## 2. The problem it solves

**Meeting notetakers are good at capture and bad at what comes after.** You
record a call, you get a clean transcript and a tidy summary, and it joins the
hundred summaries before it. Three weeks later you're hunting for a decision you
know someone made, in a meeting you can't name, on a date you don't remember.

**And they all ship your data somewhere.** Cloud notetakers either put a bot in
your call or send your transcript to a model provider. That's an inconvenience
for most people and a hard blocker for some:

- A lawyer sending client conversations to a third-party AI risks waiving privilege.
- A therapist or clinician is restricted by HIPAA from handing patient audio to a vendor who won't sign a BAA.
- A consultant juggling five clients has five different confidentiality boundaries to honor.
- An EU or defense organization simply cannot send it at all.

Before Adversaria these people had two options: use a cloud notetaker and hope
nobody audits, or take notes by hand and miss half the conversation. Adversaria
is the third option — the convenience of an AI notetaker with none of the data
leaving.

---

## 3. How it works, from the user's side

1. **Start.** Press ⌘⇧M from anywhere, click the tray icon, or click record in
   the app. No bot appears in the meeting; nobody is notified; there is no
   calendar invite from a "notetaker bot."
2. **Talk.** The app captures two separate streams — the meeting audio coming
   out of your machine, and your own microphone — so it always knows who spoke.
   While recording, the window collapses into a slim companion panel you can
   dock beside the call: a live transcript scrolling on one side, your own notes
   on the other. Switch to another app and a small pill tucks into the notch
   with a timer and a live waveform.
3. **Stop.** Transcription runs on your GPU. Speakers are separated: you are
   labeled by name, and the remote side is split into Speaker 1, Speaker 2, and
   so on.
4. **Read.** A local AI model writes the notes — title, attendees, key topics,
   decisions, action items, follow-ups — in English, Arabic, or whatever
   language was spoken. **The recording is deleted the moment transcription
   succeeds.**
5. **Act.** Action items flow onto a shared board. The week writes itself.
   Everything joins a searchable graph you can ask questions of, across your
   entire history.

---

## 4. What makes it different

**1. There is no server.** Not "we delete your audio" — there is no cloud
component at all in the default mode. Turn off your Wi-Fi and the app behaves
identically. Competitors that call themselves private still send the transcript
to OpenAI or Anthropic for the summary; that's the step Adversaria does on your
own GPU.

**2. The organization layer is the product.** Most tools treat the summary as
the output. Adversaria treats it as the input — to a to-do board, a weekly
briefing, a knowledge graph, and a cross-meeting question-answering system. Your
meetings talk to each other instead of sitting in silos.

**3. No bot means no social cost.** Nobody sees "Fireflies Bot has joined." No
calendar access is required. It listens the way a person in the room does.

**4. Arabic and RTL are first-class.** Summaries, rendering, and layout handle
Arabic properly — something essentially none of the Western competitors do.

---

## 5. The complete feature set

### Recording and capture
- **Bot-free dual capture** — system audio and microphone recorded as two
  separate channels, so speaker attribution is structural rather than guessed.
- **Global hotkeys** — ⌘⇧M (⌃⇧M on Windows) toggles recording from any app;
  ⌘⇧N opens a quick note.
- **System tray control** — start/stop without bringing the app forward.
- **Recording companion view** — while recording, the app becomes a narrow
  dockable panel: timer, live audio level, live transcript, and your notes side
  by side (or transcript-first, with notes in a footer — your choice).
- **Notch pill** — leave the app and a compact pill docks under the notch: a
  pulsing dot, timer, and live per-channel waveforms (you in blue, others in
  red). Hover to expand it into a dynamic island showing the live caption, both
  channels, and a one-tap Stop. Or hide it entirely.
- **Live captions** — a rolling on-device preview of what's being said while
  the meeting is still running, de-duplicated across channels so speaker bleed
  doesn't double sentences.
- **Auto-detect meetings** (off by default) — notices when a conferencing app
  opens your microphone and offers to record. It reads the operating system's
  own "which app is using the mic" list — the same signal behind the mic
  indicator in your menu bar. Recognizes Zoom, Teams, Webex, Slack, and browser
  meetings like Google Meet. It never starts recording on its own, and it is
  microphone-based, not calendar-based, so watching a video never triggers it.
- **Back-to-back queue** — start the next meeting while the previous one is
  still transcribing.
- **Silence auto-stop** — prompts at five minutes of silence, stops at ten.
- **Data-loss protection** — a recording that fails to transcribe is kept,
  encrypted and clearly marked, until you retry. Silent recordings are discarded
  rather than stranded.
- **Audio file import** — drop in an iPhone voice memo or any audio file and
  get the same notes.

### Transcription and speakers
- **On-device transcription** using Whisper, GPU-accelerated (Apple Silicon on
  Mac, NVIDIA CUDA on Windows).
- **Speaker diarization** — the remote side is split into individual anonymous
  speakers (Speaker 1, Speaker 2 …); your own mic channel is always you.
- **Timestamped transcripts** — every turn carries its start time.
- **Color-coded speakers** throughout the app — you in blue, others in red.
- **Custom vocabulary** — feed it names, companies, and jargon so they're
  spelled correctly.
- **Your name** — your spoken lines are labeled with your actual name, so action
  items are attributed to you by name.
- **Speaker-bleed handling** — when your laptop speakers leak into your mic, the
  duplicate lines are stripped rather than misattributed.

### Notes and summaries
- **Structured summary cards** — title, attendees, key topics, decisions, action
  items with checkboxes, follow-ups. Collapsible, editable.
- **Seven note templates** — General, One-on-one, Client meeting, Brainstorm,
  Watched video, Interview, and Detailed. All user-editable.
- **Automatic template routing** — the app works out what a recording actually
  was and picks the matching template. The interview template even detects which
  side of the table you're on. A manual choice always wins.
- **Multilingual + Arabic/RTL summaries** — English, Arabic, or match the spoken
  language, with correct right-to-left rendering.
- **Your notes, woven in** — anything you typed during the recording appears as
  a "From Your Notes" section in the summary, verbatim.
- **Re-summarize** with a different template at any time.
- **Chat with a meeting** — ask questions about one meeting, grounded in its
  transcript, streaming token by token, with the conversation saved.
- **Prompt-injection guard** — something said out loud in a meeting can't
  hijack the note-taking instructions.

### The organization layer
- **To-dos board** — every action item from every meeting in one place, as
  either a **triage board** (Overdue / This week / Later, with drag-and-drop
  that edits the due date) or a **focus queue** (one next-up card at a time).
  Owners, due dates, meeting-scope filters.
- **To-do reminders** — an OS notification digest of what's due and overdue,
  twice a day.
- **Weekly Briefing** — the local model writes "your week in sixty seconds":
  what was decided, what you committed to, what's still open, plus stats.
- **Knowledge Graph** — an interactive, physics-animated map of your meetings,
  the people in them, the topics, and who owns what. Search it, click any node
  for a dossier. **Person profiles** hold role, company, email, phone, LinkedIn,
  aliases, and notes — and fill themselves in from what was said out loud (a
  founder's title and company are waiting for you after you meet them). Anything
  you type yourself always wins.
- **Ask across meetings** — one question answered from your entire history,
  with citations back to the meetings it drew from. Uses keyword search,
  on-device semantic embeddings, and the graph together.
- **Meeting Insights (beta)** — speaking statistics computed with no AI at all:
  your talk-time share, speaking pace against a 130–175 wpm target, filler-word
  rate against a 4% benchmark, interruptions, and longest monologue. The
  coaching is about you, not about grading other people. Deliberately excludes
  camera-based emotion analysis.

### Finding things
- **Compact sidebar** grouped into date bins — Pinned, Today, Yesterday, This
  week, then by month — with details on hover. Or switch back to full cards.
- **Auto-archive** — older meetings fold into a collapsed Archive after a
  configurable window; archive any meeting by hand from its menu. Search always
  spans the archive.
- **Full-text search** across everything.
- **`@person` search chips** — type `@` to filter by attendee.
- **`#tag` search** — type `#` to filter by tag.
- **Date heatmap** — a month calendar shaded by how many meetings each day held;
  click a day to filter.
- **Colorful tags** — auto-assigned by the model from the meeting's content,
  renameable and recolorable.
- **Pin** meetings to keep them at the top.

### Getting data out
- **Slide export** — a dark, animated one-page "Meeting Minutes" presentation
  (Key Topics / Decisions / Action Items / Follow-ups), self-contained, that
  prints to a single clean PDF page. Arabic-aware.
- **Markdown export.**
- **Portable meeting bundles** (`.adversaria.json`) — export one meeting, import
  it anywhere, including into someone else's copy.
- **Backup and restore everything** in one file.
- **Second Brain export** — mirror your meetings into any local folder as
  Obsidian-ready Markdown with YAML frontmatter and `[[wikilinks]]`, plus a note
  per person. Summaries only, never raw transcripts; locked meetings excluded;
  off by default.
- **MCP server** — a separate, open-source, read-only server that lets Claude,
  Claude Code, or any MCP client answer questions from your meetings, still
  entirely locally.

### Privacy and security
- **Nothing leaves the machine by default** — capture, transcription, and note
  generation all run locally. It works with the network off.
- **Audio is deleted** as soon as it's successfully transcribed.
- **Encrypted at rest** — the meetings database is AES-256 encrypted, with the
  key held in the operating system keychain. Recordings are encrypted while
  they're pending too.
- **Per-meeting privacy lock** — a PIN or Touch ID on individual meetings.
- **No telemetry, no analytics, no crash-report upload.**
- **Optional cloud, explicitly opt-in** — users without capable hardware can
  point it at Groq, xAI Grok, OpenRouter, or any OpenAI-compatible endpoint with
  their own API key. It is off by default, labeled in the interface where it
  matters, and stated to send the transcript off-device. Local remains the
  default and the point.

### Setup and the AI engine
- **Guided first run** — checks your hardware, recommends a local model sized to
  your RAM, downloads and verifies it, requests the OS permissions it needs, and
  runs a sample summary before letting you loose. Downloads start immediately
  and run in the background while you walk through the rest.
- **Three local model tiers** — roughly a 27B, a 9B, and a 4B option, recommended
  by your machine's memory. Recommended, never forced.
- **Switchable afterwards** — a model picker in Settings changes the engine
  without reinstalling or restarting.
- **Whisper model picker** — trade accuracy for speed.
- **Auto-updates**, cryptographically verified.
- **Notarized and signed** for macOS, so it installs by dragging it in.

### Calendar (optional, off by default)
- **Apple Calendar on macOS** — zero sign-in. Reads the calendars already on
  your Mac through one OS permission; no OAuth, no accounts, no backend.
- **Google Calendar** — read-only, tokens held in the OS keychain, as the
  cross-platform path.
- Used only to pre-fill the attendee roster for a meeting you recorded — never
  to decide when to record.

---

## 6. Who it's for

**Primary paying market — regulated, client-facing professionals** who *cannot*
use cloud AI and have the hardware to run local models:

- Solo and small-firm **lawyers** — privilege-waiver exposure is real, and the
  billable-hour incentive to capture every call is real too.
- **Healthcare practitioners** — therapists, clinicians, specialists restricted
  by HIPAA. Many use no notetaker at all today.
- **Consultants and fractional executives** — many clients, many different
  confidentiality boundaries, one tool that never exfiltrates.
- **EU, sovereign, and defense** professionals — GDPR, data residency, air-gap.

The buying trigger for this group is **liability avoidance, not productivity**.

**Free funnel — privacy-minded professionals and Arabic/RTL users.** People who
want control even without a legal mandate, plus a large Arabic-speaking audience
with almost no good options. This group is the distribution engine, not the
revenue.

---

## 7. Competitive position

| | Granola | Otter / Fireflies | Zoom & MS Copilot | Meetily (OSS) | **Adversaria** |
|---|---|---|---|---|---|
| Audio stays local | Yes | No | No | Yes | **Yes** |
| **Transcript stays local** | **No** — sent to cloud AI | No | No | Yes | **Yes** |
| Bot joins the call | No | Yes | Built in | No | **No** |
| Cross-meeting Q&A | No | Some | No | No | **Yes** |
| Action-item board | No | Limited | No | No | **Yes** |
| Knowledge graph | No | No | No | No | **Yes** |
| Encrypted at rest | No | N/A (cloud) | No | No | **Yes** |
| Arabic / RTL | No | No | Partial | Partial | **Yes** |
| Price | Free (VC-funded) | $10–30/mo | Bundled | Free | **Free (source-available)** |

The honest read: **"local" alone is table stakes now** — several open-source
notetakers are local. The defensible position is the *complete* capture →
memory → action loop running on the customer's own hardware, which neither the
cloud incumbents (structurally can't) nor the OSS notetakers (they're just
notetakers) have.

The two market tailwinds are real and citable: Otter faces a privacy
class-action, and a February 2026 legal ruling made cloud AI notes a
privilege-waiver risk for lawyers.

---

## 8. Business model

| Tier | Who | Price |
|---|---|---|
| **Free** (today, everything) | Everyone | **$0**, MIT licensed |
| **Bring-your-own-key cloud** | Users without capable hardware | $0 — their key, their choice |
| **Pro** (planned, deferred) | Power users | ~$15/mo or $120/yr |
| **Sovereign / Enterprise** | Regulated organizations — self-hosted, SSO, audit logs, BAA | Quote-based |

The deliberate decision was to **launch free-only** and defer paid tiers: the
bottleneck is distribution, not monetization. The company will never build
hosted inference — local costs nothing to run, and cloud users bring their own
key.

---

## 9. Where it actually stands

**Shipping now:** v0.3.65, notarized and publicly downloadable for macOS on
Apple Silicon. Free, MIT licensed. Auto-updating.

**In progress:** Windows. The Windows code path exists and is continuously
built — the meeting-detection and audio-capture layers were originally written
for Windows first — but the installer isn't published yet.

**Honest limits, stated plainly:**
- macOS Apple Silicon only today.
- First run downloads roughly 3.5 GB of models; the machine needs real memory to
  run them well. The bring-your-own-key cloud path exists for machines that
  can't.
- The live caption during a meeting is a best-effort preview; the authoritative
  transcript is produced when you stop.
- Speakers are separated but not *named* — "Speaker 1," not "Sarah."
- Microsoft calendar isn't built yet (Apple and Google are).
- Single-user by design. No team sharing or collaboration.

**On the roadmap:** named speaker identification, Microsoft calendar, team/shared
libraries for the law-firm case, calendar-driven pre-meeting prep, and a
read-only mobile companion.

---

## 10. The north star

> **Every morning, your day's to-dos are auto-deployed from yesterday's meetings
> onto a board — entirely on your own machine.**

Everything built so far — the action-item database, the weekly briefing, the
graph, the cross-meeting Ask — is the foundation for that one workflow. The bet
is that depth on a single loop that no cloud competitor can replicate beats
breadth on features they can all copy.

---

_Source of truth for status: `STATUS.md`, `SPEC.md`, `CHANGELOG.md` in this
repository. Written 2026-07-27 against v0.3.65._
