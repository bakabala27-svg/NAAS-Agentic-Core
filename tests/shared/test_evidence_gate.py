"""The done signal is computed by code, never authored (Rocket thesis p18-19, D-319).

Each HOLD branch of ``verdict`` gets its own negative case, and the report checks
reject an authored evidence level or decision that the code would not compute.
"""

from __future__ import annotations

import copy

import pytest

from shared.evidence.gate import (
    LEVELS,
    REQUIRED_BY_ZONE,
    decision_for,
    evidence_level,
    report_problems,
    verdict,
)


def _report() -> dict:
    """A report that reaches E5 and touches only declared, unprotected files."""
    return {
        "change_id": "demo-1",
        "claim": "The router rejects unknown intents.",
        "status": "PROPOSED",
        "registered": True,
        "risk_zone": "PRODUCT",
        "scope": {
            "declared_files": ["src/router.py", "tests/test_router.py"],
            "touched_files": ["src/router.py", "tests/test_router.py"],
        },
        "protected_paths_changed": [],
        "contracts_touched": [],
        "evidence": {
            "reachability_trace": "artifacts/trace.txt",
            "tests": {"passed": 42, "failed": 0, "new_negative_cases": 5},
            "vacuity_probe": "pass",
            "mutation_score": {"before": 0.61, "after": 0.68, "floor": 0.60},
            "integration_regression": "artifacts/regression.txt",
            "runtime_check": "artifacts/runtime.txt",
        },
        "unverified": [{"what": "concurrent retries", "why": "no failure-injection harness yet"}],
        "residual_risks": [],
    }


def test_levels_are_the_documented_five_in_order() -> None:
    assert [name for name, _ in LEVELS] == ["E1", "E2", "E3", "E4", "E5"]


def test_full_report_reaches_e5_and_is_accepted() -> None:
    report = _report()
    assert evidence_level(report) == "E5"
    assert verdict(report, "E3") == "ACCEPT"
    assert decision_for(verdict(report, "E3")) == "accept"


@pytest.mark.parametrize(
    ("mutate", "expected"),
    [
        (lambda r: r.update(registered=False), "E0"),
        (lambda r: r["evidence"].update(reachability_trace=None), "E1"),
        (lambda r: r["evidence"]["tests"].update(failed=1), "E2"),
        (lambda r: r["evidence"]["tests"].update(new_negative_cases=0), "E2"),
        (lambda r: r["evidence"]["tests"].update(passed=0), "E2"),
        (lambda r: r["evidence"].update(vacuity_probe="fail"), "E3"),
        (lambda r: r["evidence"]["mutation_score"].update(after=0.55), "E3"),
        (lambda r: r["evidence"]["mutation_score"].update(before=0.70), "E3"),
        (lambda r: r["evidence"].update(runtime_check=None), "E4"),
    ],
)
def test_the_level_stops_at_the_first_unmet_rung(mutate, expected: str) -> None:
    report = _report()
    mutate(report)
    assert evidence_level(report) == expected


def test_a_missing_field_lowers_the_level_instead_of_raising() -> None:
    report = _report()
    del report["evidence"]["mutation_score"]
    assert evidence_level(report) == "E3"


def test_hold_on_out_of_scope_change() -> None:
    report = _report()
    report["scope"]["touched_files"].append("src/other.py")
    assert verdict(report, "E3") == "HOLD: out-of-scope change"


def test_hold_when_verifier_files_change() -> None:
    report = _report()
    report["protected_paths_changed"] = ["scripts/fitness/check_x.py"]
    assert verdict(report, "E3") == "HOLD: verifier files modified"


def test_hold_when_nothing_is_declared_unverified() -> None:
    report = _report()
    report["unverified"] = []
    assert verdict(report, "E3") == "HOLD: unverified list is empty without justification"


def test_hold_on_insufficient_evidence() -> None:
    report = _report()
    report["evidence"]["runtime_check"] = None
    assert verdict(report, "E5") == "HOLD: insufficient evidence"
    assert decision_for(verdict(report, "E5")) == "hold"


def test_zone_minimums_are_the_lower_bound_of_each_d318_range() -> None:
    assert REQUIRED_BY_ZONE == {"EXPERIMENT": "E2", "PRODUCT": "E3", "CRITICAL": "E5"}


def test_an_unknown_required_level_is_rejected() -> None:
    with pytest.raises(ValueError):
        verdict(_report(), "E9")


def test_report_problems_accepts_a_computed_level_and_decision() -> None:
    report = _report()
    report["evidence_level"] = evidence_level(report)
    report["decision"] = decision_for(verdict(report, REQUIRED_BY_ZONE[report["risk_zone"]]))
    assert report_problems(report) == []


def test_an_authored_level_that_differs_from_the_computed_one_is_a_problem() -> None:
    report = _report()
    report["evidence"]["runtime_check"] = None
    report["evidence_level"] = "E5"
    report["decision"] = "accept"
    problems = report_problems(report)
    assert any("evidence_level" in p for p in problems)


def test_an_authored_accept_over_a_computed_hold_is_a_problem() -> None:
    report = _report()
    report["unverified"] = []
    report["evidence_level"] = evidence_level(report)
    report["decision"] = "accept"
    assert any("decision" in p for p in report_problems(report))


def test_closed_confirmed_needs_a_measurement_file() -> None:
    report = _report()
    report["status"] = "CLOSED_CONFIRMED"
    report["evidence_level"] = evidence_level(report)
    report["decision"] = decision_for(verdict(report, "E3"))
    assert any("measurement" in p for p in report_problems(report))
    report["measurement"] = {"file": "m.json", "sha256": "a" * 64, "date": "2026-10-19"}
    assert report_problems(report) == []


def test_unknown_status_and_zone_are_problems() -> None:
    report = copy.deepcopy(_report())
    report["status"] = "DONE"
    report["risk_zone"] = "SOMEWHERE"
    problems = report_problems(report)
    assert any("status" in p for p in problems)
    assert any("risk_zone" in p for p in problems)
