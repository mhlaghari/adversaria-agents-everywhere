# Adversaria demo video — shooting script

_Two deliverables from ONE Loom recording session: (A) the 60–90s captioned
demo, (B) a 10–15s silent GIF cut. Concept: **the demo is the meeting** — you
narrate; Adversaria live-captions your narration; the summary at the end
summarizes the demo itself. Signature proof beat: Wi-Fi goes OFF before
recording starts._

Claims discipline (STRATEGY_HANDOFF §5): everything shown is real behavior in
**local mode**. No staged UI, no absolute claims in captions.

---

## Prep checklist (10 min, before any take)

- [ ] macOS **Do Not Disturb ON** (no notification leaks personal data on camera).
- [ ] Adversaria 0.3.43 running, header shows **Local ML Service: Online**.
- [ ] Sidebar presentable: keep 3–5 meetings with clean titles visible, no
      client-confidential names. (Pin the best-looking ones; they flash by.)
- [ ] Wi-Fi menu-bar icon visible (System Settings → Control Center → Wi-Fi:
      "Always Show in Menu Bar") — the off-toggle must be SEEN.
- [ ] Loom: **camera bubble ON, small, bottom-left** (founder face = trust on
      HN/PH), mic = your best mic, record **full screen**.
- [ ] Close every other app; wallpaper neutral; dock hidden (⌥⌘D).
- [ ] Rehearse the narration below 2–3×. The summary quality depends on you
      actually SAYING the decisions/action items — Whisper transcribes what you
      speak, and the summary is only as structured as the speech.
- [ ] Do 2–3 full takes; pick the one where live captions kept up nicely and
      the summary came out clean. (Regenerating the same recording is fine.)

---

## A. The 60–90s demo (target ≈ 80s)

Captions are burned-in text overlays (Loom captions or CapCut after; max 2
lines, 3–5 words per line). VO = what you say out loud — which doubles as the
meeting content being transcribed.

| # | Time | On screen (what you DO) | VO (what you SAY) | Caption overlay |
|---|------|--------------------------|-------------------|-----------------|
| 1 | 0–4s | Already-finished meeting note open: title, summary sections, action items visible. Cursor idle. | "This is an AI meeting summary. Notes, decisions, action items." | **AI meeting notes.** |
| 2 | 4–9s | Click the Wi-Fi menu-bar icon → toggle **Wi-Fi OFF**. Linger 1 beat on the empty icon. | "Now watch me make one — with the internet turned off." | **Wi-Fi: OFF.** |
| 3 | 9–14s | Press **⌘⇧M**. App snaps into the recording companion: record bar, pulsing dot, waveform, live-transcript pane + notes pane. | "One hotkey. No bot joins anything — it just listens to this Mac." | **No bot. One hotkey.** |
| 4 | 14–34s | Keep talking; live captions of YOUR OWN words scroll in ~a second behind you. Mid-shot, type a note in the notes pane: `pricing → decide next week`. | "It's transcribing me right now, on this machine — the model runs on the Mac's own chip. So let's have a meeting: I'm deciding that beta invites go out this Friday. And the action item is — email the first ten testers by Thursday." | **Transcribed on-device.** → **Your words. Your machine.** |
| 5 | 34–39s | Click **Stop & summarize**. Processing state visible. | "Done. It transcribes with Whisper and writes the summary with a local LLM. Still no internet." | **Local Whisper + local LLM.** |
| 6 | 39–54s | The finished note appears: auto title, summary, **the decision + the Thursday action item you spoke**, your typed note reflected. Scroll slowly. | "There it is — the decision I made, the action item with the deadline, and the note I typed, woven in." | **Decisions. Action items. Automatic.** |
| 7 | 54–63s | Click the **Transcript** tab: speaker-labeled lines with [MM:SS] timestamps. | "Full transcript, speaker-labeled, timestamped." | **Speaker-labeled transcript.** |
| 8 | 63–71s | Toggle **Wi-Fi back ON**, deliberately. | "Wi-Fi's been off the whole time. In local mode, no audio, no transcript, nothing leaves this machine — and the recording is deleted once it's transcribed." | **Nothing left this Mac.** |
| 9 | 71–80s | Browser: **lagharilabs.com/adversaria**, cursor to **Join the waitlist**. | "It's called Adversaria. macOS beta — link below, join the waitlist." | **lagharilabs.com/adversaria** |

**The one hard rule for shot 4:** speak the decision ("beta invites go out
Friday") and the action item ("email the first ten testers by Thursday") in
clear, complete sentences — those two lines are what make shot 6 land, because
the summary will contain them verbatim-ish under Decisions / Action Items.

**YouTube packaging (when uploading):**
- Title: `Adversaria — AI meeting notes with the internet turned off`
- Description first line: `No bot joins your call. Recording, transcription
  (Whisper), and summarization (local LLM) all happen on your Mac — in local
  mode, nothing leaves the machine. Join the beta waitlist:
  https://lagharilabs.com/adversaria/`
- Unlisted until launch week, then public (per LAUNCH_PLAN §7 asset plan).

---

## B. The 10–15s silent GIF cut

Cut from the SAME take (or its own quick take). No audio, loops cleanly.
Per LAUNCH_PLAN: "sparse note → summary + action items."

| Time | On screen |
|------|-----------|
| 0–3s | Recording companion live: captions scrolling, the typed note `pricing → decide next week` visible. |
| 3–5s | Click **Stop & summarize**. |
| 5–7s | Processing (speed-ramp 2–4× in editing so the wait reads as a beat, not a wait). |
| 7–14s | Summary + action items populate; slow scroll; end frozen 1s on the action items (loop point). |

Text overlay (one, persistent, bottom): `on-device · no bot · nothing uploaded in local mode`
Export: 720p, ≤8MB if possible (Reddit/PH galleries), MP4 + GIF versions.

---

## Why this concept (for the record)

- **Result first** (3-second rule): the finished summary is the hook, not the UI tour.
- **The Wi-Fi-off beat** is the one visual no cloud competitor can copy — it IS
  the "nothing leaves your machine" positioning, shown not claimed.
- **Self-demonstrating**: the live captions transcribing the narrator kill the
  "is this real?" doubt that pre-rendered demos create.
- Same skeleton later re-cuts into: PH gallery stills (shots 1/4/6/8), an X
  clip (shots 2–6, 30s), LinkedIn clip (shots 1–6), Shorts/Reels vertical crop.

_Changelog: 2026-07-17 — v1 (Claude), per STRATEGY_HANDOFF §6 item 1._
