"""Arena: run every agent over every task, capture results.

The arena is intentionally synchronous and single-threaded. If your
agents do network I/O and you want concurrency, wrap them in your own
``concurrent.futures`` runner; this layer stays predictable so the
tests stay predictable.
"""

from __future__ import annotations

import time
from dataclasses import asdict, dataclass, field

from agent_eval_arena.agent import Agent
from agent_eval_arena.leaderboard import Leaderboard
from agent_eval_arena.task import Task


@dataclass(frozen=True)
class RunRecord:
    """One agent's attempt at one task."""

    agent_name: str
    task_id: str
    response: str
    score: float
    elapsed_ms: float
    error: str = ""

    @property
    def ok(self) -> bool:
        return not self.error


@dataclass
class ArenaResult:
    """Everything the arena produced for one run."""

    records: list[RunRecord] = field(default_factory=list)
    leaderboard: Leaderboard = field(default_factory=Leaderboard)

    def to_dict(self) -> dict:
        return {
            "records": [asdict(r) for r in self.records],
            "leaderboard": self.leaderboard.to_dict(),
        }


class Arena:
    """Hold agents and tasks, run them, and report.

    A fresh instance is the simplest path: ``Arena(agents, tasks).run()``.
    For longer-lived setups (e.g. CI), keep the instance around and call
    ``run`` multiple times; ``Arena`` itself is stateless between runs.
    """

    def __init__(
        self,
        agents: list[Agent] | None = None,
        tasks: list[Task] | None = None,
    ) -> None:
        self.agents: list[Agent] = list(agents or [])
        self.tasks: list[Task] = list(tasks or [])
        self._guard_unique_agent_names()
        self._guard_unique_task_ids()

    def add_agent(self, agent: Agent) -> None:
        """Append an agent. Names must stay unique across the arena."""
        self.agents.append(agent)
        self._guard_unique_agent_names()

    def add_task(self, task: Task) -> None:
        """Append a task. Task IDs must stay unique across the arena."""
        self.tasks.append(task)
        self._guard_unique_task_ids()

    def run(self) -> ArenaResult:
        """Execute every (agent, task) pair, score, and build the leaderboard.

        Agent exceptions are caught per (agent, task) so one buggy agent
        cannot torch the entire run; the failure is captured on the
        ``RunRecord`` as ``error`` with score 0.0.
        """
        if not self.agents:
            raise ValueError("Arena.run requires at least one agent")
        if not self.tasks:
            raise ValueError("Arena.run requires at least one task")

        records: list[RunRecord] = []
        for agent in self.agents:
            for task in self.tasks:
                records.append(self._run_one(agent, task))

        leaderboard = Leaderboard.from_records(records)
        return ArenaResult(records=records, leaderboard=leaderboard)

    def _run_one(self, agent: Agent, task: Task) -> RunRecord:
        start = time.perf_counter()
        try:
            response = agent.run(task)
            score = task.score(response)
            err = ""
        except Exception as exc:  # noqa: BLE001 - we want every failure
            response = ""
            score = 0.0
            err = f"{type(exc).__name__}: {exc}"
        elapsed = (time.perf_counter() - start) * 1000.0
        return RunRecord(
            agent_name=agent.name,
            task_id=task.task_id,
            response=response,
            score=score,
            elapsed_ms=round(elapsed, 3),
            error=err,
        )

    def _guard_unique_agent_names(self) -> None:
        seen: set[str] = set()
        for a in self.agents:
            if a.name in seen:
                raise ValueError(f"duplicate agent name: {a.name!r}")
            seen.add(a.name)

    def _guard_unique_task_ids(self) -> None:
        seen: set[str] = set()
        for t in self.tasks:
            if t.task_id in seen:
                raise ValueError(f"duplicate task id: {t.task_id!r}")
            seen.add(t.task_id)
