"""Cloud model catalog and providers: OpenRouter chat, OpenAI Responses."""

from .config import CliError
from .transport import request, stream

OPENROUTER = "https://openrouter.ai/api/v1"
OPENAI = "https://api.openai.com/v1"


class Models:
    def __init__(self, config):
        self.config = config
        self.usage = {}

    def catalog(self, provider="openrouter"):
        if provider == "codex":
            return [{"id": "auto", "context": "Codex CLI default; explicit --model also supported"}]
        if provider == "openai":
            if not self.config.key("openai"):
                raise CliError("OpenAI needs a key: adversaria auth openai (or OPENAI_API_KEY).")
            return [
                {"id": row["id"]}
                for row in request(
                    "GET",
                    OPENAI + "/models",
                    headers={"Authorization": "Bearer " + self.config.key("openai")},
                    timeout=20,
                ).get("data", [])
            ]
        if provider == "openrouter":
            rows = request("GET", OPENROUTER + "/models", timeout=20).get("data", [])
            return [
                {
                    "id": r["id"],
                    "context": r.get("context_length"),
                    "input_per_million": float(r.get("pricing", {}).get("prompt", 0)) * 1e6,
                    "output_per_million": float(r.get("pricing", {}).get("completion", 0)) * 1e6,
                }
                for r in rows
                if "text" in r.get("architecture", {}).get("output_modalities", ["text"])
                and not r["id"].endswith(":batch")
            ]
        raise CliError("Choose openrouter or openai.")

    def resolve(self, provider, model):
        if provider == "codex":
            import shutil

            if not shutil.which("codex"):
                raise CliError("Codex CLI is not installed; choose OpenRouter or install Codex.")
            return model
        if provider == "openai":
            if not self.config.key("openai"):
                raise CliError("OpenAI needs a key: adversaria auth openai (or OPENAI_API_KEY).")
            if model == "auto":
                # Explicit stable default, verified against /models before first use.
                model = "gpt-6-astra"
                if model not in {r["id"] for r in self.catalog("openai")}:
                    raise CliError(
                        "Choose an available OpenAI text model with models use openai MODEL."
                    )
            return model
        if provider == "openrouter":
            if not self.config.key("openrouter"):
                raise CliError(
                    "OpenRouter needs a key: adversaria auth openrouter (or OPENROUTER_API_KEY)."
                )
            return "openrouter/auto" if model == "auto" else model
        raise CliError("Choose openrouter or openai with models use.")

    def generate(self, system, prompt, provider=None, model=None):
        provider, chosen = self.config.selection(provider, model)
        chosen = self.resolve(provider, chosen)
        self.usage = {"provider": provider, "model": chosen}
        messages = [{"role": "system", "content": system}, {"role": "user", "content": prompt}]
        if provider == "codex":
            from .codex_engine import generate

            yield from generate(system, prompt, chosen, self.usage)
        elif provider == "openai":
            yield from stream(
                OPENAI + "/responses",
                {
                    "model": chosen,
                    "instructions": system,
                    "input": prompt,
                    "stream": True,
                    "store": False,
                    "max_output_tokens": 8192,
                },
                {"Authorization": "Bearer " + self.config.key("openai")},
                responses=True,
                usage=self.usage,
            )
        elif provider == "openrouter":
            yield from stream(
                OPENROUTER + "/chat/completions",
                {"model": chosen, "messages": messages, "stream": True, "max_tokens": 4096},
                {
                    "Authorization": "Bearer " + self.config.key("openrouter"),
                    "X-Title": "Adversaria CLI",
                },
                usage=self.usage,
            )
