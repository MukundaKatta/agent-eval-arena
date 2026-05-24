"""Public surface is small and stable."""

from __future__ import annotations

import agent_eval_arena


def test_version_is_set():
    assert agent_eval_arena.__version__ == "0.2.0"


def test_public_exports_are_present():
    expected = {
        "Agent",
        "Arena",
        "ArenaResult",
        "FunctionAgent",
        "Leaderboard",
        "LeaderboardRow",
        "RunRecord",
        "Task",
        "contains_scorer",
        "exact_match_scorer",
        "keyword_scorer",
        "regex_scorer",
    }
    assert expected.issubset(set(agent_eval_arena.__all__))
    for name in expected:
        assert hasattr(agent_eval_arena, name), f"missing export: {name}"
