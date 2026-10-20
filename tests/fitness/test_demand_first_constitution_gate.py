"""اختبارات سلبية لبوابة قانون «الألم أولاً» (D-321): كل اختبارٍ يكسر شيئاً عمداً."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from scripts.fitness import check_demand_first_constitution as gate


def _law_text() -> str:
    markers = "\n".join(gate.REQUIRED_MARKERS)
    homes = "\n".join(f"| قاعدة | فرض | `{home}` |" for home in gate.REQUIRED_HOMES)
    return f"{markers}\n{homes}\n"


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
    assert any("بايت" in failure for failure in failures)


def test_a_missing_marker_is_rejected(tmp_path: Path, monkeypatch) -> None:
    law = tmp_path / "law.md"
    marker = gate.REQUIRED_MARKERS[0]
    law.write_text(_law_text().replace(f"{marker}\n", ""), encoding="utf-8")
    failures = _run(gate.check_law_contract, monkeypatch, LAW_DOC=law)
    assert any(marker in failure for failure in failures)


def test_a_removed_enforcing_symbol_is_rejected(tmp_path: Path, monkeypatch) -> None:
    """قاعدةٌ يُحذف رمز فارضها من موطنها تصير نثراً — يجب أن يحمرّ."""
    dropped = gate.REQUIRED_HOMES[0].split("::", 1)[1]
    symbols: dict[str, list[str]] = {}
    for home in gate.REQUIRED_HOMES[1:]:
        rel, symbol = home.split("::", 1)
        symbols.setdefault(rel, []).append(symbol)
    symbols.setdefault(gate.REQUIRED_HOMES[0].split("::", 1)[0], [])
    for rel, names in symbols.items():
        target = tmp_path / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("\n".join(name for name in names if name != dropped) + "\n", "utf-8")
    law = tmp_path / "law.md"
    law.write_text(_law_text(), encoding="utf-8")
    failures = _run(gate.check_homes, monkeypatch, LAW_DOC=law, REPO_ROOT=tmp_path)
    assert any(dropped in failure for failure in failures)


def test_the_law_must_stand_first_in_claude_md(tmp_path: Path, monkeypatch) -> None:
    """القانون الأعلى يُقرأ قبل أيّ قسم: سطره في رأس CLAUDE.md قبل أوّل فاصل."""
    claude = tmp_path / "CLAUDE.md"
    claude.write_text(f"# CogniForge\n> نصّ\n---\n> {gate.TOP_MARKER}\n", encoding="utf-8")
    failures = _run(gate.check_top_precedence, monkeypatch, CLAUDE_MD=claude)
    assert failures


def test_an_unregistered_constitution_is_rejected(tmp_path: Path, monkeypatch) -> None:
    registry = tmp_path / "registry.json"
    registry.write_text(json.dumps({"core_doctrines": [], "constitutions": []}), encoding="utf-8")
    failures = _run(gate.check_registry_entry, monkeypatch, REGISTRY=registry)
    assert any(gate.CONSTITUTION_ID in failure for failure in failures)


def test_a_commented_ci_line_does_not_count_as_wiring(tmp_path: Path, monkeypatch) -> None:
    ci = tmp_path / "ci.yml"
    ci.write_text(
        "jobs:\n  guardrails:\n    steps:\n      - run: |\n          set -euo pipefail\n"
        f"          # python scripts/fitness/{gate.GATE_NAME}\n  other:\n    steps: []\n",
        encoding="utf-8",
    )
    failures = _run(gate.check_ci_wiring, monkeypatch, CI_WORKFLOW=ci)
    assert any(gate.GATE_NAME in failure for failure in failures)


def test_an_unprotected_governing_artifact_is_rejected(tmp_path: Path, monkeypatch) -> None:
    policy = tmp_path / "policy.json"
    policy.write_text(json.dumps({"protected_paths": []}), encoding="utf-8")
    failures = _run(gate.check_protected_artifacts, monkeypatch, POLICY=policy)
    assert any(gate.LAW_REL in failure for failure in failures)
