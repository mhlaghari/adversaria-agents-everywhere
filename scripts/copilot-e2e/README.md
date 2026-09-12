# E1a Service Replay Harness (`scripts/copilot-e2e/replay.py`)

This harness drives synthetic `/live_feed` audio chunks and `/copilot_answer_stream` SSE requests to benchmark service continuity, streaming responsiveness, and contract bounds for Realtime Copilot v2.

## Important: Scope & Non-Goals

- **Service-Only:** E1a verifies the Python sidecar endpoints under delta load. It **does not** exercise or claim coverage for native macOS CoreAudio capture, Rust detector heuristics, local SQLite/FTS retrieval, card persistence, or frontend companion UI. Those are covered under E1b / E3 / E4.
- **Question Detection is Out of Scope:** Rust sentence-level question detection is native-only. In E1a, `tag_question` audio is fed to test ingestion, but detection is explicitly recorded as `not_applicable_service_only` and never reported as a detector pass or answered card.
- **Rapid-Pair Backpressure is Native-Only:** In E1a, `rapid_pair` tests sequential answer streaming for both distinct questions (Q1 and Q2) to verify service throughput. Queue backpressure (1-active, 1-waiting latest-wins replacement) is native-only and not proven by service replay.
- **Pre-flight Engine Safety:** The harness tests local engine readiness via a safe probe to `/copilot_answer_stream`. If the service is uninitialized (HTTP 503) or the engine is unreachable, it records an overall structured skip rather than producing cascading test failures. No models are ever downloaded.
- **Feed Continuity Accounting:** A case demonstrates feed continuity only if at least one background `/live_feed` call succeeds during the active answer stream and zero background calls fail. Foreground feed errors immediately fail a case.
- **Privacy & Safety:** The harness permits only loopback addresses (`127.0.0.1`, `localhost`, `::1`) and disables redirects and environment proxies. It accepts an operator-supplied manifest path, so using the bundled invented manifest is an operating requirement rather than an enforced file-path restriction.
- **Invented Fixtures:** Run acceptance only with the synthetic scenarios in `python-service/tests/fixtures/copilot/manifest.json`. Do not supply live meetings, personal notes, or proprietary knowledge.

## Prerequisites

- Python 3.12+ (standard library only; no external packages required).
- macOS built-in command-line tools for local audio synthesis:
  - `/usr/bin/say` (speech synthesis)
  - `/usr/bin/afconvert` (audio format conversion to 16 kHz 16-bit mono PCM WAV)
- A running Python sidecar instance on loopback (e.g., `http://127.0.0.1:9876`), or use `--dry-run`.

## Usage

### 1. Dry Run (Offline Simulation)
Runs the harness without connecting to any network socket or local service, verifying the manifest, telemetry structure, and calculations. Dry-run metrics are explicitly labeled as `simulated` and separated from measured acceptance counts:
```bash
python3 scripts/copilot-e2e/replay.py --dry-run --output .recon/realtime-copilot-20260905/e1a-dry-run.json
```

### 2. Live Service Replay
Execute against an active local service:
```bash
python3 scripts/copilot-e2e/replay.py \
  --service-url http://127.0.0.1:9876 \
  --llm-base-url http://127.0.0.1:11434 \
  --model qwen3.5:4b \
  --manifest python-service/tests/fixtures/copilot/manifest.json \
  --output .recon/realtime-copilot-20260905/e1a-results.json
```

The example uses the always-registered default Ollama endpoint. Pass the exact app-registered loopback URL instead when replaying against managed Ollama or Rapid-MLX.

If the service is unavailable or the local model is uninitialized, the script writes a structured skipped result with a precise reason without failing or attempting to download any model.

### CLI Options

| Argument | Default | Description |
|---|---|---|
| `--service-url` | `http://127.0.0.1:9876` | Loopback base URL of the Python service |
| `--manifest` | `python-service/tests/fixtures/copilot/manifest.json` | Path to synthetic fixture JSON manifest |
| `--output` | `.recon/realtime-copilot-20260905/e1a-results.json` | Path where JSON report is written |
| `--model` | `None` | Exact Local model id; required once the service is reachable so measured results are reproducible |
| `--llm-base-url` | `http://127.0.0.1:11434` | Registered local endpoint; override with the exact app-managed Ollama or Rapid-MLX loopback URL |
| `--llm-api-key-env` | `None` | Environment variable name holding local key (redacted from output) |
| `--cadence-ms` | `500` | Cadence interval between `/live_feed` chunks in milliseconds (must be > 0) |
| `--warmup` | `False` | Sends a short warmup audio chunk to /live_feed prior to testing (does not warm the LLM answer model, which is probed separately) |
| `--dry-run` | `False` | Executes offline simulation without hitting network sockets |
