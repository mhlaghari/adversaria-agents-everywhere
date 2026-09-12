import httpx
import pytest

from adversaria_cli.config import Config
from adversaria_cli.engine import Engine
from adversaria_cli.store import Store


@pytest.fixture
def env(tmp_path, monkeypatch):
    for key in ("OPENAI_API_KEY", "OPENROUTER_API_KEY", "EXA_API_KEY"):
        monkeypatch.delenv(key, raising=False)
    config = Config(tmp_path / "state")
    store = Store(config.directory)
    return config, store, Engine(config, store)


@pytest.fixture
def http_mock(monkeypatch):
    def install(handler):
        monkeypatch.setattr(
            "adversaria_cli.transport.client",
            lambda *a, **kw: httpx.Client(
                transport=httpx.MockTransport(handler), follow_redirects=False
            ),
        )

    return install
