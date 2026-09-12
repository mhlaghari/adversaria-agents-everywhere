# Windows code signing — decision memo (2026-08-11)

_Research memo from the cert spike (all claims verified against live sources
Aug 2026, cited in the session record; nothing from training memory). Decision:
**SSL.com eSigner OV, Tier 1, $180/yr.** Hamza executes the purchase — steps at
the bottom._

## The landscape, verified

- **Azure Trusted Signing ("Artifact Signing") remains unavailable to UAE
  orgs** — Microsoft's own eligibility list (checked 2026-08-03 revision):
  US/CA/EU/UK/AU/NZ/JP/KR/SG/CH/NO/IL. UAE never added. Ruled out.
- **EV buys nothing anymore.** Microsoft's current SmartScreen doc (updated
  2026-05-04) says verbatim that EV no longer bypasses SmartScreen; OV and EV
  both start "unrecognized" and build reputation purely from clean-download
  volume. Expect "unrecognized publisher" warnings to persist for **roughly a
  couple of months** post-launch at indie volume, whichever cert we buy. Plan
  launch comms accordingly; do not pay EV premiums.
- **Certum is cheapest (~$116/yr) but ruled out for CI:** SimplySign requires
  a live mobile-app tap per signing session and doesn't survive GitHub's
  ephemeral runners (community workaround = persistent VNC'd self-hosted
  runner — no).
- **DigiCert KeyLocker OV is the fallback** (~$369–438/yr via reseller only;
  direct exceeds budget): 1,000 signings/cert, unattended CI auth via API
  key + client cert. Caveat: their old "Software Trust Manager" GitHub Action
  is deprecated 2026-03-01 / retired 2026-05-01 — anyone copying Meetily's CI
  pattern must use the new "DigiCert Binary Signing" action.
- **Cert validity is capped at 458 days since 2026-02-27** (CA/B rule) —
  budget signing as an annual cost with every vendor.

## The pick: SSL.com eSigner OV Tier 1 — $180/yr

240 signings/yr ($1/extra) = ~120 builds/yr at our 2-signs-per-build
(installer + main exe). Standard validation 3–5 business days (skip the $599
expedite). CI is a solved pattern for exactly our stack: the official
`SSLcom/esigner-codesign` GitHub Action (CodeSignTool; auth = username +
password + credential ID + TOTP Base32 secret — fully headless), and a public
Tauri+NSIS reference wiring it through `tauri.windows.conf.json`'s
`signCommand` with a whitelist script so only the installer + main exe get
signed (sidecars/plugin DLLs skipped to preserve quota).

**Known-unverifiable risk, stated honestly:** no CA publishes UAE eligibility
explicitly (only Microsoft publishes an allowlist). SSL.com recognizing
Laghari Labs' specific registry (mainland DED vs free-zone — IFZA/RAKEZ/etc.)
as a "Reliable Data Source" is only discoverable by filing. If validation
stalls, fall back to DigiCert KeyLocker via reseller — their attorney/
accountant attestation-letter path is the escape hatch for awkward registries.

## Hamza's checklist (the purchase is founder-only)

1. Confirm the **exact legal entity name** as printed on the trade license,
   and whether Laghari Labs is mainland DED or a free-zone entity.
2. Gather: trade license · MoA/Certificate of Incorporation · passport or
   Emirates ID (authorized signatory) · reachable business phone (automated
   validation callback) · business address · company domain.
3. Order at https://www.ssl.com/certificates/code-signing/ — 1-year OV,
   **eSigner Cloud Signing** as key storage, Standard validation.
4. Submit docs in their portal; complete email link + phone callback.
5. On issuance: create a **Credential ID**, scan the TOTP QR into an
   authenticator, and keep the **Base32 secret** (CI needs the secret string,
   not the QR).
6. Add GitHub repo secrets: `SSL_COM_USERNAME`, `SSL_COM_PASSWORD`,
   `SSL_COM_CREDENTIAL_ID`, `SSL_COM_TOTP_SECRET`.
7. CI wiring (agent work, after issuance): `SSLcom/esigner-codesign` via
   Tauri `signCommand` + whitelist script; verify with
   `signtool verify /pa /v` before trusting CI output.

_The cert signs the **native Windows build** (the post-launch rewrite) just as
well as anything interim — ordering now starts the validation clock either way._
