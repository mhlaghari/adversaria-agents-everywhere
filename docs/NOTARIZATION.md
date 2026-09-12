# Adversaria macOS signing and notarization runbook

> Operational record and repeatable release procedure. Last verified on
> 2026-07-19 on an Apple-Silicon Mac running macOS 26.5.2, Xcode 26.6, and
> `notarytool` 1.1.2.

This document records the account, certificate, credentials profile, commands,
verification gates, and failure recovery used to notarize Adversaria. It does
not contain passwords, private keys, or the production Formspree endpoint.

Notarization is not the same as code signing:

1. Every executable object is signed with the Apple-issued Developer ID
   certificate and hardened runtime.
2. The signed DMG is uploaded to Apple's notary service.
3. After Apple returns `Accepted`, the ticket is stapled to the DMG.
4. Gatekeeper verifies the stapled ticket on another Mac without a terminal
   workaround or network dependency.

The canonical implementation is [`scripts/build-dmg.sh`](../scripts/build-dmg.sh).
Do not replace its release path with a collection of manual signing commands.

## 1. Account and signing identity used

| Item | Value |
|---|---|
| Apple Developer Apple Account | `hamza@lagharilabs.com` |
| Membership | Individual, under the legal name Mohammad Hamza Laghari |
| Apple Team ID | `4MY4PH5PHC` |
| Distribution certificate | `Developer ID Application: Mohammad Hamza Laghari (4MY4PH5PHC)` |
| Certificate SHA-256 fingerprint | `9F:84:81:FC:FE:1A:A9:0D:4C:06:19:B1:38:B9:E5:61:25:C0:2F:CE:64:87:FF:54:17:6E:4F:86:4A:EF:69:45` |
| Certificate validity | 2026-07-18 through **2027-02-01** |
| Local `notarytool` Keychain profile | `adversaria-notary` |
| App bundle identifier | `com.meetingnotetaker.app` |
| CPU/installer target | Apple Silicon / `arm64` |

The Git commit email (`mhlaghari@gmail.com`) and the forwarding destination for
the Laghari Labs mailbox are unrelated to signing. The Apple Developer account
used for this release is the `hamza@lagharilabs.com` account above.

The self-signed identities `NotchyPrompter Dev` and `Adversaria Dev` are only
for local development. They cannot be used for public distribution or Apple
notarization.

### Verified submission record

The local `adversaria-notary` profile currently returns this audit history:

| Date (UTC) | Artifact | Job ID | Result |
|---|---|---|---|
| 2026-07-18 10:47 | `Adversaria_aarch64.dmg` | `f72d0d8a-ac6a-4719-9dcb-e0d3cac63e1b` | Accepted |
| 2026-07-18 14:33 | `Adversaria-0.3.48-beta-macos-arm64.dmg` | `04785765-bd62-4fa2-9ba4-6af708b97282` | Invalid |
| 2026-07-18 15:36 | `Adversaria-0.3.49-beta-macos-arm64.dmg` | `0bf28d02-ee28-45d3-8fd1-5a8311e36e33` | Accepted |

The accepted 0.3.49 DMG was stapled and produced Gatekeeper's expected verdict:
`accepted`, with `source=Notarized Developer ID`.

The 0.3.48 attempt failed because the main executable and numerous nested
Rapid-MLX Mach-O files still had non-Developer-ID signatures. That failure led
to commit `f0ec7f2` (`fix(release): harden Developer ID notarization`), which
made the script verify the signing authority across the nested Mach-O tree,
sign the DMG, staple it, and generate provenance only after stapling. Commit
`8d85ed8` added retries for intermittent Apple timestamp-service failures.

## 2. One-time setup on a new release Mac

### 2.1 Install the Developer ID certificate

The certificate and its private key must both be present. A `.cer` file by
itself is insufficient.

Preferred setup on the Mac that originally created the identity:

1. Open Xcode.
2. Open **Xcode > Settings > Accounts**.
3. Select `hamza@lagharilabs.com` and team `4MY4PH5PHC`.
4. Open **Manage Certificates**.
5. Create or install a **Developer ID Application** certificate.

For a replacement release Mac, export the certificate **with its private key**
as a password-protected `.p12` from Keychain Access, transfer it securely, and
import it into the new Mac's login keychain. Keep the `.p12` and its password in
the password manager or another encrypted backup, never in this repository.

Verify the installed identity:

```bash
security find-identity -v -p codesigning
```

The output must include exactly:

```text
Developer ID Application: Mohammad Hamza Laghari (4MY4PH5PHC)
```

Inspect expiry and fingerprint when diagnosing the identity:

```bash
security find-certificate \
  -c "Developer ID Application: Mohammad Hamza Laghari (4MY4PH5PHC)" \
  -p | openssl x509 -noout -subject -issuer -dates -fingerprint -sha256
```

Renew the certificate before 2027-02-01 and update any exported `.p12` used by
CI. The Team ID should remain the same after certificate renewal.

### 2.2 Create the app-specific password

Sign in to `account.apple.com` as `hamza@lagharilabs.com`, open **Sign-In and
Security > App-Specific Passwords**, and create one for Adversaria notarization.
This is not the normal Apple Account password.

Store it in the Keychain profile using an interactive secure prompt. Omitting
`--password` keeps the password out of shell history:

```bash
xcrun notarytool store-credentials adversaria-notary \
  --apple-id hamza@lagharilabs.com \
  --team-id 4MY4PH5PHC
```

Enter the app-specific password when prompted. `notarytool` validates the
credentials before saving them. Re-run this command if the password is revoked,
the Apple Account changes, or the Keychain profile is lost.

> **Pre-flight this before every release.** Run
> `xcrun notarytool history --keychain-profile adversaria-notary` *before*
> starting the build. On 2026-08-05 the credential was revoked between the start
> of a session and stage 7, so an hour-long build reached notarization and died.
>
> **A revoked password reports as a missing profile**, not as an auth failure:
> `Error: No Keychain password item found for profile: adversaria-notary`. Do not
> chase the keychain — `security` cannot see this item at all (notarytool uses the
> data-protection keychain), so absence proves nothing. Re-store the credential
> first, and only investigate further if a *freshly generated* password also 401s.
>
> **If the interactive prompt seems to ignore your paste** (it echoes nothing),
> pass `--password 'xxxx-xxxx-xxxx-xxxx'` explicitly, then clear it from shell
> history. Two attempts were lost to this.
>
> **Prefer an App Store Connect API key for release automation.** A `.p8`
> (`--key`, `--key-id`, `--issuer`) is not revoked when the Apple Account password
> changes, which is the failure above:
> ```bash
> xcrun notarytool store-credentials adversaria-notary \
>   --key ~/private_keys/AuthKey_XXXXXXXX.p8 --key-id XXXXXXXX --issuer <issuer-uuid>
> ```

Verify the saved profile without submitting a build:

```bash
xcrun notarytool history \
  --keychain-profile adversaria-notary \
  --output-format json
```

If this returns submission history, the profile works. `ADVERSARIA_NOTARY_PROFILE`
is an environment-variable name; it is **not** the profile name. The value on
this Mac must be `adversaria-notary`.

### 2.3 Preserve the separate updater signing key

Apple's certificate signs the app and DMG. The Tauri updater uses a different
minisign-compatible private key, normally stored at:

```text
~/.tauri/adversaria-updater.key
```

Its public half must match `plugins.updater.pubkey` in
`src-tauri/tauri.conf.json`. Back up the private key and its password securely.
Losing it prevents future versions from being accepted by already installed
copies of Adversaria. Never generate a replacement merely because a new Apple
Developer ID certificate was issued; the two identities have different jobs.

## 3. Before every notarized release

1. Use a committed, reviewed version of `scripts/build-dmg.sh`. Do not edit a
   build script while a freeze is running. A shell may read the file
   incrementally, and an in-progress edit previously killed a release freeze.
2. Make sure no other freeze or signing process is running.
3. Bump and verify the app version in all release manifests and update the
   changelog.
4. Run the repository's normal source and release-acceptance checks.
5. Confirm the production Formspree registration endpoint is available from the
   password manager or release environment.
6. Confirm the Developer ID identity, notary profile, and updater key:

```bash
security find-identity -v -p codesigning
xcrun notarytool history --keychain-profile adversaria-notary
test -f "$HOME/.tauri/adversaria-updater.key"
```

7. Ensure the signing certificate has not expired:

```bash
security find-certificate \
  -c "Developer ID Application: Mohammad Hamza Laghari (4MY4PH5PHC)" \
  -p | openssl x509 -noout -dates
```

8. Decide the updater channel: `beta` for design partners; `stable` only when
   promoting an artifact that passed clean-machine acceptance.

## 4. Canonical local release command

Run from the repository root. Replace the two placeholders; do not put the
app-specific Apple password in this command.

```bash
ADVERSARIA_SIGN_IDENTITY="Developer ID Application: Mohammad Hamza Laghari (4MY4PH5PHC)" \
ADVERSARIA_NOTARY_PROFILE="adversaria-notary" \
ADVERSARIA_RELEASE_MODE=1 \
ADVERSARIA_RELEASE_CHANNEL=beta \
ADVERSARIA_FORMSPREE_ENDPOINT="https://formspree.io/f/<production-form-id>" \
ADVERSARIA_DMG_OUTPUT="src-tauri/target/release/bundle/dmg/Adversaria-<version>-beta-macos-arm64.dmg" \
ADVERSARIA_INSTALL=0 \
./scripts/build-dmg.sh
```

Use `ADVERSARIA_INSTALL=0` for a distribution build so the release process does
not silently replace the app currently installed in `/Applications`. Install
the accepted artifact deliberately during the acceptance test.

Release mode intentionally fails if any of these are missing:

- Developer ID signing identity
- `ADVERSARIA_NOTARY_PROFILE`
- production Formspree endpoint
- Tauri updater private key

The build can take a long time because the two Python/ML runtimes contain
hundreds of Mach-O objects that must be signed and timestamped. Do not launch a
second freeze against the same checkout.

### What the script does

1. Freezes the Python ML service with PyInstaller.
2. Freezes the pinned Rapid-MLX runtime.
3. Signs every nested Mach-O, then signs both sidecar launchers with their
   entitlements and hardened runtime.
4. Builds the selected Tauri updater channel.
5. Re-signs the bundled sidecars and main app, verifies the complete app, then
   repacks and signs the updater archive from that exact final app.
6. Packages and signs the DMG.
7. Submits the DMG with `notarytool --wait`, staples and validates the ticket,
   runs Gatekeeper assessment, and finally writes provenance for the stapled
   bytes.

The order matters. Repacking, re-signing, or otherwise changing the DMG after
notarization invalidates the relationship between the tested file, its hash,
and the release record. Stapling itself changes the DMG bytes, which is why
provenance is generated after stapling.

## 5. Required verification before distribution

Define explicit paths to avoid accidentally checking an older build:

```bash
APP="src-tauri/target/release/bundle/macos/Adversaria.app"
DMG="src-tauri/target/release/bundle/dmg/Adversaria-<version>-beta-macos-arm64.dmg"
```

### 5.1 Verify signatures and identity

```bash
codesign --verify --deep --strict --verbose=2 "$APP"
codesign -dvvv "$APP" 2>&1 | rg 'Authority|TeamIdentifier|Runtime Version'
codesign --verify --strict --verbose=2 "$DMG"
```

Expected authority and team:

```text
Authority=Developer ID Application: Mohammad Hamza Laghari (4MY4PH5PHC)
TeamIdentifier=4MY4PH5PHC
```

The build script already checks every nested Mach-O whenever a notary profile is
configured. Do not weaken or remove that check to get a build through.

### 5.2 Verify notarization, stapling, and Gatekeeper

```bash
xcrun stapler validate "$DMG"
spctl --assess --type open \
  --context context:primary-signature \
  --verbose=4 "$DMG"
```

Expected Gatekeeper result:

```text
accepted
source=Notarized Developer ID
```

Review Apple's server-side record when needed:

```bash
xcrun notarytool history \
  --keychain-profile adversaria-notary \
  --output-format json

xcrun notarytool info <job-id> \
  --keychain-profile adversaria-notary \
  --output-format json
```

### 5.3 Test the actual distributed DMG on another Mac

Use the exact DMG and hash that will be sent or published. On a clean Mac:

1. Download it through the intended distribution path so quarantine is applied.
2. Open the DMG and drag Adversaria to `/Applications`.
3. Launch normally. Do **not** use `xattr`, right-click bypasses, or terminal
   commands; those defeat the test.
4. Confirm there is no “Apple could not verify it is free of malware” warning.
5. Complete onboarding and grant microphone/screen-recording permissions.
6. Record, stop, transcribe, and summarize a real sample.
7. Quit and relaunch; verify permissions and data survive.
8. Confirm the installed version and exercise the updater when testing an update.

Only distribute the same stapled DMG that passed this test. Do not rebuild a
“stable” copy from the same source; promote/copy the already accepted artifact.

## 6. Failure recovery

### `No Keychain password item found for profile`

The environment variable is pointing at the wrong value, or the profile is not
present on this Mac. Recreate it with the interactive command in §2.2 and set:

```bash
ADVERSARIA_NOTARY_PROFILE=adversaria-notary
```

### Apple returns `Invalid`

Retrieve the full validation log; the console summary is not enough:

```bash
xcrun notarytool log <job-id> \
  --keychain-profile adversaria-notary \
  --output-format json
```

For 0.3.48, Apple reported `The binary is not signed with a valid Developer ID
certificate` for the main binary and nested Rapid-MLX libraries. The correction
was to sign and verify the entire Mach-O tree with the Developer ID identity,
not to repeatedly submit the same DMG.

### `A timestamp was expected but was not found`

Apple's timestamp service can fail intermittently. `sign_file()` in the build
script retries each sign up to three times with a five-second delay. If all
retries fail, stop and rerun from a clean freeze after confirming network and
Apple service health. Never remove `--timestamp` from a distribution build.

### Pre-notarization `spctl` rejection

A correctly Developer-ID-signed app may still be rejected before Apple accepts
the submission. The script records this intermediate result and performs the
real hard gate after stapling. A rejection **after** successful stapling is not
expected and must block distribution.

### Stapling fails after Apple says `Accepted`

Confirm the job with `notarytool info`, wait briefly for ticket propagation,
and retry `xcrun stapler staple <dmg>` followed by `stapler validate`. Do not
rebuild unless Apple rejected the uploaded bytes.

### Certificate missing or expired

Create/renew the Developer ID Application certificate through the same Apple
team, install the certificate with its private key, and update the encrypted
`.p12` used by CI. Recreating the certificate does not require changing the
bundle identifier, Team ID, notary profile name, or updater signing key.

### Permissions disappear on the build Mac

Changing from a self-signed identity to Developer ID changes macOS's identity
for TCC and Keychain access, so microphone/screen-recording permissions may need
to be granted once after the switch. This is separate from notarization. Once
all builds use the same Developer ID identity, normal rebuilds should retain the
stable identity.

## 7. Optional GitHub Actions release candidate

The repository contains `.github/workflows/release-candidate.yml`, designed for
a clean, self-hosted Apple-Silicon runner labelled `adversaria-release`. At the
time this runbook was written, `.github/` was still untracked; the workflow is
not active until it is reviewed and committed.

It expects the protected `macos-release` environment and these secrets:

| Secret | Purpose |
|---|---|
| `APPLE_DEVELOPER_ID_P12` | Base64-encoded Developer ID certificate plus private key |
| `APPLE_DEVELOPER_ID_PASSWORD` | Password protecting the `.p12` |
| `BUILD_KEYCHAIN_PASSWORD` | Password for the temporary CI keychain |
| `APPLE_ID` | `hamza@lagharilabs.com` |
| `APPLE_TEAM_ID` | `4MY4PH5PHC` |
| `APPLE_APP_PASSWORD` | Apple app-specific password |
| `ADVERSARIA_FORMSPREE_ENDPOINT` | Production registration endpoint |
| `TAURI_SIGNING_PRIVATE_KEY` | Existing Tauri updater private key |
| `TAURI_SIGNING_PRIVATE_KEY_PASSWORD` | Updater-key password, if configured |

CI imports the certificate into a temporary keychain, creates a temporary
`notarytool` profile named `adversaria-ci`, runs the same
`scripts/build-dmg.sh`, and uploads the DMG, updater archive/signature, and
provenance as immutable workflow artifacts.

The CI profile name is deliberately different from the local profile:

- Local interactive build: `adversaria-notary`
- GitHub Actions runner: `adversaria-ci`

Restrict workflow execution and secret access to trusted maintainers. Pull
requests from forks and unreviewed code must never receive release secrets.

## 8. Security and release rules

- Never commit the app-specific password, Apple Account password, `.p12`,
  certificate private key, updater private key, Formspree endpoint, or generated
  Keychain files.
- Do not use `NotchyPrompter Dev`, `Adversaria Dev`, or ad-hoc signing (`-`) for
  a distributable build.
- Do not use obsolete `altool`; this project uses `notarytool`.
- Do not skip nested Mach-O signing or use `--deep` as a substitute for signing
  code from the inside out.
- Do not publish a DMG merely because `notarytool` says `Accepted`; staple,
  validate, run Gatekeeper assessment, and perform the clean-machine test.
- Do not rebuild after acceptance to rename or promote a release. Name the
  artifact before submission, or copy the exact accepted bytes without changing
  their contents.
- Record the version, commit, artifact SHA-256, notary job ID, Gatekeeper result,
  and clean-machine result in the release handoff.
- Set calendar reminders at least 30 days before both the Apple Developer
  membership and Developer ID certificate expire.

## 9. Short checklist

```text
[ ] Version/changelog/release notes finalized
[ ] No concurrent freeze or build-script editor
[ ] Developer ID identity present and unexpired
[ ] notary profile adversaria-notary validates
[ ] Existing Tauri updater key present and matches pinned public key
[ ] Production Formspree endpoint supplied
[ ] RELEASE_MODE=1, correct beta/stable channel, explicit output filename
[ ] build-dmg.sh completes all seven stages
[ ] codesign deep/strict passes
[ ] notarytool result Accepted
[ ] stapler validate passes
[ ] spctl says accepted / source=Notarized Developer ID
[ ] Final provenance and SHA-256 recorded
[ ] Exact DMG passes clean-Mac install and real recording test
[ ] Exact accepted artifact published; no rebuild
```
