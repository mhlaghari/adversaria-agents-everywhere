# The Terminal Handoff — Adversaria (adversaria-terminal)

For picking up the TUI/CLI workstream cold. Read CLAUDE.md first, then this.

## Current state (2026-09-12)

**Green wall, work is runnable.** All tests pass, lint is clean, and every CLI
subcommand works against the live local service on `127.0.0.1:9876`.

```
cd terminal
uv run pytest -q        # 37 tests, ML deps stubbed, <2s
uv run ruff check src tests
uv run advterm --version / health / list / models / templates / list-models  # live-service smoke ✓
```

The service is running but **degraded**: no Whisper model downloaded yet
(`health` → transcriber "missing"), Ollama OK. `advterm import` degrades
gracefully ("No transcription model is downloaded yet.", exit 1, no orphan
row). Everything until a model is pulled must keep failing to the user clearly.

## What the terminal is

Second presentation surface for Meeting Note Taker: Textual TUI (`advterm`)
plus one-shot CLI subcommands, reusing the Python ML service on :9876 with its
own SQLite history in the OS app-data dir (`store.py`). Reuses nothing from the
desktop frontend or Rust backend; pure Python (textual + httpx + soundcard).

## Last session fixes (2026-09-12)

- **`test_boot_and_navigate` crash root cause:** `MeetingsScreen._render(self,
  query)` overrode Textual's reserved `Widget._render()`. The compositor called
  it with no args during painting, it executed the table-rebuild and returned
  `None`, so `visualize(None)` blew up in `render_strips`. Renamed to
  `_populate` (screens/meetings.py).
- **Dead bindings:** dashboard declared `ctrl+t/i/e/l/s` → actions
  `todos/import/templates/models/settings` that never existed, so those keys
  did nothing. Centralized all nav actions + bindings in `BaseScreen`
  (screens/base.py), removed the dashboard duplicates, and added matching
  App-level `go_*` bindings (app.py) so they work from any screen.
- **Linted:** first `ruff check` run surfaced 76 findings. Auto-fixed unused
  imports, import sorting, `collections.abc`, `__all__` sorting. Removed
  redundant `int(round(...))` (RUF046) and an unused test var (F841) in code.
  Deliberate patterns (`BLE001` boundary catches, `DTZ005/6` local-time display,
  `S110` soundcard fallback, `RUF012` Textual `BINDINGS`) are documented and
  ignored in `pyproject.toml` `[tool.ruff.lint]`.

## Gotchas caught along the way

- `@work(thread=False)` async workers run on the app thread — `call_from_thread`
  raises there; use `await asyncio.to_thread(...)` (all screens now do).
- `pilot.press()` is async in textual 8.2.8 — `await` it.
- Duplicate widget ids crash. (v1 had `#detail-meta` twice.)
- App must push `DashboardScreen` in `on_mount`.
- Don't name any method `_render` — it's declared on `Widget` and the compositor
  calls it with no args.
- Migrate shell tests use `pytest.mark.anyio` (anyio plugin ships the pytest
  entry point; pytest-asyncio is not installed).

## Screens

`dashboard` (status cards + quick actions), `record` (dual capture + live
captions), `meetings` (filterable table), `detail` (Notes/Transcript/To-dos
tabs, Ask with template picker, re-summarize, retry, export, delete),
`ask`, `todos`, `templates`, `models` (download), `settings`, `import`.

## Next steps

1. Download a Whisper model (`uv run advterm download-model <key>`) once the
   founder okays a multi-GB model — then a real record/transcribe/summarize
   round-trip is the remaining unverified path (esp. `avatar_record`'s
   unlink-after-retry path and live-caption flow against a real meeting).
2. Second TUI smoke test for `import` + `detail` retry with a `needs_transcribe`
   meeting (currently only CLI-import and dashboard/meetings/detail-nav are
   covered).
3. Decide whether `ruff format` should be enforced repo-wide (currently not;
   only `ruff check`).