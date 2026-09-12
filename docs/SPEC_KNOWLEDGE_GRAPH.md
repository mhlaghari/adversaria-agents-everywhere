# SPEC — Meeting Knowledge Graph View (Phase A: Structured-Data Graph, Zero LLM)

**Status:** Proposed (not implemented). Implementation spec for a human + AI to
build.
**Author:** spec pass, 2026-07-01.
**Scope:** A new graph view in Adversaria that renders meetings, people
(attendees), topics/tags, and action-item owners as nodes with their
relationships as edges — built entirely from existing structured data in SQLite.
Zero new LLM calls. Phase A of what could become a richer knowledge-graph
experience.

> **One-line summary:** Query the existing `meetings`, `attendees`, `tags`, and
> `action_items` tables to construct a `{nodes, edges}` graph payload, render it
> with cytoscape.js (self-hosted, no CDN), and let the user click a node to
> filter related meetings.

---

## 1. Goal & non-goals

### Goal
- A new "Graph" tab in the app that renders an interactive graph view of the
  user's meeting data.
- **Nodes:** meetings (by title), people (attendees), topics (tags), and
  action-item owners (assignees).
- **Edges:** meeting→attendee ("attended"), meeting→tag ("tagged"),
  meeting→owner ("owns-action"), and optionally meeting↔meeting where they share
  an attendee or tag.
- Click a node → filter/scroll the meeting list to show the related meetings.
- **Zero new LLM calls.** All data comes from the existing `get_meetings()`,
  `get_action_items()`, and the structured columns already in SQLite.

### Non-goals (this spec)
- **No entity extraction from transcripts** — that's SPEC_GRAPHRAG territory.
- **No cross-meeting entity resolution** (deciding that "Sarah" and "Sarah Chen"
  are the same person). The graph uses attendee strings as-is.
- **No LLM-generated community summaries or clustering.**
- **No persistent graph storage.** The graph is computed on the fly from the
  existing tables.
- **No graph-based search or retrieval.** This is a visualization, not a RAG
  backend.

### Success criteria
1. With real meetings in the DB, the Graph tab renders nodes for meetings,
   attendees, tags, and owners, connected by edges.
2. Clicking a node filters the meeting list to meetings connected to that node.
3. Empty DB / single meeting renders gracefully (empty state or a single node).
4. `cargo check` + `npx tsc --noEmit` pass.

---

## 2. Approach

### 2a. Data source: existing SQLite tables

The graph is constructed from three queries that are already available:

| Data | Source | Field / table |
|------|--------|---------------|
| Meetings | `get_meetings()` → `Vec<Meeting>` | `meetings` table (`storage.rs:852`) |
| Attendees | `Meeting.attendees` | JSON column, decoded at `storage.rs:596` |
| Tags | `Meeting.tags` | JSON column, decoded at `storage.rs:603` |
| Action items | `get_action_items(None)` → `Vec<ActionItem>` | `action_items` table (`storage.rs:1235`) |

**Node types and dedup:**
- **Meeting nodes:** one per meeting. Key = `meeting-{id}`.
- **Attendee nodes:** one per unique attendee string (case-insensitive dedup).
  Key = `person-{normalized_name}`.
- **Tag nodes:** one per unique tag label. Key = `tag-{label}`.
- **Owner nodes:** one per unique action-item assignee (excluding "Not mine" and
  empties). Key = `owner-{normalized_name}`.

**Edge types:**
- `meeting → attendee`: "attended" (from `meeting.attendees`).
- `meeting → tag`: "tagged" (from `meeting.tags`).
- `meeting → owner`: "owns-action" (from `action_items` where
  `assignee` matches the owner and `meeting_id` matches the meeting).
- `meeting ↔ meeting`: "shared-attendee" or "shared-tag" (computed by
  intersecting attendee/tag sets between meeting pairs).

### 2b. Rust command

```rust
/// Return a graph {nodes, edges} of the user's meetings, built from existing
/// structured data. Zero LLM calls. Node types: "meeting", "person", "tag",
/// "owner". Edge types: "attended", "tagged", "owns-action", "shared-attendee",
/// "shared-tag".
#[tauri::command]
pub async fn get_meeting_graph() -> Result<GraphData, String> {
    let meetings = crate::storage::get_meetings()
        .map_err(|e| format!("Failed to load meetings: {e}"))?;
    let items = crate::storage::get_action_items(None)
        .unwrap_or_default();

    // Build node/edge sets.
    let mut nodes: Vec<GraphNode> = Vec::new();
    let mut edges: Vec<GraphEdge> = Vec::new();
    let mut seen_nodes: std::collections::HashSet<String> = std::collections::HashSet::new();

    let mut meeting_ids: Vec<i64> = Vec::new();

    for m in &meetings {
        let mkey = format!("meeting-{}", m.id);
        add_node(&mut nodes, &mut seen_nodes, &mkey, &m.title, "meeting", Some(m.id));
        meeting_ids.push(m.id);

        // Attendee nodes + edges.
        for a in &m.attendees {
            let a = a.trim();
            if a.is_empty() || a.eq_ignore_ascii_case("me") || a.eq_ignore_ascii_case("them") {
                continue;
            }
            let pkey = format!("person-{}", a.to_lowercase());
            add_node(&mut nodes, &mut seen_nodes, &pkey, a, "person", None);
            edges.push(GraphEdge {
                source: mkey.clone(),
                target: pkey,
                label: "attended".to_string(),
            });
        }

        // Tag nodes + edges.
        for t in &m.tags {
            let tkey = format!("tag-{}", t.label.to_lowercase());
            add_node(&mut nodes, &mut seen_nodes, &tkey, &t.label, "tag", None);
            edges.push(GraphEdge {
                source: mkey.clone(),
                target: tkey,
                label: "tagged".to_string(),
            });
        }
    }

    // Owner nodes + edges (from action items).
    for item in &items {
        let assignee = item.assignee.trim();
        if assignee.is_empty() || assignee.eq_ignore_ascii_case("not mine") {
            continue;
        }
        let okey = format!("owner-{}", assignee.to_lowercase());
        add_node(&mut nodes, &mut seen_nodes, &okey, assignee, "owner", None);
        edges.push(GraphEdge {
            source: format!("meeting-{}", item.meeting_id),
            target: okey,
            label: "owns-action".to_string(),
        });
    }

    // Shared-attendee edges (meeting ↔ meeting).
    let attendee_sets: Vec<(i64, std::collections::HashSet<String>)> = meetings.iter().map(|m| {
        let set: std::collections::HashSet<String> = m.attendees.iter()
            .map(|a| a.trim().to_lowercase())
            .filter(|a| !a.is_empty() && a != "me" && a != "them")
            .collect();
        (m.id, set)
    }).collect();

    for i in 0..attendee_sets.len() {
        for j in i+1..attendee_sets.len() {
            let (id_a, set_a) = &attendee_sets[i];
            let (id_b, set_b) = &attendee_sets[j];
            if set_a.intersection(set_b).next().is_some() {
                edges.push(GraphEdge {
                    source: format!("meeting-{id_a}"),
                    target: format!("meeting-{id_b}"),
                    label: "shared-attendee".to_string(),
                });
            }
        }
    }

    Ok(GraphData { nodes, edges })
}

fn add_node(
    nodes: &mut Vec<GraphNode>,
    seen: &mut std::collections::HashSet<String>,
    key: &str,
    label: &str,
    node_type: &str,
    meeting_id: Option<i64>,
) {
    if seen.insert(key.to_string()) {
        nodes.push(GraphNode {
            key: key.to_string(),
            label: label.to_string(),
            node_type: node_type.to_string(),
            meeting_id,
        });
    }
}
```

### 2c. Rust types (`src-tauri/src/types.rs`)

```rust
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GraphData {
    pub nodes: Vec<GraphNode>,
    pub edges: Vec<GraphEdge>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GraphNode {
    pub key: String,        // unique id: "meeting-42", "person-sarah-chen", "tag-client-meeting"
    pub label: String,      // display text
    pub node_type: String,  // "meeting" | "person" | "tag" | "owner"
    pub meeting_id: Option<i64>, // set only for meeting nodes (for click→navigate)
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GraphEdge {
    pub source: String,     // node key
    pub target: String,     // node key
    pub label: String,      // "attended" | "tagged" | "owns-action" | "shared-attendee" | "shared-tag"
}
```

### 2d. Frontend types (`src/types.ts`)

```ts
export interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface GraphNode {
  key: string;
  label: string;
  node_type: "meeting" | "person" | "tag" | "owner";
  meeting_id: number | null;
}

export interface GraphEdge {
  source: string;
  target: string;
  label: string;
}
```

### 2e. Typed IPC wrapper (`src/lib/tauri.ts`)

```ts
export function getMeetingGraph(): Promise<GraphData> {
  return invoke("get_meeting_graph");
}
```

### 2f. Registration (`src-tauri/src/lib.rs`)

```rust
commands::get_meeting_graph,
```

---

## 3. Rendering: cytoscape.js (self-hosted, no CDN)

### 3a. Why cytoscape.js

- Mature, well-maintained graph visualization library.
- Supports the exact interaction model we need: click a node → callback with the
  node data.
- Lightweight enough for a few hundred nodes (meeting graphs are small — tens to
  low hundreds of meetings).
- No CDN needed — install via npm, bundled with Vite.

### 3b. Privacy: no CDN, self-host like Inter

The project already self-hosts the Inter font (no Google Fonts CDN call). Follow
the same pattern for cytoscape.js:

```bash
npm install cytoscape
```

Import it in `GraphView.tsx`:

```ts
import cytoscape from "cytoscape";
```

The Vite bundler tree-shakes and includes it in the app bundle. Zero external
network requests.

### 3c. GraphView component (`src/components/GraphView.tsx`)

```tsx
import { useEffect, useRef, useState } from "react";
import cytoscape from "cytoscape";
import { getMeetingGraph } from "../lib/tauri";
import type { GraphData, GraphNode } from "../types";

interface GraphViewProps {
  onSelectMeeting?: (id: number) => void;
}

export function GraphView({ onSelectMeeting }: GraphViewProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<cytoscape.Core | null>(null);
  const [data, setData] = useState<GraphData | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getMeetingGraph()
      .then(setData)
      .catch((e) => setError(String(e)));
  }, []);

  useEffect(() => {
    if (!data || !containerRef.current) return;

    const cy = cytoscape({
      container: containerRef.current,
      elements: [
        ...data.nodes.map((n) => ({
          data: {
            id: n.key,
            label: n.label,
            nodeType: n.node_type,
            meetingId: n.meeting_id,
          },
          classes: n.node_type,
        })),
        ...data.edges.map((e) => ({
          data: {
            id: `${e.source}--${e.label}--${e.target}`,
            source: e.source,
            target: e.target,
            label: e.label,
          },
        })),
      ],
      style: [
        {
          selector: "node",
          style: {
            label: "data(label)",
            "text-valign": "center",
            "text-halign": "center",
            "font-size": "11px",
            "background-color": "#4a5568",
            color: "#e2e8f0",
          },
        },
        {
          selector: "node.meeting",
          style: { "background-color": "#3182ce", shape: "round-rectangle" },
        },
        {
          selector: "node.person",
          style: { "background-color": "#38a169", shape: "ellipse" },
        },
        {
          selector: "node.tag",
          style: { "background-color": "#805ad5", shape: "diamond" },
        },
        {
          selector: "node.owner",
          style: { "background-color": "#dd6b20", shape: "triangle" },
        },
        {
          selector: "edge",
          style: {
            width: 1,
            "line-color": "#4a5568",
            "target-arrow-color": "#4a5568",
            "target-arrow-shape": "triangle",
            "curve-style": "bezier",
          },
        },
      ],
      layout: { name: "cose", animate: false },
    });

    cy.on("tap", "node", (evt) => {
      const node = evt.target;
      const meetingId = node.data("meetingId") as number | null;
      if (meetingId && onSelectMeeting) {
        onSelectMeeting(meetingId);
      }
    });

    cyRef.current = cy;
    return () => { cy.destroy(); };
  }, [data]);

  if (error) return <div className="error-banner">{error}</div>;
  if (!data) return <div className="loading">Loading graph…</div>;
  if (data.nodes.length === 0) {
    return <div className="empty-state">No meetings to graph yet. Record or import a meeting to see it here.</div>;
  }

  return <div ref={containerRef} style={{ width: "100%", height: "100%" }} />;
}
```

### 3d. Navigation

Add `"graph"` to the `View` type in `App.tsx` (line 33):

```ts
type View = "meetings" | "settings" | "todos" | "weekly" | "ask" | "graph";
```

Add a "Graph" button in the sidebar navigation. The graph view renders
full-width in the main content area.

When the user clicks a meeting node → switch to the `"meetings"` view and select
that meeting (or open it directly in the NoteViewer).

---

## 4. Alternative: reuse `graphify`

The user maintains a personal knowledge-graph tool called **`graphify`**
(a `graphify` skill + `graphify-vault` MCP that turns notes into an HTML graph).
A faster, code-lighter option is to feed meeting summaries into `graphify` to
produce the graph HTML, and render the resulting HTML in a webview or iframe.

### Trade-off: native cytoscape view vs. reusing graphify

| Factor | cytoscape.js (in-app) | graphify (external) |
|--------|----------------------|---------------------|
| **Integration effort** | New component, npm dep, Rust command | Export summaries → graphify → load HTML |
| **Interactivity** | Click → navigate to meeting (native) | Static HTML (no back-link to app) |
| **Maintenance** | Own the code; update deps like any other | graphify evolves independently |
| **Privacy** | Same as app (fully local) | Same (graphify runs locally) |
| **Data freshness** | Live query from SQLite | Must regenerate on meetings change |
| **Richness** | Only structured data (names, tags, owners) | graphify could ingest full summaries for richer nodes |
| **User fit** | General Adversaria user | User already maintains graphify; natural extension |

**Recommendation:** build the cytoscape.js in-app view (Phase A, this spec).
It's ~200 lines of Rust + one new React component, no external process
dependency, and the click→navigate interaction is Table Stakes for a graph
view. `graphify` can be a later enhancement that enriches nodes with summary
content.

---

## 5. Scope guard

- **Separate view, separate tab.** Do not disturb existing tabs (Meetings,
  To-dos, Weekly, Ask, Settings).
- **Graph value scales with meeting volume.** For a user with < 10 meetings, the
  graph is sparse and low-value. The empty state should acknowledge this:
  "Graphs get richer as you record more meetings."
- **Performance cap:** if the user has > 500 meetings, skip shared-attendee
  edges (O(n²) intersection) and cap the graph to the most recent 500 meetings.
  A warning: "Showing the 500 most recent meetings."

---

## 6. Edge cases

| # | Edge case | Handling |
|---|-----------|----------|
| 1 | **Empty DB** | Return empty `{nodes: [], edges: []}`. GraphView shows an empty-state message. |
| 2 | **Single meeting** | One meeting node + its attendees/tags/owners. No shared edges (need ≥ 2 meetings). The graph still renders — a star around the single meeting. |
| 3 | **Huge graphs (> 500 meetings)** | Cap meetings to 500 most recent (by `recorded_at DESC`). Skip O(n²) shared-attendee edge computation. |
| 4 | **Arabic / RTL names** | Dedup by case-insensitive lowercase. Arabic names work correctly in JSON strings. Cytoscape renders Unicode labels. |
| 5 | **Attendee name variants** ("Sarah", "Sarah Chen", "sarah chen") | No entity resolution in v1 — each variant is its own node. This is a known limitation; the graph makes it visually obvious that they should be merged, which motivates the user to clean up attendee names in the meeting view. |
| 6 | **Meeting with no attendees, no tags, no action items** | The meeting node appears but has no edges. This is correct — it's a disconnected node. |
| 7 | **Browser/node not supporting cytoscape** | cytoscape.js works in all modern browsers (including the Tauri webview). No known compatibility issues. |

---

## 7. Phasing

**Phase A (this spec) — Structured-data graph, zero LLM.**
- Rust: `get_meeting_graph()` command + types.
- Frontend: `GraphView.tsx` with cytoscape.js (self-hosted).
- Navigation: "Graph" tab in the sidebar.
- Interaction: click → filter/navigate to meeting.

**Phase B (future) — Enrich with summary content.**
- Optionally feed summaries to `graphify` for richer HTML rendering.
- Add "Export for graphify" button.

**Phase C (future) — LLM entity resolution (→ SPEC_GRAPHRAG).**
- Merge name variants ("Sarah" / "Sarah Chen") via LLM adjudication.
- Cross-meeting entity extraction from transcripts.

---

## 8. Verification commands

```bash
# Rust
cd src-tauri && cargo check

# Frontend
npx tsc --noEmit

# Python (no changes)
cd python-service && uv run pytest
```

### Manual verification
1. Open the Graph tab with meetings in the DB → nodes and edges render.
2. Click a meeting node → navigates to that meeting in the list/NoteViewer.
3. Click a person/tag/owner node → meeting list filters to related meetings.
4. Delete all meetings → Graph shows empty state.
5. Import meetings → Graph updates.

---

## 9. Docs to update when implementing

- `docs/ARCHITECTURE.md` — the graph layer (Rust-only; no Python changes).
- `docs/HANDOFF.md` — note the new Graph tab and cytoscape.js dep.
- `docs/TODO.md` — move knowledge graph from planned to phased tasks.
