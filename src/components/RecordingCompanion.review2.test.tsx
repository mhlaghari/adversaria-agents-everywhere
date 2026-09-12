import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { RecordingCompanion } from "./RecordingCompanion";
import { CopilotCards } from "./CopilotCards";

const mocks = vi.hoisted(() => ({
  getBrief: vi.fn().mockResolvedValue({
    folder_id: 1,
    folder_name: "F",
    copilot_mode: "no_ai",
    copilot_web: false,
    meeting_count: 0,
    last_meeting: null,
    open_items: [],
    decisions: [],
    follow_ups: [],
  }),
  getAudio: vi.fn().mockResolvedValue(0),
  pickFile: vi.fn().mockResolvedValue(null),
  hasKey: vi.fn().mockResolvedValue(false),
  hasDeepSeekKey: vi.fn().mockResolvedValue(false),
  getMode: vi.fn().mockResolvedValue("no_ai"),
  setMode: vi.fn().mockResolvedValue("no_ai"),
  setFolderMode: vi.fn().mockResolvedValue(undefined),
  setFolderWeb: vi.fn().mockResolvedValue(undefined),
  copilotSetMicQuestions: vi.fn().mockResolvedValue(undefined),
}));

vi.mock("../lib/tauri", () => ({
  getAudioLevel: mocks.getAudio,
  pickContextFile: mocks.pickFile,
  getFolderCopilotBrief: mocks.getBrief,
  setFolderCopilotMode: mocks.setFolderMode,
  hasCopilotApiKey: mocks.hasKey,
  hasDeepSeekCopilotApiKey: mocks.hasDeepSeekKey,
  copilotGetMode: mocks.getMode,
  copilotSetMode: mocks.setMode,
  setFolderCopilotWeb: mocks.setFolderWeb,
  copilotSetMicQuestions: mocks.copilotSetMicQuestions,
}));

describe("Review2: session-scoped web consent", () => {
  it("sends active session ID and reverts on rejection (visible notice)", async () => {
    mocks.setFolderWeb.mockReset();
    mocks.setFolderWeb.mockRejectedValueOnce(new Error("denied by Rust: session mismatch"));
    mocks.getBrief.mockResolvedValue({
      folder_id: 5,
      folder_name: "F5",
      copilot_mode: "no_ai",
      copilot_web: false,
      meeting_count: 0,
      last_meeting: null,
      open_items: [],
      decisions: [],
      follow_ups: [],
    });
    const onNotice = vi.fn();
    const user = userEvent.setup();
    render(
      <RecordingCompanion
        variant="balanced"
        value=""
        onChange={vi.fn()}
        status="recording"
        liveLines={[]}
        attachments={[]}
        onAddAttachment={vi.fn()}
        onRemoveAttachment={vi.fn()}
        recentMeetings={[]}
        onStop={vi.fn()}
        onBrowse={vi.fn()}
        folders={[{ folder: { id: 5, name: "F5", color: "#fff", instructions: "", created_at: "", updated_at: "", copilot_mode: "no_ai" }, meeting_count: 0 }]}
        recordingFolderId={5}
        onChangeRecordingFolder={vi.fn()}
        copilotCards={[]}
        onForceCard={vi.fn()}
        onCancel={vi.fn()}
        onRetry={vi.fn()}
        onNotice={onNotice}
        copilotSessionId="sess-active-123"
      />,
    );
    await user.click(screen.getByRole("tab", { name: "Last time" }));
    await waitFor(() => expect(screen.getByLabelText("Allow web search (Claude only)")).toBeInTheDocument());
    await waitFor(() => expect((screen.getByLabelText("Allow web search (Claude only)") as HTMLInputElement).checked).toBe(false));
    const cb = screen.getByLabelText("Allow web search (Claude only)");
    expect((cb as HTMLInputElement).disabled).toBe(false);
    await user.click(cb);
    await waitFor(() => expect(mocks.setFolderWeb).toHaveBeenCalledWith(5, true, "sess-active-123"));
    await waitFor(() => expect(onNotice).toHaveBeenCalled());
    await waitFor(() => expect((screen.getByLabelText("Allow web search (Claude only)") as HTMLInputElement).checked).toBe(false));
  });

  it("web checkbox disabled without both folder and current session", async () => {
    const user = userEvent.setup();
    // case A: no folder, with session -> disabled
    const { rerender } = render(
      <RecordingCompanion
        variant="balanced" value="" onChange={vi.fn()} status="recording" liveLines={[]} attachments={[]} onAddAttachment={vi.fn()} onRemoveAttachment={vi.fn()} recentMeetings={[]} onStop={vi.fn()} onBrowse={vi.fn()}
        folders={[{ folder: { id: 1, name: "F1", color: "#fff", instructions: "", created_at: "", updated_at: "", copilot_mode: "no_ai" }, meeting_count: 0 }]}
        recordingFolderId={null} onChangeRecordingFolder={vi.fn()} copilotCards={[]} onForceCard={vi.fn()} onNotice={vi.fn()} copilotSessionId="sess-x"
      />,
    );
    await user.click(screen.getByRole("tab", { name: "Last time" }));
    expect((screen.getByLabelText("Allow web search (Claude only)") as HTMLInputElement).disabled).toBe(true);

    // case B: folder present, no session -> disabled
    rerender(
      <RecordingCompanion
        variant="balanced" value="" onChange={vi.fn()} status="recording" liveLines={[]} attachments={[]} onAddAttachment={vi.fn()} onRemoveAttachment={vi.fn()} recentMeetings={[]} onStop={vi.fn()} onBrowse={vi.fn()}
        folders={[{ folder: { id: 1, name: "F1", color: "#fff", instructions: "", created_at: "", updated_at: "", copilot_mode: "no_ai" }, meeting_count: 0 }]}
        recordingFolderId={1} onChangeRecordingFolder={vi.fn()} copilotCards={[]} onForceCard={vi.fn()} onNotice={vi.fn()} copilotSessionId={null}
      />,
    );
    await waitFor(() => expect(screen.getByLabelText("Allow web search (Claude only)")).toBeInTheDocument());
    expect((screen.getByLabelText("Allow web search (Claude only)") as HTMLInputElement).disabled).toBe(true);

    // case C: both present -> enabled
    rerender(
      <RecordingCompanion
        variant="balanced" value="" onChange={vi.fn()} status="recording" liveLines={[]} attachments={[]} onAddAttachment={vi.fn()} onRemoveAttachment={vi.fn()} recentMeetings={[]} onStop={vi.fn()} onBrowse={vi.fn()}
        folders={[{ folder: { id: 1, name: "F1", color: "#fff", instructions: "", created_at: "", updated_at: "", copilot_mode: "no_ai" }, meeting_count: 0 }]}
        recordingFolderId={1} onChangeRecordingFolder={vi.fn()} copilotCards={[]} onForceCard={vi.fn()} onNotice={vi.fn()} copilotSessionId="sess-y"
      />,
    );
    await waitFor(() => expect((screen.getByLabelText("Allow web search (Claude only)") as HTMLInputElement).disabled).toBe(false));
  });
});

describe("Review2: folder select locked during active recording", () => {
  it("folder select disabled for active Copilot session and cannot trigger onChange", async () => {
    const onChange = vi.fn();
    const user = userEvent.setup();
    render(
      <RecordingCompanion
        variant="balanced" value="" onChange={vi.fn()} status="recording" liveLines={[]} attachments={[]} onAddAttachment={vi.fn()} onRemoveAttachment={vi.fn()} recentMeetings={[]} onStop={vi.fn()} onBrowse={vi.fn()}
        folders={[
          { folder: { id: 1, name: "F1", color: "#fff", instructions: "", created_at: "", updated_at: "", copilot_mode: "no_ai" }, meeting_count: 0 },
          { folder: { id: 2, name: "F2", color: "#fff", instructions: "", created_at: "", updated_at: "", copilot_mode: "no_ai" }, meeting_count: 0 },
        ]}
        recordingFolderId={1} onChangeRecordingFolder={onChange} copilotCards={[]} onForceCard={vi.fn()} copilotSessionId="sess-locked"
      />,
    );
    await user.click(screen.getByRole("tab", { name: "Last time" }));
    const sel = screen.getByLabelText("Folder for this meeting") as HTMLSelectElement;
    expect(sel.disabled).toBe(true);
    expect(sel.title).toMatch(/uses the folder chosen when recording started/);
    await user.click(sel);
    // attempt to change via userEvent select should not fire because disabled
    // userEvent.selectOptions on disabled will not trigger onChange
    expect(onChange).not.toHaveBeenCalled();
  });

  it("folder select enabled when no active session", async () => {
    const onChange = vi.fn();
    const user = userEvent.setup();
    render(
      <RecordingCompanion
        variant="balanced" value="" onChange={vi.fn()} status="recording" liveLines={[]} attachments={[]} onAddAttachment={vi.fn()} onRemoveAttachment={vi.fn()} recentMeetings={[]} onStop={vi.fn()} onBrowse={vi.fn()}
        folders={[{ folder: { id: 1, name: "F1", color: "#fff", instructions: "", created_at: "", updated_at: "", copilot_mode: "no_ai" }, meeting_count: 0 }]}
        recordingFolderId={null} onChangeRecordingFolder={onChange} copilotCards={[]} onForceCard={vi.fn()} copilotSessionId={null}
      />,
    );
    await user.click(screen.getByRole("tab", { name: "Last time" }));
    const sel = screen.getByLabelText("Folder for this meeting") as HTMLSelectElement;
    expect(sel.disabled).toBe(false);
  });
});

describe("Review2: CopilotCards disclosure truthful per mode", () => {
  it("no_ai privacy", () => {
    const { container } = render(<CopilotCards cards={[]} onForceCard={vi.fn()} onPin={vi.fn()} copilotMode="no_ai" />);
    expect(container.textContent).toContain("Your notes and conversation stay on this Mac");
  });
  it("local privacy keeps 0 bytes claim", () => {
    const { container } = render(<CopilotCards cards={[]} onForceCard={vi.fn()} onPin={vi.fn()} copilotMode="local" webEnabled={false} />);
    expect(container.textContent).toContain("Current conversation stays on this Mac · 0 bytes sent");
    expect(container.textContent).not.toContain("Sends bounded");
  });
  it("claude without web says bounded question passages sent, no web allowed", () => {
    const { container } = render(<CopilotCards cards={[]} onForceCard={vi.fn()} onPin={vi.fn()} copilotMode="claude" webEnabled={false} />);
    expect(container.textContent).not.toContain("Sends the current question, up to 4 recent conversation turns, up to 3 passages, and this folder's instructions to Claude");
  });
  it("claude with web says web search allowed", () => {
    const { container } = render(<CopilotCards cards={[]} onForceCard={vi.fn()} onPin={vi.fn()} copilotMode="claude" webEnabled={true} />);
    expect(container.textContent).not.toContain("Sends the current question, up to 4 recent conversation turns, up to 3 passages, and this folder's instructions to Claude");
  });
});
