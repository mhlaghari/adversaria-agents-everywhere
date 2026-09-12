import type { CopilotMode } from "../types";

export interface CopilotConsentBarProps {
  mode: CopilotMode;
  hasClaudeKey: boolean;
  hasDeepSeekKey?: boolean;
  hasFolder?: boolean;
  onChange: (mode: CopilotMode) => void;
}

const LINES: Record<CopilotMode, string> = {
  no_ai: "No AI \u00b7 passages from your notes only, nothing leaves this Mac",
  local: "Copilot on \u00b7 Local \u00b7 answers from your machine using this folder's sources",
  claude: "Copilot on \u00b7 Claude \u00b7 sends the current question, up to 4 recent turns, up to 3 passages from this folder's sources, this folder's instructions, your folder profile and voice samples; never the full transcript. Also sent: a one-paragraph summary of each project in this folder, and up to three earlier copilot suggestions from this session.",
  deepseek: "Copilot on \u00b7 DeepSeek \u00b7 sends the current question, up to 4 recent turns, up to 3 passages from this folder's sources, this folder's instructions, your folder profile and voice samples; never the full transcript. Also sent: a one-paragraph summary of each project in this folder, and up to three earlier copilot suggestions from this session.",
};

const SUMMARIES: Record<CopilotMode, string> = {
  no_ai: "No AI \u00b7 passages from your notes only \u00b7 nothing leaves this Mac",
  local: "Local \u00b7 question, recent turns, 3 passages, profile \u00b7 nothing leaves this Mac",
  claude: "Claude \u00b7 question, 4 turns, 3 passages, profile, project pack, 3 earlier cards \u00b7 never the transcript",
  deepseek: "DeepSeek \u00b7 question, 4 turns, 3 passages, profile, project pack, 3 earlier cards \u00b7 never the transcript",
};

export function CopilotConsentBar({ mode, hasClaudeKey, hasDeepSeekKey = false, hasFolder = true, onChange }: CopilotConsentBarProps): JSX.Element {
  return (
    <div className="copilot-consent">
      <div role="radiogroup" className="copilot-consent-seg" aria-label="Copilot mode">
        <button
          type="button"
          role="radio"
          aria-checked={mode === "no_ai"}
          className={mode === "no_ai" ? "copilot-consent-seg--active" : undefined}
          onClick={() => onChange("no_ai")}
        >
          No AI
        </button>
        <button
          type="button"
          role="radio"
          aria-checked={mode === "local"}
          className={mode === "local" ? "copilot-consent-seg--active" : undefined}
          onClick={() => onChange("local")}
        >
          AI · Local
        </button>
        <button
          type="button"
          role="radio"
          aria-checked={mode === "claude"}
          className={mode === "claude" ? "copilot-consent-seg--active" : undefined}
          disabled={!hasClaudeKey}
          title={!hasClaudeKey ? "Add an Anthropic API key in Settings \u203a Live Copilot" : undefined}
          onClick={() => onChange("claude")}
        >
          AI · Claude
        </button>
        <button
          type="button"
          role="radio"
          aria-checked={mode === "deepseek"}
          className={mode === "deepseek" ? "copilot-consent-seg--active" : undefined}
          disabled={!hasDeepSeekKey}
          title={!hasDeepSeekKey ? "Add a DeepSeek API key in Settings › Live Copilot" : undefined}
          onClick={() => onChange("deepseek")}
        >
          AI · DeepSeek
        </button>
      </div>
      <details className="copilot-consent-details">
        <summary className="copilot-consent-summary">{SUMMARIES[mode]}</summary>
        <p className="copilot-consent-line">{LINES[mode]}</p>
      </details>
      {!hasFolder && mode !== "no_ai" && (
        <p className="copilot-consent-line">No folder chosen: only your live notes and attachments are searched.</p>
      )}
      {mode === "claude" && !hasClaudeKey && (
        <p className="copilot-consent-missing">Add an Anthropic API key in Settings › Live Copilot</p>
      )}
      {mode === "deepseek" && !hasDeepSeekKey && (
        <p className="copilot-consent-missing">Add a DeepSeek API key in Settings › Live Copilot</p>
      )}
    </div>
  );
}
