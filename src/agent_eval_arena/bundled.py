"""Bundled fake agents and tasks so the demo runs with zero setup.

Nothing here calls a real model. The goal is to demonstrate the arena
contract end-to-end on a laptop with no API keys.
"""

from __future__ import annotations

from agent_eval_arena.agent import FunctionAgent
from agent_eval_arena.scorer import (
    contains_scorer,
    exact_match_scorer,
    keyword_scorer,
)
from agent_eval_arena.task import Task


def bundled_tasks() -> list[Task]:
    """Three small tasks that exercise the three default scorers."""
    return [
        Task(
            task_id="capital_france",
            prompt="What is the capital of France?",
            expected="Paris",
            scorer=exact_match_scorer(),
        ),
        Task(
            task_id="define_arena",
            prompt="In one sentence, what is an evaluation arena?",
            scorer=keyword_scorer(),
            reference={"keywords": ["agents", "tasks", "score"]},
        ),
        Task(
            task_id="cite_python",
            prompt="Name a programming language created in 1991.",
            expected="Python",
            scorer=contains_scorer(),
        ),
    ]


def bundled_agents() -> list[FunctionAgent]:
    """Three deterministic fake agents covering strong, mid, and weak."""

    def strong(task: Task) -> str:
        # A "good" agent that happens to know the bundled answers.
        answers = {
            "capital_france": "Paris",
            "define_arena": (
                "An arena runs agents against shared tasks and produces a "
                "score per agent."
            ),
            "cite_python": "Python is one example.",
        }
        return answers.get(task.task_id, "")

    def medium(task: Task) -> str:
        # Gets some right, partial credit on others.
        answers = {
            "capital_france": "paris",  # case-insensitive scorer accepts
            "define_arena": "Agents try tasks and we collect scores.",
            "cite_python": "Visual Basic launched in the early 1990s.",
        }
        return answers.get(task.task_id, "")

    def weak(task: Task) -> str:
        # Wrong on most, deterministic for tests.
        return "I do not know."

    return [
        FunctionAgent("strong_fake", strong),
        FunctionAgent("medium_fake", medium),
        FunctionAgent("weak_fake", weak),
    ]
