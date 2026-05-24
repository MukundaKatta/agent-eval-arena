"""Task: one prompt the arena will hand to every agent.

A task carries the prompt, the expected answer (or reference data the
scorer uses), and the scorer itself. Scorers are plain callables so you
can drop in your own without subclassing anything.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

# A scorer takes (response, task) and returns a float in [0.0, 1.0].
# The task is passed in so the scorer can reach into expected/reference.
Scorer = Callable[[str, "Task"], float]


@dataclass(frozen=True)
class Task:
    """A single evaluation task.

    Attributes:
        task_id: stable identifier used in run records and on the
            leaderboard. Keep it short.
        prompt: the actual prompt sent to every agent.
        expected: the canonical answer when there is one. Optional
            because regex/keyword scorers can ignore it.
        scorer: callable that scores an agent's response. See
            ``agent_eval_arena.scorer`` for built-ins.
        reference: free-form bag of extra data the scorer can use
            (keywords, patterns, rubric notes, etc.).
    """

    task_id: str
    prompt: str
    scorer: Scorer
    expected: str = ""
    reference: dict[str, Any] = field(default_factory=dict)

    def score(self, response: str) -> float:
        """Score a response against this task. Always clamps to [0.0, 1.0]."""
        raw = float(self.scorer(response, self))
        if raw < 0.0:
            return 0.0
        if raw > 1.0:
            return 1.0
        return raw
