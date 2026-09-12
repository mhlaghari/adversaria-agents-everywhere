# Demo script (three minutes, one take)

Setup before recording the video: `./start.sh` running, an **Interviews** workspace (name must match the recording folder; Local engine; SIDRA manual and architecture context attached; agents **resumed**), Interviews folder open, System Audio Recording permission granted to the terminal that launched the app, AI · Local selected in the companion, "Questions can come from my mic" ticked (solo demo: you play both sides). Shrink the window to sit beside the call (about 480 px wide) so the compact companion layout is on screen.

0:00 Title card, one line: "Adversaria: the agent that lives in the meeting." Say the pain point in two sentences: I lead an AI/ML team, my day is meetings, and every meeting leaves research and drafts that eat the time I need for my own work.

0:20 Click **Record Meeting**, choose the Interviews folder, open the **Copilot** tab. Show the readiness line ("sources indexed · pack 3 projects").

0:35 Play the client. Say: "Before we move on, what is the difference between a workflow and an agent?" Wait for the copilot card; read the first sentence aloud. One line: "That is the copilot: it answers from my own project files while the meeting runs."

1:05 Speak the first commitment, as yourself, in one breath, then stop talking until the card lands (commitments close on a silence boundary; do not prefix with "Yes," or "And"): **"I will create a solutions architecture diagram for Wael by Monday."** A **Commitment caught** card appears with owner Wael, deadline by Monday, type **Visualize**. Click **Approve**. Say: "It made that a task, in the meeting, and an agent is already drawing it." (Visualize goes first because runs in a workspace are serial; it needs the head start.)

1:35 Second commitment, same way: **"I will check the SIDRA thresholds against the manual for Wael before Friday."** Card appears with type **Research**; Approve. Say: "Research tasks and drawing tasks; nothing runs without my tap." Watch the first card flip to "Working on it…".

1:55 Click **Stop & summarize**. Switch to **Workspaces → Interviews**. Show the two tasks with the **live · HH:MM** chip. The diagram task sits under Needs you with the architecture diagram rendered inline under its row (artifact `solutions-architecture.html`); the research task is running or awaiting review. Say: "By the time the summary is written, the diagram exists. I review, I do not start from zero."

2:30 Close: "Everything ran on this laptop. The transcription, the retrieval, the agent, all local; the meeting is the trigger, and that is the difference from a chatbox." End card with the repo URL and team OOM.

Fallbacks: if the local run is slow, show the task in "running" and cut to a run that finished earlier (there are 26 in the Test workspace). If the detector misses, click **Answer current question** for the copilot part and use the explicit form "Action item: send the numbers to Wael by Monday" for the commitment.

Timing fallback (Astra, 13:12): if the diagram takes over 60 seconds in rehearsal, show a preserved successful rehearsal task and say on camera that it was made earlier; never swap its artifact into a fresh run.
