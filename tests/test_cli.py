"""CLI entrypoint: demo, run, JSON output, file loading."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from agent_eval_arena.__main__ import _load_tasks, main


def test_demo_ascii_output(capsys):
    rc = main(["demo"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "agent" in out
    assert "strong_fake" in out


def test_demo_json_output(capsys):
    rc = main(["demo", "--format", "json"])
    out = capsys.readouterr().out
    assert rc == 0
    payload = json.loads(out)
    assert "records" in payload
    assert "leaderboard" in payload
    assert len(payload["records"]) == 9


def test_run_with_tasks_file(tmp_path: Path, capsys):
    tasks_file = tmp_path / "tasks.json"
    tasks_file.write_text(
        json.dumps(
            [
                {
                    "task_id": "capital_france",
                    "prompt": "?",
                    "scorer": "exact",
                    "expected": "Paris",
                }
            ]
        )
    )
    rc = main(["run", "--tasks", str(tasks_file), "--format", "json"])
    out = capsys.readouterr().out
    assert rc == 0
    payload = json.loads(out)
    assert len(payload["records"]) == 3  # 3 bundled agents x 1 task


def test_run_with_agent_filter(tmp_path: Path, capsys):
    tasks_file = tmp_path / "tasks.json"
    tasks_file.write_text(
        json.dumps(
            [
                {
                    "task_id": "capital_france",
                    "prompt": "?",
                    "scorer": "exact",
                    "expected": "Paris",
                }
            ]
        )
    )
    rc = main(
        [
            "run",
            "--tasks",
            str(tasks_file),
            "--agents",
            "strong_fake,weak_fake",
            "--format",
            "json",
        ]
    )
    out = capsys.readouterr().out
    assert rc == 0
    payload = json.loads(out)
    names = {r["agent_name"] for r in payload["records"]}
    assert names == {"strong_fake", "weak_fake"}


def test_run_unknown_agent_exits(tmp_path: Path):
    tasks_file = tmp_path / "tasks.json"
    tasks_file.write_text(
        json.dumps(
            [
                {
                    "task_id": "t",
                    "prompt": "?",
                    "scorer": "exact",
                    "expected": "x",
                }
            ]
        )
    )
    with pytest.raises(SystemExit):
        main(["run", "--tasks", str(tasks_file), "--agents", "no_such_agent"])


def test_load_tasks_rejects_unknown_scorer(tmp_path: Path):
    p = tmp_path / "bad.json"
    p.write_text(
        json.dumps(
            [{"task_id": "t", "prompt": "?", "scorer": "blockchain", "expected": "x"}]
        )
    )
    with pytest.raises(ValueError):
        _load_tasks(p)


def test_load_tasks_rejects_non_list(tmp_path: Path):
    p = tmp_path / "bad.json"
    p.write_text(json.dumps({"task_id": "t"}))
    with pytest.raises(ValueError):
        _load_tasks(p)


def test_load_tasks_rejects_non_object_entry(tmp_path: Path):
    p = tmp_path / "bad.json"
    p.write_text(json.dumps(["just a string"]))
    with pytest.raises(ValueError):
        _load_tasks(p)
