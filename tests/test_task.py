"""Task contract and clamping behavior."""

from __future__ import annotations

import pytest

from agent_eval_arena.scorer import exact_match_scorer
from agent_eval_arena.task import Task


def test_task_holds_prompt_and_expected():
    t = Task(
        task_id="t1",
        prompt="hello?",
        expected="hi",
        scorer=exact_match_scorer(),
    )
    assert t.task_id == "t1"
    assert t.prompt == "hello?"
    assert t.expected == "hi"


def test_task_score_uses_scorer():
    t = Task(
        task_id="t1",
        prompt="?",
        expected="yes",
        scorer=exact_match_scorer(),
    )
    assert t.score("yes") == 1.0
    assert t.score("no") == 0.0


def test_task_score_clamps_above_one():
    def crazy_scorer(_response: str, _task: Task) -> float:
        return 1.5

    t = Task(task_id="t1", prompt="?", scorer=crazy_scorer)
    assert t.score("anything") == 1.0


def test_task_score_clamps_below_zero():
    def negative_scorer(_response: str, _task: Task) -> float:
        return -0.7

    t = Task(task_id="t1", prompt="?", scorer=negative_scorer)
    assert t.score("anything") == 0.0


def test_task_default_reference_is_empty_dict():
    t = Task(task_id="t1", prompt="?", scorer=exact_match_scorer())
    assert t.reference == {}


def test_task_is_frozen():
    t = Task(task_id="t1", prompt="?", scorer=exact_match_scorer())
    with pytest.raises(Exception):
        t.task_id = "t2"  # type: ignore[misc]
