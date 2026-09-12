# Why I built Adversaria

Four slides about Hamza's motivation for Adversaria, in the supplied [Laghari Labs](https://lagharilabs.com) design. The approved pain-point slide opens the story:

> Every meeting adds hours of follow-up while my own projects wait.

- [Present in a browser](output/adversaria-story.html). Works offline. Use arrow keys to move, **F** for fullscreen and **N** for speaker notes. Controls appear when you hover at the bottom right.
- [View the PDF](output/adversaria-story.pdf).
- [Edit in PowerPoint](output/adversaria-story-short.pptx). All copy is native editable text. Install the included **Silkscreen** and **JetBrains Mono** fonts from `assets/` to preserve the design. The PDF and HTML already embed the fonts.
- [Read the speaker notes](output/presenter-notes.md), then demonstrate the product.

The four slides cover the pain point, Copilot, Workspaces, and today's desktop/CLI build. Each screen keeps only the central idea. Detail and local/cloud distinctions live in the notes.

## Other versions

The approved opening is also available alone as [PDF](output/adversaria-one-slide.pdf), [PowerPoint](output/adversaria-one-slide.pptx), [HTML](output/adversaria-one-slide.html) and [PNG](output/adversaria-one-slide.png). The original [eight-slide PowerPoint](output/adversaria-story-v3.pptx) remains as a backup.

## Design and sources

The visual direction comes from the supplied `Lagharilabs design/tokens.css`, `slides.jsx`, and `system.jsx`: cream, arcade accent colors, pixel display typography, monospace body text, dark frames, and hard offset shadows. The original wordmark is retained in `assets/logo.png`.

The story comes from Hamza's brief. The 1–2 hour figure in the speaker notes describes his own experience with meeting action items. Product scope follows this repository's README, hackathon documentation and CLI documentation. Desktop local mode runs on-device. Cloud features and CLI provider calls use external services as described in the notes.

Fonts come from [Google Fonts: Silkscreen](https://fonts.google.com/specimen/Silkscreen) and [Google Fonts: JetBrains Mono](https://fonts.google.com/specimen/JetBrains+Mono). Their SIL Open Font License notices are included in `assets/` and in the self-contained HTML.

The JavaScript authoring source lives in `source/`. `build-deck.mjs` builds the current four-slide story via `build-short-story.mjs`, importing the approved opening from its PowerPoint. It uses the bundled `@oai/artifact-tool` runtime and Playwright for browser previews and PDF output. For another revision, set `STORY_PPTX` to a new filename. Runtime paths can be adjusted for another machine. Private previews and validation files stay in `.build/`.
