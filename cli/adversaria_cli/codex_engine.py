"""Run the installed Codex subscription as a draft-producing workspace engine."""

import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from .config import CliError


def generate(system, prompt, model, usage):
    executable = shutil.which("codex")
    if not executable:
        raise CliError(
            "Codex CLI is not installed. Install/login to Codex, or models use openrouter."
        )
    with tempfile.TemporaryDirectory(prefix="adversaria-codex-") as directory:
        output = Path(directory) / "draft.md"
        args = [
            executable,
            "exec",
            "--ignore-user-config",
            "--sandbox",
            "read-only",
            "--skip-git-repo-check",
            "--ephemeral",
            "--json",
            "--color",
            "never",
            "-C",
            directory,
            "-o",
            str(output),
        ]
        if model != "auto":
            args += ["--model", model]
        args.append("-")
        environment = {
            k: v
            for k, v in os.environ.items()
            if k not in {"OPENROUTER_API_KEY", "EXA_API_KEY", "OPENAI_API_KEY"}
        }
        process = subprocess.Popen(
            args,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=environment,
        )
        try:
            stdout, _stderr = process.communicate(
                system
                + "\nUse only the supplied evidence; do not use tools. Return the complete deliverable as your final message.\n\n"
                + prompt,
                timeout=300,
            )
        except BaseException as exc:
            process.terminate()
            try:
                process.communicate(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.communicate()
            if isinstance(exc, subprocess.TimeoutExpired):
                raise CliError("Codex exceeded five minutes; the task can be retried.") from exc
            raise
        completed = False
        for line in stdout.splitlines():
            try:
                event = json.loads(line)
            except ValueError:
                continue
            if event.get("type") == "turn.completed":
                completed = True
                usage.update(event.get("usage") or {})
            elif event.get("type") in {"turn.failed", "error"}:
                raise CliError(
                    "Codex could not complete the run. Check codex login status and remaining credits."
                )
        if (
            process.returncode
            or not completed
            or not output.is_file()
            or not output.read_text().strip()
        ):
            raise CliError(
                "Codex returned no completed draft. Check codex login status; the task remains retryable."
            )
        yield output.read_text()
