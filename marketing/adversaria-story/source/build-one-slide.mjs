import fs from 'node:fs/promises';
import path from 'node:path';
import { createRequire } from 'node:module';
import { Presentation, PresentationFile } from '/Users/mhlaghari/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs';
import { chromium } from '/Users/mhlaghari/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';

const ROOT = path.resolve(import.meta.dirname, '..');
const OUT = path.join(ROOT, 'output');
const BUILD = path.join(ROOT, '.build', 'one-slide');
const RUNTIME = '/Users/mhlaghari/.cache/codex-runtimes/codex-primary-runtime/dependencies';
const SKILL = '/Users/mhlaghari/.codex/plugins/cache/openai-primary-runtime/presentations/26.904.11930/skills/presentations';
process.env.RUNTIME_NODE_MODULES = RUNTIME + '/node/node_modules';
process.env.RUNTIME_NODE = RUNTIME + '/node/bin/node';
const require = createRequire(import.meta.url);
const { FontLibrary, Canvas } = require(RUNTIME + '/node/node_modules/@oai/artifact-tool/node_modules/skia-canvas');
const fontNames = ['Silkscreen-400', 'JetBrainsMono-400'];
FontLibrary.use(fontNames.map(name => path.join(ROOT, 'assets', name + '.ttf')));
await fs.mkdir(BUILD, { recursive: true });
await fs.mkdir(OUT, { recursive: true });

const C = { cream: '#F2EBDA', ink: '#0E0E12', yellow: '#FFD23F', fire: '#FF4D2E' };
const W = 1600, H = 900;
const sentence = 'Every meeting adds hours of follow-up while my own projects wait.';
const lines = ['Every meeting adds', 'hours of follow-up', 'while my own projects wait.'];
const ctx = new Canvas(1600, 900).getContext('2d');
let size = 88;
while (size > 70) {
  ctx.font = `${size}px Silkscreen`;
  if (Math.max(...lines.map(line => ctx.measureText(line).width)) <= 1408) break;
  size -= 1;
}
const entries = [];
const rect = (x, y, w, h, color, border = 0) => entries.push({ kind: 'rect', x, y, w, h, color, border });
const text = (value, x, y, w, h, fontSize, family = 'Silkscreen', color = C.ink, align = 'left') => entries.push({ kind: 'text', value, x, y, w, h, fontSize, family, color, align });

text('WHY I BUILT ADVERSARIA', 88, 65, 1100, 40, 26, 'JetBrains Mono');
text(lines[0], 88, 253, 1410, 125, size);
text(lines[1], 88, 378, 1410, 125, size, 'Silkscreen', C.fire);
// The highlight and hard offset reproduce the supplied Laghari Labs reference.
rect(86, 520, 1432, 136, C.ink);
rect(76, 510, 1432, 136, C.yellow, 4);
text(lines[2], 88, 507, 1410, 130, size);
text('LaghariLabs.com', 88, 796, 750, 48, 34);
text('Hamza / Lead AI Engineer', 900, 803, 608, 40, 24, 'JetBrains Mono', C.ink, 'right');

const notes = 'Every meeting adds hours of follow-up while my own projects wait.\n\n'
  + 'I am Hamza, a lead AI engineer. I attend many meetings, and each action item can take another hour or two. I still have my own projects to build. That is why I built Adversaria.\n\n'
  + 'Now show the product: local meeting notes, Copilot suggestions, and a research or solution architecture draft in a workspace. Today I extended the existing Copilot and Spaces workflow and built the CLI using OpenAI Codex. The CLI integrates sponsor APIs: OpenRouter for speech and models, and Exa AI for outside questions and research.\n\n'
  + 'The desktop supports fully local operation. Optional cloud features and the API-powered CLI use external services.\n\n'
  + 'Sources: Hamza’s first-person brief, 12 September 2026, and repository README/CLI documentation. Design: supplied Lagharilabs design/tokens.css and slides.jsx. The time estimate describes Hamza’s own experience.';

const presentation = Presentation.create({ slideSize: { width: W, height: H } });
const slide = presentation.slides.add();
slide.background.fill = C.cream;
slide.shapes.add({ geometry: 'rect', name: 'Laghari Labs frame', position: { left: 2, top: 2, width: W - 4, height: H - 4 }, fill: 'none', line: { fill: C.ink, width: 4 } });
for (const [i, e] of entries.entries()) {
  const shape = slide.shapes.add({
    geometry: e.kind === 'text' ? 'textbox' : 'rect',
    name: e.kind === 'text' ? `Editable text ${i}` : `Brand highlight ${i}`,
    position: { left: e.x, top: e.y, width: e.w, height: e.h },
    fill: e.kind === 'text' ? 'none' : e.color,
    line: { fill: e.border ? C.ink : 'none', width: e.border || 0 },
  });
  if (e.kind === 'text') {
    shape.text = e.value;
    shape.text.style = { typeface: e.family, fontSize: e.fontSize, color: e.color, alignment: e.align, verticalAlignment: 'top', autoFit: 'none', wrap: 'none', insets: { top: 0, bottom: 0, left: 0, right: 0 }, lineSpacing: 1.2 };
  }
}
slide.speakerNotes.textFrame.setText(notes);
const nativePreview = await presentation.export({ slide, format: 'png', scale: 1 });
await fs.writeFile(path.join(BUILD, 'native-preview.png'), new Uint8Array(await nativePreview.arrayBuffer()));
const candidatePath = path.join(BUILD, 'candidate.pptx');
await (await PresentationFile.exportPptx(presentation)).save(candidatePath);
const { finalizePresentation } = await import(SKILL + '/container_tools/artifact_tool_utils.mjs');
const finalPath = path.join(OUT, process.env.ONE_SLIDE_PPTX || 'adversaria-one-slide.pptx');
const validation = await finalizePresentation({
  workspaceDir: ROOT, candidatePath, finalPath,
  explicitTotalSlideCount: 1,
  pythonExecutable: RUNTIME + '/python/bin/python3',
  integrityValidatorPath: SKILL + '/container_tools/inspect_presentation_package_integrity.py',
  layoutValidatorPath: SKILL + '/container_tools/inspect_presentation_layout_geometry.py',
  layoutArgs: ['--expected-slide-size-emu', '15240000,8572500', '--validate-heading-fit'],
  requiredNativeTableOwnerSlides: [], requiredNativeChartOwnerSlides: [],
  fontPolicy: { basis: 'design', families: ['Silkscreen', 'JetBrains Mono'] },
  verifyArtifactToolImport: true,
  receiptPath: path.join(BUILD, path.basename(finalPath) + '.validation.json'),
});

const escape = value => value.replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;');
let fontCSS = '';
for (const name of fontNames) {
  const family = name.startsWith('Silk') ? 'Silkscreen' : 'JetBrains Mono';
  const bytes = await fs.readFile(path.join(ROOT, 'assets', name + '.ttf'));
  fontCSS += `@font-face{font-family:'${family}';font-weight:400;font-display:block;src:url(data:font/ttf;base64,${bytes.toString('base64')}) format('truetype')}\n`;
}
const licenses = (await Promise.all(['Silkscreen-OFL.txt', 'JetBrainsMono-OFL.txt'].map(name => fs.readFile(path.join(ROOT, 'assets', name), 'utf8')))).join('\n');
const content = entries.map(e => e.kind === 'rect'
  ? `<div class="element" style="left:${e.x}px;top:${e.y}px;width:${e.w}px;height:${e.h}px;background:${e.color};border:${e.border}px solid ${C.ink}"></div>`
  : `<div class="element text" style="left:${e.x}px;top:${e.y}px;width:${e.w}px;height:${e.h}px;font:400 ${e.fontSize}px '${e.family}';line-height:1.2;color:${e.color};text-align:${e.align}">${escape(e.value)}</div>`).join('\n');
const html = `<!doctype html><html lang="en"><!-- Font licenses: ${licenses} --><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Why I built Adversaria</title><style>
${fontCSS}
*{box-sizing:border-box}body{margin:0;background:#18181F;color:${C.cream};font-family:'JetBrains Mono',monospace}#slide{position:fixed;left:50%;top:50%;width:1600px;height:900px;transform-origin:center;background:${C.cream};outline:4px solid ${C.ink};outline-offset:-4px;overflow:hidden}.element{position:absolute}.text{white-space:nowrap;padding:0;margin:0}.controls{position:fixed;bottom:12px;right:16px;display:flex;gap:8px;opacity:0;transition:opacity .2s}.controls:hover,.controls:focus-within{opacity:1}button{font:13px 'JetBrains Mono';padding:10px;background:${C.cream};color:${C.ink};border:2px solid ${C.ink};cursor:pointer}#notes{display:none;position:fixed;right:20px;bottom:68px;max-width:650px;max-height:75vh;overflow:auto;background:${C.cream};color:${C.ink};padding:28px;border:4px solid ${C.ink};font-size:18px;line-height:1.5;white-space:pre-wrap}#notes.open{display:block}@page{size:1600px 900px;margin:0}@media print{body{background:none}#slide{position:relative;left:0;top:0;transform:none!important;print-color-adjust:exact;-webkit-print-color-adjust:exact}.controls,#notes{display:none!important}}
</style></head><body><main id="slide" aria-label="${escape(sentence)}">${content}</main><div class="controls"><button id="full">Fullscreen (F)</button><button id="notesButton">Notes (N)</button></div><aside id="notes">${escape(notes)}</aside><script>
function fit(){document.querySelector('#slide').style.transform='translate(-50%,-50%) scale('+Math.min(innerWidth/1600,innerHeight/900)+')'}
document.querySelector('#full').onclick=()=>document.fullscreenElement?document.exitFullscreen():document.documentElement.requestFullscreen();document.querySelector('#notesButton').onclick=()=>document.querySelector('#notes').classList.toggle('open');addEventListener('keydown',event=>{if(event.key.toLowerCase()==='f')document.querySelector('#full').click();if(event.key.toLowerCase()==='n')document.querySelector('#notesButton').click();if(event.key==='Escape')document.querySelector('#notes').classList.remove('open')});addEventListener('resize',fit);fit();
</script></body></html>`;
await fs.writeFile(path.join(OUT, 'adversaria-one-slide.html'), html);
await fs.writeFile(path.join(OUT, 'one-slide-notes.md'), '# Why I built Adversaria\n\n' + notes + '\n');
const browser = await chromium.launch({ headless: true, executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' });
try {
  const page = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 1 });
  await page.goto('file://' + path.join(OUT, 'adversaria-one-slide.html'));
  await page.evaluate(() => document.fonts.ready);
  const overflows = await page.locator('.text').evaluateAll(elements => elements.filter(e => e.scrollWidth > e.clientWidth + 1 || e.scrollHeight > e.clientHeight + 1).map(e => e.textContent));
  if (overflows.length) throw new Error('Text overflow: ' + JSON.stringify(overflows));
  await page.screenshot({ path: path.join(OUT, 'adversaria-one-slide.png') });
  await page.emulateMedia({ media: 'print' });
  await page.pdf({ path: path.join(OUT, 'adversaria-one-slide.pdf'), width: '1600px', height: '900px', printBackground: true, preferCSSPageSize: true, displayHeaderFooter: false });
  await page.emulateMedia({ media: 'screen' });
  await page.keyboard.press('n');
  if (!await page.locator('#notes').isVisible()) throw new Error('Speaker notes did not open');
  await fs.writeFile(path.join(BUILD, 'browser-validation.json'), JSON.stringify({ fontSize: size, overflows, notesToggle: true, sentence }, null, 2));
} finally { await browser.close(); }
console.log(JSON.stringify({ finalPath, fontSize: size, validation }));
