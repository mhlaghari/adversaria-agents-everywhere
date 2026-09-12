import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { RecordingCompanion } from "./RecordingCompanion";
import type { Commitment } from "../types";

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
  setFolderCopilotWeb: vi.fn().mockResolvedValue(undefined),
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

const caught: Commitment = {
  session_id: "sess-1",
  id: 7,
  text: "I'll send the deck to Naema by Friday",
  owner: "Naema",
  deadline: "by Friday",
  source: "Me",
  at_ms: 1000,
  state: "caught",
  capability: "write",
  task_id: null,
  run_queued: false,
  agents_paused: false,
};

const originalWidth = window.innerWidth;
function setWidth(px: number): void {
  Object.defineProperty(window, "innerWidth", { configurable: true, writable: true, value: px });
}

async function emitCaught(): Promise<void> {
  await waitFor(() => expect(listenHandlers["copilot-commitment"]).toBeDefined());
  listenHandlers["copilot-commitment"]({ payload: caught });
}

describe("RecordingCompanion layout by viewport width", () => {
  beforeEach(() => {
    for (const k of Object.keys(listenHandlers)) delete listenHandlers[k];
  });
  afterEach(() => setWidth(originalWidth));

  it("renders the compact layout below 900px: no tabs, status button, notes footer, answers always present", () => {
    setWidth(899);
    const { container } = render(<RecordingCompanion {...baseProps} />);
    expect(container.querySelector(".companion-layout")).toHaveAttribute("data-layout", "compact");
    expect(screen.queryByRole("tablist")).not.toBeInTheDocument();
    expect(screen.getByRole("button", { name: /· Tools$/ })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Answer current question" })).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/Jot a note/)).toBeInTheDocument();
    expect(screen.getByText("LIVE TRANSCRIPT")).toBeInTheDocument();
  });

  it("renders the balanced layout at 900px and above, honouring the configured variant", () => {
    setWidth(900);
    const { container } = render(<RecordingCompanion {...baseProps} />);
    expect(container.querySelector(".companion-layout")).toHaveAttribute("data-layout", "balanced");
    expect(screen.getByRole("tablist")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /· Tools$/ })).not.toBeInTheDocument();
  });

  it("compact: the Tools sheet opens in the answers area and Close returns focus to the status button", async () => {
    setWidth(520);
    const user = userEvent.setup();
    render(<RecordingCompanion {...baseProps} />);
    const tools = screen.getByRole("button", { name: /· Tools$/ });
    await user.click(tools);
    const sheet = screen.getByRole("region", { name: "Meeting tools" });
    expect(within(sheet).getByLabelText("Questions can come from my mic")).toBeInTheDocument();
    expect(within(sheet).getByLabelText("Folder for this meeting")).toBeInTheDocument();
    expect(within(sheet).getByRole("radiogroup", { name: "Copilot mode" })).toBeInTheDocument();
    await user.click(within(sheet).getByRole("button", { name: "Close tools" }));
    expect(screen.queryByRole("region", { name: "Meeting tools" })).not.toBeInTheDocument();
    await waitFor(() => expect(tools).toHaveFocus());
  });

  it("balanced: a caught commitment is pinned in CAUGHT while the Notes tab is active", async () => {
    setWidth(1024);
    render(<RecordingCompanion {...baseProps} />);
    expect(screen.getByRole("tab", { name: "Notes" })).toHaveAttribute("aria-selected", "true");
    await emitCaught();
    const area = await screen.findByRole("region", { name: "Caught commitments" });
    expect(area).not.toHaveAttribute("hidden");
    expect(within(area).getByTestId("commitment-card-7")).toBeInTheDocument();
    expect(within(area).getByRole("button", { name: "Approve" })).toBeInTheDocument();
    // Notes is still the active tab with its textarea showing.
    expect(screen.getByRole("tab", { name: "Notes" })).toHaveAttribute("aria-selected", "true");
    expect(screen.getByPlaceholderText(/key decision/)).toBeInTheDocument();
    expect(screen.getByRole("status")).toHaveTextContent("Commitment needs your approval");
  });

  it("compact: a caught commitment is pinned in CAUGHT above the answers", async () => {
    setWidth(380);
    const { container } = render(<RecordingCompanion {...baseProps} />);
    await emitCaught();
    const area = await screen.findByRole("region", { name: "Caught commitments" });
    expect(within(area).getByTestId("commitment-card-7")).toBeInTheDocument();
    expect(within(area).getByRole("button", { name: "Approve" })).toBeInTheDocument();
    const right = container.querySelector(".companion-right")!;
    const order = Array.from(right.children).map((el) => el.className.split(" ")[0]);
    expect(order).toEqual(["companion-caught", "companion-answers"]);
  });
});
