#!/usr/bin/env python3
"""بوابة دستور أطلس المؤسس — «لا سحر بلا دليل» (D-319).

تفشل البوابة عند نقص القانون أو تغيّر بايتٍ واحد منه أو من النصّين الحرفيّين اللذين أكّدهما
المالك، أو فكّ ربطه من سجلّ السلطة ونقاط الدخول وCI، أو حذف حكمٍ على منفذٍ من منافذ D-318،
أو غياب موطنٍ مسمّى لقاعدةٍ مفروضة (ملفٌّ محذوف أو رمزٌ أُزيل)، أو إخراج الأصول الحاكمة من
الحماية. فحصٌ بنيوي لا يدّعي إثبات صحة الإنتاج. Exit 0 = العقد حاضر وموصول؛ Exit 1 = انتهاك.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
LAW_REL = "docs/architecture/FOUNDER_ATLAS_CONSTITUTION.md"
PIN_REL = "docs/governance/D319_IMMUTABLE_TEXT.json"
GATE_REL = "scripts/fitness/check_founder_atlas_constitution.py"
TEST_REL = "tests/fitness/test_founder_atlas_constitution_gate.py"
D318_REL = "docs/architecture/EVIDENCE_PROPORTIONALITY_CONSTITUTION.md"
LAW_DOC = REPO_ROOT / LAW_REL
PIN = REPO_ROOT / PIN_REL
D318_DOC = REPO_ROOT / D318_REL
REGISTRY = REPO_ROOT / "docs/governance/CONSTITUTION_REGISTRY.json"
POLICY = REPO_ROOT / "docs/governance/ENGINEERING_GOVERNANCE_POLICY.json"
CLAUDE_MD = REPO_ROOT / "CLAUDE.md"
AGENTS_MD = REPO_ROOT / "AGENTS.md"
ENGINEERING = REPO_ROOT / "ENGINEERING_CONSTITUTION.md"
CI_WORKFLOW = REPO_ROOT / ".github/workflows/ci.yml"

CONSTITUTION_ID = "D-319"
CONSTITUTION_SECTION = "0.31"
GATE_NAME = Path(GATE_REL).name

#: النصّان الحرفيّان لوثيقتَي المالك (2026-10-11)، مثبَّتان بالبايت في PIN بعد تأكيده.
VERBATIM_RELS = (
    "docs/architecture/FOUNDER_ATLAS_VERBATIM.md",
    "docs/architecture/EVIDENCE_PROPORTIONALITY_VERBATIM.md",
)
VERBATIM_CONFIRMED = "CONFIRMED_BY_OWNER"
_SHA256 = re.compile(r"[0-9a-f]{64}")
_ISO_DATE = re.compile(r"\d{4}-\d{2}-\d{2}")
#: شكل سطر التوقيع في ملفّ PDF (تاريخ · @حساب). يُرفض الشكل، فلا يُكتب اسمٌ في الفارض.
_BYLINE = re.compile(r"(?m)^[A-Z][a-z]{2} \d{1,2}, \d{4} · @\S+")

REQUIRED_MARKERS = (
    "لا سحر بلا دليل",
    "لا يجوز تجاوز حكمٍ أو إسقاط معنى أو تخفيف قيد أو تغيير حرف",
    "اختلاف بايت واحد يجعل البوابة حمراء",
    "نصّ المالك الحرفي يغلب كل ملخّص",
    "الأشدّ يغلب",
    "أكّد المالك النسخ",
    "لا تقول PIVOT ولا STOP",
    "لا يستطيع نص داخل المستودع",
    "مراجعة بشرية مستقلة",
    "لا يفرضها فارضٌ آلي",
)

#: منافذ D-318 التي يلغيها هذا الدستور أو يكمّلها. كل عبارةٍ يجب أن توجد حرفياً في D-318،
#: وأن تُقتبَس في القانون على سطرٍ يحمل حكمها — فلا يُحذف حكمٌ ولا يُخترَع منفذ.
D318_ESCAPE_HATCHES = (
    "أو بتبرير مكتوب يثبت عدم الانطباق",
    "أو مراجع مستقل",
    "في المنطقة الحرجة",
    "بديل مبرر",
    "في مسار حساس",
    "في مهمة منتج",
    "في منطقة الاعتماد",
    "كلمتا **«يعمل»** و**«جاهز»** محجوزتان لـE5 فأعلى",
    "عميل ومشكلة ونتيجة مقيسة، ثم دفعة/عقد للدعوى المدفوعة",
)
_VERDICTS = ("**ملغى**", "**مكمَّل**")

#: مواطن القواعد المفروضة آلياً. كلٌّ يجب أن يُذكر في القانون، وأن يوجد ملفّه ورمزه.
REQUIRED_HOMES = (
    "shared/research/value_chain.py::FORBIDDEN_TERMS",
    "tests/unit/tools/test_outreach_truth.py::test_catalog_thesis_wording_states_no_unmeasured_promise",
    "tools/hard_currency_engine/buyer_claims.py::approval_seeking",
    "tools/hard_currency_engine/buyer_claims.py::full_automation",
    "tools/hard_currency_engine/buyer_claims.py::_PAYMENT_RAIL",
    "shared/research/value_chain.py::ACTIVATION_CLAIMS",
    "shared/research/value_chain.py::OFFER_FIELDS",
    "shared/research/value_chain.py::_offer_problems",
    "shared/research/value_chain.py::_proof_scope_problems",
    "shared/research/value_chain.py::MIN_REPLYING_ENTITIES",
    "tests/unit/tools/test_outreach_truth.py::test_one_package_price_everywhere",
    "tests/shared/test_contact_ledger.py::test_a_reply_or_any_non_money_row_never_moves_paid_customers_or_gate_c",
    "scripts/fitness/check_code_acceptance.py::validate_verification_claims",
    "scripts/fitness/check_engineering_governance.py::target_operating_cost",
    "scripts/fitness/check_code_acceptance.py::validate_runtime_evidence",
    "scripts/fitness/check_hard_currency_engine.py::FORBIDDEN_SEND_MODULES",
    "tools/hard_currency_engine/crm_dispatcher.py::CONFIGURATION_OUTBOUND",
    "tests/shared/test_economic_truth.py::test_every_claim_answers_the_final_reporting_standard",
    "shared/research/economic_decision.py::DECIDE_WITHIN_DAYS",
    "shared/research/economic_truth.py::atlas_view",
    "shared/research/opportunity_score.py::rank",
    "shared/evidence/gate.py::verdict",
    "scripts/fitness/check_code_acceptance.py::validate_evidence_report",
)

_FAILURES: list[str] = []


def _fail(message: str) -> None:
    _FAILURES.append(message)
    print(f"❌ D-319: {message}", file=sys.stderr)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def check_files_exist() -> None:
    for path in (LAW_DOC, PIN, D318_DOC, REGISTRY, POLICY, CLAUDE_MD, AGENTS_MD, ENGINEERING):
        if not path.is_file():
            try:
                rel = path.relative_to(REPO_ROOT)
            except ValueError:
                rel = path
            _fail(f"ملف حاكم غائب: {rel}")
    if not CI_WORKFLOW.is_file():
        _fail("ملف CI غائب: .github/workflows/ci.yml")


def check_law_contract() -> None:
    if not LAW_DOC.is_file():
        return
    text = _read(LAW_DOC)
    for marker in REQUIRED_MARKERS:
        if marker not in text:
            _fail(f"علامة دستورية غائبة: «{marker}»")


def check_escape_hatches() -> None:
    """كل منفذٍ في D-318 مقتبسٌ حرفياً، وحكمه مكتوبٌ على سطره (D-319 §4)."""
    if not LAW_DOC.is_file() or not D318_DOC.is_file():
        return
    law_lines = _read(LAW_DOC).splitlines()
    d318 = _read(D318_DOC)
    for hatch in D318_ESCAPE_HATCHES:
        if hatch not in d318:
            _fail(f"العبارة «{hatch}» لم تعد في D-318 — راجع الاقتباس قبل أي حكم")
        rows = [line for line in law_lines if f"«{hatch}" in line or hatch in line]
        if not any(any(verdict in row for verdict in _VERDICTS) for row in rows):
            _fail(f"منفذ D-318 «{hatch}» بلا حكمٍ مكتوب (ملغى أو مكمَّل)")


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
        _fail("ملف البصمة لا يشير إلى النص القانوني D-319")
    if pin.get("sha256") != hashlib.sha256(law_bytes).hexdigest():
        _fail("اختلف حرف/بايت من D-319 عن البصمة القانونية؛ يلزم تعديل دستوري مستقل")
    if pin.get("byte_count") != len(law_bytes):
        _fail("عدد بايتات D-319 لا يطابق السجل القانوني")


def _verbatim_entry_problems(entry: dict, rel: str) -> list[str]:
    path = REPO_ROOT / rel
    if not path.is_file():
        return [f"النصّ الحرفي غائب: {rel}"]
    data = path.read_bytes()
    problems: list[str] = []
    if entry.get("sha256") != hashlib.sha256(data).hexdigest():
        problems.append(f"اختلف بايت من النصّ الحرفي عن بصمته: {rel}")
    if entry.get("byte_count") != len(data):
        problems.append(f"عدد بايتات النصّ الحرفي لا يطابق البصمة: {rel}")
    if not _SHA256.fullmatch(str(entry.get("source_pdf_sha256", ""))):
        problems.append(f"source_pdf_sha256 غير صالح لـ {rel}")
    pages = entry.get("source_pdf_pages")
    if not isinstance(pages, int) or isinstance(pages, bool) or pages < 1:
        problems.append(f"source_pdf_pages غير صالح لـ {rel}")
    if not _ISO_DATE.fullmatch(str(entry.get("confirmed_by_owner_on", ""))):
        problems.append(f"confirmed_by_owner_on غير صالح لـ {rel}")
    if _BYLINE.search(data.decode("utf-8", errors="replace")):
        problems.append(f"سطر توقيعٍ باسم حسابٍ داخل النصّ الحرفي: {rel}")
    return problems


def check_verbatim_pins() -> None:
    """النصّان الحرفيّان موجودان ومطابقان لبصمتهما بالبايت، ومؤكَّدان من المالك."""
    if not PIN.is_file():
        return
    try:
        pin = json.loads(_read(PIN))
    except json.JSONDecodeError as error:
        _fail(f"ملف البصمة JSON غير صالح: {error}")
        return
    if pin.get("verbatim_texts_status") != VERBATIM_CONFIRMED:
        _fail(f"حالة النصّين الحرفيّين ليست {VERBATIM_CONFIRMED}")
    entries = pin.get("verbatim_texts")
    by_path = {
        str(entry.get("path")): entry
        for entry in (entries if isinstance(entries, list) else [])
        if isinstance(entry, dict)
    }
    for rel in VERBATIM_RELS:
        entry = by_path.get(rel)
        if entry is None:
            _fail(f"لا بصمة للنصّ الحرفي: {rel}")
            continue
        for problem in _verbatim_entry_problems(entry, rel):
            _fail(problem)


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
    for rel in (LAW_REL, PIN_REL, GATE_REL, TEST_REL, *VERBATIM_RELS):
        if not _covered_by_pattern(rel, protected):
            _fail(f"الأصل الحاكم غير محمي بسياسة التعديل: {rel}")


def main() -> int:
    _FAILURES.clear()
    check_files_exist()
    check_law_contract()
    check_escape_hatches()
    check_homes()
    check_byte_pin()
    check_verbatim_pins()
    check_registry_entry()
    check_entrypoints()
    check_ci_wiring()
    check_protected_artifacts()
    if _FAILURES:
        print(f"check_founder_atlas_constitution: FAIL ({len(_FAILURES)})", file=sys.stderr)
        return 1
    print("check_founder_atlas_constitution: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
