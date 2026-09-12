"""Unit tests for the terminal-local SQLite store."""

from __future__ import annotations

from pathlib import Path

from adversaria_terminal.models import Meeting
from adversaria_terminal.storage import Store


def _store(tmp_path: Path) -> Store:
    return Store(tmp_path / "meetings.db")


def test_add_and_get_meeting(tmp_path: Path):
    store = _store(tmp_path)
    m = Meeting(title="Standup", summary="Quick sync", transcript="Hello world.")
    added = store.add_meeting(m)
    assert added.id > 0
    got = store.get_meeting(added.id)
    assert got is not None
    assert got.title == "Standup"
    assert got.transcript == "Hello world."


def test_update_meeting_persists_fields(tmp_path: Path):
    store = _store(tmp_path)
    m = store.add_meeting(Meeting(title="Draft", status="pending"))
    m.status = "done"
    m.title = "Final"
    store.update_meeting(m)
    got = store.get_meeting(m.id)
    assert got is not None
    assert got.title == "Final"
    assert got.status == "done"


def test_list_meetings_orders_most_recent_first(tmp_path: Path):
    store = _store(tmp_path)
    a = store.add_meeting(Meeting(title="Older", recorded_at="2026-01-01T10:00:00+00:00"))
    b = store.add_meeting(Meeting(title="Newer", recorded_at="2026-02-01T10:00:00+00:00"))
    rows = store.list_meetings()
    assert [r.title for r in rows] == [b.title, a.title]


def test_delete_meeting_cascades_action_items(tmp_path: Path):
    store = _store(tmp_path)
    m = store.add_meeting(Meeting(title="With todos", summary="## Action Items\n- Do it"))
    assert store.get_action_items(m.id)
    store.delete_meeting(m.id)
    assert store.get_meeting(m.id) is None
    assert store.get_action_items(m.id) == []


def test_action_items_extracted_from_summary(tmp_path: Path):
    store = _store(tmp_path)
    m = store.add_meeting(
        Meeting(title="Planning", summary="## Action Items\n- Prepare deck\n- Book room")
    )
    items = store.get_action_items(m.id)
    assert [i.text for i in items] == ["Prepare deck", "Book room"]
    assert all(not i.done for i in items)


def test_set_action_done_toggles(tmp_path: Path):
    store = _store(tmp_path)
    m = store.add_meeting(Meeting(title="X", summary="## To-dos\n- Ship feature"))
    item = store.get_action_items(m.id)[0]
    store.set_action_done(item.id, True)
    items = store.get_action_items(m.id)
    assert items[0].done is True
    store.set_action_done(item.id, False)
    assert store.get_action_items(m.id)[0].done is False


def test_list_all_action_items_filters_done(tmp_path: Path):
    store = _store(tmp_path)
    store.add_meeting(Meeting(title="A", summary="## Actions\n- Open task"))
    done_m = store.add_meeting(Meeting(title="B", summary="## Actions\n- Done task"))
    store.set_action_done(store.get_action_items(done_m.id)[0].id, True)
    open_rows = store.list_all_action_items(include_done=False)
    assert [item.text for item, _ in open_rows] == ["Open task"]
    all_rows = store.list_all_action_items(include_done=True)
    assert len(all_rows) == 2


def test_settings_round_trip(tmp_path: Path):
    store = _store(tmp_path)
    assert store.get_setting("nope") is None
    store.set_setting("last_meeting_id", "7")
    assert store.get_setting("last_meeting_id") == "7"
    assert store.get_setting("missing", "dflt") == "dflt"


def test_attendees_json_round_trips(tmp_path: Path):
    store = _store(tmp_path)
    m = store.add_meeting(Meeting(title="T", attendees=["Alice", "Bob"]))
    got = store.get_meeting(m.id)
    assert got is not None
    assert got.attendees == ["Alice", "Bob"]