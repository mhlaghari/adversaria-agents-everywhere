import fs from 'node:fs/promises';
import path from 'node:path';
import { createRequire } from 'node:module';
import { FileBlob, PresentationFile } from '/Users/mhlaghari/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs';
import { chromium } from '/Users/mhlaghari/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';

const ROOT = path.resolve(import.meta.dirname, '..');
const OUT = path.join(ROOT, 'output');
const BUILD = path.join(ROOT, '.build', 'four-slide');
const RUNTIME = '/Users/mhlaghari/.cache/codex-runtimes/codex-primary-runtime/dependencies';
const SKILL = '/Users/mhlaghari/.codex/plugins/cache/openai-primary-runtime/presentations/26.904.11930/skills/presentations';
process.env.RUNTIME_NODE_MODULES = RUNTIME + '/node/node_modules';
process.env.RUNTIME_NODE = RUNTIME + '/node/bin/node';
const require = createRequire(import.meta.url);
const { FontLibrary } = require(RUNTIME + '/node/node_modules/@oai/artifact-tool/node_modules/skia-canvas');
FontLibrary.use(['Silkscreen-400', 'JetBrainsMono-400'].map(name => path.join(ROOT, 'assets', name + '.ttf')));
await fs.mkdir(BUILD, { recursive: true });

const C = { cream: '#F2EBDA', ink: '#0E0E12', yellow: '#FFD23F', fire: '#FF4D2E', mint: '#06D6A0', blue: '#3A86FF' };
const W = 1600, H = 900;
const specs = [];
const add = (background) => { const s = { background, elements: [], notes: '' }; specs.push(s); return s; };
const text = (s, value, x, y, w, h, size, color = C.ink, family = 'Silkscreen', align = 'left') => s.elements.push({ kind: 'text', value, x, y, w, h, size, color, family, align });
const rect = (s, x, y, w, h, color, border = 0) => s.elements.push({ kind: 'rect', x, y, w, h, color, border });
const footer = (s, dark = false) => {
  text(s, 'LaghariLabs.com', 88, 796, 750, 48, 34, dark ? C.cream : C.ink);
  text(s, 'Hamza / Lead AI Engineer', 900, 803, 608, 40, 24, dark ? C.cream : C.ink, 'JetBrains Mono', 'right');
};
const source = '\n\nSources: Hamza’s brief, 12 September 2026, and repository README/CLI documentation. Design: the supplied Lagharilabs design/tokens.css and slides.jsx.';

let s = add(C.ink);
text(s, 'COPILOT', 88, 65, 1100, 40, 26, C.mint, 'JetBrains Mono');
text(s, 'Local notes.', 88, 235, 1420, 165, 130, C.cream);
text(s, 'Live suggestions.', 88, 393, 1420, 150, 108, C.mint);
text(s, 'Help with what to say next.', 94, 612, 1400, 70, 38, C.cream, 'JetBrains Mono');
footer(s, true);
s.notes = 'Adversaria takes my meeting notes locally. Copilot brings relevant context into the conversation and suggests what I can say next. Desktop local mode runs on-device. I can also choose optional cloud providers. This is the foundation I am building on.' + source;

s = add(C.cream);
text(s, 'WORKSPACES', 88, 65, 1100, 40, 26, C.ink, 'JetBrains Mono');
text(s, 'Research.', 88, 220, 1420, 164, 128);
text(s, 'Architecture.', 88, 368, 1420, 164, 128);
rect(s, 86, 554, 1432, 128, C.ink);
rect(s, 76, 544, 1432, 128, C.mint, 4);
text(s, 'I review the drafts.', 100, 530, 1384, 120, 94);
footer(s);
s.notes = 'The action items have somewhere to go. In Workspaces, I approve a task, research an approach and create a solution architecture diagram from meeting context. Adversaria prepares a draft and I review it. Web research uses external services when enabled.' + source;

s = add(C.blue);
text(s, 'BUILT TODAY', 88, 65, 1100, 40, 26, C.cream, 'JetBrains Mono');
text(s, 'Copilot + Spaces', 88, 218, 1420, 135, 106, C.cream);
text(s, 'Extended today', 94, 364, 1400, 60, 34, C.cream, 'JetBrains Mono');
text(s, 'Adversaria CLI', 88, 467, 1420, 150, 118, C.yellow);
text(s, 'Built with OpenAI Codex', 94, 615, 1400, 60, 34, C.cream, 'JetBrains Mono');
text(s, 'Sponsor APIs: OpenRouter + Exa AI', 94, 720, 1400, 45, 28, C.cream, 'JetBrains Mono');
footer(s, true);
s.notes = 'Today I extended the existing Copilot and Spaces workflow and built a new terminal edition with OpenAI Codex. The CLI uses OpenRouter for speech and models and Exa AI for outside questions and research. The CLI uses cloud services with local storage. Let me show the workflow.' + source;

// Import the approved slide so its native editable layout stays unchanged.
const presentation = await PresentationFile.importPptx(await FileBlob.load(path.join(OUT, 'adversaria-one-slide.pptx')));
const openingNotes = 'I am Hamza, a lead AI engineer. Every meeting adds hours of follow-up while my own projects wait. An action item can take me another hour or two. That is why I built Adversaria. This describes my own experience.' + source;
presentation.slides.items[0].speakerNotes.textFrame.setText(openingNotes);
for (const spec of specs) {
  const slide = presentation.slides.add();
  slide.background.fill = spec.background;
  slide.shapes.add({ geometry: 'rect', name: 'Laghari Labs frame', position: { left: 2, top: 2, width: W - 4, height: H - 4 }, fill: 'none', line: { fill: C.ink, width: 4 } });
  for (const [i, e] of spec.elements.entries()) {
    const shape = slide.shapes.add({ geometry: e.kind === 'text' ? 'textbox' : 'rect', name: e.kind === 'text' ? `Editable text ${i}` : `Brand highlight ${i}`, position: { left: e.x, top: e.y, width: e.w, height: e.h }, fill: e.kind === 'text' ? 'none' : e.color, line: { fill: e.border ? C.ink : 'none', width: e.border || 0 } });
    if (e.kind === 'text') {
      shape.text = e.value;
      shape.text.style = { typeface: e.family, fontSize: e.size, color: e.color, alignment: e.align, verticalAlignment: 'top', autoFit: 'none', wrap: 'none', insets: { top: 0, bottom: 0, left: 0, right: 0 }, lineSpacing: 1.2 };
    }
  }
  slide.speakerNotes.textFrame.setText(spec.notes);
}
const candidatePath = path.join(BUILD, 'candidate.pptx');
await (await PresentationFile.exportPptx(presentation)).save(candidatePath);
const { finalizePresentation } = await import(SKILL + '/container_tools/artifact_tool_utils.mjs');
const finalPath = path.join(OUT, process.env.STORY_PPTX || 'adversaria-story-short.pptx');
await finalizePresentation({ workspaceDir: ROOT, candidatePath, finalPath, explicitTotalSlideCount: 4,
  pythonExecutable: RUNTIME + '/python/bin/python3', integrityValidatorPath: SKILL + '/container_tools/inspect_presentation_package_integrity.py', layoutValidatorPath: SKILL + '/container_tools/inspect_presentation_layout_geometry.py',
  layoutArgs: ['--expected-slide-size-emu', '15240000,8572500', '--validate-heading-fit'], requiredNativeTableOwnerSlides: [], requiredNativeChartOwnerSlides: [],
  fontPolicy: { basis: 'design', families: ['Silkscreen', 'JetBrains Mono'] }, verifyArtifactToolImport: true, receiptPath: path.join(BUILD, path.basename(finalPath) + '.validation.json') });
const finalDeck = await PresentationFile.importPptx(await FileBlob.load(finalPath));
for (const [i, slide] of finalDeck.slides.items.entries()) {
  const png = await finalDeck.export({ slide, format: 'png', scale: 1 });
  await fs.writeFile(path.join(BUILD, `final-pptx-${i + 1}.png`), new Uint8Array(await png.arrayBuffer()));
}

const escape = value => value.replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;');
const originalHTML = await fs.readFile(path.join(OUT, 'adversaria-one-slide.html'), 'utf8');
const fontCSS = [...originalHTML.matchAll(/@font-face\{[^}]+\}/g)].map(match => match[0]).join('\n');
const licenses = originalHTML.match(/<!-- Font licenses: ([\s\S]*?) -->/)[1];
const opening = originalHTML.match(/<main id="slide"[^>]*>([\s\S]*?)<\/main>/)[1];
const elementHTML = e => e.kind === 'rect'
  ? `<div class="element" style="left:${e.x}px;top:${e.y}px;width:${e.w}px;height:${e.h}px;background:${e.color};border:${e.border}px solid ${C.ink}"></div>`
  : `<div class="element text" style="left:${e.x}px;top:${e.y}px;width:${e.w}px;height:${e.h}px;font:400 ${e.size}px '${e.family}';line-height:1.2;color:${e.color};text-align:${e.align}">${escape(e.value)}</div>`;
const pages = [{ background: C.cream, inner: opening, notes: openingNotes }, ...specs.map(spec => ({ background: spec.background, inner: spec.elements.map(elementHTML).join('\n'), notes: spec.notes }))];
const html = `<!doctype html><html lang="en"><!-- Font licenses: ${licenses} --><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Adversaria story</title><style>${fontCSS}
*{box-sizing:border-box}body{margin:0;background:#18181F;color:${C.cream};font-family:'JetBrains Mono',monospace}#stage{position:fixed;left:50%;top:50%;width:1600px;height:900px;transform-origin:center}.slide{position:absolute;width:1600px;height:900px;outline:4px solid ${C.ink};outline-offset:-4px;overflow:hidden;display:none}.slide.active{display:block}.element{position:absolute}.text{white-space:nowrap;padding:0;margin:0}.controls{position:fixed;bottom:12px;right:16px;display:flex;align-items:center;gap:8px;opacity:0;transition:opacity .2s}.controls:hover,.controls:focus-within{opacity:1}button,#counter{font:13px 'JetBrains Mono';padding:10px;background:${C.cream};color:${C.ink};border:2px solid ${C.ink}}button{cursor:pointer}#notes{display:none;position:fixed;right:20px;bottom:68px;max-width:650px;max-height:75vh;overflow:auto;background:${C.cream};color:${C.ink};padding:28px;border:4px solid ${C.ink};font-size:18px;line-height:1.5;white-space:pre-wrap}#notes.open{display:block}@page{size:1600px 900px;margin:0}@media print{body{background:none}#stage{position:static;transform:none!important;height:auto}.slide{position:relative;display:block!important;break-after:page;page-break-after:always;print-color-adjust:exact;-webkit-print-color-adjust:exact}.slide:last-child{break-after:auto;page-break-after:auto}.controls,#notes{display:none!important}}
</style></head><body><main id="stage">${pages.map((p, i) => `<section class="slide${i === 0 ? ' active' : ''}" aria-label="Slide ${i + 1}" data-notes="${escape(p.notes)}" style="background:${p.background}">${p.inner}</section>`).join('\n')}</main><nav class="controls" aria-label="Presentation controls"><button id="prev">Previous</button><span id="counter">1 / 4</span><button id="next">Next</button><button id="full">Fullscreen (F)</button><button id="notesButton">Notes (N)</button></nav><aside id="notes"></aside><script>
const slides=[...document.querySelectorAll('.slide')];let current=0;
function fit(){document.querySelector('#stage').style.transform='translate(-50%,-50%) scale('+Math.min(innerWidth/1600,innerHeight/900)+')'}
function show(index){current=Math.max(0,Math.min(slides.length-1,index));slides.forEach((slide,i)=>slide.classList.toggle('active',i===current));document.querySelector('#counter').textContent=(current+1)+' / '+slides.length;document.querySelector('#notes').textContent=slides[current].dataset.notes;history.replaceState(null,'','#'+(current+1))}
document.querySelector('#prev').onclick=()=>show(current-1);document.querySelector('#next').onclick=()=>show(current+1);document.querySelector('#full').onclick=()=>document.fullscreenElement?document.exitFullscreen():document.documentElement.requestFullscreen();document.querySelector('#notesButton').onclick=()=>document.querySelector('#notes').classList.toggle('open');addEventListener('keydown',event=>{if(['ArrowRight','PageDown',' '].includes(event.key)){event.preventDefault();show(current+1)}if(['ArrowLeft','PageUp'].includes(event.key)){event.preventDefault();show(current-1)}if(event.key==='Home')show(0);if(event.key==='End')show(slides.length-1);if(event.key.toLowerCase()==='f')document.querySelector('#full').click();if(event.key.toLowerCase()==='n')document.querySelector('#notesButton').click();if(event.key==='Escape')document.querySelector('#notes').classList.remove('open')});addEventListener('resize',fit);fit();show(Number(location.hash.slice(1)||1)-1);
</script></body></html>`;
await fs.writeFile(path.join(OUT, 'adversaria-story.html'), html);
await fs.writeFile(path.join(OUT, 'presenter-notes.md'), '# Adversaria story\n\n' + pages.map((p, i) => `## Slide ${i + 1}\n\n${p.notes.replace(source, '')}`).join('\n\n') + '\n');
const browser = await chromium.launch({ headless: true, executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' });
try {
  const page = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 1 });
  await page.goto('file://' + path.join(OUT, 'adversaria-story.html'));
  await page.evaluate(() => document.fonts.ready);
  const checks = [];
  for (let i = 0; i < pages.length; i++) {
    await page.evaluate(i => show(i), i);
    const overflows = await page.locator('.slide.active .text').evaluateAll(elements => elements.filter(e => e.scrollWidth > e.clientWidth + 1 || e.scrollHeight > e.clientHeight + 1).map(e => e.textContent));
    if (overflows.length) throw new Error(`Slide ${i + 1} overflow: ` + JSON.stringify(overflows));
    await page.locator('.slide.active').screenshot({ path: path.join(BUILD, `html-${i + 1}.png`) });
    checks.push({ slide: i + 1, overflows });
  }
  await page.emulateMedia({ media: 'print' });
  await page.pdf({ path: path.join(OUT, 'adversaria-story.pdf'), width: '1600px', height: '900px', printBackground: true, preferCSSPageSize: true, displayHeaderFooter: false });
  await page.emulateMedia({ media: 'screen' });
  await page.keyboard.press('Home');
  await page.keyboard.press('ArrowRight');
  if (await page.locator('#counter').textContent() !== '2 / 4') throw new Error('Navigation did not advance');
  await page.keyboard.press('n');
  if (!await page.locator('#notes').isVisible()) throw new Error('Notes did not open');
  await fs.writeFile(path.join(BUILD, 'browser-validation.json'), JSON.stringify({ checks, navigation: true, notes: true }, null, 2));
} finally { await browser.close(); }
console.log('Four-slide story written: ' + finalPath);
