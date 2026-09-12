---
name: Adversaria CLI
description: A keyboard-first terminal companion from meeting capture to reviewed workspace work.
colors:
  background: "#17212b"
  text: "#e5edf3"
  raised-surface: "#253545"
  header-text: "#f2f6fa"
  accent: "#79d4e4"
  muted: "#b0bdc9"
  menu-surface: "#1d2b38"
  attention: "#ffbcad"
  preview-border: "#415464"
  preview-quote-text: "#c7d4df"
  preview-code-surface: "#111a22"
typography:
  preview-body:
    fontFamily: "Arial, sans-serif"
    fontSize: "18px"
    lineHeight: 1.6
  preview-code:
    fontFamily: "monospace"
components:
  header:
    backgroundColor: "{colors.raised-surface}"
    textColor: "{colors.header-text}"
  action-list:
    backgroundColor: "{colors.menu-surface}"
    textColor: "{colors.text}"
  selected-action:
    backgroundColor: "{colors.accent}"
    textColor: "{colors.background}"
  transcript:
    backgroundColor: "{colors.background}"
    textColor: "{colors.text}"
  status:
    backgroundColor: "{colors.raised-surface}"
    textColor: "{colors.text}"
  error-status:
    backgroundColor: "{colors.raised-surface}"
    textColor: "{colors.attention}"
  dialog:
    backgroundColor: "{colors.raised-surface}"
    textColor: "{colors.text}"
  focused-button:
    backgroundColor: "{colors.accent}"
    textColor: "{colors.background}"
  preview-diagram:
    backgroundColor: "{colors.menu-surface}"
    textColor: "{colors.text}"
  preview-download:
    backgroundColor: "{colors.accent}"
    textColor: "{colors.background}"
  preview-code:
    backgroundColor: "{colors.preview-code-surface}"
    textColor: "{colors.text}"
  preview-quote:
    backgroundColor: "{colors.raised-surface}"
    textColor: "{colors.preview-quote-text}"
---

# Design System: Adversaria CLI

## Overview

**Creative North Star: "The Meeting Companion"**

Adversaria uses the terminal's own character grid and controls to keep recording,
live captions, saved meetings and workspace tasks within reach. The workflow
continues from captured commitments through a queued task to a reviewed artifact.
Cyan identifies headings and focus; slate surfaces and the user-requested tmux-style
boxes divide actions, reading and assistance. Status lines and assistant panes
persist while the reading pane changes.

This records the implemented `STYLE`, `ActionList` and `Dashboard` in
`adversaria_cli/dashboard.py` and the workspace extension in
`adversaria_cli/workspace_dashboard.py`, with the existing command output in
`adversaria_cli/ui.py` as context. The product scope is documented in `README.md`.
The local artifact viewer in `adversaria_cli/preview.py` extends this palette into
a standalone browser page for formatted Markdown and diagrams.

**Key Characteristics:**

- Explicit text actions with visible keyboard shortcuts.
- A flexible reading pane with persistent Copilot and commitment frames.
- Explicit task states, review actions, progress messages and recovery instructions.

## Colors

The dashboard combines cool slate surfaces, pale text, cyan emphasis and warm
attention text. Frontmatter colors record the native prompt_toolkit palette and
the explicitly prefixed additions used only by the browser preview.

### Primary

- **Accent cyan:** pane titles, brand name, selected actions, focused dialog
  buttons and the scrollbar thumb. Selected surfaces use dark background-colored
  text for contrast.

### Secondary

- **Attention peach:** active recording phases and error messages. The words
  distinguish recording from failure; the color alone does not.

### Neutral

- **Background slate:** main canvas and transcript surface.
- **Menu slate:** action, meeting, workspace and task-list surfaces.
- **Raised slate:** header, status bar, dialogs and scrollbar track.
- **Pale text / header text:** reading content and the header's brighter text.
- **Muted slate text:** secondary instructions, idle state and shortcut footer.
- **Preview border slate:** browser figure edges, dividers and header border.
- **Preview quote text:** softer reading text within browser blockquotes.
- **Preview code surface:** the browser's inset source and code blocks.

**The Explicit State Rule.** Pair state color with readable status text or a
selection marker. Retain the focused row's `>` marker when changing its styling.

The command companion retains Rich's terminal-resolved `cyan` for table IDs;
it does not define a second fixed hex palette.

## Typography

The user's terminal supplies the monospace font, character size and line height.
The terminal has no application font family or size ramp to reproduce. Hierarchy uses
position, blank rows, color and terminal bold: the header, pane titles, selected
actions, focused buttons and recording state are emphasized; reading text stays
regular. State names and saved-meeting section labels use uppercase.

**The Terminal Type Rule.** Build hierarchy within the terminal character grid.
Do not invent web-font, pixel-size or numeric-weight tokens for terminal bold.

The browser preview uses the recorded `preview-body` and `preview-code` roles.
Its first-level headings are 32px with a 1.2 line height, reducing to 26px at the
600px breakpoint; second-level headings are 22px. The brand and code retain
monospace; figure controls use 14px Arial. These browser measurements do not
change the terminal's typography.

## Layout

At 110 columns and wider, native framed boxes contain a 25-column action-menu
interior, a flexible reading pane, and a 42-column stack of Copilot suggestions
and commitments. Below 110 columns, the menu is hidden and the reader sits above
a side-by-side pair of assistant frames. That assistant region occupies five rows
when terminal height is below 28 rows, otherwise eight. Shortcuts and the command
bar retain access to actions when the menu is hidden.

The workspace reader stacks its selector, a one-row divider and workspace details.
The selector shows up to seven rows, bounded by the number of workspace entries
and available terminal height; at 80 × 24 it uses up to three rows so details and
assistant frames remain visible. Lists and reading content scroll within their
regions rather than increasing the screen's required height.

The header occupies two rows, the reading-pane heading two rows, the status area
two wrapping rows, and the shortcut footer one row. Content uses blank rows and
short leading spaces for separation. A framed one-line command input remains
above the footer. Measurements are terminal cells, not pixels.
The existing command tables are borderless with zero vertical and two horizontal
cells of padding.

The browser preview centers content in a maximum 1500px main region with 28px
padding, reduced to 16px at widths up to 600px. Paragraphs and list items use a
100-character maximum line width. Diagram figures scroll horizontally: their SVG
keeps a 900px minimum width so narrow screens preserve the diagram's readable
layout. The surrounding Markdown adapts to the viewport.

## Elevation & Depth

Flat tonal surfaces separate menu, content and status. Dialogs use the raised
slate surface and native terminal frames. No shadow or animation scale is defined.

## Shapes

The dashboard uses rectangular character-grid regions, native box-drawing frames between
panes and a native scrollbar. Dialog framing comes from prompt_toolkit. There is
no terminal radius or border-token system. The browser viewer uses thin slate
figure borders and rectangular code surfaces; its Download SVG button has 4px
rounded corners.

## Components

### Action and navigation lists

Rows use explicit labels. Arrow keys move selection and Enter activates; mouse
release also activates a row. A cyan background, bold text and `>` identify the
selected row only while its list is focused. Selection scrolls into view.

The action list offers Record meeting / Live transcript, Stop & save, Previous
meetings, Workspaces, Workspace tasks, New task, configuration, shell, help and
quit. Workspace and task views add relevant actions using explicit labels;
the footer changes with the open view and task state. The stopped state labels
Stop as inactive and explains it if invoked. History rows pair the local date
and timezone with a saved meeting title.

### Workspaces and context

**W** opens a selector above the active workspace's details. The selector starts
with Create workspace, marks the current workspace with `*`, and labels paused
workspaces. Details show task and saved-meeting counts, attached context files
and instructions. **F** opens a file-path dialog; **I** edits shared guidance for
Copilot and tasks. Empty sections state how to add their first content. The
`source ID` command opens an attachment in the reader; Esc returns to Workspaces.

**P** toggles new task starts, with text explaining that a running task continues.
Recording must stop and save before switching workspaces. Browsing the current
workspace's tasks and context remains available during capture.

### Tasks and artifact review

**T** opens a list beginning with New task. Each row shows the task ID, explicit
state, capability and title. **N** opens a title dialog followed by a capability
selector: Write, Research with Exa or workspace evidence, Visualize, or Present.
Completing the dialogs queues a task; generation starts with **G**.

The task reader shows the brief, evidence mode, state-specific actions and either
the live draft, saved artifact or run error. Draft source remains readable as
plain terminal text, including Mermaid and Markdown slide outlines.

| State label | Reader actions and meaning |
| --- | --- |
| Queued | G runs the task; E edits the brief. |
| Running | The live draft is labeled as not yet saved; X cancels this dashboard's run. |
| Failed · retry | The run error remains readable; G retries and E edits the brief. |
| Review draft | Read the saved artifact, then V approves or E requests revision. |
| Approved | The artifact is saved locally and the completed review is explicit. |

Revision dialogs name the task ID and title. E applies only to an open queued,
failed or reviewable task; feedback queues a new attempt, then G generates it.
T or Esc returns from an artifact to Tasks.

**The Review Before Completion Rule.** Keep queued work, streamed drafts, saved
drafts and approved artifacts visibly distinct. An artifact approval command
opens an unseen draft first; approval requires the displayed saved draft.
Approval records a local review decision and sends or publishes nothing.

### Local artifact preview

**O / Open preview** opens a saved artifact as a local standalone browser HTML
page. Formatted Markdown supplies the reading structure; a bundled offline
Mermaid renderer turns diagram fences into SVG inside bordered figures. The
viewer uses the dashboard's slate and cyan palette with the preview-specific
border, quote-text and code-surface additions.

Each figure shows rendering status and **Download SVG**, disabled until its SVG
is ready. Mermaid source stays in a collapsed disclosure below the diagram.
Rendering errors explain how to inspect the source or request a CLI revision.
Buttons, source disclosures and links have a peach focus outline. Narrow figures
scroll horizontally while the page's text stays within the viewport.

The preview is saved alongside the original Markdown and loads no remote assets.
Opening it or downloading an SVG leaves the artifact and task review state
unchanged; V / E remain the task's approval and revision controls in the CLI.

### Reading pane

The read-only text area supports arrow keys, Page Up, Page Down and a scrollbar.
Live caption blocks contain elapsed time, source and transcript text. New captions
follow the end only while the reader remains there; scrolling back preserves the
reader's place. Saved meetings show title, local date, optional notes and transcript.
An empty history provides a direct recording instruction. Task streaming follows
the same preserve-the-reader's-place behavior as live captions.

### Copilot, commitments and command input

Copilot and commitment frames remain present across meeting, workspace and task
views. Captions and Copilot continue while a workspace task runs or the user reads
another pane. Switching workspaces after capture stops restores that workspace's
session captions and commitments; the suggestion pane resets for its context.

The commitment pane names each commitment's ID, capability and state. Its text
offers `approve c1` / `dismiss c1`; approval displays the queued task ID and a
route to Tasks. Commitment approval queues work; artifact approval reviews the
saved result. The framed command input accepts these commands and questions.
**/** focuses it, and letter shortcuts become ordinary text while it is focused.

### Header, status and shortcuts

The header keeps the workspace and recording phase visible, adding elapsed time
during capture and a task ID with running or cancelling state during generation.
Status text reports progress, success or failure. Longer recovery details appear
in the reading pane. Tab and Shift-Tab cycle the visible controls; Workspaces
includes separate stops for the selector and details. Focused pane headings add
relevant navigation hints. H opens help, including actions beyond the footer.

### Configuration dialogs

Native input and radio-list dialogs handle workspace creation, attachments,
instructions, new tasks, revisions and audio configuration. The speech-key dialog
hides entered text. Dialogs share the slate palette, cyan frame labels and cyan
focused-button treatment. Text explains cancellation and unchanged settings.

**The Single Terminal Owner Rule.** Suspend the parent dashboard's rendering and
input while a native dialog owns the terminal, then restore it. Recording and
background task workers continue; they must not repaint over the active dialog.

## Do's and Don'ts

- **Do** keep recording and task state visible while browsing meetings or workspaces.
- **Do** retain named actions, keyboard access and a visible focus marker.
- **Do** preserve the reader's position when live captions arrive.
- **Do** label task progress and show the open task's applicable review actions.
- **Do** keep workspace details usable alongside assistant frames at 80 × 24.
- **Do** sanitize external text through the existing `safe()` rendering path.
- **Do** keep original artifact source and review actions available when offering
  the browser preview.
- **Don't** use color alone to communicate selection, recording or errors.
- **Don't** imply word-by-word captions; explain pauses and provider processing.
- **Don't** apply the browser viewer's CSS measurements or font roles to terminal
  controls.

No sidecar is generated. Native terminal components remain documented as terminal
controls; the browser preview's implementation is recorded directly from its
standalone template.
