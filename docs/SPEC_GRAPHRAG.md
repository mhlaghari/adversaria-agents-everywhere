# SPEC — GraphRAG for Cross-Meeting Ask (DESIGN / RESEARCH DOC)

**Status:** Research / design document. NOT an implementation task list. This
document surveys the problem, proposes a phased approach, flags the hard parts,
and recommends a spike to validate feasibility **before building anything**.

**Author:** research + design pass, 2026-07-01.
**Scope:** Design a GraphRAG pipeline for Adversaria's cross-meeting Ask feature
that moves beyond the current keyword-ranked RAG (`ask_all_meetings` in
`commands.rs:1152`) toward graph-aware retrieval that can answer "global"
questions.

> **One-line summary:** Propose a phased GraphRAG design — entity+relationship
> extraction across meeting summaries, entity resolution (the genuinely hard
> part), community detection + summaries, and a hybrid retrieval that combines
> graph traversal with the existing FTS5 + keyword RAG for Ask. Lead with honest
> constraints: local-model quality, many-LLM-call cost, and value scaling with
> meeting volume. Recommend a spike before committing.

---

## 0. HONEST CONSTRAINTS — READ THIS FIRST

This section must be understood before any implementation is attempted. Do not
soften these.

### 0a. Microsoft's GraphRAG was designed for GPT-4-class models

Microsoft's [GraphRAG paper](https://arxiv.org/abs/2404.16130) and
implementation use GPT-4o for entity extraction, relationship extraction, entity
resolution, and community summarization. Adversaria runs a **local ~35B
parameter model** (qwen3.6-35b on MLX, or the user's Ollama model — possibly as
small as llama3.1:8b by default).

**Entity/relationship extraction quality will be noisier on a local model.**
Names will be misspelled, entities will be split when they should be merged,
some relationships will be hallucinations, and some real relationships will be
missed. The extraction prompt must be carefully tuned and validated against real
transcripts on the actual local model — not against GPT-4.

### 0b. Entity resolution is the genuinely hard part

Deciding that "Q3 project" in meeting A is the same entity as "Q3 planning" in
meeting B is a **coreference resolution** problem that even large cloud models
struggle with. On a local 35B, the error rate will be meaningful. The community
detection and summary quality downstream are only as good as the resolution
upstream — garbage entities → garbage communities.

### 0c. It's many LLM calls → slow + costly locally

A typical GraphRAG run on 100 meetings does:
- 1 extraction call per meeting (100 calls)
- 1 entity-resolution call per candidate merge pair (potentially thousands)
- 1 community-summary call per community (10s to 100s)

On a local GPU (RTX 5090 32 GB, ~60 tok/s at 35B), 100 extraction calls on
~500-token summaries is manageable (~minutes). A few thousand resolution calls
is not (~hours). The design must minimize LLM calls by doing embeddings-based
pre-filtering before adjudication.

### 0d. Value scales with meeting volume

A user with 10 meetings gets minimal value from GraphRAG — the keyword-rank RAG
(`ask_all_meetings`) already handles "search across 10 transcripts" well. A user
with 200+ meetings across multiple projects/clients is where GraphRAG shines:
"what are the recurring themes across all my client meetings?", "everything I've
discussed with X across projects", "which projects have stalled?"

**This is a power-user feature.** Ship it too early and it's dead weight.

---

## 1. Goal & non-goals

### Goal
Design a GraphRAG pipeline that extends Adversaria's existing cross-meeting Ask
(`ask_all_meetings` at `commands.rs:1152`) with graph-aware retrieval so it can
answer "global" questions that flat keyword/RAG cannot.

### Non-goals (this design doc)
- **This is not a build spec.** It's a research doc + phased plan. Implementation
  should not start until the spike (§7) validates feasibility.
- **Not replacing the existing Ask pipeline.** GraphRAG is an additional
  retrieval layer; the existing FTS5 + keyword-rank path (`rank_meetings` +
  `search_meeting_ids` in `commands.rs`) stays as the fallback and for simple
  queries.
- **Not real-time.** Graph construction is a periodic/indexing job, not a
  per-query operation. Trigger it when new meetings are added, or on demand.

---

## 2. What the current Ask pipeline does (baseline)

Understanding the starting point is essential. The current `ask_all_meetings`
(commands.rs:1152-1297):

1. **Router:** one LLM call triages the question (is it about meetings? what
   intent? condense pronouns into a standalone question).
2. **Retrieval:** FTS5 full-text search (`search_meeting_ids`) over
   `meetings_fts(title, summary, transcript)` — keyword match with ranking.
   Falls back to `rank_meetings` (title×3, summary×2, transcript×1 keyword
   overlap scoring).
3. **Answer:** grounded chat against the top-5 retrieved meeting transcripts
   (or summaries for "overview" intent).

**What this can't do:**
- "What are the recurring themes across all my client meetings?" → keyword
  search for "recurring themes client meetings" won't find anything useful.
- "Everything I've discussed with Sarah across projects" → FTS5 for "Sarah"
  works, but it returns individual transcripts; there's no aggregation or
  cross-meeting synthesis.
- "Which projects have stalled?" → "stalled" is not a keyword in transcripts;
  requires an understanding of project status across meetings.

---

## 3. Proposed GraphRAG architecture

### 3a. Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                        Indexing Pipeline                         │
│                     (runs after new meetings)                     │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────┐    ┌──────────────┐    ┌──────────────┐            │
│  │ Meeting │ →  │ Entity + Rel │ →  │   Entity     │            │
│  │Summary  │    │ Extraction   │    │ Resolution   │            │
│  │ (dense) │    │  (LLM call)  │    │ (embeddings  │            │
│  └─────────┘    └──────────────┘    │  + LLM adj.) │            │
│                                      └──────────────┘            │
│                                             │                    │
│                                             ▼                    │
│  ┌─────────┐    ┌──────────────┐    ┌──────────────┐            │
│  │Community│ ←  │  Community   │ ←  │  Knowledge   │            │
│  │Summaries│    │  Detection   │    │    Graph     │            │
│  │(LLM/gen)│    │  (Leiden)    │    │ (nodes+edges)│            │
│  └─────────┘    └──────────────┘    └──────────────┘            │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                        Query Pipeline                            │
│                     (per-Ask question)                            │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  User Question                                                   │
│       │                                                          │
│       ├─→ Intent: "global" / "overview" / "detail" (router)      │
│       │                                                          │
│       ├─→ Graph traversal: find communities matching question    │
│       │   (community summary → embed → cosine vs query embed)    │
│       │                                                          │
│       ├─→ FTS5 search: keyword-match meetings (existing path)    │
│       │                                                          │
│       └─→ Merge + rank → grounded answer (LLM)                   │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### 3b. Why extract from summaries, not transcripts

**Decision: extract entities/relationships from meeting summaries, not raw
transcripts.** Rationale:

- Summaries are ~500-1500 tokens (dense) vs transcripts at ~5,000-20,000 tokens
  (sparse). Extraction quality on a local model degrades with context length;
  summaries keep the extraction prompt tight.
- The summary already captures what the meeting was *about* — the entities and
  relationships that matter. A transcript has conversational noise.
- Extraction from summaries is **one LLM call per meeting**, not N chunks per
  meeting for long transcripts. This is the difference between 100 calls and
  500+ calls.
- **Downside:** entities mentioned only in the transcript but not the summary
  are missed. Mitigation: the existing FTS5 path handles keyword search for
  those; GraphRAG is for the "global themes" questions where summaries are the
  right grain.

### 3c. Entity + relationship extraction prompt

One LLM call per meeting summary. Input: the summary text. Output: structured
JSON (via Ollama `format=` schema or constrained generation with outlines/lm-format-enforcer).

```json
{
  "entities": [
    {"name": "Q3 Planning", "type": "project", "description": "Q3 roadmap planning initiative"},
    {"name": "Sarah Chen", "type": "person", "description": "Product manager, attended multiple sessions"},
    {"name": "Launch timeline", "type": "topic", "description": "Discussion about the Q3 launch schedule"},
    {"name": "Data pipeline migration", "type": "project", "description": "Moving ETL from Airflow to Dagster"}
  ],
  "relationships": [
    {"source": "Sarah Chen", "target": "Q3 Planning", "relation": "owns"},
    {"source": "Launch timeline", "target": "Q3 Planning", "relation": "part_of"},
    {"source": "Sarah Chen", "target": "Data pipeline migration", "relation": "stakeholder_in"}
  ]
}
```

Entity types: `person`, `project`, `topic`, `decision`, `deliverable`, `metric`,
`tool`, `organization`.

Relationship types: `owns`, `part_of`, `stakeholder_in`, `blocked_by`,
`depends_on`, `discussed_with`, `decided`, `delivered`.

**Validation requirement before building:** run this extraction on 20 real
meeting summaries with the actual local model (qwen3.6-35b or the user's
configured Ollama model). Measure:
- Entity precision/recall vs a manual gold set.
- How often the model misses entities.
- How often it hallucinates entities.
- Whether the JSON output is reliably parseable.

If precision < 60%, the local model is not capable enough and GraphRAG is not
viable on this hardware without a cloud LLM fallback.

---

## 4. Entity resolution — the crux

### 4a. The problem

After extraction, we have entities across meetings:
- Meeting 1: "Q3 project", "Sarah Chen", "launch timeline"
- Meeting 2: "Q3 planning", "Sarah C.", "launch schedule"
- Meeting 3: "Q3 roadmap", "Sarah Chen", "ship date"

Entity resolution must decide:
- "Q3 project" ≈ "Q3 planning" ≈ "Q3 roadmap" → one entity
- "Sarah Chen" ≈ "Sarah C." → one entity
- "launch timeline" ≈ "launch schedule" ≈ "ship date" → one entity

### 4b. Proposed approach: embeddings + threshold, with LLM adjudication for ambiguous pairs

**Step 1 — Embed everything.** Use the local LLM's embedding endpoint (Ollama
`/api/embed` with `nomic-embed-text` or `all-minilm`) or a dedicated embedding
model. Each entity's `name + " " + description` → embedding vector.

**Step 2 — Candidate pairs.** For each entity type (persons, projects, topics
separately), compute cosine similarity between all pairs. Pairs above a
threshold (e.g. 0.85) are "candidates" for merging.

**Step 3 — LLM adjudication (expensive, use sparingly).** For each candidate
pair, ask the LLM: "Are 'Q3 project' and 'Q3 planning' the same entity?" This
is a binary classification, fast and cheap per call — but with O(n²) candidate
pairs, it adds up. Cap the number of adjudication calls per run.

**Step 4 — Transitive closure.** If A ≈ B and B ≈ C, then A ≈ C. Apply after
adjudication to reduce the entity set.

### 4c. Cost analysis

- 100 meetings × ~8 entities per meeting = 800 raw entities.
- Embed: 800 embeddings (fast, local, no LLM).
- Candidate pairs after threshold (0.85): estimate 5-10% of pairs → ~3,000-16,000
  pairs. Too many for LLM adjudication.
- **Optimization:** only adjudicate pairs within the same entity type AND within
  the same embedding cluster (k-means, k=50). Reduces to a few hundred calls.
- **Further optimization:** use a simpler string-similarity pre-filter (Jaccard
  on tokenized names, edit distance) to prune obvious non-matches before
  embedding comparison.

**Recommendation:** the resolution pipeline is the riskiest part. Spike it
first, not last.

---

## 5. Community detection + summaries

### 5a. Graph construction

After entity resolution, build a graph:
- **Nodes:** resolved entities (people, projects, topics, decisions, …).
- **Edges:** relationships from extraction, weighted by frequency (if "Sarah
  Chen" ↔ "Q3 Planning" appears in 5 meetings, edge weight = 5).

### 5b. Community detection

Run the **Leiden algorithm** (igraph or networkx + leidenalg) to partition the
graph into communities. Each community is a cluster of related entities — e.g.
all entities related to "Q3 Planning" form one community.

Python deps to propose: `networkx` + `leidenalg` (or `igraph`'s Python
bindings). Add as an optional extra to `pyproject.toml`:

```toml
[project.optional-dependencies]
graphrag = [
    "networkx>=3",
    "leidenalg>=0.10",
    "scikit-learn>=1",  # for cosine similarity
]
```

### 5c. Community summaries

For each community, gather the entities, their descriptions, and the meeting
summaries that contributed to them. Feed this into the LLM to produce a
**community summary**: a 2-4 sentence description of what this cluster of
meetings is about, key participants, status, and recurring themes.

Community summaries are ONE LLM call per community (10s to 100s of calls). These
are the "global view" content that GraphRAG enables.

### 5d. Storage

Communities and their summaries are stored in a new SQLite table:

```sql
CREATE TABLE IF NOT EXISTS graphrag_communities (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    level       INTEGER NOT NULL DEFAULT 0,  -- hierarchy level (Leiden is hierarchical)
    title       TEXT NOT NULL,               -- short label
    summary     TEXT NOT NULL,               -- 2-4 sentence community summary
    entity_ids  TEXT NOT NULL,               -- JSON array of entity names in this community
    meeting_ids TEXT NOT NULL,               -- JSON array of meeting ids contributing
    created_at  TEXT NOT NULL,
    updated_at  TEXT NOT NULL
);
```

Plus a table for resolved entities:

```sql
CREATE TABLE IF NOT EXISTS graphrag_entities (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL,
    type        TEXT NOT NULL,               -- person, project, topic, decision, ...
    description TEXT NOT NULL DEFAULT '',
    canonical   TEXT NOT NULL,               -- resolved canonical name
    embedding   BLOB,                        -- cached embedding vector (optional)
    meeting_ids TEXT NOT NULL DEFAULT '[]',   -- which meetings mention this entity
    created_at  TEXT NOT NULL,
    updated_at  TEXT NOT NULL
);
```

### 5e. Where this runs

The indexing pipeline (entity extraction, resolution, community detection,
community summarization) runs in the **Python service** — it's an ML workload
that needs the LLM, embeddings, and the graph libraries. Add a new
`/graphrag/index` endpoint that the Rust backend calls:

- After each new meeting is saved (trigger: `transcribe_and_summarize` or
  `transcribe_meeting` success).
- Or on demand via a "Rebuild knowledge graph" button in Settings.

The Rust side passes meeting summaries to the Python service; the service runs
the full pipeline and writes results to the new SQLite tables.

---

## 6. Hybrid retrieval for Ask

### 6a. Query-time flow

When the user asks a question in the Ask tab:

1. **Router** (existing, `commands.rs:1174`): classify intent as
   `"detail"` / `"overview"` / `"todos"` / `"recap"`. Add a new intent:
   `"global"` — for questions that need the graph.

2. **If intent = "global":**
   - Embed the question.
   - Find the top-K communities by cosine similarity (community summary embed vs
     question embed).
   - Gather the meeting transcripts for those communities.
   - Build context: community summaries + meeting transcripts.
   - Answer grounded in both.

3. **If intent = "overview" or "detail":**
   - Run the existing FTS5 + keyword path (hybrid: first try the graph for
     additional context, but always include keyword results as fallback).
   - Optionally: graph-traverse from entities found in the question ("Sarah
     Chen" → find her community → include that community's summary as context).

### 6b. Integration with the existing router

The existing router (`ROUTER_INSTRUCTION`, `commands.rs:783`) already classifies
intent. Extend it with:

```
"global": a question about patterns, themes, status, or relationships across
          MANY meetings — not answerable from a single meeting or keyword search.
```

Example: "what are the recurring themes across all my client meetings?" →
intent = "global".

### 6c. Hybrid retrieval (the safe default)

GraphRAG retrieval is **layered on top** of the existing FTS5 path, not
replacing it. For every question:
1. Run graph retrieval (community match → meeting transcripts).
2. Run FTS5 keyword retrieval (existing path).
3. Merge both result sets (dedup by meeting id), keeping the top-N by combined
   score.
4. Grounded answer with both community summaries and raw transcripts in the
   context.

If the graph index is stale or unavailable (user hasn't indexed yet), fall back
to pure FTS5 — exactly today's behavior.

---

## 7. Spike — validate before building

**This is the most important section. Do not write a line of production code
before running this spike.**

### What the spike measures

1. **Extraction quality on the local model.** Take 20 real meeting summaries
   from the user's Adversaria DB. Run the entity+relationship extraction prompt
   against the configured local model (qwen3.6-35b via MLX, or the user's
   Ollama model). Measure:
   - How many entities are extracted per summary? (Expect 5-15.)
   - What fraction are real vs hallucinated? (Target: > 70% real.)
   - Is the JSON reliably parseable? (Target: > 95% of calls produce valid JSON.)
   - How long does one extraction call take? (Target: < 5s on local GPU.)

2. **Entity resolution accuracy.** Take the extracted entities from step 1.
   Run the embedding+threshold pipeline. For the top-20 candidate merge pairs,
   manually label whether they should be merged. Measure:
   - Precision at threshold 0.85.
   - How many clearly-wrong merges the LLM adjudication catches/causes.

3. **End-to-end latency.** Run the full pipeline on 50 meeting summaries:
   extraction → resolution → community detection → community summarization.
   Measure total wall-clock time.

4. **Query quality.** Ask 10 "global" questions against the resulting graph.
   Compare answers from:
   - Pure FTS5 (baseline, today's `ask_all_meetings`).
   - GraphRAG hybrid (graph + FTS5).
   - Manually rate each answer for relevance, completeness, and groundedness.

### Go / no-go criteria

| Metric | Go threshold | No-go if |
|--------|-------------|----------|
| Extraction JSON validity | > 95% of calls | < 80% (unreliable parsing breaks the pipeline) |
| Entity hallucination rate | < 30% | > 50% (too many fake entities) |
| Entity resolution precision | > 70% | < 50% (worse than random) |
| End-to-end latency (50 meetings) | < 10 minutes | > 30 minutes (too slow for periodic re-index) |
| Query quality improvement | GraphRAG ≥ FTS5 for ≥ 60% of global questions | GraphRAG never better (don't build it) |

### If the spike fails

If the local model can't produce reliable entity extractions, the GraphRAG path
is not viable on-device. Fallback options:
- **Hybrid cloud:** offer optional cloud LLM for graph indexing only (the user's
  API key, used only for extraction/resolution — summaries and transcripts stay
  local). This violates the "everything local" default but could be an opt-in
  power-user toggle.
- **Simpler graph from structured data:** the SPEC_KNOWLEDGE_GRAPH graph
  (structured data only, zero LLM) still works and can be extended with basic
  co-occurrence analysis without LLM extraction.
- **Wait for better local models:** local model quality improves fast. Revisit
  in 6-12 months.

---

## 8. Possible reuse of `graphify`

The user maintains a personal knowledge-graph tool called **`graphify`**
(a `graphify` skill + `graphify-vault` MCP that turns notes into an HTML graph).

**Relevance to GraphRAG:**
- `graphify` could serve as the graph construction engine: feed meeting
  summaries + extracted entities → `graphify` builds the graph.
- The resulting graph HTML could be rendered in a webview as a visualization
  layer.
- `graphify` already handles entity linking and graph traversal — reusing it
  would mean less code to build and maintain.

**Trade-off:**
- Pro: less code, reuses an existing tool the user trusts.
- Con: `graphify` is a personal tool, not a library — integration involves
  MCP-based IPC rather than an import. This adds complexity and fragility.
- Con: the graph needs to be queryable at Ask time (not just visualized), which
  means we need programmatic access to the graph structure — likely a SQLite
  table, not just an HTML file.

**Recommendation:** build the graph storage in SQLite (new tables, per §5d) for
query-time access. Optionally *also* export to `graphify` for visualization, as
a separate feature. Don't make `graphify` the primary graph store.

---

## 9. Phased plan

### Phase 0 — Spike (validate, decide go/no-go)
- Run the spike in §7. Measure everything.
- → **ADR in `docs/DECISIONS.md`**: "GraphRAG spike results — go / no-go."
- 1-2 days of focused work.

### Phase 1 — Entity extraction on summaries (cheapest LLM path)
- Add extraction prompt to the Python service.
- New endpoint: `POST /graphrag/extract` — takes summary text, returns entities
  + relationships.
- Cache extracted entities in `graphrag_entities` table.
- → **Verify:** extraction JSON is parseable on 50 real summaries; no
  regressions in existing tests.

### Phase 2 — Entity resolution (the crux)
- Embeddings + cosine threshold + LLM adjudication.
- Canonical entity table with resolved names.
- → **Verify:** resolution precision on a gold set.

### Phase 3 — Community detection + summaries
- Leiden algorithm on the entity graph.
- Community summary generation (one LLM call per community).
- Store in `graphrag_communities`.
- → **Verify:** communities are coherent and summaries are useful.

### Phase 4 — Hybrid retrieval
- Extend `ask_all_meetings` with graph-aware retrieval.
- New intent: "global".
- Merge graph results with FTS5 results.
- → **Verify:** "global" questions produce better answers than pure FTS5.

### Phase 5 — Incremental indexing
- Trigger re-indexing when new meetings are saved.
- Only re-extract for the new meeting; re-resolve only affected entities.
- → **Verify:** indexing time is proportional to new meetings, not total.

---

## 10. Open questions

These should be answered before/during the spike:

1. **Which embedding model?** `nomic-embed-text` via Ollama is the default.
   Does it produce good enough similarity scores for entity resolution on
   meeting-derived entities?
2. **Threshold tuning.** What cosine similarity threshold balances recall and
   precision for candidate merge pairs? 0.85 is a starting guess.
3. **Community count vs meeting count.** How many communities does Leiden
   produce from N meetings? A rough target is √N communities (10 communities
   from 100 meetings). Validate.
4. **Re-indexing trigger.** After every new meeting, or batched (every N
   meetings, or on demand)? Incremental is ideal but complex. Batch is simpler
   and acceptable for a power-user feature.
5. **GraphRAG storage vs DB size.** How large do the `graphrag_entities` and
   `graphrag_communities` tables get for 500 meetings? Estimate before building.
6. **Local model drift across runs.** If the user switches their Ollama model
   between indexing runs, the entity extraction quality and style change. Does
   this break entity resolution? Should we store which model was used for each
   extraction?
7. **Cloud LLM opt-in for indexing only.** If the local model fails the spike,
   should we offer an opt-in cloud LLM for graph indexing (summaries only — not
   transcripts, not audio)? This is a product decision, not just a technical one.

---

## 11. Risks

| # | Risk | Likelihood | Mitigation |
|---|------|------------|------------|
| 1 | Local model extraction quality is too low for reliable entity graphs | Medium | Spike first (§7). If it fails, don't build. |
| 2 | Entity resolution produces noisy merges that corrupt downstream communities | High | Conservative threshold; LLM adjudication only for top candidates; manual review in spike. |
| 3 | Indexing is too slow for the user to tolerate (hours vs minutes) | Medium | Cap extraction to recent meetings; offer "index in background" with progress. |
| 4 | GraphRAG answers are no better than FTS5 for the user's actual question patterns | Medium | Hybrid retrieval keeps FTS5 as fallback; measure query quality in spike. |
| 5 | Storage bloat from entity/community tables | Low | Entities are small text; communities are tens of summaries. 500 meetings → a few MB. |
| 6 | Model switching breaks the graph (different models extract different entities) | Medium | Store model id with each extraction; full re-index on model change. |

---

## 12. Docs to update when the spike completes

- `docs/DECISIONS.md` — the Phase-0 ADR: spike results + go/no-go decision.
- `docs/ARCHITECTURE.md` — the GraphRAG layer (if go).
- `docs/HANDOFF.md` — spike outcomes and next steps.
- `docs/TODO.md` — move GraphRAG from "planned/design" to "in progress" or
  "deferred."
