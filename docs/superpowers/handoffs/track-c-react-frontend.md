# Track C Handoff: React Frontend

**Scope:** Tasks 11–14 — App shell with recording state machine, meetings list
with controls, note viewer, settings panel + error banner.

**Dependencies satisfied:** Task 1 complete — TypeScript types in
`src/types.ts`, Tauri invoke wrappers in `src/lib/tauri.ts`, Tailwind + Vite
configured, `App.tsx` placeholder.

**Output:** A React UI in the Tauri webview with full recording flow,
meeting list, note viewing, and settings management.

## Files to create/modify

| File | Purpose |
|------|---------|
| `src/hooks/useRecording.ts` | Recording state machine hook (Task 11) |
| `src/hooks/useMeetings.ts` | Meetings data hook (Task 12) |
| `src/hooks/useConfig.ts` | Config hook (Task 14) |
| `src/components/AppShell.tsx` | Main layout + recording button (Task 11) |
| `src/components/RecordingControls.tsx` | Start/stop + status indicator (Task 11) |
| `src/components/MeetingsList.tsx` | Scrollable meeting list (Task 12) |
| `src/components/NoteViewer.tsx` | Transcript + summary display (Task 13) |
| `src/components/Settings.tsx` | Config form (Task 14) |
| `src/components/ErrorBanner.tsx` | Dismissible error banner (Task 14) |
| `src/App.tsx` | Modify — compose all components |

## Component tree

```
App
├── ErrorBanner (global errors)
├── AppShell
│   ├── RecordingControls (start/stop, status)
│   ├── MeetingsList (sidebar)
│   │   └── MeetingCard (per meeting)
│   └── NoteViewer (main area)
│       ├── Transcript tab
│       └── Summary tab
└── Settings (modal/panel)
```

## Task breakdown

### Task 11: App Shell + Recording State Machine

**`src/hooks/useRecording.ts`:**
- State machine: `idle → recording → stopping → processing → done`
- Exposes: `status`, `startRecording()`, `stopRecording()`, `error`
- Calls `startRecording()` / `stopRecording()` from `src/lib/tauri.ts`
- Listens for Tauri events: `recording-started`, `recording-stopped`

**`src/components/AppShell.tsx`:**
- Main layout: sidebar (meetings) + content area
- Grid/flex layout with Tailwind

**`src/components/RecordingControls.tsx`:**
- Big record button (red when recording, gray when idle)
- Status text: "Ready", "Recording...", "Processing..."
- Disabled states during processing

### Task 12: Meetings List

**`src/hooks/useMeetings.ts`:**
- Fetches meetings via `getMeetings()` from `src/lib/tauri.ts`
- Exposes: `meetings: Meeting[]`, `selectedId: number | null`, `selectMeeting(id)`, `refresh()`

**`src/components/MeetingsList.tsx`:**
- Scrollable list of past meetings
- Each item: title, date, duration, template used
- Click to select → opens in NoteViewer
- Sorted newest-first

### Task 13: Note Viewer

**`src/components/NoteViewer.tsx`:**
- Shows selected meeting's transcript + summary
- Tab switcher: "Transcript" | "Summary"
- Transcript: scrollable pre/code block
- Summary: rendered markdown/sections
- Empty state: "Select a meeting to view notes"

### Task 14: Settings + ErrorBanner

**`src/hooks/useConfig.ts`:**
- Fetches config via `getConfig()`, saves via `updateConfig()`
- Exposes: `config`, `updateConfig(partial)`

**`src/components/Settings.tsx`:**
- Form fields:
  - Python service URL (text)
  - Default prompt template (dropdown: general, one-on-one, client-meeting)
  - Ollama model (text)
  - Claude API key (password, optional)
- Save button → calls `updateConfig`

**`src/components/ErrorBanner.tsx`:**
- Red banner at top of app
- Shows error message + dismiss button
- Props: `message: string | null`, `onDismiss: () => void`

## State management

No external state library needed for Phase 1. Custom hooks + React context
for global state (errors, selected meeting, recording status).

## Styling

Tailwind CSS dark theme (gray-950 background, gray-100 text).
Follow the existing `src/index.css` base.

## Execution order

Tasks 11, 12, 13, 14 are **independent** — can run in any order.
Update `src/App.tsx` as the last step to compose all components.
Commit after each task.

## TypeScript types (from Task 1)

All types are in `src/types.ts`:
```typescript
Meeting, AppConfig, TranscribeResponse, SummarizeResponse,
TemplateInfo, HealthResponse, PromptTemplate
```

Tauri invoke wrappers in `src/lib/tauri.ts`:
```typescript
startRecording, stopRecording, transcribeAndSummarize,
getMeetings, getMeeting, getConfig, updateConfig, checkServiceHealth
```
