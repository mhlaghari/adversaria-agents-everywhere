---
name: Adversaria CLI
description: A keyboard-first terminal companion for recording and reading meetings.
colors:
  background: "#17212b"
  text: "#e5edf3"
  raised-surface: "#253545"
  header-text: "#f2f6fa"
  accent: "#79d4e4"
  muted: "#b0bdc9"
  menu-surface: "#1d2b38"
  attention: "#ffbcad"
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
---

# Design System: Adversaria CLI

## Overview

**Creative North Star: "The Meeting Companion"**

Adversaria uses the terminal's own character grid and controls to keep recording,
live captions and saved meetings within reach. Cyan identifies headings and
focus; slate surfaces divide actions from reading. The persistent action menu
and status lines make the current operation visible while the reading pane changes.

This records the implemented `STYLE`, `ActionList` and `Dashboard` in
`adversaria_cli/dashboard.py`, with the existing command output in
`adversaria_cli/ui.py` as context. The product scope is documented in `README.md`.

**Key Characteristics:**

- Explicit text actions with visible keyboard shortcuts.
- A spacious reading pane beside, or below, a compact action list.
- Persistent recording state, progress messages and recovery instructions.

## Colors

The dashboard combines cool slate surfaces, pale text, cyan emphasis and warm
attention text. Frontmatter colors record the native prompt_toolkit palette.

### Primary

- **Accent cyan:** pane titles, brand name, selected actions, focused dialog
  buttons and the scrollbar thumb. Selected surfaces use dark background-colored
  text for contrast.

### Secondary

- **Attention peach:** active recording phases and error messages. The words
  distinguish recording from failure; the color alone does not.

### Neutral

- **Background slate:** main canvas and transcript surface.
- **Menu slate:** action and meeting-list surfaces.
- **Raised slate:** header, status bar, dialogs and scrollbar track.
- **Pale text / header text:** reading content and the header's brighter text.
- **Muted slate text:** secondary instructions, idle state and shortcut footer.

**The Explicit State Rule.** Pair state color with readable status text or a
selection marker. Retain the focused row's `>` marker when changing its styling.

The command companion retains Rich's terminal-resolved `cyan` for table IDs;
it does not define a second fixed hex palette.

## Typography

The user's terminal supplies the monospace font, character size and line height.
There is no application font family or size ramp to reproduce. Hierarchy uses
position, blank rows, color and terminal bold: the header, pane titles, selected
actions, focused buttons and recording state are emphasized; reading text stays
regular. State names and saved-meeting section labels use uppercase.

**The Terminal Type Rule.** Build hierarchy within the terminal character grid.
Do not invent web-font, pixel-size or numeric-weight tokens for terminal bold.

## Layout

At 110 columns and wider, native framed boxes contain the action menu, transcript,
and a 42-column stack of Copilot suggestions and commitments. Narrower terminals
place the transcript above an eight-row pair of assistant panes. A framed command
bar accepts questions and commitment approvals; shortcuts remain visible.

The header occupies two rows, the reading-pane heading two rows, the status area
two wrapping rows, and the shortcut footer one row. Content uses blank rows and
short leading spaces for separation. Measurements are terminal cells, not pixels.
The existing command tables are borderless with zero vertical and two horizontal
cells of padding.

## Elevation & Depth

Flat tonal surfaces separate menu, content and status. Dialogs use the raised
slate surface and native terminal frames. No shadow or animation scale is defined.

## Shapes

The dashboard uses rectangular character-grid regions, native box-drawing frames between
panes and a native scrollbar. Dialog framing comes from prompt_toolkit. There is
no application radius or border-token system.

## Components

### Action and meeting lists

Rows use explicit labels. Arrow keys move selection and Enter activates; mouse
release also activates a row. A cyan background, bold text and `>` identify the
selected row only while its list is focused. Selection scrolls into view.

The action list offers Record meeting / Live transcript, Stop & save, Previous
meetings, Audio inputs, Speech API key, Command shell and Quit. The stopped state
labels Stop as inactive and explains it if invoked. History rows pair the local
date and timezone with a saved meeting title.

### Reading pane

The read-only text area supports arrow keys, Page Up, Page Down and a scrollbar.
Live caption blocks contain elapsed time, source and transcript text. New captions
follow the end only while the reader remains there; scrolling back preserves the
reader's place. Saved meetings show title, local date, optional notes and transcript.
An empty history provides a direct recording instruction.

### Header, status and shortcuts

The header keeps the workspace and recording phase visible, adding elapsed time
during capture. Status text reports progress, success or failure. Longer recovery
details appear in the reading pane. Tab switches panes; focused pane headings add
relevant navigation hints. The footer repeats the primary shortcuts.

### Configuration dialogs

Native radio lists select microphone and optional loopback inputs. The speech-key
dialog hides entered text. Dialogs share the slate palette, cyan frame labels and
cyan focused-button treatment. Text explains cancellation and unchanged settings.

## Do's and Don'ts

- **Do** keep recording state visible while browsing saved meetings.
- **Do** retain named actions, keyboard access and a visible focus marker.
- **Do** preserve the reader's position when live captions arrive.
- **Do** sanitize external text through the existing `safe()` rendering path.
- **Don't** use color alone to communicate selection, recording or errors.
- **Don't** imply word-by-word captions; explain pauses and provider processing.
- **Don't** introduce CSS, font, shadow or radius tokens that the terminal does
  not implement.

No browser sidecar is generated: the documented components are Python terminal
controls, and the sidecar's HTML/CSS previews would invent a different renderer.
