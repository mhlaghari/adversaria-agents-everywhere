# Track A Handoff: Python ML Service

**Scope:** Tasks 2–5 — Transcriber, Summarizer, FastAPI server, smoke test.

**Dependencies satisfied:** Task 1 complete — Pydantic models in
`python-service/src/models.py`, types defined, project scaffold ready.

**Output:** A working Python service on `localhost:9876` that accepts audio
files, transcribes them with faster-whisper, and summarizes transcripts with
Ollama using configurable prompt templates.

## Files to create/modify

| File | Purpose |
|------|---------|
| `python-service/src/transcriber.py` | faster-whisper wrapper |
| `python-service/src/summarizer.py` | Ollama summarization with templates |
| `python-service/src/server.py` | FastAPI app wiring /transcribe, /summarize, /health, /templates |
| `python-service/tests/test_transcriber.py` | Unit tests (mocked whisper) |
| `python-service/tests/test_summarizer.py` | Unit tests (mocked ollama) |
| `python-service/tests/test_server.py` | Integration tests (httpx + test client) |
| `python-service/src/__init__.py` | Package marker (exists) |

## Config

```
WHISPER_MODEL = "large-v3" (int8, runs on RTX 5090)
OLLAMA_MODEL = "llama3.1:8b"
OLLAMA_BASE_URL = "http://localhost:11434"
HOST = "127.0.0.1"
PORT = 9876
```

## Task breakdown

### Task 2: Transcriber Module
- `python-service/src/transcriber.py` — `WhisperTranscriber` class
  - `__init__`: loads faster-whisper model (large-v3, int8, cuda)
  - `transcribe(audio_path: str) -> TranscribeResponse`: returns text, language, duration
  - `transcribe_bytes(audio: bytes) -> TranscribeResponse`: for raw bytes
- Tests in `python-service/tests/test_transcriber.py`
  - Mock `faster_whisper.WhisperModel` — test shape of response
  - Test with a tiny real audio file if available

### Task 3: Summarizer Module
- `python-service/src/summarizer.py` — `OllamaSummarizer` class
  - `__init__`: configures ollama client, caches templates
  - `_load_template(name: str) -> str`: reads from `prompts/{name}.md`
  - `summarize(transcript: str, template_name: str) -> SummarizeResponse`
  - `list_templates() -> list[TemplateInfo]`
- Tests in `python-service/tests/test_summarizer.py`
  - Mock `ollama.Client` — test template loading, summarize call shape

### Task 4: FastAPI Server
- `python-service/src/server.py` — FastAPI app
  - `POST /transcribe` — multipart file upload → TranscribeResponse
  - `POST /summarize` — JSON body (SummarizeRequest) → SummarizeResponse
  - `GET /health` — HealthResponse
  - `GET /templates` — list[TemplateInfo]
  - `GET /templates/{name}` — raw template content
  - Lifespan: init whisper + ollama at startup, clean up at shutdown
- Tests in `python-service/tests/test_server.py`
  - Use `httpx.AsyncClient` + FastAPI `TestClient` (or lifepan test)
  - Test all 5 endpoints

### Task 5: Smoke Test
- Starting from a clean state, verify:
  1. `python-service/` has all source files + prompt templates
  2. `python -c "from src.models import TranscribeResponse"` works
  3. Server starts with `uvicorn src.server:app` (or script)
  4. Health endpoint responds
  5. Templates endpoint returns 3 templates

## API contracts (from Task 1)

Models live in `python-service/src/models.py`:

```python
class SummarizeRequest(BaseModel):
    transcript: str
    template_name: str = "general"

class TranscribeResponse(BaseModel):
    text: str
    language: str
    duration_seconds: float

class SummarizeResponse(BaseModel):
    summary: str
    template_used: str

class TemplateInfo(BaseModel):
    name: str
    description: str

class HealthResponse(BaseModel):
    status: str
    whisper_model: str
    ollama_available: bool
```

## Execution order

Tasks must run sequentially: **2 → 3 → 4 → 5**.
Commit after each task (TDD: test first, then implement, then commit).

## Self-review checklist (per task)

- [ ] Tests written first, they fail, then implementation makes them pass
- [ ] No `print()` — use `logging`
- [ ] Type annotations on all function signatures
- [ ] Error handling: graceful degradation if Ollama/whisper unavailable
- [ ] Audio files deleted after transcription
- [ ] All endpoints return proper models (match contracts)
