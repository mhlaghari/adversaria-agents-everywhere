from html.parser import HTMLParser

import pytest

from adversaria_cli.config import CliError
from adversaria_cli.demo import seed_demo
from adversaria_cli.preview import build_preview, open_preview


class Elements(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))


def test_diagram_preview_is_local_and_keeps_the_artifact_and_review_state(env, monkeypatch):
    config, store, _ = env
    _, tasks = seed_demo(config, store)
    task = next(t for t in tasks if t["kind"] == "visualize")
    artifact = store.artifact(task["id"])
    original = artifact.read_bytes()
    opened = []
    monkeypatch.setattr(
        "adversaria_cli.preview.webbrowser.open", lambda url: opened.append(url) or True
    )
    preview = open_preview(store, task["id"])
    assert preview.parent == artifact.parent and preview.name == "preview.html"
    page = preview.read_text()
    assert "Download SVG" in page and "Prepared demo fixture" in page
    assert "flowchart LR" in page and 'securityLevel:"strict"' in page
    tags = Elements()
    tags.feed(page)
    scripts = [attrs for tag, attrs in tags.tags if tag == "script"]
    assert len(scripts) == 2 and all("src" not in attrs for attrs in scripts)
    assert all(attrs.get("nonce") for attrs in scripts)
    assert "connect-src" in page
    assert opened == [preview.as_uri()]
    assert store.task(task["id"])["status"] == "awaiting_review"
    assert artifact.read_bytes() == original


def test_preview_escapes_html_and_diagram_script_breakouts(env):
    config, store, _ = env
    _, tasks = seed_demo(config, store)
    task = next(t for t in tasks if t["kind"] == "visualize")
    artifact = store.artifact(task["id"])
    fence = "\x60" * 3
    artifact.write_text(
        '<script>alert("html")</script>\n\n' + fence + "mermaid\n"
        '%%{init: {"securityLevel": "loose"}}%%\n'
        'flowchart LR\nA["</script><script>alert(1)</script>"] --> B["Safe"]\n' + fence + "\n"
    )
    preview = build_preview(store, task["id"])
    page = preview.read_text()
    tags = Elements()
    tags.feed(page)
    scripts = [attrs for tag, attrs in tags.tags if tag == "script"]
    assert len(scripts) == 2 and all(attrs.get("nonce") for attrs in scripts)
    assert '<script>alert("html")</script>' not in page
    assert '%%{init: {"securityLevel": "loose"}}%%' not in page


def test_document_preview_and_missing_artifact_errors(env, monkeypatch):
    config, store, _ = env
    _, tasks = seed_demo(config, store)
    document = next(t for t in tasks if t["kind"] == "present")
    preview = open_preview(store, document["id"], launch=False)
    page = preview.read_text()
    assert "<h2>Slide 1" in page and "<hr" in page
    assert 'id="diagram-' not in page
    queued = next(t for t in tasks if t["status"] == "queued")
    with pytest.raises(CliError, match="No completed artifact"):
        build_preview(store, queued["id"])
    monkeypatch.setattr("adversaria_cli.preview.webbrowser.open", lambda url: False)
    with pytest.raises(CliError, match="Preview saved at"):
        open_preview(store, document["id"])
