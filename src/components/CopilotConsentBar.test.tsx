import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { CopilotConsentBar } from "./CopilotConsentBar";

describe("CopilotConsentBar", () => {
  it("renders four radios", () => {
    render(<CopilotConsentBar mode="no_ai" hasClaudeKey={true} hasDeepSeekKey={true} onChange={vi.fn()} />);
    expect(screen.getByRole("radio", { name: "No AI" })).toBeInTheDocument();
    expect(screen.getByRole("radio", { name: "AI \u00b7 Local" })).toBeInTheDocument();
    expect(screen.getByRole("radio", { name: "AI \u00b7 Claude" })).toBeInTheDocument();
    expect(screen.getByRole("radio", { name: "AI \u00b7 DeepSeek" })).toBeInTheDocument();
  });
  it("active reflects mode", () => {
    const { rerender } = render(<CopilotConsentBar mode="local" hasClaudeKey={true} onChange={vi.fn()} />);
    expect(screen.getByRole("radio", { name: "AI \u00b7 Local" })).toHaveAttribute("aria-checked", "true");
    rerender(<CopilotConsentBar mode="claude" hasClaudeKey={true} onChange={vi.fn()} />);
    expect(screen.getByRole("radio", { name: "AI \u00b7 Claude" })).toHaveAttribute("aria-checked", "true");
  });
  it("Claude disabled + title when no key", () => {
    render(<CopilotConsentBar mode="no_ai" hasClaudeKey={false} onChange={vi.fn()} />);
    const btn = screen.getByRole("radio", { name: "AI \u00b7 Claude" });
    expect(btn).toBeDisabled();
    expect(btn).toHaveAttribute("title", "Add an Anthropic API key in Settings \u203a Live Copilot");
  });
  it("clicking Local calls onChange", async () => {
    const onChange = vi.fn();
    render(<CopilotConsentBar mode="no_ai" hasClaudeKey={true} onChange={onChange} />);
    await userEvent.setup().click(screen.getByRole("radio", { name: "AI \u00b7 Local" }));
    expect(onChange).toHaveBeenCalledWith("local");
  });
  it("DeepSeek is enabled only with its own saved key", () => {
    const { rerender } = render(
      <CopilotConsentBar mode="no_ai" hasClaudeKey={true} hasDeepSeekKey={false} onChange={vi.fn()} />,
    );
    const button = screen.getByRole("radio", { name: "AI \u00b7 DeepSeek" });
    expect(button).toBeDisabled();
    expect(button).toHaveAttribute("title", "Add a DeepSeek API key in Settings › Live Copilot");
    rerender(<CopilotConsentBar mode="deepseek" hasClaudeKey={true} hasDeepSeekKey={true} onChange={vi.fn()} />);
    expect(screen.getByRole("radio", { name: "AI \u00b7 DeepSeek" })).toHaveAttribute("aria-checked", "true");
  });
  it("each mode shows its exact line", () => {
    const { rerender } = render(<CopilotConsentBar mode="no_ai" hasClaudeKey={true} onChange={vi.fn()} />);
    expect(screen.getByText("No AI \u00b7 passages from your notes only, nothing leaves this Mac")).toBeInTheDocument();
    rerender(<CopilotConsentBar mode="local" hasClaudeKey={true} onChange={vi.fn()} />);
    expect(screen.getByText("Copilot on \u00b7 Local \u00b7 answers from your machine using this folder's sources")).toBeInTheDocument();
    rerender(<CopilotConsentBar mode="claude" hasClaudeKey={true} onChange={vi.fn()} />);
    expect(screen.getByText("Copilot on \u00b7 Claude \u00b7 sends the current question, up to 4 recent turns, up to 3 passages from this folder's sources, this folder's instructions, your folder profile and voice samples; never the full transcript. Also sent: a one-paragraph summary of each project in this folder, and up to three earlier copilot suggestions from this session.")).toBeInTheDocument();
    rerender(<CopilotConsentBar mode="deepseek" hasClaudeKey={true} hasDeepSeekKey={true} onChange={vi.fn()} />);
    expect(screen.getByText("Copilot on \u00b7 DeepSeek \u00b7 sends the current question, up to 4 recent turns, up to 3 passages from this folder's sources, this folder's instructions, your folder profile and voice samples; never the full transcript. Also sent: a one-paragraph summary of each project in this folder, and up to three earlier copilot suggestions from this session.")).toBeInTheDocument();
  });
  it("consent_pack_memory", () => {
    const cloudClaude = render(<CopilotConsentBar mode="claude" hasClaudeKey={true} onChange={vi.fn()} />).container.textContent ?? "";
    expect(cloudClaude).toContain("Also sent: a one-paragraph summary of each project in this folder, and up to three earlier copilot suggestions from this session.");
    const { rerender } = render(<CopilotConsentBar mode="deepseek" hasClaudeKey={true} hasDeepSeekKey={true} onChange={vi.fn()} />);
    expect(rerender).toBeDefined();
    // local and no_ai must NOT contain the pack sentence
    const { container: localC } = render(<CopilotConsentBar mode="local" hasClaudeKey={true} onChange={vi.fn()} />);
    expect(localC.textContent).not.toContain("Also sent: a one-paragraph summary");
    const { container: noAiC } = render(<CopilotConsentBar mode="no_ai" hasClaudeKey={true} onChange={vi.fn()} />);
    expect(noAiC.textContent).not.toContain("Also sent: a one-paragraph summary");
  });
  it("shows second line when no folder and mode not no_ai", () => {
    const { rerender } = render(<CopilotConsentBar mode="claude" hasClaudeKey={true} hasFolder={false} onChange={vi.fn()} />);
    expect(screen.getByText("No folder chosen: only your live notes and attachments are searched.")).toBeInTheDocument();
    rerender(<CopilotConsentBar mode="local" hasClaudeKey={true} hasFolder={false} onChange={vi.fn()} />);
    expect(screen.getByText("No folder chosen: only your live notes and attachments are searched.")).toBeInTheDocument();
    rerender(<CopilotConsentBar mode="no_ai" hasClaudeKey={true} hasFolder={false} onChange={vi.fn()} />);
    expect(screen.queryByText("No folder chosen: only your live notes and attachments are searched.")).not.toBeInTheDocument();
    rerender(<CopilotConsentBar mode="claude" hasClaudeKey={true} hasFolder={true} onChange={vi.fn()} />);
    expect(screen.queryByText("No folder chosen: only your live notes and attachments are searched.")).not.toBeInTheDocument();
  });
});
