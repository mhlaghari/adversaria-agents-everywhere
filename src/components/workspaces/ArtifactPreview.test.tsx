import { mockIPC } from "@tauri-apps/api/mocks";
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import type { WorkspaceArtifact } from "../../types";
import { ArtifactPreview } from "./ArtifactPreview";

const SVG =
  '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 360"><rect width="10" height="10"/></svg>';

function artifact(name: string): WorkspaceArtifact {
  return {
    id: 9,
    workspace_id: 4,
    run_id: 51,
    name,
    path: `/tmp/${name}`,
    created_at: "2026-09-12T10:00:00Z",
  };
}

function mockArtifactText(text: string) {
  mockIPC((command) => (command === "read_workspace_artifact" ? text : null));
}

describe("ArtifactPreview diagrams", () => {
  it("renders an .svg artifact as an image", async () => {
    mockArtifactText(SVG);
    render(<ArtifactPreview artifact={artifact("diagram.svg")} />);

    const image = await screen.findByRole("img", {
      name: "diagram.svg: solutions architecture diagram",
    });
    expect(image).toHaveClass("ws-diagram-preview");
    expect(image.getAttribute("src")).toMatch(/^data:image\/svg\+xml;charset=utf-8,/);
    expect(decodeURIComponent(image.getAttribute("src") ?? "")).toContain(
      'xmlns="http://www.w3.org/2000/svg"',
    );
    expect(screen.getByRole("button", { name: "Open in default app" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Reveal in Finder" })).toBeInTheDocument();
  });

  it("extracts the inline svg from an .html artifact", async () => {
    mockArtifactText(
      `<!doctype html><html><body><h1>Architecture</h1>${SVG}</body></html>`,
    );
    render(<ArtifactPreview artifact={artifact("solutions-architecture.html")} />);

    const image = await screen.findByRole("img", {
      name: "solutions-architecture.html: solutions architecture diagram",
    });
    expect(decodeURIComponent(image.getAttribute("src") ?? "")).toContain("<rect");
  });

  it("says the preview is unavailable when the html has no svg", async () => {
    mockArtifactText("<html><body><p>No diagram here.</p></body></html>");
    render(<ArtifactPreview artifact={artifact("notes.html")} />);

    expect(await screen.findByText("Diagram preview unavailable")).toBeInTheDocument();
    expect(screen.queryByRole("img")).not.toBeInTheDocument();
  });
});
