# Astra, fast pass (20 minutes): the minimal "commitments become live workspace tasks" slice, checked against this code

Read-only. No file changes. Output Markdown, at most 2,000 words, no em dashes. This is a hackathon build with a hard stop: three workers (Rust, frontend, Python) start in 25 minutes and must finish in 90. Every design decision must be settled by you or me; workers get none.

Repo: this directory (a fork of Adversaria with Workspaces and the Live Copilot). Read `HACKATHON.md`, then the code: `src-tauri/src/workspace_runs.rs` (runs, engines, artifacts), `src-tauri/src/storage.rs` (grep `workspace_tasks`, `workspace_runs`, `meeting_workspace_bindings`, `agents_paused` or the pause flag), `src-tauri/src/commands.rs` (workspace commands, `copilot_start_session`, recording start and stop, where the meeting row is created), `src-tauri/src/copilot_session.rs` (`on_caption`, `detect_turn`, the events it emits), `src-tauri/src/copilot.rs` (`extract_keywords`, question regex), `src/components/WorkspacesView.tsx`, `src/components/RecordingCompanion.tsx`, `src/components/CopilotCards.tsx`, `src/hooks/useCopilotLiveContext.ts`, `src/lib/tauri.ts`, `src/types.ts`.

## The slice (what the demo must show, three minutes)

During a recording, when a participant says a commitment ("I'll send the numbers to Wael by Monday", "let's get the deck to Naema", "we need to check the SIDRA thresholds"), the app creates a workspace task on the spot, shows a "Commitment caught" card in the recording companion with Approve and Dismiss, and on Approve queues an agent run on the Local engine so an artifact (a draft or a brief) exists before the recording stops. The Workspaces tab shows the task with a "live" marker and the run result as today.

## What I need from you

1. **Hook points, exact.** Where in `copilot_session.rs::on_caption` (or wherever captions arrive) a commitment detector runs beside the question detector; whether the current recording has a meeting id during capture (if not, what to store on the task now and how to backfill the meeting id at stop; name the function that creates the meeting row); which workspace the task goes to (the folder's bound workspace? a default "Live meeting" workspace created on first use? give the rule); how a task is inserted today (function names and required columns in `workspace_tasks`); how a run is queued and what the pause flag does to it; the event the companion should listen to.
2. **Detector.** A regex set for commitments with a person and a deadline as optional captures, tuned to avoid questions and the copilot's own SAY text (the Me channel is the founder). Give the patterns as a Rust `&[&str]` list and five positive and five negative fixtures.
3. **Approval and run.** The exact command signatures to add: `commitment_approve(task_id) -> Result<RunView, String>` (queues a run; if agents are paused, queue only and say so), `commitment_dismiss(task_id)`. What `RunView` already exists.
4. **Frontend.** The minimal companion card (component, props, event) and the Workspaces "live" marker; which existing test files to extend.
5. **Python.** Say explicitly whether the Python service needs any change for this slice (I believe none). If a "draft email" artifact format needs a prompt tweak in the run engine, give the exact prompt addition and file.
6. **Cut list.** What to leave out so this fits in 90 minutes per worker with one feedback round.
