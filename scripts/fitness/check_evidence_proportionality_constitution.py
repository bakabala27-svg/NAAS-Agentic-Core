#!/usr/bin/env python3
"""بوابة دستور تناسب الدليل وهندسة الثقة (D-318).

تفشل البوابة عند نقص القانون، أو فك ربطه من سجل السلطة/نقاط الدخول/CI، أو حذف
درجة أو قانون أو قاعدة NAAS، أو إخراج الأصول الحاكمة من الحماية. هي فحص بنيوي
ولا تدّعي إثبات صحة الإنتاج. Exit 0 = العقد حاضر وموصول؛ Exit 1 = انتهاك.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
LAW_REL = "docs/architecture/EVIDENCE_PROPORTIONALITY_CONSTITUTION.md"
PIN_REL = "docs/governance/D318_IMMUTABLE_TEXT.json"
GATE_REL = "scripts/fitness/check_evidence_proportionality_constitution.py"
TEST_REL = "tests/fitness/test_evidence_proportionality_constitution_gate.py"
LAW_DOC = REPO_ROOT / LAW_REL
PIN = REPO_ROOT / PIN_REL
REGISTRY = REPO_ROOT / "docs/governance/CONSTITUTION_REGISTRY.json"
POLICY = REPO_ROOT / "docs/governance/ENGINEERING_GOVERNANCE_POLICY.json"
CLAUDE_MD = REPO_ROOT / "CLAUDE.md"
AGENTS_MD = REPO_ROOT / "AGENTS.md"
ENGINEERING = REPO_ROOT / "ENGINEERING_CONSTITUTION.md"
CI_WORKFLOW = REPO_ROOT / ".github/workflows/ci.yml"

CONSTITUTION_ID = "D-318"
CONSTITUTION_SECTION = "0.30"
GATE_NAME = Path(GATE_REL).name

EVIDENCE_LEVELS = tuple(f"E{number}" for number in range(8))
LAWS = tuple(f"L{number}" for number in range(1, 13))
NAAS_RULES = tuple(f"NF-{number}" for number in range(1, 6))
RISK_ZONES = ("EXPERIMENT", "PRODUCT", "CRITICAL")
REQUIRED_MARKERS = (
    "يجب أن تتناسب قوة الدليل مع كلفة الخطأ",
    "لا يجوز تجاوز حكمٍ أو إسقاط معنى أو تخفيف قيد أو تغيير حرف",
    "اختلاف بايت واحد يجعل البوابة حمراء",
    "لا ادعاء فوق دليله",
    "استقلال المولد والحكم",
    "الحالة المجهولة ليست فشلًا ولا نجاحًا",
    "النموذج يقترح والنظام يقرر",
    "protected_paths_changed",
    "touched_files - declared_files",
    "مراجعة بشرية مستقلة",
)

_FAILURES: list[str] = []


def _fail(message: str) -> None:
    _FAILURES.append(message)
    print(f"❌ D-318: {message}", file=sys.stderr)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def check_files_exist() -> None:
    for path in (
        LAW_DOC,
        PIN,
        REGISTRY,
        POLICY,
        CLAUDE_MD,
        AGENTS_MD,
        ENGINEERING,
        CI_WORKFLOW,
    ):
        if not path.is_file():
            try:
                rel = path.relative_to(REPO_ROOT)
            except ValueError:
                rel = path
            _fail(f"ملف حاكم غائب: {rel}")


def check_law_contract() -> None:
    if not LAW_DOC.is_file():
        return
    text = _read(LAW_DOC)
    for level in EVIDENCE_LEVELS:
        if not re.search(rf"\|\s*`{level}`\s*\|", text):
            _fail(f"درجة الدليل {level} غائبة من السلم")
    for law in LAWS:
        if not re.search(rf"^### {re.escape(law)}\s+—", text, flags=re.MULTILINE):
            _fail(f"القانون {law} غائب")
    for rule in NAAS_RULES:
        if not re.search(rf"\|\s*`{re.escape(rule)}\b", text):
            _fail(f"قاعدة NAAS {rule} غائبة")
    for zone in RISK_ZONES:
        if f"`{zone}`" not in text:
            _fail(f"منطقة الخطر {zone} غائبة")
    for marker in REQUIRED_MARKERS:
        if marker not in text:
            _fail(f"علامة دستورية غائبة: «{marker}»")
    if "لا يستطيع نص داخل المستودع" not in text:
        _fail("حد الحماية الواقعي غائب؛ النص لا يجوز أن يدعي استحالة ميتافيزيقية")


def check_byte_pin() -> None:
    """ارفض أي اختلاف بايت واحد بين القانون وبصمته الدستورية."""
    if not LAW_DOC.is_file() or not PIN.is_file():
        return
    try:
        pin = json.loads(_read(PIN))
    except json.JSONDecodeError as error:
        _fail(f"ملف البصمة JSON غير صالح: {error}")
        return
    law_bytes = LAW_DOC.read_bytes()
    actual = hashlib.sha256(law_bytes).hexdigest()
    if pin.get("canonical_text") != LAW_REL:
        _fail("ملف البصمة لا يشير إلى النص القانوني D-318")
    if pin.get("sha256") != actual:
        _fail("اختلف حرف/بايت من D-318 عن البصمة القانونية؛ يلزم تعديل دستوري مستقل")
    if pin.get("byte_count") != len(law_bytes):
        _fail("عدد بايتات D-318 لا يطابق السجل القانوني")


def check_registry_entry() -> None:
    if not REGISTRY.is_file():
        return
    try:
        registry = json.loads(_read(REGISTRY))
    except json.JSONDecodeError as error:
        _fail(f"السجل الدستوري JSON غير صالح: {error}")
        return
    rows = list(registry.get("core_doctrines", [])) + list(registry.get("constitutions", []))
    row = next((item for item in rows if item.get("id") == CONSTITUTION_ID), None)
    if row is None:
        _fail(f"{CONSTITUTION_ID} غير مسجل")
        return
    if str(row.get("section")) != CONSTITUTION_SECTION:
        _fail(f"قسم السجل ليس {CONSTITUTION_SECTION}")
    if LAW_REL not in row.get("law_docs", []):
        _fail(f"السجل لا يسمّي وثيقة القانون {LAW_REL}")
    if GATE_NAME not in row.get("enforcers", []):
        _fail(f"السجل لا يسمّي الفارض {GATE_NAME}")


def check_entrypoints() -> None:
    expected = (
        (CLAUDE_MD, f"## {CONSTITUTION_SECTION}.", "CLAUDE.md"),
        (AGENTS_MD, LAW_REL, "AGENTS.md"),
        (ENGINEERING, LAW_REL, "ENGINEERING_CONSTITUTION.md"),
    )
    for path, marker, label in expected:
        if path.is_file() and marker not in _read(path):
            _fail(f"{label} لا يحمل نقطة الدخول المطلوبة: {marker}")


def check_ci_wiring() -> None:
    if not CI_WORKFLOW.is_file():
        return
    text = _read(CI_WORKFLOW)
    start = text.find("  guardrails:")
    if start < 0:
        _fail("وظيفة guardrails غائبة")
        return
    guardrails = text[start:]
    if GATE_NAME not in guardrails:
        _fail(f"{GATE_NAME} غير منفذ في guardrails")
    if "set -euo pipefail" not in guardrails:
        _fail("guardrails لا يعلن set -euo pipefail")


def _covered_by_pattern(path: str, patterns: list[str]) -> bool:
    """تغطية محافظة لأنماط الحماية المستعملة حاليًا (exact و/**)."""
    return any(
        pattern == path or (pattern.endswith("/**") and path.startswith(pattern[:-3] + "/"))
        for pattern in patterns
    )


def check_protected_artifacts() -> None:
    if not POLICY.is_file():
        return
    try:
        policy = json.loads(_read(POLICY))
    except json.JSONDecodeError as error:
        _fail(f"سياسة الحوكمة JSON غير صالحة: {error}")
        return
    protected = policy.get("protected_paths", [])
    for rel in (LAW_REL, PIN_REL, GATE_REL, TEST_REL):
        if not _covered_by_pattern(rel, protected):
            _fail(f"الأصل الحاكم غير محمي بسياسة التعديل: {rel}")


def main() -> int:
    _FAILURES.clear()
    check_files_exist()
    check_law_contract()
    check_byte_pin()
    check_registry_entry()
    check_entrypoints()
    check_ci_wiring()
    check_protected_artifacts()
    if _FAILURES:
        print(
            f"check_evidence_proportionality_constitution: FAIL ({len(_FAILURES)})", file=sys.stderr
        )
        return 1
    print("check_evidence_proportionality_constitution: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
