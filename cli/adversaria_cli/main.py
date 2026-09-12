"""Command entry point and interactive recording companion."""

from __future__ import annotations

import argparse
import getpass
import json
import os
import shlex
import shutil
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from . import __version__
from .audio import Recorder, devices
from .config import CliError, Config, atomic_text
from .copilot import Copilot
from .engine import INSTRUCTIONS, Engine
from .research import search
from .store import Store
from .ui import render_stream, say, show_markdown, table


def add_model_options(parser):
    parser.add_argument("--provider", choices=("openrouter", "codex", "openai"))
    parser.add_argument("--model", help="Exact model ID, or auto")


def parser():
    p = argparse.ArgumentParser(
        prog="adversaria", description="Listen. Remember. Do the work — in your terminal."
    )
    p.add_argument("--version", action="version", version=__version__)
    p.add_argument("--home", help="Isolated CLI data directory (also ADVERSARIA_CLI_HOME)")
    sub = p.add_subparsers(dest="command")
    sub.add_parser("tui", help="Full-screen meeting dashboard (default)")
    sub.add_parser("tmux", help="Open the dashboard in a persistent tmux session")
    sub.add_parser("shell", help="Command-based meeting companion")
    sub.add_parser("doctor", help="Check cloud configuration, credentials and devices")
    sub.add_parser("setup", help="Configure OpenRouter and Exa; use your installed Codex login")
    demo = sub.add_parser("demo", help="Add prepared sample tasks and outputs; no provider calls")
    demo.add_argument("--workspace", help="Target workspace; defaults to the current workspace")
    auth = sub.add_parser("auth", help="Save a key via a hidden prompt")
    auth.add_argument("provider", choices=("openai", "openrouter", "exa"))
    auth.add_argument(
        "--stdin",
        action="store_true",
        help="Read a key from stdin; never put keys in command arguments",
    )
    models = sub.add_parser("models", help="Discover and choose cloud models")
    ms = models.add_subparsers(dest="action")
    ml = ms.add_parser("list")
    ml.add_argument("--provider", choices=("openrouter", "codex", "openai"), default="openrouter")
    ml.add_argument("--filter", default="")
    ml.add_argument("--json", action="store_true")
    mu = ms.add_parser("use")
    mu.add_argument("provider", choices=("openrouter", "codex", "openai"))
    mu.add_argument("model", nargs="?", default="auto")
    speech = ms.add_parser("speech", help="View or change transcription providers and models")
    speech.add_argument("--provider", choices=("openrouter", "openai"))
    speech.add_argument("--router-model")
    speech.add_argument("--list", action="store_true")
    speech.add_argument("--file-model")
    speech.add_argument("--live-model")
    sub.add_parser("devices", help="List microphone and loopback inputs")
    rec = sub.add_parser("record", help="Record with live captions; Ctrl-C stops and saves")
    rec.add_argument("--device", type=int)
    rec.add_argument("--system-device", type=int, help="Optional loopback INPUT ID from devices")
    rec.add_argument("--duration", type=float, help="Stop after this many seconds")
    rec.add_argument("--workspace")
    rec.add_argument("--title", default="Terminal recording")
    rec.add_argument(
        "--copilot", action="store_true", help="Generate suggestions on detected questions"
    )
    add_model_options(rec)
    tr = sub.add_parser("transcribe", help="Transcribe audio using your cloud speech provider")
    tr.add_argument("file")
    tr.add_argument("--mic", help="Optional separate microphone audio track")
    tr.add_argument("--workspace")
    tr.add_argument("--title")
    tr.add_argument("--summarize", action="store_true")
    add_model_options(tr)
    me = sub.add_parser("meetings", help="List, read, summarize or export saved meetings")
    mes = me.add_subparsers(dest="action")
    mel = mes.add_parser("list")
    mel.add_argument("--workspace")
    for action in ("show", "summarize", "export"):
        child = mes.add_parser(action)
        child.add_argument("id", type=int)
        if action == "summarize":
            add_model_options(child)
        if action == "export":
            child.add_argument("file")
    ws = sub.add_parser("workspace", help="Create workspaces, attach context and control agents")
    wss = ws.add_subparsers(dest="action")
    wss.add_parser("list")
    for action in ("create", "use", "pause", "resume"):
        child = wss.add_parser(action)
        child.add_argument("name")
    att = wss.add_parser("attach")
    att.add_argument("file")
    att.add_argument("--workspace")
    ins = wss.add_parser("instructions")
    ins.add_argument("text")
    ins.add_argument("--workspace")
    for name in ("ask", "suggest"):
        ask = sub.add_parser(name, help="Stream a grounded answer from a workspace")
        ask.add_argument("question")
        ask.add_argument("--workspace")
        ask.add_argument(
            "--web",
            action=argparse.BooleanOptionalAction,
            default=None,
            help="Force Exa lookup, or --no-web to disable it; outside questions search automatically",
        )
        add_model_options(ask)
    research = sub.add_parser("search", help="Search Exa and return cited source excerpts")
    research.add_argument("query")
    research.add_argument("--count", type=int, choices=range(1, 11), default=5)
    research.add_argument("--json", action="store_true")
    task = sub.add_parser("task", help="Create, run and review workspace tasks")
    ts = task.add_subparsers(dest="action")
    tl = ts.add_parser("list")
    tl.add_argument("--workspace")
    ta = ts.add_parser("add")
    ta.add_argument("title")
    ta.add_argument("--kind", choices=tuple(INSTRUCTIONS), default="write")
    ta.add_argument("--details", default="")
    ta.add_argument("--workspace")
    ta.add_argument("--web", action="store_true", help="Use Exa when this task runs")
    ta.add_argument("--run", action="store_true")
    add_model_options(ta)
    for name in ("show", "run", "approve", "revise", "artifact", "preview", "retry", "recover"):
        child = ts.add_parser(name)
        child.add_argument("id", type=int)
        if name == "run":
            add_model_options(child)
        if name == "artifact":
            child.add_argument("--raw", action="store_true")
        if name == "preview":
            child.add_argument(
                "--no-open", action="store_true", help="Save HTML without opening a browser"
            )
    work = sub.add_parser("work", help="Run queued tasks in order (optionally stay watching)")
    work.add_argument("--workspace")
    work.add_argument("--watch", action="store_true")
    add_model_options(work)
    replay = sub.add_parser(
        "replay", help="Feed a transcript through the live detector; does not auto-approve"
    )
    replay.add_argument("file")
    replay.add_argument("--workspace")
    replay.add_argument("--copilot", action="store_true")
    add_model_options(replay)
    return p


def model_notice(config, provider=None, model=None):
    provider, model = config.selection(provider, model)
    say(
        f"Model · {provider} / {model}"
        + (
            " · uses your Codex login"
            if provider == "codex"
            else f" · sends supplied text/context to {provider}"
        ),
        "dim",
    )


def doctor(config):
    rows = [
        {"part": "LLM", "status": config.values["provider"], "detail": config.values["model"]},
        {
            "part": "Speech",
            "status": config.values["speech_provider"],
            "detail": config.values["openrouter_speech_model"]
            if config.values["speech_provider"] == "openrouter"
            else config.values["live_model"],
        },
    ]
    for name in ("openai", "openrouter", "exa"):
        if name == "openai" and "openai" not in {
            config.values["provider"],
            config.values["speech_provider"],
        }:
            continue
        rows.append(
            {
                "part": name,
                "status": "key configured (not validated)" if config.key(name) else "no key",
                "detail": f"auth {name}",
            }
        )
    try:
        rows.append({"part": "Audio inputs", "status": str(len(devices())), "detail": "devices"})
    except (CliError, OSError):
        rows.append(
            {
                "part": "Audio inputs",
                "status": "unavailable",
                "detail": "Check PortAudio / microphone access",
            }
        )
    rows.append({"part": "Storage", "status": "CLI only", "detail": str(config.directory)})
    rows.append(
        {
            "part": "Codex",
            "status": "installed" if shutil.which("codex") else "optional",
            "detail": "Uses codex login; no separate API key",
        }
    )
    rows.append(
        {
            "part": "ffmpeg",
            "status": "installed" if shutil.which("ffmpeg") else "optional",
            "detail": "Used for audio files over 24 MB",
        }
    )
    table(rows, [("Component", "part"), ("Status", "status"), ("Detail", "detail")])
    selected = config.values["provider"]
    return (
        0
        if config.key(config.values["speech_provider"])
        and (shutil.which("codex") if selected == "codex" else config.key(selected))
        else 1
    )


def run_and_report(engine, task_id, provider=None, model=None):
    model_notice(engine.config, provider, model)
    say(f"Running task {task_id}…", "cyan")
    render_stream(engine.run_task(task_id, provider, model))
    say(f"Draft ready · task {task_id} · {engine.store.artifact(task_id)}", "green")
    say(f"Review: task artifact {task_id} → task approve {task_id}", "dim")


def execute(args, config, store, engine):
    cmd = args.command
    if cmd == "tmux":
        if not os.environ.get("TMUX"):
            executable = shutil.which("tmux")
            if not executable:
                raise CliError(
                    "tmux is not installed. Run adversaria for the same boxed dashboard."
                )
            command = shlex.join(
                [sys.executable, "-m", "adversaria_cli", "--home", str(config.directory), "tui"]
            )
            return subprocess.run(
                [executable, "new-session", "-A", "-s", "adversaria", command], check=False
            ).returncode
        cmd = "tui"
    if cmd in {None, "tui"}:
        if not sys.stdin.isatty() or not sys.stdout.isatty():
            if cmd == "tui":
                raise CliError("The dashboard needs an interactive terminal. Run adversaria there.")
            parser().print_help()
            return 0
        from .dashboard import Dashboard

        if Dashboard(config, store, engine).run() == "shell":
            Shell(config, store, engine).loop()
        return 0
    if cmd == "doctor":
        return doctor(config)
    if cmd == "demo":
        from .demo import seed_demo

        workspace, tasks = seed_demo(config, store, args.workspace)
        say(f"Prepared demo fixtures in {workspace['name']}. No API calls were made.")
        table(tasks, [("ID", "id"), ("Task", "title"), ("State", "status")])
        say(
            "Open the dashboard, select this workspace with W, and press T. "
            "Enter reads a task; V approves; E revises. G starts a real provider run."
        )
        return 0
    if cmd == "auth":
        value = (
            sys.stdin.readline().strip()
            if args.stdin
            else getpass.getpass(f"{args.provider} API key (hidden): ")
        )
        config.save_key(args.provider, value)
        say(f"Saved {args.provider} key in {config.directory} (owner-only file).")
    elif cmd == "setup":
        say(
            "OpenRouter transcribes speech and generates answers. Exa researches queries. Codex can run tasks using your existing login.\nKeys are stored in owner-only files outside the repo; press Enter to keep/skip a key."
        )
        for provider in ("openrouter", "exa"):
            value = getpass.getpass(f"{provider} API key (hidden): ").strip()
            if value:
                config.save_key(provider, value)
        config.save(provider="openrouter", model="auto", speech_provider="openrouter")
        return doctor(config)
    elif cmd == "devices":
        table(
            devices(),
            [
                ("ID", "id"),
                ("Input device", "name"),
                ("Channels", "inputs"),
                ("Rate", "sample_rate"),
            ],
        )
    elif cmd == "models":
        action = args.action or "list"
        if action == "list":
            rows = engine.models.catalog(getattr(args, "provider", "openrouter"))
            rows = [r for r in rows if getattr(args, "filter", "").lower() in r["id"].lower()]
            if getattr(args, "json", False):
                print(json.dumps(rows, indent=2))
            else:
                table(
                    rows,
                    [
                        ("Model", "id"),
                        ("Context", "context"),
                        ("Input $/M", "input_per_million"),
                        ("Output $/M", "output_per_million"),
                    ],
                )
        elif action == "use":
            if (
                args.provider != "codex"
                and args.model != "auto"
                and args.model not in {r["id"] for r in engine.models.catalog(args.provider)}
            ):
                raise CliError(
                    "Model ID is not in the live text-model catalog. Run models list to choose one."
                )
            config.save(provider=args.provider, model=args.model)
            model_notice(config)
        elif action == "speech":
            changes = {}
            if args.provider:
                changes["speech_provider"] = args.provider
            if args.router_model:
                changes["openrouter_speech_model"] = args.router_model
            if args.file_model:
                changes["transcription_model"] = args.file_model
            if args.live_model:
                changes["live_model"] = args.live_model
            if changes:
                config.save(**changes)
            if args.list:
                from .transport import request

                rows = request(
                    "GET",
                    "https://openrouter.ai/api/v1/models?output_modalities=transcription",
                    timeout=20,
                ).get("data", [])
                table(rows, [("Speech model", "id")])
            if config.values["speech_provider"] == "openrouter":
                say(f"OpenRouter speech · {config.values['openrouter_speech_model']}")
            else:
                say(
                    f"OpenAI file · {config.values['transcription_model']}\nOpenAI live · {config.values['live_model']}"
                )
    elif cmd == "workspace":
        action = args.action or "list"
        if action == "list":
            table(
                store.rows("SELECT * FROM workspaces ORDER BY name"),
                [("ID", "id"), ("Workspace", "name"), ("Paused", "paused")],
            )
        elif action in {"create", "use", "pause", "resume"}:
            ws = store.workspace(args.name)
            if action in {"create", "use"}:
                config.save(workspace=ws["name"])
            else:
                store.configure_workspace(ws["id"], paused=action == "pause")
            say(f"Workspace {ws['name']} · {action}")
        elif action == "attach":
            ws = engine.workspace(args.workspace)
            store.attach(ws["id"], args.file)
            say(f"Attached {Path(args.file).name} to {ws['name']}.")
        elif action == "instructions":
            store.configure_workspace(
                engine.workspace(args.workspace)["id"], instructions=args.text
            )
            say("Workspace instructions saved.")
    elif cmd == "transcribe":
        say(f"Transcribing · uploads audio to {config.values['speech_provider']}…", "cyan")
        mid, data = engine.transcribe(args.file, args.workspace, args.title, args.mic)
        say(data["text"])
        say(f"Saved meeting {mid}", "green")
        if args.summarize:
            model_notice(config, args.provider, args.model)
            render_stream(engine.summarize(mid, args.provider, args.model))
    elif cmd == "meetings":
        action = args.action or "list"
        if action == "list":
            ws = engine.workspace(getattr(args, "workspace", None))
            table(
                store.rows(
                    "SELECT id,title,created FROM meetings WHERE workspace_id=? ORDER BY id DESC",
                    (ws["id"],),
                ),
                [("ID", "id"), ("Meeting", "title"), ("Date", "created")],
            )
        elif action == "summarize":
            model_notice(config, args.provider, args.model)
            render_stream(engine.summarize(args.id, args.provider, args.model))
        else:
            m = store.get_meeting(args.id)
            content = f"# {m['title']}\n\n{m['summary']}\n\n## Transcript\n\n{m['transcript']}\n"
            if action == "show":
                show_markdown(content)
            else:
                path = Path(args.file).expanduser().resolve()
                if path.exists():
                    raise CliError("Export target exists; choose a new filename.")
                atomic_text(path, content)
                say(f"Exported {path}")
    elif cmd in {"ask", "suggest"}:
        model_notice(config, args.provider, args.model)
        if args.web:
            say("Research · sends this question to Exa", "dim")
        render_stream(
            engine.answer(
                args.question,
                args.workspace,
                provider=args.provider,
                model=args.model,
                web=args.web,
                on_status=lambda status: say(status, "dim") if status != "Thinking…" else None,
            )
        )
    elif cmd == "search":
        results = search(config, args.query, args.count)
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            for i, row in enumerate(results, 1):
                say(f"[{i}] {row['title']}\n{row['url']}", "cyan")
                say(row["text"][:1200])
            if not results:
                say("No results returned.")
    elif cmd == "task":
        action = args.action or "list"
        if action == "list":
            ws = engine.workspace(getattr(args, "workspace", None))
            table(
                store.rows(
                    "SELECT id,kind,status,title FROM tasks WHERE workspace_id=? ORDER BY id DESC",
                    (ws["id"],),
                ),
                [("ID", "id"), ("Kind", "kind"), ("Status", "status"), ("Task", "title")],
            )
        elif action == "add":
            tid = store.add_task(
                engine.workspace(args.workspace)["id"],
                args.title,
                args.kind,
                args.details,
                args.web,
            )
            say(f"Queued task {tid} · {args.kind}", "green")
            if args.run:
                run_and_report(engine, tid, args.provider, args.model)
        elif action == "show":
            say(json.dumps(store.task(args.id), indent=2))
            table(
                store.rows(
                    "SELECT id,status,error,usage FROM runs WHERE task_id=? ORDER BY id DESC",
                    (args.id,),
                ),
                [("Run", "id"), ("Status", "status"), ("Error", "error"), ("Usage", "usage")],
            )
        elif action == "run":
            run_and_report(engine, args.id, args.provider, args.model)
        elif action == "preview":
            from .preview import open_preview

            path = open_preview(store, args.id, launch=not args.no_open)
            say(f"Local preview: {path}")
        elif action in {"approve", "revise"}:
            store.review(args.id, action == "approve")
            say(f"Task {args.id} · {'done' if action == 'approve' else 'queued for revision'}")
        elif action == "retry":
            store.retry(args.id)
            say(f"Task {args.id} queued. Run task run {args.id}.")
        elif action == "recover":
            store.recover(args.id)
            say(
                f"Task {args.id} marked failed. Retry only after the old worker process has stopped."
            )
        elif action == "artifact":
            content = store.artifact(args.id).read_text()
            say(content) if args.raw else show_markdown(content)
    elif cmd == "work":
        ws = engine.workspace(args.workspace)
        while True:
            rows = store.rows(
                "SELECT t.id FROM tasks t JOIN workspaces w ON w.id=t.workspace_id "
                "WHERE t.workspace_id=? AND t.status='queued' AND w.paused=0 ORDER BY t.id LIMIT 1",
                (ws["id"],),
            )
            if rows:
                run_and_report(engine, rows[0]["id"], args.provider, args.model)
            elif args.watch:
                time.sleep(1)
            else:
                break
    elif cmd in {"shell", None, "record", "replay"}:
        shell = Shell(config, store, engine)
        try:  # multi-pane record/replay screen (TTY only; ADVERSARIA_PLAIN=1 disables)
            from .tui import attach

            attach(shell, cmd)
        except (ImportError, OSError, RuntimeError) as exc:
            say(f"Live pane unavailable: {exc}. Continuing with plain output.", "yellow")
        if cmd == "record":
            return shell.record_command(args)
        if cmd == "replay":
            shell.workspace = args.workspace or shell.workspace
            shell.provider, shell.model = config.selection(args.provider, args.model)
            shell.ai = args.copilot
            shell.replay(args.file)
            if sys.stdin.isatty():
                shell.loop()
            else:
                shell.close()
        else:
            shell.loop()
    return 0


class Shell:
    def __init__(self, config, store, engine):
        self.config, self.store, self.engine = config, store, engine
        self.copilot = Copilot()
        self.commitment_workspaces = {}
        self.workspace = config.values["workspace"]
        self.provider, self.model = config.selection()
        self.ai = True
        self.recorder = None
        self.record_title = "Terminal recording"
        self.record_workspace = self.workspace
        self.pool = ThreadPoolExecutor(max_workers=1, thread_name_prefix="adversaria")
        self.futures = []
        self.lock = threading.RLock()

    def job(self, function, *args):
        self.futures = [f for f in self.futures if not f.done()]
        if len(self.futures) >= 8:
            say("Agent queue is full. Task stays queued; use work to run it later.", "yellow")
            return

        def run():
            try:
                function(*args)
            except (CliError, OSError, ValueError) as exc:
                say(f"Error · {exc}", "red")

        self.futures.append(self.pool.submit(run))

    def caption(self, text, source="Me", boundary="silence"):
        if text.strip():
            say(f"{source} › {text}")
        with self.lock:
            caught, question = self.copilot.feed(text, source, boundary)
            turns = list(self.copilot.turns)
        if caught:
            self.commitment_workspaces[caught.id] = (
                self.record_workspace if self.recorder else self.workspace
            )
            say(
                f"CAUGHT {caught.id} · {caught.kind} · {caught.deadline or 'no deadline'}\n  {caught.text}\n  approve {caught.id}  ·  dismiss {caught.id}",
                "yellow",
            )
        if question and self.ai:
            self.job(self.answer, question, turns, self.workspace, self.provider, self.model)

    def answer(self, question, turns, workspace, provider, model, web=None):
        # Each job owns its model client/usage, preventing shared receipts across jobs.
        engine = Engine(self.config, self.store)
        say(f"SUGGESTION · {question}", "cyan")
        model_notice(self.config, provider, model)
        render_stream(
            engine.answer(
                question,
                workspace,
                turns,
                provider,
                model,
                web,
                on_status=lambda status: say(status, "dim") if status != "Thinking…" else None,
            )
        )

    def replay(self, file):
        path = Path(file).expanduser()
        text = path.read_text()
        for line in text.splitlines():
            if not line.strip():
                continue
            source, sep, content = line.partition(":")
            self.caption(
                content.strip() if sep and source in {"Me", "Them"} else line,
                source if sep and source in {"Me", "Them"} else "Me",
            )
        mid = self.store.meeting(self.engine.workspace(self.workspace)["id"], path.stem, text)
        say(f"Saved transcript as meeting {mid}. Commitments remain unsaved until approve.", "dim")

    def start_recording(self, device=None, system_device=None, title="Terminal recording"):
        if self.recorder:
            raise CliError("A recording is already active. Use stop first.")
        old_commitments = self.copilot.commitments
        self.copilot = Copilot()
        self.copilot.commitments = old_commitments
        self.record_workspace = self.workspace
        recorder = Recorder(
            self.config, self.caption, lambda text: say(text, "yellow"), device, system_device
        )
        say(
            f"Live transcription · sends captured audio to {self.config.values['speech_provider']}",
            "dim",
        )
        recorder.start()
        self.recorder = recorder
        self.record_title = title
        say(
            "● Recording · microphone"
            + (" + loopback input" if system_device is not None else "")
            + " · stop to transcribe and save",
            "green",
        )

    def stop_recording(self):
        if not self.recorder:
            raise CliError("No recording is active.")
        recorder = self.recorder
        say("Stopping capture and flushing the final caption…", "cyan")
        recorder.stop()
        self.recorder = None
        try:
            text = "\n".join(line for _, line in sorted(recorder.transcript))
            mid = self.store.meeting(
                self.engine.workspace(self.record_workspace)["id"],
                self.record_title + (" [partial]" if recorder.errors else ""),
                text,
            )
            say(f"Saved meeting {mid}. Use meetings summarize {mid} for notes.", "green")
            if recorder.errors:
                say(
                    f"Some audio could not be transcribed live. Full audio preserved at {recorder.directory}; use transcribe FILE to recover.",
                    "yellow",
                )
            else:
                recorder.cleanup()
        except (CliError, OSError) as exc:
            raise CliError(
                f"{exc} Audio preserved at {recorder.directory}; retry with transcribe FILE."
            ) from exc

    def approve(self, words):
        if len(words) < 2:
            raise CliError("Usage: approve c1 [research|write|visualize|present] [--web] [--queue]")
        with self.lock:
            caught = self.copilot.commitments.get(words[1])
            if not caught:
                raise CliError("Unknown commitment. Use caught to list this session's cards.")
            if caught.status == "dismissed":
                raise CliError("That commitment was dismissed.")
            if caught.task_id is not None:
                say(f"Already approved as task {caught.task_id}.")
                return
            kind = next((w for w in words[2:] if w in INSTRUCTIONS), caught.kind)
            ws = self.engine.workspace(self.commitment_workspaces.get(caught.id, self.workspace))
            tid = self.store.add_task(
                ws["id"],
                caught.text,
                kind,
                f"Caught live · {caught.source} · {caught.deadline or 'no stated deadline'}",
                "--web" in words,
                caught.origin,
            )
            caught.task_id, caught.status = tid, "approved"
        say(f"Approved {caught.id} → task {tid}", "green")
        if not ws["paused"] and "--queue" not in words:
            self.job(
                run_and_report, Engine(self.config, self.store), tid, self.provider, self.model
            )
        else:
            say("Task queued. Run work when ready.", "dim")

    def line(self, text):
        words = shlex.split(text.lstrip("/"))
        if not words:
            return True
        cmd = words[0]
        if cmd in {"quit", "exit"}:
            return False
        if cmd in {"help", "?"}:
            say(
                "record [--device ID] [--system-device ID]   stop   devices\n"
                "say Me: I will draft the proposal by Friday.\n"
                "caught   approve c1 [kind] [--web] [--queue]   dismiss c1\n"
                'ask "question" [--web]   copilot on|off\n'
                "workspace create NAME   workspace attach FILE   workspace use NAME\n"
                "models list [--provider openrouter]   models use PROVIDER [MODEL]\n"
                "task list   task run ID   task artifact ID   task approve ID\n"
                "meetings list   meetings show ID   meetings summarize ID\n"
                'search "query"   work   status   exit\n'
                "Any CLI command also works here. Quote multiword arguments."
            )
        elif cmd == "say":
            content = text[text.find("say") + 3 :].strip()
            source, sep, body = content.partition(":")
            self.caption(
                body.strip() if sep and source in {"Me", "Them"} else content,
                source if sep and source in {"Me", "Them"} else "Me",
            )
        elif cmd == "caught":
            with self.lock:
                rows = [vars(c).copy() for c in self.copilot.commitments.values()]
            table(
                rows, [("ID", "id"), ("Kind", "kind"), ("Status", "status"), ("Commitment", "text")]
            )
        elif cmd == "approve":
            self.approve(words)
        elif cmd == "dismiss":
            with self.lock:
                caught = self.copilot.commitments.get(words[1] if len(words) > 1 else "")
                if not caught or caught.status != "caught":
                    raise CliError("Choose an unapproved commitment from caught.")
                caught.status = "dismissed"
            say(f"Dismissed {caught.id}. No task created.")
        elif cmd == "copilot":
            if len(words) != 2 or words[1] not in {"on", "off"}:
                raise CliError("Usage: copilot on|off")
            self.ai = words[1] == "on"
            say(f"Copilot suggestions {words[1]}. Commitment detection stays active.")
        elif cmd == "status":
            say(
                f"Workspace · {self.workspace}\nRecording · {'active' if self.recorder else 'off'}\n"
                f"Agent jobs · {sum(not f.done() for f in self.futures)}"
            )
            model_notice(self.config, self.provider, self.model)
        elif cmd == "stop":
            self.stop_recording()
        else:
            args = parser().parse_args(words)
            if hasattr(args, "workspace") and args.workspace is None:
                args.workspace = self.workspace
            if hasattr(args, "provider") and hasattr(args, "model") and args.provider is None:
                args.provider = self.provider
                args.model = args.model or self.model
            if args.command in {"shell", "tui", "tmux", "replay"}:
                if args.command == "replay":
                    self.replay(args.file)
                else:
                    raise CliError("Run this command in another terminal.")
            elif args.command == "record":
                if args.workspace:
                    self.workspace = args.workspace
                self.provider, self.model = self.config.selection(args.provider, args.model)
                self.start_recording(args.device, args.system_device, args.title)
            elif args.command in {"ask", "suggest"}:
                with self.lock:
                    turns = list(self.copilot.turns)
                self.job(
                    self.answer,
                    args.question,
                    turns,
                    args.workspace,
                    args.provider,
                    args.model,
                    args.web,
                )
            elif (
                args.command == "work"
                or (
                    args.command == "task"
                    and (args.action == "run" or (args.action == "add" and args.run))
                )
                or (args.command == "meetings" and args.action == "summarize")
            ):
                self.job(execute, args, self.config, self.store, Engine(self.config, self.store))
            else:
                execute(args, self.config, self.store, self.engine)
                self.workspace = self.config.values["workspace"]
                self.provider, self.model = self.config.selection()
        return True

    def record_command(self, args):
        if args.duration is not None and args.duration <= 0:
            raise CliError("Duration must be greater than zero.")
        self.workspace = args.workspace or self.workspace
        self.provider, self.model = self.config.selection(args.provider, args.model)
        self.ai = args.copilot
        try:
            self.start_recording(args.device, args.system_device, args.title)
            start = time.monotonic()
            while args.duration is None or time.monotonic() - start < args.duration:
                if self.recorder.stop_event.wait(0.1):
                    break
        except KeyboardInterrupt:
            pass
        finally:
            try:
                if self.recorder:
                    self.stop_recording()
            except BaseException:
                self.close()
                raise
        if sys.stdin.isatty() and any(
            c.status == "caught" for c in self.copilot.commitments.values()
        ):
            say("Recording saved. Review the caught commitments in the companion.", "dim")
            self.loop()
        else:
            self.close()
        return 0

    def loop(self):
        from prompt_toolkit import PromptSession
        from prompt_toolkit.completion import WordCompleter
        from prompt_toolkit.patch_stdout import patch_stdout

        say("ADVERSARIA  /  TERMINAL\nListen. Remember. Do the work.", "bold cyan")
        say("Type help for commands. Start with record, or say Me: I'll draft the proposal.", "dim")
        model_notice(self.config, self.provider, self.model)
        session = PromptSession(
            completer=WordCompleter(
                [
                    "record",
                    "stop",
                    "say",
                    "caught",
                    "approve",
                    "dismiss",
                    "ask",
                    "workspace",
                    "task",
                    "models",
                    "search",
                    "meetings",
                    "status",
                    "help",
                    "exit",
                ]
            )
        )
        try:
            with patch_stdout(raw=True):
                while True:
                    try:
                        line = session.prompt(
                            lambda: f"{'● ' if self.recorder else ''}{self.workspace} › "
                        )
                        if not self.line(line):
                            break
                    except KeyboardInterrupt:
                        say("Use stop to finish recording; exit to leave.", "dim")
                    except EOFError:
                        break
                    except SystemExit:
                        pass
                    except (CliError, OSError, ValueError) as exc:
                        say(f"Error · {exc}", "red")
        finally:
            try:
                if self.recorder:
                    self.stop_recording()
            finally:
                self.close()

    def close(self):
        if any(not f.done() for f in self.futures):
            say("Waiting for active agent jobs to finish…", "dim")
        self.pool.shutdown(wait=True, cancel_futures=True)


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        config = Config(args.home)
        store = Store(config.directory)
        code = execute(args, config, store, Engine(config, store))
    except KeyboardInterrupt:
        say("Interrupted.", "yellow")
        code = 130
    except (CliError, OSError, ValueError) as exc:
        say(f"Error · {exc}", "red")
        code = 1
    raise SystemExit(code or 0)
