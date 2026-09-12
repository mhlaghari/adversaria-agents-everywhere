import { render, screen, waitFor } from "@testing-library/react";
import { mockIPC } from "@tauri-apps/api/mocks";
import { describe, expect, it, vi } from "vitest";
import type { WorkspaceDetail, WorkspaceEngine } from "../../types";
import { WorkspacesView } from "../WorkspacesView";
import userEvent from "@testing-library/user-event";

const engines: WorkspaceEngine[] = [
  { id: "local", label: "Local model", available: true, version: "", detail: "" },
];

const summary = {
  workspace: { id: 4, name: "Live meetings", engine: "local", model: "", network_allowed: false, instructions: "", color: "blue", created_at: "2026-08-17T10:00:00Z", updated_at: "2026-08-17T10:00:00Z" },
  queued_task_count: 1, needs_you_count: 0, running_task_count: 0, awaiting_review_count: 0, approved_task_count: 0, total_task_count: 1, meeting_count: 0, folder_count: 0,
};

function detailWith(tasks: WorkspaceDetail["tasks"]): WorkspaceDetail {
  return {
    workspace: summary.workspace,
    context_items: [],
    addons: [],
    tasks,
    artifacts: [],
  };
}

describe("workspaces_live_chip", () => {
  it("shows when and that a task was caught live", async () => {
    const liveDetail = detailWith([
      {
        id: 42,
        workspace_id: 4,
        title: "I'll send the numbers to Wael by Monday",
        details: "Caught live during the meeting at 10:30 from Me.\nOwner: Wael. Deadline: by Monday.\nSession: sess-1",
        capability: "write",
        status: "queued",
        source_meeting_id: null,
        source_meeting_title: "",
        action_item_id: null,
        attempt: 1,
        rejection_notes: [],
        agent_eligible: true,
        created_at: "2026-08-18T10:00:00Z",
        updated_at: "2026-08-18T10:00:00Z",
      },
    ]);
    const normalDetail = detailWith([
      {
        id: 43,
        workspace_id: 4,
        title: "Normal task",
        details: "Regular details",
        capability: "write",
        status: "queued",
        source_meeting_id: null,
        source_meeting_title: "",
        action_item_id: null,
        attempt: 1,
        rejection_notes: [],
        agent_eligible: true,
        created_at: "2026-08-18T10:00:00Z",
        updated_at: "2026-08-18T10:00:00Z",
      },
    ]);
    // First test live chip present
    mockIPC((command) => {
      if (command === "list_workspaces") return [summary];
      if (command === "get_workspace") return liveDetail;
      if (command === "list_workspace_addons") return [];
      if (command === "detect_workspace_engines") return engines;
      if (command === "get_agents_paused") return false;
      if (command === "get_latest_workspace_run") return null;
      if (command === "plugin:event|listen") return null;
      return null;
    });
    const user = userEvent.setup();
    const { unmount } = render(<WorkspacesView onOpenMeeting={vi.fn()} />);
    await user.click(await screen.findByText("Live meetings"));
    await user.click(await screen.findByRole("button", { name: "I'll send the numbers to Wael by Monday details" }));
    expect(await screen.findByText("live · 10:30")).toBeInTheDocument();
    unmount();

    // Second: normal task should not have Live chip
    mockIPC((command) => {
      if (command === "list_workspaces") return [summary];
      if (command === "get_workspace") return normalDetail;
      if (command === "list_workspace_addons") return [];
      if (command === "detect_workspace_engines") return engines;
      if (command === "get_agents_paused") return false;
      if (command === "get_latest_workspace_run") return null;
      if (command === "plugin:event|listen") return null;
      return null;
    });
    render(<WorkspacesView onOpenMeeting={vi.fn()} />);
    await user.click(await screen.findByText("Live meetings"));
    await user.click(await screen.findByRole("button", { name: "Normal task details" }));
    await waitFor(() => expect(screen.getByText("Normal task")).toBeInTheDocument());
    expect(screen.queryByText(/^live · /)).not.toBeInTheDocument();
  });
});
