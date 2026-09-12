# Why I built Adversaria

Eight slides about Hamza's motivation for Adversaria and the Copilot, Spaces and CLI work built on 12 September 2026. The deck adapts the supplied Laghari Labs design to a 16:9 presentation.

- [Present in a browser](output/adversaria-story.html). The file works offline. Use the arrow keys to move, **F** for fullscreen, **N** for presenter notes, or **H** to hide the controls. **Edit text** and **Save HTML** create an edited copy.
- [View the PDF](output/adversaria-story.pdf).
- [Edit in PowerPoint](output/adversaria-story-v3.pptx). All slide copy is native editable text. Install the included **Silkscreen** and **JetBrains Mono** fonts from `assets/` to preserve the design. PowerPoint may substitute fonts until they are installed. The PDF and HTML already embed the fonts.
- [Read the presenter notes](output/presenter-notes.md).

## Design and sources

The visual direction comes from the supplied `Lagharilabs design/tokens.css`, `slides.jsx`, and `system.jsx`: cream, arcade accent colors, pixel display typography, monospace body text, dark frames, and hard offset shadows. The original wordmark is retained in `assets/logo.png`.

The story comes from Hamza's brief. The 1–2 hour figure describes his own experience with meeting action items. Product scope follows this repository's README, hackathon documentation and CLI documentation. Desktop local mode runs on-device. Cloud features and CLI provider calls use external services as described on the slides and in the notes.

Fonts come from [Google Fonts: Silkscreen](https://fonts.google.com/specimen/Silkscreen) and [Google Fonts: JetBrains Mono](https://fonts.google.com/specimen/JetBrains+Mono). Their SIL Open Font License notices are included in `assets/` and in the self-contained HTML.

The JavaScript authoring source lives in `source/`. It uses the existing bundled `@oai/artifact-tool` runtime for the editable PowerPoint and Playwright for browser previews and PDF output. Runtime paths can be adjusted for another machine. Private previews and validation files stay in `.build/`.
