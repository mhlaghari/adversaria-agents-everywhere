"""Convenience wiring: config -> Store."""

from __future__ import annotations

from .config import AppConfig
from .storage import Store


def open_store(config: AppConfig) -> Store:
    store = Store(config.applied_data_dir() / "meetings.db")
    store.data_dir = config.applied_data_dir()
    return store