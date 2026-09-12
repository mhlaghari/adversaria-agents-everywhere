"""Complete-turn detection and ephemeral commitment approvals."""

import re
import time
import uuid
from dataclasses import dataclass

VERBS = r"send|share|prepare|write|draft|check|look into|find out|book|schedule|set up|follow up|circulate|review|update|create|put together|get|ask|confirm|draw up|draw|sketch|build|make|map out|diagram"
PREFIX = r"i'll|i will|i can|i could|i'm going to|i am going to|let me|we'll|we will|we need to|we should|we have to|let's|lets|i"
COMMIT = re.compile(
    rf"^(?:{PREFIX})\s+(?:{VERBS})\b|\b(?:action item|to[- ]?do|follow[- ]?up)\s*[:\-]\s*\S",
    re.IGNORECASE,
)
DEADLINE = re.compile(
    r"\b(?:by|before|on)\s+(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday|tomorrow|today|tonight|end of (?:the )?(?:day|week|month)|eod|eow|next week)\b",
    re.IGNORECASE,
)
QUESTION = re.compile(
    r"^(?:what|why|how|when|where|who|which|can you|could you|would you|do you|does|is it|are we|tell me|explain|walk me through)\b",
    re.IGNORECASE,
)


def capability(text):
    if re.search(
        r"\b(diagram|draw|drawing|sketch|chart|flowchart|visuali[sz]e|mock ?up|wireframe|solutions architecture|system design)\b",
        text,
        re.IGNORECASE,
    ):
        return "visualize"
    if re.search(r"\b(deck|slides?|presentation)\b", text, re.IGNORECASE):
        return "present"
    action = re.sub(
        rf"^(?:{PREFIX})\s+|^(?:action item|to[- ]?do|follow[- ]?up)\s*[:\-]\s*",
        "",
        text,
        flags=re.IGNORECASE,
    )
    return (
        "research"
        if re.match(
            r"(?:check|look into|find out|review|confirm|ask|research)\b", action, re.IGNORECASE
        )
        else "write"
    )


@dataclass
class Commitment:
    id: str
    text: str
    kind: str
    source: str
    deadline: str | None
    origin: str
    status: str = "caught"
    task_id: int | None = None


class Copilot:
    def __init__(self):
        self.session = uuid.uuid4().hex
        self.pending = {}
        self.turns = []
        self.commitments = {}
        self.seen = {}

    def feed(self, text, source="Me", boundary="silence"):
        text = text.strip().replace("’", "'")
        if not text and not (boundary == "silence" and self.pending.get(source)):
            return None, None
        combined = " ".join(filter(None, [self.pending.pop(source, ""), text]))
        # Timed ASR fragments can already contain a complete question. Do not make
        # it wait for a silence event that noisy microphone input may never produce.
        if boundary != "silence" and not combined.endswith("?"):
            self.pending[source] = combined
            return None, None
        self.turns.append(f"{source}: {combined}")
        self.turns = self.turns[-8:]
        stamp = time.monotonic()
        self.seen = {key: at for key, at in self.seen.items() if stamp - at < 60}
        key = re.sub(r"[^\w\s]", "", combined.lower())
        key = " ".join(key.split())
        if key in self.seen:
            return None, None
        self.seen[key] = stamp
        commitment = None
        if not combined.endswith("?") and COMMIT.search(combined):
            cid = f"c{len(self.commitments) + 1}"
            deadline = DEADLINE.search(combined)
            commitment = Commitment(
                cid,
                combined,
                capability(combined),
                source,
                deadline.group() if deadline else None,
                f"{self.session}:{cid}",
            )
            self.commitments[cid] = commitment
        question = combined if combined.endswith("?") or QUESTION.match(combined) else None
        return commitment, question
