# STRATEGY

_A **living doc** — the honest version on purpose, not a pitch._

> **Canonical strategy lives in [docs/STRATEGY.md](./docs/STRATEGY.md)** (the full
> grounded competitive/market memo, 2026-06-18). This file is the distilled bottom
> line for the stuntman read-first contract — keep it in sync; put new analysis in
> `docs/STRATEGY.md`.

## Bottom line (read this first)
1. **This is not "another meeting notetaker."** Adversaria is the **sovereign capture organ of lagharilabs OS** — alone it's a commodity; in the stack it makes "nothing leaves the building" actually true (replacing the OS's current dependency on cloud-processed Granola).
2. **The wedge is compliance, not consumer.** The privacy paradox is real — consumers say they care and don't pay. The buyers who *must* pay are regulated: legal (privilege-waiver risk), healthcare (no BAA from Granola), EU/sovereign, defense (air-gap/IL5).
3. **"Local" is table stakes, not a moat.** The niche is crowded (Hyprnote YC S25; Meetily — OSS, ~12.5k stars, *already ships the diarization we lack*). The moat is the integrated **capture → memory → action loop on-device**, the data flywheel, and the enterprise apparatus (SSO/audit/BAA) OSS clones won't build.
4. **Build ONE 10× workflow flawlessly first:** "every morning, your day's to-dos auto-deploy from yesterday's meetings + inbox, onto a board — fully local." Depth + reliability beats 15-skills-wide breadth.
5. **The business is the Sovereign/Enterprise self-hosted tier**, not Pro/prosumer (a knife-fight vs. free OSS + free MS/Zoom bundles — deprioritize).

## Honest assessment
- **Working:** the core on-device loop is real and mature on Windows; the macOS port builds + transcribes. Engineering is ahead of distribution.
- **Not working / risk:** **dev-only — nothing sells until it installs** (no signed package). **Bus factor = 1** across two repos + many integrations + sidecars. **Reliability at autonomy** — one wrong autonomous action destroys the trust the whole compliance pitch rests on. **Sovereign ↔ autonomy tension** — local small-model reasoning ceiling vs. agentic ambition.

## Hackathon terminal scope — 2026-09-12

The founder explicitly chose a cloud-backed CLI to demonstrate the
meeting → commitment → task → reviewed artifact workflow using OpenRouter and
Exa credits. Workspace creation, context attachments, task generation and
revision now stay inside the boxed terminal, reducing demo setup and navigation.
Keep the submission focused on that complete workflow and its source evidence.

This edition has separate plaintext local storage and sends selected audio/text
to its providers; the desktop's local-only positioning does not describe the CLI.
Show generated Mermaid/slide Markdown honestly as source artifacts, label
simulated screenshots, and present measured provider calls as individual samples.
Diagram artifacts now have a rendered local browser preview and SVG download;
show the diagram itself with O during the task review.
The next step is a real microphone/loopback rehearsal and submission, rather
than expanding the feature scope before the deadline.

The prepared CLI rehearsal now has five labeled sample tasks and four saved
outputs in the founder's current workspace. Use them to show review/revision
immediately, then run the queued example live. Seeded research is workspace
evidence, not a claim that Exa was queried during sample loading.

## Direction
Sequence the unglamorous gating work: (1) make the ONE workflow (to-do board from meetings) flawless and trustworthy; (2) packaging + signing (`.dmg`); (3) the enterprise apparatus (SSO, audit logs, BAA, SOC 2 path); (4) speaker diarization — or position explicitly around its absence. ICP beachhead: small law firms / boutique pro-services / exec teams who **can't** use cloud AI; buying trigger = liability avoidance, not productivity.

## Open questions / to revisit
- **Pre-meeting notes (calendar prep)** — build it or not? Clarify exact value first (see [SPEC.md](./SPEC.md) Open decisions).
- Per-tier line on what's air-gapped vs. cloud-allowed, given the sovereignty↔autonomy tension.
- When does the lagharilabs-OS bridge become the focus vs. "stay on Adversaria"? (User: stay on Adversaria for now.)

## Changelog
- 2026-09-12 — Recorded the founder-selected cloud CLI demo scope and completed workspace-to-reviewed-artifact workflow.
- 2026-06-19 — created during stuntman scaffold; distilled from [docs/STRATEGY.md](./docs/STRATEGY.md).
