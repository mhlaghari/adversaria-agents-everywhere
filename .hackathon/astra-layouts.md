## 1. Companion narrow layout

**Ship a pinned CAUGHT area, a fixed transcript pane, and independently scrolling answers.** Preserve the existing visual style.

The breakpoint is **900px**, not 980px. The latter only rearranges Copilot controls. Layout currently follows config alone, and the transcript sheet overlays the transcript. (`src/prototype.css:4883`, `src/prototype.css:5385`, `src/components/RecordingCompanion.tsx:82`, `src/prototype.css:5432`.)

**Derive layout with `matchMedia`.** This matches the existing viewport breakpoint and the companion’s hidden sidebar. A root `ResizeObserver` adds unnecessary sizing logic here. Keep `recording_view` untouched: compact below 900px; honor the configured variant above it. (`src/prototype.css:4360`, `src/App.tsx:163`, `src/App.tsx:618`, `src/App.tsx:1502`.)

```tsx
const wideQuery = "(min-width: 900px)";
const [wide, setWide] = useState(
  () => window.matchMedia(wideQuery).matches
);

useEffect(() => {
  const media = window.matchMedia(wideQuery);
  const update = () => setWide(media.matches);
  update();
  media.addEventListener("change", update);
  return () => media.removeEventListener("change", update);
}, []);

const layout = !wide
  ? "compact"
  : variant === "transcript" ? "transcript" : "balanced";
```

Restrict `isCopilotFocus` to `layout === "transcript"` so compact never inherits the 26% transcript cap. (`src/components/RecordingCompanion.tsx:469`, `src/prototype.css:5389`.)

**Visible without scrolling at 380–520 × 720:**

- **44px recording bar:** recording dot, elapsed time, Browse, Stop & summarize. Hide the wordmark, waveform and redundant “Recording” text.
- **28px status button:** current provider, folder and actual readiness, ending in “Tools”. Indexing and errors replace the ready count.
- **CAUGHT, maximum 184px:** pending commitments first, newest first. The first demo commitment shows its sentence, owner, deadline, type selector, Approve and Dismiss. Older commitments scroll inside this area.
- **176px transcript:** approximately six readable lines, with its own scroll position.
- **Answers:** at least 244px with the maximum CAUGHT area. Show the latest question and streaming Say text. Collapse Specifics and From your notes under “More”; retain Context and Sources disclosures.
- **44px notes footer:** one visible input line. Expand the footer to 88px only while focused, then collapse even when nonempty.

The current readiness string already distinguishes indexing, errors and source counts; preserve those conditions. The existing notes footer instead stays expanded whenever it contains text. (`src/components/RecordingCompanion.tsx:415`, `src/components/RecordingCompanion.tsx:358`.)

**Tabs disappear in compact.** Copilot is always present; Notes becomes the footer; Last time, attachments, consent and the mic-question checkbox move into a **nonmodal Tools sheet occupying only the Answers area**. It never covers CAUGHT or transcript. Escape and Close restore focus to Tools. Keep Answer current question beside the ANSWERS heading.

Component tree below shows the compact composition. Named components extract existing JSX. Keep one mounted `CommitmentCard` list across width changes, using CSS placement rather than separate desktop/mobile copies. Its approval result and artifact shortcut currently live inside the card. (`src/components/CommitmentCard.tsx:37`, `src/components/CommitmentCard.tsx:49`.)

```tsx
<div className="companion-layout" data-layout={layout}>
  <RecordingBar className="companion-recbar" />
  <button className="companion-status" onClick={openTools}>
    {statusLabel} · Tools
  </button>

  <div className="companion-body">
    <TranscriptPane className="companion-transcript" />

    <div className="companion-right">
      <section className="companion-caught" hidden={!hasCommitments}>
        <div className="companion-section-label">CAUGHT {tapCountLabel}</div>
        <div className="companion-caught-list">
          {commitmentCards}
        </div>
      </section>

      <section className="companion-answers">
        <AnswerHeading onForceCard={forceCurrentQuestion} />
        <CopilotCards {...copilotProps} showControls={false} compact />
        {toolsOpen && (
          <MeetingToolsSheet
            className="companion-tools-sheet"
            onClose={closeTools}
          />
        )}
      </section>
    </div>
  </div>

  <NotesFooter className="companion-notefoot" />
</div>
```

Lift the mic flag and its existing persistence handler into the companion; share that value between Tools and the manual-answer action. These currently belong to `CopilotCards`. (`src/components/CopilotCards.tsx:147`, `src/components/CopilotCards.tsx:227`.)

Append this block after existing companion rules:

```css
@media (width < 900px) {
  .companion-layout[data-layout="compact"] {
    display: grid;
    grid-template-columns: minmax(0, 1fr);
    grid-template-rows: 44px 28px minmax(0, 1fr) 44px;
    height: 100%;
    min-height: 0;
    overflow: hidden;
  }
  .companion-layout[data-layout="compact"]:has(
    .companion-notefoot-input:focus
  ) {
    grid-template-rows: 44px 28px minmax(0, 1fr) 88px;
  }

  .companion-chrome, .companion-waveform,
  .companion-status-label, .companion-tabs,
  .companion-divider { display: none; }

  .companion-recbar {
    box-sizing: border-box;
    height: 44px;
    padding: 4px 10px;
    gap: 8px;
  }
  .companion-recbar button { min-height: 36px; }
  .companion-status {
    min-width: 0;
    padding: 0 10px;
    border: 0;
    background: var(--bg-secondary);
    color: var(--text-secondary);
    font-size: 11px;
    text-align: left;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .companion-body {
    display: grid;
    grid-template-columns: minmax(0, 1fr);
    grid-template-rows: auto 176px minmax(0, 1fr);
    grid-template-areas: "caught" "transcript" "answers";
    min-height: 0;
    overflow: hidden;
  }
  .companion-right { display: contents; }
  .companion-caught {
    grid-area: caught;
    max-height: 184px;
    overflow: hidden;
    padding: 0 10px;
  }
  .companion-caught[hidden] { display: none; }
  .companion-caught-list {
    max-height: 160px;
    overflow-y: auto;
    overscroll-behavior: contain;
  }
  .companion-caught .companion-section-label {
    box-sizing: border-box;
    height: 24px;
    padding: 4px 0;
    margin: 0;
    color: var(--accent-amber);
  }
  .companion-caught .commitment-card {
    padding: 8px;
    gap: 6px;
    margin-bottom: 6px;
  }
  .companion-caught .commitment-text {
    font-size: 14px;
    line-height: 20px;
    max-height: 60px;
    overflow-y: auto;
  }
  .commitment-actions {
    display: grid;
    grid-template-columns: minmax(0, 1fr) 80px 68px;
    gap: 6px;
  }
  .commitment-actions-spacer, .commitment-type-label { display: none; }
  .commitment-type { min-width: 0; }
  .commitment-type-select { width: 100%; min-width: 0; }
  .commitment-actions button, .commitment-type-select { height: 36px; }

  .companion-layout[data-layout="compact"] .companion-transcript {
    grid-area: transcript;
    min-height: 0;
    max-height: none;
    border-block: 1px solid var(--border-color);
  }
  .companion-feed { min-height: 0; overflow-y: auto; }
  .companion-feed-line {
    max-width: none;
    margin: 0;
    font-size: 14px;
    line-height: 21px;
    color: var(--text-secondary);
  }

  .companion-answers {
    grid-area: answers;
    position: relative;
    display: flex;
    flex-direction: column;
    min-height: 0;
    overflow: hidden;
  }
  .companion-answers .copilot-cards,
  .companion-answers .copilot-list {
    flex: 1;
    min-height: 0;
  }
  .companion-answers .copilot-list {
    overflow-y: auto;
    overscroll-behavior: contain;
  }
  .copilot-card { flex-shrink: 0; }
  .companion-tools-sheet {
    position: absolute;
    inset: 0;
    z-index: 3;
    overflow-y: auto;
    padding: 10px;
    background: var(--bg-primary);
  }
  .companion-notefoot { padding: 6px 10px; }
  .companion-notefoot-input,
  .companion-notefoot-input.expanded {
    box-sizing: border-box;
    height: 32px;
    font-size: 14px;
  }
  .companion-notefoot-input:focus { height: 76px; }
}
```

**Arrival behavior:** on a new caught ID, scroll only the CAUGHT list to zero and announce “Commitment needs your approval”. Keep keyboard focus unchanged. Preserve the transcript’s existing follow-latest threshold and Jump button. Answer tokens must never scroll either region. (`src/components/RecordingCompanion.tsx:381`, `src/components/RecordingCompanion.tsx:390`.)

Approved cards become 44px progress rows beneath pending cards. Show capability, stage, and one shortcut: Open artifact when available, otherwise Open in Workspaces. Preserve their mounted state and existing polling. (`src/components/CommitmentCard.tsx:54`, `src/components/CommitmentCard.tsx:226`.)

**Fallback:** retain these same bands and priorities, but replace the Tools sheet with native `<details>` inside the Answers area. Its expanded content scrolls there. This removes sheet positioning and focus-management work.

## 2. Companion wide layout

At the configured 1024×720 window, make only these six corrections. (`src-tauri/tauri.conf.json:57`.)

1. Set the transcript basis to **320px** at 900–1199px, replacing the current `34vw` allocation. (`src/prototype.css:4887`.)
2. Make the tabs **36px high**, with `padding: 0 10px`; preserve all three. (`src/prototype.css:4913`.)
3. Move CAUGHT outside the scrolling tab panel, immediately below the tabs, so it remains visible while Notes is selected. Cap its list at **200px**. (`src/components/RecordingCompanion.tsx:765`.)
4. Make the answer panel a bounded flex column with `overflow:hidden`; give `.copilot-list` `min-height:0; overflow-y:auto`. Its current `overflow:visible` prevents its scroll logic from owning the actual scrolling. (`src/prototype.css:4846`, `src/prototype.css:5105`, `src/components/CopilotCards.tsx:156`.)
5. Put readiness and consent access in one **32px** row. Move privacy explanation and mic setup into its disclosure; keep manual answer visible. (`src/components/RecordingCompanion.tsx:767`, `src/components/CopilotCards.tsx:219`.)
6. Increase untapped cards’ amber inset edge to **3px**; change the Say eyebrow to muted text so amber identifies required action. (`src/prototype.css:8095`, `src/prototype.css:5439`.)

## 3. Workspaces detail view for the demo

**Lead with Tasks, with the diagram already visible under its awaiting-review row.**

Preserve Needs you → Running → Queued → Done. A completed run correctly produces an `awaiting_review` task, not a Done task. (`src/components/workspaces/WorkspaceDetailView.tsx:1330`, `src-tauri/src/storage.rs:6967`.)

At widths through **1120px**:

- Set `.ws-detail-grid` to one column.
- Move New task below Tasks into a closed disclosure.
- Put Project brain below Tasks in a closed “Context” disclosure.
- Allow task titles two lines; use a **36px text Approve button**.
- Keep Research collapsed initially; display the Visualize preview at **240px high**, full row width.

These replace the current competing columns, prominent creation form and single-line titles. (`src/prototype.css:7161`, `src/components/workspaces/WorkspaceDetailView.tsx:1230`, `src/prototype.css:6756`.)

**What preview handles today:**

| Format | Current behavior |
|---|---|
| Markdown | Rendered through `markdownToHtml`. |
| TXT/JSON/CSV/YAML/log | Plain text preview. |
| HTML/SVG | Read as text, then unsupported-file message. |
| PNG | No image renderer; the text reader generally rejects its bytes. |
| `.drawio` XML | Reading is skipped; offers Open in draw.io. |

Anchors: `src/components/workspaces/ArtifactPreview.tsx:34`, `src/components/workspaces/ArtifactPreview.tsx:70`, `src-tauri/src/commands.rs:6910`.

**What Local actually does:** `visualize` requests self-contained HTML containing standalone SVG, but its installed adapter is `drawio-diagram`, whose instructions request `<topic>.drawio` plus `<topic>.md`. That adapter is selected during commitment staffing. (`src-tauri/src/workspace_runs.rs:75`, `src-tauri/src/workspace_runs.rs:535`, `src-tauri/src/addons.rs:34`, `src-tauri/src/commands.rs:6026`.)

Local calls `draft_stream`, parses file blocks, writes their supplied filenames, and writes leftover prose to **`draft.md`**. There is no guaranteed Visualize filename. Draw.io validation produces warnings; this path does not export SVG or PNG. (`src-tauri/src/commands.rs:7212`, `src-tauri/src/commands.rs:7238`, `src-tauri/src/commands.rs:7262`.)

**Settle the output contract:** for Local Visualize, exclude the drawio adapter at execution and require:

```text
=== FILE: solutions-architecture.html ===
```

Follow with one complete HTML document containing one standalone SVG, `viewBox="0 0 960 360"`, at most six source-grounded nodes, short labels, presentation attributes and no external assets. Put a short legend inside the SVG. No additional files.

Apply this through the Local instruction at `src-tauri/src/commands.rs:6743` and the selected skills at `src-tauri/src/commands.rs:7071`. Also change the Markdown-only opening of `DRAFT_SYSTEM_PROMPT` to “Write the complete deliverable in the format requested by the brief.” (`python-service/src/summarizer.py:55`.)

**Smallest preview change:** support `.html` by extracting its first SVG with `DOMParser`; support `.svg` directly. Serialize with `XMLSerializer`, ensuring the SVG namespace, and display an image:

```tsx
<img
  className="ws-diagram-preview"
  src={`data:image/svg+xml;charset=utf-8,${encodeURIComponent(svgText)}`}
  alt={`${artifact.name}: solutions architecture diagram`}
/>
```

Use `width:100%; height:240px; object-fit:contain; background:#fff`. Reject missing SVG, XML parser errors and image load failures with “Diagram preview unavailable”. Keep existing Open/Reveal actions. The current CSP already permits data images. (`src-tauri/tauri.conf.json:68`.)

In `renderTaskRow`, select the latest run’s `solutions-architecture.html`, then SVG, then other HTML, with filename sorting as the tie-breaker. Render its preview **after the row and outside `{expanded && ...}`** when capability is Visualize and status is awaiting_review. Exclude that artifact from the expanded duplicate list. Current previews require both row expansion and Preview. (`src/components/workspaces/WorkspaceDetailView.tsx:912`, `src/components/workspaces/WorkspaceDetailView.tsx:898`, `src/components/workspaces/WorkspaceDetailView.tsx:1086`.)

Clear preview/run caches only when workspace ID changes, not on every detail refresh; key artifact reads by ID/path. Existing resets would cause avoidable flashing. (`src/components/workspaces/WorkspaceDetailView.tsx:495`, `src/components/workspaces/ArtifactPreview.tsx:53`.)

**Timing verdict:** there is no verified two-minute guarantee from this read-only review. The unmodified path cannot deliver the required inline preview regardless of model speed. Qualify the new HTML/SVG path with one rehearsal while recording. If the diagram takes over **60 seconds**, use a preserved successful rehearsal task and explicitly identify it as earlier work. Do not substitute its artifact into a fresh run.

## 4. Demo action items

**Speak Visualize first**, because execution is serial within a workspace. (`src-tauri/src/commands.rs:6961`.)

1. **“I will create a solutions architecture diagram for Wael by Monday.”**
2. **“I will check the SIDRA thresholds against the manual for Wael before Friday.”**

Both match the detector. The Visualize branch landed during this review and recognizes the first; `check` maps the second to Research. (`src-tauri/src/copilot_session.rs:44`, `src-tauri/src/copilot_session.rs:92`, `src-tauri/src/copilot_session.rs:113`.)

The task titles are those sentences verbatim, including punctuation if retained by transcription. Both are below the 120-character title limit. Their details are exactly these templates, with actual capture time and session ID substituted. (`src-tauri/src/copilot_session.rs:1428`.)

```text
Caught live during the meeting at HH:MM from Me.
Owner: Wael. Deadline: by Monday.
Session: SESSION_ID
```

```text
Caught live during the meeting at HH:MM from Me.
Owner: Wael. Deadline: before Friday.
Session: SESSION_ID
```

Expected artifacts after the contract fix: **`solutions-architecture.html`** and **`draft.md`**. Require Research to return plain Markdown without file markers, capped at 350 words.

Pause after each sentence until its card appears, then Approve. Commitments are assembled at a silence boundary. Remove the old “Yes,” and “And” prefixes, which fail the anchored patterns. (`src-tauri/src/copilot_session.rs:456`, `.hackathon/demo-script.md:11`.)

Before filming, prepare an **Interviews** workspace with Local selected, the SIDRA manual and architecture context attached, and agents resumed. A matching workspace name determines commitment routing. After Stop, click **Workspaces → Interviews**; the current view initially opens its workspace list. (`src-tauri/src/storage.rs:5514`, `src/components/WorkspacesView.tsx:32`, `src/components/WorkspacesView.tsx:264`.)

## 5. Cut list

Drop in this order:

1. Wide cosmetic corrections, retaining scroll ownership and pinned CAUGHT.
2. Workspaces Context disclosure polish.
3. Tools sheet implementation; activate the native-details fallback.
4. Live diagram generation during the take; use the explicitly labelled rehearsal result.

Never cut transcript visibility, approval controls, truthful task status or inline diagram preview.

Allocate **45 minutes companion, 25 minutes Workspaces/preview, 20 minutes verification**. Verify 380, 520, 899, 900 and 1024px widths, including streaming plus two commitments, resize during approval, notes retention and review preview. Run the build and affected existing tests. Freeze by **15:15**, leaving rehearsal time before 15:30.

Read-only review completed; no files changed.