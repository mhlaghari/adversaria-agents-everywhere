# Friend beta invite — draft (first external tester)

_Tester profile: hops meeting-to-meeting all day — the core Adversaria use
case. Send personally (WhatsApp/iMessage/email), not as a campaign._

## The message (adapt the first line to the actual conversation)

> Following up on what we talked about — here's the app. It sits in your
> meetings (no bot joins), records locally, and gives you notes, action items,
> and a weekly summary. Nothing leaves your Mac — no cloud, no uploads, which
> is the whole point.
>
> Install:
> 1. You need an Apple Silicon Mac (M1 or newer).
> 2. Open the DMG, drag Adversaria to Applications, launch it — no security
>    warnings, it's notarized by Apple.
> 3. First launch downloads the on-device models (a few GB, one time) and asks
>    for microphone + screen-recording permissions — that's how it hears both
>    sides of a call without a bot.
>
> Then just take your meetings like normal for a few days. I'll ping you for
> 10 minutes of feedback at the end of the week.

## Feedback questions (ask after ~3 days of real use)

1. Install and first run — where did you hesitate or almost give up?
2. Back-to-back meetings: did starting/stopping capture fit your flow
   (hotkey, auto-detect), or did you forget to record some meetings?
3. Read your notes from two days ago: are they good enough that you didn't
   need to rewatch/re-ask anyone anything?
4. The To-dos board and Monday weekly briefing — useful, ignorable, or noise?
5. Did anything feel slow, confusing, or creepy? Did you look for something
   that wasn't there?

## Logistics

- Build to send (2026-07-18 evening): the **notarized** DMG —
  `src-tauri/target/release/bundle/dmg/Adversaria-0.3.49-beta-macos-arm64.dmg`
  (stapled; Gatekeeper: "accepted — Notarized Developer ID"). No install
  friction.
- Tester context: works at **Aleph Alpha**, back-to-back meetings — ideal ICP
  and a credible EU-AI-company early adopter.
- In-app beta registration is compiled out of staging builds (no production
  Formspree endpoint yet) — not a problem here; we already have his contact.
- Delivery: AirDrop / Drive link — the DMG is ~800 MB.
