# Fresh-account QA — the onboarding proof ritual

_The "works 100%" machine: run the whole journey on a **virgin macOS user
account**, where nothing is cached, nothing is granted, and nothing can be
assumed. Every stumble becomes a punch-list item; fix; re-run. The product is
onboarding-done only when a full pass produces **zero manual retries, zero
dead-ends, zero raw errors** — the bar the paid funnel needs (churn here kills
it). Budget ~40 minutes plus download time. Never run against your real
account: cached models and granted permissions make it lie._

**Version under test:** ______ · **Date:** ______ · **Machine/RAM:** ______

Score each step ✅ PASS / ❌ FAIL / ⚠️ FRICTION (worked, but confusing or ugly).
Write down every wait longer than it felt like it should be.

---

## Phase 0 — Prep (5 min)

1. System Settings → Users & Groups → add user `qa-fresh` (standard, not
   admin unless testing the non-admin path — note which). Log into it.
   Do **not** sign into iCloud. Wi-Fi connected.
2. Confirm virginity: no `~/Library/Application Support/meeting-note-taker`,
   no `~/.cache/huggingface`, no Ollama installed.
3. In Safari (not your dev browser): go to **lagharilabs.com** and use the
   real Download button — the QA covers the funnel from the website, not
   from a DMG you copied over.
   - ☐ The button serves the **macOS** DMG (platform detection).

## Phase A — Install & first open (5 min)

4. Open the DMG, drag to Applications, eject, launch from Applications.
   - ☐ **No Gatekeeper scare.** It must open with the plain "downloaded from
     the internet" confirmation at most. Any "unidentified developer" or
     "damaged" dialog = FAIL (stapling/notarization regression).
5. First-run wizard appears.
   - ☐ Three screens max (You → Permissions → Done). Count them.
   - ☐ **Nothing downloads before you click a Download button.** Watch
     Activity Monitor's network if unsure — any uninvited multi-MB pull is
     an instant FAIL (the V2 rule).

## Phase B — The wizard (5 min)

6. **You:** enter name + email, consent box.
   - ☐ Copy is honest about what registration is for.
   - ☐ After finishing: Settings → Setup status shows **Registered** (give
     it a minute online). "Registration queued" that never clears = FAIL.
     (Check the Formspree dashboard afterward — the entry must actually
     arrive.)
7. **Permissions:** grant microphone. Then the **System audio** row: press
   **Check system audio** — the app plays a brief near-silent tone and
   listens for it through the tap (there is no other honest check; macOS
   has no API for this permission). On a virgin account macOS should show
   the **System Audio Recording** consent during this check — approve it.
   - ☐ Each permission states *why* before macOS prompts.
   - ☐ The system-audio consent fires **during the wizard check** (not
     later, mid-recording), and **at most once, ever**.
   - ☐ After approving, the row lands on **Granted**. If it lands
     "not granted" instead: note whether your Mac was muted (unmute →
     Check again), and whether **Open System Settings** drops you inside
     *Screen & System Audio Recording* or just on Privacy & Security.
   - ☐ **Screen Recording is never requested.** Any Screen Recording
     prompt anywhere in setup = FAIL (regression to the suppressed-prompt
     trap that broke 0.3.78).
8. **Done / guide card:** it should point you at exactly one next action —
   downloading a transcription model — with an **honest size** on the button.

## Phase C — Model download (download time + 5 min)

9. Click Download on the recommended model.
   - ☐ The progress bar **moves continuously from the first seconds** —
     byte-real, not a fake ~5% stall (the old `_downloaded_bytes` bug class).
   - ☐ Navigate away (Settings → General) and back mid-download: progress
     survives, no restart.
10. **Interruption drill (the one deliberate sabotage):** mid-download, turn
    Wi-Fi off for ~20 s, then on.
    - ☐ The download recovers on its own or offers ONE clear Retry that
      resumes. Wedged forever / silent 0% / needing app restart = FAIL
      (this is what the reset machinery exists for).
11. When it lands: Setup status → Transcribe shows **Ready** with the model
    named. The status must say ready only when a model can actually load.

## Phase D — First recording (10 min)

12. Play any video with speech (YouTube in Safari). Hit **Record Meeting**
    (or Ctrl+Shift+M). Speak a few sentences yourself too.
    - ☐ **No permission prompt appears here** — consent was settled in the
      wizard (step 7). A consent prompt at record time = the wizard check
      didn't stick; FAIL.
    - ☐ **Purple system-audio dot** appears in the menu bar (expected —
      the honest indicator).
    - ☐ Recording waveforms move for BOTH channels (them = video, me = you).
    - ☐ The video keeps playing normally (the tap never disturbs playback).
13. Stop after ~2 minutes.
    - ☐ Transcript appears, both speakers labeled, readable paragraphs.
    - ☐ Timing: note how long stop → transcript takes on this machine.
    - ☐ Safety net (only if system audio failed anyway): the meeting must
      still exist as a mic-only meeting with an honest warning — the old
      "No system audio reached the encrypted spool" hard error is retired
      and must never appear.

## Phase E — Notes without an engine (5 min)

14. A fresh account has **no Ollama / no LLM**. The meeting must show the
    honest state: transcript saved, a clear "notes need a model" explanation,
    and a path forward (Settings → Notes).
    - ☐ **No dead end, no raw JSON, no spinner-forever.** The transcript is
      never lost or hidden behind the missing notes step.
15. Optional full path: install Ollama, `ollama pull` a small model, then use
    **Generate notes** on the same meeting.
    - ☐ Retroactive notes work without re-recording.

## Phase F — The seams (5 min)

16. Quit and relaunch the app.
    - ☐ No wizard again; the meeting is there; Setup status all green —
      **including the Permissions card**: Microphone and System audio both
      show **Granted** (the probe result survived the relaunch).
    - ☐ With the app running, launch Adversaria from Applications again:
      it must **focus the existing window**, not start a second copy.
17. Settings → General → **Appearance**: flip through all five themes.
    - ☐ Every surface follows, tags/pills/buttons legible in each.
18. Transcript tab: select a misheard word → **Fix this word** → correct it.
    - ☐ It updates transcript + notes and lands in the dictionary.

---

## Verdict

- **PASS** = every ☐ green, zero manual retries anywhere, and you would hand
  this account's experience to a paying stranger without apologizing.
- Anything else: list every ❌/⚠️ below with the step number. Each becomes a
  TODO item; fix; **re-run the whole script from Phase 0 on a NEW fresh
  account** (a re-run on the same account is not a fresh run).

Findings:

1. …
2. …

_When macOS is done, the same ritual (adapted: installer, Defender/EDR
present, no admin) runs on a fresh Windows 11 VM for whatever Windows build
we bless — that script gets written when the Windows rewrite lands._
