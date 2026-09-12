# OpenRouter speech: verified recipe (2026-09-12 14:51)

> **Historical investigation, superseded.** Later successful STT requests are
> recorded in [cli/PROVIDER_CHECK.md](../cli/PROVIDER_CHECK.md). The early
> conclusion below that OpenRouter has no transcription endpoint is incorrect.
> Use [the current CLI guide](../cli/README.md) for the implemented provider path.

OpenRouter has NO speech-to-text endpoint: `/api/v1/audio/transcriptions` returns 401 "User not found" even with a valid key, and the catalog (445 models) has no transcribe/whisper model; `openai/gpt-transcribe` does not exist there. What works is an audio-input chat model.

Verified with a 16 kHz mono WAV (two sentences) and a valid key:

| model | params | latency | result |
|---|---|---|---|
| `google/gemini-3.8-flash` | `reasoning: {effort: "low"}`, `max_tokens: 600` | 3.1 s | verbatim, 22 output tokens |
| `google/gemini-3.7-flash` | same | 3.6 s | verbatim |
| `meta/muse-spark-1.3` | | 403 | needs 18+ attestation on openrouter.ai/settings/preferences |

Reasoning cannot be disabled (`reasoning.enabled=false` and `effort:"none"` both 400 "Reasoning is mandatory"); with `max_tokens` 60 the answer was truncated because thinking eats the budget. Use `max_tokens >= 400`.

Request shape (OpenAI-compatible `input_audio` content part):

```python
body = {
  "model": "google/gemini-3.8-flash",
  "reasoning": {"effort": "low"},
  "max_tokens": 600,
  "messages": [{"role": "user", "content": [
      {"type": "text", "text": "Transcribe this audio verbatim. Output only the spoken words."},
      {"type": "input_audio", "input_audio": {"data": base64_wav, "format": "wav"}}]}],
}
# POST https://openrouter.ai/api/v1/chat/completions, Authorization: Bearer <key>
```

For live captions: send each silence-bounded chunk (2 to 6 s, 16 kHz mono WAV) as its own request; 3 s round trip per chunk was measured. Emit the chunk as a final caption; no partials from this path.
