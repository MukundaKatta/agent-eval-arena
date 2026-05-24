"""agent-eval-arena: a tiny offline arena for running agents against tasks.

Public surface kept small on purpose. If you need more, compose the pieces
yourself rather than asking the package to grow.
"""

from agent_eval_arena.agent import Agent, FunctionAgent
from agent_eval_arena.arena import Arena, ArenaResult, RunRecord
from agent_eval_arena.leaderboard import Leaderboard, LeaderboardRow
from agent_eval_arena.scorer import (
    contains_scorer,
    exact_match_scorer,
    keyword_scorer,
    regex_scorer,
)
from agent_eval_arena.task import Task

__version__ = "0.2.0"

__all__ = [
    "Agent",
    "Arena",
    "ArenaResult",
    "FunctionAgent",
    "Leaderboard",
    "LeaderboardRow",
    "RunRecord",
    "Task",
    "__version__",
    "contains_scorer",
    "exact_match_scorer",
    "keyword_scorer",
    "regex_scorer",
]
