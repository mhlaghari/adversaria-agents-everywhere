# CLAUDE.md — Meeting Note Taker

Guidance for any AI agent (and human) working in this repository. Read this
first, every session. It is intentionally short; the deep detail lives in the
linked companion documents under [`docs/`](./docs).

---

## What this project is

**Meeting Note Taker** is a privacy-first, bot-free, Granola-style meeting
notetaker for **Windows and macOS** (Apple Silicon). It records meeting audio
locally, transcribes it on-device, and generates structured notes with a local
LLM. **Nothing leaves the machine** — no bot joins the call, no audio or
transcript is uploaded, and recordings are deleted once a meeting is successfully
transcribed (a recording that couldn't be transcribed is kept on-device, marked, until you retry).

Three layers talk to each other on one machine:

```
React UI ──invoke──▶ Tauri (Rust) ──HTTP :9876──▶ Python ML service (FastAPI)
                       │                            ├─ faster-whisper / mlx-whisper (transcription, GPU)
                       │                            └─ Ollama           (summarization, local LLM)
                       ├─ dual capture: system ("Them") + mic ("Me") → WAV
                       │    Windows: WASAPI loopback · macOS: Core Audio process tap + cpal (SCK removed 2026-08-13)
                       └─ SQLite meeting history (per-OS app-data dir)
```

The OS-specific layers (audio capture, meeting detection, Whisper backend) are
`#[cfg]`-gated; everything else is shared. macOS port: **ADR-010** + the macOS
runbook in [docs/HANDOFF.md](./docs/HANDOFF.md).

Full system design, data flow, and the public interface of every layer are in
**[docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md)**. The original design spec and
phase plan live in [`docs/superpowers/`](./docs/superpowers).

---

## Core principles

1. **Research the latest first — never rely on training memory for anything
   versioned.** Before you implement against, advise on, or debug any library,
   framework, API, model, or CLI, verify the *current* docs and version facts
   (WebSearch / context7 / official changelogs). This stack moves fast
   (Tauri 2, faster-whisper/CTranslate2 + Blackwell GPU support, uv, Ollama,
   Pydantic, httpx) and memory-based answers have already caused real bugs here.
   Cite versions and link sources in whatever you produce. When memory and a
   fetched source disagree, the source wins.

2. **Privacy is the product.** Default to 100% local/offline. Audio is deleted
   after transcription. Never add a code path that sends audio, transcripts, or
   summaries off-device unless the user has *explicitly* opted in for that
   specific run, and the UI clearly says so. The webview never needs network
   access to the Python service — Rust talks to it via `reqwest`. Keep it that
   way.

3. **Verify against reality, don't assume.** Read the actual file before editing
   it. Run the tests. Run the app. Check the database / config on disk. Several
   bugs in this repo's history were "looked fine, wasn't" — a stale port cached
   in memory, a status stuck in one state, a mic channel never captured. Confirm
   behavior, then report it plainly (including failures).

4. **Many small, focused files; immutability; explicit errors.** Follow the
   per-language conventions in [Conventions](#conventions). Handle errors at
   every boundary with user-facing messages; never silently swallow them.

5. **Leave the docs better than you found them.** When you discover something
   non-obvious, fix a bug, make a decision, or finish a chunk of work, update
   the relevant companion doc (below) in the same change. Docs that lie are
   worse than no docs.

---

## Companion documents

Keep these current. They are the project's memory between sessions.

| Document | Purpose | Update when |
|----------|---------|-------------|
| [docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md) | System design, layers, data flow, interfaces | The shape of a layer or its contract changes |
| [docs/HANDOFF.md](./docs/HANDOFF.md) | Current state; how to pick up work cold | You pause work or finish a session |
| [docs/LESSONS_LEARNED.md](./docs/LESSONS_LEARNED.md) | Roadblocks hit and how they were resolved | You burn time on a non-obvious problem |
| [docs/TODO.md](./docs/TODO.md) | Prioritized backlog, known issues, roadmap | You find a bug/idea or complete a roadmap item |
| [docs/DECISIONS.md](./docs/DECISIONS.md) | Why the architecture is shaped as it is (ADR-style) | You make a decision with alternatives |
| [docs/marketing_strategy.md](./docs/marketing_strategy.md) | Competitive assessment + GTM recommendations | You reassess competitive position or strategy |
| [docs/STRATEGY_HANDOFF.md](./docs/STRATEGY_HANDOFF.md) | GTM/marketing workstream baton: live-funnel state, phase plan, toolkit, queue | Any marketing/launch work happens or its next step changes |
| [docs/DEEP_DIVE_BUSINESS.md](./docs/DEEP_DIVE_BUSINESS.md) | Comprehensive business-oriented project overview (market, strategy, GTM) | Product scope, market position, or strategy shifts |
| [docs/DEEP_DIVE_TECHNICAL.md](./docs/DEEP_DIVE_TECHNICAL.md) | Comprehensive technical deep-dive (architecture, internals, stack) | Major feature added or architecture changes |

---

## Reading and writing documents effectively

Docs are a tool for getting work done, not a formality. Use them well.

**Reading (before you act):**
- Read this file, then the *one or two* companion docs relevant to your task —
  not everything. For a bug, start with `LESSONS_LEARNED.md` (it may already be
  solved) and `ARCHITECTURE.md` for the affected layer.
- Treat every doc as **point-in-time**. A doc naming a file, flag, version, or
  default may be stale — confirm against the live code/config before relying on
  it. Principle #1 applies to our own docs too.
- Prefer the source of truth: code over docs for *how it works now*; docs over
  code for *why it's that way* and *what's intended next*.

**Writing (as you work):**
- **One concern per document.** Don't put a roadmap item in LESSONS or a
  decision in TODO. Link between them instead of duplicating.
- **Lead with the answer.** State the conclusion / current state / decision in
  the first sentence; put the reasoning and detail below. A reader skimming the
  first line should get the gist.
- **Be concrete and verifiable.** Reference `file_path:line`, exact commands,
  exact version numbers, real error strings. Avoid vague advice ("handle errors
  properly") in favor of the specific thing to do here.
- **Date and attribute decisions.** Convert "recently" / "now" to absolute
  dates. State what was tried, what was chosen, and why.
- **Write the smallest doc that does the job.** Cut anything the reader can get
  faster from the code. If a section is going stale faster than it earns its
  keep, delete it.
- **Keep CLAUDE.md lean.** It loads into context every session. New deep content
  goes in a companion doc with a one-line pointer here.

---

## Development quickstart

You need two processes. See [docs/HANDOFF.md](./docs/HANDOFF.md) for the full
runbook and troubleshooting.

```powershell
# Terminal 1 — Python ML service (loads Whisper; first run downloads the model)
cd python-service
uv sync --extra cuda          # --extra cuda installs cuBLAS/cuDNN for GPU; omit on CPU-only
uv run uvicorn src.server:app --host 127.0.0.1 --port 9876 --log-level info

# Terminal 2 — the desktop app
npm install
npm run tauri dev
```

Health check: `curl http://127.0.0.1:9876/health` →
`{"status":"ok","whisper_model":"large-v3","ollama_available":true}`.

Prerequisite: Ollama running with the model pulled (`ollama pull llama3.1:8b`).

**Tests / checks:**
```powershell
cd python-service; uv run pytest          # 50 tests, ML deps mocked, <1s
cd src-tauri;      cargo check            # Rust compiles
npx tsc --noEmit                          # frontend type-check
```

---

## Critical gotchas (the short list)

The full list with root causes is in [LESSONS_LEARNED.md](./docs/LESSONS_LEARNED.md).
These are the ones that will bite you fastest:

- **`cargo` is not on PATH in Git Bash** — prefix with `export PATH="$HOME/.cargo/bin:$PATH"` or use PowerShell.
- **Stale port holders** — a crashed run can leave a listener on **9876** (Python) or **1420** (Vite). Kill it before relaunching, or the next start fails.
- **Config URL is cached in memory** — `AppState`'s HTTP client is built once at startup from `config.json`. Changing the service URL in Settings does **not** take effect until app restart. (This caused the `9878` connection failures.)
- **GPU libraries are an opt-in extra** — plain `uv sync` does *not* install the CUDA DLLs; you must `uv sync --extra cuda`, or transcription silently runs on CPU.
- **Test with real speech, not silence** — Whisper hallucinates on silent audio (mitigated, but recording nothing is not a valid test). Mic capture records your **default** Windows input device.

---

## Known issues to be aware of

Verified, currently-live correctness issues are tracked at the top of
[docs/TODO.md](./docs/TODO.md). The two long-standing 🔴 bugs — Ollama `num_ctx`
truncation and the wrong Whisper `compute_type` — were **fixed 2026-06-16**, and
no known correctness bugs remain.

The one live **setup gotcha (macOS):** the MLX Whisper model download hangs at 0
bytes because this box's `hf_xet` is broken — launch the Python service with
`HF_HUB_DISABLE_XET=1` (see [LESSONS_LEARNED.md](./docs/LESSONS_LEARNED.md) and the
macOS runbook in [HANDOFF.md](./docs/HANDOFF.md)).

---

## Conventions

Follow the user's global rules in `~/.claude/rules/` and the patterns already in
this codebase. In short:

- **Rust:** IPC commands are `#[tauri::command] async fn … -> Result<T, String>`
  with human-readable errors. Keep std-Mutex guards from crossing `.await`.
- **Python:** PEP 8, type annotations on all signatures, Pydantic v2 models at
  the API boundary, `logging` (never `print`), pytest with ML deps mocked.
- **TypeScript/React:** function components with explicit prop interfaces (no
  `React.FC`), immutable state updates (spread), typed IPC wrappers in
  `src/lib/tauri.ts` mapping 1:1 to Rust commands, no `any`.
- **Commits:** Conventional Commits (`feat:`, `fix:`, `docs:`, `refactor:`,
  `test:`, `chore:`). Analyze full history for PRs. Commit/push only when asked.

---

## Repository map

```
src/                  React frontend (components/, hooks/, lib/tauri.ts, types.ts)
src-tauri/src/        Rust backend
  audio/mod.rs        WASAPI dual capture (system loopback + microphone) → WAV
  commands.rs         Tauri IPC commands + AppState
  http_client.rs      Typed client for the Python service
  storage.rs          SQLite meeting store
  config.rs           config.json load/save
  tray.rs             system tray + Ctrl+Shift+M global hotkey
  types.rs            shared serde types
python-service/
  src/server.py       FastAPI app: /health /templates /transcribe (+me_label/vocabulary) /summarize
  src/transcriber.py  Whisper wrapper (faster-whisper CUDA→CPU / MLX; dual/labeled; relabel_me + vocab initial_prompt)
  src/summarizer.py   Ollama wrapper + prompt template loading
  src/config.py       prompt template discovery/loading
  src/models.py       Pydantic request/response models
  prompts/            editable summarization templates (general, one-on-one, client-meeting)
  tests/              50 pytest tests (ML deps mocked)
docs/                 ARCHITECTURE, HANDOFF, LESSONS_LEARNED, TODO, DECISIONS
  superpowers/        original design spec, phase plan, build handoffs
```

<!-- stuntman:scaffold:start -->
## Project memory protocol

These are **living documents** — read them first, keep them current.

**Read this first — start of every session** (or just run `/handoff`):
1. `HANDOFF.md` — the session baton: what the last session changed, the next step, gotchas. Assume zero memory of prior sessions.
2. `STATUS.md` — the board: built / in progress / planned.
3. `SPEC.md` — the contract: what this is, the load-bearing principles, where it's going. Build to it.
4. `STRATEGY.md` — the honest why / direction. Read before any big call.
5. `README.md` — what the project is and how to run it.

**Before you stop — end of every session:**
- Always update `HANDOFF.md` (what changed, next step, gotchas) and `STATUS.md` (refresh the board).
- Update `SPEC.md`, `STRATEGY.md`, or `README.md` whenever the change touched what they cover — and add a dated changelog line.
- Never commit without explicit user authorization.

A task isn't "done" until the docs its change touched reflect it.
<!-- stuntman:scaffold:end -->
