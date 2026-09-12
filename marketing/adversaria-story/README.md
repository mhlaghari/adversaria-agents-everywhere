# Why I built Adversaria

One opening slide about Hamza's motivation for Adversaria, in the supplied Laghari Labs design. The pain point is the whole story on screen:

> Every meeting adds hours of follow-up while my own projects wait.

- [Present in a browser](output/adversaria-one-slide.html). Works offline. Press **F** for fullscreen or **N** for speaker notes. Controls appear when you hover at the bottom right.
- [View the PDF](output/adversaria-one-slide.pdf) or [PNG](output/adversaria-one-slide.png).
- [Edit in PowerPoint](output/adversaria-one-slide.pptx). All copy is native editable text. Install the included **Silkscreen** and **JetBrains Mono** fonts from `assets/` to preserve the design. The PDF and HTML already embed the fonts.
- [Read the speaker notes](output/one-slide-notes.md), then move straight into the Copilot, Workspaces and CLI demo.

## Original deck for backup

The original eight-slide story remains available as [PDF](output/adversaria-story.pdf), [PowerPoint](output/adversaria-story-v3.pptx), [offline HTML](output/adversaria-story.html) and [presenter notes](output/presenter-notes.md). In the original HTML, use arrow keys to navigate, **F** for fullscreen, **N** for notes, and **H** to hide controls.

## Design and sources

The visual direction comes from the supplied `Lagharilabs design/tokens.css`, `slides.jsx`, and `system.jsx`: cream, arcade accent colors, pixel display typography, monospace body text, dark frames, and hard offset shadows. The original wordmark is retained in `assets/logo.png`.

The story comes from Hamza's brief. The 1–2 hour figure in the speaker notes describes his own experience with meeting action items. Product scope follows this repository's README, hackathon documentation and CLI documentation. Desktop local mode runs on-device. Cloud features and CLI provider calls use external services as described in the notes.

Fonts come from [Google Fonts: Silkscreen](https://fonts.google.com/specimen/Silkscreen) and [Google Fonts: JetBrains Mono](https://fonts.google.com/specimen/JetBrains+Mono). Their SIL Open Font License notices are included in `assets/` and in the self-contained HTML.

The JavaScript authoring source lives in `source/`. It uses the existing bundled `@oai/artifact-tool` runtime for the editable PowerPoint and Playwright for browser previews and PDF output. Runtime paths can be adjusted for another machine. Private previews and validation files stay in `.build/`.
