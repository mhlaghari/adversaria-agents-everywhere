import fs from 'node:fs/promises';
import path from 'node:path';
import { createRequire } from 'node:module';
import { Presentation, PresentationFile } from '/Users/mhlaghari/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs';
const require=createRequire(import.meta.url);
const {FontLibrary}=require('/Users/mhlaghari/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/@oai/artifact-tool/node_modules/skia-canvas');
const ROOT=path.resolve(import.meta.dirname,'..');
const OUT=path.join(ROOT,'output');
const SKILL='/Users/mhlaghari/.codex/plugins/cache/openai-primary-runtime/presentations/26.904.11930/skills/presentations';
const RUNTIME='/Users/mhlaghari/.cache/codex-runtimes/codex-primary-runtime/dependencies';
process.env.RUNTIME_NODE_MODULES=RUNTIME+'/node/node_modules';
process.env.RUNTIME_NODE=RUNTIME+'/node/bin/node';
const C={bg:'#F2EBDA',bg2:'#E8DFC6',ink:'#0E0E12',muted:'#6B6470',red:'#FF4D2E',yellow:'#FFD23F',blue:'#3A86FF',mint:'#06D6A0',purple:'#B388FF'};
const fonts=['JetBrainsMono-400','JetBrainsMono-500','JetBrainsMono-700','Silkscreen-400','Silkscreen-700'];
FontLibrary.use(fonts.map(x=>path.join(ROOT,'assets',x+'.ttf')));
const W=1600,H=900;
const deck=[];
const S=(bg=C.bg)=>{const s={bg,e:[],notes:''};deck.push(s);return s;};
const box=(s,x,y,w,h,fill=C.bg,border=0,shadow=null)=>s.e.push({kind:'box',x,y,w,h,fill,border,shadow});
const text=(s,str,x,y,w,h,size=36,opts={})=>s.e.push({kind:'text',str,x,y,w,h,size,font:opts.display?'Silkscreen':'JetBrains Mono',color:opts.color??C.ink,bold:opts.bold??false,align:opts.align??'left',leading:opts.leading??1.2});
const title=(s,str,x,y,w,h,size=100,color=C.ink)=>text(s,str,x,y,w,h,size,{display:true,color,leading:1.02});
const foot=(s,n,dark=false)=>{const ink=dark?C.bg:C.ink;box(s,60,816,1480,3,ink);text(s,'LaghariLabs.io',60,839,400,35,27,{display:true,color:ink,bold:true});text(s,'@mhlaghari',1110,839,235,35,24,{color:ink});text(s,String(n).padStart(2,'0')+' / 08',1385,839,155,35,24,{color:ink,align:'right'});};
const label=(s,str,color=C.ink)=>text(s,str,60,52,1440,36,24,{color,bold:true});
const source='Sources: Hamza’s brief, 12 September 2026; repository README.md, HACKATHON.md and CLI documentation. Design: LaghariLabs design/tokens.css, slides.jsx and system.jsx. Fonts: Silkscreen and JetBrains Mono, Google Fonts.';

let s=S();
label(s,'FIELD NOTES     ADVERSARIA');
title(s,'Why I built',60,204,1430,140,124);
box(s,60,353,1300,168,C.yellow,4,C.ink);
title(s,'Adversaria',84,353,1270,166,146);
text(s,'Meetings create more work than I have time for.',64,570,1410,75,38);
text(s,'Mohammad Hamza Laghari',64,704,1380,48,30,{bold:true});
text(s,'Lead AI Engineer   /   An ongoing Laghari Labs project',64,756,1380,44,26,{color:C.muted});
foot(s,1);
s.notes='I am Hamza, a lead AI engineer. Adversaria is an ongoing project I am building at Laghari Labs. I built it because my meetings kept producing more work while my own projects waited. Today I extended the desktop Copilot and Spaces experience and built a terminal edition. '+source;

s=S();label(s,'THE WORK AFTER THE MEETING');
title(s,'Every action item',60,136,1480,110,92);
title(s,'costs me time',60,236,1480,110,92);
title(s,'1–2',48,380,800,286,246,C.red);
title(s,'hours',78,637,600,85,76);
box(s,852,397,5,322,C.ink);
text(s,'Research the options.\nDraft the architecture.\nWrite the follow-up.',905,415,620,200,37,{leading:1.6});
text(s,'Then the next meeting starts.',905,665,620,70,30,{bold:true});
foot(s,2);
s.notes='As a lead AI engineer, I attend many meetings. In my experience, an action item can take another hour or two. The work might be researching an approach or turning the discussion into a solution architecture. The meeting ends, but that work remains. The time estimate is my experience, not a claim about everyone or a measured time saving. '+source;

s=S(C.blue);label(s,'WHAT GETS SQUEEZED',C.bg);
title(s,'My own projects',60,168,1450,135,106,C.bg);
title(s,'get the time',60,295,1450,135,106,C.bg);
box(s,60,445,1130,144,C.yellow,4,C.ink);
title(s,'left over',86,446,1080,138,120);
text(s,'I needed help with the work\nthat meetings create.',66,655,1390,112,40,{color:C.bg,leading:1.4});
foot(s,3,true);
s.notes='I still have my own projects to build. When every meeting produces more follow-up, those projects get whatever time is left. That is the personal pain behind Adversaria. I wanted the context and commitments from a meeting to help me start the actual work. '+source;

s=S();label(s,'THE FOUNDATION');
title(s,'Local meeting notes',60,139,1460,105,92);
text(s,'A memory I can come back to.',64,271,1390,66,40);
box(s,60,390,1470,329,C.bg2,4,C.red);
text(s,'ON MY MACHINE',94,424,1365,40,27,{bold:true});
title(s,'Audio. Transcript. Notes.',94,496,1390,96,66);
text(s,'Capture the discussion and keep its context\nwith the work that follows.',98,576,1365,105,33,{leading:1.4});
text(s,'Desktop local mode runs on-device. Cloud features are optional.',64,752,1440,44,26,{color:C.muted});
foot(s,4);
s.notes='Adversaria starts with a local desktop meeting workflow. It captures the meeting and keeps transcripts and notes locally. In local mode, the desktop can use on-device transcription and AI. It also supports optional external providers. Workspace web research and cloud agents require external services, so I do not describe those paths as completely local. The local notes workflow is the foundation. '+source;

s=S();label(s,'COPILOT');
title(s,'Help while I’m',60,137,1460,124,104);
title(s,'in the room',60,247,1460,124,104);
box(s,60,423,1470,145,C.yellow,3,C.ink);
title(s,'What to say next',91,447,1410,68,54);
text(s,'Relevant context and suggestions for what to say.',94,514,1390,48,29);
box(s,60,605,1470,145,C.mint,3,C.ink);
title(s,'A commitment I can act on',91,629,1410,68,54);
text(s,'Surface the follow-up so I can review it.',94,696,1390,48,29);
foot(s,5);
s.notes='During a meeting, Copilot uses the discussion to suggest useful context and talking points. It also catches commitments and presents the follow-up for my review. That means I can stay in the conversation and still see what needs to happen afterward. '+source;

s=S();label(s,'SPACES / WORKSPACES');
title(s,'The work has a place',60,134,1470,112,92);
text(s,'Meeting context stays with the task.',64,274,1440,62,39);
box(s,60,385,712,318,C.bg2,3);
text(s,'RESEARCH',92,423,645,45,26,{bold:true});
title(s,'Explore the\noptions',92,487,645,132,60);
text(s,'Sources and a draft to review.',94,653,634,50,25);
box(s,806,385,724,318,C.mint,3,C.ink);
text(s,'ARCHITECTURE',838,423,652,45,26,{bold:true});
title(s,'Make the\nsolution visible',838,487,652,132,55);
text(s,'Solution diagrams in the workspace.',840,653,640,50,25);
text(s,'I approve the task. Adversaria drafts. I review the result.',64,751,1438,45,28,{bold:true});
foot(s,6);
s.notes='Spaces, called Workspaces in the app, connect meeting context to work. I can approve an action item, research options and create a solution architecture diagram inside the workspace. Then I review the artifact. The diagram and research are drafts for engineering judgment. Web research uses external services when enabled. Human review remains part of the workflow. '+source;

s=S();label(s,'BUILT TODAY     12 SEP 2026');
title(s,'Two ways to use it',60,135,1460,110,94);
box(s,60,305,711,418,C.bg2,3);
text(s,'01   DESKTOP',92,340,632,44,27,{bold:true});
title(s,'Copilot\n+ Spaces',92,407,635,152,68);
text(s,'Extended the companion\nand workspace flow.',96,586,630,105,31,{leading:1.4});
box(s,806,305,724,418,C.ink,3,C.blue);
text(s,'02   TERMINAL',838,340,640,44,27,{bold:true,color:C.mint});
title(s,'Adversaria\nCLI',838,407,645,152,68,C.bg);
text(s,'Cloud speech, models\nand research with my keys.',842,586,640,105,31,{leading:1.4,color:C.bg});
text(s,'CLI: OpenRouter + Exa   /   Optional OpenAI   /   Codex uses its own login',64,755,1450,42,25,{color:C.muted});
foot(s,7);
s.notes='Today I built on the existing Copilot and Spaces foundation, including a compact companion and inline diagram preview. I also built Adversaria CLI: a terminal meeting copilot and work interface. It uses configured provider credentials. OpenRouter handles cloud speech and models, Exa handles web research, and OpenAI is an optional direct model and transcription provider. Codex task execution uses a separate Codex login, not a provider API key. This is a cloud BYOK edition with local storage, not an entirely offline CLI. '+source;

s=S(C.ink);label(s,'WHY I KEEP BUILDING',C.yellow);
title(s,'More room',60,172,1460,148,124,C.bg);
title(s,'to build',60,308,1460,148,124,C.yellow);
text(s,'That’s why I built Adversaria.',66,516,1390,70,43,{color:C.bg});
text(s,'Hamza’s ongoing project at Laghari Labs.',66,611,1410,56,31,{color:C.bg});
box(s,60,708,1465,64,C.ink,2);
text(s,'./adversaria setup     then     ./adversaria',80,721,1420,43,28,{color:C.mint});
foot(s,8,true);
s.notes='The goal is simple: give me more room to do the engineering and personal projects I care about. Adversaria is an ongoing project, and today’s Copilot, Spaces and CLI work move it forward. In a demo, I would first show the local meeting context, then a Copilot commitment, then a research or architecture draft in a workspace. The CLI is another way to use the same idea from the terminal. Setup requires the relevant credentials for the selected cloud providers. '+source;

await fs.mkdir(OUT,{recursive:true});
await fs.writeFile(path.join(ROOT,'.build','deck.json'),JSON.stringify(deck,null,2));
const esc=x=>x.replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
let fontCSS='';
for(const name of fonts){const family=name.startsWith('Silk')?'Silkscreen':'JetBrains Mono',weight=name.split('-')[1];fontCSS+=`@font-face{font-family:'${family}';font-weight:${weight};font-style:normal;font-display:block;src:url(data:font/ttf;base64,${(await fs.readFile(path.join(ROOT,'assets',name+'.ttf'))).toString('base64')}) format('truetype')}\n`;}
const elements=e=>e.kind==='box'?`<div class="shape" style="left:${e.x}px;top:${e.y}px;width:${e.w}px;height:${e.h}px;background:${e.fill};border:${e.border}px solid ${C.ink};${e.shadow?'box-shadow:10px 10px 0 '+e.shadow+';':''}"></div>`:`<div class="txt" style="left:${e.x}px;top:${e.y}px;width:${e.w}px;height:${e.h}px;font:${e.bold?'700':'400'} ${e.size}px '${e.font}';line-height:${e.leading};color:${e.color};text-align:${e.align}" contenteditable="false">${esc(e.str).replaceAll('\n','<br>')}</div>`;
const pages=deck.map((s,i)=>`<section class="slide${i===0?' active':''}" aria-label="Slide ${i+1}" data-notes="${esc(s.notes)}" style="background:${s.bg}">${s.e.map(elements).join('')}</section>`).join('\n');
const licenses=(await fs.readFile(path.join(ROOT,'assets','Silkscreen-OFL.txt'),'utf8'))+'\n'+(await fs.readFile(path.join(ROOT,'assets','JetBrainsMono-OFL.txt'),'utf8'));
const html=`<!DOCTYPE html><html lang="en"><!-- Embedded font licenses: ${licenses} --><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Why I built Adversaria — Hamza / Laghari Labs</title><style>${fontCSS}
*{box-sizing:border-box}body{margin:0;background:#18181F;color:${C.bg};font-family:'JetBrains Mono',monospace}#stage{position:fixed;left:50%;top:calc(50% - 30px);width:1600px;height:900px;transform-origin:center}.slide{position:absolute;width:1600px;height:900px;border:4px solid ${C.ink};overflow:hidden;display:none}.slide.active{display:block}.shape,.txt{position:absolute}.txt{white-space:normal;margin:0;padding:0;outline-offset:4px}.txt[contenteditable=true]{cursor:text}.txt[contenteditable=true]:focus{outline:2px dashed ${C.blue}}.controls{position:fixed;bottom:10px;left:50%;transform:translateX(-50%);display:flex;gap:10px;align-items:center;background:#18181fee;padding:8px 12px;border:1px solid #7e7971;color:${C.bg};font-size:12px;z-index:4}.controls button{font:inherit;background:transparent;color:inherit;border:1px solid #8c8579;padding:6px 9px;cursor:pointer}.controls button:hover{background:#34343f}.notes{display:none;position:fixed;right:20px;bottom:80px;max-width:650px;padding:24px;background:${C.bg};color:${C.ink};border:3px solid ${C.ink};box-shadow:8px 8px 0 ${C.blue};z-index:6;font-size:17px;line-height:1.6}.notes.open{display:block}.hint{opacity:.65}body.clean .controls{display:none}@page{size:1600px 900px;margin:0}@media print{body{background:none}#stage{position:static;transform:none!important;width:1600px;height:auto}.slide{position:relative;display:block!important;break-after:page;page-break-after:always;print-color-adjust:exact;-webkit-print-color-adjust:exact}.controls,.notes{display:none!important}}
</style><body><main id="stage">${pages}</main><aside class="notes" id="notes" aria-live="polite"></aside><nav class="controls" aria-label="Presentation controls"><button id="prev" aria-label="Previous slide">Previous</button><span id="counter">1 / 8</span><button id="next" aria-label="Next slide">Next</button><button id="full">Fullscreen</button><button id="note">Notes</button><button id="edit">Edit text</button><button id="save" hidden>Save HTML</button><span class="hint">← → · F · N</span></nav><script>
const slides=[...document.querySelectorAll('.slide')];let current=Math.max(0,Math.min(slides.length-1,Number(location.hash.slice(1)||1)-1));let editing=false;
function fit(){const k=Math.min((innerWidth-24)/1600,(innerHeight-74)/900);document.querySelector('#stage').style.transform='translate(-50%,-50%) scale('+k+')'}
function show(n){current=Math.max(0,Math.min(slides.length-1,n));slides.forEach((s,i)=>s.classList.toggle('active',i===current));document.querySelector('#counter').textContent=(current+1)+' / '+slides.length;document.querySelector('#notes').textContent=slides[current].dataset.notes;history.replaceState(null,'','#'+(current+1));}
document.querySelector('#prev').onclick=()=>show(current-1);document.querySelector('#next').onclick=()=>show(current+1);document.querySelector('#full').onclick=()=>document.fullscreenElement?document.exitFullscreen():document.documentElement.requestFullscreen();document.querySelector('#note').onclick=()=>document.querySelector('#notes').classList.toggle('open');document.querySelector('#edit').onclick=()=>{editing=!editing;document.querySelectorAll('.txt').forEach(e=>e.contentEditable=String(editing));document.querySelector('#edit').textContent=editing?'Finish editing':'Edit text';document.querySelector('#save').hidden=!editing;};document.querySelector('#save').onclick=()=>{const copy=document.documentElement.cloneNode(true);copy.querySelectorAll('.txt').forEach(e=>e.contentEditable='false');copy.querySelector('#edit').textContent='Edit text';copy.querySelector('#save').hidden=true;const blob=new Blob(['<!DOCTYPE html>'+copy.outerHTML],{type:'text/html'}),a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='adversaria-story-edited.html';a.click();};
addEventListener('keydown',e=>{if(editing)return;if(['ArrowRight','PageDown',' '].includes(e.key)){e.preventDefault();show(current+1)}if(['ArrowLeft','PageUp'].includes(e.key)){e.preventDefault();show(current-1)}if(e.key==='Home')show(0);if(e.key==='End')show(slides.length-1);if(e.key.toLowerCase()==='n')document.querySelector('#note').click();if(e.key.toLowerCase()==='f')document.querySelector('#full').click();if(e.key.toLowerCase()==='h')document.body.classList.toggle('clean');});addEventListener('resize',fit);fit();show(current);
</script></body></html>`;
await fs.writeFile(path.join(OUT,'adversaria-story.html'),html);
await fs.writeFile(path.join(OUT,'presenter-notes.md'),'# Why I built Adversaria\n\n'+deck.map((s,i)=>'## Slide '+(i+1)+'\n\n'+s.notes.replace(source,'').trim()).join('\n\n'));

const pres=Presentation.create({slideSize:{width:W,height:H}});
for(let i=0;i<deck.length;i++){
 const spec=deck[i],slide=pres.slides.add();slide.background.fill=spec.bg;
 // The frame and panels reproduce the supplied brand layout. All copy is native editable text.
 slide.shapes.add({geometry:'rect',name:'Brand frame',position:{left:2,top:2,width:1596,height:896},fill:'none',line:{fill:C.ink,width:4}});
 for(const [j,e] of spec.e.entries()){
  if(e.kind==='box'){
   if(e.shadow)slide.shapes.add({geometry:'rect',name:'Pixel offset shadow',position:{left:e.x+10,top:e.y+10,width:e.w,height:e.h},fill:e.shadow,line:{fill:'none',width:0}});
   slide.shapes.add({geometry:'rect',name:'Brand layout surface',position:{left:e.x,top:e.y,width:e.w,height:e.h},fill:e.fill,line:{fill:e.border?C.ink:'none',width:e.border}});
  }else{
   const sh=slide.shapes.add({geometry:'textbox',name:'Editable '+i+'-'+j,position:{left:e.x,top:e.y,width:e.w,height:e.h},fill:'none',line:{fill:'none',width:0}});
   sh.text=e.str;sh.text.style={typeface:e.font,fontSize:e.size,bold:e.bold,color:e.color,alignment:e.align,verticalAlignment:'top',autoFit:'none',wrap:'none',insets:{top:0,bottom:0,left:0,right:0},lineSpacing:e.leading};
  }
 }
 slide.speakerNotes.textFrame.setText(spec.notes);
 const png=await pres.export({slide,format:'png',scale:1});
 await fs.writeFile(path.join(ROOT,'.build','slide-'+(i+1)+'.png'),new Uint8Array(await png.arrayBuffer()));
}
const candidate=path.join(ROOT,'.build','candidate-v3.pptx');await(await PresentationFile.exportPptx(pres)).save(candidate);
const {finalizePresentation}=await import(SKILL+'/container_tools/artifact_tool_utils.mjs');
const result=await finalizePresentation({workspaceDir:ROOT,candidatePath:candidate,finalPath:path.join(OUT,'adversaria-story-v3.pptx'),pythonExecutable:RUNTIME+'/python/bin/python3',integrityValidatorPath:SKILL+'/container_tools/inspect_presentation_package_integrity.py',layoutValidatorPath:SKILL+'/container_tools/inspect_presentation_layout_geometry.py',layoutArgs:['--expected-slide-size-emu','15240000,8572500','--validate-heading-fit'],requiredNativeTableOwnerSlides:[],requiredNativeChartOwnerSlides:[],fontPolicy:{basis:'design',families:['Silkscreen','JetBrains Mono']},verifyArtifactToolImport:true,receiptPath:path.join(ROOT,'.build','validation-v3.json')});
console.log(JSON.stringify(result));
console.log('OUTPUT '+OUT);
