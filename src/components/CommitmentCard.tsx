import { useEffect, useRef, useState } from "react";
import type { Commitment, CommitmentResult, WorkspaceArtifact } from "../types";
import {
  commitmentApprove,
  commitmentDismiss,
  getLatestWorkspaceRun,
  getWorkspace,
  openWorkspaceArtifact,
} from "../lib/tauri";
import {
  CAPABILITY_ARTIFACT_NOUN,
  CAPABILITY_OPTIONS,
  isTaskCapability,
  type TaskCapability,
} from "./workspaces/capabilities";

interface CommitmentCardProps {
  commitment: Commitment;
}

/** How often an approved commitment asks its task how it is getting on. */
const PROGRESS_POLL_MS = 3000;

type Stage = "queued" | "running" | "ready" | "failed" | "paused";

function stageLabel(stage: Stage, capability: TaskCapability): string {
  if (stage === "paused") return "Waiting — agents are paused";
  if (stage === "queued") return "Queued for an agent";
  if (stage === "running") return "Working on it…";
  if (stage === "failed") return "The run did not finish";
  return `${CAPABILITY_ARTIFACT_NOUN[capability]} ready`;
}

export function CommitmentCard({ commitment }: CommitmentCardProps): JSX.Element | null {
  const [approving, setApproving] = useState(false);
  const [dismissing, setDismissing] = useState(false);
  const [result, setResult] = useState<CommitmentResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [hidden, setHidden] = useState(false);
  const [capability, setCapability] = useState<TaskCapability>(
    isTaskCapability(commitment.capability) ? commitment.capability : "write",
  );
  const [stage, setStage] = useState<Stage | null>(null);
  const [artifact, setArtifact] = useState<WorkspaceArtifact | null>(null);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const isApproved = commitment.state === "approved" || result !== null;
  const taskId = result?.task.id ?? commitment.task_id;
  const workspaceId = result?.task.workspace_id ?? null;
  const agentsPaused = result ? result.agents_paused : commitment.agents_paused;

  // Follow the task the approval created, so the answer lands on this card
  // instead of making the user go hunting for it in the Workspaces tab.
  useEffect(() => {
    if (!isApproved || taskId == null) return;
    let cancelled = false;

    const check = async () => {
      try {
        const run = await getLatestWorkspaceRun(taskId);
        if (cancelled) return;
        if (!run) {
          setStage(agentsPaused ? "paused" : "queued");
          return;
        }
        if (run.status === "running") {
          setStage("running");
          return;
        }
        if (run.status === "failed") {
          setStage("failed");
        } else if (run.status === "done") {
          setStage("ready");
          if (workspaceId != null) {
            try {
              const detail = await getWorkspace(workspaceId);
              if (cancelled) return;
              const made = detail.artifacts.filter((item) => item.run_id === run.id);
              if (made.length > 0) setArtifact(made[0]);
            } catch {
              // the stage still reads "ready"; only the shortcut is missing
            }
          }
        } else {
          setStage(agentsPaused ? "paused" : "queued");
          return;
        }
        if (pollRef.current) {
          clearInterval(pollRef.current);
          pollRef.current = null;
        }
      } catch {
        // transient; the next tick tries again
      }
    };

    setStage(agentsPaused ? "paused" : "queued");
    void check();
    pollRef.current = setInterval(() => {
      void check();
    }, PROGRESS_POLL_MS);

    return () => {
      cancelled = true;
      if (pollRef.current) {
        clearInterval(pollRef.current);
        pollRef.current = null;
      }
    };
  }, [isApproved, taskId, workspaceId, agentsPaused]);

  // If externally marked dismissed, hide (parent filters, but immediate hide for stale render)
  if (hidden || commitment.state === "dismissed") return null;

  const handleApprove = async () => {
    setError(null);
    setApproving(true);
    try {
      const res = await commitmentApprove(commitment.session_id, commitment.id, capability);
      setResult(res);
    } catch (e) {
      setError(String(e));
    } finally {
      setApproving(false);
    }
  };

  const handleDismiss = async () => {
    setError(null);
    setDismissing(true);
    try {
      await commitmentDismiss(commitment.session_id, commitment.id);
      setHidden(true);
    } catch (e) {
      setError(String(e));
    } finally {
      setDismissing(false);
    }
  };

  const handleOpenWorkspaces = () => {
    try {
      window.dispatchEvent(
        new CustomEvent("adversaria:open-view", {
          detail: { view: "workspaces", workspaceId, taskId },
        }),
      );
    } catch {
      // the tab is still reachable by hand
    }
  };

  const handleOpenArtifact = async () => {
    if (!artifact) return;
    try {
      await openWorkspaceArtifact(artifact.path);
    } catch (e) {
      setError(String(e));
    }
  };

  const shown: Stage = stage ?? (agentsPaused ? "paused" : "queued");

  return (
    <article
      className={`commitment-card${isApproved ? " approved" : ""}`}
      data-testid={`commitment-card-${commitment.id}`}
      data-stage={isApproved ? shown : "caught"}
      aria-label={`Commitment: ${commitment.text}`}
    >
      <p className="commitment-text" dir="auto">{commitment.text}</p>
      {(commitment.owner || commitment.deadline) && (
        <div className="commitment-chips">
          {commitment.owner && (
            <span className="badge-tag commitment-chip" data-testid="commitment-owner-chip">
              {commitment.owner}
            </span>
          )}
          {commitment.deadline && (
            <span className="badge-tag commitment-chip" data-testid="commitment-deadline-chip">
              {commitment.deadline}
            </span>
          )}
        </div>
      )}
      {!isApproved ? (
        <div className="commitment-actions">
          <label className="commitment-type">
            <span className="commitment-type-label">Do</span>
            <select
              className="commitment-type-select"
              aria-label="Task type"
              value={capability}
              disabled={approving || dismissing}
              onChange={(e) => {
                const next = e.target.value;
                if (isTaskCapability(next)) setCapability(next);
              }}
            >
              {CAPABILITY_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </label>
          <span className="commitment-actions-spacer" />
          <button
            type="button"
            className="btn-primary"
            onClick={() => void handleApprove()}
            disabled={approving || dismissing}
          >
            {approving ? "Approving…" : "Approve"}
          </button>
          <button
            type="button"
            className="btn-secondary"
            onClick={() => void handleDismiss()}
            disabled={approving || dismissing}
          >
            {dismissing ? "Dismissing…" : "Dismiss"}
          </button>
        </div>
      ) : (
        <div className="commitment-approved">
          <span className={`commitment-stage commitment-stage--${shown}`} role="status">
            {stageLabel(shown, capability)}
          </span>
          <span className="commitment-actions-spacer" />
          {artifact ? (
            <button type="button" className="btn-primary" onClick={() => void handleOpenArtifact()}>
              Open {CAPABILITY_ARTIFACT_NOUN[capability].toLowerCase()}
            </button>
          ) : null}
          <button type="button" className="btn-ghost" onClick={handleOpenWorkspaces}>
            Open in Workspaces
          </button>
        </div>
      )}
      {error && <p className="commitment-error">{error}</p>}
    </article>
  );
}
