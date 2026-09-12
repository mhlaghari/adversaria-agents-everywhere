import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi, beforeEach } from "vitest";
import type { Commitment, WorkspaceRun } from "../types";

const mocks = vi.hoisted(() => ({
  approve: vi.fn(),
  dismiss: vi.fn(),
  latestRun: vi.fn(),
  getWorkspace: vi.fn(),
  openArtifact: vi.fn(),
}));

vi.mock("../lib/tauri", () => ({
  commitmentApprove: mocks.approve,
  commitmentDismiss: mocks.dismiss,
  getLatestWorkspaceRun: mocks.latestRun,
  getWorkspace: mocks.getWorkspace,
  openWorkspaceArtifact: mocks.openArtifact,
}));

import { CommitmentCard } from "./CommitmentCard";

function commitment(overrides: Partial<Commitment> = {}): Commitment {
  return {
    session_id: "sess-1",
    id: 1,
    text: "I'll send the numbers to Wael by Monday",
    owner: "Wael",
    deadline: "by Monday",
    source: "Me",
    at_ms: Date.now(),
    state: "caught",
    capability: "write",
    task_id: null,
    run_queued: false,
    agents_paused: false,
    ...overrides,
  };
}

function task(overrides: Record<string, unknown> = {}) {
  return {
    id: 42,
    workspace_id: 1,
    title: "t",
    details: "",
    capability: "write",
    status: "queued",
    source_meeting_id: null,
    source_meeting_title: "",
    action_item_id: null,
    attempt: 1,
    rejection_notes: [],
    agent_eligible: true,
    created_at: "",
    updated_at: "",
    ...overrides,
  };
}

function run(overrides: Partial<WorkspaceRun> = {}): WorkspaceRun {
  return {
    id: 9,
    workspace_id: 1,
    task_id: 42,
    engine: "local",
    status: "running",
    log: "",
    report: "",
    error: "",
    started_at: "",
    finished_at: "",
    ...overrides,
  };
}

describe("commitment_card_flow", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mocks.latestRun.mockResolvedValue(null);
    mocks.getWorkspace.mockResolvedValue({ workspace: {}, context_items: [], addons: [], tasks: [], artifacts: [] });
  });

  it("renders owner and deadline chips", () => {
    render(<CommitmentCard commitment={commitment()} />);
    expect(screen.getByText("Wael")).toBeInTheDocument();
    expect(screen.getByText("by Monday")).toBeInTheDocument();
  });

  it("offers the inferred task type and sends it on approve", async () => {
    mocks.approve.mockResolvedValue({ task: task(), run_queued: true, agents_paused: false });
    render(<CommitmentCard commitment={commitment({ capability: "research" })} />);
    const select = screen.getByLabelText("Task type") as HTMLSelectElement;
    expect(select.value).toBe("research");
    await userEvent.setup().click(screen.getByRole("button", { name: "Approve" }));
    await waitFor(() => expect(mocks.approve).toHaveBeenCalledWith("sess-1", 1, "research"));
  });

  it("lets the user correct the task type before approving", async () => {
    mocks.approve.mockResolvedValue({ task: task(), run_queued: true, agents_paused: false });
    const user = userEvent.setup();
    render(<CommitmentCard commitment={commitment({ capability: "write" })} />);
    await user.selectOptions(screen.getByLabelText("Task type"), "research");
    await user.click(screen.getByRole("button", { name: "Approve" }));
    await waitFor(() => expect(mocks.approve).toHaveBeenCalledWith("sess-1", 1, "research"));
  });

  it("after approve it reports progress in plain words, not a task id", async () => {
    mocks.approve.mockResolvedValue({ task: task(), run_queued: true, agents_paused: false });
    mocks.latestRun.mockResolvedValue(run({ status: "running" }));
    render(<CommitmentCard commitment={commitment()} />);
    await userEvent.setup().click(screen.getByRole("button", { name: "Approve" }));
    await waitFor(() => expect(screen.getByText("Working on it…")).toBeInTheDocument());
    expect(screen.queryByText(/Task #/)).not.toBeInTheDocument();
  });

  it("says agents are paused when they are", async () => {
    mocks.approve.mockResolvedValue({ task: task({ id: 7 }), run_queued: false, agents_paused: true });
    render(<CommitmentCard commitment={commitment({ id: 2 })} />);
    await userEvent.setup().click(screen.getByRole("button", { name: "Approve" }));
    await waitFor(() => expect(screen.getByText("Waiting — agents are paused")).toBeInTheDocument());
  });

  it("surfaces the finished artifact on the card", async () => {
    mocks.approve.mockResolvedValue({ task: task(), run_queued: true, agents_paused: false });
    mocks.latestRun.mockResolvedValue(run({ status: "done" }));
    mocks.getWorkspace.mockResolvedValue({
      workspace: {},
      context_items: [],
      addons: [],
      tasks: [],
      artifacts: [{ id: 3, workspace_id: 1, run_id: 9, name: "draft.md", path: "/tmp/draft.md", created_at: "" }],
    });
    const user = userEvent.setup();
    render(<CommitmentCard commitment={commitment({ id: 6 })} />);
    await user.click(screen.getByRole("button", { name: "Approve" }));
    await waitFor(() => expect(screen.getByText("Draft ready")).toBeInTheDocument());
    await user.click(screen.getByRole("button", { name: "Open draft" }));
    expect(mocks.openArtifact).toHaveBeenCalledWith("/tmp/draft.md");
  });

  it("Dismiss hides the card", async () => {
    mocks.dismiss.mockResolvedValue(undefined);
    render(<CommitmentCard commitment={commitment({ id: 3 })} />);
    expect(screen.getByText("I'll send the numbers to Wael by Monday")).toBeInTheDocument();
    await userEvent.setup().click(screen.getByRole("button", { name: "Dismiss" }));
    await waitFor(() => expect(screen.queryByText("I'll send the numbers to Wael by Monday")).not.toBeInTheDocument());
  });

  it("shows inline error on approve failure", async () => {
    mocks.approve.mockRejectedValue(new Error("network down"));
    render(<CommitmentCard commitment={commitment({ id: 4 })} />);
    await userEvent.setup().click(screen.getByRole("button", { name: "Approve" }));
    await waitFor(() => expect(screen.getByText(/network down/)).toBeInTheDocument());
  });

  it("Open in Workspaces dispatches adversaria:open-view with the task", async () => {
    mocks.approve.mockResolvedValue({ task: task(), run_queued: true, agents_paused: false });
    const handler = vi.fn();
    window.addEventListener("adversaria:open-view", handler as EventListener);
    render(<CommitmentCard commitment={commitment({ id: 5 })} />);
    await userEvent.setup().click(screen.getByRole("button", { name: "Approve" }));
    await waitFor(() => expect(screen.getByText("Open in Workspaces")).toBeInTheDocument());
    await userEvent.setup().click(screen.getByText("Open in Workspaces"));
    expect(handler).toHaveBeenCalled();
    const event = handler.mock.calls[0][0] as CustomEvent;
    expect(event.detail).toMatchObject({ view: "workspaces", workspaceId: 1, taskId: 42 });
    window.removeEventListener("adversaria:open-view", handler as EventListener);
  });
});
