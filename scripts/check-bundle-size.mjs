import { readFile, stat } from "node:fs/promises";
import { resolve } from "node:path";

// 2026-09-12: raised 500_000 -> 520_000 for the live-commitment UI in the
// recording companion (task type control + in-card run progress). The Phase 0
// number was a self-imposed ceiling, not a measured limit; 20 kB of JS is not a
// meaningful cost on the 8 GB target (see docs/PERF_8GB.md). Revisit if the
// entry chunk keeps climbing — the next step is code-splitting Workspaces.
const budgetBytes = 520_000;
const distDir = resolve("dist");
const html = await readFile(resolve(distDir, "index.html"), "utf8");
const match = html.match(/<script[^>]+src="([^"]+\.js)"/);

if (!match) {
  throw new Error("Bundle budget check could not find the entry script in dist/index.html");
}

const entryPath = resolve(distDir, match[1].replace(/^\//, ""));
const { size } = await stat(entryPath);
const kb = (size / 1000).toFixed(2);

if (size > budgetBytes) {
  throw new Error(
    `Main entry bundle is ${kb} kB; the budget is ${(budgetBytes / 1000).toFixed(0)} kB`,
  );
}

console.log(`Bundle budget passed: main entry ${kb} kB / ${(budgetBytes / 1000).toFixed(2)} kB`);
