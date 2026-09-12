# Provider checks — 12 September 2026

Validation used the user's configured keys without displaying or copying them
into this repository. Requests contained synthetic speech or public test queries.

| Check | Result |
| --- | --- |
| OpenRouter current-key endpoint | HTTP 200, paid account |
| Exa search | HTTP 200, one result, 1.22 seconds |
| OpenRouter `openai/gpt-4o-mini-transcribe` | HTTP 200, correct sample text, 1.25 seconds |
| OpenRouter `openai/gpt-transcribe` | HTTP 200, correct sample text, 1.28 seconds |
| OpenRouter `nvidia/nemotron-3.5-asr-streaming-multilingual-0.6b` | HTTP 200, completed JSON, 2.48 seconds |
| OpenRouter `openai/whisper-large-v3-turbo` | HTTP 200, correct sample text, 2.80 seconds |
| OpenRouter `google/gemini-2.5-flash-lite` | First text token 0.91 seconds; complete 1.07 seconds |
| OpenRouter `openai/gpt-5.4-nano` | First text token 1.12 seconds; complete 1.39 seconds |
| OpenRouter `openai/gpt-4.1-mini` | First text token 1.15 seconds; complete 1.46 seconds |

These are individual requests from this machine, not benchmarks or latency promises.
The configured speech model is `openai/gpt-4o-mini-transcribe`; Copilot uses
`google/gemini-2.5-flash-lite` on OpenRouter. Exa is used by `search QUERY`.
No local model or separate OpenAI API key was used in these checks.

The production ASR → dashboard → Copilot path was then exercised with a generated
spoken sample: “Hey, what's happening? What is an LLM?” It produced the complete
transcript at 4.11 seconds and an answer defining LLM at 5.34 seconds from sample
playback start. This used real provider requests and isolated, synthetic workspace
data. It did not capture the microphone or upload a real meeting.

A two-second chunk trial cut the final question across requests and lost its
meaning. Four-second fragments are retained for context; 400 ms silence closes
shorter turns. ASR requests run on two workers and emit in audio order. A complete
question ending in `?` triggers Copilot even before a silence boundary, fixing the
reported empty suggestions pane. Incomplete commitments still await turn closure.

[OpenRouter's documented STT API](https://openrouter.ai/docs/guides/overview/multimodal/stt)
returns a JSON transcription for supplied audio. No live WebSocket ASR transport
was found in its documentation index. A model named “streaming” still returned
completed JSON through the tested endpoint. The CLI streams chat tokens and
updates ASR captions per completed chunk; it does not claim word-by-word ASR.
