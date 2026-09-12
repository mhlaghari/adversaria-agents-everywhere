import { useEffect, useState } from "react";

import { markdownToHtml } from "../../lib/markdown";
import {
  openWorkspaceArtifact,
  readWorkspaceArtifact,
  revealWorkspaceArtifact,
} from "../../lib/tauri";
import type { WorkspaceArtifact } from "../../types";

interface ArtifactPreviewProps {
  artifact: WorkspaceArtifact;
}

function errorMessage(error: unknown): string {
  return error instanceof Error ? error.message : String(error);
}

const SVG_NS = "http://www.w3.org/2000/svg";

/**
 * The first standalone `<svg>` in an `.svg` or `.html` artifact, serialized
 * with the SVG namespace so it renders as a data-URI image. Null when the
 * text has no SVG or the parser rejected it.
 */
export function extractSvgMarkup(text: string, isHtml: boolean): string | null {
  const parser = new DOMParser();
  const doc = parser.parseFromString(text, isHtml ? "text/html" : "image/svg+xml");
  if (doc.getElementsByTagName("parsererror").length > 0) return null;
  const svg = doc.getElementsByTagName("svg")[0];
  if (!svg) return null;
  if (svg.namespaceURI !== SVG_NS) svg.setAttribute("xmlns", SVG_NS);
  return new XMLSerializer().serializeToString(svg);
}

export function ArtifactPreview({ artifact }: ArtifactPreviewProps) {
  const lowerName = artifact.name.toLowerCase();
  const isDrawio = lowerName.endsWith(".drawio");
  const isSvg = lowerName.endsWith(".svg");
  const isHtml = lowerName.endsWith(".html") || lowerName.endsWith(".htm");
  const path = artifact.path;
  const [loading, setLoading] = useState(true);
  const [imageFailed, setImageFailed] = useState(false);
  const [text, setText] = useState("");
  const [readError, setReadError] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [actionPending, setActionPending] = useState(false);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setText("");
    setReadError(null);
    setActionError(null);
    setImageFailed(false);
    if (isDrawio) {
      setLoading(false);
      return () => {
        cancelled = true;
      };
    }
    void readWorkspaceArtifact(path)
      .then((content) => {
        if (!cancelled) setText(content);
      })
      .catch((error: unknown) => {
        if (!cancelled) setReadError(errorMessage(error));
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
    // Keyed by id/path (not the artifact object) so a detail refresh that
    // rebuilds the artifact list does not re-read and flash the preview.
  }, [artifact.id, isDrawio, path]);

  const runAction = async (action: (path: string) => Promise<void>) => {
    if (actionPending) return;
    setActionPending(true);
    setActionError(null);
    try {
      await action(artifact.path);
    } catch (error) {
      setActionError(errorMessage(error));
    } finally {
      setActionPending(false);
    }
  };

  if (loading) return <p className="ws-preview-status">Loading…</p>;

  const isMarkdown = lowerName.endsWith(".md") || lowerName.endsWith(".markdown");
  const isPlainText = [".txt", ".json", ".csv", ".yaml", ".yml", ".log"].some(
    (extension) => lowerName.endsWith(extension),
  );
  const svgMarkup =
    (isSvg || isHtml) && !readError ? extractSvgMarkup(text, isHtml) : null;

  return (
    <>
      {isDrawio ? (
        <p className="ws-preview-status">Diagram — opens in draw.io</p>
      ) : readError ? (
        <p className="ws-error">{readError}</p>
      ) : isMarkdown ? (
        <article
          className="ws-artifact-preview"
          dangerouslySetInnerHTML={{ __html: markdownToHtml(text) }}
        />
      ) : isPlainText ? (
        <pre className="ws-artifact-preview ws-artifact-preview--plain">{text}</pre>
      ) : isSvg || isHtml ? (
        svgMarkup && !imageFailed ? (
          <img
            className="ws-diagram-preview"
            src={`data:image/svg+xml;charset=utf-8,${encodeURIComponent(svgMarkup)}`}
            alt={`${artifact.name}: solutions architecture diagram`}
            onError={() => setImageFailed(true)}
          />
        ) : (
          <p className="ws-preview-status">Diagram preview unavailable</p>
        )
      ) : (
        <p className="ws-preview-status">No in-app preview for this file type.</p>
      )}
      {actionError && <p className="ws-error">{actionError}</p>}
      <div className="ws-preview-actions">
        <button
          className="btn-secondary"
          type="button"
          disabled={actionPending}
          onClick={() => void runAction(openWorkspaceArtifact)}
        >
          {isDrawio ? "Open in draw.io" : "Open in default app"}
        </button>
        <button
          className="btn-secondary"
          type="button"
          disabled={actionPending}
          onClick={() => void runAction(revealWorkspaceArtifact)}
        >
          Reveal in Finder
        </button>
      </div>
    </>
  );
}
