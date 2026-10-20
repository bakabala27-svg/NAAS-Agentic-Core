"""اختبارات سلبية لبوابة دستور تناسب الدليل (D-318)."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from scripts.fitness import check_evidence_proportionality_constitution as gate


def _law_text() -> str:
    levels = "\n".join(f"| `E{n}` | claim | evidence |" for n in range(8))
    laws = "\n".join(f"### L{n} — law" for n in range(1, 13))
    rules = "\n".join(f"| `NF-{n} rule` | rule | proof |" for n in range(1, 6))
    zones = " ".join(f"`{zone}`" for zone in gate.RISK_ZONES)
    markers = "\n".join(gate.REQUIRED_MARKERS)
    return (
        f"{levels}\n{laws}\n{rules}\n{zones}\n{markers}\n"
        "لا يستطيع نص داخل المستودع منع سلطة المنصة الخارجية.\n"
    )


def test_one_byte_change_is_rejected(tmp_path: Path, monkeypatch) -> None:
    """أي تغيير بايت واحد في النص القانوني يجب أن يفشل أمام البصمة المجمدة."""
    law = tmp_path / "law.md"
    pin = tmp_path / "pin.json"
    original = _law_text().encode("utf-8")
    law.write_bytes(original + b"x")
    pin.write_text(
        json.dumps(
            {
                "canonical_text": gate.LAW_REL,
                "sha256": hashlib.sha256(original).hexdigest(),
                "byte_count": len(original),
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(gate, "LAW_DOC", law)
    monkeypatch.setattr(gate, "PIN", pin)
    gate._FAILURES.clear()
    gate.check_byte_pin()
    assert any("اختلف حرف/بايت" in failure for failure in gate._FAILURES)


def test_missing_evidence_level_is_rejected(tmp_path: Path, monkeypatch) -> None:
    """حذف E4، درجة حساسية الاختبار، يجعل العقد ناقصًا ويفشل البوابة."""
    law = tmp_path / "law.md"
    law.write_text(_law_text().replace("| `E4` | claim | evidence |\n", ""), encoding="utf-8")
    monkeypatch.setattr(gate, "LAW_DOC", law)
    gate._FAILURES.clear()
    gate.check_law_contract()
    assert any("E4" in failure for failure in gate._FAILURES)


def test_missing_independence_law_is_rejected(tmp_path: Path, monkeypatch) -> None:
    """لا يمكن حذف قانون استقلال المولد والحكم مع إبقاء البوابة خضراء."""
    law = tmp_path / "law.md"
    law.write_text(_law_text().replace("### L6 — law\n", ""), encoding="utf-8")
    monkeypatch.setattr(gate, "LAW_DOC", law)
    gate._FAILURES.clear()
    gate.check_law_contract()
    assert any("L6" in failure for failure in gate._FAILURES)


def test_unprotected_gate_is_rejected(tmp_path: Path, monkeypatch) -> None:
    """إخراج القانون/الفارض/اختباره من protected_paths انتهاك دستوري."""
    policy = tmp_path / "policy.json"
    policy.write_text(json.dumps({"protected_paths": []}), encoding="utf-8")
    monkeypatch.setattr(gate, "POLICY", policy)
    gate._FAILURES.clear()
    gate.check_protected_artifacts()
    assert {gate.LAW_REL, gate.GATE_REL, gate.TEST_REL} <= {
        failure.rsplit(": ", 1)[-1] for failure in gate._FAILURES
    }


def test_registry_without_enforcer_is_rejected(tmp_path: Path, monkeypatch) -> None:
    """دستور مسجل بلا فارض ليس دستورًا منفذًا."""
    registry = tmp_path / "registry.json"
    registry.write_text(
        json.dumps(
            {
                "constitutions": [
                    {
                        "id": "D-318",
                        "section": "0.30",
                        "law_docs": [gate.LAW_REL],
                        "status_docs": [],
                        "enforcers": [],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(gate, "REGISTRY", registry)
    gate._FAILURES.clear()
    gate.check_registry_entry()
    assert any(gate.GATE_NAME in failure for failure in gate._FAILURES)


def test_gate_absent_from_guardrails_is_rejected(tmp_path: Path, monkeypatch) -> None:
    """وجود ملف الفارض دون تشغيله في المسار الإلزامي لا يمنح حماية."""
    workflow = tmp_path / "ci.yml"
    workflow.write_text(
        "jobs:\n  guardrails:\n    run: |\n      set -euo pipefail\n", encoding="utf-8"
    )
    monkeypatch.setattr(gate, "CI_WORKFLOW", workflow)
    gate._FAILURES.clear()
    gate.check_ci_wiring()
    assert any("غير منفذ" in failure for failure in gate._FAILURES)


def test_commented_out_gate_in_guardrails_is_rejected(tmp_path: Path, monkeypatch) -> None:
    """D-319: سطرٌ مُعلَّق لا يُنفَّذ — وجود الاسم في تعليقٍ ليس توصيلاً."""
    workflow = tmp_path / "ci.yml"
    workflow.write_text(
        "jobs:\n  guardrails:\n    run: |\n      set -euo pipefail\n"
        f"      # python scripts/fitness/{gate.GATE_NAME}\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(gate, "CI_WORKFLOW", workflow)
    gate._FAILURES.clear()
    gate.check_ci_wiring()
    assert any("غير منفذ" in failure for failure in gate._FAILURES)


def test_gate_run_only_in_a_later_job_is_rejected(tmp_path: Path, monkeypatch) -> None:
    """D-319: القراءة تنحصر في وظيفة guardrails لا حتى نهاية الملف."""
    workflow = tmp_path / "ci.yml"
    workflow.write_text(
        "jobs:\n  guardrails:\n    run: |\n      set -euo pipefail\n"
        "  other:\n    run: |\n"
        f"      python scripts/fitness/{gate.GATE_NAME}\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(gate, "CI_WORKFLOW", workflow)
    gate._FAILURES.clear()
    gate.check_ci_wiring()
    assert any("غير منفذ" in failure for failure in gate._FAILURES)
