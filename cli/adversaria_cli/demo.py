"""Prepared, explicitly simulated workspace tasks; seeding never calls a provider."""

import json

from .config import atomic_text
from .store import now

NOTICE = "Prepared demo fixture — simulated task/output, not a live provider run."

CONTEXT = """# Adversaria hackathon demo context

This reference supports the tasks labeled DEMO. The examples are prepared for
rehearsal; they do not represent a real recorded meeting or fresh web research.

Adversaria captures meetings, offers Copilot suggestions, and turns approved
spoken commitments into workspace tasks. The CLI was built using OpenAI Codex.
OpenRouter supplies cloud speech transcription and streaming model responses.
Exa supplies external search evidence. CLI state is stored separately from the
desktop app in local SQLite and Markdown files.

The task workflow is: create or approve a commitment, run the task, read the
artifact, approve it or request a revision. Workspace context includes attached
UTF-8 files, relevant saved meeting passages, and instructions. Write produces
documents; Research produces briefs; Visualize produces Mermaid source; Present
produces Markdown slides and notes. Saved artifact approval does not send or
publish anything. Earlier drafts remain available on disk.

Captions arrive after pauses or bounded speech chunks and provider processing.
This OpenRouter path is not word-by-word WebSocket ASR. Microphone and loopback
inputs are separate channels; labels do not identify individual remote people.

For a two-minute demo, show a prepared draft first. Approve one, revise another,
and run the queued judge follow-up through the configured OpenRouter model.
Explain that the prepared examples are simulated and that G starts a real run.
"""

# Insert the ready-to-run task first so completed examples lead the newest-first list.
SAMPLES = (
    (
        "follow-up",
        "Draft an Adversaria hackathon judge follow-up",
        "write",
        None,
        False,
    ),
    (
        "slides",
        "Create the Adversaria four-slide demo outline",
        "present",
        """# Adversaria: from meeting to reviewed work

## Slide 1 — The follow-up problem
Every meeting adds work: notes to organize, questions to research, and documents
to draft. Keeping the conversation and its follow-up together saves context.

Speaker notes: Describe your own meeting workload. This sample supplies wording,
not a claim about measured customer results.

---

## Slide 2 — Listen and assist
- Record the meeting and follow live captions.
- Ask a question aloud or through the command bar.
- Use workspace evidence, with Exa sources for outside questions.

Speaker notes: Show the transcript and Copilot panes. Explain chunk-based captions.

---

## Slide 3 — Turn a commitment into a draft
- Approve a spoken commitment to queue a task.
- Generate a document, research brief, architecture diagram, or slide outline.
- Read, revise, and approve the saved artifact.

Speaker notes: Open a prepared task, then run the queued example live.

---

## Slide 4 — What powers the CLI
- Built using OpenAI Codex.
- OpenRouter: speech and streaming model responses.
- Exa AI: external search evidence.
- SQLite and files: workspace context, tasks, and draft history.

Speaker notes: Distinguish this cloud CLI from the desktop's local mode.
""",
        True,
    ),
    (
        "research",
        "Research Adversaria speech and search trade-offs",
        "research",
        """# Speech and search: demo research brief

Evidence scope: prepared from the attached Adversaria demo context. No live Exa
search was performed for this fixture. This is a product workflow comparison,
not a benchmark or a current provider-market survey.

## OpenRouter speech transcription
The CLI uploads bounded audio turns and displays returned captions. This makes
cloud speech available without installing a local ASR model. The trade-off is
that caption latency includes the speech boundary and the provider response.
It should be demonstrated as chunk-based transcription.

## OpenRouter task generation
The model receives the task, workspace instructions, and matching context.
Text streams into the task reader, then a completed Markdown artifact awaits
review. A local approval state makes it clear which drafts were accepted.

## Exa search
Exa supplies outside evidence for selected research tasks and external Copilot
questions. Saved source links make the answer inspectable. Lookup adds a network
step; internal meeting questions can rely on workspace evidence.

## Demo recommendation
Open a prepared artifact before recording. Show its review controls, then run a
short queued task live. Use an explicit search to demonstrate real Exa sources.
Avoid promising a fixed response time from a single successful run.

## Source
Attached file: Adversaria hackathon demo context. Fresh web research can be
created with N → Research → Exa web sources, then G.
""",
        False,
    ),
    (
        "architecture",
        "Map the Adversaria meeting-to-task architecture",
        "visualize",
        """# Meeting-to-task architecture

```mermaid
flowchart LR
    A["Microphone / loopback"] --> B["OpenRouter speech"]
    B --> C["Transcript + Copilot"]
    C --> D["Approved workspace task"]
    E["Workspace context"] --> C
    E --> D
    D --> F["OpenRouter task model"]
    G["Exa evidence when selected"] --> F
    F --> H["Markdown artifact + review"]
    H -->|"Revision feedback"| D
```

## Walkthrough
1. Capture microphone audio and, when routed, the other side of the call.
2. Display captions and generate Copilot answers from the current question.
3. Keep a spoken commitment pending until the user approves it as a task.
4. Run that task with relevant workspace evidence and optional Exa sources.
5. Save the draft, then approve it or request a revision.

## Boundaries
The CLI's database and artifacts are separate from the desktop app's store.
Cloud providers process selected audio/text. This terminal displays Mermaid
source; it does not render the diagram graphically. Revision creates another
artifact while preserving the earlier one.
""",
        False,
    ),
    (
        "readme",
        "Draft the Adversaria hackathon submission README",
        "write",
        """# Adversaria — meetings that lead to reviewed work

Adversaria connects a meeting's conversation to its follow-up: live captions,
Copilot answers, approved commitments, and workspace artifacts.

## What the terminal demo shows
Record a meeting and ask a question. Copilot suggests an answer using relevant
workspace context and, when needed, external evidence. Approve a spoken promise
as a task, generate its draft, and review the result in the same interface.

## Try the workflow
1. Choose a workspace with W and attach project context with F.
2. Press R to record and follow captions.
3. Approve a caught commitment, or press N to create a task.
4. Press T, open the task, and press G to generate a draft.
5. Read it. V approves; E adds revision feedback for another G run.

## Implementation
The CLI was built using OpenAI Codex and integrates hackathon sponsors
OpenRouter for speech/model responses and Exa AI for search/research. Local
SQLite tracks workspaces and task state; files retain Markdown artifacts.

## Scope
This submission extends an existing Adversaria project. CLI processing uses
cloud services and its own local storage. Captions arrive in bounded chunks;
Mermaid diagrams and slide decks are displayed as Markdown source. Approval
marks a local draft complete, with no automatic sending or publication.

Prepared tasks in this rehearsal are labeled DEMO. Run the queued judge
follow-up to demonstrate an actual response from the configured model.
""",
        False,
    ),
)


def seed_demo(config, store, workspace_name=None):
    """Add missing fixtures only, preserving real tasks and edits on repeated runs."""
    workspace = store.workspace(workspace_name or config.values["workspace"])
    wid = workspace["id"]
    context_path = config.directory / "demos" / str(wid) / "adversaria-demo-context.md"
    with store.db() as db:
        db.execute("BEGIN IMMEDIATE")
        if not db.execute(
            "SELECT 1 FROM sources WHERE workspace_id=? AND origin=?",
            (wid, str(context_path)),
        ).fetchone():
            atomic_text(context_path, CONTEXT)
            db.execute(
                "INSERT INTO sources(workspace_id,title,text,origin) VALUES (?,?,?,?)",
                (wid, "DEMO · Adversaria hackathon context", CONTEXT, str(context_path)),
            )
        for slug, title, kind, artifact, approved in SAMPLES:
            origin = f"adversaria-demo:v1:{wid}:{slug}"
            if db.execute("SELECT 1 FROM tasks WHERE origin=?", (origin,)).fetchone():
                continue
            task_id = db.execute(
                "INSERT INTO tasks(workspace_id,title,kind,details,status,origin,created) "
                "VALUES (?,?,?,?,?,?,?)",
                (
                    wid,
                    "DEMO · " + title,
                    kind,
                    NOTICE
                    + "\nUse the attached Adversaria hackathon demo context. "
                    + (
                        "Write a short follow-up draft for the judges. G starts a real provider run."
                        if artifact is None
                        else "E requests a revision; G then starts a real provider run."
                    ),
                    "queued" if artifact is None else ("done" if approved else "awaiting_review"),
                    origin,
                    now(),
                ),
            ).lastrowid
            if artifact is None:
                continue
            run_id = db.execute(
                "INSERT INTO runs(task_id,status,usage,created) VALUES (?,?,?,?)",
                (
                    task_id,
                    "awaiting_review",
                    json.dumps(
                        {
                            "provider": "simulation",
                            "model": "prepared-fixture-v1",
                            "simulated": True,
                        }
                    ),
                    now(),
                ),
            ).lastrowid
            path = config.directory / "artifacts" / str(task_id) / str(run_id) / "artifact.md"
            atomic_text(path, "> " + NOTICE + "\n\n" + artifact)
            atomic_text(path.with_name("sources.json"), "[]\n")
            db.execute("UPDATE runs SET artifact=? WHERE id=?", (str(path), run_id))
    tasks = store.rows(
        "SELECT id,title,status,kind FROM tasks WHERE workspace_id=? AND origin LIKE ? ORDER BY id DESC",
        (wid, f"adversaria-demo:v1:{wid}:%"),
    )
    return workspace, tasks
