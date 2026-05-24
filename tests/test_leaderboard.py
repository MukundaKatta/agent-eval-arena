"""Leaderboard aggregation and rendering."""

from __future__ import annotations

from agent_eval_arena.arena import RunRecord
from agent_eval_arena.leaderboard import Leaderboard


def _rec(name: str, task: str, score: float, lat: float = 1.0, err: str = "") -> RunRecord:
    return RunRecord(
        agent_name=name,
        task_id=task,
        response="x" if not err else "",
        score=score,
        elapsed_ms=lat,
        error=err,
    )


def test_from_records_ranks_by_total_score_desc():
    recs = [
        _rec("low", "t1", 0.0),
        _rec("low", "t2", 0.5),
        _rec("high", "t1", 1.0),
        _rec("high", "t2", 1.0),
    ]
    lb = Leaderboard.from_records(recs)
    assert lb.rows[0].agent_name == "high"
    assert lb.rows[0].rank == 1
    assert lb.rows[1].agent_name == "low"
    assert lb.rows[1].rank == 2


def test_from_records_breaks_ties_by_latency():
    recs = [
        _rec("slow", "t1", 1.0, lat=10.0),
        _rec("fast", "t1", 1.0, lat=1.0),
    ]
    lb = Leaderboard.from_records(recs)
    # Same score, lower latency wins.
    assert lb.rows[0].agent_name == "fast"


def test_from_records_breaks_ties_by_name_when_latency_also_equal():
    recs = [
        _rec("beta", "t1", 1.0, lat=1.0),
        _rec("alpha", "t1", 1.0, lat=1.0),
    ]
    lb = Leaderboard.from_records(recs)
    assert lb.rows[0].agent_name == "alpha"


def test_counts_errors_and_completed():
    recs = [
        _rec("a", "t1", 1.0),
        _rec("a", "t2", 0.0, err="RuntimeError: boom"),
        _rec("a", "t3", 0.5),
    ]
    lb = Leaderboard.from_records(recs)
    row = lb.rows[0]
    assert row.tasks_attempted == 3
    assert row.tasks_completed == 2
    assert row.errors == 1


def test_means_computed_correctly():
    recs = [
        _rec("a", "t1", 1.0, lat=2.0),
        _rec("a", "t2", 0.0, lat=4.0),
    ]
    lb = Leaderboard.from_records(recs)
    row = lb.rows[0]
    assert row.mean_score == 0.5
    assert row.mean_latency_ms == 3.0


def test_to_dict_serializes_all_rows():
    recs = [_rec("a", "t1", 1.0), _rec("b", "t1", 0.5)]
    payload = Leaderboard.from_records(recs).to_dict()
    assert len(payload["rows"]) == 2
    assert payload["rows"][0]["rank"] == 1


def test_render_ascii_includes_headers_and_rows():
    recs = [_rec("a", "t1", 1.0), _rec("b", "t1", 0.5)]
    out = Leaderboard.from_records(recs).render_ascii()
    assert "agent" in out
    assert "total" in out
    assert "a" in out
    assert "b" in out


def test_render_ascii_empty_message():
    assert Leaderboard().render_ascii() == "(empty leaderboard)"
