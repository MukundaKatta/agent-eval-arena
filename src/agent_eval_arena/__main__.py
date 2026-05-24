"""``python -m agent_eval_arena``: thin CLI over the arena.

Two commands:

* ``demo``  : run the bundled agents over the bundled tasks. Zero setup.
* ``run``   : load tasks from a JSON file and run them against named
              bundled agents. Real LLMs are out of scope here; the
              library is BYO-Agent in Python code.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from agent_eval_arena.arena import Arena
from agent_eval_arena.bundled import bundled_agents, bundled_tasks
from agent_eval_arena.scorer import (
    contains_scorer,
    exact_match_scorer,
    keyword_scorer,
    regex_scorer,
)
from agent_eval_arena.task import Task

_SCORERS = {
    "exact": exact_match_scorer,
    "contains": contains_scorer,
    "keyword": keyword_scorer,
    "regex": regex_scorer,
}


def _load_tasks(path: Path) -> list[Task]:
    """Load tasks from a JSON file with a small declarative schema.

    Expected shape:
        [
          {
            "task_id": "...",
            "prompt": "...",
            "scorer": "exact" | "contains" | "keyword" | "regex",
            "expected": "...",            # optional
            "reference": { ... }           # optional
          },
          ...
        ]
    """
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise ValueError(f"{path}: expected a JSON list of tasks")
    tasks: list[Task] = []
    for i, item in enumerate(raw):
        if not isinstance(item, dict):
            raise ValueError(f"{path}: task {i} is not an object")
        scorer_name = item.get("scorer", "exact")
        factory = _SCORERS.get(scorer_name)
        if factory is None:
            raise ValueError(
                f"{path}: task {i}: unknown scorer {scorer_name!r}; "
                f"choices are {sorted(_SCORERS)}"
            )
        tasks.append(
            Task(
                task_id=str(item["task_id"]),
                prompt=str(item["prompt"]),
                scorer=factory(),
                expected=str(item.get("expected", "")),
                reference=dict(item.get("reference", {})),
            )
        )
    return tasks


def _filter_agents(names: list[str] | None):
    pool = {a.name: a for a in bundled_agents()}
    if not names:
        return list(pool.values())
    selected = []
    for n in names:
        if n not in pool:
            raise SystemExit(
                f"unknown bundled agent {n!r}; available: {sorted(pool)}"
            )
        selected.append(pool[n])
    return selected


def _emit(result, fmt: str) -> None:
    if fmt == "json":
        print(json.dumps(result.to_dict(), indent=2, default=str))
    else:
        print(result.leaderboard.render_ascii())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="agent-eval-arena")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_demo = sub.add_parser("demo", help="Run bundled agents over bundled tasks.")
    p_demo.add_argument(
        "--format", choices=("ascii", "json"), default="ascii"
    )

    p_run = sub.add_parser("run", help="Run bundled agents over tasks from a JSON file.")
    p_run.add_argument("--tasks", required=True, help="Path to tasks JSON file.")
    p_run.add_argument(
        "--agents",
        default="",
        help="Comma-separated bundled agent names (default: all).",
    )
    p_run.add_argument(
        "--format", choices=("ascii", "json"), default="ascii"
    )

    args = parser.parse_args(argv)

    if args.cmd == "demo":
        arena = Arena(agents=bundled_agents(), tasks=bundled_tasks())
        _emit(arena.run(), args.format)
        return 0

    if args.cmd == "run":
        names = [n.strip() for n in args.agents.split(",") if n.strip()]
        tasks = _load_tasks(Path(args.tasks))
        arena = Arena(agents=_filter_agents(names), tasks=tasks)
        _emit(arena.run(), args.format)
        return 0

    parser.print_help(sys.stderr)
    return 2


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
