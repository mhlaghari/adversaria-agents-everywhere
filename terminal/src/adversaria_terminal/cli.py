"""Command-line interface for Adversaria Terminal.

`advterm` (no subcommand) launches the full TUI. The subcommands below give
scriptable one-shot access to the same features:

    advterm record [--seconds N]     record mic + system audio, then transcribe
                                     and summarize, printing the note
    advterm import <audio-file>      transcribe + summarize an existing file
    advterm list                     browse meeting history
    advterm notes [--meeting ID]     print a meeting's notes (latest by default)
    advterm transcript [--meeting]   print the raw transcript
    advterm ask <question>           grounded Q&A over a meeting (streamed)
    advterm todos                    list open action items across meetings
    advterm health                   check the Python service
    advterm templates                list note templates
    advterm models                   list transcription models + download state
    advterm download-model <key>     download a Whisper model
    advterm export [--meeting]       write notes to a markdown file
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from rich.console import Console
from rich.markdown import Markdown
from rich.table import Table

from . import __version__

console = Console()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="advterm",
        description="Meeting Note Taker for the terminal.",
    )
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument(
        "--data-dir",
        help="Override the terminal data directory (also: ADVERSARIA_TERMINAL_DIR).",
    )
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("health", help="Check the Python ML service.")
    sub.add_parser("list", help="List meeting history.")
    sub.add_parser("templates", help="List note templates.")
    sub.add_parser("models", help="List transcription models and download state.")
    sub.add_parser("todos", help="List open action items across all meetings.")

    p_notes = sub.add_parser("notes", help="Print a meeting's notes.")
    p_notes.add_argument("--meeting", type=int, help="Meeting id (default: latest).")

    p_transcript = sub.add_parser("transcript", help="Print a meeting's transcript.")
    p_transcript.add_argument("--meeting", type=int, help="Meeting id (default: latest).")

    p_dl = sub.add_parser("download-model", help="Download a Whisper model.")
    p_dl.add_argument("key", help="Model key (see `advterm models`).")

    p_record = sub.add_parser("record", help="Record a meeting and produce notes.")
    p_record.add_argument("--seconds", type=float, help="Record for N seconds, then stop.")
    p_record.add_argument("--template", help="Note template name.")
    p_record.add_argument("--no-mic", action="store_true", help="Skip microphone capture.")
    p_record.add_argument("--no-system", action="store_true", help="Skip system audio capture.")
    p_record.add_argument("--no-diarize", action="store_true", help="Disable speaker diarization.")
    p_record.add_argument("--summary-language", help="Summary language code (e.g. en, ar).")

    p_import = sub.add_parser("import", help="Transcribe an audio file and produce notes.")
    p_import.add_argument("path", help="Path to the audio file.")
    p_import.add_argument("--template", help="Note template name.")
    p_import.add_argument("--no-diarize", action="store_true", help="Disable speaker diarization.")
    p_import.add_argument("--whisper-model", help="Whisper model key override.")

    p_ask = sub.add_parser("ask", help="Ask a question grounded in a meeting.")
    p_ask.add_argument("question", help="Your question.")
    p_ask.add_argument("--meeting", type=int, help="Meeting id (default: latest).")

    p_export = sub.add_parser("export", help="Export a meeting's notes to a markdown file.")
    p_export.add_argument("--meeting", type=int, help="Meeting id (default: latest).")
    p_export.add_argument("--output", help="Output .md path (default: data dir).")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command is None:
        return _launch_tui(args)
    try:
        return _dispatch(args)
    except KeyboardInterrupt:
        console.print("[dim]aborted.[/dim]")
        return 130


def _launch_tui(args: argparse.Namespace) -> int:
    from .app import AdversariaApp

    app = AdversariaApp(data_dir=args.data_dir)
    return app.run()


def _runtime(args: argparse.Namespace):
    from .client import ServiceClient
    from .config import load_config, service_url_env
    from .store import open_store

    config = load_config()
    if args.data_dir:
        config.data_dir = args.data_dir
    url = service_url_env() or config.python_service_url
    client = ServiceClient(url)
    store = open_store(config)
    return config, client, store


def _dispatch(args: argparse.Namespace) -> int:
    config, client, store = _runtime(args)

    if args.command == "health":
        return _cmd_health(client)
    if args.command == "list":
        return _cmd_list(store)
    if args.command == "templates":
        return _cmd_templates(client)
    if args.command == "models":
        return _cmd_models(client)
    if args.command == "todos":
        return _cmd_todos(store)
    if args.command == "download-model":
        return _cmd_download_model(client, args.key)
    if args.command == "notes":
        return _cmd_notes(store, args.meeting)
    if args.command == "transcript":
        return _cmd_transcript(store, args.meeting)
    if args.command == "record":
        return _cmd_record(config, client, store, args)
    if args.command == "import":
        return _cmd_import(config, client, store, args)
    if args.command == "ask":
        return _cmd_ask(store, client, args)
    if args.command == "export":
        return _cmd_export(store, config, args)
    console.print(f"[red]Unknown command: {args.command}[/red]")
    return 2


def _fail(exc: Exception) -> int:
    console.print(f"[red]{exc}[/red]")
    return 1


def _cmd_health(client) -> int:
    try:
        health = client.health()
    except Exception as exc:
        return _fail(exc)
    status = "[green]ok[/green]" if health.status == "ok" else f"[yellow]{health.status}[/yellow]"
    ollama = "[green]yes[/green]" if health.ollama_available else "[red]no[/red]"
    console.print(
        f"Service: {status}\n"
        f"Transcriber: [bold]{health.whisper_model}[/bold] ({health.transcriber_state})\n"
        f"Ollama: {ollama}\n"
        f"Embedder: {health.embedder_state}\n"
        f"Live captions: {health.live_captions_state}"
    )
    if health.transcriber_detail:
        console.print(f"[yellow]{health.transcriber_detail}[/yellow]")
    return 0


def _cmd_list(store) -> int:
    meetings = store.list_meetings()
    if not meetings:
        console.print("[dim]No meetings yet. Record one or `advterm import <file>`.[/dim]")
        return 0
    table = Table(title="Meeting history")
    table.add_column("#", justify="right", style="dim")
    table.add_column("Title", style="bold")
    table.add_column("Date", style="cyan")
    table.add_column("Category")
    table.add_column("Dur")
    table.add_column("Status")
    for m in meetings:
        table.add_row(
            str(m.id),
            m.title or "(untitled)",
            m.recorded_date(),
            m.category or "",
            _human_dur(m.duration_seconds),
            m.status,
        )
    console.print(table)
    return 0


def _cmd_templates(client) -> int:
    try:
        templates = client.list_templates()
    except Exception as exc:
        return _fail(exc)
    table = Table(title="Note templates")
    table.add_column("Name", style="bold cyan")
    table.add_column("Description")
    for t in templates:
        table.add_row(t.name, t.description)
    console.print(table)
    return 0


def _cmd_models(client) -> int:
    try:
        models = client.whisper_models()
    except Exception as exc:
        return _fail(exc)
    table = Table(title="Transcription models")
    table.add_column("Key", style="bold")
    table.add_column("Size")
    table.add_column("Downloaded")
    for m in models:
        table.add_row(m.key, m.size, "[green]yes[/green]" if m.downloaded else "[dim]no[/dim]")
    console.print(table)
    return 0


def _cmd_download_model(client, key: str) -> int:
    console.print(f"Downloading [bold]{key}[/bold] — this can take a while…")
    try:
        client.whisper_download(key)
    except Exception as exc:
        return _fail(exc)
    console.print("[green]Downloaded.[/green] The service picks it up automatically.")
    return 0


def _cmd_todos(store) -> int:
    items = store.list_all_action_items(include_done=False)
    if not items:
        console.print("[dim]No open action items.[/dim]")
        return 0
    table = Table(title="Open action items")
    table.add_column("#", justify="right", style="dim")
    table.add_column("Item", style="bold")
    table.add_column("Meeting", style="cyan")
    table.add_column("Date")
    for item, meeting in items:
        table.add_row(str(item.id), item.text, meeting.title or "(untitled)", meeting.recorded_date())
    console.print(table)
    return 0


def _cmd_notes(store, meeting_id: int | None) -> int:
    meeting = _resolve_meeting(store, meeting_id)
    if meeting is None:
        console.print("[red]Meeting not found.[/red]")
        return 1
    console.print(f"[bold]{meeting.title or '(untitled)'}[/bold]  {meeting.recorded_date()}")
    console.print(Markdown(meeting.summary or "_no summary_"))
    return 0


def _cmd_transcript(store, meeting_id: int | None) -> int:
    meeting = _resolve_meeting(store, meeting_id)
    if meeting is None:
        console.print("[red]Meeting not found.[/red]")
        return 1
    console.print(meeting.transcript or "_no transcript_")
    return 0


def _cmd_record(config, client, store, args) -> int:
    from .audio import RecordingSession, available_sources
    from .models import Meeting, now_iso

    sources, reason = available_sources()
    if not sources or reason:
        return _fail(ValueError(f"Audio capture unavailable: {reason or 'no sources'}"))
    names = {s.kind: s.device_name for s in sources}
    console.print(
        f"[bold]Recording[/bold]\n"
        f"  system audio (Them): [cyan]{names.get('them', 'off (disabled)')}[/cyan]\n"
        f"  microphone (Me):     [cyan]{names.get('me', 'off (disabled)')}[/cyan]\n"
        "[dim]Speak now — Ctrl+C to stop.[/dim]"
    )

    audio_dir = config.applied_data_dir() / "audio"
    session = RecordingSession(audio_dir, them=not args.no_system, me=not args.no_mic)
    warnings = session.start()
    for w in warnings:
        console.print(f"[yellow]{w}[/yellow]")

    t0 = time.time()
    try:
        if args.seconds:
            time.sleep(max(0.1, args.seconds))
        else:
            while True:
                time.sleep(0.2)
    except KeyboardInterrupt:
        pass
    elapsed = args.seconds or (time.time() - t0)
    session.stop()
    console.print(f"[dim]Captured {_human_dur(elapsed)}.[/dim]")

    template = args.template or config.default_prompt_template
    try:
        console.print("[bold]Transcribing…[/bold]")
        result = client.transcribe(
            audio_path=str(session.system_path) if session.them and session.system_path else None,
            mic_audio_path=str(session.mic_path) if session.me and session.mic_path else None,
            me_label=config.user_name,
            vocabulary=config.custom_vocabulary,
            diarize=not args.no_diarize,
        )
        transcript = result.get("text", "")
        console.print("[bold]Summarizing…[/bold]")
        summary = client.summarize(
            transcript,
            template_name=template,
            model=config.ollama_model,
            output_language=args.summary_language or config.summary_language,
            meeting_date=now_iso()[:10],
        )
    except Exception as exc:
        _cleanup_audio(session)
        return _fail(exc)

    meeting = Meeting(
        title=summary.get("title") or "Untitled",
        summary=summary.get("summary", ""),
        transcript=transcript,
        language=result.get("language", ""),
        duration_seconds=result.get("duration_seconds", elapsed),
        template_used=summary.get("template_used") or template,
        category=summary.get("category") or "",
        attendees=summary.get("attendees") or [],
        source="recorded",
        status="done",
        recorded_at=now_iso(),
    )
    meeting = store.add_meeting(meeting)
    console.print(f"\n[bold]Meeting #{meeting.id}:[/bold] {meeting.title}")
    console.print(Markdown(meeting.summary))
    _cleanup_audio(session)
    return 0


def _cmd_import(config, client, store, args) -> int:
    from datetime import datetime

    from .models import Meeting, now_iso

    path = Path(args.path)
    if not path.exists():
        console.print(f"[red]File not found: {path}[/red]")
        return 1
    template = args.template or config.default_prompt_template
    console.print(f"[bold]Importing[/bold] {path}")
    try:
        result = client.transcribe(
            audio_path=str(path.resolve()),
            me_label=config.user_name,
            vocabulary=config.custom_vocabulary,
            diarize=not args.no_diarize,
            single_file=True,
            whisper_model=args.whisper_model,
        )
        transcript = result.get("text", "")
        console.print("[bold]Summarizing…[/bold]")
        summary = client.summarize(
            transcript,
            template_name=template,
            model=config.ollama_model,
            output_language=config.summary_language,
            meeting_date=datetime.fromtimestamp(path.stat().st_mtime).date().isoformat(),
        )
    except Exception as exc:
        return _fail(exc)
    meeting = Meeting(
        title=summary.get("title") or path.stem,
        summary=summary.get("summary", ""),
        transcript=transcript,
        language=result.get("language", ""),
        duration_seconds=result.get("duration_seconds", 0.0),
        template_used=summary.get("template_used") or template,
        category=summary.get("category") or "",
        attendees=summary.get("attendees") or [],
        source="imported",
        status="done",
        recorded_at=now_iso(),
    )
    meeting = store.add_meeting(meeting)
    console.print(f"\n[bold]Meeting #{meeting.id}:[/bold] {meeting.title}")
    console.print(Markdown(meeting.summary))
    return 0


def _cmd_ask(store, client, args) -> int:
    meeting = _resolve_meeting(store, args.meeting)
    if meeting is None:
        console.print("[red]Meeting not found.[/red]")
        return 1
    if not meeting.transcript:
        console.print("[red]That meeting has no transcript.[/red]")
        return 1
    console.print(f"[bold]{meeting.title}[/bold]\nQuestion: [cyan]{args.question}[/cyan]\n")
    try:
        for kind, value in client.chat_stream(meeting.transcript, args.question):
            if kind == "text":
                console.print(value, end="")
            elif kind == "error":
                console.print(f"\n[red]{value}[/red]")
                return 1
    except Exception as exc:
        console.print(f"\n[red]{exc}[/red]")
        return 1
    console.print()
    return 0


def _cmd_export(store, config, args) -> int:
    meeting = _resolve_meeting(store, args.meeting)
    if meeting is None:
        console.print("[red]Meeting not found.[/red]")
        return 1
    out = Path(args.output) if args.output else (config.applied_data_dir() / f"meeting-{meeting.id}.md")
    rendered = (
        f"# {meeting.title or '(untitled)'}\n\n"
        f"- Recorded: {meeting.recorded_date()}\n"
        f"- Category: {meeting.category or '—'}\n"
        f"- Attendees: {', '.join(meeting.attendees) or '—'}\n\n"
        f"## Notes\n\n{meeting.summary}\n"
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(rendered, encoding="utf-8")
    console.print(f"Wrote [green]{out}[/green]")
    return 0


def _resolve_meeting(store, meeting_id: int | None):
    if meeting_id:
        return store.get_meeting(meeting_id)
    meetings = store.list_meetings()
    return meetings[0] if meetings else None


def _cleanup_audio(session) -> None:
    for path in (session.system_path, session.mic_path):
        if path and path.exists():
            try:
                path.unlink()
            except OSError:
                pass


def _human_dur(seconds: float) -> str:
    seconds = round(seconds)
    if seconds <= 0:
        return "—"
    mm, ss = divmod(seconds, 60)
    return f"{mm}m{ss:02d}s" if mm else f"{ss}s"


if __name__ == "__main__":
    sys.exit(main())