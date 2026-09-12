# Copilot dossier recipe: turning a project into interview evidence the Live Copilot can retrieve

Written 2026-09-08 from the Adversaria dossier build. Hand this file, unchanged, to any agent asked to write a dossier for another project. The Adversaria result is the reference: `~/Desktop/Adversaria Copilot Sources/adversaria/` (25 files).

## What a dossier is for

Hamza Laghari is the candidate in a technical interview for a Lead AI/ML role. During the interview Adversaria's Live Copilot hears the question, retrieves passages from the folder sources of the Interviews folder, and streams an answer he can say aloud. Dossier files are that evidence. A wrong number in a file becomes a wrong claim in his mouth, so every fact is verified against the project's code, config or dated records before it is written. Recorded measurements are reported as recorded, with their date and machine, never rerun from memory.

## How retrieval works (verified in `src-tauri/src` on 2026-09-08; the copilot reads these files, nothing else)

- A folder `dir` source is walked to depth 3, at most 200 files, 200 KB each, `.md` and `.txt` only (`folder_sources.rs:15-18`). Each file is one document; its title is the first line starting with `# `, else the file name stem.
- Ranking is SQLite FTS5 bm25 with the title weighted ten times the body (`storage.rs:4158`), over an OR of the question's words. Keywords are words of four or more letters that are not stopwords (`copilot.rs:381-406`). The folder tier runs only when the question yields two keywords or one of at least seven letters (`copilot.rs:415-423`); "What is RAG?" yields none and retrieves nothing. Slice 2 relaxes this; files cannot.
- **One excerpt per file:** the body is split on blank lines and the single paragraph with the most keyword occurrences is kept, cut at 600 characters (`copilot_provenance.rs:46-75`). Cloud providers then cap a passage at 1,000 UTF-8 bytes. At most three passages reach the model per question.
- No semantic search on folder docs; keyword match only. So the interviewer's own words must be in the title and in the paragraph that answers them.

## Structure

- Directory: `~/Desktop/Adversaria Copilot Sources/<project>/` (a subdirectory of the attached source root; depth is fine). Never place dossiers in the vault root or beside interview transcripts.
- 15 to 30 files, one topic each, named `<project>-<topic>.md`. Every file:

```
# <Project>: <topic in the words an interviewer would use>

<paragraph 1: the direct answer to the most likely question, 350 to 500 characters>

<paragraph 2: mechanism and numbers, 350 to 500 characters>

<paragraph 3: alternatives tried and why they lost, the limitation, what broke, 350 to 500 characters>
```

- Exactly three paragraphs, each 350 to 500 characters and under 900 UTF-8 bytes, file under 2,000 characters. No bullets, tables, headings, links, code blocks or front matter. Plain sentences. No em dashes. No marketing words.
- Third person, factual ("ERDC runs twelve agents as plain Python with Pydantic contracts"). Ownership is stated once, in `<project>-overview.md` paragraph 1, in words the founder confirms ("Hamza led the product strategy, architecture and delivery of ..."). The copilot's profile supplies identity; the files supply mechanism and evidence.
- Every number carries subject, unit, environment and date or version in the same sentence. No number in the sources, no number in the file. Never estimate.
- Where a sharp follow-up could puncture a claim, the caveat sits in the same paragraph (what was measured versus designed; what is documented versus remembered; what the client owns versus what the founder built).
- Topic words the interviewer would say (latency, retries, idempotency, evaluation, hallucination, cost, orchestration, RAG, reranker) appear naturally two or three times in the paragraph that answers them. No stuffing: paragraph selection counts occurrences, so repetition beats substance if you let it.
- `<project>-overview.md` paragraph 1 doubles as the project's entry in the standing pack (one paragraph per project sent with every request), so it must stand alone: what it is, for whom, the founder's role, the headline number.

## Process that produced the Adversaria dossier (repeat it)

1. Inventory: an evidence-cited timeline of every model, engine, technique and measured number in the project, one row each with `path:line`, built by a large-context worker (Antigravity `gemini-3.8-flash-high`). Rows without evidence are deleted.
2. Plan: Astra (`codex exec -m gpt-6-astra`, read-only) lists the 25 questions an interviewer would ask about the project and maps each to one file, with per-file paragraph plans, verify pointers and the claims a follow-up would puncture.
3. Write: two workers, disjoint file lists, the format rules above and the two indexes as input. Each worker appends a `_verification-<id>.md` listing the paths it checked per file.
4. Review: the orchestrator runs a format check (three paragraphs, lengths, no lists, third person, no dashes), spot-checks the puncture-prone numbers against code, and runs a retrieval simulation over the 25 questions plus real rehearsal questions to confirm each question's best file. Titles are adjusted until they do. In the Adversaria run this review fixed eleven factual errors the workers made.
5. Place the files in the project's subdirectory of the source root, then start one recording with the Interviews folder so the app re-indexes (`sync_folder_sources` runs at session start).

## Converting an existing long dossier (added 2026-09-10)

When a project already has a long, code-verified dossier (the `interview-dossiers` repo produced 460 KB and 270 KB single files with a quick card, ownership map, timeline, STAR war stories and a master Q&A), do not attach it as is: it exceeds the 200 KB per-file cap and yields one paragraph per question. Convert it with the same rules plus these: no new facts and keep every qualifier the source attaches to a number ("measured", "claim in a commit", "one-report demo figure"); replace colleague names with roles; turn every "don't say / say instead" row into the caveat sentence inside the paragraph it corrects, and also write `<project>-what-not-to-say.md`; one file per war story (first person only where the ownership map supports it); fold the Q&A answers into the topic files; add `<project>-ownership.md`, `<project>-agents-and-pipeline.md` and `<project>-numbers-and-provenance.md`. Then run the Q&A questions through the retrieval simulation and rewrite titles until each maps to its file. Worked example: `.recon/interview-copilot-20260908/spec-convert-common.md` and the `erdc/` and `tis/` sets in the source root. Remove any older note about the same project from the source root (two `<project>-overview.md` files produce two pack entries and can contradict each other).

## What to exclude

- Code, credentials, client names under NDA, anything the founder would not say aloud in an interview. With a cloud provider the three retrieved passages leave the machine.
- Interview transcripts and copilot rehearsal outputs: they compete with the dossier for passages and pollute profile generation. Keep them out of the source root.
- Opinions, advice, roadmap promises phrased as done.

## Known gaps to prepare with the founder, not with files

Questions that fail the keyword gate (short questions) until slice 2 ships. Facts nobody wrote down: for ERDC, the twelve agents (name, input, output, RAG use, dependencies, failure behaviour) and the reconciled numbers (team size, assessment time before and after) must come from the founder's dictation before a worker writes them.
