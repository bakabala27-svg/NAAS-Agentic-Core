"""The done signal is computed here, never authored by the model.

A faithful port of ``gate.py`` from the owner's thesis «الصاروخ لا يُصدَّق بمنظره»
(pages 18-19), made binding by D-319. ``LEVELS``, ``evidence_level`` and ``verdict``
keep the thesis's logic and messages exactly. Fields are read through ``_at`` and
``_num`` instead of bare indexing, so the report stays typed as ``object`` and the module
carries no ``Any`` (``check_no_new_any``). Two additions only make it fail-closed:

- a predicate that meets a missing or malformed field counts as *not met*, so a report
  that omits evidence stops at a lower level instead of crashing;
- ``report_problems`` checks the report template of page 18 and rejects an authored
  ``evidence_level`` or ``decision`` that differs from what this module computes.

Pure stdlib, deterministic, no I/O.
"""

from __future__ import annotations

from collections.abc import Callable, Collection, Mapping

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

Report = Mapping[str, object]


def _at(r: Report, *keys: str) -> object:
    """``r[k1][k2]…``; a missing key raises ``KeyError``, a non-mapping ``TypeError``."""
    value: object = r
    for key in keys:
        if not isinstance(value, Mapping):
            raise TypeError(f"{'.'.join(keys)}: {key!r} is read from a non-mapping")
        value = value[key]
    return value


def _num(r: Report, *keys: str) -> float:
    value = _at(r, *keys)
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise TypeError(f"{'.'.join(keys)} must be a number")
    return value


def _items(r: Report, *keys: str) -> set[object]:
    value = _at(r, *keys)
    if isinstance(value, str | bytes) or not isinstance(value, Collection):
        raise TypeError(f"{'.'.join(keys)} must be a list")
    return set(value)


LEVELS: list[tuple[str, Callable[[Report], bool]]] = [
    ("E1", lambda r: bool(_at(r, "registered"))),
    ("E2", lambda r: _at(r, "evidence", "reachability_trace") is not None),
    (
        "E3",
        lambda r: _num(r, "evidence", "tests", "failed") == 0
        and _num(r, "evidence", "tests", "passed") > 0
        and _num(r, "evidence", "tests", "new_negative_cases") > 0,
    ),
    (
        "E4",
        lambda r: _at(r, "evidence", "vacuity_probe") == "pass"
        and _num(r, "evidence", "mutation_score", "after")
        >= _num(r, "evidence", "mutation_score", "floor")
        and _num(r, "evidence", "mutation_score", "after")
        >= _num(r, "evidence", "mutation_score", "before"),
    ),
    ("E5", lambda r: _at(r, "evidence", "runtime_check") is not None),
]

#: The lower bound of each risk zone's range in D-318 (EXPERIMENT E2–E3, PRODUCT E3–E5,
#: CRITICAL E5–E7): the least evidence that zone may accept.
REQUIRED_BY_ZONE: dict[str, str] = {"EXPERIMENT": "E2", "PRODUCT": "E3", "CRITICAL": "E5"}

#: Report statuses of the template (page 18); CLOSED_CONFIRMED only with a measurement file.
REPORT_STATUSES: tuple[str, ...] = ("OPEN", "PROPOSED", "CLOSED_CONFIRMED")

#: Decisions of the template, set by gate code.
DECISIONS: tuple[str, ...] = ("accept", "fix", "hold", "collect_more_evidence")

_ALL_LEVELS = tuple(f"E{number}" for number in range(8))


def _met(ok: Callable[[Report], bool], report: Report) -> bool:
    try:
        return bool(ok(report))
    except (KeyError, TypeError, IndexError):
        return False


def evidence_level(r: Report) -> str:
    level = "E0"
    for name, ok in LEVELS:
        if not _met(ok, r):
            break
        level = name
    return level


def verdict(r: Report, required: str) -> str:
    if required not in _ALL_LEVELS:
        raise ValueError(f"required level must be one of E0..E7, got {required!r}")
    if _items(r, "scope", "touched_files") - _items(r, "scope", "declared_files"):
        return "HOLD: out-of-scope change"
    if _at(r, "protected_paths_changed"):
        return "HOLD: verifier files modified"
    if not _at(r, "unverified"):
        return "HOLD: unverified list is empty without justification"
    if evidence_level(r) < required:  # E0..E7 compare correctly as strings
        return "HOLD: insufficient evidence"
    return "ACCEPT"


def decision_for(computed_verdict: str) -> str:
    """Map a computed verdict to the template's decision word."""
    return "accept" if computed_verdict == "ACCEPT" else "hold"


def _filled(item: object, keys: tuple[str, ...]) -> bool:
    return isinstance(item, Mapping) and all(str(item.get(k) or "").strip() for k in keys)


def _header_problems(r: Report) -> list[str]:
    problems: list[str] = []
    status = r.get("status")
    if status not in REPORT_STATUSES:
        problems.append(f"status must be one of {REPORT_STATUSES}, got {status!r}")
    zone = r.get("risk_zone")
    if zone not in REQUIRED_BY_ZONE:
        problems.append(f"risk_zone must be one of {tuple(REQUIRED_BY_ZONE)}, got {zone!r}")
    problems.extend(f"{key} is empty" for key in ("change_id", "claim") if not _filled(r, (key,)))
    if status == "CLOSED_CONFIRMED" and not _filled(
        r.get("measurement"), ("file", "sha256", "date")
    ):
        problems.append("CLOSED_CONFIRMED needs a measurement with file, sha256 and date")
    return problems


def _shape_problems(r: Report) -> list[str]:
    """Shape errors that would make ``verdict`` unreadable; any one stops the check."""
    scope = r.get("scope")
    if not isinstance(scope, Mapping) or not all(
        isinstance(scope.get(k), list) for k in ("declared_files", "touched_files")
    ):
        return ["scope needs declared_files and touched_files lists"]
    if not isinstance(r.get("protected_paths_changed"), list):
        return ["protected_paths_changed must be a list"]
    unverified = r.get("unverified")
    if not isinstance(unverified, list):
        return ["unverified must be a list"]
    if not all(_filled(item, ("what", "why")) for item in unverified):
        return ["each unverified entry needs a non-empty what and why"]
    return []


def _computed_field_problems(r: Report) -> list[str]:
    problems: list[str] = []
    computed_level = evidence_level(r)
    if r.get("evidence_level") != computed_level:
        problems.append(
            f"evidence_level is computed by gate code: expected {computed_level}, "
            f"got {r.get('evidence_level')!r}"
        )
    zone = r.get("risk_zone")
    if isinstance(zone, str) and zone in REQUIRED_BY_ZONE:
        computed = decision_for(verdict(r, REQUIRED_BY_ZONE[zone]))
        if r.get("decision") != computed:
            problems.append(
                f"decision is set by gate code: expected {computed!r}, got {r.get('decision')!r}"
            )
    return problems


def report_problems(r: Report) -> list[str]:
    """Problems with a filled report; an empty list means the report is admissible."""
    problems = _header_problems(r)
    shape = _shape_problems(r)
    if shape:
        return problems + shape
    return problems + _computed_field_problems(r)
