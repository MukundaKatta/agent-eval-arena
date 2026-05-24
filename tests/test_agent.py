"""Agent protocol and FunctionAgent adapter."""

from __future__ import annotations

import pytest

from agent_eval_arena.agent import Agent, FunctionAgent
from agent_eval_arena.scorer import exact_match_scorer
from agent_eval_arena.task import Task


def _make_task() -> Task:
    return Task(
        task_id="t",
        prompt="ping",
        expected="pong",
        scorer=exact_match_scorer(),
    )


def test_function_agent_passes_task_to_callable():
    seen: list[Task] = []

    def fn(task: Task) -> str:
        seen.append(task)
        return "pong"

    agent = FunctionAgent("echo", fn)
    task = _make_task()
    assert agent.run(task) == "pong"
    assert seen == [task]


def test_function_agent_coerces_non_string_to_string():
    agent = FunctionAgent("intish", lambda _t: 42)  # type: ignore[arg-type]
    assert agent.run(_make_task()) == "42"


def test_function_agent_requires_name():
    with pytest.raises(ValueError):
        FunctionAgent("", lambda _t: "x")


def test_function_agent_satisfies_protocol():
    agent = FunctionAgent("a", lambda _t: "x")
    assert isinstance(agent, Agent)


def test_function_agent_repr_includes_name():
    agent = FunctionAgent("named", lambda _t: "x")
    assert "named" in repr(agent)
