"""HTTP and streaming framing shared by the service, OpenRouter, and Exa."""

from __future__ import annotations

import json

import httpx

from .config import CliError


def client(timeout=180.0) -> httpx.Client:
    # No ambient proxy or redirects: local meeting data stays on loopback,
    # provider credentials only go to the fixed first-party host.
    return httpx.Client(
        timeout=httpx.Timeout(timeout, connect=5), trust_env=False, follow_redirects=False
    )


def check(response: httpx.Response):
    if response.is_success:
        return
    # Provider bodies can echo request text/keys; do not print them.
    hints = {
        401: "credential rejected; run auth",
        403: "key lacks access",
        402: "credits exhausted",
        429: "rate limited; retry later",
        404: "endpoint or model unavailable",
        503: "service/model is not ready",
    }
    raise CliError(
        f"{response.url.host}: HTTP {response.status_code} "
        f"({hints.get(response.status_code, 'request failed')})"
    )


def request(method, url, **kwargs):
    try:
        with client(kwargs.pop("timeout", 180.0)) as http:
            response = http.request(method, url, **kwargs)
            check(response)
            return response.json()
    except httpx.HTTPError as exc:
        raise CliError(
            f"Cannot reach {httpx.URL(url).host}. Check the service/network ({type(exc).__name__})."
        ) from exc
    except ValueError as exc:
        raise CliError("The service returned invalid JSON.") from exc


def sse_events(lines):
    """SSE comments, CRLF and multiline data; a final unterminated frame is valid."""
    data = []
    for line in lines:
        if not line:
            if data:
                yield "\n".join(data)
                data = []
        elif line.startswith("data:"):
            data.append(line[5:].lstrip(" "))
    if data:
        yield "\n".join(data)


def stream(url, payload, headers=None, *, ollama=False, responses=False, usage=None):
    done = False
    emitted = False
    try:
        with client() as http, http.stream("POST", url, json=payload, headers=headers) as response:
            check(response)
            events = response.iter_lines() if ollama else sse_events(response.iter_lines())
            for raw in events:
                if not raw:
                    continue
                if raw == "[DONE]":
                    done = True
                    break
                frame = json.loads(raw)
                if frame.get("error"):
                    raise CliError(
                        "The model reported a stream error. Partial output was not accepted; retry the run."
                    )
                if usage is not None:
                    if frame.get("model"):
                        usage["model"] = frame["model"]
                    if frame.get("usage"):
                        usage.update(frame["usage"])
                if responses:
                    kind = frame.get("type")
                    if kind in {"error", "response.failed", "response.incomplete"}:
                        raise CliError(
                            "OpenAI did not complete the response; retry or select another model."
                        )
                    token = frame.get("delta", "") if kind == "response.output_text.delta" else ""
                    if kind == "response.completed":
                        done = True
                        if usage is not None:
                            receipt = frame.get("response", {})
                            usage.update(receipt.get("usage") or {})
                            usage["model"] = receipt.get("model", usage.get("model"))
                elif ollama:
                    token = frame.get("message", {}).get("content", "")
                    done = bool(frame.get("done"))
                    if done and usage is not None:
                        usage.update(
                            {
                                "prompt_tokens": frame.get("prompt_eval_count", 0),
                                "completion_tokens": frame.get("eval_count", 0),
                            }
                        )
                else:
                    choices = frame.get("choices") or []
                    token = frame.get("t", "") or (
                        choices[0].get("delta", {}).get("content") or "" if choices else ""
                    )
                    if choices and choices[0].get("finish_reason") in {
                        "length",
                        "content_filter",
                        "error",
                    }:
                        raise CliError(
                            "The model stopped before completing its answer. Try another model or a smaller brief."
                        )
                if token:
                    emitted = True
                    yield token
                if (ollama or responses) and done:
                    break
    except httpx.HTTPError as exc:
        raise CliError(
            f"Model connection interrupted ({type(exc).__name__}); retry the run."
        ) from exc
    except (ValueError, KeyError, TypeError) as exc:
        raise CliError("Malformed model stream; partial output was not accepted.") from exc
    if not done or not emitted:
        raise CliError("Model stream ended without a complete answer; retry the run.")
