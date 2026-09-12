import type { ReactNode } from "react";
import { useEffect, useLayoutEffect, useRef, useState } from "react";
import type { CopilotCard, CopilotMode, CopilotPassage } from "../types";
import { copilotSetMicQuestions } from "../lib/tauri";

export interface CopilotCardsProps {
  cards: CopilotCard[];
  onForceCard: (useMeFallback: boolean) => void;
  onPin: (card: CopilotCard) => void;
  onCancel?: (cardId: number) => void;
  onRetry?: (cardId: number) => void;
  copilotMode?: CopilotMode;
  webEnabled?: boolean;
  copilotSessionId?: string | null;
  /** Hide the manual-answer / mic / privacy header (the compact companion renders its own). */
  showControls?: boolean;
  /** Compact companion: fold Specifics and From your notes under a "More" disclosure. */
  compact?: boolean;
  /** Controlled mic flag: when `onMicQuestionsChange` is given the companion owns the checkbox and privacy line. */
  micQuestions?: boolean;
  onMicQuestionsChange?: (checked: boolean) => void;
}

export function readMicQuestionsFlag(): boolean {
  try {
    return localStorage.getItem("copilot.micQuestions") === "1";
  } catch {
    return false;
  }
}

export function persistMicQuestionsFlag(checked: boolean): void {
  try {
    localStorage.setItem("copilot.micQuestions", checked ? "1" : "0");
  } catch {}
  copilotSetMicQuestions(checked).catch(() => {});
}

function providerName(provider: string | undefined): string {
  if (provider === "no_ai") return "No AI";
  if (provider === "local") return "Local";
  if (provider === "deepseek") return "DeepSeek";
  return "Claude";
}

function formatTime(askedAtMs: number): string {
  const d = new Date(askedAtMs);
  const m = String(d.getMinutes()).padStart(2, "0");
  const s = String(d.getSeconds()).padStart(2, "0");
  return `${m}:${s}`;
}

function sourceLabel(passage: CopilotPassage): string {
  switch (passage.source_kind) {
    case "meeting":
      return passage.title;
    case "vault":
      return passage.title;
    case "project":
      return passage.title;
    case "notes":
      return "Your notes";
    case "attachment":
      return passage.title;
    case "folder":
      return passage.title;
    default:
      return passage.title;
  }
}

function escapeRegExp(s: string): string {
  return s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

export function cleanPassageText(text: string, title: string): string {
  if (!text) return "";
  const lines = text.split(/\r?\n/);
  if (title && lines.length > 0) {
    const first = lines[0].trim();
    const t = title.trim();
    if (t) {
      const lowerFirst = first.toLowerCase();
      const lowerTitle = t.toLowerCase();
      let shouldDrop = lowerFirst === lowerTitle;
      if (!shouldDrop) {
        const esc = escapeRegExp(t);
        const re = new RegExp(`^${esc}\\s*\\(.*\\)\\s*$`, "i");
        if (re.test(first)) shouldDrop = true;
      }
      if (shouldDrop) {
        lines.shift();
      }
    }
  }
  return lines.join("\n");
}

export function renderPassage(text: string): ReactNode[] {
  if (!text) return [];
  const result: ReactNode[] = [];
  const re = /\*\*(.+?)\*\*/g;
  let lastIndex = 0;
  let match: RegExpExecArray | null;
  let key = 0;
  while ((match = re.exec(text)) !== null) {
    const before = text.slice(lastIndex, match.index);
    if (before) result.push(before);
    result.push(<strong key={key++}>{match[1]}</strong>);
    lastIndex = match.index + match[0].length;
  }
  const after = text.slice(lastIndex);
  if (after) result.push(after);
  if (result.length === 0) result.push(text);
  return result;
}

function renderAnswerText(text: string, isStreaming: boolean): JSX.Element {
  const lines = text.split("\n");
  const bulletLines: string[] = [];
  const otherLines: string[] = [];
  for (const line of lines) {
    if (/^\s*-\s/.test(line)) bulletLines.push(line.replace(/^\s*-\s/, ""));
    else if (line.trim() !== "") otherLines.push(line);
  }
  const bullets = bulletLines.length > 0 ? bulletLines : otherLines;
  if (bullets.length === 0 && !text) {
    return <>{isStreaming ? <span className="copilot-answer-cursor">▌</span> : null}</>;
  }
  if (bulletLines.length > 0) {
    return (
      <ul className="copilot-answer-list">
        {bullets.map((b, i) => (
          <li key={i} className="copilot-answer-bullet" dir="auto">
            {b}
            {isStreaming && i === bullets.length - 1 ? <span className="copilot-answer-cursor">▌</span> : null}
          </li>
        ))}
      </ul>
    );
  }
  return (
    <p className="copilot-answer-text" dir="auto">
      {text}
      {isStreaming ? <span className="copilot-answer-cursor">▌</span> : null}
    </p>
  );
}

function domainFromUrl(url: string): string {
  try {
    return new URL(url).hostname.replace(/^www\./, "");
  } catch {
    return "";
  }
}

function splitContextTurn(turn: string): { speaker: string; text: string } {
  const match = /^(Me|Them):\s*([\s\S]*)$/.exec(turn.trim());
  return match ? { speaker: match[1], text: match[2] } : { speaker: "Context", text: turn };
}

export function CopilotCards({ cards, onForceCard, onPin, onCancel, onRetry, copilotMode = "no_ai", webEnabled = false, copilotSessionId, showControls = true, compact = false, micQuestions, onMicQuestionsChange }: CopilotCardsProps): JSX.Element {
  const scrollRef = useRef<HTMLDivElement>(null);
  const prevLenRef = useRef(cards.length);
  const [expandedPassages, setExpandedPassages] = useState<Set<string>>(() => new Set());
  const [expandedSources, setExpandedSources] = useState<Set<string>>(() => new Set());
  const [expandedContexts, setExpandedContexts] = useState<Set<string>>(() => new Set());
  const [ownMicFlag, setOwnMicFlag] = useState(readMicQuestionsFlag);
  const micControlled = onMicQuestionsChange !== undefined;
  const useMeFallback = micControlled ? !!micQuestions : ownMicFlag;
  const [showNewPill, setShowNewPill] = useState(false);

  useLayoutEffect(() => {
    if (cards.length > prevLenRef.current) {
      const el = scrollRef.current;
      if (el) {
        if (el.scrollTop <= 40) {
          el.scrollTop = 0;
          setShowNewPill(false);
        } else {
          const firstArticle = el.querySelector("article") as HTMLElement | null;
          if (firstArticle) {
            el.scrollTop += firstArticle.offsetHeight;
          }
          setShowNewPill(true);
        }
      }
    }
    prevLenRef.current = cards.length;
  }, [cards.length]);

  useEffect(() => {
    const trimmed = copilotSessionId?.trim();
    if (trimmed && useMeFallback) {
      copilotSetMicQuestions(true).catch(() => {});
    }
  }, [copilotSessionId, useMeFallback]);

  function handleScroll(): void {
    const el = scrollRef.current;
    if (!el) return;
    if (el.scrollTop <= 40 && showNewPill) {
      setShowNewPill(false);
    }
  }

  function togglePassage(key: string): void {
    setExpandedPassages((prev) => {
      const next = new Set(prev);
      if (next.has(key)) next.delete(key);
      else next.add(key);
      return next;
    });
  }

  function toggleSources(key: string): void {
    setExpandedSources((prev) => {
      const next = new Set(prev);
      if (next.has(key)) next.delete(key);
      else next.add(key);
      return next;
    });
  }

  function toggleContext(key: string): void {
    setExpandedContexts((prev) => {
      const next = new Set(prev);
      if (next.has(key)) next.delete(key);
      else next.add(key);
      return next;
    });
  }

  return (
    <div className="copilot-cards">
      {showControls && <div className="copilot-header">
        <button
          type="button"
          className="copilot-force-btn"
          onClick={() => onForceCard(useMeFallback)}
        >
          Answer current question
        </button>
        {!micControlled && <label className="copilot-me-toggle">
          <input
            type="checkbox"
            checked={useMeFallback}
            onChange={(event) => {
              const checked = event.target.checked;
              setOwnMicFlag(checked);
              persistMicQuestionsFlag(checked);
            }}
            aria-label="Questions can come from my mic"
          />
          Questions can come from my mic
        </label>}
        {!micControlled && (copilotMode === "local" || copilotMode === "no_ai") && (
          <span className="copilot-privacy">
            {copilotMode === "local"
              ? "Current conversation stays on this Mac · 0 bytes sent"
              : "Your notes and conversation stay on this Mac"}
          </span>
        )}
      </div>}

      {cards.length === 0 ? (
        <>
          <p className="copilot-empty">Questions from the other side will appear here as short, live answers.</p>
          <p className="copilot-hint">Testing alone? Tick &quot;Questions can come from my mic&quot; and ask out loud.</p>
        </>
      ) : (
        <div className="copilot-list" ref={scrollRef} role="feed" aria-label="Copilot answers" onScroll={handleScroll}>
          {showNewPill && (
            <button
              type="button"
              className="copilot-new-pill"
              onClick={() => {
                const el = scrollRef.current;
                if (el) el.scrollTo({ top: 0 });
                setShowNewPill(false);
              }}
            >
              New question ↑
            </button>
          )}
          {cards.map((card, index) => {
            const isStreaming = card.answer?.status === "streaming" || card.answer?.status === "searching";
            const showNothingInNotes = card.passages.length === 0 && card.status !== "heard";
            const canPin = card.passages.length > 0 || !!(card.answer?.text?.trim() || card.answer?.provenance?.length || card.answer?.sections);
            const cardKey = `${card.session_id}-${card.id}`;
            const sourcesAreOpen = expandedSources.has(cardKey);
            const contextIsOpen = expandedContexts.has(cardKey);
            const sourcesId = `copilot-sources-${card.id}`;
            const contextId = `copilot-context-${card.id}`;
            const contextTurns = card.context_turns ?? [];
            const contextCount = contextTurns.length + 1;
            const active = card.status === "heard" || card.status === "answering";

            return (
              <article
                key={cardKey}
                data-testid={`copilot-card-${card.id}`}
                className={`copilot-card${index === 0 ? " copilot-card--new" : ""}${active ? " copilot-card--active" : ""}`}
                aria-label={`Copilot answer for: ${card.question}`}
              >
                <div className="copilot-card-question">
                  <span className="copilot-question-text" dir="auto">{card.question}</span>
                  <span className="copilot-provider-chip">{providerName(card.provider_frozen)}</span>
                  <span className="copilot-time">{formatTime(card.asked_at_ms)}</span>
                  {card.trigger === "manual" && <span className="copilot-manual-chip">manual</span>}
                </div>

                <p className="copilot-lifecycle" data-testid="copilot-lifecycle">
                  {card.status === "heard" && "Heard the complete question"}
                  {card.status === "answering" && card.answer?.status === "searching" && "Searching the web…"}
                  {card.status === "answering" && card.answer && card.answer.status !== "searching" && card.answer.status !== "done" && card.answer.status !== "error" && card.answer.status !== "cancelled" && (
                    <>Answering ({providerName(card.answer.provider)})…</>
                  )}
                  {card.status === "answering" && !card.answer && "Looking in your notes…"}
                  {card.status === "done" && card.provider_frozen === "no_ai" && "Done · No AI · passages only"}
                  {card.status === "skipped" && (card.reason === "superseded" ? "Skipped, newer question arrived" : card.reason === "cancelled" ? "Skipped: cancelled" : card.reason === "session_ended" ? "Skipped: session ended" : "Skipped")}
                  {card.status === "done" && card.provider_frozen !== "no_ai" && card.answer?.status === "done" && "Done"}
                </p>

                {card.answer && (
                  <div className={`copilot-answer${isStreaming ? " copilot-answer--streaming" : ""}`} aria-live="polite">
                    {(() => {
                      const answer = card.answer!;
                      const retryMatchesConsent =
                        card.provider_frozen === copilotMode &&
                        !(answer.web_requested === true && !webEnabled);
                      if (answer.status === "error") {
                        return (
                          <>
                            <p className="copilot-answer-error" dir="auto">{answer.error}</p>
                            {onRetry && retryMatchesConsent && <button type="button" className="copilot-retry-btn" onClick={() => onRetry(card.id)}>Retry</button>}
                          </>
                        );
                      }
                      if (answer.status === "cancelled") {
                        const reasonLabel = answer.reason === "user" ? "Cancelled" : answer.reason === "mode_changed" ? "Cancelled: mode changed" : answer.reason === "session_ended" ? "Cancelled: session ended" : "Cancelled";
                        return (
                          <>
                            <p className="copilot-answer-cancelled" dir="auto">{reasonLabel}</p>
                            {onRetry && retryMatchesConsent && <button type="button" className="copilot-retry-btn" onClick={() => onRetry(card.id)}>Retry</button>}
                          </>
                        );
                      }
                      const hasSections = !!answer.sections && (answer.status === "streaming" || answer.status === "searching" || answer.status === "done");
                      if (hasSections) {
                        const sections = answer.sections!;
                        const saySentences = sections.say ?? [];
                        const specifics = (sections.specifics ?? []).filter((s) => s.trim() !== "");
                        const notes = sections.notes ?? [];
                        const nextVal = sections.next ?? null;
                        // streaming without sections yet but hasSections false handled below; this branch is rev6
                        return (
                          <>
                            {answer.status === "searching" && <p className="copilot-answer-searching">Searching the web…</p>}
                            <p className="copilot-say-eyebrow">Say</p>
                            <p className="copilot-say" dir="auto">
                              {saySentences.map((sentence, sIdx) => (
                                <span key={sIdx} className="copilot-say-sentence">{sentence}{sIdx < saySentences.length - 1 ? " " : ""}</span>
                              ))}
                              {(isStreaming || answer.status === "searching") && saySentences.length === 0 ? <span className="copilot-answer-cursor">▌</span> : null}
                              {isStreaming && saySentences.length > 0 ? <span className="copilot-answer-cursor">▌</span> : null}
                            </p>
                            {(() => {
                              const detail = (
                                <>
                                  {specifics.length > 0 && (
                                    <ul className="copilot-specifics">
                                      {specifics.map((spec, sIdx) => (
                                        <li key={sIdx} className="copilot-specific" dir="auto">{spec}</li>
                                      ))}
                                    </ul>
                                  )}
                                  {notes.length > 0 && (
                                    <div className="copilot-notes">
                                      <span className="copilot-notes-label">From your notes</span>
                                      {notes.map((note, nIdx) => {
                                        const title = typeof note.passage_index === "number" ? (card.passages[note.passage_index]?.title ?? `P${(note.passage_index ?? 0) + 1}`) : "Notes";
                                        const hasQuote = note.quote && note.quote.trim() !== "";
                                        return (
                                          <div key={nIdx} className="copilot-note">
                                            <span className="copilot-chip chip--notes">{title}</span>
                                            {hasQuote ? (
                                              <>
                                                <q dir="auto">{note.quote}</q>
                                                <span className="copilot-note-clause">{note.clause}</span>
                                              </>
                                            ) : (
                                              <span className="copilot-note-raw" dir="auto">{note.text}</span>
                                            )}
                                          </div>
                                        );
                                      })}
                                    </div>
                                  )}
                                </>
                              );
                              if (compact && (specifics.length > 0 || notes.length > 0)) {
                                return (
                                  <details className="copilot-more">
                                    <summary>More</summary>
                                    {detail}
                                  </details>
                                );
                              }
                              return detail;
                            })()}
                            {nextVal && nextVal.trim() !== "" && (
                              <details className="copilot-next">
                                <summary>Possible follow-up</summary>
                                <p dir="auto">{nextVal}</p>
                              </details>
                            )}
                            {answer.status === "done" && (
                              <p className="copilot-answer-footer">
                                {answer.provider === "local" ? "0 bytes left this Mac" : `Prepared request payload: ${answer.egress_bytes ?? 0} bytes`}
                                {answer.web_performed != null && answer.web_performed > 0 ? ` · ${answer.web_performed} web searches` : ""}
                              </p>
                            )}
                            {isStreaming && onCancel && <button type="button" className="copilot-cancel-btn" onClick={() => onCancel(card.id)}>Cancel</button>}
                          </>
                        );
                      }
                      // legacy / No AI path
                      return (
                        <>
                          {answer.status === "searching" && <p className="copilot-answer-searching">Searching the web…</p>}
                          {answer.status === "done" && answer.provenance && answer.provenance.length > 0 ? (
                            <ul className="copilot-answer-list">
                              {answer.provenance.map((bullet, bulletIndex) => {
                                const isWeb = bullet.label === "web" && !!bullet.url;
                                const domain = isWeb ? domainFromUrl(bullet.url!) : "";
                                const chipLabel = bullet.label === "notes" ? "your notes" : isWeb ? `web · ${domain}` : providerName(answer.provider);
                                const chipClass = bullet.label === "notes" ? "chip--notes" : bullet.label === "web" ? "chip--web" : "chip--model";
                                const chip = <span className={`copilot-chip ${chipClass}`}>{chipLabel}</span>;
                                return (
                                  <li key={bulletIndex} className="copilot-answer-bullet" dir="auto">
                                    {bullet.text}{" "}
                                    {isWeb && bullet.url ? <a href={bullet.url} target="_blank" rel="noreferrer">{chip}</a> : chip}
                                  </li>
                                );
                              })}
                            </ul>
                          ) : (
                            renderAnswerText(answer.text, isStreaming)
                          )}
                          {answer.status === "done" && (
                            <p className="copilot-answer-footer">
                              {answer.provider === "local" ? "0 bytes left this Mac" : `Prepared request payload: ${answer.egress_bytes ?? 0} bytes`}
                              {answer.web_performed != null && answer.web_performed > 0 ? ` · ${answer.web_performed} web searches` : ""}
                            </p>
                          )}
                          {isStreaming && onCancel && <button type="button" className="copilot-cancel-btn" onClick={() => onCancel(card.id)}>Cancel</button>}
                        </>
                      );
                    })()}
                  </div>
                )}

                {card.status === "answering" && !card.answer && onCancel && (
                  <button type="button" className="copilot-cancel-btn" onClick={() => onCancel(card.id)}>Cancel</button>
                )}

                <div className="copilot-card-footer">
                  <div className="copilot-card-context">
                    <button
                      type="button"
                      className="copilot-disclosure-btn"
                      aria-expanded={contextIsOpen}
                      aria-controls={contextId}
                      onClick={() => toggleContext(cardKey)}
                    >
                      <span className="copilot-disclosure-caret" aria-hidden="true">›</span>
                      Context <span>· {contextCount} {contextCount === 1 ? "turn" : "turns"}</span>
                    </button>
                    {card.passages.length > 0 ? (
                      <button
                        type="button"
                        className="copilot-disclosure-btn"
                        aria-expanded={sourcesAreOpen}
                        aria-controls={sourcesId}
                        onClick={() => toggleSources(cardKey)}
                      >
                        <span className="copilot-disclosure-caret" aria-hidden="true">›</span>
                        Sources <span>· {card.passages.length}</span>
                      </button>
                    ) : showNothingInNotes ? (
                      <span className="copilot-no-passages">No matching notes</span>
                    ) : null}
                    <span className="copilot-retrieval">{card.retrieval_ms != null ? `${card.retrieval_ms} ms` : ""}</span>
                  </div>
                  <button
                    type="button"
                    className="copilot-pin-btn"
                    aria-label={`Pin card ${card.id} to notes`}
                    onClick={() => onPin(card)}
                    disabled={!canPin}
                  >
                    Pin
                  </button>
                </div>

                {contextIsOpen && (
                  <div className="copilot-context-window" id={contextId}>
                    <strong>Conversation used for this answer</strong>
                    {[...contextTurns, `${card.question_source ?? "Them"}: ${card.question}`].map((turn, turnIndex) => {
                      const parsed = splitContextTurn(turn);
                      return (
                        <div className="copilot-context-turn" key={`${cardKey}-context-${turnIndex}`}>
                          <span>{parsed.speaker}</span>
                          <p dir="auto">{parsed.text}</p>
                        </div>
                      );
                    })}
                  </div>
                )}

                {sourcesAreOpen && card.passages.length > 0 && (
                  <div className="copilot-passages" id={sourcesId}>
                    {card.passages.map((passage, passageIndex) => {
                      const key = `${cardKey}-${passageIndex}`;
                      const cleaned = cleanPassageText(passage.text, passage.title);
                      const needsToggle = cleaned.split("\n").length > 6 || cleaned.length > 420;
                      const isExpanded = expandedPassages.has(key);
                      const clamped = needsToggle && !isExpanded;
                      return (
                        <div key={key} className="copilot-passage">
                          <span className="context-used-chip" title={passage.source_id}>{sourceLabel(passage)}</span>
                          <p className={`copilot-passage-text${clamped ? " copilot-passage-text--clamped" : ""}`} dir="auto">
                            {renderPassage(cleaned)}
                          </p>
                          {needsToggle && (
                            <button type="button" className="copilot-passage-toggle" onClick={() => togglePassage(key)}>
                              {isExpanded ? "Show less" : "Show more"}
                            </button>
                          )}
                        </div>
                      );
                    })}
                  </div>
                )}
              </article>
            );
          })}
        </div>
      )}
    </div>
  );
}
