# STRATEGY HANDOFF — Adversaria GTM / marketing baton

_A **living doc** for the marketing & launch workstream, sibling of the
engineering baton ([../HANDOFF.md](../HANDOFF.md)). Read this first before any
marketing/growth work; update it before you stop. The deep strategy lives in
[LAUNCH_PLAN.md](./LAUNCH_PLAN.md) (channel-ranked playbook, pressure-tested),
[STRATEGY.md](./STRATEGY.md) (the why), and
[marketing_strategy.md](./marketing_strategy.md) (competitive assessment) —
link there, don't duplicate._

> **⚠️ SUPERSEDED IN PART (2026-07-25).** The waitlist/private-beta posture below
> is no longer current: Adversaria is **free, MIT, open source and publicly
> downloadable** (v0.3.64), the site leads with a Download button, and a LinkedIn
> post is live. Ready-to-paste copy for every channel + the asset inventory now
> live in **[LAUNCH_ASSETS.md](./LAUNCH_ASSETS.md)** — start there.
> Positioning also shifted: lead with **organization**, not privacy.

**State (2026-07-18): the funnel is fully live, the hard launch gate is
cleared, and the product is at v0.3.46 — a deliberately TIGHTER launch story
(standalone notes hidden, Insights honestly labeled Beta). We are in PHASE 1
(quiet accumulation), blocked only on user inputs (§6.2) and the Apple
activation email. The demo-video script is done and still valid against
0.3.46; the next deliverable is the USER'S Loom recording.**

---

## 1. Where we stand (all verified live)

| Asset | State |
|---|---|
| Product | **v0.3.46 installed & stable (2026-07-18).** Since 0.3.43: `#` tag search (0.3.44) · to-do triage board w/ drag-and-drop, LLM **Weekly Briefing**, graph **people dossiers** + Obsidian vault sync, alarm digests (0.3.45) · weekly pager polish, **Insights → honest Beta** (your-delivery coaching only), **standalone notes hidden** (0.3.46). Net for marketing: the demo-able story is now "meetings → notes → to-dos → weekly briefing → knowledge graph", with no half-baked surfaces visible |
| lagharilabs.com | LIVE on Cloudflare Pages (config-panel strip removed, responsive-polished, 1200px content column) |
| lagharilabs.com/adversaria | LIVE — landing page w/ working waitlist, user calls it "perfect" |
| Waitlist backend | First-party: Pages Function → D1 (`lagharilabs-waitlist`, stores email/product/source ONLY — the restraint is the brand). At 0 rows, clean for real signups |
| Confirmation emails | Resend, verified domain; branded plain-text from adversaria@lagharilabs.com on every NEW signup (idempotent, fail-safe). E2e-verified to inbox |
| Email on domain | Cloudflare Email Routing ENABLED: hello@/hamza@/adversaria@ + catch-all → Gmail. Proven by Apple's own enrollment mail |
| Apple Developer | **🟢 NOTARIZATION LIVE (2026-07-18 evening).** Cert `Developer ID Application: Mohammad Hamza Laghari (4MY4PH5PHC)` in the keychain; first **notarized + stapled DMG exists**: `Adversaria-0.3.49-beta-macos-arm64.dmg` — Gatekeeper verdict "**accepted — source=Notarized Developer ID**" (the launch-plan hard gate's artifact). Remaining gate step: the **clean-machine install test**. Produced via the (still-uncommitted) build-dmg.sh notarization flow from the parallel workstream |
| First external tester | **Identified 2026-07-18; upgraded to the notarized build.** Friend works at **Aleph Alpha**, back-to-back meetings — ideal ICP + credible EU-AI early adopter. Send `Adversaria-0.3.49-beta-macos-arm64.dmg` (no install friction). Invite draft + feedback questions: [../marketing/beta/friend-invite-draft.md](../marketing/beta/friend-invite-draft.md) |
| Beta distribution policy | **Discussed 2026-07-18 (user: "how do I ensure only he downloads it?").** Reality: the download is controllable, the file isn't — notarized DMG runs anywhere, no activation by design (privacy brand forbids phone-home DRM; launch is free anyway). Policy: **AirDrop or 24 h R2 presigned links** for testers + a "just for you for now" line in invites. Escalation options when first-10 grows (not built): per-tester watermark baked into the DMG · 45-day beta expiry. Nuclear lever: Apple cert/ticket revocation kills Gatekeeper acceptance for ALL copies. NO license keys/activation — collides with "nothing leaves your machine" |
| Website distribution | **DECISION QUEUED (user ask 2026-07-18): downloadable DMG on lagharilabs.com.** Recommended: **Cloudflare R2** (same account as Pages/D1) — the ~786 MB DMG is far over Pages' 25 MiB/file limit; R2 has ZERO egress fees (100 downloads ≈ 78 GB out, free) and ~1¢/month storage; public bucket behind `dl.lagharilabs.com` + a Download button on /adversaria. Alternative: GitHub Releases on a public repo (2 GB/file, off-brand URL). R2 can later also host the in-app updater channel. ~30–60 min in the `lagharilabs-website` repo + R2 bucket; AWAITING GO |
| Site repos | `lagharilabs-website` (private GitHub, wrangler direct-upload deploys) · this repo now works on **`master`** (`handtest-hardening` retired 2026-07-18) |
| Animated launch videos | On disk, **NOT in git**: HyperFrames renders `marketing/launch-video-v3/renders/adversaria-launch-v3-final.mp4` (w/ VO + music mix pipeline) and `marketing/launch-video-v4/renders/adversaria-launch-v4-final.mp4` (Jul 10–14), plus the `video/` composition. Separate asset class from the Loom product demo — no user verdict recorded on which cut (if any) is launch-ready |

## 2. The strategy in one paragraph

Lead with **"nothing leaves your machine"** (the claim cloud rivals structurally
can't make); "no bot" is the second sentence. Direct fight = Hyprnote/Meetily
(open-source local rivals), not Granola. **Show HN is the primary launch motion**
(merit-based, no audience needed), Product Hunt a second peak 2–3 days later,
then one fitted subreddit per day, then newsletters/reviewers riding the HN
credibility. Launch **free-only**; monetization comes 30–60 days later from
**regulated client-facing solos** (lawyers/clinicians/consultants — compliance
framing), with prosumers as a $0 awareness funnel. Success = pull, not vanity:
**10 onboarded → 6 process real meetings → 3 retained weekly → 1–3 pay**.
Budget < $2k, $0 on upvotes/hunters ever. Full detail + risk table:
[LAUNCH_PLAN.md](./LAUNCH_PLAN.md) §7–8.

## 3. Two phases

**PHASE 1 — NOW (until the notarized clean-machine install passes):**
- Waitlist person-by-person (first-10 hand-picked invitees; right-click→Open
  install friction is acceptable for people who know Hamza)
- Directory pre-seeding so listings index by launch day: AlternativeTo (as
  alternative to Otter/Granola/Fireflies), SaaSHub, BetaList
- Product Hunt "Coming Soon" page (follower building; account needs age)
- Soft participation (helpful human, zero pitching, 10% rule) in r/macapps,
  r/LocalLLaMA, r/privacy
- Asset production: 60–90s captioned demo + 10–15s silent GIF, Show HN post
  draft, PH gallery, X/LinkedIn content calendar
- **Launch date stays soft — gated on the notarized clean-machine install, not
  the calendar**

**PHASE 2 — LAUNCH WEEK (gates green):** Show HN Tue/Wed 8–10am PT (answer every
comment ~6h) → PH separate day 12:01am PT → subreddit cascade → newsletter/
reviewer pitches ("front page of HN" as the hook). Channel ranking, titles,
mechanics, and risk mitigations: [LAUNCH_PLAN.md](./LAUNCH_PLAN.md) §7.

## 4. The toolkit (who does what)

**Installed 2026-07-16 from coreyhaines31/marketingskills** (reviewed; in
`~/.claude/skills/`): `launch` · `community-marketing` (Reddit playbooks) ·
`directory-submissions` · `cold-email` (beta invites) · `emails` (lifecycle) ·
`social` (X/LinkedIn + listening) · `copywriting` · `cro` · `public-relations`
(reviewer/newsletter pitches) · `competitors` (vs-pages) · `product-marketing`
(ICP context doc) · `marketing-plan`.
**Already present:** `content-engine`, `article-writing`, `market-research`,
`research-agent`, `deep-research`, `llm-council` (pressure-tests), `dataviz`,
Gmail/Calendar MCP, firecrawl/brave (channel research), Playwright (funnel QA).

**Division of labor (non-negotiable for HN/Reddit):** Claude drafts *everything*
— posts, replies, submissions, emails, scripts. **The user posts under his own
name and spends ~30 min/day replying** (Claude drafts each reply behind him).
Corporate-smelling content gets burned on HN/Reddit; authenticity is the whole
game. Never vote-ring, never "please upvote" (lifetime bans).

## 5. Claims discipline (risk P5 — read before writing ANY public copy)

No absolute privacy claims. Precise, true claims only: "no audio or transcript
is uploaded **in local mode**", enumerate every egress (updater check, opt-in
Groq path, OAuth), never "HIPAA-compliant"/"bar-approved" (say "designed for
confidentiality"), cite the Bilzerian/Otter story only via the public docket +
WaPo/NPR. The landing page copy already follows this — keep it that way.

## 6. Immediate queue

> **2026-08-17 — WINDOWS CTA FIXED (was a live 404 since ~08-11).** Every
> Windows link pointed at `releases/latest/download/…-setup.exe`, but releases
> have been macOS-only since v0.3.76 — guaranteed GitHub 404 for every Windows
> visitor. Now: Windows visitors get an honest "being rebuilt natively" note +
> an email capture into the first-party waitlist (D1, `source=windows-wait`) —
> so **Windows demand is now measurable** for the rewrite decision. Deployed,
> live-verified (0 stale .exe refs; API smoke-tested), committed `b4ca71d` in
> `lagharilabs-website`. SmartScreen note retired with it.
> **Founder direction (same day): launch push next** — HN + Product Hunt + a
> new X account (name TBD: company vs personal) + outreach to "Andrew"
> (The Next Big Thing). Assets already exist in LAUNCH_ASSETS.md §3; the
> Show HN gate (§6: ~5 clean non-developer first-runs) still stands. The §7
> legal note is RESOLVED (see LAUNCH_ASSETS §7: open-source/no-revenue
> framing; no public premium/pricing talk until he quits).
> **Same day, later: X ACCOUNT SECURED AND WIPED.** Decision: repurpose the
> founder's dormant aged account **@knubbe24_** (joined Dec 2014, 22
> followers) instead of a new signup (X was silently refusing signup emails
> to hamza@lagharilabs.com; new accounts get reach-throttled anyway). The
> full public footprint (~193 header count: political posts/reposts/replies
> + NFT-era content, 2021–2023) was deleted via browser automation on his
> explicit "yes delete everything": Posts, Replies, Reposts tabs all render
> empty and `from:knubbe24_` live search returns "No results". Header
> counter lags (24 at last check, falling to 0); re-verify in a day for
> deep-pagination stragglers. Andrew (Next Big Thing) LinkedIn DM drafted
> and sent by the founder. STANDING COPY RULE captured in agent memory: **no
> em dashes** in anything drafted for Hamza.
> REMAINING on the X account: prune following list (99, politics-heavy),
> new handle + display name + bio + avatar + banner, switch account email
> to hamza@lagharilabs.com, then 1–2 weeks of light warm-up posting before
> the launch thread.
> **Same day, evening: X FOLLOWING LIST FULLY CLEARED on founder's "ok
> clear X".** All ~97 follows removed in verified batches (10 political
> incl. Imran Khan/PTI/journalists/Grenell; Tate brothers + Bilzerian;
> ~80 NFT/crypto-era accounts incl. Binance/CZ, RTFKT, BAYC, LooksRare;
> also Bukele, Musk, Logan Paul, garyvee). Profile header confirms
> **2 Following**: the keepers IndieHackers + zaara_ai. X's own "you
> might like" now suggests Product Hunt and Courtland Allen — the
> algorithm already re-reads it as a builder account. During warm-up the
> founder should follow ~20-30 tech/builder accounts fresh.
> **EMAIL TO ANDREW SENT by the founder (same day)** — the final draft
> (local-first opener, confidential-projects motivation, feature list
> incl. self-building graph, time-saved-via-MCP traction framing, and a
> Workspaces teaser with no premium mention) went to
> andrew@thenextnewthing.ai. Awaiting his reply; likely next asks: demo
> video and a prep call.
> **🎉 ANDREW REPLIED (same day) — INTERESTED.** Correction: the show is
> **The Next NEW Thing** (thenextnewthing.ai), not "Next Big Thing". He
> asked 6 questions (models/tools powering it · live demo · on-device
> workflow + differentiation · problems solved · measurable traction ·
> what viewers can apply) and asked to continue over EMAIL:
> andrew@thenextnewthing.ai (Andrew rarely uses LinkedIn). Draft reply
> prepared in-session; traction section left for the founder's honest
> numbers. This is the warmest earned-media lead on the board.

> **2026-08-02 — /adversaria LANDING REPLACED with Hamza's own design,
> "Meetings become memory"** — real app screenshots + screen-capture videos,
> live and verified; audited claims-clean before deploy (canonical/OG +
> SmartScreen note added). Both download buttons → 0.3.70 stable URLs.
> Supersedes all prior landing copy references in this doc.

> **2026-08-01 — HUB71 ACCESS APPLICATION ✅ SUBMITTED (same day).** Deck =
> the LaghariLabs arcade brand, 16 slides incl. the UAE-mandate tie ("the UAE
> just mandated our category") and the git-verified velocity chart; PDF
> generated headless. Remaining Hub71 work: chase a partner/founder REFERRAL
> (form allows adding it? follow up) + start one UAE regulated-pilot
> conversation before review rounds.
> **(Verified deadline was 21 Aug 2026,
> Cohort 20, starts Feb 2027 — the "Aug 2" scare was a third-party error).** Full
> package prepared: paste-ready answers for every form field + an
> Adversaria-branded HTML deck (print → PDF ≤10MB) covering the required
> sections. Story: sovereign on-device notetaker → agentic loop (MCP
> write-back, the 10-minute to-do story) → suite of agentic/local/sovereign
> products; stage Post-launch/Pre-revenue, bootstrapped $0, ask = incentives +
> gov/enterprise access + investor network + setup. Hamza fills: nationality,
> sector dropdown, phone, relocation answer (recommended YES). Vault note
> Verified terms: AED 250k cash via uncapped/no-discount SAFE + 250k in-kind
> + optional 250k top-up for equity; founder on-ground Feb–Apr 2027; ADGM at
> onboarding (cost covered); ~1.1% acceptance. Deck now 12 slides incl. the
> REQUIRED Abu Dhabi economic-diversification slide. Next 20 days: source a
> Hub71 partner/founder REFERRAL + start any UAE regulated-pilot conversation
> (worth more than downloads in round 3). Vault `hub71-funding-terms` updated
> to verified.


1. ✅ **Demo-video script DONE (2026-07-17):** [../marketing/demo-video/SCRIPT.md](../marketing/demo-video/SCRIPT.md)
   — shot-by-shot for one Loom session → both cuts (80s captioned + 10–15s GIF).
   Concept: **the demo IS the meeting** (narration gets live-captioned on screen,
   then summarized) + the signature **Wi-Fi-OFF** proof beat. Includes prep
   checklist, exact VO lines (spoken decision + action item make the summary
   land), captions, YouTube packaging. **Re-validated 2026-07-18 against
   v0.3.46:** the script demos summary/transcript/action-items/Wi-Fi-off only —
   neither the hidden standalone notes nor the reworked Insights appear in any
   shot, so record as written (on 0.3.46, so the sidebar has no notes button —
   matches what viewers will install). **USER: rehearse 2–3×, record 2–3 takes,
   pick the cleanest.**
2. **NEW — first tester motion (2026-07-18):** send the friend the 0.3.47 DMG
   with the invite draft (`marketing/beta/friend-invite-draft.md`); collect
   feedback after ~3 days of real meetings. **Notarization unlock (user, ~15
   min):** (a) in Xcode → Settings → Accounts → Manage Certificates, create a
   **Developer ID Application** cert (this also proves the membership is
   active); (b) make an app-specific password at account.apple.com, then run
   `xcrun notarytool store-credentials adversaria-notary --apple-id <id>
   --team-id <TEAMID>` (type `! <cmd>` in-session). Claude then ships the
   first notarized DMG. ⚠️ Re-signing the local install with the new identity
   wipes this Mac's mic/screen-recording TCC grants once — re-grant on next
   launch.
3. **User inputs still owed:** X + LinkedIn handles (active/dormant?) · PH
   account created · first-10 invitee list (names + emails) · the words
   "start phase 1" · delete the Resend `lagharilabs-setup` key (hygiene).
4. **On "start phase 1", Claude produces:** beta invite email (cold-email
   skill) · AlternativeTo/SaaSHub/BetaList submissions (directory-submissions)
   · PH Coming Soon copy · 2-week X/LinkedIn calendar (social) · Reddit
   soft-participation plan (community-marketing) · `.agents/product-marketing.md`
   context doc (product-marketing skill) so every asset shares one ICP/positioning.
5. **On the Developer ID cert landing:** notarized build (engineering baton
   owns it) → clean-machine test → set the launch week.

## 7. Open strategic decisions (paused, not forgotten)

- **Individual vs Organization** Apple enrollment surface: enrolled (which type
  the user completed — confirm; affects the "identified developer" name users
  see in TCC prompts; org needs D-U-N-S + legal entity).
- **Open-sourcing the read-only MCP server** as the closed-source trust hedge +
  HN discovery asset (decided in principle 2026-06-28; not yet executed).
- Windows: launch is macOS-only; Windows untested for weeks (parity later).
- YC: assessment done 2026-07-16 (see claude-mem S1834/S1835) — the pull
  metrics in §2 are the YC-ready narrative; revisit after 90-day metrics exist.

---

_Changelog: 2026-07-17 — created (Claude), consolidating the 2026-07-16
launch-GO decision, funnel build-out, Apple enrollment, marketing-toolkit
install, and phase plan from the session record.
2026-07-18 — product state → v0.3.46 (tighter launch story: notes hidden,
Insights Beta, weekly/graph/briefing features since 0.3.43); repo baseline →
master; demo script re-validated against 0.3.46 (record as written); recorded
the on-disk (untracked) HyperFrames launch-video v3/v4 final renders as a
pending-verdict asset. Queue and phase plan unchanged — still blocked on §6.2
user inputs + Apple activation.
2026-07-18 (midday) — first external tester identified (meeting-hopper
friend); invite draft written; Apple state corrected: enrollment done but NO
Developer ID cert in the keychain yet — cert creation is the two-step unlock
for notarized builds (queue §6.2); pipeline + notarytool verified ready.
2026-07-18 (evening) — 🟢 NOTARIZATION DONE: cert created, first stapled DMG
(0.3.49) Gatekeeper-accepted; tester = Aleph Alpha employee, gets the
notarized build (invite draft updated, right-click step removed); website
download decision queued (R2 recommended). Remaining launch gate: the
clean-machine install test._
