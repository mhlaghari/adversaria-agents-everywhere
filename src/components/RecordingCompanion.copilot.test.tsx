import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { RecordingCompanion } from "./RecordingCompanion";

const mocks = vi.hoisted(() => ({
  copilotGetMode: vi.fn().mockResolvedValue("no_ai"),
  copilotSetMode: vi.fn().mockResolvedValue(undefined),
  hasCopilotApiKey: vi.fn().mockResolvedValue(true),
  hasDeepSeekCopilotApiKey: vi.fn().mockResolvedValue(true),
  getFolderCopilotBrief: vi.fn().mockResolvedValue({ folder_id: 3, folder_name: "F", copilot_mode: "no_ai", copilot_web: false, meeting_count: 0, last_meeting: null, open_items: [], decisions: [], follow_ups: [] }),
  setFolderCopilotMode: vi.fn().mockResolvedValue(undefined),
  copilotSetMicQuestions: vi.fn().mockResolvedValue(undefined),
}));

vi.mock("../lib/tauri", () => ({
  getAudioLevel: vi.fn().mockResolvedValue(0),
  pickContextFile: vi.fn().mockResolvedValue(null),
  getFolderCopilotBrief: mocks.getFolderCopilotBrief,
  setFolderCopilotMode: mocks.setFolderCopilotMode,
  copilotGetMode: mocks.copilotGetMode,
  copilotSetMode: mocks.copilotSetMode,
  hasCopilotApiKey: mocks.hasCopilotApiKey,
  hasDeepSeekCopilotApiKey: mocks.hasDeepSeekCopilotApiKey,
  copilotSetMicQuestions: mocks.copilotSetMicQuestions,
}));

const props = {
  variant: "balanced", value: "", onChange: vi.fn(), status: "idle" as const, liveLines: [], attachments: [], onAddAttachment: vi.fn(), onRemoveAttachment: vi.fn(), recentMeetings: [], onStop: vi.fn(), onBrowse: vi.fn(),
  folders: [{ folder: { id: 3, name: "F", color: "#fff", instructions: "", created_at: "", updated_at: "", copilot_mode: "no_ai" as const }, meeting_count: 1 }],
  recordingFolderId: 3, onChangeRecordingFolder: vi.fn(), copilotCards: [], onForceCard: vi.fn(),
};

describe("RecordingCompanion copilot", () => {
  it("consent bar visible on Copilot tab", async () => {
    render(<RecordingCompanion {...props} />);
    await userEvent.setup().click(screen.getByRole("tab", { name: /Copilot/ }));
    expect(screen.getByRole("radiogroup")).toBeInTheDocument();
  });
  it("changing mode calls copilotSetMode and setFolderCopilotMode", async () => {
    render(<RecordingCompanion {...props} />);
    await userEvent.setup().click(screen.getByRole("tab", { name: /Copilot/ }));
    await userEvent.setup().click(screen.getByRole("radio", { name: "AI \u00b7 Local" }));
    expect(mocks.copilotSetMode).toHaveBeenCalledWith("local");
    expect(mocks.setFolderCopilotMode).toHaveBeenCalledWith(3, "local");
  });
});
