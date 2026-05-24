"""Built-in scorer factories."""

from __future__ import annotations

import re

from agent_eval_arena.scorer import (
    contains_scorer,
    exact_match_scorer,
    keyword_scorer,
    regex_scorer,
)
from agent_eval_arena.task import Task


def _task(expected: str = "", reference: dict | None = None) -> Task:
    return Task(
        task_id="t",
        prompt="?",
        expected=expected,
        scorer=lambda r, t: 0.0,
        reference=reference or {},
    )


# exact ----------------------------------------------------------------------


def test_exact_match_case_insensitive_by_default():
    s = exact_match_scorer()
    assert s("Paris", _task("paris")) == 1.0
    assert s("paris", _task("Paris")) == 1.0


def test_exact_match_strips_whitespace():
    s = exact_match_scorer()
    assert s("  Paris\n", _task("Paris")) == 1.0


def test_exact_match_case_sensitive_when_asked():
    s = exact_match_scorer(case_sensitive=True)
    assert s("Paris", _task("Paris")) == 1.0
    assert s("paris", _task("Paris")) == 0.0


# contains -------------------------------------------------------------------


def test_contains_matches_substring():
    s = contains_scorer()
    assert s("Yes, the answer is Paris today.", _task("paris")) == 1.0


def test_contains_misses_when_substring_absent():
    s = contains_scorer()
    assert s("Berlin", _task("Paris")) == 0.0


def test_contains_returns_zero_when_expected_empty():
    s = contains_scorer()
    assert s("anything", _task("")) == 0.0


def test_contains_case_sensitive_flag():
    s = contains_scorer(case_sensitive=True)
    assert s("hello PARIS", _task("PARIS")) == 1.0
    assert s("hello paris", _task("PARIS")) == 0.0


# keyword --------------------------------------------------------------------


def test_keyword_full_credit_when_all_present():
    s = keyword_scorer()
    task = _task(reference={"keywords": ["alpha", "beta", "gamma"]})
    assert s("alpha beta gamma in some order", task) == 1.0


def test_keyword_partial_credit():
    s = keyword_scorer()
    task = _task(reference={"keywords": ["alpha", "beta", "gamma", "delta"]})
    score = s("alpha and gamma", task)
    assert score == 0.5  # 2 of 4


def test_keyword_zero_when_no_keywords_configured():
    s = keyword_scorer()
    assert s("anything", _task()) == 0.0


def test_keyword_skips_empty_keyword_entries():
    s = keyword_scorer()
    task = _task(reference={"keywords": ["alpha", "", "beta"]})
    # Empty string would match every response; skip it instead.
    assert s("alpha beta", task) == 1.0


def test_keyword_case_sensitive_flag():
    s = keyword_scorer(case_sensitive=True)
    task = _task(reference={"keywords": ["Alpha"]})
    assert s("alpha", task) == 0.0
    assert s("Alpha", task) == 1.0


# regex ----------------------------------------------------------------------


def test_regex_matches():
    s = regex_scorer()
    task = _task(reference={"pattern": r"\bParis\b"})
    assert s("the answer: Paris.", task) == 1.0


def test_regex_misses():
    s = regex_scorer()
    task = _task(reference={"pattern": r"\bParis\b"})
    assert s("the answer: Berlin.", task) == 0.0


def test_regex_zero_without_pattern():
    s = regex_scorer()
    assert s("anything", _task()) == 0.0


def test_regex_flags_honored():
    s = regex_scorer(flags=re.IGNORECASE)
    task = _task(reference={"pattern": "paris"})
    assert s("PARIS", task) == 1.0
