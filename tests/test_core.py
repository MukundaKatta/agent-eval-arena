"""Tests for AgentEvalArena."""
from src.core import AgentEvalArena
def test_init(): assert AgentEvalArena().get_stats()["ops"] == 0
def test_op(): c = AgentEvalArena(); c.process(x=1); assert c.get_stats()["ops"] == 1
def test_multi(): c = AgentEvalArena(); [c.process() for _ in range(5)]; assert c.get_stats()["ops"] == 5
def test_reset(): c = AgentEvalArena(); c.process(); c.reset(); assert c.get_stats()["ops"] == 0
def test_service_name(): c = AgentEvalArena(); r = c.process(); assert r["service"] == "agent-eval-arena"
