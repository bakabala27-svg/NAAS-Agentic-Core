#!/usr/bin/env python3
"""بوابة قانون «الألم أولاً» — لا بناء بلا ألمٍ يُبحث عن حلّه ودافعٍ موجود (D-321).

تفشل البوابة عند نقص القانون أو تغيّر بايتٍ واحد منه، أو فكّ ربطه من سجلّ السلطة ونقاط
الدخول وCI، أو نزوله عن رأس ``CLAUDE.md``، أو غياب موطنٍ مسمّى لقاعدةٍ مفروضة (ملفٌّ محذوف أو
رمزٌ أُزيل)، أو إخراج أصوله من الحماية. القواعد نفسها تفرضها ``check_value_chain`` و
``check_code_acceptance``؛ هذه البوابة تحرس أنّها ما زالت موصولة. فحصٌ بنيوي لا يدّعي إثبات
الطلب. Exit 0 = العقد حاضر وموصول؛ Exit 1 = انتهاك.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
LAW_REL = "docs/architecture/DEMAND_FIRST_CONSTITUTION.md"
PIN_REL = "docs/governance/D321_IMMUTABLE_TEXT.json"
GATE_REL = "scripts/fitness/check_demand_first_constitution.py"
TEST_REL = "tests/fitness/test_demand_first_constitution_gate.py"
LAW_DOC = REPO_ROOT / LAW_REL
PIN = REPO_ROOT / PIN_REL
REGISTRY = REPO_ROOT / "docs/governance/CONSTITUTION_REGISTRY.json"
POLICY = REPO_ROOT / "docs/governance/ENGINEERING_GOVERNANCE_POLICY.json"
CLAUDE_MD = REPO_ROOT / "CLAUDE.md"
AGENTS_MD = REPO_ROOT / "AGENTS.md"
ENGINEERING = REPO_ROOT / "ENGINEERING_CONSTITUTION.md"
CI_WORKFLOW = REPO_ROOT / ".github/workflows/ci.yml"

CONSTITUTION_ID = "D-321"
CONSTITUTION_SECTION = "0.32"
GATE_NAME = Path(GATE_REL).name
#: سطر القانون الأعلى في رأس CLAUDE.md، قبل أوّل فاصل ``---``: يُقرأ قبل أيّ قسم.
TOP_MARKER = "الألم أولاً (D-321"

REQUIRED_MARKERS = (
    "أكبر خطرٍ كارثي هو بناء منتجٍ بلا سوق",
    "من يتألّم",
    "من يبحث عن الحلّ الآن",
    "من يدفع",
    "الدليل العامّ يُرخّص اختبار مشترٍ فقط",
    "ثلاث جهاتٍ متمايزة ردّت في السجلّ",
    "ما بُني قبل الطلب يُعرَض ولا يُحذف",
    "الدَّين يتقلّص فقط",
    "لا يقول PIVOT ولا STOP",
    "الأشدّ يغلب",
    "اختلاف بايت واحد يجعل البوابة حمراء",
    "لا يستطيع نص داخل المستودع",
    "مراجعة بشرية مستقلة",
    "لا يفرضها فارضٌ آلي",
)

#: مواطن القواعد المفروضة آلياً. كلٌّ يجب أن يُذكر في القانون، وأن يوجد ملفّه ورمزه.
REQUIRED_HOMES = (
    "shared/research/value_chain.py::DEMAND_LEGS",
    "shared/research/value_chain.py::CODE_LINKS",
    "shared/research/value_chain.py::MIN_REPLYING_ENTITIES",
    "shared/research/value_chain.py::_demand_state",
    "shared/research/value_chain.py::_demand_declaration_problems",
    "shared/research/value_chain.py::_built_before_demand_problems",
    "shared/research/value_chain.py::BUILT_BEFORE_DEMAND",
    "scripts/fitness/check_value_chain.py::built_before_demand",
    "scripts/fitness/check_code_acceptance.py::validate_demand_first",
    "scripts/fitness/check_code_acceptance.py::current_added_paths",
    "docs/governance/ENGINEERING_GOVERNANCE_POLICY.json::product_code_prefixes",
)

_FAILURES: list[str] = []


def _fail(message: str) -> None:
    _FAILURES.append(message)
    print(f"❌ D-321: {message}", file=sys.stderr)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def check_files_exist() -> None:
    for path in (LAW_DOC, PIN, REGISTRY, POLICY, CLAUDE_MD, AGENTS_MD, ENGINEERING, CI_WORKFLOW):
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
    for marker in REQUIRED_MARKERS:
        if marker not in text:
            _fail(f"علامة دستورية غائبة: «{marker}»")


def check_homes() -> None:
    """كل قاعدةٍ مفروضة تسمّي موطنها، والموطن موجود: ملفٌّ ورمزٌ فيه."""
    if not LAW_DOC.is_file():
        return
    text = _read(LAW_DOC)
    for home in REQUIRED_HOMES:
        if f"`{home}`" not in text:
            _fail(f"الموطن {home} غير مذكور في القانون")
        rel, symbol = home.split("::", 1)
        path = REPO_ROOT / rel
        if not path.is_file():
            _fail(f"ملف الموطن غائب: {rel}")
        elif not re.search(rf"\b{re.escape(symbol)}\b", _read(path)):
            _fail(f"الرمز {symbol} غائب من {rel} — قاعدةٌ بلا فارض")


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
    if pin.get("canonical_text") != LAW_REL:
        _fail("ملف البصمة لا يشير إلى النص القانوني D-321")
    if pin.get("sha256") != hashlib.sha256(law_bytes).hexdigest():
        _fail("اختلف حرف/بايت من D-321 عن البصمة القانونية؛ يلزم تعديل دستوري مستقل")
    if pin.get("byte_count") != len(law_bytes):
        _fail("عدد بايتات D-321 لا يطابق السجل القانوني")


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
    for rel in (LAW_REL, PIN_REL):
        if rel not in row.get("law_docs", []):
            _fail(f"السجل لا يسمّي {rel}")
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


def check_top_precedence() -> None:
    """القانون الأعلى يُقرأ قبل أيّ قسم: سطره في رأس CLAUDE.md قبل أوّل فاصل ``---``."""
    if not CLAUDE_MD.is_file():
        return
    head: list[str] = []
    for line in _read(CLAUDE_MD).splitlines():
        if line.strip() == "---":
            break
        head.append(line)
    if not any(line.startswith(">") and TOP_MARKER in line for line in head):
        _fail(f"سطر «{TOP_MARKER}» ليس في رأس CLAUDE.md قبل أوّل فاصل")


def _job_block(text: str, job: str) -> str | None:
    """أسطر وظيفةٍ واحدة بلا تعليقات: من رأسها إلى رأس الوظيفة التالية."""
    lines = text.splitlines()
    start = next((i for i, line in enumerate(lines) if line.rstrip() == f"  {job}:"), None)
    if start is None:
        return None
    block: list[str] = []
    for line in lines[start + 1 :]:
        if re.match(r"^(  )?\S", line):
            break
        if not line.lstrip().startswith("#"):
            block.append(line)
    return "\n".join(block)


def check_ci_wiring() -> None:
    if not CI_WORKFLOW.is_file():
        return
    guardrails = _job_block(_read(CI_WORKFLOW), "guardrails")
    if guardrails is None:
        _fail("وظيفة guardrails غائبة")
        return
    if GATE_NAME not in guardrails:
        _fail(f"{GATE_NAME} غير منفذ في guardrails")
    if "set -euo pipefail" not in guardrails:
        _fail("guardrails لا يعلن set -euo pipefail")


def _covered_by_pattern(path: str, patterns: list[str]) -> bool:
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
    protected = [str(pattern) for pattern in policy.get("protected_paths", [])]
    for rel in (LAW_REL, PIN_REL, GATE_REL, TEST_REL):
        if not _covered_by_pattern(rel, protected):
            _fail(f"الأصل الحاكم غير محمي بسياسة التعديل: {rel}")


def main() -> int:
    _FAILURES.clear()
    check_files_exist()
    check_law_contract()
    check_homes()
    check_byte_pin()
    check_registry_entry()
    check_entrypoints()
    check_top_precedence()
    check_ci_wiring()
    check_protected_artifacts()
    if _FAILURES:
        print(f"check_demand_first_constitution: FAIL ({len(_FAILURES)})", file=sys.stderr)
        return 1
    print("check_demand_first_constitution: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
