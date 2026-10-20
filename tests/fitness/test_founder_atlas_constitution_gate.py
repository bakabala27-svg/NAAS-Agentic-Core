"""اختبارات سلبية لبوابة دستور أطلس المؤسس (D-319): كل اختبارٍ يكسر شيئاً عمداً."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from scripts.fitness import check_founder_atlas_constitution as gate


def _law_text() -> str:
    markers = "\n".join(gate.REQUIRED_MARKERS)
    hatches = "\n".join(f"| «{hatch}» | **ملغى**: سبب |" for hatch in gate.D318_ESCAPE_HATCHES)
    homes = "\n".join(f"| قاعدة | فرض | `{home}` |" for home in gate.REQUIRED_HOMES)
    return f"{markers}\n{hatches}\n{homes}\n"


def _run(check, monkeypatch, **paths: Path) -> list[str]:
    for name, path in paths.items():
        monkeypatch.setattr(gate, name, path)
    gate._FAILURES.clear()
    check()
    return list(gate._FAILURES)


def test_the_real_repository_passes() -> None:
    assert gate.main() == 0


def test_one_byte_change_is_rejected(tmp_path: Path, monkeypatch) -> None:
    law, pin = tmp_path / "law.md", tmp_path / "pin.json"
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
    failures = _run(gate.check_byte_pin, monkeypatch, LAW_DOC=law, PIN=pin)
    assert any("اختلف حرف/بايت" in failure for failure in failures)


def test_a_missing_marker_is_rejected(tmp_path: Path, monkeypatch) -> None:
    law = tmp_path / "law.md"
    law.write_text(_law_text().replace("الأشدّ يغلب\n", ""), encoding="utf-8")
    failures = _run(gate.check_law_contract, monkeypatch, LAW_DOC=law)
    assert any("الأشدّ يغلب" in failure for failure in failures)


def test_an_escape_hatch_without_its_verdict_is_rejected(tmp_path: Path, monkeypatch) -> None:
    """حذف «ملغى» من سطر منفذٍ يُعيد المنفذ حيّاً — يجب أن يحمرّ."""
    law = tmp_path / "law.md"
    hatch = "أو مراجع مستقل"
    law.write_text(
        _law_text().replace(f"| «{hatch}» | **ملغى**: سبب |", f"| «{hatch}» | سبب |"),
        encoding="utf-8",
    )
    failures = _run(gate.check_escape_hatches, monkeypatch, LAW_DOC=law)
    assert any(hatch in failure for failure in failures)


def test_an_invented_escape_hatch_is_rejected(tmp_path: Path, monkeypatch) -> None:
    """عبارةٌ لا توجد في D-318 لا يُحكم عليها باسمه."""
    d318 = tmp_path / "d318.md"
    d318.write_text("نصٌّ لا يحمل أيّ منفذ", encoding="utf-8")
    law = tmp_path / "law.md"
    law.write_text(_law_text(), encoding="utf-8")
    failures = _run(gate.check_escape_hatches, monkeypatch, LAW_DOC=law, D318_DOC=d318)
    assert any("لم تعد في D-318" in failure for failure in failures)


def test_a_removed_enforcing_symbol_is_rejected(tmp_path: Path, monkeypatch) -> None:
    """قاعدةٌ يُحذف رمز فارضها من موطنها تصير نثراً — يجب أن يحمرّ."""
    root = tmp_path
    for home in gate.REQUIRED_HOMES:
        rel, symbol = home.split("::", 1)
        target = root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        previous = target.read_text(encoding="utf-8") if target.exists() else ""
        target.write_text(previous + f"{symbol} = 1\n", encoding="utf-8")
    victim = root / "shared/research/value_chain.py"
    victim.write_text(victim.read_text(encoding="utf-8").replace("OFFER_FIELDS = 1\n", ""))
    law = tmp_path / "law.md"
    law.write_text(_law_text(), encoding="utf-8")
    failures = _run(gate.check_homes, monkeypatch, LAW_DOC=law, REPO_ROOT=root)
    assert any("OFFER_FIELDS" in failure for failure in failures)
    assert len(failures) == 1


def test_a_home_dropped_from_the_law_is_rejected(tmp_path: Path, monkeypatch) -> None:
    law = tmp_path / "law.md"
    home = "shared/research/economic_truth.py::atlas_view"
    law.write_text(_law_text().replace(f"`{home}`", ""), encoding="utf-8")
    failures = _run(gate.check_homes, monkeypatch, LAW_DOC=law)
    assert any(home in failure for failure in failures)


def test_registry_without_enforcer_is_rejected(tmp_path: Path, monkeypatch) -> None:
    registry = tmp_path / "registry.json"
    registry.write_text(
        json.dumps(
            {
                "constitutions": [
                    {
                        "id": "D-319",
                        "section": "0.31",
                        "law_docs": [gate.LAW_REL, gate.PIN_REL],
                        "enforcers": [],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    failures = _run(gate.check_registry_entry, monkeypatch, REGISTRY=registry)
    assert any(gate.GATE_NAME in failure for failure in failures)


def test_a_commented_out_ci_line_is_not_wiring(tmp_path: Path, monkeypatch) -> None:
    workflow = tmp_path / "ci.yml"
    workflow.write_text(
        "jobs:\n  guardrails:\n    run: |\n      set -euo pipefail\n"
        f"      # python scripts/fitness/{gate.GATE_NAME}\n",
        encoding="utf-8",
    )
    failures = _run(gate.check_ci_wiring, monkeypatch, CI_WORKFLOW=workflow)
    assert any("غير منفذ" in failure for failure in failures)


def _verbatim_repo(tmp_path: Path, monkeypatch, **overrides: object) -> Path:
    """مستودعٌ مصغّر: نصّان حرفيّان وبصمةٌ تطابقهما، ثمّ يُكسَر ما يُطلب كسره."""
    entries = []
    for rel in gate.VERBATIM_RELS:
        path = tmp_path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        data = f"# {rel}\nنصٌّ حرفي\n".encode()
        path.write_bytes(data)
        entries.append(
            {
                "path": rel,
                "sha256": hashlib.sha256(data).hexdigest(),
                "byte_count": len(data),
                "source_title": "عنوان",
                "source_pdf_sha256": "a" * 64,
                "source_pdf_bytes": 1000,
                "source_pdf_pages": 2,
                "confirmed_by_owner_on": "2026-10-20",
            }
        )
    pin_payload: dict[str, object] = {
        "verbatim_texts_status": gate.VERBATIM_CONFIRMED,
        "verbatim_texts": entries,
    }
    pin_payload.update(overrides)
    pin = tmp_path / "pin.json"
    pin.write_text(json.dumps(pin_payload), encoding="utf-8")
    monkeypatch.setattr(gate, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(gate, "PIN", pin)
    return tmp_path


def _verbatim_failures() -> list[str]:
    gate._FAILURES.clear()
    gate.check_verbatim_pins()
    return list(gate._FAILURES)


def test_matching_verbatim_texts_pass(tmp_path: Path, monkeypatch) -> None:
    _verbatim_repo(tmp_path, monkeypatch)
    assert _verbatim_failures() == []


def test_a_one_byte_change_in_a_verbatim_text_is_rejected(tmp_path: Path, monkeypatch) -> None:
    root = _verbatim_repo(tmp_path, monkeypatch)
    target = root / gate.VERBATIM_RELS[0]
    target.write_bytes(target.read_bytes() + b"x")
    assert any(gate.VERBATIM_RELS[0] in failure for failure in _verbatim_failures())


def test_a_missing_verbatim_text_is_rejected(tmp_path: Path, monkeypatch) -> None:
    root = _verbatim_repo(tmp_path, monkeypatch)
    (root / gate.VERBATIM_RELS[1]).unlink()
    assert any(gate.VERBATIM_RELS[1] in failure for failure in _verbatim_failures())


def test_a_verbatim_text_still_pending_confirmation_is_rejected(
    tmp_path: Path, monkeypatch
) -> None:
    _verbatim_repo(tmp_path, monkeypatch, verbatim_texts_status="PENDING_OWNER_CONFIRMATION")
    assert any(gate.VERBATIM_CONFIRMED in failure for failure in _verbatim_failures())


def test_a_dropped_verbatim_pin_is_rejected(tmp_path: Path, monkeypatch) -> None:
    _verbatim_repo(tmp_path, monkeypatch, verbatim_texts=[])
    failures = _verbatim_failures()
    assert all(any(rel in failure for failure in failures) for rel in gate.VERBATIM_RELS)


def test_a_verbatim_pin_without_its_source_pdf_hash_is_rejected(
    tmp_path: Path, monkeypatch
) -> None:
    root = _verbatim_repo(tmp_path, monkeypatch)
    pin = json.loads(gate.PIN.read_text(encoding="utf-8"))
    pin["verbatim_texts"][0]["source_pdf_sha256"] = "not-a-hash"
    gate.PIN.write_text(json.dumps(pin), encoding="utf-8")
    assert root and any("source_pdf_sha256" in failure for failure in _verbatim_failures())


def test_a_byline_in_a_verbatim_text_is_rejected(tmp_path: Path, monkeypatch) -> None:
    """سطر التوقيع (تاريخ · @حساب) لا يدخل المستودع العامّ؛ الشكل يُرفض لا الاسم."""
    root = _verbatim_repo(tmp_path, monkeypatch)
    target = root / gate.VERBATIM_RELS[0]
    data = target.read_bytes() + "Oct 11, 2026 · @someone\n".encode()
    target.write_bytes(data)
    pin = json.loads(gate.PIN.read_text(encoding="utf-8"))
    pin["verbatim_texts"][0].update(sha256=hashlib.sha256(data).hexdigest(), byte_count=len(data))
    gate.PIN.write_text(json.dumps(pin), encoding="utf-8")
    assert any("توقيع" in failure for failure in _verbatim_failures())


def test_unprotected_verbatim_texts_are_rejected(tmp_path: Path, monkeypatch) -> None:
    policy = tmp_path / "policy.json"
    policy.write_text(
        json.dumps({"protected_paths": [gate.LAW_REL, gate.PIN_REL, gate.GATE_REL, gate.TEST_REL]}),
        encoding="utf-8",
    )
    failures = _run(gate.check_protected_artifacts, monkeypatch, POLICY=policy)
    assert set(gate.VERBATIM_RELS) <= {failure.rsplit(": ", 1)[-1] for failure in failures}


def test_unprotected_artifacts_are_rejected(tmp_path: Path, monkeypatch) -> None:
    policy = tmp_path / "policy.json"
    policy.write_text(json.dumps({"protected_paths": []}), encoding="utf-8")
    failures = _run(gate.check_protected_artifacts, monkeypatch, POLICY=policy)
    assert {gate.LAW_REL, gate.PIN_REL, gate.GATE_REL, gate.TEST_REL} <= {
        failure.rsplit(": ", 1)[-1] for failure in failures
    }
