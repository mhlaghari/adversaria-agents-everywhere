import json

import pytest

from adversaria_cli.demo import NOTICE, seed_demo
from adversaria_cli.main import execute, parser


def test_demo_seeds_current_workspace_without_touching_real_work_or_provider_settings(
    env, monkeypatch
):
    config, store, engine = env
    config.save(workspace="Interviews", provider="openrouter", model="chosen-model")
    workspace = engine.workspace()
    store.configure_workspace(workspace["id"], instructions="Existing guidance", paused=True)
    real_task = store.add_task(workspace["id"], "A real task", "write")
    other = store.workspace("Other")
    other_task = store.add_task(other["id"], "Unrelated task", "research")
    settings = dict(config.values)

    def reject_key_read(*args):
        raise AssertionError("Prepared fixtures must not read credentials or call providers")

    monkeypatch.setattr(config, "key", reject_key_read)
    assert execute(parser().parse_args(["demo"]), config, store, engine) == 0
    tasks = store.rows("SELECT * FROM tasks WHERE origin LIKE 'adversaria-demo:%'")
    assert len(tasks) == 5
    assert {t["workspace_id"] for t in tasks} == {workspace["id"]}
    assert sorted(t["status"] for t in tasks) == [
        "awaiting_review",
        "awaiting_review",
        "awaiting_review",
        "done",
        "queued",
    ]
    assert {t["kind"] for t in tasks} == {"write", "research", "visualize", "present"}
    assert all(t["title"].startswith("DEMO · ") and NOTICE in t["details"] for t in tasks)
    for task in tasks:
        if task["status"] == "queued":
            assert store.rows("SELECT * FROM runs WHERE task_id=?", (task["id"],)) == []
            continue
        artifact = store.artifact(task["id"])
        assert NOTICE in artifact.read_text() and artifact.stat().st_size > 500
        assert json.loads(artifact.with_name("sources.json").read_text()) == []
    assert all(json.loads(r["usage"])["simulated"] for r in store.rows("SELECT * FROM runs"))
    assert store.task(real_task)["status"] == store.task(other_task)["status"] == "queued"
    assert store.workspace("Interviews")["instructions"] == "Existing guidance"
    assert store.workspace("Interviews")["paused"]
    assert config.values == settings
    assert store.rows("SELECT * FROM meetings") == []


def test_demo_repeat_preserves_review_decisions_and_artifact_edits(env):
    config, store, _ = env
    workspace, tasks = seed_demo(config, store)
    draft = next(t for t in tasks if t["status"] == "awaiting_review")
    store.review(draft["id"], True)
    path = store.artifact(draft["id"])
    path.write_text("User-edited artifact")
    _, repeated = seed_demo(config, store)
    assert len(repeated) == 5
    assert store.task(draft["id"])["status"] == "done"
    assert path.read_text() == "User-edited artifact"
    assert len(store.rows("SELECT * FROM runs")) == 4
    assert len(store.rows("SELECT * FROM sources")) == 1
    _, elsewhere = seed_demo(config, store, "Separate rehearsal")
    assert {t["id"] for t in tasks}.isdisjoint({t["id"] for t in elsewhere})
    assert config.values["workspace"] == workspace["name"]


def test_demo_write_failure_rolls_back_fixture_rows_and_can_be_retried(env, monkeypatch):
    from adversaria_cli import demo

    config, store, engine = env
    original = store.add_task(engine.workspace()["id"], "Keep this task", "write")
    write = demo.atomic_text

    def fail_artifact(path, text):
        if path.name == "artifact.md":
            raise OSError("Disk full")
        write(path, text)

    monkeypatch.setattr(demo, "atomic_text", fail_artifact)
    with pytest.raises(OSError, match="Disk full"):
        seed_demo(config, store)
    assert [row["id"] for row in store.rows("SELECT * FROM tasks")] == [original]
    assert store.rows("SELECT * FROM runs") == []
    monkeypatch.setattr(demo, "atomic_text", write)
    _, tasks = seed_demo(config, store)
    assert len(tasks) == 5
    assert len(store.rows("SELECT * FROM runs")) == 4
