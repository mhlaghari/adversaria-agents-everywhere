# Agents, Everywhere: Adversaria at the AI Tinkerers hackathon (2026-09-12, team OOM)

## The pain point

I lead an AI/ML team. My day is client meetings, design reviews and stand-ups, and every one of them ends with research, follow-ups and drafts that eat the time I need for my own projects. The agent I want does not live in a chatbox. It lives in the meeting, catches the work as it is spoken, and has it done by the time I am back at my desk.

## Prior work (built before the hackathon, disclosed)

- **Adversaria**, the local meeting engine: on-device dual-channel capture, Whisper transcription, local-LLM notes, SQLCipher storage, macOS and Windows. Nothing leaves the machine by default.
- **Workspaces** (August 2026): a tab where meeting to-dos become tasks and agent runs (local model, Claude Code or Codex) execute them into artifacts. 26 runs completed before today.
- **Live Copilot** (September 2026): while a meeting runs, questions are detected on the live captions, passages are retrieved from folder-scoped sources, and a spoken answer is streamed from a local or cloud model.

## Built at the hackathon

Built between 11:15 and 13:25 on 2026-09-12 (uncommitted at the time of writing; lands as commit 3 onward):

- **Commitments caught live become workspace tasks.** A detector runs beside the question detector on the live captions; a spoken commitment ("I will create a solutions architecture diagram for Wael by Monday") shows a *Commitment caught* card in the companion with the owner, deadline and inferred task type (Research / Write / Visualize / Present, correctable before approval). Approve creates the task in the matching workspace and queues a Local run; Dismiss creates nothing; nothing is persisted before the tap. The card then follows its own run ("Queued for an agent → Working on it… → Diagram ready → Open diagram").
- **A compact companion layout** for the window shrunk beside a video call (<900 px): pinned CAUGHT area, fixed transcript pane, independently scrolling answers, a Tools sheet for consent and folder settings.
- **Diagrams rendered in-app.** A Visualize task on the local model now produces one HTML file with a standalone SVG (no draw.io dependency, no network) and the Workspaces tab shows it inline under the task before it is approved. Tasks caught live carry a `live · HH:MM` chip.
- Layouts were designed by an OpenAI Codex model (gpt-6-astra) from a written brief; implementation was split across Claude and Codex workers and integrated by hand. Python service: no change.
- **A terminal Adversaria on cloud credits.** `cli/` was built at the hackathon by a Codex agent: `adversaria record` captures a meeting with live captions, streams grounded answers while it runs, catches spoken commitments as approve/dismiss cards that become workspace tasks, and `work` runs those tasks into Markdown artifacts. It uses OpenRouter (speech and text), Exa (search) and the user's Codex login instead of local models, so audio and transcripts do leave the machine. Details: [cli/README.md](./cli/README.md).

## Demo

### Terminal extension — 2026-09-12

The founder redirected this checkout toward a terminal edition using the provided
OpenRouter, Exa and Codex credits. `cli/` and the `adversaria` launchers implement
cloud speech transcription, an interactive Copilot with caught commitments,
persistent workspaces, background task runs, Exa source retrieval, Markdown/
Mermaid artifacts and explicit review. The desktop implementation remains intact.
The boxed dashboard now exposes workspace switching, context attachments,
instructions, task creation, streamed drafts, and approve/revise actions directly.
Recording and Copilot continue while workspace tasks run.
Saved artifacts have a local browser preview (**O**): Mermaid diagrams render
as SVG and can be downloaded. The renderer is bundled for offline use.
OpenRouter is the default speech/model provider; Codex runs through the existing
CLI login. Direct OpenAI API support is optional, not required by the credits path.

Verified: 93 CLI tests, live OpenRouter catalogs, terminal approval flow, and a
synthetic Codex task producing an artifact awaiting review. Later provider checks
also exercised OpenRouter speech/model calls and Exa research with synthetic
speech and public queries; see [cli/PROVIDER_CHECK.md](cli/PROVIDER_CHECK.md).
Actual microphone/loopback capture still needs a rehearsal. Full instructions
and limitations: [cli/README.md](cli/README.md).

```bash
./adversaria setup
./adversaria workspace create Demo
./adversaria workspace attach cli/examples/context.md
./adversaria replay cli/examples/meeting.txt
```

### Desktop demo

_Three minutes: a mock design review with one question (copilot card), two commitments caught live (workspace tasks created on the spot), one finished artifact approved before the recording stops._

## Run it

One command after the clone. It checks the toolchain (Node, Rust, uv, ffmpeg, Ollama), installs what is missing, pulls the local models, starts the Python service and launches the app in dev mode, which is the mode that shows the Workspaces tab. The Copilot tab is inside the recording companion.

```
macOS:    ./start.sh
Windows:  .\start.ps1
```

First run downloads the Whisper model and a 3 GB local LLM (set `SMALL_MODELS=0` for the 35B copilot model). Copilot cloud modes need a DeepSeek or Anthropic key in Settings › Live Copilot; Local needs nothing.

### CLI

Needs uv and an OpenRouter key (`./adversaria setup`); see [cli/README.md](./cli/README.md).

```
macOS:    ./adversaria
Windows:  .\adversaria.ps1
```

In the dashboard: **W** selects a workspace, **F** attaches context, **N** creates
a task, **T** opens tasks, **G** runs the selected task, and **V** approves a
reviewed artifact. **E** records revision feedback for another run.
