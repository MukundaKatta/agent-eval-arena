"""Agent protocol: anything that maps a prompt to a string response.

The arena does not care whether your agent is a real LLM call, a regex,
a lookup table, or a hand-rolled mock. Implement ``Agent`` or wrap a
callable with ``FunctionAgent`` and you're in.
"""

from __future__ import annotations

from typing import Callable, Protocol, runtime_checkable

from agent_eval_arena.task import Task


@runtime_checkable
class Agent(Protocol):
    """Minimum surface every agent must expose.

    Two attributes (``name`` is the leaderboard label) and one method
    (``run`` is the actual work). That's intentional: the arena needs to
    label runs and execute them, nothing else.
    """

    name: str

    def run(self, task: Task) -> str:  # pragma: no cover - protocol stub
        ...


class FunctionAgent:
    """Adapt a plain callable into an ``Agent`` without writing a class.

    Useful for fake agents, stub agents, and one-line wrappers around an
    LLM SDK call. The callable receives the ``Task`` and returns the
    raw response string.
    """

    __slots__ = ("_fn", "name")

    def __init__(self, name: str, fn: Callable[[Task], str]) -> None:
        if not name:
            raise ValueError("FunctionAgent name must be non-empty")
        self.name = name
        self._fn = fn

    def run(self, task: Task) -> str:
        result = self._fn(task)
        # Force a string here so the scorer never has to defend itself.
        return result if isinstance(result, str) else str(result)

    def __repr__(self) -> str:
        return f"FunctionAgent(name={self.name!r})"
