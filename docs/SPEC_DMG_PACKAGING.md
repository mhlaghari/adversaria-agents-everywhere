# SPEC — macOS `.dmg` packaging (Apple Silicon)

> **Release operator:** use [NOTARIZATION.md](./NOTARIZATION.md) for the exact
> Apple account, certificate, Keychain profile, release command, verification
> gates, failure recovery, and next-release checklist. This file remains the
> packaging design/specification; the notarization document is the live runbook.

> **STATUS 2026-06-20: Phase 1 DONE.** `./scripts/build-dmg.sh` produces a working `Adversaria.dmg`; verified end-to-end. `.dmg` is packaged with `hdiutil` (Tauri's `bundle_dmg.sh` fails on the large app). Sidecar signed with `entitlements.plist` (disable-library-validation).


**One-line goal:** double-click a `.dmg` → drag *Adversaria* to `/Applications`
→ launch → it works (record → transcribe → summarize) with **no Terminal, no
`uvicorn`, no manual Python/uv setup**, and a clean shutdown that leaves no
orphaned `python-service` and no held port.

This is the macOS counterpart to [PACKAGING.md](./PACKAGING.md) (which is
Windows/NSIS-focused). Where the two overlap (sidecar spawn, free-port,
health-gate, shutdown), the *plumbing is shared*; this doc covers the parts that
differ on macOS: the **MLX** Whisper backend, **ffmpeg** bundling, the
**`.dmg`** bundle target, and Apple **signing/notarization**.

> Verified 2026-06-20 against live repo + current upstream docs. Versions and
> sources are cited inline. Per CLAUDE.md principle #1, treat any version/flag
> here as point-in-time — re-confirm before a release build.

---

## 1. Goal & definition of done

### Definition of done (Phase 1 — personal `.dmg`)

A fresh Apple-Silicon Mac (macOS ≥ 14.4, **with the two prerequisites below
installed** — see §8) can:

1. Open `Adversaria_0.1.0_aarch64.dmg`, drag the app to `/Applications`.
2. Launch it from Finder **without** the "damaged / can't be opened" dialog
   (after the one-time quarantine step in §7 for an *unsigned* personal build).
3. See a "Starting transcription engine…" state while the bundled Python
   sidecar boots and loads MLX Whisper (cold-start can be tens of seconds the
   first time; the MLX model downloads on first transcribe — see §9).
4. Record a real meeting → get a labeled transcript (MLX Whisper) → get a
   summary (via the prerequisite LLM server).
5. Quit → **no `python-service` / sidecar process remains, the port is free**
   (`lsof -nP -iTCP -sTCP:LISTEN | grep <port>` empty). Relaunch works first try.

Acceptance is binary: if any step needs a Terminal, it's not done. (The §8
prerequisites — ffmpeg-free since we bundle it, plus the LLM server — are
installed once and are out of the app's control; see "what stays a prerequisite".)

### Definition of done (Phase 2 — distributable `.dmg`)

Same, but the `.dmg` is **signed (Developer ID) + notarized + stapled**, so any
Mac opens it with no quarantine workaround and no Gatekeeper warning. Requires a
paid Apple Developer account (§7).

---

## 2. Current state (what exists, what's missing)

Verified by reading the repo on 2026-06-20.

**Exists / works in dev:**
- macOS stack is all-Apple-GPU (ADR-010, HANDOFF.md): ScreenCaptureKit + cpal
  capture; **MLX Whisper** (`mlx-community/whisper-large-v3-mlx`) for STT;
  **Rapid-MLX** (`qwen3.6-27b`, OpenAI-compatible at `127.0.0.1:8000/v1`) for
  summarization.
- `python-service/src/transcriber.py:399` — `MlxWhisperTranscriber`; model
  auto-downloads to the HF cache on first use; mlx-whisper imported lazily.
- `python-service/src/summarizer.py:48-62` — backend auto-selects `openai`
  (Rapid-MLX) on Apple Silicon via `default_llm_backend()`.
- `src-tauri/Cargo.toml` — `tauri-plugin-shell = "2"` is **already a dependency**
  and `tauri_plugin_shell::init()` is registered in `src-tauri/src/lib.rs:26`.
- `tauri.conf.json` — `bundle.macOS.minimumSystemVersion: "14.4"`; icons incl.
  `icon.icns`; `productName: "Meeting Note Taker"`, `identifier:
  com.meetingnotetaker.app`. (Window title is "Adversaria".)
- `pyproject.toml` — `[project.optional-dependencies] mlx` installs
  `mlx-whisper>=0.4.3` (arm64-macOS marker).

**Missing for a `.dmg` (the gap this spec closes):**
- **No PyInstaller build.** The service is run by hand via `uvicorn` CLI; there
  is **no `src-tauri/bin/`** directory and no sidecar binary.
- **`server.py` has no `--port`/`--host` CLI and no `__main__`** — it's launched
  externally by `uvicorn src.server:app`. A PyInstaller entrypoint and an
  argparse `--port` must be added (§5.1).
- **No `/shutdown` endpoint.** No graceful stop path; shutdown is "kill the
  terminal" today.
- **`tauri.conf.json` has no `bundle.externalBin`** and **no `bundle.targets`**
  (so `tauri build` won't produce a `.dmg` deterministically). `app.security.csp`
  is `null`.
- **No sidecar spawn in Rust.** `lib.rs setup()` never starts the Python
  service; `AppState` builds its `HttpClient` from `config.python_service_url`
  (hard-coded `http://127.0.0.1:9876`, `config.rs`/`commands.rs:46`). No
  free-port pick, no health-gate, no `ExitRequested` shutdown.
- **`capabilities/default.json`** has `shell:allow-open` only — no
  `shell:allow-execute` with `sidecar: true`.
- **ffmpeg is not bundled** — today it's `brew install ffmpeg` (HANDOFF.md:137),
  on the user's `PATH`. mlx-whisper shells out to it for audio decode.

---

## 3. Recommended toolchain (with versions + why)

| Concern | Tool | Version (verified 2026-06-20) | Why |
|---|---|---|---|
| Python → standalone binary | **PyInstaller, `--onedir`** | **6.21.0** (stable; 6.20.0 was 2026-04-22) | Most battle-tested for compiled-extension ML stacks; `--onedir` starts fast and avoids the per-launch temp-unpack orphan-process class that `--onefile` causes. See §3.1. |
| Bundle into the `.app` | **Tauri 2 `bundle.externalBin`** | tauri 2.x; `tauri-plugin-shell` **2.3.x** | Already a dependency. Tauri copies the sidecar into `Adversaria.app/Contents/MacOS/` and signs it as part of `tauri build`. |
| Spawn / supervise sidecar | **`tauri-plugin-shell` `shell().sidecar()`** | 2.3.x | Native Tauri 2 sidecar API; gives `(rx, child)` for stdout + a kill handle. |
| Audio decode for MLX | **ffmpeg static arm64 binary**, bundled as a *resource* | ffmpeg ≥ 7.x | mlx-whisper requires ffmpeg on `PATH`; we ship it and point at it (§6). |
| `.dmg` packaging | **Tauri bundler** (`bundle.targets: ["dmg"]`) | tauri 2.x | Built-in; no extra tooling. |
| Signing/notarization | **`codesign` (ad-hoc, Phase 1)** → **Developer ID + `notarytool` (Phase 2)** | Xcode 16+ CLT | `altool` is dead (rejected since 2023-11-01); `notarytool` is the only path. |

### 3.1 Is PyInstaller still the right tool in 2026? — Yes, for this repo.

Alternatives considered, with the 2026 reality:

- **`uv`-based standalone:** `uv` is now the standard project/dep manager
  (and we already use it), but it does **not** produce a self-contained,
  Python-free `.app` payload. It's for `uv run`/`uvx` script distribution, not
  for shipping to a Mac with no toolchain. **Not a packaging tool here.**
- **py2app:** macOS-native `.app` builder, but brittle with large compiled-
  extension stacks (recipes lag), macOS-only, steeper for complex apps. Tauri is
  *already* producing the `.app`; we only need the **Python part as a binary**,
  not a second app bundle. **Wrong layer.**
- **Briefcase (BeeWare):** great when the *native installer* is the whole
  product — but here Tauri owns the app shell. Adding Briefcase would mean two
  app-bundle builders. **Redundant.**
- **PyInstaller `--onedir`:** produces a folder (`python-service/` + a launcher
  binary) that we treat as the sidecar payload. Handles mlx/numba/uvicorn with
  hidden-imports + collect-all, which the others make harder to control.
  **Chosen.**

**Bottom line:** PyInstaller `--onedir` for the *service*, Tauri `externalBin`
for *embedding it in the `.app`*. This matches PACKAGING.md's Windows decision,
so one mental model covers both OSes.

---

## 4. Architecture of the packaged app

```
Adversaria.app/
└─ Contents/
   ├─ MacOS/
   │  ├─ adversaria                         ← Tauri/Rust main binary
   │  └─ python-service-aarch64-apple-darwin → sidecar launcher (suffix stripped at bundle time)
   ├─ Resources/
   │  ├─ _up_/ … or resources/ffmpeg        ← bundled ffmpeg arm64 (a Tauri bundle resource)
   │  └─ python-service/                     ← PyInstaller --onedir payload (libs, mlx, etc.)
   └─ Info.plist
```

Runtime flow (replaces the dev "two terminals"):

```
Rust setup():
  pick free port P  (TcpListener "127.0.0.1:0")
  spawn sidecar:  python-service --host 127.0.0.1 --port P
                  env: HF_HUB_DISABLE_XET=1, PATH=<bundled ffmpeg dir>:$PATH
  build HttpClient at http://127.0.0.1:P
  poll GET /health until ok → emit "service-ready" → UI leaves loading state
Quit (RunEvent::ExitRequested):
  POST /shutdown → wait briefly → child.kill() fallback
```

The summarizer (Rapid-MLX / Ollama) is **not** spawned by us — it's a separate
local server the user runs (§8). The sidecar talks to it over localhost exactly
as in dev.

---

## 5. Step-by-step build pipeline

### 5.1 Make `server.py` runnable as a binary with a `--port`

Add a CLI entrypoint (PyInstaller needs a real script to freeze; the service
also needs to accept the Rust-chosen port). New file
`python-service/run_service.py`:

```python
"""PyInstaller entrypoint: run the FastAPI app under uvicorn on a chosen port."""
import argparse
import uvicorn
from src.server import app  # noqa: F401  (kept importable for the frozen build)

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=9876)
    args = parser.parse_args()
    uvicorn.run(app, host=args.host, port=args.port, log_level="info")

if __name__ == "__main__":
    main()
```

Add a graceful shutdown endpoint in `python-service/src/server.py` (so Rust can
ask it to stop before falling back to kill):

```python
import os, signal
from fastapi import BackgroundTasks

@app.post("/shutdown")
async def shutdown(background: BackgroundTasks) -> dict:
    background.add_task(lambda: os.kill(os.getpid(), signal.SIGTERM))
    return {"status": "shutting-down"}
```
(uvicorn handles SIGTERM → graceful lifespan teardown, which already nulls the
singletons in `server.py`'s `lifespan`.)

### 5.2 PyInstaller spec (`--onedir`)

Create `python-service/pyinstaller.spec`. Key points for **this** dependency set:

- **Entrypoint:** `run_service.py`.
- **Hidden imports — uvicorn:** uvicorn lazy-imports its loop/protocol/lifespan
  plugins, which PyInstaller misses. Include:
  `uvicorn`, `uvicorn.logging`, `uvicorn.loops`, `uvicorn.loops.auto`,
  `uvicorn.loops.asyncio`, `uvicorn.protocols`, `uvicorn.protocols.http.auto`,
  `uvicorn.protocols.http.h11_impl`, `uvicorn.protocols.websockets.auto`,
  `uvicorn.protocols.websockets.websockets_impl`, `uvicorn.lifespan.on`,
  `uvicorn.lifespan.off`.
- **Hidden imports — our app:** `src.server`, `src.transcriber`,
  `src.summarizer`, `src.config`, `src.models` (PyInstaller's static analysis
  can miss the dynamic FastAPI wiring).
- **`mlx` / `mlx-whisper` — use `collect_all`.** mlx ships a **Metal library
  data file** (`*.metallib`) and numba/JIT bits that PyInstaller's hook may not
  fully grab. Use:
  ```python
  from PyInstaller.utils.hooks import collect_all
  mlx_datas, mlx_bins, mlx_hidden = collect_all("mlx")
  mlxw_datas, mlxw_bins, mlxw_hidden = collect_all("mlx_whisper")
  numba_datas, numba_bins, numba_hidden = collect_all("numba")
  ```
  Merge those into `datas`, `binaries`, `hiddenimports`. Verify the bundled
  binary can import `mlx.core` and run a tiny `mlx_whisper.transcribe` — the
  `.metallib` is the thing most likely to be left out.
- **mlx-whisper data:** `mlx_whisper` ships `assets/` (mel filters, tokenizer);
  `collect_all("mlx_whisper")` should pull it — confirm `assets/mel_filters.npz`
  lands in the payload.
- **`tiktoken` / tokenizer regex:** if a tokenizer import error appears at
  runtime, add `tiktoken_ext` + `tiktoken_ext.openai_public` to hidden imports.
- **`faster_whisper` / `ctranslate2`:** still imported by `transcriber.py`
  (the non-mac fallback path). On a mac-only build you *may* exclude them to cut
  size, but the module imports `from faster_whisper import WhisperModel` at top
  level (`transcriber.py:15`), so either keep them bundled or guard that import.
  Simplest for Phase 1: **keep them** (mac wheels are CPU-only and small-ish) to
  avoid touching the import.

Build (from `python-service/`):
```bash
uv sync --extra mlx --extra dev          # ensure mlx + pyinstaller present
uv pip install pyinstaller               # or add to a [tool.uv] dev group
uv run pyinstaller pyinstaller.spec --noconfirm --clean
# → dist/python-service/  (the --onedir payload + the launcher binary)
```

### 5.3 Place the binary as a Tauri sidecar (target-triple suffix)

Tauri's `externalBin` requires the launcher named with the **host target-triple
suffix**; Tauri strips it at bundle time. Find the triple with
`rustc --print host-tuple` → on this box `aarch64-apple-darwin`.

```bash
mkdir -p src-tauri/bin
# the --onedir launcher (PyInstaller names it after the entry, e.g. run_service)
cp python-service/dist/python-service/run_service \
   src-tauri/bin/python-service-aarch64-apple-darwin
# the rest of the --onedir payload travels as a bundle *resource* (see 5.5)
cp -R python-service/dist/python-service src-tauri/resources/python-service
```
> Note: with `--onedir`, the launcher binary depends on the sibling payload
> folder. The cleanest layout is to ship the **whole `--onedir` folder** as a
> Tauri **resource** and point the sidecar entry at the launcher inside it. Two
> viable shapes:
> - **(A) Resource-folder:** put the entire `dist/python-service/` under
>   `bundle.resources`, and `externalBin` points at the launcher copy — at
>   runtime resolve the payload via the resource dir. Cleanest for `--onedir`.
> - **(B) Self-contained launcher:** if PyInstaller's launcher can find its
>   `_internal/` relative to itself inside `Contents/MacOS/`, ship that folder
>   too. Test which layout PyInstaller produces and pick one. Verify the copied
>   binary launches standalone *before* wiring Tauri.

### 5.4 `tauri.conf.json` bundle config

Add `externalBin`, `resources`, `targets`, and a CSP. Edit
`src-tauri/tauri.conf.json` `bundle`:

```json
"bundle": {
  "active": true,
  "targets": ["dmg", "app"],
  "externalBin": ["bin/python-service"],
  "resources": ["resources/ffmpeg", "resources/python-service"],
  "icon": [ /* unchanged */ ],
  "macOS": {
    "minimumSystemVersion": "14.4",
    "entitlements": "Entitlements.plist",
    "hardenedRuntime": true
  }
}
```
And tighten the CSP (the webview needs **no** network — Rust proxies the
service):
```json
"app": { "security": { "csp": "default-src 'self'; connect-src 'self' ipc: http://ipc.localhost; img-src 'self' data:; style-src 'self' 'unsafe-inline'" } }
```
> `externalBin` value is the path **without** the `-aarch64-apple-darwin`
> suffix; the suffixed file must exist on disk. (v2.tauri.app/develop/sidecar)

### 5.5 Capability: allow executing just this sidecar

Edit `src-tauri/capabilities/default.json` `permissions` — add a scoped execute
permission (keep `shell:allow-open`):

```json
{
  "identifier": "shell:allow-execute",
  "allow": [{ "name": "bin/python-service", "sidecar": true }]
}
```
No general shell exec — only this sidecar.

### 5.6 Rust: free-port spawn + health-gate + shutdown

In `src-tauri/src/lib.rs setup()` (after the existing init), spawn the sidecar.
Sketch (uses `tauri-plugin-shell`'s `ShellExt`, already a dep):

```rust
use std::net::TcpListener;
use tauri::Manager;
use tauri_plugin_shell::ShellExt;
use tauri_plugin_shell::process::{CommandChild, CommandEvent};

// 1) pick a free port the OS hands us
let port = {
    let l = TcpListener::bind("127.0.0.1:0").expect("no free port");
    l.local_addr().unwrap().port()                // listener dropped → port freed
};

// 2) resolve bundled ffmpeg dir so mlx-whisper can find it (see §6)
let resource_dir = app.path().resource_dir().unwrap();
let ffmpeg_dir = resource_dir.join("resources/ffmpeg");
let path_env = format!("{}:{}", ffmpeg_dir.display(),
                       std::env::var("PATH").unwrap_or_default());

// 3) spawn the sidecar on that port
let sidecar = app.shell()
    .sidecar("python-service").expect("sidecar missing")
    .args(["--host", "127.0.0.1", "--port", &port.to_string()])
    .env("HF_HUB_DISABLE_XET", "1")     // documented gotcha (this box's hf_xet)
    .env("PATH", path_env);
let (mut rx, child) = sidecar.spawn().expect("failed to spawn sidecar");

// 4) keep the child handle so we can kill it on exit
app.manage(SidecarHandle(std::sync::Mutex::new(Some(child))));

// 5) point the HttpClient at the chosen port (retire the hard-coded 9876)
app.state::<commands::AppState>()
    .client.set_base_url(format!("http://127.0.0.1:{port}"));

// 6) drain stdout for logs (optional)
tauri::async_runtime::spawn(async move {
    while let Some(ev) = rx.recv().await {
        if let CommandEvent::Stderr(b) | CommandEvent::Stdout(b) = ev {
            log::debug!("[py] {}", String::from_utf8_lossy(&b));
        }
    }
});

// 7) health-gate: poll /health, then emit service-ready for the UI
let handle = app.handle().clone();
tauri::async_runtime::spawn(async move {
    let state = handle.state::<commands::AppState>();
    for _ in 0..120 {                                  // ~2 min budget
        if state.client.check_health().await.is_ok() {
            let _ = handle.emit("service-ready", ());
            return;
        }
        tokio::time::sleep(std::time::Duration::from_millis(1000)).await;
    }
    let _ = handle.emit("service-failed", ());
});
```

`SidecarHandle` newtype + clean shutdown on app exit. In `run()` replace
`.run(...)` with the closure form and handle `ExitRequested`:

```rust
struct SidecarHandle(std::sync::Mutex<Option<CommandChild>>);

// …builder…
.build(tauri::generate_context!())
.expect("error building app")
.run(|app_handle, event| {
    if let tauri::RunEvent::ExitRequested { .. } = event {
        // best-effort graceful stop, then kill
        let st = app_handle.state::<commands::AppState>();
        let base = st.client_base_url();               // add a small getter
        let _ = std::process::Command::new("curl")     // or reqwest blocking
            .args(["-s", "-X", "POST", &format!("{base}/shutdown")])
            .output();
        if let Some(child) = app_handle.state::<SidecarHandle>().0.lock().unwrap().take() {
            let _ = child.kill();
        }
    }
});
```
> Notes:
> - The known **"URL cached at startup" bug** (LESSONS_LEARNED) disappears for
>   the packaged path because the URL is now derived from the spawned port, not
>   from `config.json`.
> - `child.kill()` on the `tauri-plugin-shell` `CommandChild` terminates the
>   PyInstaller launcher; with `--onedir` there's no temp-dir process tree to
>   orphan (the `--onefile` failure mode PACKAGING.md warns about).
> - The frontend should already gate on a `service-ready`/`service-failed`
>   event (PACKAGING.md Phase 4). Add an event listener in
>   `src/lib/tauri.ts` + a loading state if not present.

### 5.7 UI health-gate (frontend)

Listen for `service-ready` / `service-failed` and show "Starting transcription
engine…" until ready; disable record/transcribe until then (never fire into a
dead socket). This is the same as PACKAGING.md Phase 4 — reuse it.

### 5.8 Build the `.dmg`

```bash
npm install
npm run tauri build            # → src-tauri/target/release/bundle/dmg/Adversaria_0.1.0_aarch64.dmg
```
(With `targets: ["dmg","app"]` you also get the `.app` for quick local testing.)

---

## 6. ffmpeg bundling

mlx-whisper decodes audio by **shelling out to `ffmpeg`** (confirmed: PyPI
mlx-whisper lists ffmpeg as a prerequisite). Today that's `brew install ffmpeg`
on `PATH`. To remove that prerequisite:

1. **Get a static arm64 ffmpeg binary.** Easiest reproducible source: the
   evermeet.cx static builds, or `brew install ffmpeg && cp $(brew --prefix)/bin/ffmpeg`
   (note: Homebrew ffmpeg is *dynamically* linked against many brew libs — for a
   self-contained bundle prefer a **static** build). Put it at
   `src-tauri/resources/ffmpeg/ffmpeg` and `chmod +x`.
2. **Ship it as a Tauri resource** (already added in §5.4 `bundle.resources`).
3. **Point mlx-whisper at it via `PATH`** — done in the sidecar spawn env
   (§5.6 step 2/3): prepend the bundled `ffmpeg` dir to `PATH`. mlx-whisper /
   openai-whisper invoke `ffmpeg` by bare name, so a `PATH` entry is sufficient;
   no code change in `transcriber.py` needed.
4. **Verify:** in the built `.app`, transcribe a real WAV with **no Homebrew
   ffmpeg installed / PATH cleaned** — it must still decode.

> Static ffmpeg also needs the same signing treatment as any nested binary on a
> notarized build (§7). For the **ad-hoc** Phase-1 build, `--deep` ad-hoc sign
> covers it.

---

## 7. Signing & notarization

### 7.1 Minimum for a **personal** `.dmg` (Phase 1, no paid account)

You can ship and run an **unsigned** (or **ad-hoc-signed**) `.dmg` on your own
Macs. The catch is the quarantine attribute Gatekeeper adds to anything that
arrives via browser/AirDrop/`.dmg`, which triggers *"Adversaria is damaged and
can't be opened"* (the misleading message for unsigned/quarantined apps).

Two ways to make it run:

- **Ad-hoc sign the bundle before packaging** (recommended, deterministic):
  Tauri ad-hoc signs by default when no identity is set, but to be sure the
  nested sidecar + ffmpeg are covered, after `tauri build` you can re-sign:
  ```bash
  codesign --force --deep --sign - \
    "src-tauri/target/release/bundle/macos/Adversaria.app"
  ```
  Ad-hoc signatures are valid **on the machine that built them** without further
  steps; on *other* Macs the user still removes quarantine (next bullet).
- **Strip quarantine on the target Mac** (the universal personal-use escape
  hatch):
  ```bash
  xattr -dr com.apple.quarantine /Applications/Adversaria.app
  # or, before first launch, on the .dmg's mounted app
  ```
  After this the app launches normally. This is the **minimum** to get a
  personal `.dmg` running on your own Mac without the "damaged" error.

> Do **not** rely on `hardenedRuntime: true` for the *personal/unsigned* path —
> hardened runtime is meaningful only with a Developer ID signature +
> notarization. For Phase 1, you may leave `hardenedRuntime` off and skip the
> entitlements file. (Set them when you move to Phase 2.)

### 7.2 Path to a **distributable** `.dmg` (Phase 2, paid account)

Requires an **Apple Developer Program** membership ($99/yr) and a **Developer ID
Application** certificate. Then Tauri can sign + notarize during `tauri build`:

```bash
export APPLE_SIGNING_IDENTITY="Developer ID Application: Your Name (TEAMID)"
export APPLE_ID="you@example.com"
export APPLE_PASSWORD="app-specific-password"   # appleid.apple.com → App-Specific Passwords
export APPLE_TEAM_ID="TEAMID"
npm run tauri build            # Tauri signs the .app (+nested bins) and notarizes the .dmg
```
Set in `tauri.conf.json` `bundle.macOS`: `hardenedRuntime: true` and an
`Entitlements.plist` (WebView needs JIT entitlements:
`com.apple.security.cs.allow-jit`, `…allow-unsigned-executable-memory`).

**Known gotcha — externalBin + notarization (Tauri issue #11992):** with a
sidecar in `externalBin`, the bundler signs the sidecar first then re-signs the
main binary, which has produced *"The signature of the binary is invalid"* /
notarization rejections for some users. If you hit it:
- Ensure **every** nested Mach-O (sidecar launcher, PyInstaller `_internal/*.so`
  / `*.dylib`, bundled `ffmpeg`, mlx `.dylib`s) is signed with the **same
  Developer ID** and **hardened runtime**, *inner-to-outer*, before the outer
  `.app` is signed. A common fix is a post-build script that
  `codesign --force --options runtime --timestamp` each nested binary, then the
  `.app`, then submit to `notarytool`.
- Notarize manually if Tauri's inline flow fights you:
  ```bash
  xcrun notarytool submit Adversaria_0.1.0_aarch64.dmg \
    --apple-id "$APPLE_ID" --team-id "$APPLE_TEAM_ID" --password "$APPLE_PASSWORD" --wait
  xcrun stapler staple Adversaria_0.1.0_aarch64.dmg
  ```
- `altool` is **removed** from the notary service (since 2023-11-01) — use
  `notarytool` only.

### 7.3 Wiring into *our* `build-dmg.sh` (the planned Gate-1 change — blocked on enrollment, 2026-06-28)

`scripts/build-dmg.sh` currently signs with the self-signed **`NotchyPrompter Dev`**
(`ADVERSARIA_SIGN_IDENTITY`) — correct for **local** TCC-stable dev re-freezes, but
**not notarizable**. The distributable path (launch Gate 1) needs the Developer ID
cert from §7.2, then these changes, **gated on the Apple env vars so the dev path
keeps working** when they're absent:

1. **Sign + notarize via `tauri build` itself.** When `APPLE_SIGNING_IDENTITY` +
   `APPLE_ID` + `APPLE_PASSWORD` + `APPLE_TEAM_ID` are exported, run `tauri build`
   with them set so Tauri signs the `.app` (and every nested Mach-O — sidecar,
   PyInstaller `_internal/*.so`/`*.dylib`, mlx dylibs, ffmpeg) with the Developer ID
   under **hardened runtime**, then notarizes. Set `bundle.macOS.hardenedRuntime: true`
   + the existing `entitlements.plist` in `tauri.conf.json` (its
   `disable-library-validation` is the hardened-runtime exception those bundled
   dylibs need).
2. **This fixes Known-issue #1 (updater TCC reset) for free.** Today the updater
   `.app.tar.gz` is produced *during* `tauri build` from the **ad-hoc** app
   (`createUpdaterArtifacts`), *before* the line-61 `NotchyPrompter Dev` re-sign — so
   an auto-update ships an ad-hoc app and **resets mic/screen/calendar grants**.
   Signing with the Developer ID *at* `tauri build` means the tarball is built from
   the properly-signed app → no TCC reset. The post-build re-sign (lines 58–62)
   becomes a no-op for the Developer ID path and is skipped when the Apple env vars
   are present.
3. **Notarize the `.dmg` too**, after the `hdiutil` step (line 64):
   `xcrun notarytool submit Adversaria_aarch64.dmg --apple-id … --team-id … --password … --wait`
   then `xcrun stapler staple`. Verify the result on a **clean** machine:
   `spctl -a -vvv -t install Adversaria.app` → "accepted, source=Notarized Developer ID",
   and `xcrun stapler validate` on both the `.app` and the `.dmg`.
4. **Keep the `NotchyPrompter Dev` branch** for everyday local re-freezes (no Apple
   round-trip, TCC-stable) — selected when the Apple env vars are absent.

Make this change **with the cert in hand** so each step is verified against a real
notary submission, not blind. The founder's manual prerequisites (enroll → Developer
ID Application cert → app-specific password) — and the verified unblock checklist for
the "enrollment could not be completed" rejection — are tracked in [TODO.md](./TODO.md)
"Launch gates" → Gate 1.

**Post-enrollment gotchas (verified 2026-06-28 — don't get surprised after the account activates):**
- **The cert:** create the **Developer ID Application** cert at `developer.apple.com/account`
  (or via Xcode); only the **Account Holder** can (an Individual enrollee is, by default).
  Max **5** Developer ID Application certs ever; each valid **5 years**.
- **Back up the exported `.p12` + its password immediately** (password manager). You
  **cannot re-download** a Developer ID cert — losing the private key burns one of your 5.
- **Credentials for Tauri's notarize step:** an **app-specific password**
  (account.apple.com → Sign-In and Security — requires 2FA, NOT your Apple ID login
  password) **or** an App Store Connect API key, plus `APPLE_TEAM_ID` and the signing
  identity (`APPLE_SIGNING_IDENTITY`, or `APPLE_CERTIFICATE`+`APPLE_CERTIFICATE_PASSWORD`).
- **The second wall — notarization can still REJECT after enrollment succeeds.** Apple
  requires a valid Developer ID signature + **hardened runtime** + a **secure timestamp**
  + **no `get-task-allow` entitlement** + a recent SDK. Verify with `codesign -dvvv` (look
  for the `runtime` flag) before submitting. Separately, a freshly-enrolled team can hit
  **error 7000 "team is not yet configured for notarization"** — an Apple-side activation
  lag that may require *another* government-ID upload; reopen a support case if it persists.
- **`altool` is removed** (since 2023-11-01) — `notarytool` only. Tauri 2 uses it internally.

---

## 8. What stays a prerequisite (out of scope to bundle)

Confirmed stance — these remain user-installed, *not* in the `.dmg`:

1. **The LLM server (Rapid-MLX on macOS / Ollama elsewhere).** This is correct
   and intentional:
   - It's large and separately licensed; bundling a multi-GB model in a `.dmg`
     is impractical.
   - On macOS the summarizer talks to **Rapid-MLX** at `127.0.0.1:8000/v1`
     (`summarizer.py:51`), installed via
     `brew install raullenchai/rapid-mlx/rapid-mlx` (HANDOFF.md:139). Ollama is
     the equivalent elsewhere.
   - **Recommendation:** keep it a prerequisite. On launch, detect whether the
     LLM endpoint answers (`GET {LLM_BASE_URL}/models`) and, if not, show a
     first-run screen with the one-line install command + a "re-check" button
     (mirrors PACKAGING.md Phase 5, minus bundling). Do **not** spawn it.
2. **Model downloads happen at runtime, not in the `.dmg`:**
   - **MLX Whisper** weights (`whisper-large-v3-mlx`, ~1.5 GB) download to the
     HF cache on **first transcribe** (`transcriber.py:405-406`). Either accept
     a one-time first-recording delay or pre-warm during first-run setup.
   - The LLM model is pulled by Rapid-MLX/Ollama, outside our app.
   - These keep the `.dmg` to ~the app + PyInstaller payload + ffmpeg, not
     multi-GB.

---

## 9. Risks & gotchas

- **PyInstaller + mlx hidden imports / Metal lib (highest risk).** mlx ships a
  `.metallib` Metal kernel blob and numba JIT pieces PyInstaller can miss →
  runtime `ImportError`/missing-Metal-library. Mitigate with `collect_all("mlx")`
  / `collect_all("mlx_whisper")` / `collect_all("numba")` and **test the frozen
  binary in isolation** (run it from a clean shell, transcribe a real WAV)
  *before* wiring Tauri. (See §5.2.) This is the single most likely place the
  build "looks fine, isn't".
- **First-run model download.** First transcribe blocks while ~1.5 GB downloads;
  with this box's broken `hf_xet`, **must** pass `HF_HUB_DISABLE_XET=1` to the
  sidecar (§5.6) or it hangs at 0 bytes (known repo gotcha, LESSONS_LEARNED).
- **ffmpeg dynamic linking.** A Homebrew `ffmpeg` copied into the bundle drags
  brew dylibs and breaks on a clean Mac — use a **static** arm64 build (§6).
- **externalBin notarization (#11992).** Sidecars complicate Apple notarization;
  fine for ad-hoc Phase 1, needs the inner-to-outer signing care in §7.2 for
  Phase 2.
- **`--onefile` trap.** Don't use it: it unpacks the (large) ML payload to a
  temp dir each launch (slow) and is the classic orphan-process source. Use
  `--onedir` (matches PACKAGING.md).
- **Blackwell / CUDA is N/A on Mac.** All the Windows CUDA-DLL bundling concerns
  in PACKAGING.md do **not** apply here — macOS is pure MLX/Metal. Don't carry
  that complexity over.
- **mlx model size & app size.** The PyInstaller payload (mlx + faster-whisper
  fallback + uvicorn) is sizeable; the `.dmg` will be a few hundred MB before
  any model. Acceptable for Phase 1; consider dropping the faster-whisper
  fallback from the mac build later (requires guarding `transcriber.py:15`).
- **Window/identifier naming drift.** `productName` is still "Meeting Note
  Taker" while the brand is "Adversaria" — the `.dmg`/`.app` will be named
  "Meeting Note Taker" unless `productName` is updated. Decide before shipping
  (cosmetic, but user-visible).
- **Quarantine UX.** For the unsigned personal build, the user *will* hit the
  "damaged" dialog until they `xattr -dr com.apple.quarantine` (§7.1). Document
  this in the README for testers; it disappears once notarized (Phase 2).

---

## 10. Phased plan

### Phase 1 — Unsigned personal `.dmg` that launches the bundled sidecar (goal)

Get a double-clickable `.dmg` that works on the dev Mac, no Terminal at runtime.

1. **Service entrypoint + shutdown** → add `run_service.py` (`--port`) and
   `POST /shutdown` to `server.py`. *Verify:* `uv run python run_service.py
   --port 9999` serves `/health`; `curl -XPOST /shutdown` stops it cleanly.
2. **PyInstaller `--onedir`** → write `pyinstaller.spec`, build. *Verify:* run
   the frozen launcher from a **clean shell** (no venv), `GET /health` ok, and a
   **real WAV transcribes via MLX** (the metallib/hidden-import gate).
3. **ffmpeg** → drop a **static** arm64 `ffmpeg` in `resources/ffmpeg`.
   *Verify:* transcribe with Homebrew ffmpeg removed from PATH.
4. **Tauri wiring** → `externalBin` + `resources` + `targets:["dmg","app"]` in
   `tauri.conf.json`; `shell:allow-execute` (sidecar) in capabilities; place the
   `-aarch64-apple-darwin`-suffixed launcher in `src-tauri/bin/`.
5. **Rust spawn + health-gate + shutdown** → free-port pick, spawn with
   `HF_HUB_DISABLE_XET=1` + bundled-ffmpeg `PATH`, `set_base_url(port)`, poll
   `/health` → `service-ready`, kill child on `ExitRequested`. *Verify:* `cargo
   check`; `npm run tauri dev` reaches the auto-spawned service.
6. **UI loading state** → listen for `service-ready`/`service-failed`. *Verify:*
   cold launch shows loading → ready, no error toast.
7. **`npm run tauri build`** → ad-hoc sign (`codesign --force --deep --sign -`).
   *Verify (definition of done §1):* on the dev Mac, open the `.dmg`
   (`xattr -dr com.apple.quarantine` if needed), record → transcribe →
   summarize (with Rapid-MLX running), quit → **no leftover sidecar, port free**.

### Phase 2 — Distributable signed + notarized `.dmg`

8. Enroll in Apple Developer Program; create a **Developer ID Application** cert.
9. Set `hardenedRuntime: true` + `Entitlements.plist` (JIT for WebView); export
   `APPLE_*` env; `npm run tauri build`. Handle #11992 (inner-to-outer signing)
   if notarization rejects. *Verify:* `spctl -a -vv Adversaria.app` →
   "accepted, source=Notarized Developer ID"; opens on a **second** Mac with no
   quarantine step.

### Phase 3 (later) — First-run polish

10. Detect the LLM server on launch; first-run screen with the `brew install`
    command + re-check (don't bundle). Optional: pre-warm the MLX Whisper model
    download with a progress bar instead of a silent first-transcribe delay.

---

## Sources (verified 2026-06-20)

- Tauri 2 — Embedding External Binaries (externalBin, target-triple suffix,
  `shell:allow-execute` sidecar, Rust `shell().sidecar()` spawn pattern):
  https://v2.tauri.app/develop/sidecar/
- Tauri 2 — Configuration reference (bundle targets/resources):
  https://v2.tauri.app/reference/config/
- Tauri 2 — macOS code signing & notarization (`APPLE_*`, hardenedRuntime,
  entitlements, notarytool): https://v2.tauri.app/distribute/sign/macos/
- Tauri issue #11992 — externalBin codesign/notarization breakage on macOS:
  https://github.com/tauri-apps/tauri/issues/11992
- PyInstaller 6.21 docs / changelog (stable; 6.20.0 = 2026-04-22):
  https://pyinstaller.org/en/stable/ ,
  https://pyinstaller.org/en/stable/CHANGES.html
- PyInstaller + FastAPI/uvicorn hidden-imports pattern (entrypoint runs
  `uvicorn.run`): https://github.com/iancleary/pyinstaller-fastapi ,
  https://github.com/K-RT-Dev/fastapi-pyinstaller
- mlx-whisper 0.4.3 (2025-08-29) — requires ffmpeg, downloads models from HF at
  runtime: https://pypi.org/project/mlx-whisper/
- MLX Metal-library packaging (the `.metallib` must travel with the binary):
  https://github.com/ml-explore/mlx-swift/issues/345
- macOS ad-hoc signing + quarantine ("damaged"/"can't be opened") personal-use
  fix (`codesign --force --deep --sign -`, `xattr -dr com.apple.quarantine`):
  https://developer.apple.com/forums/thread/676584 ,
  https://gist.github.com/rsms/929c9c2fec231f0cf843a1a746a416f5
- Rust ephemeral free-port (`TcpListener::bind("127.0.0.1:0")` + `local_addr`):
  https://doc.rust-lang.org/std/net/struct.TcpListener.html
- Packaging-tool landscape 2026 (PyInstaller vs Briefcase/py2app/uv for ML):
  https://briefcase.beeware.org/ , https://realpython.com/pyinstaller-python/
- Rapid-MLX (OpenAI-compatible local LLM for Apple Silicon — stays a
  prerequisite): https://github.com/raullenchai/Rapid-MLX

---

*Companion docs:* [PACKAGING.md](./PACKAGING.md) (Windows/NSIS path + shared
sidecar/health/shutdown rationale), [DECISIONS.md](./DECISIONS.md) (ADR-010
macOS port), [HANDOFF.md](./HANDOFF.md) (macOS dev runbook + prerequisites),
[LESSONS_LEARNED.md](./LESSONS_LEARNED.md) (`HF_HUB_DISABLE_XET` gotcha).
*Created 2026-06-20.*
