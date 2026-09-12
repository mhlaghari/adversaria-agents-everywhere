# Adversaria terminal demo

Adversaria is a terminal meeting companion. The user records microphone audio;
an optional loopback input captures the other side as a separate channel.
OpenRouter speech-to-text transcribes bounded audio turns. The terminal detects
questions and commitments on completed turns. Questions receive model-generated
suggestions grounded in the active workspace's attached files and past meetings.

A commitment stays in memory until the user approves it. Approval creates one
SQLite task. A task runs through OpenRouter or the installed Codex CLI, with Exa
web evidence when --web was requested. It writes a Markdown artifact. Diagram
artifacts contain Mermaid. The user reviews and approves the result. Research
sources are saved beside the artifact. No email or post is sent automatically.

CLI data is independent of the desktop app's encrypted database. This hackathon
edition uses cloud credits, not a local LLM or a local transcription model.
