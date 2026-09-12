"""Workspace browsing and reviewable background tasks for the terminal dashboard."""

from __future__ import annotations

import asyncio
from pathlib import Path

from prompt_toolkit.shortcuts import input_dialog, radiolist_dialog

from .config import CliError
from .copilot import Copilot
from .engine import INSTRUCTIONS, Engine

TASK_STATUS = {
    "queued": "Queued",
    "running": "Running",
    "awaiting_review": "Review draft",
    "done": "Approved",
    "failed": "Failed · retry",
}


class WorkspaceDashboard:
    """Uses Dashboard's UI loop; all task network work runs on a separate worker."""

    def workspace_entries(self):
        return [(None, "+ Create workspace")] + [
            (
                ws["id"],
                ("* " if ws["id"] == self.workspace["id"] else "  ")
                + ws["name"]
                + (" · paused" if ws["paused"] else ""),
            )
            for ws in self.workspaces
        ]

    def show_workspaces(self):
        self.workspace = self.store.workspace(self.workspace["name"])
        self.workspaces = self.store.rows("SELECT * FROM workspaces ORDER BY name COLLATE NOCASE")
        self.view = "workspaces"
        sources = self.store.rows(
            "SELECT id,title FROM sources WHERE workspace_id=? ORDER BY title",
            (self.workspace["id"],),
        )
        counts = self.store.rows(
            "SELECT status,COUNT(*) count FROM tasks WHERE workspace_id=? GROUP BY status",
            (self.workspace["id"],),
        )
        meetings = self.store.rows(
            "SELECT COUNT(*) count FROM meetings WHERE workspace_id=?", (self.workspace["id"],)
        )[0]["count"]
        self.set_body(
            f"ACTIVE WORKSPACE · {self.workspace['name']}\n"
            f"Tasks {'paused' if self.workspace['paused'] else 'enabled'} · {meetings} saved meetings\n"
            + (
                " · ".join(f"{c['count']} {TASK_STATUS[c['status']]}" for c in counts)
                or "No tasks yet"
            )
            + "\n\nF Attach context · I Instructions · P Pause/resume tasks\n"
            "T Browse tasks · N New task\n\n"
            "CONTEXT FILES\n"
            + (
                "\n".join(f"  {s['id']} · {s['title']}" for s in sources)
                or "No files attached. Press F to add a text or Markdown file."
            )
            + "\nType /source ID to read an attachment. Saved meetings also provide context.\n\n"
            "INSTRUCTIONS\n"
            + (
                self.workspace["instructions"]
                or "No custom instructions. Press I to add guidance for Copilot and tasks."
            )
        )
        self.focus_reader()
        self.set_status(
            "Arrows + Enter choose a workspace. F attaches context; Tab moves to workspace details."
        )

    def select_workspace(self, wid):
        if wid is None:
            self.action("new_workspace")
            return
        try:
            ws = next(w for w in self.workspaces if w["id"] == wid)
            self.use_workspace(ws["name"])
        except (CliError, OSError, ValueError) as exc:
            self.set_status(str(exc), error=True)

    def use_workspace(self, name):
        # Keep captions, unsaved audio, and caught commitments in their originating space.
        if self.recorder or self.phase in {"starting", "saving"}:
            raise CliError(
                "Stop and save with S before switching workspaces. You can still browse tasks."
            )
        ws = self.store.workspace(name)
        if ws["id"] != self.workspace["id"]:
            self.workspace_sessions[self.workspace["id"]] = (self.copilot, self.live_lines)
            self.workspace = ws
            self.copilot, self.live_lines = self.workspace_sessions.get(ws["id"], (Copilot(), []))
            self.generation += 1
            self.pending_question = None
            self.set_panel(
                self.suggestions, "Ask a question about this workspace. Press / to type."
            )
            self.refresh_commitments()
        self.config.save(workspace=ws["name"])
        self.show_workspaces()
        self.set_status(f"Workspace: {ws['name']}. F adds context; T opens tasks.")

    async def workspace_dialog(self):
        if self.recorder:
            raise CliError("Stop and save with S before creating or switching workspaces.")
        name = await self.dialog(
            input_dialog,
            title="Create workspace",
            text="Name this workspace:",
        )
        if name is not None and name.strip():
            self.use_workspace(name)

    def attach_context(self, value):
        value = value.strip()
        if len(value) > 1 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        self.store.attach(self.workspace["id"], value)
        self.show_workspaces()
        self.set_status(
            f"Attached {Path(value).name}. Copilot and tasks can use matching passages."
        )

    async def attachment_dialog(self):
        value = await self.dialog(
            input_dialog,
            title="Attach workspace context",
            text="Path to a UTF-8 file under 2 MB (Markdown, text, code, JSON or CSV):",
        )
        if value and value.strip():
            self.attach_context(value)

    def open_source(self, source_id):
        rows = self.store.rows(
            "SELECT * FROM sources WHERE id=? AND workspace_id=?",
            (source_id, self.workspace["id"]),
        )
        if not rows:
            raise CliError("That attachment is not in the current workspace.")
        source = rows[0]
        self.view = "source"
        self.body.buffer.cursor_position = 0
        self.set_body(
            f"{source['title']}\n{source['origin']}\n\n{source['text']}\n\nEsc returns to Workspaces."
        )
        self.focus_reader()

    def save_instructions(self, text):
        self.store.configure_workspace(self.workspace["id"], instructions=text.strip())
        self.show_workspaces()
        self.set_status("Workspace instructions saved.")

    async def instructions_dialog(self):
        value = await self.dialog(
            input_dialog,
            title="Workspace instructions",
            text="Guidance for Copilot and tasks. Leave blank to clear:",
            default=self.workspace["instructions"],
        )
        if value is not None:
            self.save_instructions(value)

    def pause_workspace(self, paused=None):
        ws = self.store.workspace(self.workspace["name"])
        paused = not ws["paused"] if paused is None else paused
        self.store.configure_workspace(ws["id"], paused=paused)
        self.show_workspaces()
        self.set_status(
            "Tasks paused. A run already in progress continues; X cancels it."
            if paused
            else "Tasks enabled. Select a queued task and press G to run it."
        )

    def task_entries(self):
        return [(None, "+ New task")] + [
            (t["id"], f"{t['id']} · {TASK_STATUS[t['status']]} · {t['kind']} · {t['title']}")
            for t in self.tasks
        ]

    def refresh_tasks(self):
        self.tasks = self.store.rows(
            "SELECT * FROM tasks WHERE workspace_id=? ORDER BY id DESC", (self.workspace["id"],)
        )

    def show_tasks(self):
        self.refresh_tasks()
        self.view = "tasks"
        self.focus_reader()
        self.set_status(
            "Enter opens a task. N creates one. Drafts need your review before completion."
        )

    def scoped_task(self, task_id):
        task = self.store.task(task_id)
        if task["workspace_id"] != self.workspace["id"]:
            raise CliError("That task belongs to another workspace. Press W to switch first.")
        return task

    def open_task(self, task_id):
        if task_id is None:
            self.action("new_task")
            return
        try:
            self.scoped_task(task_id)
            self.selected_task = task_id
            self.view = "task"
            self.body.buffer.cursor_position = 0
            self.render_task()
            self.focus_reader()
            self.set_status(
                f"Task {task_id}. "
                + {
                    "queued": "G runs it; E edits the brief.",
                    "failed": "G retries it; E edits the brief.",
                    "awaiting_review": "Read the draft, then V approves or E requests a revision.",
                    "done": "Approved artifact saved locally. O opens the rendered preview.",
                    "running": "The draft is being generated.",
                }[self.task_state]
            )
        except (CliError, OSError, ValueError) as exc:
            self.set_status(str(exc), error=True)

    def render_task(self, *, follow=False):
        task = self.scoped_task(self.selected_task)
        latest = self.store.rows(
            "SELECT * FROM runs WHERE task_id=? ORDER BY id DESC LIMIT 1", (task["id"],)
        )
        state = task["status"]
        self.task_state = state
        self.task_has_artifact = bool(latest and latest[0]["artifact"])
        actions = {
            "queued": "G Run task · E Edit brief",
            "failed": "G Retry task · E Edit brief",
            "running": (
                "X Cancel this run (waits for the current network response)"
                if task["id"] == self.running_task
                else "This task is running in another terminal."
            ),
            "awaiting_review": "Read the draft below. V Approve · E Request revision",
            "done": "Approved. The artifact is saved locally.",
        }[state]
        if self.task_has_artifact:
            actions = "O Open rendered preview in browser\n" + actions
        text = (
            f"TASK {task['id']} · {TASK_STATUS[state]}\n{task['title']}\n"
            f"{task['kind']} · {'Exa web research' if task['web'] else 'Workspace evidence'}\n\n"
            f"{actions}\nT / Esc returns to Tasks\n\n"
        )
        if task["details"]:
            text += f"BRIEF\n{task['details']}\n\n"
        if task["id"] == self.running_task and self.task_active and state in {"queued", "running"}:
            text += "LIVE DRAFT · not yet saved\n\n" + (
                self.task_text or "Connecting to OpenRouter…"
            )
        elif latest and latest[0]["error"]:
            text += f"RUN ERROR\n{latest[0]['error']}\n\nPress G to retry."
        elif latest and latest[0]["artifact"]:
            path = self.store.artifact(task["id"])
            text += f"SAVED ARTIFACT\n\n{path.read_text(encoding='utf-8')}\n\nFile: {path}"
        else:
            text += "The agent will draft a local Markdown artifact using this workspace's context."
        self.set_body(text, follow=follow)

    async def preview_task(self):
        if self.view != "task" or self.selected_task is None:
            raise CliError("Press T and open a task with a saved artifact, then press O.")
        task = self.scoped_task(self.selected_task)
        from .preview import open_preview

        self.set_status("Preparing local artifact preview…")
        path = await asyncio.to_thread(open_preview, self.store, task["id"])
        self.set_status(
            f"Preview opened for task {task['id']}. Download SVG from the diagram. {path}"
        )

    def add_workspace_task(self, title, kind="write", details="", web=False):
        if kind not in INSTRUCTIONS:
            raise CliError("Choose write, research, visualize, or present.")
        tid = self.store.add_task(self.workspace["id"], title, kind, details, web)
        self.open_task(tid)
        self.set_status(f"Task {tid} queued. G runs it with OpenRouter.")
        return tid

    async def new_task_dialog(self):
        title = await self.dialog(
            input_dialog,
            title="New workspace task",
            text="What should the agent produce?",
        )
        if not title or not title.strip():
            return
        choice = await self.dialog(
            radiolist_dialog,
            title="Task capability",
            text="Choose the deliverable. Nothing runs until you press G.",
            values=[
                ("write", "Write — document or draft"),
                ("research_web", "Research — Exa web sources + workspace evidence"),
                ("research", "Research — workspace evidence only"),
                ("visualize", "Visualize — Mermaid architecture diagram in Markdown"),
                ("present", "Present — slide outline and notes in Markdown"),
            ],
            default="write",
        )
        if choice is None:
            return
        self.add_workspace_task(
            title.strip(),
            "research" if choice == "research_web" else choice,
            web=choice == "research_web",
        )

    @property
    def task_active(self):
        return self.task_future is not None and not self.task_future.done()

    def run_workspace_task(self, task_id=None):
        if task_id is None and self.view != "task":
            raise CliError("Press T, open a queued task, then press G.")
        task_id = task_id or self.selected_task
        if task_id is None:
            raise CliError("Press T, open a queued task, then press G.")
        task = self.scoped_task(task_id)
        if self.task_active:
            raise CliError(f"Task {self.running_task} is already running. X cancels it.")
        # Consume the previous completion before reusing its worker/run identity.
        self.drain_events()
        if task["paused"]:
            raise CliError("Workspace tasks are paused. Press W then P to resume.")
        if task["status"] not in {"queued", "failed"}:
            raise CliError(
                "Run a queued or failed task. Request a revision with E for a saved draft."
            )
        self.running_task = task_id
        self.task_text = ""
        self.task_cancel.clear()
        model = self.config.values.get("workspace_model") or (
            self.config.values["model"]
            if self.config.values["provider"] == "openrouter"
            else self.config.values.get("copilot_model", "google/gemini-2.5-flash-lite")
        )

        def run():
            tokens = None
            error = None
            try:
                if self.task_cancel.is_set():
                    return
                tokens = Engine(self.config, self.store).run_task(
                    task_id, provider="openrouter", model=model
                )
                for token in tokens:
                    if self.task_cancel.is_set():
                        tokens.throw(CliError("Run cancelled. Press G to retry."))
                    self.events.put(("task_token", task_id, token))
            except Exception as exc:  # noqa: BLE001 - report provider failures in the dashboard.
                error = str(exc) or type(exc).__name__
            finally:
                try:
                    if tokens is not None:
                        tokens.close()  # Engine persists a failed run on generator cancellation.
                finally:
                    self.events.put(("task_finished", task_id, error))

        self.task_future = self.task_worker.submit(run)
        self.open_task(task_id)
        self.set_status(
            f"Running task {task_id} with OpenRouter. You can record or browse while it works."
        )

    def cancel_workspace_task(self):
        if not self.task_active:
            raise CliError("No task is running in this dashboard.")
        self.task_cancel.set()
        self.set_status(
            f"Cancelling task {self.running_task}; waiting for the current network response…"
        )

    async def finish_workspace_task(self):
        if self.task_active:
            self.cancel_workspace_task()
            await asyncio.wrap_future(self.task_future)
            self.drain_events()

    def approve_task(self, task_id=None):
        task_id = task_id or self.selected_task
        task = self.scoped_task(task_id)
        if self.view != "task" or self.selected_task != task_id:
            self.open_task(task_id)
            self.set_status("Read this draft, then press V or type approve again to mark it done.")
            return
        if task["status"] != "awaiting_review":
            raise CliError("Only a saved draft awaiting review can be approved.")
        # Missing/unreadable artifacts cannot be approved by repeating a command.
        self.store.artifact(task_id).read_text(encoding="utf-8")
        self.store.review(task_id, True)
        self.render_task()
        self.set_status(
            f"Task {task_id} approved. Artifact saved locally; nothing is sent or published."
        )

    async def revise_task_dialog(self):
        if self.view != "task":
            raise CliError("Press T and open the task you want to edit or revise.")
        task = self.scoped_task(self.selected_task)
        if task["status"] not in {"queued", "failed", "awaiting_review"}:
            raise CliError(
                "Edit a queued/failed task, or request a revision of a draft awaiting review."
            )
        value = await self.dialog(
            input_dialog,
            title=("Request revision" if task["status"] == "awaiting_review" else "Edit brief")
            + f" · Task {task['id']}",
            text=f"{task['title']}\n\nWhat should the agent change or include?",
        )
        if value and value.strip():
            self.revise_task(task["id"], value)

    def revise_task(self, task_id, feedback):
        self.scoped_task(task_id)
        self.store.revise(task_id, feedback)
        self.open_task(task_id)
        self.set_status(f"Task {task_id} queued with your feedback. G generates a new draft.")

    def workspace_event(self, kind, task_id, text):
        if kind == "task_token":
            self.task_text += text
        elif kind == "task_finished":
            task = self.store.task(task_id)
            self.set_status(
                f"Task {task_id} · {task['workspace']}: "
                + (text if text else TASK_STATUS[task["status"]] + ". Press T to view."),
                error=bool(text),
            )
        else:
            return False
        return True

    def workspace_command(self, command, value):
        if command == "workspaces":
            self.show_workspaces()
        elif command == "workspace" and value:
            self.use_workspace(value.strip().strip('"'))
        elif command == "attach" and value:
            self.attach_context(value)
        elif command == "source" and value:
            self.open_source(int(value))
        elif command == "instructions":
            self.save_instructions(value)
        elif command in {"pause", "resume"}:
            self.pause_workspace(command == "pause")
        elif command == "tasks":
            self.show_tasks()
        elif command == "new" and value:
            kind, _, title = value.partition(" ")
            web = title.startswith("--web ")
            self.add_workspace_task(title[6:].strip() if web else title, kind, web=web)
        elif command == "open" and value:
            self.open_task(int(value))
        elif command == "preview":
            if value:
                self.scoped_task(int(value))
                self.open_task(int(value))
            self.action("preview_task")
        elif command == "run":
            self.run_workspace_task(int(value) if value else None)
        elif command in {"accept", "approve"} and (not value or value.isdigit()):
            self.approve_task(int(value) if value else None)
        elif command == "revise" and value:
            tid, _, feedback = value.partition(" ")
            self.revise_task(int(tid), feedback)
        elif command == "cancel":
            self.cancel_workspace_task()
        elif command == "help":
            self.show_help()
        else:
            return False
        return True

    def show_help(self):
        self.view = "help"
        self.body.buffer.cursor_position = 0
        self.set_body(
            "WORKSPACES\nW Browse / create workspace   F Attach context file\n"
            "I Workspace instructions   P Pause/resume new runs\n\n"
            "TASKS\nT Browse   N New task   Enter Read a task\n"
            "G Run / retry   V Approve draft   E Edit brief / revise\n"
            "O Open rendered artifact / diagram in browser (Download SVG)\n"
            "X Cancel current run   Esc Back\n\n"
            "MEETINGS\nR Record / live transcript   S Stop & save   M History\n"
            "A Audio inputs   K Speech key\n\n"
            "COMMAND BAR · press /, type, then Enter\n"
            "workspace Hackathon\nattach /path/to/context.md\nsource 1\n"
            "new write Draft the submission README\nnew research --web Compare speech APIs\n"
            "new visualize Map our architecture\nrun 1\nopen 1\npreview 1\napprove 1\n"
            "revise 1 Add the latency measurements\ncancel\n"
            "ask What did we decide?\nsearch latest speech recognition research\n"
            "approve c1   dismiss c1\n\n"
            "Tab / Shift-Tab switch panes. Q saves capture, cancels any task run, and quits.\n"
            "Task cancellation waits for the current network response.\n"
            "Artifacts are saved as Markdown. O renders diagrams and documents in a local browser preview."
        )
        self.focus_reader()
