import { render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi, beforeEach } from "vitest";
import { RecordingCompanion } from "./RecordingCompanion";
import type { Commitment } from "../types";

// Mock @tauri-apps/api/event listen to capture copilot-commitment handlers
const listenHandlers: Record<string, (event: { payload: unknown }) => void> = {};
vi.mock("@tauri-apps/api/event", () => ({
  listen: vi.fn((eventName: string, handler: (e: { payload: unknown }) => void) => {
    listenHandlers[eventName] = handler;
    return Promise.resolve(() => {
      delete listenHandlers[eventName];
    });
  }),
}));

vi.mock("../lib/tauri", () => ({
  getAudioLevel: vi.fn().mockResolvedValue(0),
  pickContextFile: vi.fn().mockResolvedValue(null),
  getFolderCopilotBrief: vi.fn().mockResolvedValue({ folder_id: 3, folder_name: "F", copilot_mode: "no_ai", copilot_web: false, meeting_count: 0, last_meeting: null, open_items: [], decisions: [], follow_ups: [] }),
  setFolderCopilotMode: vi.fn().mockResolvedValue(undefined),
  copilotGetMode: vi.fn().mockResolvedValue("no_ai"),
  copilotSetMode: vi.fn().mockResolvedValue("no_ai"),
  hasCopilotApiKey: vi.fn().mockResolvedValue(true),
  hasDeepSeekCopilotApiKey: vi.fn().mockResolvedValue(true),
  copilotSetMicQuestions: vi.fn().mockResolvedValue(undefined),
  commitmentApprove: vi.fn().mockResolvedValue({ task: { id: 42 }, run_queued: true, agents_paused: false }),
  commitmentDismiss: vi.fn().mockResolvedValue(undefined),
  copilotFolderReadiness: vi.fn().mockResolvedValue({ session_id: "sess-1", folder_id: 3, status: "ready", count: 1, pack_projects: 1, pack_chars: 100, pack_hash: "h", error: null }),
}));

const baseProps = {
  variant: "balanced",
  value: "",
  onChange: vi.fn(),
  status: "recording" as const,
  liveLines: [],
  attachments: [],
  onAddAttachment: vi.fn(),
  onRemoveAttachment: vi.fn(),
  recentMeetings: [],
  onStop: vi.fn(),
  onBrowse: vi.fn(),
  folders: [{ folder: { id: 3, name: "F", color: "#fff", instructions: "", created_at: "", updated_at: "", copilot_mode: "no_ai" as const }, meeting_count: 1 }],
  recordingFolderId: 3,
  onChangeRecordingFolder: vi.fn(),
  copilotCards: [],
  onForceCard: vi.fn(),
  copilotSessionId: "sess-1",
};

function emitCommitment(c: Commitment) {
  const h = listenHandlers["copilot-commitment"];
  if (h) h({ payload: c });
}

describe("RecordingCompanion commitment state", () => {
  beforeEach(() => {
    for (const k of Object.keys(listenHandlers)) delete listenHandlers[k];
  });

  it("stale session id event is ignored", async () => {
    render(<RecordingCompanion {...baseProps} />);
    // wait for listen to register
    await waitFor(() => expect(listenHandlers["copilot-commitment"]).toBeDefined());
    // Show copilot tab to make cards visible
    const copilotTab = screen.getByRole("tab", { name: /Copilot/ });
    // click to open copilot panel
    copilotTab.click();
    const stale: Commitment = {
      session_id: "sess-other",
      id: 99,
      text: "I'll send the deck to Naema",
      owner: "Naema",
      deadline: null,
      source: "Me",
      at_ms: 1000,
      state: "caught",
        capability: "write",
      task_id: null,
      run_queued: false,
      agents_paused: false,
    };
    emitCommitment(stale);
    // give effect time
    await new Promise((r) => setTimeout(r, 50));
    expect(screen.queryByText("I'll send the deck to Naema")).not.toBeInTheDocument();
  });

  it("caught commitment for current session renders newest first above copilot cards", async () => {
    render(<RecordingCompanion {...baseProps} />);
    await waitFor(() => expect(listenHandlers["copilot-commitment"]).toBeDefined());
    screen.getByRole("tab", { name: /Copilot/ }).click();
    const c1: Commitment = {
      session_id: "sess-1",
      id: 1,
      text: "I'll send the numbers to Wael by Monday",
      owner: "Wael",
      deadline: "by Monday",
      source: "Me",
      at_ms: 1000,
      state: "caught",
        capability: "write",
      task_id: null,
      run_queued: false,
      agents_paused: false,
    };
    const c2: Commitment = {
      session_id: "sess-1",
      id: 2,
      text: "let's get the deck to Naema",
      owner: "Naema",
      deadline: null,
      source: "Them",
      at_ms: 2000,
      state: "caught",
        capability: "write",
      task_id: null,
      run_queued: false,
      agents_paused: false,
    };
    emitCommitment(c1);
    emitCommitment(c2);
    await waitFor(() => expect(screen.getByText("let's get the deck to Naema")).toBeInTheDocument());
    expect(screen.getByText("I'll send the numbers to Wael by Monday")).toBeInTheDocument();
    const cards = screen.getAllByTestId(/commitment-card-/);
    // newest first => id 2 before id 1
    expect(cards[0].getAttribute("data-testid")).toBe("commitment-card-2");
    expect(cards[1].getAttribute("data-testid")).toBe("commitment-card-1");
  });
});
