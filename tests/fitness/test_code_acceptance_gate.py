"""Negative proofs for the acceptance packet's pre-modification and deletion controls."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "fitness"))

import check_code_acceptance as acceptance_gate


def _policy() -> dict:
    return json.loads(
        (ROOT / "docs/governance/ENGINEERING_GOVERNANCE_POLICY.json").read_text(encoding="utf-8")
    )


def test_pre_modification_evidence_is_required() -> None:
    """Feature-first packets without current state or old-debt analysis are red."""
    failures = acceptance_gate.validate_pre_modification({}, _policy())
    assert len(failures) >= 1
    assert "pre_modification" in "\n".join(failures)


def test_false_external_verified_claim_is_rejected() -> None:
    """A checkout cannot turn an unavailable GitHub Admin/API observation into VERIFIED."""
    pre_modification = {
        field: "evidence"
        for field in _policy()["pre_modification_packet"]["required_fields"]
        if field not in {"foundational_frontier", "claim_statuses"}
    }
    pre_modification["foundational_frontier"] = {
        "status": "NO_BLOCKING_FOUNDATIONAL_DEFECT_IDENTIFIED"
    }
    pre_modification["claim_statuses"] = {"branch_protection_live_state": "RUNTIME " + "VERIFIED"}
    failures = acceptance_gate.validate_pre_modification(
        {"pre_modification": pre_modification}, _policy()
    )
    assert len(failures) >= 1
    assert "falsely claims local verification" in "\n".join(failures)


def test_actual_deleted_path_cannot_be_hidden_by_zero_declaration(monkeypatch) -> None:
    """A declared zero is not proof when Git reports a deleted test or gate."""
    monkeypatch.setattr(acceptance_gate, "run_git", lambda _args: "tests/test_removed.py\n")
    monkeypatch.delenv("CODE_ACCEPTANCE_BASE_SHA", raising=False)
    assert acceptance_gate.current_deleted_paths() == ["tests/test_removed.py"]


# ── D-319: the done signal is computed, and no PASS is self-declared ──────────────


def _report(**overrides: object) -> dict:
    """A filled report in the template of the thesis (page 18), PRODUCT zone, level E3."""
    report: dict = {
        "change_id": "CHG-1",
        "claim": "one sentence",
        "status": "PROPOSED",
        "risk_zone": "PRODUCT",
        "registered": True,
        "evidence_level": "E3",
        "scope": {"declared_files": ["a.py", "b.py"], "touched_files": ["a.py"]},
        "protected_paths_changed": [],
        "contracts_touched": [],
        "evidence": {
            "reachability_trace": "trace.txt",
            "tests": {"passed": 3, "failed": 0, "new_negative_cases": 1},
            "vacuity_probe": "not_run",
            "mutation_score": None,
            "runtime_check": None,
        },
        "unverified": [{"what": "behaviour under load", "why": "no load harness"}],
        "residual_risks": [],
        "decision": "accept",
    }
    report.update(overrides)
    return report


def test_evidence_report_is_required() -> None:
    failures = acceptance_gate.validate_evidence_report({}, ["a.py"], [])
    assert "evidence_report" in "\n".join(failures)


def test_a_clean_report_matching_git_passes() -> None:
    packet = {"evidence_report": _report()}
    assert acceptance_gate.validate_evidence_report(packet, ["a.py"], []) == []


def test_touched_files_come_from_git_not_from_the_author() -> None:
    packet = {"evidence_report": _report()}
    failures = acceptance_gate.validate_evidence_report(packet, ["a.py", "c.py"], [])
    assert "touched_files" in "\n".join(failures)


def test_protected_paths_come_from_the_policy_not_from_the_author() -> None:
    packet = {"evidence_report": _report()}
    failures = acceptance_gate.validate_evidence_report(packet, ["a.py"], ["a.py"])
    assert "protected_paths_changed" in "\n".join(failures)


def test_an_authored_accept_over_a_computed_hold_is_rejected() -> None:
    report = _report(
        scope={"declared_files": ["a.py"], "touched_files": ["a.py"]},
        protected_paths_changed=["a.py"],
    )
    failures = acceptance_gate.validate_evidence_report(
        {"evidence_report": report}, ["a.py"], ["a.py"]
    )
    assert "decision is set by gate code" in "\n".join(failures)


def test_a_pass_for_a_gate_ci_never_runs_is_rejected() -> None:
    """Atlas master-prompt rules 8-9: a gate claimed PASS must be one CI runs again."""
    packet = {"verification": {"commands": ["python3 scripts/fitness/check_value_chain.py — PASS"]}}
    failures = acceptance_gate.validate_verification_claims(packet, ci_text="run: pytest\n")
    assert "check_value_chain.py" in "\n".join(failures)
    wired = "      python scripts/fitness/check_value_chain.py\n"
    assert acceptance_gate.validate_verification_claims(packet, ci_text=wired) == []


def test_a_commented_out_ci_line_does_not_count_as_wiring() -> None:
    packet = {"verification": {"commands": ["python3 scripts/fitness/check_value_chain.py — PASS"]}}
    commented = "      # python scripts/fitness/check_value_chain.py\n"
    assert acceptance_gate.validate_verification_claims(packet, ci_text=commented) != []


def test_a_verification_command_citing_a_missing_file_is_rejected() -> None:
    packet = {
        "verification": {"commands": ["pytest tests/fitness/test_does_not_exist.py — 3 passed"]}
    }
    failures = acceptance_gate.validate_verification_claims(packet, ci_text="")
    assert "test_does_not_exist.py" in "\n".join(failures)


def test_runtime_evidence_paths_must_exist() -> None:
    packet = {"production": {"runtime_evidence_paths": ["docs/does/not/exist.json"]}}
    failures = acceptance_gate.validate_runtime_evidence(packet)
    assert "docs/does/not/exist.json" in "\n".join(failures)


def test_pre_modification_names_non_goals_acceptance_criteria_and_operating_cost() -> None:
    """Atlas §8.1 (D-319): a build plan states what it will not do, how it is accepted,
    and what it may cost to run."""
    required = set(_policy()["pre_modification_packet"]["required_fields"])
    assert {"non_goals", "acceptance_criteria", "target_operating_cost"} <= required
