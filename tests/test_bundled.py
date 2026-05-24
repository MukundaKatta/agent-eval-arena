"""Bundled fakes run end-to-end and produce a leaderboard."""

from __future__ import annotations

from agent_eval_arena.arena import Arena
from agent_eval_arena.bundled import bundled_agents, bundled_tasks


def test_bundled_demo_runs_end_to_end():
    arena = Arena(agents=bundled_agents(), tasks=bundled_tasks())
    result = arena.run()
    assert len(result.records) == 3 * 3  # 3 agents x 3 tasks
    assert len(result.leaderboard.rows) == 3


def test_strong_agent_is_first():
    arena = Arena(agents=bundled_agents(), tasks=bundled_tasks())
    lb = arena.run().leaderboard
    assert lb.rows[0].agent_name == "strong_fake"


def test_weak_agent_is_last():
    arena = Arena(agents=bundled_agents(), tasks=bundled_tasks())
    lb = arena.run().leaderboard
    assert lb.rows[-1].agent_name == "weak_fake"


def test_strong_agent_scores_meaningfully_above_weak():
    arena = Arena(agents=bundled_agents(), tasks=bundled_tasks())
    lb = arena.run().leaderboard
    strong = next(r for r in lb.rows if r.agent_name == "strong_fake")
    weak = next(r for r in lb.rows if r.agent_name == "weak_fake")
    assert strong.total_score - weak.total_score >= 1.0
