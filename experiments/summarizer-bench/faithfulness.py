#!/usr/bin/env python3
"""Objective attendee-faithfulness check.

A listed attendee is legitimate if the name appears EITHER in the transcript
OR in the bundle's `attendees` METADATA field — the app feeds that field to its
summarizer, so a name there is real even when the (garbled) transcript never
spells it. v1 of this script checked ONLY the transcript and wrongly flagged
real metadata attendees as "fabricated" (caught by Hamza 2026-07-19: Dr.Hend/
Jamshed/Alaa etc. ARE real attendees in the metadata). This version loads the
matching bundle's attendees too.

Usage: python3 faithfulness.py results-real real-bundles
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

# Words that look like capitalized names but are roles/labels/section words —
# never counted as a fabricated attendee.
STOPWORDS = {
    "Me", "Them", "Speaker", "None", "Key", "Topics", "Discussed", "Decisions",
    "Made", "Action", "Items", "Follow", "Ups", "Follow-ups", "Needed", "The",
    "A", "An", "Attendees", "Meeting", "Notes", "Summary", "Title", "Role",
    "Company", "Unknown", "Both", "Team", "Doctor", "Dr", "Mr", "Ms", "Mrs",
    "AI", "ML", "US", "UK", "PhD", "TRL", "SDG", "SDGs", "CTO", "CEO",
}

NAME = re.compile(r"\b([A-Z][a-z]{2,}(?:\.[A-Z][a-z]+)?)\b")


def attendee_line_names(summary: str) -> set[str]:
    """Names the summary presents as attendees (from an Attendees line/section)."""
    names: set[str] = set()
    for line in summary.splitlines():
        low = line.lower()
        if "attendee" in low or low.strip().startswith("- **") and "attendee" in low:
            for m in NAME.findall(line):
                if m not in STOPWORDS:
                    names.add(m)
    return names


def source_has(name: str, sources: str) -> bool:
    base = name.split(".")[-1]  # "Dr.Hend" → "Hend"
    return re.search(rf"\b{re.escape(base)}\b", sources, re.IGNORECASE) is not None


def bundle_attendees(bundles_dir: Path, meeting_dir_name: str) -> str:
    """Concatenated attendee metadata for the bundle matching this meeting dir."""
    for b in bundles_dir.glob("*.json"):
        if b.stem.replace(".adversaria", "") == meeting_dir_name:
            try:
                m = json.loads(b.read_text())
                m = m.get("meeting", m)
                return " ".join(m.get("attendees", []) or [])
            except (json.JSONDecodeError, AttributeError):
                return ""
    return ""


def main() -> None:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else "results-real")
    bundles = Path(sys.argv[2] if len(sys.argv) > 2 else "real-bundles")
    rows: list[tuple[str, str, int, int, str]] = []
    for meeting in sorted(root.iterdir()):
        tpath = meeting / "transcript.txt"
        if not tpath.exists():
            continue
        # Legitimate names live in the transcript OR the attendees metadata.
        transcript = tpath.read_text() + "\n" + bundle_attendees(bundles, meeting.name)
        for cand in sorted(meeting.glob("*.md")):
            if cand.name in ("JUDGE_ME.md",):
                continue
            cond = cand.stem
            names = attendee_line_names(cand.read_text())
            fabricated = sorted(n for n in names if not source_has(n, transcript))
            rows.append((meeting.name[:34], cond, len(names), len(fabricated),
                         ", ".join(fabricated) or "—"))

    # Aggregate fabrication rate per condition.
    agg: dict[str, list[int]] = {}
    for _m, cond, _listed, fab, _f in rows:
        agg.setdefault(cond, []).append(fab)

    print("\n=== FABRICATED ATTENDEES per condition (lower = more faithful) ===")
    for cond in sorted(agg, key=lambda c: sum(agg[c])):
        total = sum(agg[cond])
        print(f"  {cond:<32} {total} fabricated across {len(agg[cond])} meetings")

    print("\n=== per-summary detail (only rows WITH fabrications) ===")
    for m, cond, listed, fab, flist in rows:
        if fab:
            print(f"  {m:<34} {cond:<28} {fab}/{listed} fabricated: {flist}")


if __name__ == "__main__":
    main()
