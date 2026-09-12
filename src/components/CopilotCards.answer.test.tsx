import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

vi.mock("../lib/tauri", () => ({
  copilotSetMicQuestions: vi.fn().mockResolvedValue(undefined),
}));

import { CopilotCards } from "./CopilotCards";
import type { CopilotCard } from "../types";

function baseCard(overrides: Partial<CopilotCard> = {}): CopilotCard {
  return {
    id: 1,
    session_id: "sess-1",
    status: "answering",
    provider_frozen: "claude",
    question: "Q?",
    asked_at_ms: 65_000,
    trigger: "auto",
    passages: [{ source_kind: "meeting", source_id: "1", title: "M", text: "passage", score: 1 }],
    retrieval_ms: 10,
    ...overrides,
  };
}

describe("CopilotCards answer", () => {
  it("streaming shows text + cursor", () => {
    const card = baseCard({ answer: { provider: "claude", status: "streaming", text: "- hello world", citations: [] } });
    const { container } = render(<CopilotCards cards={[card]} onForceCard={vi.fn()} onPin={vi.fn()} />);
    expect(container.textContent).toContain("hello world");
    expect(container.querySelector(".copilot-answer-cursor")).not.toBeNull();
  });
  it("searching shows line", () => {
    const card = baseCard({ answer: { provider: "claude", status: "searching", text: "", citations: [] } });
    render(<CopilotCards cards={[card]} onForceCard={vi.fn()} onPin={vi.fn()} />);
    expect(screen.getAllByText("Searching the web…").length).toBeGreaterThan(0);
  });
  it("done renders provenance chips and footer", () => {
    const card = baseCard({
      answer: {
        provider: "claude", status: "done", text: "- bullet", citations: [],
        provenance: [
          { text: "note bullet", label: "notes", passage_index: 0 },
          { text: "web bullet", label: "web", url: "https://example.com" },
          { text: "model bullet", label: "model" },
        ],
        egress_bytes: 812, web_performed: 1,
      },
    });
    const { container } = render(<CopilotCards cards={[card]} onForceCard={vi.fn()} onPin={vi.fn()} />);
    expect(screen.getByText("your notes")).toBeInTheDocument();
    expect(screen.getByText("web · example.com")).toBeInTheDocument();
    expect(screen.getAllByText("Claude")).toHaveLength(2);
    expect(screen.getByText((content) => content.includes("Prepared request payload: 812 bytes"))).toBeInTheDocument();
    expect(container.querySelector("a[href='https://example.com']")).not.toBeNull();
  });
  it("local done shows stayed and Local chip", () => {
    const card = baseCard({
      answer: { provider: "local", status: "done", text: "", citations: [], provenance: [{ text: "b", label: "model" }], egress_bytes: 0 },
    });
    render(<CopilotCards cards={[card]} onForceCard={vi.fn()} onPin={vi.fn()} />);
    expect(screen.getByText("0 bytes left this Mac")).toBeInTheDocument();
    expect(screen.getByText("Local")).toBeInTheDocument();
  });
  it("error shows message and Retry", () => {
    const card = baseCard({ answer: { provider: "claude", status: "error", text: "", citations: [], error: "boom" } });
    render(<CopilotCards cards={[card]} onForceCard={vi.fn()} onPin={vi.fn()} onRetry={vi.fn()} copilotMode="claude" />);
    expect(screen.getByText("boom")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Retry" })).toBeInTheDocument();
  });
  it("cancelled shows message and Retry", () => {
    const card = baseCard({ answer: { provider: "claude", status: "cancelled", text: "", citations: [], reason: "user" } });
    render(<CopilotCards cards={[card]} onForceCard={vi.fn()} onPin={vi.fn()} onRetry={vi.fn()} copilotMode="claude" />);
    expect(screen.getByText("Cancelled")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Retry" })).toBeInTheDocument();
  });
  it("hostile string renders as text", () => {
    const card = baseCard({ answer: { provider: "claude", status: "streaming", text: "<img src=x onerror=alert(1)>", citations: [] } });
    const { container } = render(<CopilotCards cards={[card]} onForceCard={vi.fn()} onPin={vi.fn()} />);
    expect(container.querySelector("img")).toBeNull();
    expect(container.textContent).toContain("<img src=x onerror=alert(1)>");
  });
  it("done without provenance falls back to streamed text", () => {
    const card = baseCard({ answer: { provider: "claude", status: "done", text: "fallback text", citations: [] } });
    const { container } = render(<CopilotCards cards={[card]} onForceCard={vi.fn()} onPin={vi.fn()} />);
    expect(container.textContent).toContain("fallback text");
  });
  it("sections say two sentences inside copilot-say with Say eyebrow", () => {
    const card = baseCard({
      answer: {
        provider: "claude",
        status: "done",
        text: "First sentence. Second sentence.",
        citations: [],
        sections: { say: ["First sentence.", "Second sentence."], specifics: [], notes: [], next: null },
      },
    });
    const { container } = render(<CopilotCards cards={[card]} onForceCard={vi.fn()} onPin={vi.fn()} />);
    expect(screen.getByText("Say")).toBeInTheDocument();
    const say = container.querySelector(".copilot-say");
    expect(say).not.toBeNull();
    expect(say?.textContent).toContain("First sentence.");
    expect(say?.textContent).toContain("Second sentence.");
    expect(container.querySelectorAll(".copilot-say-sentence")).toHaveLength(2);
  });
  it("first-person sentence is rendered", () => {
    const card = baseCard({
      answer: {
        provider: "claude",
        status: "done",
        text: "I built the gating agent first. Second.",
        citations: [],
        sections: { say: ["I built the gating agent first.", "Second."], specifics: [], notes: [], next: null },
      },
    });
    const { container } = render(<CopilotCards cards={[card]} onForceCard={vi.fn()} onPin={vi.fn()} />);
    expect(container.textContent).toContain("I built the gating agent first.");
  });
  it("note with passage_index 0 shows title chip and quote in q", () => {
    const card = baseCard({
      passages: [{ source_kind: "meeting", source_id: "1", title: "Kickoff", text: "passage", score: 1 }],
      answer: {
        provider: "claude",
        status: "done",
        text: "",
        citations: [],
        sections: { say: ["Hi."], specifics: [], notes: [{ passage_index: 0, quote: "exact quote", clause: "supports", text: "P1 | \"exact quote\" | supports" }], next: null },
      },
    });
    render(<CopilotCards cards={[card]} onForceCard={vi.fn()} onPin={vi.fn()} />);
    expect(screen.getByText("Kickoff")).toBeInTheDocument();
    const q = document.querySelector("q");
    expect(q).not.toBeNull();
    expect(q?.textContent).toBe("exact quote");
  });
  it("non-empty next renders inside details copilot-next not open", () => {
    const card = baseCard({
      answer: {
        provider: "claude",
        status: "done",
        text: "",
        citations: [],
        sections: { say: ["Hi."], specifics: [], notes: [], next: "What next?" },
      },
    });
    const { container } = render(<CopilotCards cards={[card]} onForceCard={vi.fn()} onPin={vi.fn()} />);
    const details = container.querySelector("details.copilot-next") as HTMLDetailsElement | null;
    expect(details).not.toBeNull();
    expect(details?.open).toBe(false);
    expect(details?.textContent).toContain("What next?");
  });
  it("card with text and no sections still renders text", () => {
    const card = baseCard({ answer: { provider: "claude", status: "done", text: "fallback text", citations: [] } });
    const { container } = render(<CopilotCards cards={[card]} onForceCard={vi.fn()} onPin={vi.fn()} />);
    expect(container.textContent).toContain("fallback text");
  });
  it("error answer with partial sections shows error text", () => {
    const card = baseCard({
      answer: {
        provider: "claude",
        status: "error",
        text: "",
        citations: [],
        error: "boom error",
        sections: { say: ["Partial."], specifics: [], notes: [], next: null },
      },
    });
    render(<CopilotCards cards={[card]} onForceCard={vi.fn()} onPin={vi.fn()} onRetry={vi.fn()} copilotMode="claude" />);
    expect(screen.getByText("boom error")).toBeInTheDocument();
    expect(screen.queryByText("Partial.")).not.toBeInTheDocument();
  });
});
