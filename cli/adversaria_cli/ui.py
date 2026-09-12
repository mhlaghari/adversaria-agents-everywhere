"""Terminal output: do not interpret model/source text as terminal control codes."""

import re
import sys

from rich.console import Console
from rich.markdown import Markdown
from rich.table import Table

console = Console(highlight=False)


def safe(text):
    # CSI/OSC and remaining control characters, including DEL/C1/bidi controls.
    text = re.sub(r"\x1b\][^\x07]*(?:\x07|\x1b\\)", "", str(text))
    text = re.sub(r"\x1b\[[0-?]*[ -/]*[@-~]", "", text)
    return "".join(
        c
        for c in text
        if c in "\n\t"
        or (
            ord(c) >= 32
            and not 127 <= ord(c) <= 159
            and not 0x202A <= ord(c) <= 0x202E
            and not 0x2066 <= ord(c) <= 0x2069
        )
    )


def say(text, style=None):
    console.print(safe(text), style=style, markup=False)


def table(rows, columns):
    tab = Table(box=None, padding=(0, 2), expand=False)
    for label, _ in columns:
        tab.add_column(label, style="cyan" if label == "ID" else None)
    for row in rows:
        tab.add_row(*(safe(row.get(key, "")) for _, key in columns))
    console.print(tab)


def show_markdown(text):
    console.print(Markdown(safe(text)))


def render_stream(tokens):
    # Drop ESC itself before writing chunks, so even a control sequence split
    # across model tokens cannot activate a terminal escape.
    chunks = []
    try:
        for token in tokens:
            chunks.append(token)
            sys.stdout.write(safe(token))
            sys.stdout.flush()
    finally:
        sys.stdout.write("\n")
        sys.stdout.flush()
        tokens.close()
    return "".join(chunks)
