//! Live Copilot: "Them" question detector, local passage retrieval, and `copilot-card` events.
//!
//! Evaluates incoming live captions from the other party ("them"). When a question or prompt is
//! detected, a background consumer retrieves relevant passages from:
//! 1. Live inputs (typed notes, attached meetings/files)
//! 2. Meeting FTS (folder-prioritized)
//! 3. Context FTS (vault notes + project cards)
//! 4. Semantic enrichment (bounded by remaining budget)
//!
//! Emits "copilot-card" Tauri event with at most 3 deduplicated passages.

use std::collections::HashSet;
use std::time::{Duration, Instant};

use rusqlite::Connection;

use crate::http_client::HttpClient;
use crate::types::{CopilotLiveContext, CopilotPassage};

macro_rules! info {
    ($($arg:tt)*) => {
        eprintln!("[copilot] {}", format_args!($($arg)*));
    };
}

macro_rules! debug {
    ($($arg:tt)*) => {
        if cfg!(debug_assertions) {
            eprintln!("[copilot:debug] {}", format_args!($($arg)*));
        }
    };
}

/// Total retrieval budget before the pipeline returns whatever passages it has gathered.
const RETRIEVAL_BUDGET_MS: u64 = 900;
/// Minimum budget required to attempt semantic enrichment.
const MIN_SEMANTIC_BUDGET_MS: u64 = 300;
/// Maximum character length for any passage text.
const MAX_PASSAGE_CHARS: usize = 600;

/// Conversational fillers to strip from the beginning of candidate prompt sentences.
const FILLERS: &[&str] = &[
    "so", "okay", "ok", "and", "but", "well", "um", "uh", "alright", "right", "wow",
];

/// Tag questions that should never trigger the copilot.
const TAG_QUESTIONS: &[&str] = &["alright", "got it", "okay", "ok", "right", "you know"];

/// Starter keywords that indicate a question or prompt.
const PROMPT_STARTERS: &[&str] = &[
    "what",
    "how",
    "why",
    "when",
    "where",
    "which",
    "who",
    "can you",
    "could you",
    "would you",
    "do you",
    "did you",
    "have you",
    "are you",
    "is there",
    "tell me",
    "walk me",
    "describe",
    "explain",
    "talk me through",
    "give me",
];

/// English stopwords for keyword extraction.
const STOPWORDS: &[&str] = &[
    "a",
    "about",
    "above",
    "after",
    "again",
    "against",
    "all",
    "also",
    "am",
    "an",
    "and",
    "another",
    "any",
    "are",
    "aren't",
    "as",
    "at",
    "be",
    "because",
    "been",
    "before",
    "being",
    "below",
    "between",
    "both",
    "but",
    "by",
    "came",
    "can",
    "can't",
    "cannot",
    "come",
    "could",
    "couldn't",
    "did",
    "didn't",
    "do",
    "does",
    "doesn't",
    "doing",
    "don't",
    "down",
    "during",
    "each",
    "even",
    "few",
    "for",
    "from",
    "further",
    "get",
    "got",
    "had",
    "hadn't",
    "has",
    "hasn't",
    "have",
    "haven't",
    "having",
    "he",
    "he'd",
    "he'll",
    "he's",
    "her",
    "here",
    "here's",
    "hers",
    "herself",
    "him",
    "himself",
    "his",
    "how",
    "how's",
    "i",
    "i'd",
    "i'll",
    "i'm",
    "i've",
    "if",
    "in",
    "into",
    "is",
    "isn't",
    "it",
    "it's",
    "its",
    "itself",
    "just",
    "let's",
    "like",
    "make",
    "many",
    "me",
    "more",
    "most",
    "much",
    "must",
    "mustn't",
    "my",
    "myself",
    "never",
    "no",
    "nor",
    "not",
    "now",
    "of",
    "off",
    "on",
    "once",
    "only",
    "or",
    "other",
    "ought",
    "our",
    "ours",
    "ourselves",
    "out",
    "over",
    "own",
    "really",
    "same",
    "shan't",
    "she",
    "she'd",
    "she'll",
    "she's",
    "should",
    "shouldn't",
    "so",
    "some",
    "such",
    "tell",
    "than",
    "that",
    "that's",
    "the",
    "their",
    "theirs",
    "them",
    "themselves",
    "then",
    "there",
    "there's",
    "these",
    "they",
    "they'd",
    "they'll",
    "they're",
    "they've",
    "this",
    "those",
    "through",
    "to",
    "too",
    "under",
    "until",
    "up",
    "very",
    "was",
    "wasn't",
    "we",
    "we'd",
    "we'll",
    "we're",
    "we've",
    "well",
    "were",
    "weren't",
    "what",
    "what's",
    "whatever",
    "when",
    "when's",
    "where",
    "where's",
    "which",
    "while",
    "who",
    "who's",
    "whom",
    "why",
    "why's",
    "will",
    "with",
    "won't",
    "would",
    "wouldn't",
    "yeah",
    "yes",
    "you",
    "you'd",
    "you'll",
    "you're",
    "you've",
    "your",
    "yours",
    "yourself",
    "yourselves",
];

/// Generic words excluded from FTS queries to avoid broad, low-relevance matches.
const GENERIC_WORDS: &[&str] = &[
    "system", "systems", "thing", "things", "people", "meeting", "question", "project", "work",
    "time", "today", "going", "think", "know", "really", "right", "okay", "like", "want", "need",
    "make", "said", "talk", "talking", "discuss", "tell",
];

/// Strips leading conversational fillers from a lowercase string slice.
fn strip_leading_fillers(mut text: &str) -> &str {
    let mut changed = true;
    while changed {
        changed = false;
        text = text
            .trim_start_matches(|c: char| c.is_whitespace() || c == ',' || c == '-' || c == ':');
        for filler in FILLERS {
            if let Some(rest) = text.strip_prefix(filler) {
                if rest.is_empty() || rest.starts_with(|c: char| !c.is_alphanumeric()) {
                    text = rest;
                    changed = true;
                    break;
                }
            }
        }
    }
    text.trim_start_matches(|c: char| c.is_whitespace() || c == ',' || c == '-' || c == ':')
}

/// Sentence-level question and prompt detector.
///
/// Splits text on '.', '?', '!'. A sentence qualifies as a prompt if:
/// - It ends with '?' (and is not a tag question like "Alright?", "Got it?", "Okay?"), OR
/// - It starts with a prompt keyword after stripping leading fillers (and has > 3 words).
pub fn is_prompt(text: &str) -> bool {
    let clean_text = if let Some((prefix, rest)) = text.split_once(':') {
        if !prefix.contains(['.', '?', '!']) && prefix.split_whitespace().count() <= 3 {
            rest.trim()
        } else {
            text.trim()
        }
    } else {
        text.trim()
    };

    if clean_text.is_empty() {
        return false;
    }

    let mut sentence_start = 0;
    let chars: Vec<(usize, char)> = clean_text.char_indices().collect();

    for (i, &(byte_idx, ch)) in chars.iter().enumerate() {
        let is_delim = ch == '.' || ch == '?' || ch == '!';
        let is_last = i == chars.len() - 1;

        if is_delim || is_last {
            let sentence_end = if is_delim {
                byte_idx
            } else {
                byte_idx + ch.len_utf8()
            };

            let raw_sentence = clean_text[sentence_start..sentence_end].trim();
            sentence_start = byte_idx + ch.len_utf8();

            if raw_sentence.is_empty() {
                continue;
            }

            let word_count = raw_sentence.split_whitespace().count();
            let lower = raw_sentence.to_lowercase();
            let clean_words: String = lower
                .chars()
                .filter(|c| c.is_alphanumeric() || c.is_whitespace())
                .collect();
            let clean_words_trimmed = clean_words.trim();

            if TAG_QUESTIONS.contains(&clean_words_trimmed) && ch == '?' {
                continue;
            }

            let stripped = strip_leading_fillers(&lower);
            let has_starter = PROMPT_STARTERS.iter().any(|starter| {
                if let Some(rest) = stripped.strip_prefix(starter) {
                    rest.is_empty() || rest.starts_with(|c: char| !c.is_alphanumeric())
                } else {
                    false
                }
            });

            if ch == '?' {
                // A question of <= 3 words without a prompt starter is treated as a tag question
                if word_count <= 3 && !has_starter {
                    continue;
                }
                return true;
            } else if has_starter && word_count > 3 {
                return true;
            }
        }
    }

    false
}

/// Extract searchable keywords (length >= 4, stopwords removed, casefolded).
/// Hyphenated words count as one keyword (e.g. "air-gapped").
pub fn extract_keywords(text: &str) -> HashSet<String> {
    let lower = text.to_lowercase().replace("--", " ");
    lower
        .split(|c: char| !c.is_alphanumeric() && c != '-')
        .map(|w| w.trim_matches('-'))
        .filter(|w| w.len() >= 4 && !STOPWORDS.contains(w))
        .map(|w| w.to_string())
        .collect()
}

/// Extract candidate FTS keywords: length >= 4, not in stopwords, not in generic words.
/// Deduplicated in encounter order. Hyphenated words count as one keyword.
pub fn extract_fts_keywords(text: &str) -> Vec<String> {
    extract_fts_keywords_for_folder(text, &HashSet::new())
}

pub(crate) fn is_specific_word(word: &str) -> bool {
    !STOPWORDS.contains(&word) && !GENERIC_WORDS.contains(&word)
}

pub fn extract_fts_keywords_for_folder(text: &str, terms: &HashSet<String>) -> Vec<String> {
    let lower = text.to_lowercase().replace("--", " ");
    let mut seen = HashSet::new();
    let mut keywords = Vec::new();

    for raw in lower.split(|c: char| !c.is_alphanumeric() && c != '-') {
        let w = raw.trim_matches('-');
        if (w.chars().count() >= 4 || ((2..=3).contains(&w.chars().count()) && terms.contains(w)))
            && is_specific_word(w)
            && seen.insert(w.to_string())
        {
            keywords.push(w.to_string());
        }
    }

    keywords
}

/// Whether the extracted keywords meet the floor to run FTS tiers:
/// - >= 2 specific keywords, OR
/// - 1 single rare keyword of length >= 7 (e.g. "air-gapped", "kubernetes").
pub fn qualifies_for_fts(keywords: &[String]) -> bool {
    if keywords.len() >= 2 {
        true
    } else if keywords.len() == 1 {
        keywords[0].len() >= 7
    } else {
        false
    }
}

/// Score an FTS hit by keyword coverage: 0.75 * (matched / total).
pub fn fts_coverage_score(matched_keywords: usize, query_keywords: usize) -> f32 {
    if query_keywords == 0 {
        return 0.0;
    }
    0.75 * (matched_keywords as f32 / query_keywords as f32)
}

/// Strips a leading line from `text` that equals `title` (optionally followed by ` (YYYY-MM-DD)`),
/// so the passage body never repeats the meeting chip.
pub fn strip_title_line<'a>(text: &'a str, title: &str) -> &'a str {
    let title_trimmed = title.trim();
    if title_trimmed.is_empty() {
        return text;
    }

    let trimmed = text.trim_start();
    let (first_line, rest) = match trimmed.split_once('\n') {
        Some((fl, r)) => (fl, r),
        None => (trimmed, ""),
    };

    let fl = first_line.trim_end_matches('\r').trim();
    let is_title_line = if let Some(rem) = fl.strip_prefix(title_trimmed) {
        let rem_trimmed = rem.trim();
        if rem_trimmed.is_empty() {
            true
        } else if let Some(inner) = rem_trimmed
            .strip_prefix('(')
            .and_then(|s| s.strip_suffix(')'))
        {
            inner.len() == 10
                && inner.chars().enumerate().all(|(i, c)| {
                    if i == 4 || i == 7 {
                        c == '-'
                    } else {
                        c.is_ascii_digit()
                    }
                })
        } else {
            false
        }
    } else {
        false
    };

    if is_title_line {
        rest.trim_start_matches('\r')
            .trim_start_matches('\n')
            .trim_start()
    } else {
        text
    }
}

/// Execute the bounded multi-tier retrieval pipeline for one frozen question.
pub async fn retrieve_passages(
    client: &HttpClient,
    live: &CopilotLiveContext,
    question: &str,
    previous_them: Option<&str>,
) -> (Vec<CopilotPassage>, u64) {
    let start = Instant::now();
    let deadline = tokio::time::Instant::now() + Duration::from_millis(RETRIEVAL_BUDGET_MS);
    let query = if question.split_whitespace().count() < 6 {
        previous_them.map_or_else(
            || question.to_string(),
            |previous| format!("{question} {previous}"),
        )
    } else {
        question.to_string()
    };

    let sync_live = live.clone();
    let sync_query = query.clone();
    let (mut passages, mut tiers_hit) = run_blocking_until(deadline, move || {
        crate::storage::connect_for_sync()
            .map(|conn| retrieve_sync_tiers(&conn, &sync_live, &sync_query))
            .unwrap_or_default()
    })
    .await
    .unwrap_or_default();

    let minimum_semantic_budget = Duration::from_millis(MIN_SEMANTIC_BUDGET_MS);
    let mut semantic_ran = false;
    if let Some(folder_id) = live.folder_id {
        if deadline.saturating_duration_since(tokio::time::Instant::now()) > minimum_semantic_budget
        {
            semantic_ran = true;
            let semantic = tokio::time::timeout_at(
                deadline,
                retrieve_semantic_tier(client, &query, folder_id, deadline),
            )
            .await
            .unwrap_or_default();
            if !semantic.is_empty() {
                tiers_hit.push("semantic");
                passages.extend(semantic);
            }
        }
    }
    if semantic_ran {
        passages.retain(|passage| passage.score >= 0.375);
    }

    let mut passages = dedup_and_sort_passages(passages);
    passages.truncate(3);
    let retrieval_ms = start.elapsed().as_millis() as u64;
    info!(
        "question_len={}, tiers=[{}], passages={}, retrieval_ms={}",
        question.len(),
        tiers_hit.join(","),
        passages.len(),
        retrieval_ms
    );
    (passages, retrieval_ms)
}

pub(crate) fn dedup_and_sort_passages(passages: Vec<CopilotPassage>) -> Vec<CopilotPassage> {
    use crate::copilot_provenance::canonical_evidence_key;
    let mut deduplicated: std::collections::HashMap<String, CopilotPassage> =
        std::collections::HashMap::new();
    for passage in passages {
        let key = canonical_evidence_key(&passage);
        match deduplicated.get(&key) {
            Some(existing) if passage_order(existing, &passage) != std::cmp::Ordering::Greater => {}
            _ => {
                deduplicated.insert(key, passage);
            }
        }
    }
    let mut passages: Vec<_> = deduplicated.into_values().collect();
    passages.sort_by(passage_order);
    passages
}

fn passage_order(left: &CopilotPassage, right: &CopilotPassage) -> std::cmp::Ordering {
    // The tier-d score reaches this value exactly only at full coverage.
    let full = |p: &CopilotPassage| p.source_kind == "folder" && p.score >= 0.86 + 0.10;
    full(right)
        .cmp(&full(left))
        .then_with(|| right.score.total_cmp(&left.score))
        .then_with(|| {
            crate::copilot_provenance::canonical_evidence_key(left)
                .cmp(&crate::copilot_provenance::canonical_evidence_key(right))
        })
}

/// Run every SQLite/FTS/file tier on the blocking pool while sharing the
/// caller's one absolute deadline. Dropping this future on card cancellation
/// detaches the blocking task but immediately stops all result propagation.
async fn run_blocking_until<T, F>(deadline: tokio::time::Instant, work: F) -> Option<T>
where
    T: Send + 'static,
    F: FnOnce() -> T + Send + 'static,
{
    match tokio::time::timeout_at(deadline, tokio::task::spawn_blocking(work)).await {
        Ok(Ok(result)) => Some(result),
        Ok(Err(error)) => {
            debug!("copilot blocking retrieval failed: {error}");
            None
        }
        Err(_) => {
            debug!("copilot blocking retrieval reached the absolute deadline");
            None
        }
    }
}

/// Retrieve synchronous tiers (Live inputs, Meeting FTS, Context FTS) using a given connection.
pub fn retrieve_sync_tiers(
    conn: &Connection,
    live: &CopilotLiveContext,
    query: &str,
) -> (Vec<CopilotPassage>, Vec<&'static str>) {
    let mut passages = Vec::new();
    let mut tiers_hit = Vec::new();
    let query_keywords = extract_keywords(query);

    // -----------------------------------------------------------------------
    // Tier a: Live inputs
    // -----------------------------------------------------------------------
    let mut live_hit = false;

    // 1. Typed notes lines
    let mut best_note_line: Option<(&str, usize)> = None;
    for line in live.notes.lines() {
        let line_trimmed = line.trim();
        if line_trimmed.is_empty() {
            continue;
        }
        let line_keywords = extract_keywords(line_trimmed);
        let shared = query_keywords.intersection(&line_keywords).count();
        if shared >= 2 && best_note_line.is_none_or(|(_, best)| shared > best) {
            best_note_line = Some((line_trimmed, shared));
        }
    }

    if let Some((line, _)) = best_note_line {
        live_hit = true;
        passages.push(CopilotPassage {
            source_kind: "notes".to_string(),
            source_id: "notes".to_string(),
            title: "Notes".to_string(),
            text: crate::copilot_provenance::truncate_word_boundary(line, MAX_PASSAGE_CHARS),
            score: 0.9,
        });
    }

    // 2. Attached meetings and files
    for attachment in &live.attachments {
        if attachment.kind == "meeting" {
            if let Ok(meeting_id) = attachment.value.parse::<i64>() {
                if let Ok(Some(meeting)) = crate::storage::get_meeting_on(conn, meeting_id) {
                    live_hit = true;
                    let text_body = if !meeting.summary.is_empty() {
                        &meeting.summary
                    } else {
                        &meeting.transcript
                    };
                    let stripped = strip_title_line(text_body, &meeting.title);
                    let excerpt = crate::copilot_provenance::excerpt_around_keywords(
                        stripped,
                        &query_keywords,
                        MAX_PASSAGE_CHARS,
                    );
                    let date = meeting
                        .recorded_at
                        .get(..10)
                        .unwrap_or(&meeting.recorded_at);
                    let title = if date.is_empty() {
                        meeting.title
                    } else {
                        format!("{} ({date})", meeting.title)
                    };

                    passages.push(CopilotPassage {
                        source_kind: "meeting".to_string(),
                        source_id: meeting_id.to_string(),
                        title,
                        text: excerpt,
                        score: 0.85,
                    });
                }
            }
        } else {
            let path = std::path::Path::new(&attachment.value);
            if path.exists() {
                if let Ok(file) = std::fs::File::open(path) {
                    use std::io::Read;
                    let mut buffer = String::new();
                    let mut handle = file.take(20 * 1024);
                    if handle.read_to_string(&mut buffer).is_ok() && !buffer.trim().is_empty() {
                        live_hit = true;
                        let excerpt = crate::copilot_provenance::excerpt_around_keywords(
                            &buffer,
                            &query_keywords,
                            MAX_PASSAGE_CHARS,
                        );
                        let title = if attachment.label.is_empty() {
                            path.file_name()
                                .map(|f| f.to_string_lossy().to_string())
                                .unwrap_or_else(|| "Attached File".to_string())
                        } else {
                            attachment.label.clone()
                        };

                        passages.push(CopilotPassage {
                            source_kind: "attachment".to_string(),
                            source_id: attachment.value.clone(),
                            title,
                            text: excerpt,
                            score: 0.8,
                        });
                    }
                }
            }
        }
    }

    if live_hit {
        tiers_hit.push("live");
    }

    let Some(folder_id) = live.folder_id else {
        return (passages, vec!["live"]);
    };
    let folder_ids = crate::storage::folder_meeting_ids_on(conn, folder_id).unwrap_or_default();
    let sources = crate::storage::folder_source_paths_on(conn, folder_id).unwrap_or_default();

    // -----------------------------------------------------------------------
    // Tier b: Meeting FTS
    // -----------------------------------------------------------------------
    let fts_keywords = extract_fts_keywords(query);
    let fts_eligible = qualifies_for_fts(&fts_keywords);

    if fts_eligible && !folder_ids.is_empty() {
        let fts_query = fts_keywords.join(" ");
        let fts_keywords_set: HashSet<String> = fts_keywords.iter().cloned().collect();

        if let Ok(all_meeting_ids) = crate::storage::search_meeting_ids_on(conn, &fts_query, 10) {
            let target_ids: Vec<i64> = all_meeting_ids
                .into_iter()
                .filter(|id| folder_ids.contains(id))
                .collect();

            let mut fts_passages = Vec::new();
            for &meeting_id in &target_ids {
                if let Ok(Some(meeting)) = crate::storage::get_meeting_on(conn, meeting_id) {
                    let chunk_texts = crate::storage::get_meeting_chunk_texts_on(conn, meeting_id)
                        .unwrap_or_default();

                    let mut full_text = format!(
                        "{} {} {}",
                        meeting.title, meeting.summary, meeting.transcript
                    );
                    for chunk in &chunk_texts {
                        full_text.push(' ');
                        full_text.push_str(chunk);
                    }
                    let meeting_words = extract_keywords(&full_text);
                    let matched_count = fts_keywords
                        .iter()
                        .filter(|kw| meeting_words.contains(kw.as_str()))
                        .count();

                    if matched_count == 0 {
                        continue;
                    }

                    let score = fts_coverage_score(matched_count, fts_keywords.len());

                    let raw_text = if !chunk_texts.is_empty() {
                        let mut best_chunk = &chunk_texts[0];
                        let mut best_hits = 0;
                        for chunk in &chunk_texts {
                            let hits = crate::copilot_provenance::keyword_hit_count(
                                chunk,
                                &fts_keywords_set,
                            );
                            if hits > best_hits {
                                best_hits = hits;
                                best_chunk = chunk;
                            }
                        }
                        strip_title_line(best_chunk, &meeting.title)
                    } else {
                        let summary_body = if !meeting.summary.is_empty() {
                            &meeting.summary
                        } else {
                            &meeting.transcript
                        };
                        strip_title_line(summary_body, &meeting.title)
                    };

                    let text = if !chunk_texts.is_empty() {
                        crate::copilot_provenance::truncate_word_boundary(
                            raw_text,
                            MAX_PASSAGE_CHARS,
                        )
                    } else {
                        crate::copilot_provenance::excerpt_around_keywords(
                            raw_text,
                            &fts_keywords_set,
                            MAX_PASSAGE_CHARS,
                        )
                    };

                    let date = meeting
                        .recorded_at
                        .get(..10)
                        .unwrap_or(&meeting.recorded_at);
                    let title = if date.is_empty() {
                        meeting.title
                    } else {
                        format!("{} ({date})", meeting.title)
                    };

                    fts_passages.push(CopilotPassage {
                        source_kind: "meeting".to_string(),
                        source_id: meeting_id.to_string(),
                        title,
                        text,
                        score,
                    });
                }
            }

            if !fts_passages.is_empty() {
                tiers_hit.push("meeting_fts");
                fts_passages.sort_by(|a, b| {
                    b.score
                        .partial_cmp(&a.score)
                        .unwrap_or(std::cmp::Ordering::Equal)
                });
                passages.extend(fts_passages);
            }
        }
    }

    // -----------------------------------------------------------------------
    // Tier c: Context FTS (vault + project)
    // -----------------------------------------------------------------------
    if fts_eligible && !sources.is_empty() {
        let fts_query = fts_keywords.join(" ");
        let fts_keywords_set: HashSet<String> = fts_keywords.iter().cloned().collect();

        if let Ok(doc_ids) = crate::storage::search_context_doc_ids_on(conn, &fts_query, None, 50) {
            if !doc_ids.is_empty() {
                if let Ok(docs) = crate::storage::get_context_docs_on(conn, &doc_ids) {
                    let mut context_passages = Vec::new();
                    for doc in &docs {
                        if !crate::folder_sources::path_in_sources(&doc.path, &sources) {
                            continue;
                        }
                        let doc_text = format!("{} {}", doc.title, doc.body);
                        let doc_words = extract_keywords(&doc_text);
                        let matched_count = fts_keywords
                            .iter()
                            .filter(|kw| doc_words.contains(kw.as_str()))
                            .count();

                        if matched_count == 0 {
                            continue;
                        }

                        let score = fts_coverage_score(matched_count, fts_keywords.len());
                        let excerpt = crate::copilot_provenance::excerpt_around_keywords(
                            &doc.body,
                            &fts_keywords_set,
                            MAX_PASSAGE_CHARS,
                        );

                        context_passages.push(CopilotPassage {
                            source_kind: doc.source.clone(),
                            source_id: doc.path.clone(),
                            title: doc.title.clone(),
                            text: excerpt,
                            score,
                        });
                    }

                    if !context_passages.is_empty() {
                        tiers_hit.push("context_fts");
                        context_passages.sort_by(|a, b| {
                            b.score
                                .partial_cmp(&a.score)
                                .unwrap_or(std::cmp::Ordering::Equal)
                        });
                        passages.extend(context_passages);
                    }
                }
            }
        }
    }

    // Tier d: Documents indexed directly from this folder's sources.
    let terms = crate::storage::get_folder_terms_on(conn, folder_id)
        .unwrap_or_default()
        .into_iter()
        .collect();
    let fts_keywords = extract_fts_keywords_for_folder(query, &terms);
    if !fts_keywords.is_empty() {
        let fts_query = fts_keywords.join(" ");
        let keywords: HashSet<String> = fts_keywords.iter().cloned().collect();
        if let Ok(ids) = crate::storage::search_folder_doc_ids_on(conn, folder_id, &fts_query, 10) {
            if let Ok(docs) = crate::storage::get_folder_docs_on(conn, &ids) {
                let mut folder_hit = false;
                for (_, path, title, body) in docs {
                    let words: HashSet<_> =
                        extract_fts_keywords_for_folder(&format!("{title} {body}"), &terms)
                            .into_iter()
                            .collect();
                    let matched = fts_keywords
                        .iter()
                        .filter(|word| words.contains(word.as_str()))
                        .count();
                    if matched == 0 {
                        continue;
                    }
                    folder_hit = true;
                    passages.push(CopilotPassage {
                        source_kind: "folder".to_string(),
                        source_id: path,
                        title,
                        text: crate::copilot_provenance::excerpt_around_keywords(
                            &body,
                            &keywords,
                            MAX_PASSAGE_CHARS,
                        ),
                        score: 0.86 + 0.10 * (matched as f32 / fts_keywords.len() as f32),
                    });
                }
                if folder_hit {
                    tiers_hit.push("folder");
                }
            }
        }
    }

    (passages, tiers_hit)
}

/// Retrieve semantic tier candidates within remaining budget.
async fn retrieve_semantic_tier(
    client: &HttpClient,
    query: &str,
    folder_id: i64,
    deadline: tokio::time::Instant,
) -> Vec<CopilotPassage> {
    let Some((folder_ids, sources)) = run_blocking_until(deadline, move || {
        let conn = crate::storage::connect_for_sync().ok()?;
        Some((
            crate::storage::folder_meeting_ids_on(&conn, folder_id).ok()?,
            crate::storage::folder_source_paths_on(&conn, folder_id).ok()?,
        ))
    })
    .await
    .flatten() else {
        return Vec::new();
    };
    let mut results = Vec::new();

    // 1. Related meetings. The embedding request is async; chunk loading,
    // vector ranking, and meeting hydration all stay on the blocking pool.
    let input = [query.to_string()];
    let meeting_results = if folder_ids.is_empty() {
        Vec::new()
    } else {
        match client.embed(&input).await {
            Ok((vectors, model)) if !vectors.is_empty() => {
                let query_vector = vectors[0].clone();
                run_blocking_until(deadline, move || {
                    let mut results = Vec::new();
                    let Ok(conn) = crate::storage::connect_for_sync() else {
                        return results;
                    };
                    let ranked = crate::storage::get_chunks_for_model(&model)
                        .map(|chunks| {
                            crate::embeddings::best_cosine_per_meeting(&chunks, &query_vector)
                        })
                        .unwrap_or_default();
                    for (meeting_id, cosine) in ranked
                        .into_iter()
                        .filter(|(meeting_id, cosine)| {
                            folder_ids.contains(meeting_id) && *cosine >= 0.55
                        })
                        .take(3)
                    {
                        if let Ok(Some(meeting)) = crate::storage::get_meeting_on(&conn, meeting_id)
                        {
                            let date = meeting
                                .recorded_at
                                .get(..10)
                                .unwrap_or(&meeting.recorded_at);
                            let title = if date.is_empty() {
                                meeting.title.clone()
                            } else {
                                format!("{} ({date})", meeting.title)
                            };
                            let text_body = if !meeting.summary.is_empty() {
                                &meeting.summary
                            } else {
                                &meeting.transcript
                            };
                            let stripped = strip_title_line(text_body, &meeting.title);
                            let text = crate::copilot_provenance::truncate_word_boundary(
                                stripped,
                                MAX_PASSAGE_CHARS,
                            );

                            results.push(CopilotPassage {
                                source_kind: "meeting".to_string(),
                                source_id: meeting_id.to_string(),
                                title,
                                text,
                                score: cosine,
                            });
                        }
                    }
                    results
                })
                .await
                .unwrap_or_default()
            }
            _ => Vec::new(),
        }
    };
    results.extend(meeting_results);

    // 2. Context search (vault + project)
    let context_hits = if sources.is_empty() {
        Vec::new()
    } else {
        crate::context_index::search(client, query, 3, 2, 0.55).await
    };
    for hit in context_hits {
        if !crate::folder_sources::path_in_sources(&hit.path, &sources) {
            continue;
        }
        let score = if hit.signal.starts_with("[semantic match: ") {
            hit.signal
                .trim_start_matches("[semantic match: ")
                .trim_end_matches(']')
                .parse::<f32>()
                .unwrap_or(0.55)
        } else {
            0.55
        };

        results.push(CopilotPassage {
            source_kind: hit.source,
            source_id: hit.path,
            title: hit.title,
            text: crate::copilot_provenance::truncate_word_boundary(
                &hit.excerpt,
                MAX_PASSAGE_CHARS,
            ),
            score,
        });
    }

    results
}

// ===========================================================================
// Tests
// ===========================================================================
#[cfg(test)]
mod tests {
    use super::*;

    fn evidence_db() -> Connection {
        let conn = in_memory_db();
        crate::storage::setup_fts(&conn).unwrap();
        crate::storage::setup_context_fts(&conn).unwrap();
        conn.execute("INSERT INTO meetings (id, title, transcript, recorded_at) VALUES (1, 'Other meeting', 'hermetic deployment', '2026-09-07')", []).unwrap();
        for path in [
            "/approved/inside.md",
            "/approved-other/outside.md",
            "/exact.md",
            "/exact.md-other",
        ] {
            crate::storage::upsert_context_doc_on(
                &conn,
                "vault",
                path,
                "Project",
                "Project",
                "hermetic deployment",
                "1",
            )
            .unwrap();
        }
        conn
    }

    #[test]
    fn no_folder_never_retrieves_meetings_context_or_folder_documents() {
        let conn = evidence_db();
        crate::storage::upsert_folder_doc_on(
            &conn,
            1,
            "/folder.md",
            "Folder",
            "hermetic deployment",
            "1",
            "now",
        )
        .unwrap();
        let live = CopilotLiveContext {
            folder_id: None,
            notes: "hermetic deployment".into(),
            attachments: Vec::new(),
        };
        let (passages, tiers) = retrieve_sync_tiers(&conn, &live, "hermetic deployment");
        assert_eq!(tiers, vec!["live"]);
        assert_eq!(passages.len(), 1);
        assert_eq!(passages[0].source_kind, "notes");
    }

    #[test]
    fn empty_folder_does_not_fall_back_to_all_meetings() {
        let conn = evidence_db();
        let id = crate::storage::create_folder_on(&conn, "Empty", "blue")
            .unwrap()
            .id;
        let live = CopilotLiveContext {
            folder_id: Some(id),
            ..Default::default()
        };
        let (passages, tiers) = retrieve_sync_tiers(&conn, &live, "hermetic deployment");
        assert!(passages.is_empty());
        assert!(tiers.is_empty());
    }

    #[test]
    fn meeting_fts_only_returns_meetings_filed_in_the_selected_folder() {
        let conn = evidence_db();
        let id = crate::storage::create_folder_on(&conn, "Me", "blue")
            .unwrap()
            .id;
        conn.execute("INSERT INTO meetings (id, title, transcript, recorded_at) VALUES (2, 'Filed meeting', 'hermetic deployment', '2026-09-07')", []).unwrap();
        crate::storage::set_meeting_folder_on(&conn, 2, Some(id)).unwrap();
        let live = CopilotLiveContext {
            folder_id: Some(id),
            ..Default::default()
        };
        let (passages, _) = retrieve_sync_tiers(&conn, &live, "hermetic deployment");
        assert_eq!(passages.len(), 1);
        assert_eq!(passages[0].source_kind, "meeting");
        assert_eq!(passages[0].source_id, "2");
    }

    #[test]
    fn context_documents_require_an_exact_file_or_directory_source() {
        let conn = evidence_db();
        let id = crate::storage::create_folder_on(&conn, "Me", "blue")
            .unwrap()
            .id;
        crate::storage::insert_folder_source_on(&conn, id, "/approved", "dir", "now").unwrap();
        crate::storage::insert_folder_source_on(&conn, id, "/exact.md", "file", "now").unwrap();
        let live = CopilotLiveContext {
            folder_id: Some(id),
            ..Default::default()
        };
        let (passages, tiers) = retrieve_sync_tiers(&conn, &live, "hermetic deployment");
        assert_eq!(tiers, vec!["context_fts"]);
        let paths: HashSet<_> = passages.iter().map(|p| p.source_id.as_str()).collect();
        assert_eq!(paths, HashSet::from(["/approved/inside.md", "/exact.md"]));
    }

    #[test]
    fn folder_document_tier_returns_the_document_title_path_and_excerpt() {
        let conn = in_memory_db();
        let id = crate::storage::create_folder_on(&conn, "Me", "blue")
            .unwrap()
            .id;
        crate::storage::upsert_folder_doc_on(
            &conn,
            id,
            "/me.md",
            "My project",
            "hermetic deployment",
            "1",
            "now",
        )
        .unwrap();
        crate::storage::upsert_folder_doc_on(
            &conn,
            id + 1,
            "/other.md",
            "Other project",
            "hermetic deployment",
            "1",
            "now",
        )
        .unwrap();
        let live = CopilotLiveContext {
            folder_id: Some(id),
            ..Default::default()
        };
        let (passages, tiers) = retrieve_sync_tiers(&conn, &live, "hermetic deployment");
        assert_eq!(tiers, vec!["folder"]);
        assert_eq!(passages.len(), 1);
        assert_eq!(passages[0].source_kind, "folder");
        assert_eq!(passages[0].source_id, "/me.md");
        assert_eq!(passages[0].title, "My project");
        assert_eq!(passages[0].text, "hermetic deployment");
        assert_eq!(passages[0].score, 0.86 + 0.10);
    }

    use crate::storage::in_memory_db;

    #[test]
    fn prompt_detection_keeps_real_questions_and_suppresses_tags() {
        assert!(!is_prompt("Alright?"));
        assert!(!is_prompt("Got it?"));
        assert!(is_prompt("So, can you walk me through it"));
        assert!(is_prompt("Well, what do you think about this?"));
        assert!(!is_prompt("We shipped it."));
    }

    #[test]
    fn fts_keyword_floor_and_score_are_stable() {
        let rare = extract_fts_keywords("What is an air-gapped system?");
        assert_eq!(rare, vec!["air-gapped".to_string()]);
        assert!(qualifies_for_fts(&rare));
        assert!(!qualifies_for_fts(&extract_fts_keywords("What do we do?")));
        assert!((fts_coverage_score(2, 3) - 0.5).abs() < 1e-6);
    }

    #[tokio::test(flavor = "multi_thread", worker_threads = 2)]
    async fn blocking_retrieval_obeys_the_absolute_deadline() {
        let deadline = tokio::time::Instant::now() + Duration::from_millis(10);
        let result = run_blocking_until(deadline, || {
            std::thread::sleep(Duration::from_millis(100));
            "late"
        })
        .await;
        assert_eq!(result, None);
    }

    #[test]
    fn title_line_is_removed_from_passage_body() {
        let text = "Interview — FDE Candidate (2026-07-06)\nHamza: details";
        assert_eq!(
            strip_title_line(text, "Interview — FDE Candidate"),
            "Hamza: details"
        );
    }

    #[test]
    fn live_notes_retrieval_is_bounded_and_ranked_first() {
        let conn = in_memory_db();
        let live = CopilotLiveContext {
            folder_id: None,
            notes: format!(
                "Unrelated\n{}",
                "Deployment cluster configuration remains hermetic ".repeat(30)
            ),
            attachments: Vec::new(),
        };
        let (passages, tiers) = retrieve_sync_tiers(
            &conn,
            &live,
            "How should deployment cluster configuration work?",
        );
        assert!(tiers.contains(&"live"));
        assert_eq!(passages[0].source_kind, "notes");
        assert!(passages[0].text.chars().count() <= MAX_PASSAGE_CHARS);
    }
    #[test]
    fn folder_acronym_coverage() {
        let conn = in_memory_db();
        let folder = crate::storage::create_folder_on(&conn, "Interview", "blue")
            .unwrap()
            .id;
        crate::storage::set_folder_terms_on(&conn, folder, &["rag".into(), "ct2".into()]).unwrap();
        crate::storage::upsert_folder_doc_on(
            &conn,
            folder,
            "/adversaria.md",
            "Adversaria: Hybrid retrieval and GraphRAG tradeoffs",
            "RAG combines FTS retrieval and generation. CT2 runs speech recognition.",
            "1",
            "now",
        )
        .unwrap();
        let live = CopilotLiveContext {
            folder_id: Some(folder),
            ..Default::default()
        };
        for (query, expected) in [
            ("What is RAG?", 0.96),
            ("What is CT2?", 0.96),
            ("RAG latency", 0.91),
        ] {
            let (passages, tiers) = retrieve_sync_tiers(&conn, &live, query);
            assert_eq!(tiers, ["folder"]);
            assert_eq!(passages.len(), 1);
            assert!((passages[0].score - expected).abs() < 0.00001);
        }
        assert!(
            retrieve_sync_tiers(&conn, &CopilotLiveContext::default(), "What is RAG?")
                .0
                .is_empty()
        );
        assert!(retrieve_sync_tiers(&conn, &live, "What is an unknownword?")
            .0
            .is_empty());
        assert!(extract_fts_keywords("What is RAG?").is_empty());
        let terms = ["rag".into(), "ct2".into()].into_iter().collect();
        assert_eq!(
            extract_fts_keywords_for_folder("RAG rag CT2 and no UI", &terms),
            ["rag", "ct2"]
        );
    }

    #[test]
    fn curated_dedup_and_sort() {
        let passage = |kind: &str, path: &str, score| CopilotPassage {
            source_kind: kind.into(),
            source_id: path.into(),
            title: "Evidence".into(),
            text: "RAG".into(),
            score,
        };
        let sorted = dedup_and_sort_passages(vec![
            passage("vault", "/Evidence/./a.md", 0.75),
            passage("notes", "notes", 0.99),
            passage("folder", "/Evidence/a.md", 0.86 + 0.10),
            passage("folder", "/Evidence/c.md", 0.91),
            passage("attachment", "/Evidence/c.md", 0.80),
            passage("folder", "/Evidence/b.md", 0.91),
            passage("vault", "/evidence/a.md", 0.75),
        ]);
        assert_eq!(sorted.len(), 5);
        assert_eq!(
            sorted
                .iter()
                .map(|p| p.source_id.as_str())
                .collect::<Vec<_>>(),
            [
                "/Evidence/a.md",
                "notes",
                "/Evidence/b.md",
                "/Evidence/c.md",
                "/evidence/a.md"
            ]
        );
        assert_eq!(
            crate::copilot_provenance::canonical_evidence_key(&passage(
                "project",
                "/Projects/./A",
                1.0
            )),
            "project:/Projects/A"
        );
        assert_eq!(
            crate::copilot_provenance::canonical_evidence_key(&passage("meeting", "42", 1.0)),
            "meeting:42"
        );
    }
}
