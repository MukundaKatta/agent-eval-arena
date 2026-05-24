"""Built-in scorers.

Each scorer is a factory: call it to get a callable that takes
``(response, task)`` and returns a float in [0.0, 1.0]. The clamp
happens inside ``Task.score`` so individual scorers stay simple.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agent_eval_arena.task import Task


def exact_match_scorer(*, case_sensitive: bool = False):
    """1.0 if the response equals ``task.expected``, 0.0 otherwise.

    Both sides are stripped before comparison so trailing newlines from
    chat models don't sink an otherwise-correct answer.
    """

    def scorer(response: str, task: "Task") -> float:
        left = response.strip()
        right = task.expected.strip()
        if not case_sensitive:
            left = left.lower()
            right = right.lower()
        return 1.0 if left == right else 0.0

    return scorer


def contains_scorer(*, case_sensitive: bool = False):
    """1.0 if ``task.expected`` appears anywhere in the response.

    Looser than exact-match. Useful when the response is a sentence and
    the expected value is a key phrase.
    """

    def scorer(response: str, task: "Task") -> float:
        needle = task.expected
        hay = response
        if not case_sensitive:
            needle = needle.lower()
            hay = hay.lower()
        if not needle:
            # No expected substring means we can't say anything useful.
            return 0.0
        return 1.0 if needle in hay else 0.0

    return scorer


def keyword_scorer(*, case_sensitive: bool = False):
    """Fraction of keywords (from ``task.reference['keywords']``) present.

    Returns 0.0 if no keywords are configured. This is the scorer to
    reach for when you want partial credit on freeform answers.
    """

    def scorer(response: str, task: "Task") -> float:
        keywords = [k for k in (task.reference.get("keywords") or []) if k]
        if not keywords:
            return 0.0
        hay = response if case_sensitive else response.lower()
        hits = 0
        for kw in keywords:
            needle = kw if case_sensitive else kw.lower()
            if needle in hay:
                hits += 1
        return hits / len(keywords)

    return scorer


def regex_scorer(*, flags: int = 0):
    """1.0 if ``task.reference['pattern']`` matches the response.

    The pattern is compiled lazily per-call so callers can pass dynamic
    patterns without paying a re-compile cost on the hot path; small
    inputs make that cheap enough.
    """

    def scorer(response: str, task: "Task") -> float:
        pattern = task.reference.get("pattern")
        if not pattern:
            return 0.0
        return 1.0 if re.search(pattern, response, flags) else 0.0

    return scorer
