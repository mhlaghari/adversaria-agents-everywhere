import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

vi.mock("../lib/tauri", () => ({
  copilotSetMicQuestions: vi.fn().mockResolvedValue(undefined),
}));

import { CopilotCards } from "./CopilotCards";
import type { CopilotCard } from "../types";

function cardFixture(overrides: Partial<CopilotCard> = {}): CopilotCard {
  return {
    id: 1,
    session_id: "sess-1",
    status: "answering",
    provider_frozen: "claude",
    question: "What did we decide about the API?",
    asked_at_ms: new Date("2026-09-02T10:05:30Z").getTime(),
    trigger: "auto",
    passages: [
      {
        source_kind: "meeting",
        source_id: "42",
        title: "Northstar kickoff",
        text: "We decided to use GraphQL for the new API.",
        score: 0.9,
      },
    ],
    retrieval_ms: 87,
    ...overrides,
  };
}

describe("CopilotCards", () => {
  it("renders newest first and keeps source passages collapsed until requested", async () => {
    const older = cardFixture({ id: 1, question: "Older question?" });
    const newer = cardFixture({ id: 2, question: "Newer question?" });
    // pass newest first per contract
    render(<CopilotCards cards={[newer, older]} onForceCard={vi.fn()} onPin={vi.fn()} />);

    const questions = screen.getAllByText(/question\?/);
    expect(questions[0].textContent).toBe("Newer question?");
    expect(questions[1].textContent).toBe("Older question?");
    expect(screen.queryByText("Northstar kickoff")).not.toBeInTheDocument();
    const sourceButtons = screen.getAllByRole("button", { name: "Sources · 1" });
    const user = userEvent.setup();
    await user.click(sourceButtons[0]);
    await user.click(sourceButtons[1]);
    expect(screen.getAllByText("Northstar kickoff").length).toBe(2);
    expect(screen.getAllByText("We decided to use GraphQL for the new API.").length).toBe(2);
    // time shown (mm:ss) — use regex for any valid time
    expect(screen.getAllByText(/\d{2}:\d{2}/).length).toBeGreaterThan(0);
    // source chip title attr = source_id
    const chip = screen.getAllByText("Northstar kickoff")[0];
    expect(chip).toHaveAttribute("title", "42");
    // retrieval ms
    expect(screen.getAllByText("87 ms").length).toBe(2);
  });

  it("empty passages with done status shows nothing-in-your-notes copy", () => {
    const card = cardFixture({ passages: [], status: "done" });
    render(<CopilotCards cards={[card]} onForceCard={vi.fn()} onPin={vi.fn()} />);
    expect(screen.getByText("No matching notes")).toBeInTheDocument();
  });

  it("heard with empty passages does NOT show nothing-in-your-notes", () => {
    const card = cardFixture({ passages: [], status: "heard" });
    render(<CopilotCards cards={[card]} onForceCard={vi.fn()} onPin={vi.fn()} />);
    expect(screen.queryByText("No matching notes")).not.toBeInTheDocument();
    expect(screen.getByText("Heard the complete question")).toBeInTheDocument();
  });

  it("no cards shows empty state", () => {
    render(<CopilotCards cards={[]} onForceCard={vi.fn()} onPin={vi.fn()} />);
    expect(screen.getByText("Questions from the other side will appear here as short, live answers.")).toBeInTheDocument();
  });

  it("Pin to notes calls onPin with the card", async () => {
    const onPin = vi.fn();
    const card = cardFixture();
    const user = userEvent.setup();
    render(<CopilotCards cards={[card]} onForceCard={vi.fn()} onPin={onPin} />);
    await user.click(screen.getByRole("button", { name: "Pin card 1 to notes" }));
    expect(onPin).toHaveBeenCalledWith(card);
  });

  it("Pin disabled when no passage or answer", () => {
    const card = cardFixture({ passages: [], status: "heard" });
    render(<CopilotCards cards={[card]} onForceCard={vi.fn()} onPin={vi.fn()} />);
    expect(screen.getByRole("button", { name: "Pin card 1 to notes" })).toBeDisabled();
  });

  it("force button calls onForceCard with false by default", async () => {
    const onForceCard = vi.fn();
    const user = userEvent.setup();
    render(<CopilotCards cards={[]} onForceCard={onForceCard} onPin={vi.fn()} />);
    await user.click(screen.getByRole("button", { name: "Answer current question" }));
    expect(onForceCard).toHaveBeenCalledWith(false);
  });

  it("Me fallback checkbox true passes true", async () => {
    const onForceCard = vi.fn();
    const user = userEvent.setup();
    render(<CopilotCards cards={[]} onForceCard={onForceCard} onPin={vi.fn()} />);
    await user.click(screen.getByLabelText("Questions can come from my mic"));
    await user.click(screen.getByRole("button", { name: "Answer current question" }));
    expect(onForceCard).toHaveBeenCalledWith(true);
  });

  it("manual card shows the chip", () => {
    const card = cardFixture({ trigger: "manual" });
    render(<CopilotCards cards={[card]} onForceCard={vi.fn()} onPin={vi.fn()} />);
    expect(screen.getByText("manual")).toBeInTheDocument();
  });

  it("shows the provider frozen onto an older card after the mode changes", () => {
    const card = cardFixture({
      status: "done",
      provider_frozen: "no_ai",
      passages: [],
    });
    render(
      <CopilotCards
        cards={[card]}
        onForceCard={vi.fn()}
        onPin={vi.fn()}
        copilotMode="deepseek"
      />,
    );
    expect(screen.getByText("No AI", { selector: ".copilot-provider-chip" })).toBeInTheDocument();
    expect(screen.getByText("Done · No AI · passages only")).toBeInTheDocument();
  });

  it("auto card does not show manual chip", () => {
    const card = cardFixture({ trigger: "auto" });
    render(<CopilotCards cards={[card]} onForceCard={vi.fn()} onPin={vi.fn()} />);
    expect(screen.queryByText("manual")).not.toBeInTheDocument();
  });

  it("maps notes source_kind to Your notes label", async () => {
    const card = cardFixture({
      passages: [
        { source_kind: "notes", source_id: "notes", title: "Notes", text: "my notes passage", score: 0.8 },
      ],
    });
    render(<CopilotCards cards={[card]} onForceCard={vi.fn()} onPin={vi.fn()} />);
    await userEvent.setup().click(screen.getByRole("button", { name: "Sources · 1" }));
    expect(screen.getByText("Your notes")).toBeInTheDocument();
  });

  it("renders privacy line", () => {
    render(<CopilotCards cards={[]} onForceCard={vi.fn()} onPin={vi.fn()} />);
    expect(screen.getByText("Your notes and conversation stay on this Mac")).toBeInTheDocument();
  });

  it("discloses the exact recent dialogue and assembled current turn", async () => {
    const card = cardFixture({
      question: "What risks would that introduce?",
      question_source: "Them",
      context_turns: [
        "Them: We may temporarily connect the local model.",
        "Me: The connection is only for research.",
      ],
    });
    render(<CopilotCards cards={[card]} onForceCard={vi.fn()} onPin={vi.fn()} />);
    expect(screen.queryByText("The connection is only for research.")).not.toBeInTheDocument();
    await userEvent.setup().click(screen.getByRole("button", { name: "Context · 3 turns" }));
    expect(screen.getByText("Conversation used for this answer")).toBeInTheDocument();
    expect(screen.getByText("The connection is only for research.")).toBeInTheDocument();
    expect(screen.getAllByText("Them")).toHaveLength(2);
    expect(screen.getByText("Me")).toBeInTheDocument();
  });

  it("newest card gets copilot-card--new class", () => {
    const older = cardFixture({ id: 1 });
    const newer = cardFixture({ id: 2 });
    const { container } = render(<CopilotCards cards={[newer, older]} onForceCard={vi.fn()} onPin={vi.fn()} />);
    const cards = container.querySelectorAll(".copilot-card");
    expect(cards[0]).toHaveClass("copilot-card--new");
    expect(cards[1]).not.toHaveClass("copilot-card--new");
  });

  it("shows Cancel when answering streaming", () => {
    const card = cardFixture({ answer: { provider: "claude", status: "streaming", text: "hi", citations: [] } });
    render(<CopilotCards cards={[card]} onForceCard={vi.fn()} onPin={vi.fn()} onCancel={vi.fn()} />);
    expect(screen.getByRole("button", { name: "Cancel" })).toBeInTheDocument();
  });

  it("shows Retry for error", () => {
    const card = cardFixture({ answer: { provider: "claude", status: "error", text: "", citations: [], error: "boom" } });
    render(<CopilotCards cards={[card]} onForceCard={vi.fn()} onPin={vi.fn()} onRetry={vi.fn()} copilotMode="claude" />);
    expect(screen.getByRole("button", { name: "Retry" })).toBeInTheDocument();
  });

  it("shows Retry for cancelled", () => {
    const card = cardFixture({ answer: { provider: "claude", status: "cancelled", text: "", citations: [], reason: "user" } });
    render(<CopilotCards cards={[card]} onForceCard={vi.fn()} onPin={vi.fn()} onRetry={vi.fn()} copilotMode="claude" />);
    expect(screen.getByRole("button", { name: "Retry" })).toBeInTheDocument();
  });

  it("only offers Retry while the frozen provider and web consent still match", () => {
    const card = cardFixture({
      answer: {
        provider: "claude",
        status: "error",
        text: "",
        citations: [],
        error: "boom",
        web_requested: true,
      },
    });
    const props = { cards: [card], onForceCard: vi.fn(), onPin: vi.fn(), onRetry: vi.fn() };
    const { rerender } = render(<CopilotCards {...props} copilotMode="no_ai" webEnabled />);
    expect(screen.queryByRole("button", { name: "Retry" })).not.toBeInTheDocument();
    rerender(<CopilotCards {...props} copilotMode="claude" webEnabled={false} />);
    expect(screen.queryByRole("button", { name: "Retry" })).not.toBeInTheDocument();
    rerender(<CopilotCards {...props} copilotMode="claude" webEnabled />);
    expect(screen.getByRole("button", { name: "Retry" })).toBeInTheDocument();
  });

  it("skipped shows correct copy", () => {
    const card = cardFixture({ status: "skipped", reason: "superseded" });
    render(<CopilotCards cards={[card]} onForceCard={vi.fn()} onPin={vi.fn()} />);
    expect(screen.getByText("Skipped, newer question arrived")).toBeInTheDocument();
  });

  it("egress bytes copy for local and claude", () => {
    const local = cardFixture({ answer: { provider: "local", status: "done", text: "", citations: [], provenance: [{ text: "b", label: "model" }], egress_bytes: 0 } });
    const { rerender } = render(<CopilotCards cards={[local]} onForceCard={vi.fn()} onPin={vi.fn()} />);
    expect(screen.getByText("0 bytes left this Mac")).toBeInTheDocument();
    const claude = cardFixture({ answer: { provider: "claude", status: "done", text: "", citations: [], provenance: [{ text: "b", label: "model" }], egress_bytes: 512 } });
    rerender(<CopilotCards cards={[claude]} onForceCard={vi.fn()} onPin={vi.fn()} />);
    expect(screen.getByText("Prepared request payload: 512 bytes")).toBeInTheDocument();
  });

  it("toggling mic checkbox calls copilotSetMicQuestions with true", async () => {
    const { copilotSetMicQuestions } = await import("../lib/tauri");
    const mocked = vi.mocked(copilotSetMicQuestions);
    mocked.mockClear();
    const user = userEvent.setup();
    render(<CopilotCards cards={[]} onForceCard={vi.fn()} onPin={vi.fn()} />);
    await user.click(screen.getByLabelText("Questions can come from my mic"));
    expect(mocked).toHaveBeenCalledWith(true);
  });

  it("say_90_words", async () => {
    const sentences = [
      "First we clarified the requirements by asking what the user really needs and where the data lives.",
      "Then we built a small prototype that streams the audio locally and only sends the question when needed.",
      "Next we added a folder index that extracts one paragraph per project and keeps the pack under six thousand bytes.",
      "We also stored the last three copilot suggestions in this session so follow up questions can be resolved correctly.",
      "Finally we measured the tradeoff between latency and accuracy and chose the faster model for live answers.",
    ];
    const wordCount = sentences.join(" ").split(/\s+/).filter(Boolean).length;
    expect(wordCount).toBeGreaterThanOrEqual(85);
    expect(wordCount).toBeLessThanOrEqual(95);
    const card = cardFixture({
      id: 99,
      passages: [{ source_kind: "meeting", source_id: "1", title: "M", text: "p", score: 1 }],
      answer: {
        provider: "claude",
        status: "done",
        text: sentences.join(" "),
        citations: [],
        sections: { say: sentences, specifics: [], notes: [], next: null },
      },
    });
    const onPin = vi.fn();
    const { container } = render(<CopilotCards cards={[card]} onForceCard={vi.fn()} onPin={onPin} />);
    const spans = container.querySelectorAll(".copilot-say-sentence");
    expect(spans).toHaveLength(5);
    for (const s of sentences) {
      expect(screen.getByText(s)).toBeInTheDocument();
    }
    // verify Pin contains all sentences
    await userEvent.setup().click(screen.getByRole("button", { name: "Pin card 99 to notes" }));
    expect(onPin).toHaveBeenCalled();
    // Exercise the RecordingCompanion pin path: simulate what onPin would do via container check
    // Directly check that rendered say text includes all sentences (wraps without layout change)
    const sayEl = container.querySelector(".copilot-say");
    expect(sayEl).not.toBeNull();
    for (const s of sentences) {
      expect(sayEl?.textContent).toContain(s);
    }
    // Additionally, exercise Pin via CopilotCards onPin -> simulate pin text contains sentences
    // The parent (RecordingCompanion) joins say sentences; we verify onPin received card with all sentences
    const pinnedCard = onPin.mock.calls[0][0] as import("../types").CopilotCard;
    expect(pinnedCard.answer?.sections?.say).toEqual(sentences);
  });
});
