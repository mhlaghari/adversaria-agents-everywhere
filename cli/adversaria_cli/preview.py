"""Local artifact previews with a bundled Mermaid renderer and no remote assets."""

from __future__ import annotations

import html
import json
import re
import secrets
import webbrowser
from pathlib import Path

from markdown_it import MarkdownIt

from .config import CliError, atomic_text

CSS = """
*{box-sizing:border-box}
body{margin:0;background:#17212b;color:#e5edf3;font:18px/1.6 Arial,sans-serif}
header{display:flex;align-items:center;justify-content:space-between;gap:20px;
padding:16px 28px;background:#253545;border-bottom:1px solid #415464}
header strong{font:700 18px monospace;color:#79d4e4}
header span{color:#b0bdc9;font-size:14px}
main{max-width:1500px;margin:auto;padding:28px}
h1{font-size:32px;line-height:1.2;margin:12px 0 24px}h2{font-size:22px;margin-top:32px}
p,li{max-width:100ch}a{color:#79d4e4}
blockquote{margin:0 0 22px;padding:12px 18px;background:#253545;color:#c7d4df;font-size:15px}
blockquote p{margin:0}
pre{padding:18px;background:#111a22;white-space:pre-wrap;overflow-wrap:anywhere}
code{font-family:monospace}hr{border:0;border-top:1px solid #415464;margin:40px 0}
.figure{margin:24px 0 36px;border:1px solid #415464;background:#1d2b38}
.figure-head{display:flex;align-items:center;justify-content:space-between;gap:12px;
padding:12px 18px;border-bottom:1px solid #415464}
.figure-head span{color:#b0bdc9;font-size:14px}
.diagram{overflow:auto;padding:24px 12px;min-height:220px}
.diagram svg{width:100%;min-width:900px;height:auto;display:block;margin:auto}
button{border:1px solid #79d4e4;background:#79d4e4;color:#17212b;font:700 14px Arial,sans-serif;
padding:10px 16px;border-radius:4px;cursor:pointer}
button:disabled{opacity:.5;cursor:wait}
button:focus-visible,summary:focus-visible,a:focus-visible{outline:3px solid #ffbcad;outline-offset:4px}
details{border-top:1px solid #415464;padding:12px 18px;font-size:14px}
summary{cursor:pointer;color:#b0bdc9}
.error{color:#ffbcad;padding:18px}
footer{color:#b0bdc9;font-size:13px;margin-top:40px}
@media(max-width:600px){main{padding:16px}header{padding:14px 16px}h1{font-size:26px}}
@media print{body{background:white;color:black}header,button,details{display:none}
.figure{break-inside:avoid}.diagram svg{min-width:0}main{padding:0}}
"""

SCRIPT = """
mermaid.initialize({
  startOnLoad:false, securityLevel:"strict", theme:"base", look:"classic",
  fontFamily:"Arial, sans-serif",
  flowchart:{htmlLabels:false,curve:"basis",nodeSpacing:45,rankSpacing:55},
  themeVariables:{
    background:"#1d2b38",primaryColor:"#253545",primaryTextColor:"#e5edf3",
    primaryBorderColor:"#79d4e4",lineColor:"#79d4e4",secondaryColor:"#253545",
    tertiaryColor:"#17212b",edgeLabelBackground:"#1d2b38",fontSize:"18px"
  }
});
for (const [index, source] of diagrams.entries()) {
  const target=document.getElementById("diagram-"+index);
  const status=document.getElementById("status-"+index);
  const button=document.getElementById("download-"+index);
  try {
    const result=await mermaid.render("rendered-"+index,source);
    target.innerHTML=result.svg;
    status.textContent="Rendered diagram";
    button.disabled=false;
    button.onclick=()=>{
      const blob=new Blob([result.svg],{type:"image/svg+xml;charset=utf-8"});
      const url=URL.createObjectURL(blob);
      const link=document.createElement("a");
      link.href=url;link.download="task-"+taskId+"-diagram-"+(index+1)+".svg";
      link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
    };
  } catch (error) {
    target.textContent="This diagram could not be rendered. Open Mermaid source below, or request a revision in the CLI.";
    target.classList.add("error");status.textContent="Diagram needs a revision";
    console.error(error);
  }
}
document.documentElement.dataset.previewReady="true";
"""


def build_preview(store, task_id):
    task = store.task(task_id)
    artifact = store.artifact(task_id)
    markdown = artifact.read_text(encoding="utf-8")
    if len(markdown) > 2_000_000:
        raise CliError("This artifact is too large for a browser preview.")
    diagrams = []
    renderer = MarkdownIt("commonmark", {"html": False})
    default_fence = renderer.renderer.rules["fence"]

    def fence(tokens, idx, options, env):
        token = tokens[idx]
        if token.info.strip().lower() != "mermaid":
            return default_fence(tokens, idx, options, env)
        # Diagram input cannot override the local viewer's rendering/security config.
        source = re.sub(r"%%\{.*?\}%%", "", token.content, flags=re.DOTALL)
        source = re.sub(r"\A\s*---\s*\n.*?\n---\s*\n", "", source, flags=re.DOTALL)
        index = len(diagrams)
        diagrams.append(source)
        return (
            '<section class="figure" aria-label="Diagram preview">'
            f'<div class="figure-head"><span id="status-{index}" role="status">Rendering diagram…</span>'
            f'<button id="download-{index}" disabled>Download SVG</button></div>'
            f'<div class="diagram" id="diagram-{index}"></div>'
            "<details><summary>Mermaid source</summary><pre>"
            + html.escape(source)
            + "</pre></details></section>"
        )

    renderer.renderer.rules["fence"] = fence
    content = renderer.render(markdown)
    nonce = secrets.token_urlsafe(24)
    policy = (
        "default-src 'none'; "
        f"script-src 'nonce-{nonce}'; "
        "style-src 'unsafe-inline'; img-src data: blob:; font-src data:; "
        "connect-src 'none'; base-uri 'none'; form-action 'none'"
    )
    scripts = ""
    if diagrams:
        vendor = Path(__file__).with_name("vendor") / "mermaid.tiny.js"
        if not vendor.is_file():
            raise CliError("The Mermaid renderer is missing. Reinstall the Adversaria CLI.")
        bundle = re.sub(r"</script", r"<\\/script", vendor.read_text(), flags=re.IGNORECASE)
        data = json.dumps(diagrams).replace("<", "\\u003c")
        scripts = (
            f'<script nonce="{nonce}">{bundle}</script>'
            f'<script type="module" nonce="{nonce}">const diagrams={data};const taskId={int(task_id)};'
            + SCRIPT
            + "</script>"
        )
    title = html.escape(task["title"])
    document = (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        f'<meta http-equiv="Content-Security-Policy" content="{html.escape(policy, quote=True)}">'
        f"<title>{title} · Adversaria</title><style>{CSS}</style></head><body>"
        f"<header><strong>ADVERSARIA</strong><span>Task {int(task_id)} · "
        + html.escape(task["workspace"])
        + "</span></header><main>"
        + content
        + "<footer>Local artifact preview · original Markdown remains saved alongside this page.</footer>"
        + "</main>"
        + scripts
        + "</body></html>"
    )
    path = artifact.with_name("preview.html")
    atomic_text(path, document)
    return path


def open_preview(store, task_id, *, launch=True):
    path = build_preview(store, task_id)
    if launch and not webbrowser.open(path.as_uri()):
        raise CliError(f"Preview saved at {path}. Open this file in your browser.")
    return path
