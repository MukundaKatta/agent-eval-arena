"""Arena execution: pairing, error capture, validation."""

from __future__ import annotations

import pytest

from agent_eval_arena.agent import FunctionAgent
from agent_eval_arena.arena import Arena
from agent_eval_arena.scorer import exact_match_scorer
from agent_eval_arena.task import Task


def _t(task_id: str, expected: str = "ok") -> Task:
    return Task(
        task_id=task_id,
        prompt=f"task {task_id}",
        expected=expected,
        scorer=exact_match_scorer(),
    )


def test_run_pairs_every_agent_with_every_task():
    a1 = FunctionAgent("a1", lambda _t: "ok")
    a2 = FunctionAgent("a2", lambda _t: "ok")
    arena = Arena([a1, a2], [_t("x"), _t("y"), _t("z")])
    result = arena.run()
    assert len(result.records) == 6  # 2 agents x 3 tasks


def test_run_captures_response_and_score():
    agent = FunctionAgent("a", lambda _t: "ok")
    arena = Arena([agent], [_t("x")])
    result = arena.run()
    rec = result.records[0]
    assert rec.agent_name == "a"
    assert rec.task_id == "x"
    assert rec.response == "ok"
    assert rec.score == 1.0
    assert rec.error == ""
    assert rec.ok is True


def test_run_catches_agent_exception():
    def boom(_t):
        raise RuntimeError("kaboom")

    agent = FunctionAgent("crash", boom)
    arena = Arena([agent], [_t("x")])
    result = arena.run()
    rec = result.records[0]
    assert rec.score == 0.0
    assert "RuntimeError" in rec.error
    assert "kaboom" in rec.error
    assert rec.ok is False


def test_run_continues_after_failing_agent():
    bad = FunctionAgent("bad", lambda _t: (_ for _ in ()).throw(ValueError("nope")))
    good = FunctionAgent("good", lambda _t: "ok")
    arena = Arena([bad, good], [_t("x")])
    result = arena.run()
    assert len(result.records) == 2
    # Good agent still scores 1.0 despite bad agent crashing.
    good_rec = [r for r in result.records if r.agent_name == "good"][0]
    assert good_rec.score == 1.0


def test_run_records_elapsed_ms_non_negative():
    arena = Arena([FunctionAgent("a", lambda _t: "ok")], [_t("x")])
    rec = arena.run().records[0]
    assert rec.elapsed_ms >= 0.0


def test_run_requires_agents():
    arena = Arena([], [_t("x")])
    with pytest.raises(ValueError):
        arena.run()


def test_run_requires_tasks():
    arena = Arena([FunctionAgent("a", lambda _t: "ok")], [])
    with pytest.raises(ValueError):
        arena.run()


def test_duplicate_agent_names_rejected():
    a1 = FunctionAgent("dup", lambda _t: "x")
    a2 = FunctionAgent("dup", lambda _t: "x")
    with pytest.raises(ValueError):
        Arena([a1, a2], [_t("x")])


def test_duplicate_task_ids_rejected():
    with pytest.raises(ValueError):
        Arena([FunctionAgent("a", lambda _t: "x")], [_t("same"), _t("same")])


def test_add_agent_validates_uniqueness():
    arena = Arena([FunctionAgent("a", lambda _t: "x")], [_t("x")])
    with pytest.raises(ValueError):
        arena.add_agent(FunctionAgent("a", lambda _t: "x"))


def test_add_task_validates_uniqueness():
    arena = Arena([FunctionAgent("a", lambda _t: "x")], [_t("x")])
    with pytest.raises(ValueError):
        arena.add_task(_t("x"))


def test_arena_result_to_dict_round_trips():
    arena = Arena([FunctionAgent("a", lambda _t: "ok")], [_t("x")])
    payload = arena.run().to_dict()
    assert "records" in payload
    assert "leaderboard" in payload
    assert payload["records"][0]["agent_name"] == "a"
