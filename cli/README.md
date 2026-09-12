# Adversaria CLI

Record meetings, get live suggestions, approve spoken commitments, research with
Exa, and run workspace tasks with OpenRouter or your Codex login. This terminal
edition uses the hackathon's **OpenRouter + Exa + Codex** credits. No desktop app,
Rust build, Ollama, local LLM, or Python ML service is required.

## Start

Install [uv](https://docs.astral.sh/uv/getting-started/installation/), then from the
repository root:

```bash
./adversaria setup
./adversaria
```

Windows: use `.\adversaria.ps1 setup`, then `.\adversaria.ps1`.
`setup` asks for OpenRouter and Exa keys through hidden prompts. You can instead
provide `OPENROUTER_API_KEY` and `EXA_API_KEY` in your environment. Keys never need
to appear in a command argument, transcript, task, or repository file.

To install the `adversaria` command globally:

```bash
uv tool install ./cli
adversaria setup
adversaria
```

Python 3.11+ is required; uv manages the environment. Microphone capture uses
PortAudio through sounddevice (install your system's PortAudio library if needed
on Linux). ffmpeg is optional for small supported audio files and is used to split
imports larger than 24 MB. The existing desktop `start.sh` is a separate launcher.

## Meeting dashboard

Run `adversaria` (or `./adversaria` from the repository) to open the full-screen
dashboard. It works directly in your terminal, including inside tmux; tmux is not
required. Select an action with arrow keys and Enter, click it, or use a shortcut:

| Key | Action |
| --- | --- |
| R | Record a meeting, or return to its live transcript |
| S | Stop capture, wait for the final caption, and save |
| M | Browse previous meetings in the current workspace |
| A | Choose a microphone and optional loopback input |
| K | Add the speech provider's API key through a hidden prompt |
| Tab | Switch between the menu and reading pane |
| Q | Save an active recording and quit |
| / | Type `ask QUESTION`, `search QUERY` (Exa), `approve c1`, or `dismiss c1` |
| : | Open the command companion |

The live transcript follows new captions unless you scroll back. Use arrow keys,
Page Up and Page Down to read it. Previous meetings opens a selectable list;
Enter reads a meeting, and Esc returns to the list. You can browse saved meetings
while capture continues. Failed or empty transcription preserves the audio and
shows its recovery path. Speech captions arrive after a pause and provider
processing. Copilot automatically streams a suggested answer when a completed
speech turn contains a question; a timed fragment ending in `?` triggers immediately. Spoken commitments appear in their own pane;
press `/` and type `approve c1` or `dismiss c1`. Approval queues a workspace task;
run it from the command companion with `work`. Press `/` and type `ask QUESTION`
for an on-demand suggestion grounded in recent speech and workspace evidence.
`search QUERY` uses your Exa key and streams an OpenRouter answer with source evidence.
Dashboard Copilot uses OpenRouter and the `copilot_model` configuration setting
(default `google/gemini-2.5-flash-lite`), independently of the task engine.

`adversaria tmux` opens it inside a persistent tmux session (requires tmux);
Ctrl-B then D detaches. `adversaria tui` explicitly opens the dashboard. Piped `adversaria` prints help.
The command interface is available with `adversaria shell`.

## Command companion

Inside `adversaria shell`, all normal CLI commands are available. Quote multiword
arguments. Prefixing commands with `/` is optional.

```text
workspace create "Hackathon"
workspace attach cli/examples/context.md
record
```

Speak: “I will create a solutions architecture diagram by Monday.” After a pause,
the terminal shows `CAUGHT c1`. While capture continues:

```text
approve c1
task list
task artifact 1
task approve 1
stop
meetings list
meetings summarize 1
```

`approve c1 research --web` changes the inferred capability and includes an Exa
search when the task runs. `approve c1 --queue` queues without starting. `dismiss
c1` creates no task. Repeated approval returns the same task. Workspace pause
blocks new runs; resume then use `work` to drain the queue. Approval of an artifact
marks the task done; it does not publish or send anything.

Questions in completed speech turns generate suggestions automatically. `copilot
off` disables model suggestions while retaining transcription and commitment
detection. `ask "What should I say?"` includes the recent conversation and matching
workspace evidence. `ask "Latest developments?" --web` adds Exa results.

Use `devices` to list inputs. For both sides of a call, route the call's output to
a loopback input such as BlackHole, then `record --device MIC_ID --system-device
LOOPBACK_ID`. The CLI does not implement the desktop app's native macOS system
audio tap or Windows WASAPI loopback. Merely selecting BlackHole does not route
the call's output there; configure the OS/call output first. Labels are channel
labels (`Me`/`Them`), not identification of individual remote speakers.

OpenRouter live captions use audio-level silence detection (no local ML model),
then transcribe each bounded turn (400 ms pause detection, 250 ms audio delivery). Continuous speech produces fragments at four
seconds; two bounded requests can run concurrently while captions retain audio order.
Commitments are detected once the turn closes. Caption latency includes
the pause and the provider's response time. Real microphone sensitivity and
provider latency still need a credentialed rehearsal. This mode is not a
word-by-word WebSocket transcription service.

## Models and credits

```bash
./adversaria models list --filter anthropic
./adversaria models list --filter google
./adversaria models use openrouter auto
./adversaria models speech --list
./adversaria models speech --router-model openai/gpt-transcribe
```

The text catalog comes from OpenRouter, includes context limits and current
text-token prices, and excludes image-only and batch-only entries. `auto` uses
OpenRouter's `openrouter/auto` router; explicit IDs use the selected model. Speech
has a separate catalog and configuration. The default speech model is
`openai/gpt-transcribe`, **billed through your OpenRouter key**.

Codex uses its own existing login/subscription, not an OpenRouter or OpenAI API
key. Install Codex and run `codex login` if it is not already authenticated:

```bash
./adversaria task add "Draft our architecture document" --kind visualize
./adversaria task run 1 --provider codex
# Or use Codex for every subsequent LLM operation:
./adversaria models use codex
```

The Codex engine runs `codex exec` in a temporary working directory with a
read-only sandbox, an ephemeral session, and user-config loading disabled. It
asks for a final deliverable from supplied evidence. It returns the final text
when Codex finishes; OpenRouter/OpenAI answers stream tokens. No repository edits
or arbitrary task-generated code execution are part of this CLI's task runner.
`--model` selects an explicit Codex model; `auto` uses the CLI default. Keep
OpenRouter selected for faster live suggestions and pass `--provider codex` to
individual workspace runs if preferred.

Direct OpenAI API access is optional and separate from Codex credits:

```bash
./adversaria auth openai
./adversaria models use openai MODEL_ID
./adversaria models speech --provider openai
```

That speech mode uses `gpt-live-transcribe` over Realtime WebSockets for capture
and `gpt-transcribe` for file uploads. `models speech --file-model ID --live-model
ID` overrides them. It requires `OPENAI_API_KEY` or an `auth openai` key; a Codex
ChatGPT login alone cannot authenticate it. Return to the main path with `models
speech --provider openrouter`.

## Commands

```bash
./adversaria doctor
./adversaria transcribe ./meeting.wav --workspace "Hackathon" --summarize
./adversaria record --duration 60 --copilot --workspace "Hackathon"
./adversaria meetings show 1
./adversaria meetings export 1 ./meeting-notes.md
./adversaria workspace instructions "Use concise, source-backed explanations."
./adversaria ask "What did we decide about the architecture?"
./adversaria search "latest voice agent tooling" --count 5
./adversaria task add "Research voice agent tooling" --kind research --web --run
./adversaria task show 1
./adversaria task artifact 1 --raw
./adversaria task revise 1
./adversaria task run 1
./adversaria work --watch
```

`research` without `--web` uses local workspace evidence and is labelled that way
in its prompt. `--web` sends the task title/question to Exa; returned URLs and text
ground the draft. Each successful run writes `artifact.md` and `sources.json` and
saves available model usage in its run receipt. `task show ID` includes errors
and usage. Aborted or incomplete streams fail the run instead of accepting a
partial draft. `task retry ID` requeues a failed draft. If a process was killed,
first verify that worker has stopped, then `task recover ID` marks its stuck run
failed so it can be retried. Shell jobs are serialized; capture continues in
separate bounded workers.

## Rehearse without a microphone

```bash
./adversaria workspace create "Demo"
./adversaria workspace attach cli/examples/context.md
./adversaria replay cli/examples/meeting.txt
```

Replay saves the example transcript and catches two commitments. On a terminal it
then opens the companion, where `approve c1` creates the diagram task. Add
`--copilot` to also generate the answer to the example question. Piped/noninteractive
replay detects and reports but does not approve commitments. You can also enter
`say Me: I will write the proposal by Friday.` in the companion for a quick check.

## Data and boundaries

The CLI stores its own SQLite database, workspace evidence and Markdown artifacts
in `~/.local/share/adversaria-cli`. Set `ADVERSARIA_CLI_HOME` or `--home PATH` for
an isolated demo. **It does not read, migrate, or synchronize the desktop
SQLCipher database.** Export desktop notes as Markdown and attach them if needed.

This is a cloud hackathon edition: audio goes to the selected speech provider;
questions, selected evidence and task briefs go to the chosen model provider;
explicit research queries go to Exa. The desktop's local-only privacy promises
do not describe this edition. CLI storage is plaintext with restrictive POSIX
directory/file permissions, not SQLCipher or an encrypted recording spool.
Windows permissions follow the user's filesystem ACLs.

Capture retains full WAV audio during a session. On a clean completion it saves
the final transcripts and removes only its own recordings. On caption failure or
empty transcription, it preserves the audio and prints recovery paths. Imported
originals are never removed. Exports refuse to overwrite an existing target.
Remote text is rendered without terminal escape controls. Attachments currently
support UTF-8 text up to 2 MB; retrieval is bounded lexical matching.

## Validation

```bash
uv sync --project cli --group dev
uv run --project cli pytest cli/tests
uv run --project cli ruff check cli
uv run --project cli ruff format --check cli
```

Tests cover cloud request/stream contracts, speech framing and resampling,
out-of-order realtime completions, silence/forced-turn handling, input capture,
explicit/idempotent commitment approval, scoped retrieval, task claims,
failure/cancellation/retry, source retention, Codex subprocess handling and exports,
plus dashboard keyboard navigation, live captions, final-caption saving on
stop/quit, scoped history and audio recovery.
Verified live: OpenRouter text/STT catalogs, local input enumeration, interactive
approval flow, and one synthetic Codex task through the logged-in CLI into a
reviewable diagram artifact, then explicit approval to mark its task done.
OpenRouter key authentication, real cloud ASR, streamed Copilot answers and Exa
search passed a credentialed synthetic-audio rehearsal on 2026-09-12. The full
audio-to-answer check returned its first caption at 4.1 seconds and a complete
answer at 5.3 seconds from sample playback start; these single-run timings are
not latency guarantees. See [provider checks](PROVIDER_CHECK.md). Actual microphone
capture, optional direct OpenAI calls and Windows runtime still need rehearsal.

API references: [OpenRouter speech](https://openrouter.ai/docs/guides/overview/multimodal/stt),
[OpenRouter chat](https://openrouter.ai/docs/quickstart),
[Exa search](https://exa.ai/docs/reference/search),
[Codex noninteractive mode](https://learn.chatgpt.com/docs/non-interactive-mode),
[OpenAI live transcription](https://developers.openai.com/api/docs/guides/realtime-transcription),
[OpenAI file transcription](https://developers.openai.com/api/docs/guides/speech-to-text).
