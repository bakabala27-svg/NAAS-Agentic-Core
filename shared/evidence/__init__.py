"""The computed done signal (D-319): evidence level and verdict come from code, never from the author."""

from __future__ import annotations

from .gate import (
    DECISIONS,
    LEVELS,
    REPORT_STATUSES,
    REQUIRED_BY_ZONE,
    decision_for,
    evidence_level,
    report_problems,
    verdict,
)

__all__ = [
    "DECISIONS",
    "LEVELS",
    "REPORT_STATUSES",
    "REQUIRED_BY_ZONE",
    "decision_for",
    "evidence_level",
    "report_problems",
    "verdict",
]
