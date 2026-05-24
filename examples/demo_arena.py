"""End-to-end demo: three fake agents, three tasks, one leaderboard.

Run it with::

    PYTHONPATH=src python3 examples/demo_arena.py

or, after ``pip install -e .``::

    agent-eval-arena demo
"""

from __future__ import annotations

from agent_eval_arena.arena import Arena
from agent_eval_arena.bundled import bundled_agents, bundled_tasks


def main() -> None:
    arena = Arena(agents=bundled_agents(), tasks=bundled_tasks())
    result = arena.run()

    print(result.leaderboard.render_ascii())
    print()

    # Show one example per agent so you can see the raw responses too.
    seen: set[str] = set()
    for rec in result.records:
        if rec.agent_name in seen:
            continue
        seen.add(rec.agent_name)
        print(
            f"[{rec.agent_name}] task={rec.task_id} "
            f"score={rec.score:.2f} "
            f"response={rec.response!r}"
        )


if __name__ == "__main__":
    main()
