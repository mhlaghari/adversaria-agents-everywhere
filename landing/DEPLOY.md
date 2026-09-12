# Adversaria landing page — go-live runbook

> **⚠️ SUPERSEDED (2026-07-16): the page is LIVE at <https://lagharilabs.com/adversaria/>.**
> The deployed source of truth now lives in the separate `lagharilabs-website`
> repo (`public/adversaria/index.html`, private GitHub), served by Cloudflare
> Pages with a first-party `/api/waitlist` Pages Function → D1 (no Formspree).
> This runbook and the `index.html` here are kept as the original standalone
> reference only — edit the copy in `lagharilabs-website` from now on.

A single static file (`index.html`, self-contained — no build step, no dependencies).
Soft-launch goal: **collect waitlist emails** at `https://lagharilabs.io`.

Steps 1–3 are the ones only you can do (accounts, money, DNS). ~30 minutes total.

---

## 1. Wire the waitlist form (Formspree) — 5 min

1. Sign up at <https://formspree.io> (free tier = 50 submissions/mo; paid lifts it).
2. **+ New form** → name it "Adversaria waitlist" → copy the endpoint, which looks like
   `https://formspree.io/f/abcdwxyz`.
3. In `index.html`, replace **both** occurrences of `REPLACE_WITH_FORM_ID` with your
   real id (`abcdwxyz`). There are two forms — the hero and the final CTA — and they
   share one endpoint, so both feed the same list.
4. In Formspree: turn on email notifications to yourself, and (recommended) enable
   its built-in spam filter / reCAPTCHA.

> The form submits via `fetch` and shows an inline success message — no page reload,
> no redirect. Until the id is set, the form politely says it isn't connected yet.

## 2. Buy the domain — 5 min

- Register **lagharilabs.io** (Cloudflare Registrar is at-cost and pairs cleanly with
  Cloudflare Pages; Porkbun/Namecheap also fine).

## 3. Deploy — 10 min (pick one; all free)

**Cloudflare Pages (recommended — free, fast, easy custom domain):**
1. <https://dash.cloudflare.com> → Workers & Pages → Create → Pages → **Upload assets**.
2. Drag in the `landing/` folder (or connect the GitHub repo and set the build output
   directory to `landing`). No build command.
3. Custom domains → add `lagharilabs.io` → follow the DNS prompts (instant if the
   domain is on Cloudflare).

**Netlify / Vercel:** same idea — drag-drop `landing/`, or connect the repo with the
root/output set to `landing`, then add the custom domain. Both give a free
`*.netlify.app` / `*.vercel.app` URL immediately so you can test before DNS.

## 4. Social share image (`og.png`) — before you post links anywhere

`index.html` references `https://lagharilabs.io/og.png` for link previews (Slack,
iMessage, X, LinkedIn). Create a **1200×630** PNG and drop it in this folder.
Easiest source: a still from `marketing/launch-video-v4/renders/…` or a screenshot of
the hero. Without it, shared links show no image. *(Want me to generate one from the
hero design? Ask.)*

## 5. Verify before announcing

- [ ] Submit a test email → arrives in Formspree + your inbox.
- [ ] Open the live URL on phone + desktop — layout holds, form works.
- [ ] Paste the URL into Slack/iMessage — preview shows title, description, og.png.
- [ ] `https://` works and the domain resolves.

---

## Notes

- **This is the soft-public step** — a page + waitlist. The actual app download stays
  gated until macOS **notarization** is done (an Apple Developer account + Developer ID
  cert). Until then the build is Gatekeeper-blocked; see the top of
  [`../docs/LESSONS_LEARNED.md`](../docs/LESSONS_LEARNED.md) and
  [`../HANDOFF.md`](../HANDOFF.md).
- **Design source:** the app's own identity — dark glass, azure `#24A0ED`, Instrument
  Serif wordmark. For a pixel-exact wordmark match you can embed the app's bundled
  Instrument Serif (`src/lib/instrumentSerifFont.ts`) as a `@font-face` data URI; the
  page currently uses a system-serif stack so it stays dependency-free.
- **Copy is honest** — every claim maps to a shipped feature (on-device Whisper +
  diarization, live mic transcript, audio deleted after transcription, macOS-first
  beta with Windows next). Keep it that way as features change.
