import "@testing-library/jest-dom/vitest";
import { cleanup } from "@testing-library/react";
import { clearMocks } from "@tauri-apps/api/mocks";
import { afterEach } from "vitest";

afterEach(() => {
  cleanup();
  clearMocks();
});

// jsdom has no matchMedia. Width queries resolve against window.innerWidth, which defaults to a
// 1280px desktop here (wider than the 900px companion and 1120px Workspaces breakpoints) so views
// render their wide layouts unless a test narrows the window; non-width queries are false.
Object.defineProperty(window, "innerWidth", { configurable: true, writable: true, value: 1280 });

function evaluateMediaQuery(query: string): boolean {
  const min = /\(min-width:\s*(\d+)px\)/.exec(query);
  if (min) return window.innerWidth >= Number(min[1]);
  const max = /\(max-width:\s*(\d+)px\)/.exec(query);
  if (max) return window.innerWidth <= Number(max[1]);
  const lt = /\(width\s*<\s*(\d+)px\)/.exec(query);
  if (lt) return window.innerWidth < Number(lt[1]);
  return false;
}

Object.defineProperty(window, "matchMedia", {
  writable: true,
  value: (query: string) => ({
    matches: evaluateMediaQuery(query),
    media: query,
    onchange: null,
    addListener: () => undefined,
    removeListener: () => undefined,
    addEventListener: () => undefined,
    removeEventListener: () => undefined,
    dispatchEvent: () => false,
  }),
});

class ResizeObserverStub {
  observe() {}
  unobserve() {}
  disconnect() {}
}

globalThis.ResizeObserver = ResizeObserverStub;
