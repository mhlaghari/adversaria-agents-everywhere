# Astra fast pass: full notes (extracted from astra.jsonl)

Two details shape this slice: recording start creates a Copilot session ID but no meeting row, and new workspace tasks are immediately eligible for autopilot. Live commitments need an approval gate and a stored session ID so they can run during capture and link to the meeting afterward.

---

There is no folder-to-workspace binding or `RunView` type in this checkout. I’m fixing routing to one lazily created “Live meeting” workspace and defining a small approval response around the existing `WorkspaceRun`. Queued work currently lives in `workspace_tasks`; a run row is created only when execution starts.

---

The existing Python endpoint already streams drafts, and Rust saves them as workspace artifacts. I’m keeping that path intact. The handoff will require approved live tasks to use Local and preserve the existing artifact review step. I also found a second model call for the run summary; live tasks can use a fixed “Draft ready for review” summary to save demo time.

---

The working tree changed during this review: commitment code has just appeared. I’ll check that addition before finalizing the handoff. Its current approval API uses a session ID and commitment ID, which differs from your requested task-ID contract.

---

Build this as **persisted task → approval → Local autopilot → existing artifact review**. No files changed.

Concurrent edits appeared during this review. At my last read, they catch commitments in memory, create tasks only on approval, route through a folder namesake, and expose `commitment_approve(session_id, id, capability)`. Those choices miss your requested slice. The contract below supersedes them.

**The caption hook belongs immediately after turn assembly.** In [copilot_session.rs](/Users/mhlaghari/Documents/Documents/MyProjects/adversaria-agents-everywhere/src-tauri/src/copilot_session.rs), use `on_caption`, after `assemble_caption` returns a completed turn and `speaker` becomes `Me` or `Them`, beside `detect_turn`, before `push_dialogue_turn`.

- Process completed captions from `commands.rs::feed_live_source`, through `on_me_caption` and `on_them_caption`. Never process `live-partial`.
- Run commitment detection on both channels, independently of `mic_questions` and Copilot mode.
- Keep forced chunks buffered until silence. One completed turn produces at most one commitment.
- Commit task creation before emitting the card. Detector/storage failure must not suppress question handling.
- Deduplicate with a session-wide `HashSet` of `CopilotSession::norm(turn)`, inserted only after successful persistence. Retain the key after dismissal.

**Meeting identity is available only after capture.** [commands.rs](/Users/mhlaghari/Documents/Documents/MyProjects/adversaria-agents-everywhere/src-tauri/src/commands.rs) has no `copilot_start_session` command. `start_recording` calls `copilot_session::start_session`, which persists a UUID in `copilot_sessions`; it does not create a meeting.

`stop_recording` retires that session and returns its UUID. The frontend subsequently calls `enqueue_recording`, which calls `save_pending_meeting`, then `storage::insert_meeting_with_copilot_session`. The actual meeting INSERT is `insert_meeting_on`.

Add nullable `workspace_tasks.source_session_id TEXT`. During capture, set it to the Copilot UUID and leave `source_meeting_id` and `action_item_id` NULL. Never use meeting ID zero.

Backfill inside `storage::attach_copilot_session_in_transaction`, alongside existing card attachment:

```sql
UPDATE workspace_tasks
SET source_meeting_id = ?1
WHERE source_session_id = ?2 AND source_meeting_id IS NULL;
```

This covers enqueue and direct transcription/save paths transactionally, including tasks whose runs already finished. Preserve `source_session_id` permanently as live provenance.

**Routing is fixed: one “Live meeting” workspace.** There is no actual folder-to-workspace binding. `meeting_workspace_bindings` requires an existing meeting; workspace context items of kind `folder` contain filesystem paths.

Replace the newly added namesake heuristic in `commitment_workspace_on`: select the lowest-ID workspace named exactly `Live meeting`, otherwise create it with `create_workspace_on(..., "Live meeting", "blue")`, in the task-creation transaction. Cache its ID for the session. The recording folder supplies context, never routing.

Do not call `set_meeting_binding` during backfill: it also pushes summarized action items and introduces another task-creation path.

**Task creation must begin ineligible.** Today, [storage.rs](/Users/mhlaghari/Documents/Documents/MyProjects/adversaria-agents-everywhere/src-tauri/src/storage.rs) exposes:

```rust
create_workspace_task(
    workspace_id, title, details, capability,
    source_meeting_id, action_item_id
)
```

It delegates to `create_workspace_task_on`, then `create_workspace_task_with_eligibility_on`, with eligibility **true**. The command wrapper also kicks autopilot.

Add a transactional `create_live_commitment_task` wrapper around the eligibility helper, passing **false**, and write `source_session_id` before committing.

Required columns without defaults are `workspace_id`, `title`, `created_at`, `updated_at`. Defaults cover `details`, `capability`, `status='queued'`, `attempt=1`, `rejection_notes='[]'`, and `agent_eligible=1`; explicitly override eligibility.

Use the complete heard commitment as title. Details contain speaker, recipient, spoken deadline, session UUID, capture offset, up to four preceding spoken turns of 600 characters each, and up to 4,000 characters of the already available `standing_pack`. Missing context remains missing. Map `check/review/investigate` to `research`, all other accepted verbs to `write`. Persist manual baseline staffing with no agent or skills, avoiding automatic adapters.

**Use this deliberately narrow detector.** In [copilot.rs](/Users/mhlaghari/Documents/Documents/MyProjects/adversaria-agents-everywhere/src-tauri/src/copilot.rs), the question detector is `is_prompt`, not a regex. Reject a turn containing `?` or satisfying `is_prompt` before matching.

Compile these once. Pattern 0 is mandatory; extract the optional deadline with pattern 1, remove that suffix and trailing punctuation, then extract the optional recipient with pattern 2 from `work`.

```rust
const COMMITMENT_PATTERNS: &[&str] = &[
    r"(?i)^\s*(?:i['’]ll|i will|we['’]ll|we will|let['’]s|we need to)\s+(?P<verb>send|share|email|get|draft|prepare|write|check|review|investigate)\s+(?P<work>[^?\r\n]+?)\s*[.!]?\s*$",
    r"(?i)\b(?:by|before|on)\s+(?P<deadline>(?:(?:next|this)\s+)?(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)|today|tomorrow|eod|end of (?:day|week)|\d{4}-\d{2}-\d{2})\s*[.!]?\s*$",
    r"(?i:\bto)\s+(?P<person>\p{Lu}[\p{L}'’-]*(?:\s+\p{Lu}[\p{L}'’-]*){0,2})\s*$",
];
```

`person` means recipient, not task owner. Record the speaker separately as `Me` or `Them`. Keep deadlines verbatim. Lowercase names can miss metadata extraction without losing the task.

Never detect against `copilot-answer`, `sections.say`, recent generated cards, or pinned notes. A founder actually speaking a suggested commitment is valid microphone input.

| Positive fixture | Recipient | Deadline |
|---|---|---|
| I'll send the numbers to Wael by Monday | Wael | Monday |
| let's get the deck to Naema | Naema | absent |
| we need to check the SIDRA thresholds | absent | absent |
| We'll draft the brief before tomorrow. | absent | tomorrow |
| I will review the report by next Friday. | absent | next Friday |

Negative fixtures:

- `Can you send the numbers to Wael by Monday?`
- `Will you send the deck to Naema`
- `I won't send the numbers`
- `We should check the SIDRA thresholds`
- `SAY: I'll send the numbers to Wael by Monday`

All ten lexical fixtures passed through ripgrep’s Rust regex engine. Audio-origin and question guards still need integration tests.

**Approval queues work immediately and returns without waiting for generation.** No `RunView` exists. Existing `WorkspaceRun` contains `id`, `workspace_id`, `task_id`, `engine`, `status`, `log`, `report`, `error`, `started_at`, and `finished_at`. The concurrent addition introduces `CommitmentResult`, not `RunView`.

Freeze these new signatures and response:

```rust
pub struct RunView {
    pub task: WorkspaceTask,
    pub run: Option<WorkspaceRun>,
    pub agents_paused: bool,
}

#[tauri::command]
pub async fn commitment_approve(
    app: AppHandle, task_id: i64,
) -> Result<RunView, String>;

#[tauri::command]
pub async fn commitment_dismiss(
    app: AppHandle, task_id: i64,
) -> Result<(), String>;

#[tauri::command]
pub async fn commitment_list(
    session_id: String,
) -> Result<Vec<WorkspaceTask>, String>;
```

Register them in `lib.rs`; [tauri.ts](/Users/mhlaghari/Documents/Documents/MyProjects/adversaria-agents-everywhere/src/lib/tauri.ts) sends `{ taskId }` and `{ sessionId }`.

- Approve validates live provenance, atomically changes queued/ineligible to eligible, returns a snapshot, emits `workspace-task-changed`, then kicks autopilot when unpaused. Repeated approval returns current state without rerunning completed work.
- Dismiss deletes only a queued, unapproved live task. An already missing task succeeds; an approved task errors. Serialize approval/dismissal through `autopilot_gate`.
- For live tasks, eligibility is the approval gate. Reject generic eligibility changes; prevent manual Run before approval.
- Existing `approve_workspace_task` approves a finished artifact. Keep that separate.

[autopilot.rs](/Users/mhlaghari/Documents/Documents/MyProjects/adversaria-agents-everywhere/src-tauri/src/autopilot.rs) picks the oldest queued eligible task, one running task per workspace. Force `local` for live tasks in both dispatch and execution, regardless of workspace engine settings.

`agents_paused` is configuration, not a storage column. It prevents new automatic starts; running tasks finish. Recheck it under the execution gate before claiming a live task; a pause race leaves the task queued, without a failed run. Resume already kicks autopilot.

There is no queued run status: `workspace_runs` permits `running/done/failed/stopped`. Therefore `RunView.run` is NULL until `create_workspace_run` claims execution.

**Reuse the companion work that just landed, with one durable contract.** Keep event name `copilot-commitment`, replacing its payload with:

```ts
{ session_id: string; task: WorkspaceTask; agents_paused: boolean }
```

Emit after insertion, plus existing `workspace-task-changed`. Use `CommitmentCard` with props `task`, `run`, `agentsPaused`, `busy`, `error`, `onApprove`, `onDismiss`. Show “Commitment caught”, the quote, Approve and Dismiss. After approval show `Queued`, `Queued · agents paused`, `Running · Local`, or `Draft ready` from actual task/run state. The current `run_queued` boolean cannot justify “run started”.

Mount the card list below the recording bar, outside tab conditionals, so both companion layouts show it immediately. Subscribe before `commitment_list`; refresh on workspace events, guard asynchronous results by session, and clear cards on every session change.

In `WorkspaceDetailView::renderTaskRow`, replace the new `details.startsWith("Caught live")` check with `source_session_id != null`. Label it `live`, tooltip “Caught during recording”. Pending live rows use the same approval actions. Preserve existing run polling, artifact preview, dates, and review controls. `CopilotCards` and `useCopilotLiveContext` need no behavioral change.

Extend `CommitmentCard.test.tsx`, `RecordingCompanion.commitment.test.tsx`, `WorkspaceLiveChip.test.tsx`, `WorkspacesView.test.tsx`, and `WorkspaceDetailView.test.tsx`. Cover session isolation, duplicate clicks, paused approval, dismissal, refresh, and artifact visibility. Extend Rust tests in storage, Copilot session, commands, and autopilot for persistence-before-approval, backfill, forced chunks, and Local-only pickup.

**Python service changes: none.** `/draft_stream` already accepts the brief and instruction; Rust writes `draft.md`, persists artifacts, and moves successful tasks to `awaiting_review`.

In `commands.rs`, append this to `LOCAL_WORKSPACE_INSTRUCTION` **only for live tasks**:

> Produce one Markdown draft of at most 250 words. For sending or sharing work, including getting material to a recipient, use To:, Subject:, then the email body. Otherwise use Findings, Suggested next step, and Open questions. Preserve spoken deadline wording. Use [needed: ...] for missing facts, numbers, or links. Never claim anything was sent or completed. Output plain Markdown without FILE blocks.

For live runs, replace the additional `generate_workspace_run_report` model call with stored report `Draft ready for review.`

**The 90-minute allocation is fixed.** Rust owns persistence, detector, commands, dispatch, and prompt. Frontend owns types, wrappers, cards, marker, and UI tests. Python owns existing service smoke tests, model warming, and timed demo rehearsal. Use Ollama `qwen3.5:4b` for the demo; verify effective endpoint/model selection because `start.sh` downloading it does not select it.

Integrate at minute 55, take one feedback round by 65, fix through 80, rehearse through 90. Acceptance: task visible before approval; paused approval produces no run; resume produces a Local artifact before recording stops; stop backfills the same task.

Cut semantic detection, fuzzy deduplication, date resolution, identity lookup, folder routing, actual sending, deck generation, new engines, stop-time caption flushing, and crash recovery of uncompleted speech. Pause between demo utterances. The application was not built or run during this read-only review.

---

I made no code changes in this session; the working tree changed concurrently during the review. I’ll check the memory files, but this session’s read-only filesystem permissions prevent me from updating them.

---

I couldn’t update [HANDOFF.md](/Users/mhlaghari/Documents/Documents/MyProjects/adversaria-agents-everywhere/HANDOFF.md) or [STATUS.md](/Users/mhlaghari/Documents/Documents/MyProjects/adversaria-agents-everywhere/STATUS.md): this session’s filesystem is read-only. I made no code changes; the hook detected concurrent edits.

The handoff entry should record:

- **Done:** Code-grounded implementation handoff delivered; ten regex fixtures verified.
- **Pending:** Align concurrent implementation with task creation before approval, task-ID commands, session backfill, and Local-only dispatch.
- **Next:** Workers integrate, complete focused tests, then demonstrate an artifact before recording stops.
- **Validation:** No application build or runtime verification performed in this session.