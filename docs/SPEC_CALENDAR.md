# SPEC — Read-Only Calendar Integration (Google + Microsoft)

**Status:** Proposed (not implemented). This is an implementation spec for a
future session (human + AI). Nothing in this document is built yet.

**Author note / source-of-truth date:** Versions, scopes, and OAuth patterns
below were verified against current vendor docs and crate registries on
**2026-06-20**. Per CLAUDE.md principle #1, re-verify versions before you start —
this stack moves fast. Sources are cited inline.

> **One-line summary:** Add an **off-by-default, opt-in, read-only** calendar
> connection (Google Calendar and/or Microsoft Outlook) so the app can show
> upcoming meetings and pre-fill an **attendee roster** onto a recorded meeting.
> All OAuth and calendar HTTP happens in **Rust** (never the webview); tokens
> live in the **OS keychain** (not `config.json`, not SQLite). It is the most
> data-exposing feature in the product, so the privacy stance gates every part
> of it.

---

## 1. Goal & non-goals

### Goal
- Let a user **optionally** connect one or more calendar accounts (Google,
  Microsoft) **read-only**.
- **Primary near-term use (Phase 1):**
  1. Show a short list of **upcoming events** (today / next few hours) in the UI.
  2. When the user records, pre-fill the meeting's **attendee roster** from the
     event whose time window the recording falls inside, so attendees are real
     names/emails rather than Whisper's guess.
- **Later uses (Phase 2+):** a "pre-meeting prep" prompt (summarize prior
  meetings with the same attendees before a call) and **meeting auto-arming**
  (offer to start recording when a calendar event begins).

### Non-goals (explicitly out of scope)
- **No write access ever.** We never create, edit, move, delete, or RSVP to
  events. Read-only scopes only. This is a hard product constraint, not a phase
  deferral.
- **No server, no backend, no shared OAuth app.** There is no Adversaria-hosted
  redirect/token service. The app stays 100% local. (Consequence: the user must
  supply their own OAuth client — see §4, the hard prerequisite.)
- **No background polling by default.** Calendar is fetched on demand (app
  focus, manual refresh, recording start). No always-on sync daemon in Phase 1.
- **No storing of full calendar contents.** We do not mirror the user's calendar
  into SQLite. We fetch a small window on demand and keep only what the user
  attaches to a saved meeting (the roster). See §3.
- **No contact/directory/email scopes.** Only calendar read scopes.
- **No CalDAV / Apple Calendar / Exchange-on-prem** in this spec (possible later;
  EventKit on macOS is a separate, cleaner local path worth a future ADR).

---

## 2. Privacy guarantees (the contract)

These are guarantees the implementation **must** satisfy. Treat any violation as
a release blocker.

| Guarantee | How it's enforced |
|-----------|-------------------|
| **Off by default** | No calendar config exists until the user connects. `calendar` config block defaults to "not configured / disabled". The Settings section ships collapsed with an explicit consent explanation; nothing happens until the user clicks Connect. |
| **Opt-in, per provider** | Connecting Google and connecting Microsoft are separate, independent actions. Neither is implied by the other. |
| **Read-only** | Only `*.readonly` (Google) / `Calendars.Read` (Microsoft) scopes are ever requested. Code review checklist: grep for any non-`.readonly`/write scope string → must be zero. |
| **All network in Rust** | The webview never makes a calendar or OAuth HTTP request. OAuth (system browser + loopback capture) and Graph/Calendar calls go through Rust `reqwest`. The webview only invokes IPC commands. (Mirrors the existing rule: webview never talks to the Python service.) |
| **Tokens never in plaintext on disk** | Access + refresh tokens live in the **OS keychain** via the `keyring` crate (macOS Keychain, Windows Credential Manager). They are **never** written to `config.json` or SQLite. `config.json` holds only non-secret metadata (which account is connected, its email, scopes granted) — see §3. |
| **Client credentials are the user's** | The OAuth Client ID (and, for Google installed-app clients, the non-secret "client secret") are entered by the user and stored in the keychain too — not committed, not bundled. |
| **Fetched-on-demand, not mirrored** | Upcoming-events list is fetched live and held in memory only. The **only** calendar data persisted is the attendee roster the user attaches to a meeting (already-public-to-them names/emails of people they met with) — stored in the existing meeting record, same as today's `attendees`. |
| **Clear disclosure** | The Settings consent text states plainly: *what* is read (events in a small time window + attendee names/emails), *what is never done* (no writes, no upload, no audio/transcript shared), *where tokens live* (this Mac's keychain), and that data **stays on this machine**. |
| **One-click disconnect** | Disconnect deletes the keychain entries, clears the config metadata, and revokes the token at the provider (best-effort) so the grant is gone both locally and server-side. |
| **Honors privacy lock** | Calendar features add no new way to expose locked meetings; rosters on a locked meeting follow the existing lock behavior. |

**What is stored vs fetched-on-demand (precise):**

- **Stored (keychain):** access token, refresh token, token expiry, OAuth client
  id/secret per provider.
- **Stored (`config.json`, non-secret):** per-provider `enabled` flag, connected
  account `email`/`display_name`, `scopes_granted`, last-known `token_expires_at`
  (for UI "needs reconnect" hints — the token itself stays in keychain).
- **Stored (SQLite):** nothing new is required for Phase 1. Rosters reuse the
  existing `meetings.attendees` column. (Optional later: an `event_id`/`source`
  marker — see §3.)
- **Fetched on demand, kept in memory only:** the upcoming-events list and each
  event's attendee list. Discarded when the request completes (except the roster
  the user chooses to attach).

---

## 3. Recommended OAuth approach for Tauri 2

**Decision: OAuth 2.0 Authorization Code + PKCE, with a temporary loopback
(`http://127.0.0.1:<port>`) redirect captured by a local server, opened in the
system browser.** Tokens stored in the OS keychain via the `keyring` crate.

### Why loopback, not a custom URI scheme (deep link)
- **Google explicitly dropped custom URI schemes** for new installed-app clients
  ("Custom URI schemes are no longer supported due to the risk of app
  impersonation"); the supported native option is the **loopback IP address**
  redirect. ([Google: OAuth 2.0 for Native Apps](https://developers.google.com/identity/protocols/oauth2/native-app))
- **Google also retired the OOB (`urn:ietf:wg:oauth:2.0:oob`) copy-paste flow.**
  Loopback is the path that works for both providers with one code path.
- Microsoft supports both loopback and custom-scheme redirects for public
  clients, so loopback is the **common denominator** — one redirect strategy for
  both providers, less surface area.
- Deep-link redirects (`tauri-plugin-deep-link`) also work on Microsoft and add
  real friction on macOS: deep links require a **fully bundled, installed `.app`**
  and don't fire under `tauri dev`, which complicates development and testing.
  Loopback works identically in dev and prod.

**Trade-off acknowledged:** the loopback port is unauthenticated, so the callback
handler **must** validate the OAuth `state` parameter (CSRF) and only accept the
single expected request, then shut the server down. (`tauri-plugin-oauth`'s own
docs flag this.)

### Crates / plugins (verified 2026-06-20 — re-verify before building)

| Purpose | Crate / plugin | Version (as of 2026-06-20) | Notes |
|---------|----------------|----------------------------|-------|
| Spawn the loopback callback server & hand the redirect URL back to the app | [`tauri-plugin-oauth`](https://github.com/FabianLars/tauri-plugin-oauth) (FabianLars) | `2` (v2.0.0, Tauri-2 compatible) | Minimal: starts a localhost server on a free port, captures the redirect, returns it. We do the PKCE + token exchange ourselves in Rust. |
| Open the consent URL in the **system** browser | `tauri-plugin-shell` (`shell.open`) — **already a dependency** (`Cargo.toml:18`) | `2` | Or `tauri-plugin-opener` `2` if preferred; shell is already present, so reuse it. |
| Secure token storage in OS keychain | [`keyring`](https://crates.io/crates/keyring) | `keyring = "4"` (4.0.x current; was 3.6.x) — enable native backends (`apple-native`, `windows-native`) | macOS Keychain + Windows Credential Manager. **Do NOT use `tauri-plugin-stronghold`** — it's being deprecated and removed in Tauri v3, and it doesn't use the OS keychain. ([keyring-rs](https://github.com/open-source-cooperative/keyring-rs), [Tauri discussion #7846](https://github.com/orgs/tauri-apps/discussions/7846)) |
| HTTP (token exchange + calendar reads) | `reqwest` — **already a dependency** (`Cargo.toml:24`) | `0.12` | Reuse it. No new HTTP stack. |
| PKCE + token types | Hand-roll a tiny PKCE helper (S256: SHA-256 of a random verifier, base64url) in a new `oauth.rs`. A full OAuth crate (e.g. `oauth2`) is optional but adds weight for a flow this small. | — | Keep it small per CLAUDE.md §2. SHA-256 via `sha2`; random via `rand` or `getrandom`. |

> **Why not Stronghold:** prior Tauri guidance recommended it, but it is now
> slated for removal in Tauri v3 and stores secrets in its own encrypted DB
> (needs a password/key you'd have to store anyway), **not** the OS keychain.
> `keyring` is the native, future-proof choice for OAuth refresh tokens.

### The flow (per provider), all in Rust
1. **Read client config** from keychain (Client ID, optional Google client
   secret). If absent → return an error the UI turns into "enter your OAuth
   credentials first" (the §4 prerequisite).
2. **Generate PKCE** `code_verifier` (random, 43–128 chars) + `code_challenge`
   (`S256`), and a random `state`.
3. **Start the loopback server** (`tauri-plugin-oauth`); it gives back the actual
   `127.0.0.1:<port>`. Build the redirect URI from it.
4. **Open the system browser** (`shell.open`) to the provider's authorization
   endpoint with: `client_id`, `redirect_uri`, `response_type=code`,
   `scope`, `code_challenge`, `code_challenge_method=S256`, `state`,
   `access_type=offline`+`prompt=consent` (Google, to guarantee a refresh
   token), and for Microsoft the `common` tenant authorize URL.
5. **Capture the redirect** on loopback; **validate `state`**; pull `code`.
6. **Exchange `code` for tokens** via `reqwest` POST to the token endpoint, with
   `code_verifier` (PKCE). Public clients send **no** secret (Microsoft); Google
   installed-app clients send their (non-confidential) client secret if their
   client type requires it.
7. **Store** access token, refresh token, expiry, and account email in the
   keychain; write non-secret metadata to `config.json`.
8. **On expiry**, refresh transparently using the refresh token before any
   calendar read; if refresh fails (revoked/expired), mark the provider as
   "needs reconnect" in config and surface a non-blocking UI hint.

### Provider endpoints & scopes (verified 2026-06-20)

**Google** ([authorize/token endpoints](https://developers.google.com/identity/protocols/oauth2/native-app), [scopes](https://developers.google.com/workspace/calendar/api/auth))
- Authorize: `https://accounts.google.com/o/oauth2/v2/auth`
- Token: `https://oauth2.googleapis.com/token`
- Revoke: `https://oauth2.googleapis.com/revoke`
- Scope (use the narrowest): `https://www.googleapis.com/auth/calendar.events.readonly`
  (view events on all calendars). Use `calendar.readonly` only if you later need
  calendar-list metadata. Prefer `events.readonly` for Phase 1.
- Read events: `GET https://www.googleapis.com/calendar/v3/calendars/primary/events?timeMin=…&timeMax=…&singleEvents=true&orderBy=startTime`
  → each event's `attendees[]` has `email`, `displayName`, `responseStatus`,
  `organizer`.

**Microsoft Graph** ([auth-code+PKCE flow](https://learn.microsoft.com/en-us/entra/identity-platform/v2-oauth2-auth-code-flow), [calendarView](https://learn.microsoft.com/en-us/graph/api/user-list-calendarview?view=graph-rest-1.0))
- Authorize: `https://login.microsoftonline.com/common/oauth2/v2.0/authorize`
- Token: `https://login.microsoftonline.com/common/oauth2/v2.0/token`
- Scope: `https://graph.microsoft.com/Calendars.Read` (+ `offline_access` for a
  refresh token, + `openid email profile` to get the account email).
- Public client → **no client secret** (PKCE only).
- Read events in a window:
  `GET https://graph.microsoft.com/v1.0/me/calendarView?startDateTime=…&endDateTime=…`
  → each event's `attendees[]` has `emailAddress.{name,address}`, `type`, `status`.

---

## 4. Provider setup the USER must do — HARD PREREQUISITE / BLOCKER

> **This is the gating dependency for the whole feature.** Because Adversaria has
> no backend and ships no shared OAuth app, **the user must register their own
> OAuth client** with Google and/or Microsoft and paste the resulting Client ID
> (and Google's client secret, if its client type provides one) into the app.
> Without this, nothing in §5–§7 can run. The UI must explain this up front and
> link to step-by-step instructions; treat "user has no credentials" as the
> expected initial state, not an error.

**Implications to design around:**
- This is **friction most users won't complete.** Set expectations: this is a
  power-user / privacy-conscious-user feature, consistent with the product.
- Document the steps in-app (a short guide + "Open Google Cloud Console" /
  "Open Azure Portal" buttons via `shell.open`).
- Google's unverified OAuth app shows a **"Google hasn't verified this app"**
  warning and, in "Testing" publishing status, **limits refresh-token lifetime
  to 7 days** and restricts use to listed test users. Since the user owns the
  app and is their own test user, this is acceptable but **must be disclosed**
  ("you may need to reconnect periodically"). Note this in the consent text.

### Google Cloud (per user)
1. Create / pick a project at console.cloud.google.com.
2. Enable the **Google Calendar API**.
3. Configure the **OAuth consent screen** (External; add yourself as a test
   user). Add the `calendar.events.readonly` scope.
4. Create an **OAuth client ID** of type **Desktop app**.
5. Copy the **Client ID** (and client secret, if shown) into Adversaria Settings.

### Azure (Microsoft, per user)
1. Azure Portal → **App registrations** → New registration.
2. Supported account types: personal + work/school (multi-tenant) as needed.
3. Add a **platform: Mobile and desktop applications**; add a redirect URI of
   type **public client / loopback** (`http://localhost`). Mark the app as a
   **public client** (allow public client flows = yes).
4. **API permissions** → Microsoft Graph → **Delegated** → `Calendars.Read`
   (+ `offline_access`, `openid`, `email`, `profile`). Grant consent.
5. Copy the **Application (client) ID** into Adversaria Settings.

---

## 5. Data model

### 5.1 New config fields — `src-tauri/src/types.rs` (`AppConfig`) + `src-tauri/src/config.rs` (defaults)

Add a single optional, non-secret block. **No tokens here.** All new fields use
`#[serde(default)]` so existing `config.json` files keep loading (matches the
established pattern at `types.rs:106-128`).

```rust
// types.rs — add to AppConfig
/// Read-only calendar integration. None / both-disabled = feature off (default).
#[serde(default)]
pub calendar: CalendarConfig,

// New types in types.rs
#[derive(Debug, Clone, Default, Serialize, Deserialize)]
pub struct CalendarConfig {
    #[serde(default)]
    pub google: Option<CalendarAccount>,
    #[serde(default)]
    pub microsoft: Option<CalendarAccount>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CalendarAccount {
    pub enabled: bool,            // off by default; user toggles
    pub email: String,            // connected account, for display
    pub display_name: String,
    pub scopes_granted: Vec<String>,
    pub token_expires_at: String, // RFC3339; UI "needs reconnect" hint only
    // NOTE: access/refresh tokens + client id/secret are NOT here — keychain only.
}
```

`config.rs::Default for AppConfig` adds `calendar: CalendarConfig::default()`
(both providers `None` → feature off).

### 5.2 Keychain entries (via `keyring`) — new `src-tauri/src/calendar/tokens.rs`

Service name `"adversaria-calendar"`, account key per provider, e.g.:
- `google:client` → JSON `{ client_id, client_secret? }`
- `google:tokens` → JSON `{ access_token, refresh_token, expires_at }`
- `microsoft:client`, `microsoft:tokens` → same shape.

### 5.3 "An attendee from calendar" — what it looks like

Phase 1 reuses the **existing** `meetings.attendees: Vec<String>` (no schema
change). A calendar attendee is rendered to the same display-string convention
already used (`types.rs:57-59`, e.g. `"Sarah Chen — sarah@acme.com"`), so the
existing meeting view and `update_attendees` command work unchanged.

In flight (in-memory only), an attendee is richer:

```rust
// types.rs — used by the live "upcoming events" command, not persisted as-is
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CalendarEvent {
    pub provider: String,          // "google" | "microsoft"
    pub id: String,
    pub title: String,
    pub start: String,             // RFC3339
    pub end: String,
    pub attendees: Vec<CalendarAttendee>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CalendarAttendee {
    pub name: String,
    pub email: String,
    pub response_status: String,   // accepted/declined/tentative/needsAction
    pub organizer: bool,
}
```

**Optional, Phase 2+** (only if "which event was this recording" needs to be
durable): add nullable columns `meetings.calendar_event_id TEXT` and
`meetings.calendar_provider TEXT`. Not required for Phase 1; mention in the
storage migration but leave unused until a later phase needs it.

---

## 6. Rust commands to add — `src-tauri/src/commands.rs` (+ new `src-tauri/src/calendar/` module)

Follow the existing convention: `#[tauri::command] async fn … -> Result<T, String>`
with human-readable errors. New module `calendar/` (`mod.rs`, `oauth.rs`,
`tokens.rs`, `google.rs`, `microsoft.rs`) keeps `commands.rs` thin.

```rust
// --- Credentials (the §4 prerequisite) ---

/// Store the user's own OAuth client credentials for a provider in the keychain.
/// provider = "google" | "microsoft". secret is None for Microsoft public clients.
#[tauri::command]
pub async fn calendar_set_credentials(
    provider: String,
    client_id: String,
    client_secret: Option<String>,
) -> Result<(), String>;

/// Whether credentials exist for a provider (drives the Settings UI state).
#[tauri::command]
pub async fn calendar_has_credentials(provider: String) -> Result<bool, String>;

// --- Connect / disconnect ---

/// Run the full OAuth + PKCE + loopback flow in Rust, store tokens in the
/// keychain, write non-secret account metadata to config. Returns the account.
#[tauri::command]
pub async fn calendar_connect(
    app: AppHandle,
    provider: String,
) -> Result<CalendarAccount, String>;

/// Delete keychain tokens, clear config metadata, best-effort revoke at provider.
#[tauri::command]
pub async fn calendar_disconnect(provider: String) -> Result<(), String>;

/// Connection status for both providers (for Settings + meeting view).
#[tauri::command]
pub async fn calendar_status() -> Result<CalendarConfig, String>;

// --- Reads (on demand; refreshes the token first if needed) ---

/// Upcoming events across all connected+enabled providers within [now, now+window_minutes].
/// In-memory only; nothing persisted. Used by the upcoming-events list and roster pre-fill.
#[tauri::command]
pub async fn calendar_upcoming_events(
    window_minutes: u32,
) -> Result<Vec<CalendarEvent>, String>;

/// The single event whose [start,end] contains `at` (RFC3339), if any — used to
/// pick the roster for a just-recorded meeting. Returns None if no match.
#[tauri::command]
pub async fn calendar_event_at(at: String) -> Result<Option<CalendarEvent>, String>;
```

**Wiring:** register all of the above in the `invoke_handler!` (alongside the
existing commands) and add `tauri-plugin-oauth`'s init in the builder. Token
refresh is internal to `calendar/oauth.rs` (called before each read), not its own
command. Note the **existing gotcha** (CLAUDE.md): per-request config is read
fresh on each call (like `configured_model()` at `commands.rs:180`) so a connect
takes effect without restart — but tokens come from the keychain, not the cached
`AppState` HTTP client, so they're naturally live.

---

## 7. Frontend

### 7.1 Typed IPC wrappers — `src/lib/tauri.ts`

Add 1:1 wrappers (matching the file's existing style, e.g. lines 130-136) plus
the new types in `src/types.ts` (`CalendarConfig`, `CalendarAccount`,
`CalendarEvent`, `CalendarAttendee`):

```ts
export function calendarStatus(): Promise<CalendarConfig> {
  return invoke("calendar_status");
}
export function calendarSetCredentials(provider: string, clientId: string, clientSecret: string | null): Promise<void> {
  return invoke("calendar_set_credentials", { provider, clientId, clientSecret });
}
export function calendarHasCredentials(provider: string): Promise<boolean> {
  return invoke("calendar_has_credentials", { provider });
}
export function calendarConnect(provider: string): Promise<CalendarAccount> {
  return invoke("calendar_connect", { provider });
}
export function calendarDisconnect(provider: string): Promise<void> {
  return invoke("calendar_disconnect", { provider });
}
export function calendarUpcomingEvents(windowMinutes: number): Promise<CalendarEvent[]> {
  return invoke("calendar_upcoming_events", { windowMinutes });
}
export function calendarEventAt(at: string): Promise<CalendarEvent | null> {
  return invoke("calendar_event_at", { at });
}
```

### 7.2 Settings "Calendar" section — `src/components/Settings.tsx`

A new collapsed-by-default section, visually consistent with existing Settings
blocks. States:

1. **Not connected (default):** a clear **consent explanation** before any
   button — *what is read* (your events in a small time window + attendee names
   and emails), *what is never done* (no writing to your calendar, no uploading
   anything, your audio/transcripts are never shared), *where tokens live* (this
   Mac's keychain), *that it stays on this machine*, and *that you must supply
   your own Google/Microsoft OAuth credentials first*. Two providers shown
   independently.
2. **No credentials yet:** inline fields for **Client ID** (+ Google client
   secret, optional) with "Open Google Cloud Console" / "Open Azure Portal"
   helper links (`shell.open`) and a short setup checklist. **Connect** is
   disabled until credentials are saved.
3. **Credentials saved, not connected:** **Connect <Provider>** button → triggers
   `calendar_connect` (opens system browser). Shows a spinner / "complete sign-in
   in your browser" hint.
4. **Connected:** show account email, granted scopes (read-only), an
   **enabled** toggle (still off until the user flips it — connecting ≠
   enabling), a "needs reconnect" hint if `token_expires_at` has passed, and a
   **Disconnect** button.

The default state of the toggle is **off**. Nothing fetches calendar data until
the provider is both connected **and** enabled.

### 7.3 Where rosters surface in the meeting view

- **Upcoming events (optional, Phase 1):** a small read-only "Upcoming" strip on
  the home/recording screen listing the next few events (title + time), populated
  via `calendarUpcomingEvents`. Purely informational; no actions.
- **Roster pre-fill (the primary value):** after a recording stops and
  `transcribe_and_summarize` returns, call `calendarEventAt(recordedAt)`; if an
  event matches the recording's time window, **propose** its attendees to merge
  into the meeting's existing attendee list (the component that already renders
  `meeting.attendees` and calls `updateAttendees`). Make it a **suggestion the
  user confirms**, not an automatic write — keeps the user in control and avoids
  attaching the wrong meeting's roster. Calendar-sourced attendees render in the
  existing display-string format so no new attendee UI is required.

---

## 8. Phased implementation plan

**Phase 0 — Prerequisite plumbing (no calendar reads yet)**
- Add `keyring = "4"` + `tauri-plugin-oauth = "2"` to `Cargo.toml`; init the
  plugin. Create the `calendar/` module skeleton (`mod.rs`, `oauth.rs`,
  `tokens.rs`).
- Implement `calendar_set_credentials` / `calendar_has_credentials` (keychain
  round-trip) and the PKCE helper. → **verify:** can store and read back a
  client id from the OS keychain; `cargo check` + `npx tsc --noEmit` clean.

**Phase 1 — Minimal: connect + upcoming events + attendee rosters (the goal)**
- Implement the full OAuth+PKCE+loopback flow for **one provider first**
  (Google), then Microsoft. `calendar_connect` / `calendar_disconnect` /
  `calendar_status`; token refresh-before-read.
- Implement `calendar_upcoming_events` and `calendar_event_at` (Google Calendar
  v3 / Graph calendarView).
- Settings "Calendar" section (consent text, credentials entry, connect/disconnect,
  enable toggle).
- Roster pre-fill suggestion after recording; optional "Upcoming" strip.
- → **verify (manual, with a real account):** connect succeeds in a fresh build;
  upcoming events list matches the real calendar; recording during an event
  proposes the correct roster; disconnect removes keychain entries (check with
  `security find-generic-password` on macOS) and revokes server-side.
- → **privacy verify:** webview makes **zero** calendar/OAuth network requests
  (inspect with devtools network tab — all traffic is Rust-side); tokens are not
  present in `config.json` or the SQLite DB on disk.

**Phase 2 — Pre-meeting prep prompt**
- Before/at the start of a calendar event, gather prior meetings sharing those
  attendees and produce a short prep summary via the existing local LLM path
  (reuse `ask_all_meetings`-style retrieval, scoped by attendee). Off by default.

**Phase 3 — Meeting auto-arming**
- When a connected+enabled calendar event begins and the existing meeting-detection
  signals a call, **offer** (notification, not auto-start) to begin recording.
  Reuses `auto_detect`/tray plumbing. Strictly opt-in; never records without a
  user action.

**Phase 4 (optional) — macOS EventKit path**
- Consider a separate, login-free local calendar source on macOS via EventKit
  (no OAuth, no user-supplied client). Different enough to warrant its own ADR;
  not part of this spec.

---

## 9. Risks & open decisions

| # | Risk / open decision | Notes / recommendation |
|---|----------------------|------------------------|
| 1 | **User-supplied OAuth client is a steep barrier** (§4). Most users won't finish setup. | Accept it — it's the price of zero-backend privacy. Make the in-app guide excellent; consider a short screen recording. Re-evaluate only if a privacy-preserving shared client becomes viable (it generally isn't for a local app). |
| 2 | **Google "Testing" apps cap refresh tokens at 7 days** → periodic reconnect. | Disclose in consent text; surface a gentle "reconnect" hint when `token_expires_at` lapses. Publishing the app to "Production" avoids it but adds Google verification friction the user owns. |
| 3 | **Loopback port is unauthenticated.** | Mandatory: validate OAuth `state`, accept exactly one matching request, then shut the server down immediately. Bind to `127.0.0.1` only. |
| 4 | **`keyring` v4 backend selection / Windows quirks.** Reported rough edges on Windows historically. | Pin a version, enable `apple-native` + `windows-native`, and test the keychain round-trip on **both** OSes early (Phase 0). Handle "keychain locked / access denied" with a clear error. |
| 5 | **Matching a recording to the right event** (overlapping/back-to-back meetings, all-day events, wrong time zone). | Keep it a **user-confirmed suggestion**, never an automatic write. Use the recording's actual start/end; ignore all-day events; normalize time zones to UTC for comparison. |
| 6 | **Scope creep toward write/contacts.** | Hard line: only `*.readonly` / `Calendars.Read`. Add a code-review gate (grep for non-readonly scopes). |
| 7 | **Multiple calendars / shared calendars / multiple accounts per provider.** | Phase 1: primary calendar, one account per provider. Multi-account is a later decision. |
| 8 | **Open decision: should "Upcoming events" persist or always be live?** | Recommendation: **always live, in-memory only** (privacy-first). Revisit only if offline display is requested. |
| 9 | **Open decision: revoke-on-disconnect failure handling.** | If the network revoke fails, still delete local tokens (local disconnect must always succeed) and tell the user to revoke in their account settings; provide a link. |
| 10 | **tauri-plugin-oauth maintenance.** Small community plugin (last release v2.0.0). | Acceptable for the tiny surface we use (a loopback capture). If it stalls, the loopback server is ~50 lines of `tiny_http`/`hyper` we can inline. Note this as a fallback. |

---

## Sources (verified 2026-06-20)

- Google — OAuth 2.0 for Native/Installed Apps (loopback, no custom scheme, PKCE optional-but-recommended, no client secret for some client types): https://developers.google.com/identity/protocols/oauth2/native-app
- Google — Choose Calendar API scopes (`calendar.events.readonly`): https://developers.google.com/workspace/calendar/api/auth
- Microsoft — Auth code flow + PKCE, public client (no secret): https://learn.microsoft.com/en-us/entra/identity-platform/v2-oauth2-auth-code-flow
- Microsoft Graph — List calendarView (read events in a window, attendees): https://learn.microsoft.com/en-us/graph/api/user-list-calendarview?view=graph-rest-1.0
- `tauri-plugin-oauth` (FabianLars) — loopback capture, Tauri 2 (`= "2"`, v2.0.0): https://github.com/FabianLars/tauri-plugin-oauth
- `keyring` crate — cross-platform OS keychain, v4.x, native backends: https://crates.io/crates/keyring and https://github.com/open-source-cooperative/keyring-rs
- Tauri secure-storage discussion (Stronghold deprecation / keyring guidance): https://github.com/orgs/tauri-apps/discussions/7846
- Tauri Stronghold plugin (being deprecated; removed in v3): https://v2.tauri.app/plugin/stronghold/
