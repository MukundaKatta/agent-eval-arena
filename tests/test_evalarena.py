"""Tests for EvalArena."""
import pytest
from src.evalarena import EvalArena

def test_init():
    obj = EvalArena()
    stats = obj.get_stats()
    assert stats["total_ops"] == 0

def test_operation():
    obj = EvalArena()
    result = obj.create_match(input="test")
    assert result["processed"] is True
    assert result["operation"] == "create_match"

def test_multiple_ops():
    obj = EvalArena()
    for m in ['create_match', 'run_evaluation', 'record_result']:
        getattr(obj, m)(data="test")
    assert obj.get_stats()["total_ops"] == 3

def test_caching():
    obj = EvalArena()
    r1 = obj.create_match(key="same")
    r2 = obj.create_match(key="same")
    assert r2.get("cached") is True

def test_reset():
    obj = EvalArena()
    obj.create_match()
    obj.reset()
    assert obj.get_stats()["total_ops"] == 0

def test_stats():
    obj = EvalArena()
    obj.create_match(x=1)
    obj.run_evaluation(y=2)
    stats = obj.get_stats()
    assert stats["total_ops"] == 2
    assert "ops_by_type" in stats
