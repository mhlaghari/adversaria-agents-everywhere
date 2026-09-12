# Packaging Milestone — "Double-click to working app"

**Goal:** a non-technical Windows user downloads one installer, double-clicks it,
and gets a working app — record → transcribe → summarize — with **no terminal,
no manually-run `uvicorn`, no manually-run Ollama**, and a **clean shutdown** that
leaves no orphaned process or locked port behind.

This is the gate to everything else: real OSS adoption, a demo video, and any paid
tier all require an installable product. It is also mostly the same work whether
or not the project is ever monetized.

> Status: **not started** (2026-06-16). Today the app assumes a dev stack — two
> terminals plus a pre-running Ollama. See [HANDOFF.md](./HANDOFF.md) for the dev
> runbook this milestone replaces.

---

## Definition of done

A fresh Windows 11 machine (no Python, no uv, no dev tools) can:

1. Run `Meeting-Note-Taker-x.y.z-setup.exe`, click through, launch the app.
2. Complete a first-run setup (Ollama present-or-installed, default model pulled,
   with visible progress) without touching a terminal.
3. Record a real meeting and get a transcript + summary.
4. Close the window to the tray; quit from the tray with **no leftover
   `python-service` process and no port still held** (verified via Task Manager /
   `netstat`).
5. See a clear loading state while the ML service warms up — never a raw
   connection-failed error.

Acceptance is binary: if any step needs a terminal or a manual process, it's not
done.

---

## Current gaps (verified 2026-06-16)

- `tauri.conf.json`: no `externalBin`, no installer `targets`, `security.csp` is
  `null` (Tauri's main XSS mitigation is off).
- The Python service is launched by hand (`start_python_service.bat` / `uvicorn`)
  and the URL/port is read once at startup — the source of the 9876/9877 orphan-
  port saga.
- No deterministic shutdown: a crashed run can leave a listener on the port and
  the GPU pinned (see [LESSONS_LEARNED.md](./LESSONS_LEARNED.md)).
- Ollama is assumed already installed with the model pulled.
- GPU path needs CUDA 12 runtime DLLs (cuBLAS/cuDNN) that today come from the dev
  environment's nvidia pip packages — these must travel inside the bundle.

---

## Phases

Each phase is independently testable. Recommended order is top-to-bottom; phases
2–4 can overlap.

### Phase 1 — Python service as a PyInstaller `--onedir` build

**Why `--onedir`, not `--onefile`:** `--onefile` unpacks ~400 MB of CUDA libs to a
temp dir on every launch (slow) and is the classic source of orphaned-process
bugs. `--onedir` ships a folder and starts fast.

- [ ] PyInstaller spec for `python-service` that bundles `faster-whisper`,
      `ctranslate2`, FastAPI/uvicorn, and **the CUDA 12 runtime DLLs**
      (`cublas64_12.dll`, cuDNN, `cudart`, `cuda_nvrtc`) from the active env's
      `nvidia/*/bin` dirs. Verify the GPU path loads in the built exe, not just
      in dev.
- [ ] Confirm the built service still falls back to CPU (`int8`) when no GPU /
      DLLs are present — the installer must work on GPU-less machines too.
- [ ] Output named for Tauri's sidecar convention:
      `src-tauri/bin/python-service-x86_64-pc-windows-msvc.exe` (the wrapper exe;
      the `--onedir` payload sits alongside).
- [ ] Acceptance: run the built exe directly on a clean VM → `GET /health` returns
      `ok` and a real WAV transcribes.

### Phase 2 — Spawn + supervise the sidecar from Rust

- [ ] Add `externalBin` (the sidecar) to `tauri.conf.json` `bundle`.
- [ ] In `lib.rs setup()`, spawn the sidecar via `app.shell().sidecar(...)`.
      **Pick a free ephemeral port** at spawn time and pass it to the sidecar
      (`--port`), then build the `HttpClient` from that port — this retires the
      hard-coded 9876/9877 problem and the "URL cached at startup" bug for the
      packaged path.
- [ ] Add a scoped capability: `shell:allow-execute` (or `allow-spawn`) with
      `sidecar: true` for just this binary — no general shell exec.
- [ ] Acceptance: launching the app starts the service with no terminal; the app
      reaches it on the chosen port.

### Phase 3 — Deterministic shutdown (no orphans)

- [ ] Add `POST /shutdown` to `server.py` that stops uvicorn gracefully.
- [ ] In Rust, handle `RunEvent::ExitRequested`: call `/shutdown`, wait briefly,
      then hard-kill the child (`taskkill /F /T /PID`) as a fallback.
- [ ] Also kill the child on `WindowEvent::CloseRequested` path if quitting.
- [ ] Acceptance: quit the app → no `python-service*` process remains and the port
      is free (`netstat -ano | findstr <port>` empty). Relaunch works first try.

### Phase 4 — Health-gate the UI

- [ ] After spawning the sidecar, poll `/health` (model load is slow — seconds to
      a minute) and emit a `service-ready` event.
- [ ] UI shows a "Starting transcription engine…" state until ready; recording /
      transcribe controls are disabled or queued until then, never firing into a
      dead socket.
- [ ] Acceptance: cold launch → loading state → ready, with no transient error
      toast.

### Phase 5 — First-run setup (Ollama + model)

Ollama and its multi-GB models are **not** bundled (size + licensing). Manage them
instead.

- [ ] Detect Ollama on launch (is the daemon reachable / is the binary present).
- [ ] If missing: a setup screen that links the official installer (or shells the
      winget/installer), then re-checks.
- [ ] Pull the default model (`qwen3.6:35b-a3b`) with a **visible progress bar**
      driven by Ollama's pull API; block summarization until present.
- [ ] Let the user choose GPU vs CPU and confirm VRAM headroom up front.
- [ ] Acceptance: on a machine with neither Ollama nor the model, first-run ends
      with both ready, no terminal used.

> Note: once the Groq/cloud tier exists, GPU-less users can skip Ollama entirely
> and use cloud inference — this setup flow should branch on "local vs cloud".
> Out of scope for this milestone; see [TODO.md](./TODO.md).

### Phase 6 — Harden + ship the installer

- [ ] Set `app.security.csp` (e.g.
      `default-src 'self'; connect-src 'self' ipc: http://ipc.localhost`). The
      webview needs **no** network to the service — Rust proxies it. Keep it that
      way.
- [ ] **Close-to-tray:** intercept `WindowEvent::CloseRequested` →
      `prevent_close()` + `hide()` so closing keeps it running in the tray (also
      makes the meeting-detected card / tray flow real).
- [ ] Configure NSIS bundle target → `Meeting-Note-Taker-x.y.z-setup.exe`.
- [ ] **Code-sign** the installer and the bundled sidecar exe (reduces
      SmartScreen / AV friction — unsigned will scare off non-technical users).
- [ ] (Optional) Add the Tauri updater plugin for signed auto-updates.
- [ ] Acceptance: the full "Definition of done" checklist passes on a clean VM.

---

## Key risks / open decisions

- **Bundle size.** CUDA libs + large-v3 model assets push the installer large.
  Decide: ship CPU-only Whisper by default and download CUDA libs on demand, or
  accept a big GPU bundle. (The Ollama model is pulled separately, so it's not in
  the installer either way.)
- **Code-signing cert.** An OV/EV cert costs money and takes setup; without it,
  SmartScreen flags the app. Decide before public release — it materially affects
  install conversion.
- **Whisper model distribution.** `large-v3` weights download on first transcribe
  (faster-whisper fetches from HF). Either pre-warm during first-run setup or
  accept a one-time delay on the first recording.
- **Multi-GPU / scaling factor** edge cases for window placement and CUDA device
  selection on machines unlike the dev 5090.

---

## Out of scope (intentionally)

- macOS / Linux packaging (Windows-first; revisit after Windows ships).
- The Groq/cloud tier and managed subscription (separate milestone — they *reuse*
  the sidecar/health/first-run plumbing but add auth/billing).
- Auto-update signing infrastructure beyond the optional updater stub above.
