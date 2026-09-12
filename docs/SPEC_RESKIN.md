# SPEC — Frontend Reskin (the `adversaria-samples` design)

**Status:** IMPLEMENTED (2026-06-22) — all phases done on branch `feat/reskin-phase0`, not merged;
minor polish remains (see §4). Source: the interactive prototype at
`/Users/mhlaghari/Documents/Documents/MyProjects/adversaria-samples`
(`index.html` / `styles.css` / `app.js` / `widget.html`), reviewed 2026-06-21.

> **One-line:** Re-skin the existing React app to the prototype's **dark glassmorphic
> Apple-style** look — *not* a rebuild. The whole feature set already exists; the
> backend, IPC, and data flow are **unchanged**. Two data-model upgrades the prototype
> implies (structured transcript, first-class action items) are tracked separately as
> **M1/M2** in [TODO.md](./TODO.md) and unblock the Transcript-bubbles and To-dos pieces.

## 1. Design language (port these tokens)
The prototype is a dark, glass theme using Apple system colors. Define as CSS custom
properties in the global stylesheet (replacing the current "Granola cream" palette;
note Settings is already dark-gray, so this also *unifies* the theme):

```
--bg-primary:#09090b  --bg-secondary:#121215  --bg-tertiary:#1a1a1f
--bg-glass:rgba(18,18,21,0.75) + backdrop-filter:blur(20px)
--text-primary:#f4f4f5  --text-secondary:#a1a1aa  --text-muted:#52525b
--accent-blue:#007aff  --accent-purple:#af52de  --accent-green:#34c759
--accent-amber:#ff9500  --accent-red:#ff3b30   --border:rgba(255,255,255,0.08)
--font-sans:Inter        --font-serif:Instrument Serif (already self-hosted from the rebrand)
```
Tag colors map to the 5 accents (blue/purple/orange→amber/green/red) — the existing
`{label,color}` tag model already matches.

## 2. Scope
- **In:** visual reskin + a few layout reorganizations (monthly heatmap, inner-sidebar
  Settings, glass toolbar, +Add-Tag color picker, transcript bubbles, floating widget).
- **Out / unchanged:** all Rust IPC commands, the Python service, SQLite schema (except the
  separate M1/M2 migrations), and the privacy model. No new backend.
- **Keep:** RTL/Arabic rendering (`dir="auto"`), accessibility (focus states, labels),
  the existing health-check (powers the "Local ML Service: Online" status pill).

## 3. Component mapping (prototype → existing React component → change)
| Prototype piece | Component | Change |
|---|---|---|
| Header + centered view-tabs (Meetings/To-dos/Weekly/Ask/Settings) + "ML Service: Online" pill | `AppShell.tsx` | Add the tab nav + status pill (reuse `checkServiceHealth`) |
| Glass record button (pulse dot + wave bars) | `RecordingControls.tsx` | Restyle to the glass pill; keep start/stop wiring |
| New Standalone Note | `NewNoteButton.tsx` | Restyle (secondary glass button) |
| Search | `MeetingsList.tsx` | Restyle input |
| **Monthly calendar heatmap** (‹ June 2026 ›, 7-col grid, click-day filter) | `DateHeatmap.tsx` | Replace current heatmap with a **month grid + prev/next month nav**; "has-meetings" dot; selected-day highlight |
| Tag filter pills ("All" + one per label) | `MeetingsList.tsx` | Restyle; logic already one-per-label |
| Meeting cards (pin/lock icons, title, date•time•dur, snippet, tag badges) | `MeetingCard.tsx` | Restyle to glass card |
| Detail meta row + title + **glass toolbar** (pin/lock/delete) | `NoteViewer.tsx` | Glass toolbar pill; keep IPC |
| **Tags row + "+Add Tag" color-picker popup** (5 dots) | `NoteViewer.tsx` | Add the popup (label input + color dots); `set_meeting_tags` already exists |
| Attendee chips (add/remove) | `NoteViewer.tsx` | Restyle; `update_attendees` exists |
| 4 tabs: Summary / Transcript / Chat / Personal Notes | `NoteViewer.tsx` | Restyle tab bar |
| Summary (markdown + task checkboxes) | `SummaryView.tsx` | Checkboxes read/write **action_items** after **M2** |
| **Transcript bubbles** (me vs them) | transcript tab | Render `transcript_turns` after **M1** (bubble styling) |
| Chat-with-meeting | `MeetingChat.tsx` | Restyle |
| Personal Notes (save-on-blur) | `NoteViewer.tsx` notes tab | Restyle; `update_meeting_notes` exists |
| To-dos (Action Items + All/Today/Overdue/Upcoming, grouped, assignee + due badges) | `TodosView.tsx` | Read **action_items** after **M2**; restyle |
| Weekly recap cards (decisions/actions/topics) | `WeeklyView.tsx` | Restyle |
| Ask (cross-meeting + suggestions + reference links) | `AskAllView.tsx` | Restyle; add suggestion chips + source links |
| Settings **inner-sidebar menu** (Summarizer / Transcription / Auto-Stop / Security) | `Settings.tsx` | Restructure flat settings into a left-menu + section cards; keep the provider dropdown + all fields |
| Transcribing view (live feed + quick-notes pad + wave + Stop&Summarize) | `RecordingNotes.tsx` | Restyle |
| Floating record widget (`widget.html`) | existing floating record/detected card / tray | Granola-style mini timer pill |
| PIN prompt + delete confirm modals | existing in-app modals | Restyle (delete modal already exists) |

## 4. Phased plan
- ✅ **Phase 0 — theme tokens** (`795d2b8`, branch `feat/reskin-phase0`, 2026-06-21). The cream
  theme was implemented by **inverting the Tailwind `gray` ramp** in `tailwind.config.js` (one
  source of truth: components use `bg-gray-950/900/800` for surfaces, `text-gray-100/200/300`
  for text). Phase 0 **flipped that same ramp to the dark-glass values** (gray-950 `#09090b`
  canvas → gray-100 `#f4f4f5` text) → the whole app goes dark with **zero component edits**.
  Added (additive, no current visual impact — for Phases 1-4): Tailwind `accent` (Apple
  blue/purple/green/amber/red), `glass`, `hairline` colors; `font-sans`/`serif` + `backdrop-blur-glass`;
  CSS custom properties in `:root` mirroring the palette; `color-scheme: dark`; glass scrollbars +
  `::selection`. **Inter is NOT CDN-loaded (privacy) → native Apple-stack fallback.** Default
  blue/red/green/amber utilities left untouched (accent buttons already read fine on dark).
  Verified: `tsc` + `vite build` green; compiled CSS confirms the flip (cream `#f7f5ef` gone).
  ⏳ **Awaiting the user's live-smoke of the dark palette before Phase 1** (the de-risk gate).
**Foundation (`6512724`):** Inter self-hosted via `@fontsource-variable/inter` (bundled, no CDN);
the prototype's `styles.css` copied verbatim to `src/prototype.css` and imported (class-scoped →
dormant until used; only `body/header/nav/*` are global). **The reskin method:** rewrite each
component's JSX to the prototype's class names. Execution: **12 parallel agents** (one per component,
presentation-only, wiring preserved) via a Workflow, plus `App.tsx` shell converted by hand. Commits:
**`6512724`** (foundation + header), **`ce6f865`** (all 13 components + App shell), **`6dbccf7`**
(wired NoteViewer toolbar/Add-Tag + RecordingNotes stop, which agents couldn't reach across files).

- ✅ **Phase 1 — shell + sidebar.** Header (gradient serif logo + segmented-pill nav + live ML status
  pill), always-visible `.sidebar` + `.resize-divider` + swapping `.content-area` (To-dos/Weekly/Ask/
  Settings now render WITH the sidebar, per the prototype), glass record button + wave bars, New Note
  `.btn-secondary`, `.search-container`, `.tag-pill` filters, glass `.meeting-card`s, and the
  always-visible **monthly calendar grid + month nav** (`DateHeatmap`).
- ✅ **Phase 2 — detail viewer.** `.glass-toolbar` (pin/lock/delete — wired), `+Add-Tag` color-picker
  popup (wired to `updateMeetingTags`), 4 `.tab-link` tabs, transcript **speaker bubbles** (M1),
  `.summary-markdown` + `.task-item` checkboxes (M2), `.chat-msg` bubbles, notes tab.
- ✅ **Phase 3 — other views + settings.** `.todos-layout`, `.weekly-card`, `.ask-layout` (+ suggestion
  chips), and **Settings `.settings-sidebar-layout`** inner-sidebar (Summarizer/Transcription/Auto-Stop/
  Security/Calendar menu) — all existing fields preserved.
- ✅ **Phase 4 — recording + modals.** `.transcribing-layout` (live feed + quick notes + wave + wired
  Stop), PIN/delete `.modal-box`.
- ✅ **Floating record bubble** (`59b617f`) — Granola-style small always-on-top window (label `recording`, `?widget=recording`) shown while recording when the main window is minimized/blurred; click to return. Driven by `AppState.recording` + a main-window `Focused` handler in Rust.
- ⏳ **Polish remaining (non-blocking):** TodosView shows 2 filter tabs not 4 (Overdue/Upcoming need
  new filter logic); NewNoteButton modal reuses oversized `.notes-textarea` + centered `.modal-input`;
  Settings calendar/cloud-warning sub-cards keep Tailwind (no prototype class); `gray`/`yellow` tag
  colors fall back to un-tinted `.badge-tag`; `backdrop-filter` perf pass on Windows WebView2 not
  yet profiled.

## 5. Risks / notes
- **Theme shift (cream → dark glass).** Check contrast/readability; the rebrand already
  self-hosts Instrument Serif, so the serif accents carry over.
- **`backdrop-filter: blur()` performance** in the webview — fine on macOS WKWebview, can be
  heavier on Windows WebView2; profile and degrade gracefully (solid fallback) if needed.
- **Incremental + low-risk:** backend/IPC unchanged, so each phase ships independently and is
  trivially revertible. Do Phase 0 first behind the existing app to de-risk the palette.
- The prototype is a *mock* (in-memory array, simulated AI); the real app already wires every
  one of these to the backend — so this is styling + a few layout moves, not logic.
