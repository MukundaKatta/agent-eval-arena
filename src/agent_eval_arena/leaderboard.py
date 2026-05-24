"""Leaderboard: aggregate run records into per-agent rows.

Renders as JSON, plain text, or ASCII table. Sorted by total score
descending, then by mean latency ascending (faster breaks ties).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agent_eval_arena.arena import RunRecord


@dataclass(frozen=True)
class LeaderboardRow:
    """One agent's aggregated performance across all tasks."""

    rank: int
    agent_name: str
    total_score: float
    mean_score: float
    tasks_completed: int
    tasks_attempted: int
    mean_latency_ms: float
    errors: int

    def to_dict(self) -> dict:
        return {
            "rank": self.rank,
            "agent_name": self.agent_name,
            "total_score": round(self.total_score, 4),
            "mean_score": round(self.mean_score, 4),
            "tasks_completed": self.tasks_completed,
            "tasks_attempted": self.tasks_attempted,
            "mean_latency_ms": round(self.mean_latency_ms, 3),
            "errors": self.errors,
        }


@dataclass
class Leaderboard:
    """Ordered list of per-agent rows plus a couple of rendering helpers."""

    rows: list[LeaderboardRow] = field(default_factory=list)

    @classmethod
    def from_records(cls, records: list["RunRecord"]) -> "Leaderboard":
        """Build a leaderboard by grouping run records on ``agent_name``."""
        grouped: dict[str, list["RunRecord"]] = {}
        for rec in records:
            grouped.setdefault(rec.agent_name, []).append(rec)

        rows: list[LeaderboardRow] = []
        for name, recs in grouped.items():
            total = sum(r.score for r in recs)
            attempted = len(recs)
            completed = sum(1 for r in recs if r.ok)
            errors = attempted - completed
            mean_score = total / attempted if attempted else 0.0
            mean_latency = (
                sum(r.elapsed_ms for r in recs) / attempted if attempted else 0.0
            )
            rows.append(
                LeaderboardRow(
                    rank=0,  # filled in after sort
                    agent_name=name,
                    total_score=total,
                    mean_score=mean_score,
                    tasks_completed=completed,
                    tasks_attempted=attempted,
                    mean_latency_ms=mean_latency,
                    errors=errors,
                )
            )

        # Highest total first; faster mean latency breaks ties; then name
        # for deterministic ordering when latency also ties (mostly only
        # in tests with mocked agents).
        rows.sort(key=lambda r: (-r.total_score, r.mean_latency_ms, r.agent_name))
        rows = [
            LeaderboardRow(
                rank=i + 1,
                agent_name=row.agent_name,
                total_score=row.total_score,
                mean_score=row.mean_score,
                tasks_completed=row.tasks_completed,
                tasks_attempted=row.tasks_attempted,
                mean_latency_ms=row.mean_latency_ms,
                errors=row.errors,
            )
            for i, row in enumerate(rows)
        ]
        return cls(rows=rows)

    def to_dict(self) -> dict:
        return {"rows": [r.to_dict() for r in self.rows]}

    def render_ascii(self) -> str:
        """Render a small fixed-width ASCII table suitable for terminals."""
        if not self.rows:
            return "(empty leaderboard)"
        headers = [
            "#",
            "agent",
            "total",
            "mean",
            "done",
            "lat_ms",
            "errs",
        ]
        body = [
            [
                str(r.rank),
                r.agent_name,
                f"{r.total_score:.2f}",
                f"{r.mean_score:.2f}",
                f"{r.tasks_completed}/{r.tasks_attempted}",
                f"{r.mean_latency_ms:.1f}",
                str(r.errors),
            ]
            for r in self.rows
        ]
        widths = [
            max(len(headers[i]), *(len(row[i]) for row in body))
            for i in range(len(headers))
        ]

        def fmt(row: list[str]) -> str:
            return "  ".join(cell.ljust(widths[i]) for i, cell in enumerate(row))

        sep = "  ".join("-" * w for w in widths)
        lines = [fmt(headers), sep] + [fmt(row) for row in body]
        return "\n".join(lines)
