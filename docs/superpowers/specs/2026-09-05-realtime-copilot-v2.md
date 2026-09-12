# Realtime Copilot v2: session-bound answers while recording (2026-09-06, rev 5)

Authors: GPT-6-Astra (host) and Claude Fable (coauthor/reviewer). Status: **rev 5 is implemented on `feat/live-copilot-c` (uncommitted)**. It includes Fable's final review, the host's final audit fixes, DeepSeek support, the conversation-window correction and the approved flat answer-feed UI. Rev 0 (brief reconciliation), rev 1 (contract), rev 2 (initial as-built audit), rev 3 (Claude/Local as-built state), and rev 4 (DeepSeek plus caption-line behavior) are superseded. Supersedes the behaviour sections of [2026-09-02-live-copilot-design.md](./2026-09-02-live-copilot-design.md); its Interview Assist shell, keyboard shortcuts, screen-share exclusion and "questions to ask" brief remain out of scope. Decision record: ADR-020 in [docs/DECISIONS.md](../../DECISIONS.md). Installed `/Applications/Adversaria.app` is 0.3.83 from the 18:35 GST build and does **not** contain rev 5; use the current debug bundle for review.

Labels: **Verified** = read in code or re-run by Fable or the host on 2026-09-05/06; **Observed** = taken from a saved log or JSON; **Pending** = not proven by anyone yet. Nothing in this document claims a native DeepSeek or Anthropic request was exercised.

## Rev 5 amendment: answer the conversation, not a transcript line (Implemented)

Founder correction, 2026-09-06: a live caption line is an audio-processing chunk, not a meaningful question boundary. A long sentence can be split by the eight-second forced cut, and a short final caption can depend on everything said before it. Therefore no automatic or manual Copilot path defines its task as “answer the last line.” This amendment replaces the capture semantics in §2.2 and the matching UX copy in §4.

### Conversation envelope

For every confirmed caption, retain `{source: me|them, text, started_at_ms, ended_at_ms, boundary: silence|forced}`. The sidecar must expose whether a caption ended at real trailing silence or at the live pipeline's forced-length cut. Consecutive `forced` chunks from the same source are joined into one speech turn; they are never independently treated as questions. A speech turn ends at a real silence boundary or when the other side begins speaking.

The answer request freezes one bounded **conversation envelope**:

| Part | Selection rule | Bound |
|------|----------------|-------|
| Current turn | The complete latest *Them* speech turn. Keep the prompt sentence and its same-turn lead-in together; never select only the final caption chunk. | 2,000 characters, truncated at word boundaries around the prompt sentence |
| Recent dialogue | The immediately preceding *Me* and *Them* turns needed to resolve follow-ups such as “that”, “it”, “those risks”, and “given what you said”. Preserve chronological order. | Up to four turns, 600 characters each, and 2,400 characters total |
| Knowledge | Retrieved notes, folder instructions and provider rules already defined by rev 4. | Existing bounds |

The same semantic envelope is used for Local, Claude and DeepSeek so answers do not change meaning when the provider changes. Local keeps the entire envelope on the Mac. Claude and DeepSeek may receive only the frozen bounded envelope described above, never the full transcript or audio; the consent line and receipt must use that wording.

### Detection and manual action

- Automatic detection runs on the assembled *Them* speech turn after a real turn boundary. Forced audio cuts may pre-start retrieval, but cannot create or display a card by themselves.
- The prompt anchor is the last real question/request sentence in the assembled turn. The request still includes the same-turn lead-in so “And what are its vulnerabilities?” is answered in the context of the system just described.
- A newer continuation of the same turn updates the pending intent before dispatch. It does not create a second card. Once an answer is streaming, a materially extended question follows the existing latest-intent cancellation and replacement rule.
- The manual control is **Answer current question**. It freezes the latest complete *Them* turn plus recent dialogue. The solo-test option changes the source to the latest complete *Me* turn; it does not reduce the request to one caption line.
- Dedup compares the normalized assembled prompt, not individual caption chunks.

### Reviewable UX

The card displays a concise question span while answering from the full envelope. A collapsed **Context · N turns** disclosure shows the exact dialogue sent to the answer engine, with *Me* and *Them* labels; **Sources · N** remains a separate disclosure for retrieved knowledge. This keeps the feed calm while making context selection inspectable. The review artifact is [`.recon/copilot-feed-concepts-20260906/index.html`](../../../.recon/copilot-feed-concepts-20260906/index.html).

Acceptance scenarios covered by the rev 5 automated contract and component tests:

1. A 20-second question split by two forced cuts produces one card whose request contains the entire question.
2. “We may connect the local model for research.” followed by “What risks does that create?” resolves “that” from the preceding turn.
3. A *Me* clarification between two *Them* turns is present in the frozen envelope and changes the answer appropriately.
4. Manual **Answer current question** uses the assembled turn; solo test uses the assembled *Me* turn.
5. Opening **Context** shows exactly the bounded text used by Local or sent to the selected cloud provider.
6. No card is emitted for a forced chunk that contains only the first half of a question.

## Rev 4 addendum: DeepSeek Copilot (Verified unless marked)

DeepSeek is a fourth effective mode beside `no_ai`, `local`, and `claude`. It follows the same session, latest-intent queue, cancellation, retrieval, terminal, persistence and provenance contracts below. The differences are provider-specific and intentionally narrow:

| Contract | DeepSeek behavior |
|----------|-------------------|
| Credential | Separate OS-keychain account and Tauri commands; the consent control is disabled until a DeepSeek key exists |
| Endpoint/model | Fixed `https://api.deepseek.com` and `deepseek-v4-pro`; no user-configurable override |
| Payload | Complete current question turn ≤ 2000 chars, up to four recent Me/Them turns ≤ 600 chars each, up to three retrieved passages, folder instructions ≤ 400 chars; never the full transcript |
| Provider features | Chat Completions streaming with thinking disabled; Copilot web search is always false |
| Network boundary | Rust and Python allow HTTPS host `api.deepseek.com`, no userinfo/port/query/fragment, and only empty/root/`/v1` paths; rejection happens before provider I/O |
| Completion | Requires `finish_reason: stop`, upstream `[DONE]`, final usage and nonblank text; length, early EOF, auth, rate-limit, timeout and provider failures terminate as errors |
| Accounting | Provider is `deepseek`; request bytes are counted after credential fields are removed; receipts add `deepseek_questions`; provenance model chips render `DeepSeek` |
| Retry | Same frozen-provider rule as Claude/Local. The current mode must still be DeepSeek; completed retrieval may be reused; the key/model/endpoint frozen on the new job remain provider-locked |

Automated state after rev 5 plus the manual retry correction: frontend **41 files / 383 tests**, Rust **420 passed / 1 ignored**, Python **652 passed / 1 skipped**. TypeScript, production bundle/security, Rust fmt/clippy and changed-file Ruff lint/format pass. A credentialed DeepSeek acceptance response is still not recorded as verified evidence; the provider contract is covered by mocked upstream tests.

Sources read for rev 2 and reconciled in rev 3: `src-tauri/src/copilot_session.rs`, `copilot.rs`, `copilot_provenance.rs`, `commands.rs`, `storage.rs`, `http_client.rs`, `types.rs`, `python-service/src/{copilot_answer.py,models.py,server.py,summarizer.py}`, `src/{App.tsx,lib/copilotAnswer.ts,lib/tauri.ts,types.ts,hooks/useRecording.ts,hooks/useCopilotLiveContext.ts,components/{CopilotAnswerStrip,CopilotCards,CopilotConsentBar,RecordingCompanion,NoteViewer,FolderView}.tsx}`, `scripts/copilot-e2e/{replay.py,README.md}`, `python-service/tests/fixtures/copilot/manifest.json`, and under `.recon/realtime-copilot-20260905/`: `audit-frontend.md`, `audit-python.md`, `gemini-harness-review2-result.json`, `e1a-dry-run-host-final.json`, `e1a-results-host-final.json`, `native-runbook.md`, `final-{frontend,rust,python}-host.log`, the review logs, and worker result JSON files.

## 1. Defects found at spec time and where they stand (Verified)

| # | Defect (rev 0/1 wording) | Status now |
|---|--------------------------|------------|
| D1 | Manual card never got an answer | Fixed: `copilot_ask_last` enqueues through the same queue (`copilot_session::ask_last`); `copilot_force_card` kept as an alias |
| D2 | No session identity; delayed deltas mutated the next recording | Fixed: UUIDv4 `session_id` on every event and row; frontend drops other sessions |
| D3 | Stop cancelled nothing; Python never saw disconnects | Fixed: retire on stop/new start; per-card and session tokens; `StreamControl` closers in Python |
| D4 | FIFO(4), 8 s blackout, silent drops | Fixed: one active + one waiting, `skipped {superseded}` is visible and persisted |
| D5 | Mode resolved at execution, switch cancelled nothing | Fixed: `provider_frozen` at capture; `copilot_set_mode` cancels active and waiting |
| D6 | EOF or truncated Local output became `done` | Fixed: authoritative `[DONE]` only after usage; Local `max_tokens`/`num_predict` 200 |
| D7 | Three-word overlap promoted fabricated claims to *your notes* | Fixed: five-token rule with citation membership; "Not in your notes" enforced in Rust |
| D8 | Unicode slice panic; bounds only in Python; blank/contradictory fields accepted | Fixed: char-based excerpt; bounds in Rust at capture; Pydantic validators reject blank and provider-incompatible fields |
| D9 | Process-local epoch persistence, orphans, `egress_chars`, web hard-coded true | Fixed: `copilot_sessions`, session attach, `egress_bytes`, web = folder opt-in and Claude only |
| D10 | `provider="local"` did not enforce local egress | Fixed: registered loopback set in Rust and Python; `trust_env=False`, `follow_redirects=False` |
| D11 | Web accounting from the start frame | Fixed: `web_performed` from the final usage frame; `web_requested` = dispatched with `web_search=true` |
| D12 | Local output unbounded, zero usage | Fixed: 200-token cap; real token counts when the backend reports them |
| D13 | Transcript-first hid Copilot; pin dropped the answer; errors console-only | Fixed: answer strip and slide-over sheet; labelled pin; failures revert and show a notice |

## 2. Implemented contract (Verified unless marked)

### 2.1 Session

`start_recording(copilot_folder_id)` creates the session before capture starts (`copilot_session::start_session`): it retires any previous session, snapshots the folder (`copilot_mode`, `instructions` truncated to 400 chars as persona, `copilot_web`), inserts a `copilot_sessions` row, installs the in-memory `CopilotSession`, and spawns exactly one consumer task. If capture or asset registration then fails, the session is retired again. The command returns `{copilot_session_id}`.

| Field | Meaning |
|-------|---------|
| `session_id` | UUIDv4, durable, unique across restarts |
| `internal_epoch` | the caption loop's `LIVE_CAPTION_EPOCH`; captions from another epoch are ignored |
| `folder_id`, `mode_at_start`, `folder_persona`, `folder_web` | frozen at start; `folder_web` is the only one updatable during the session (§2.6) |
| `token`, `notify` | session `CancellationToken` (parent of card tokens) and consumer wake-up |
| `active`, `waiting` | the one running card and the one pending job |
| `answered_norms` | last three `done` questions, for dedup |
| `terminal_jobs` | frozen snapshots of `error`/`cancelled` cards, for retry |

`stop_recording()` retires the session **before** stopping capture and returns `{system_path, mic_path, warning, copilot_session_id}`. `enqueue_recording(..., copilot_session_id)` rejects a blank id and attaches inside the meeting insert transaction (§2.8). Frontend: `useRecording` keeps `copilotSessionId`; `App.tsx` drops any `copilot-card`/`copilot-answer` whose `session_id` differs; `useCopilotLiveContext(sessionId)` pushes typed notes and attachments with a 1 s debounce and Rust overwrites `folder_id` with the session's folder.

### 2.2 Capture: what freezes when a question is heard

The sidecar returns each confirmed caption with a parallel `caption_boundaries` value. `forced` means the eight-second latency cap split continuous speech; `silence` means VAD observed a real trailing-silence boundary. Rust maintains separate pending chunk buffers for *Me* and *Them*. A `forced` chunk stays buffered and cannot create a card. The next `silence` chunk from that source completes one joined speech turn, truncated at a word boundary to 2,000 characters.

`on_them_caption` runs `copilot::is_prompt` only on that completed *Them* turn. `prepare_job` freezes: the assembled `question`, `question_source`, `context_turns` (up to four immediately preceding chronological Me/Them turns, each label plus text ≤ 600 chars, current question excluded), `provider_frozen` (`mode_override` else `mode_at_start`), `persona`, `web_search = folder_web && provider == "claude"`, and for Local the engine config (model, base URL, managed key) validated against the registered loopback set. A failed validation is stored on the job and surfaces at activation as `error {validation}`. The same bounded envelope goes to Local, Claude or DeepSeek; only cloud modes send it off the Mac.

Automatic detection compares the normalised assembled question with active work, waiting work and the last three answered questions, and silently drops a duplicate. Manual Ask compares only with active and waiting work: a duplicate click while the same question is live returns `Err("Question is already in progress")`, while an explicit re-ask after completion or a provider switch creates a new provider-frozen card. `persist_and_queue` then INSERTs the `heard` row **synchronously on the caption path under the copilot mutex** (accepted for this release, see §8), places the job in the waiting slot (a displaced job is persisted and emitted as `skipped {superseded}` first), emits `copilot-card {status:"heard"}` with the frozen context and empty passages, and wakes the consumer. **Answer current question** uses the latest complete Them turn; **Use mic speech for solo testing** uses the latest complete Me turn and returns `Err("No mic speech heard yet")` when absent.

### 2.3 Activation: retrieval, answering, outcome

The consumer activates the waiting job (child token from the session token) and runs `run_job`: retrieval (`copilot::retrieve_passages`, 2.5 s budget, same tiers as before) under a select against card and session tokens, skipped when `reuse_passages` (retry); passages sanitised to ≤ 3, text ≤ 600, title ≤ 200, source basename for non-meeting kinds, ≤ 300. `no_ai` cards terminate `done` here and emit `copilot-card {status:"done"}` with passages. Otherwise `copilot-card {status:"answering"}` is emitted with passages and `retrieval_ms`, and the request is built: Claude uses its keychain key, `claude-opus-5`, and the frozen web flag; DeepSeek uses its separate keychain key, fixed `deepseek-v4-pro` + `https://api.deepseek.com`, and web false; Local uses the frozen loopback config and web false. `egress_bytes` is the byte length of the sidecar request body after `api_key` and `llm_api_key` are removed for cloud providers, or 0 for Local. Dispatch is marked (`dispatched=1` in SQLite and memory) **inside the request future immediately before `send()`**, under a cancellation-first `biased` select and a 20 s `ANSWER_TIMEOUT`. Frames become `copilot-answer` `delta`/`citation`/`searching` only while the card is active and not terminal; `usage` sets `web_performed`; an `error` frame is recorded. Outcome: timeout → `error {timeout}` "Answer timed out after 20 s"; transport/provider failure → `error {classified reason}`; frame error → `error`; stream ended without usage → `error {ended_early}`; else `done`.

### 2.4 Cancellation and terminals

| Trigger | Active card | Waiting job |
|---------|-------------|-------------|
| `copilot_cancel(card_id)` | `cancelled {user}` | `skipped {cancelled}`; any other id → `Err("Card is not in progress")` |
| `copilot_set_mode` to a different mode | `cancelled {mode_changed}` | `skipped {cancelled}`; override stored; returns the mode |
| Stop, new recording, failed start | `cancelled {session_ended}` | `skipped {session_ended}`; session token cancelled; consumer exits |

Terminal write (`finish_terminal`): an atomic `TerminalGuard` admits one writer; provenance is labelled for `done` non-`no_ai`; one UPDATE `... WHERE id = ? AND status = 'heard'` also fills `meeting_id` from `copilot_sessions`. **Persist happens before emit.** On SQLite failure the guard is released and the write is retried after 50 ms × attempt, three attempts in total. **After the third failure there is no recovery: the row stays `heard`, no terminal event is emitted, and the card stays in its last non-terminal state in the UI.** On success the event is `copilot-card` (`skipped`, and `done` for `no_ai`) or `copilot-answer` (`done`/`cancelled`/`error`) carrying provenance, `egress_bytes`, `web_requested`, `web_performed`, `reason`, `error`. Dropping the reqwest body closes the socket; the Python route polls `request.is_disconnected()` every 50 ms and closes the registered upstream through `StreamControl` (§2.6).

### 2.5 Retry

`copilot_retry(card_id)` accepts a card whose snapshot in `terminal_jobs` is `error`, or `cancelled` with a reason. Before creating work it requires the current effective mode to equal `provider_frozen`; a Claude card that originally requested web also requires web consent still enabled. It then creates a **new** card (new id, `retry_of`, `trigger:"manual"`, new guard) from the frozen snapshot, including provider, web choice, persona and Local config. Passages are reused only when the original retrieval completed (`retrieval_ms` is present); a card cancelled during retrieval retrieves again. The command returns `{session_id, card_id}`, and lifecycle arrives by events. The UI offers Retry only while the same provider and any required web consent remain selected.

### 2.6 Local-only boundary and disconnects

Rust `validate_local_endpoint` (at capture): `http`, host `127.0.0.1|localhost|::1`, no userinfo, path `""|/|/v1`, no query or fragment, **and** membership in the registered set {`http://127.0.0.1:11434`, `http://127.0.0.1:11434/v1`, the managed Ollama host, the managed Rapid-MLX base}; a key is allowed only for the Rapid-MLX base. Python: `/setup/llm_host` registers `ollama_host` and `local_openai_base_url` (loopback shapes only); `/copilot_answer_stream` calls `validate_copilot_local_endpoint` and returns 400 before any I/O; `CopilotAnswerRequest` also rejects `local` with `api_key`/`web_search`, a key without a base, non-loopback bases, and `claude` with Local fields. Upstream clients are request-local: `httpx.Client(trust_env=False, follow_redirects=False)`, `ollama.Client(..., trust_env=False, follow_redirects=False)`, `anthropic.Anthropic(timeout=18, max_retries=0)`; each registers its `close` with the request's `StreamControl`, which closes idempotently from another thread and closes a late registration immediately. `set_folder_copilot_web(copilot_session_id, folder_id, enabled)` validates the exact current session and its folder, persists `folders.copilot_web` first, then updates `session.folder_web` for **future** captures only; the folder selector is disabled while a session is active.

### 2.7 Stream termination

Python emits `data: [DONE]` only after an authoritative stop **and** a `usage` frame: Claude `stop_reason ∈ {end_turn, stop_sequence}` (`max_tokens` → "Answer cut off at token limit"; other → "Anthropic ended the answer before completion."; HTTP 400/404 → "Anthropic model or tool configuration is unavailable."); DeepSeek and Local OpenAI-compatible streams require `finish_reason:"stop"`, upstream `[DONE]`, and `stream_options.include_usage` (`length` → error; EOF/malformed JSON → provider-specific early-end error; 18 s deadline → timeout); Local Ollama requires `done:true` with `done_reason:"stop"` and `eval_count`s. Empty answers are errors. Rust `CopilotDecoder`: split UTF-8 buffered, invalid UTF-8 and unknown frame shapes are malformed, unknown well-formed keys ignored, `[DONE]` without a preceding usage frame is malformed, EOF without `[DONE]` is an error, and the body has its own 20 s timeout.

### 2.8 Persistence and accounting

`copilot_cards` now carries `session_id`, `status` (`heard|done|skipped|cancelled|error`), `reason`, `trigger`, `provider_frozen`, `retry_of`, `dispatched`, `error`, `egress_bytes`, `web_requested`, `web_performed`, `finished_at` (legacy `epoch`, `egress_chars`, `web_used`, `cancelled` columns remain; migration is idempotent). `copilot_sessions(session_id PK, meeting_id, folder_id, mode_at_start, started_at)`. Writes per card: one INSERT at `heard`, one UPDATE at dispatch (dispatched cards only), one guarded terminal UPDATE. `insert_meeting_with_copilot_session` attaches in one transaction with a compare-and-set on the session mapping and rejects a session whose cards belong to another meeting; a terminal written after attach resolves `meeting_id` by subquery. Receipt (`copilot_receipt_v2`): `questions` and `passages` from `done|error` rows with provider ≠ `no_ai`; `claude_questions`/`deepseek_questions`/`local_questions` from `dispatched=1`; `web_requested` = rows dispatched with `web_search=true`; `web_performed` = sum of usage counts. The note shows "Copilot sent N questions and M passages … · K web searches" with K = `web_performed`, plus the providers used. The v1 epoch-based helpers (`insert_copilot_card`, `finish_copilot_card`, `attach_copilot_cards_to_meeting`, `copilot_receipt`) remain in `storage.rs` but are no longer called from commands.

### 2.9 Provenance

`copilot_provenance::label_bullets(answer_md, passages, citations, web_performed, personal_question)`: `notes` when the bullet shares ≥ 5 consecutive normalised tokens with a passage (a Claude citation is used only if its index is valid, its `cited_text` occurs verbatim in that passage, and the bullet shares the run with both); `web` only when `web_performed > 0`, the citation has an `http(s)` URL, and the run test passes; otherwise `model`. At most three bullets, **each truncated to 12 words**; prose-only output becomes one bullet from its first sentence (≤ 160 chars); `answer_md` is persisted verbatim. `personal_question` is `(?i)\b(you|your|yourself)\b` on the question; with no passages the first bullet is forced to start with "Not in your notes".

## 3. Cross-layer schema (as implemented)

| Event | Payload |
|-------|---------|
| `/live_feed` response | `{captions, caption_boundaries: (silence\|forced)[], partial}`; boundary indexes match surviving captions |
| `copilot-card` | `{id, session_id, status: heard\|answering\|done\|skipped, provider_frozen, reason?, retry_of?, question, question_source: Me\|Them, context_turns, asked_at_ms, trigger: auto\|manual, passages, retrieval_ms?}` |
| `copilot-answer` | `{card_id, session_id, provider, kind: delta\|citation\|searching\|done\|error\|cancelled, text?, citation?, provenance?, egress_bytes?, web_requested?, web_performed?, error?, reason?}` |

`copilot-headline` is **not implemented**; the expressive recording bubble carries no Copilot content (deferred).

| Command | Signature |
|---------|-----------|
| `start_recording(copilot_folder_id?)` | `-> {copilot_session_id}` |
| `stop_recording()` | `-> {system_path, mic_path, warning?, copilot_session_id}` |
| `enqueue_recording(audio_path, template, user_notes?, copilot_session_id)` | blank id rejected |
| `copilot_set_live_context(session_id, context)` | rejects a retired or other session |
| `copilot_set_mode(mode)` | `-> mode`; cancels per §2.4 |
| `copilot_get_mode()` | effective mode of the current session, else `no_ai` |
| `copilot_ask_last(use_me_fallback)` / `copilot_force_card()` | `-> {session_id, card_id}`; acts on the latest complete speech turn |
| `copilot_cancel(card_id)` | `-> ()` |
| `copilot_retry(card_id)` | `-> {session_id, card_id}` |
| `set_folder_copilot_web(copilot_session_id, folder_id, enabled)` | session and folder must match |
| `set/clear/has_deepseek_copilot_api_key` | separate OS-keychain credential lifecycle |
| `get_copilot_receipt(meeting_id)` | `-> {questions, passages, claude_questions, deepseek_questions, local_questions, web_requested, web_performed}` |

Python: `POST /copilot_answer_stream` (`CopilotAnswerRequest`, frames `{"t"}`, `{"c"}`, `{"w"}`, `{"usage"}`, `{"error"}`, then `data: [DONE]` on success only); `POST /setup/llm_host` (`ollama_host?`, `local_openai_base_url?`).

## 4. Companion UX (Verified in code; native rendering Pending)

- **Answer strip** (`CopilotAnswerStrip`): shows only the newest card (question ≤ 80 chars, state text, "Open"); hidden when there are no cards or the Copilot tab is active. Balanced: above the tabs; Open selects the Copilot tab and focuses the card. Transcript-first: under the transcript header; Open raises a `role="dialog"` slide-over sheet (`companion-copilot-sheet`, Close button, Esc) that leaves the transcript mounted.
- **Answer feed**: one flat transcript-style stream with hairline separators and a blue active marker. New rows enter at the top and stream answer text in place. Rows show the concise current question, a frozen-provider chip, lifecycle state (including "Heard the complete question" and "Done · No AI · passages only"), answer, low-chrome Pin action, latency and egress. Retrieved material is collapsed under **Sources · N**. The exact frozen Me/Them envelope is collapsed under **Context · N turns**. There are no nested answer-card surfaces.
- **Manual and consent controls**: the action is **Answer current question**; **Use mic speech for solo testing** switches the source to the latest complete Me turn. No AI and Local say the conversation stays on this Mac. Claude and DeepSeek disclose the complete current question, up to four recent conversation turns, up to three passages and folder instructions; Claude additionally shows web search when opted in, while DeepSeek says no web search. Cancel and consent-matched Retry behavior is unchanged. Retried answers appear as new feed rows.
- **Pin** writes "Copilot: " + question, up to three bullets with `[your notes]`, `[Local]`, `[Claude]`, `[DeepSeek]`, `[web · domain]`, and passage titles; a first-person model bullet is not pinned (tested).
- **Consent**: the bar disables Claude or DeepSeek independently when that provider's key is absent and points to Settings › Live Copilot; a failed mode change reverts and shows the notice; the folder default lives in `FolderView`; the web checkbox on the Last time panel is disabled without a folder and a current session and reverts on failure; the folder select is disabled during a session with a title explaining why. Ask/Cancel/Retry failures surface in the notice slot.

## 5. Verification evidence

### 5.1 Automated suites

| Layer | Result | How verified |
|-------|--------|--------------|
| Python | **652 passed, 1 skipped**; changed-file Ruff lint/format clean | Host re-run after caption-boundary and four-turn request changes |
| Rust | **420 passed, 0 failed, 1 ignored**; fmt and clippy clean | Host re-run after complete-turn assembly, Me/Them context and manual-repeat dedup changes |
| Frontend | **41 files, 383 tests**; `tsc --noEmit`, `vite build`, bundle 486.68 kB / 500 kB, security check clean | Host re-run after the approved answer-feed, disclosure and provider-chip changes |

Worker-boundary numbers before the host's harness fixes were Python 639 / 1 skipped (Gemini report, 19 replay tests). The host then disabled proxy inheritance and redirects, corrected evidence redaction, wrote readiness state atomically, joined the feed worker, enforced answer shape and usage, pinned a registered Local default, paced request starts including the VAD flush, and made any foreground or warmup feed error fail the run. The focused replay suite is now **25 passed** and the full Python suite is 645 passed / 1 skipped.

### 5.2 Test inventory against the rev 1 scenarios (Verified by name and location)

| Scenario | Automated coverage | Level |
|----------|--------------------|-------|
| T1 session isolation | `copilotAnswer.test.ts` "delayed session A delta cannot affect session B card 1"; Rust `stale_epoch_cannot_mutate_session_history`; listener gating in `App.tsx` | unit |
| T2 stop mid-stream | Rust `cancel_before_request_poll_does_not_begin_dispatch`, `retrieval_wait_returns_immediately_when_card_is_cancelled`, `compare_and_take_never_retires_a_replacement_session` | unit, state-level; **no consumer-level test against a mock SSE server** |
| T3 mode switch cancels | `RecordingCompanion.modeFailure.test.tsx` (UI revert); Rust keeps the cancel reason (`cancellation_reason_is_retained_with_the_retry_snapshot`) but **no test drives `set_mode` against an active card** | partial |
| T4/T5 latest-intent and dedup | `one_waiting_slot_supersedes_without_touching_active`, `dedup_checks_active_waiting_and_three_answered`, `manual_ask_can_repeat_a_completed_question_but_not_active_work` | unit |
| T6 manual Ask and Retry | Me-fallback checkbox and notice path in Vitest; Rust retry consent/retrieval tests; component test gates Retry on provider and web consent; Rust error strings in `ask_last` (no dedicated Ask test) | partial |
| T7 reader terminals | `copilot_decoder_*` (split UTF-8, non-authoritative terminals, invalid UTF-8), `copilot_reader_has_an_independent_body_timeout` | unit |
| T8/T9/T20 provenance and format | seven `copilot_provenance` tests incl. Unicode excerpt, five-token rule, invalid citations, personal prefix, prose fallback, 3×12 bound | unit |
| T10 injection | `test_prompt_marks_passages_untrusted_and_keeps_source`; `skipped_frozen_web_job_is_not_counted_as_requested` | prompt-level only |
| T11 Unicode | `unicode_excerpt_never_slices_a_multibyte_character` | unit |
| T12/T13 attach race, restart | `copilot_meeting_insert_attaches_heard_and_late_finish_without_rebinding`, `copilot_v2_attach_before_and_after_heard_are_session_safe`, `copilot_attachment_rejects_a_session_with_conflicting_card_ownership`, `sessions_use_unique_durable_ids`, `copilot_v2_partial_migration_is_independently_idempotent` | unit on in-memory DB |
| T14/T15 transcript-first, mode failure | `RecordingCompanion.review2.test.tsx` (strip, sheet, Esc, transcript mounted), `RecordingCompanion.modeFailure.test.tsx`, `RecordingCompanion.folderWeb.test.tsx` | component |
| T16 local egress table | `static_loopback_endpoint_validation_rejects_path_and_userinfo_tricks`, `invalid_local_endpoint_is_not_frozen_at_capture`; Python `test_registered_local_endpoint_table_and_credentials`, `test_unregistered_local_route_rejects_before_stream_or_socket`, `test_provider_incompatible_inputs_are_safe_400_before_socket` | unit + route |
| T17 Local terminal matrix | `test_local_openai_terminal_matrix_and_request_shape`, `test_local_ollama_terminal_matrix_usage_and_bound`, `test_local_openai_exception_after_delta_preserves_partial_and_errors`, `test_copilot_thinking_and_whitespace_never_become_success` | route with faked upstream |
| T18 offline disconnect control ≤ 500 ms | `test_disconnect_closes_real_generator_upstream_within_500ms`, `test_disconnect_wrapper_closes_cooperative_iterator_promptly`, `test_stream_control_close_is_idempotent_and_late_registration_closes`; actual live SDK/socket timing is unmeasured | route |
| T19 web accounting | `test_claude_web_accounting_comes_only_from_final_usage`, `test_claude_started_but_failed_has_no_usage_or_done`; Rust `copilot_v2_receipt_separates_dispatch_and_web_counts` | unit |
| T21 provider pin | `test_retired_claude_shape_gets_stable_configuration_error`, `test_claude_documented_success_stop_reasons_finish` | offline SDK shape |
| T22 validation | `test_blank_oversized_and_invalid_local_shapes_are_safe_400_before_socket`, `test_validation_trims_text_and_enforces_blank_and_unicode_bounds` | route |
| T23 DeepSeek provider boundary | Rust `deepseek_request_uses_fixed_provider_contract_and_hides_credentials_from_receipt_bytes`, `deepseek_endpoint_cannot_be_overridden`, key-cache and receipt tests; Python DeepSeek endpoint/model validation, bounded stream/usage, auth and early-EOF tests; frontend consent/settings/label/receipt tests | unit + route + component |
| T24 complete-turn conversation envelope | Python `test_completed_utterance_events_distinguish_forced_cut_from_silence` plus live-feed boundary response tests; Rust forced-chunk assembly/context and manual-current-turn tests; frontend context disclosure and collapsed-source tests | unit + route + component |

Coverage is unit-level plus Python route-level integration. There is no Rust integration test that drives the real consumer against a mock SSE server, and no test executes the detector, retrieval, answer and persistence path together.

### 5.3 Acceptance evidence (Observed)

- **E1a dry run** (`e1a-dry-run-host-final.json`): `simulated: true`, 14 cases, 9 eligible, **0 executed, 0 passed**; every latency value is generated by the simulator and is not evidence.
- **E1a live** (`e1a-results-host-final.json`): `status: "skipped"`, "Connection refused" on `127.0.0.1:9876`, 0 executed; no model was started or downloaded. The harness itself (`scripts/copilot-e2e/replay.py`) is loopback-only, refuses redirects and proxies, requires an exact `--model` once the service is reachable, requires an authoritative `[DONE]` plus valid usage and a bounded 1–3-bullet answer for every case, records the TTFT sample count, paces foreground request starts including the VAD flush, fails on any feed error, measures feed continuity by timestamps without vacuous success, and marks partial TTS runs `incomplete`. It never exercises the Rust detector or queue; `tag_question` is recorded as `not_applicable_service_only` and `rapid_pair` proves sequential streaming only.
- **E1b, E3, E4**: `pending native capture`. The operator runbook (`native-runbook.md`) prescribes a disposable `ADVERSARIA_DATA_DIR`, a virtual loopback device or acoustic speaker-to-mic capture, invented grounding text, a manifest-derived two-minute E3 WAV plus timestamp metadata, and a `null`-placeholder results template. Deterministic native queue stress additionally requires a delayed instrumented Local engine.
- **E2**: `pending credential` (no Anthropic key on this Mac). Claude coverage is offline SDK-shape and recorded-frame tests only.
- **E5 DeepSeek**: `pending credentialed smoke` (the founder has a key but it has not been entered). Provider behavior is covered with mocked upstream streams only.

Latency targets (heard ≤ 100 ms after the confirmed caption; first bullet ≤ 3 s p50 / ≤ 5 s p95 warmed local) remain **targets, unmeasured** for this build. The prior probe medians (1.68 s to confirmed caption, 32 ms retrieval, 0.5–0.9 s local card) predate this code and used a different model.

## 6. Who built what (Observed from result JSONs and HANDOFF)

| Stage | Worker and session | Outcome | Wrapper-reported usage |
|-------|--------------------|---------|------------------------|
| Spec (rev 0–2) | Claude Fable `8a3ac041-3eea-41e0-8f05-3739320fbf5e` | coauthored and performed final read-only audit; rev 3 records host fixes from that audit | **$20.97394675** total across the known Fable runs |
| S1+S2 core, first attempt | Opus (Antigravity) `4cfb3791-b01f-480d-95fb-ed5f4f05659d` | **incomplete, `is_error: true`**; retries `7678d7eb-…` and 2b failed on quota with zero usage | 338k in / 21k out |
| S1+S2 core recovery, provenance extraction | Sol (Codex) `01a07268-6162-7203-a6d9-7648d8825d4b` | `copilot_session.rs`, `copilot_provenance.rs`, storage v2, commands | 20.36M in / 113k out |
| S3 transport, Python boundary, web consent command | Sol (Codex) `01a0728c-a828-7121-ad75-4601f90fdcf6` | reader, `StreamControl`, validators, terminals | 3.76M in / 32k out |
| S4 frontend | Muse `01a0728c-a84f-7e70-87d5-775261671676` | strip, sheet, cards, consent, hooks | reported 0 / 0 (unreported) |
| S5+S6 harness, fixtures, runbook, docs | Gemini Flash `fdb74b0b-86b7-4386-9020-32c528b3790f` | `replay.py`, manifest, runbook, doc blocks | 1.23M in / 187k out |
| Final audit fixes and gates | host (GPT-6-Astra) | retry consent/retrieval, disclosures, UI accounting copy, harness privacy/cadence/pass rules, runbook and docs | n/a |
| Rev 4 DeepSeek addendum | host (GPT-6-Astra) | keychain integration, fixed provider transport, UI/receipts, tests and docs | n/a |

Every worker JSON reports `cost_usd: 0`; that value is **unreported**, not free. Dollar usage for Codex, Muse and Antigravity is unknown. The S2/S3 ownership split in rev 1 was honoured in the end state (Sol edited `copilot_session.rs` in S2 and `copilot_provenance.rs`/transport in S3) but by the same worker, not by Opus then Sol.

## 7. Completion matrix (honest)

| Capability | Unit | Integration | E1a service replay | Native E1b/E3/E4 | Claude E2 | DeepSeek E5 |
|------------|------|-------------|--------------------|------------------|-----------|-------------|
| Session-bound events | green | reducer + listener only | n/a | pending native capture | pending credential | pending credentialed smoke |
| Terminals and cancellation | green | Python route green; **Rust consumer: no test** | not run (service offline) | pending native capture | pending credential | mocked upstream green |
| Latest-intent queue | green (state) | **no test** | not applicable (sequential only) | pending native capture | n/a | pending credentialed smoke |
| Manual Ask, Retry | partial | n/a | n/a | pending native capture | pending credential | pending credentialed smoke |
| Provider egress validation | green | Python route green | not run | n/a | offline shape green | DeepSeek route green |
| Provenance, "Not in your notes", format | green | n/a | not run | pending native capture | pending credential | component green |
| Web accounting | green | n/a | n/a | n/a | pending credential | n/a: disabled |
| Bounds and Unicode | green | n/a | n/a | pending native capture | n/a | route green |
| Complete-turn assembly and Me/Them context | green | sidecar route + frontend component green | n/a | pending native speech capture | pending credential | mocked request green |
| Persistence, attach race, receipt | green (in-memory DB) | green (in-memory DB) | n/a | pending native capture (E4) | pending credential | receipt unit green |
| Transcript-first, strip, pin, errors | component green | n/a | n/a | pending native capture (E4) | n/a | component green |
| Latency targets | n/a | n/a | not run | pending native capture | pending credential | pending credentialed smoke |
| Provider pin | offline shape green | n/a | n/a | n/a | pending credential | mocked request green |

No row is **done**. "Green" means the named automated tests pass in the suites above; it does not mean the product behaviour was seen in a running app.

## 8. Final audit disposition

No P0 remains, and the final current-tree audits found no open P1. Fable's consent-boundary findings were fixed before the final gates.

| ID | Severity | Disposition |
|----|----------|-------------|
| G1 | P1 | **Fixed:** Rust refuses Retry unless current provider and required web consent match the frozen job; the UI hides Retry under the same conditions |
| G2 | P2 | **Fixed:** retry reuses passages only when original retrieval completed, otherwise it retrieves again |
| G3 | P1 | **Fixed:** both Claude disclosures enumerate question, two preceding Them lines, three passages, and folder instructions |
| G4 | P2 | **Fixed in copy:** the UI labels the value as a prepared request payload; `egress_bytes` remains the sidecar JSON byte count after removing the API key |
| G5 | P2 | **Open:** heard persistence and Local config resolution remain synchronous on the caption path; E1b must measure the ≤100 ms target before any optimization |
| G6 | P2 | **Open:** after three failed terminal writes the row stays `heard` and the UI receives no terminal event |
| G7 | P2 | **Partly fixed:** mismatch copy now says the authoritative returned id is used. If capture stop itself fails after session retirement, its cards can remain unattached |
| G8 | P2 | **Fixed:** new card/provenance status copy uses colons instead of em dashes |
| G9 | P2 | **Open:** legacy v1 storage helpers remain until the migration has shipped |

## 9. Prerequisites still open

1. Founder enters the DeepSeek key locally in Settings › Live Copilot and performs E5; the key must not enter docs, fixtures or chat.
2. Anthropic API key on the reference Mac for E2 (`claude-opus-5`; `web_search_20260209` and `allowed_callers: ["direct"]` host-checked against the web-search tool reference).
3. A virtual loopback device or acoustic playback for E1b/E3/E4; the report must record which.
4. A running local sidecar with a cached local model for a real E1a run (the recorded run was skipped because the service was offline).
5. A founder decision on committing `feat/live-copilot-c`; nothing here is committed or released.

References (host-checked 2026-09-05/06): Tauri 2 events https://v2.tauri.app/develop/calling-frontend/ · Claude citations https://platform.claude.com/docs/en/build-with-claude/citations · Claude model ids https://platform.claude.com/docs/en/models/overview · Claude web search https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-search-tool · DeepSeek OpenAI-compatible function calling/base URL https://api-docs.deepseek.com/guides/function_calling · DeepSeek model/pricing table https://api-docs.deepseek.com/quick_start/pricing · DeepSeek Chat Completions streaming/usage https://api-docs.deepseek.com/api/create-chat-completion/.
