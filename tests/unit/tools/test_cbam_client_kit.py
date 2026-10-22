"""عدّة العميل الأولى (CBAM) تُفحَص كالكود: أرقامُها وسنداتُها وترتيبُها.

**لماذا هذا الاختبار موجود.** العدّة في
``docs/commercial/outreach/CBAM_FIRST_CLIENT_KIT_2026-10-22/`` تُقرأ من مشترٍ ومحقّق
أوروبيٍّ كلمةً بكلمة، وتحمل رقماً واحداً هو كلّ قيمتها: الوفر لكلّ طنّ. وثلاثة أنواع
من الانحراف تجعلها تكذب بلا أن يلاحظ أحد:

- رقمٌ في ``README.md`` لا يقابله سندٌ في ``EVIDENCE.csv`` (أو سندٌ معرَّفٌ ولا يُستعمل)؛
- يدٌ تُحرّر ``CBAM_ECONOMICS.json`` بعد توليده، فيصير الملفّ حقيقةً ثانية؛
- درجةُ مرشّحٍ لا تساوي مجموع معاييره، أو رتبتان متساويتان، فيُقرأ ترتيبٌ لا وجود له.

الاختبار لا يقرأ الشبكة ولا ساعة الحائط: يقرأ الملفّات ويشغّل الآلة الحسابية نفسها.
الحالات السلبية الستّ تُبرهن أنّ الفحص يحمرّ عند كلّ انحرافٍ من هذه الفئات — لا أنّه
يمرّ لأنّه لا يفحص.

**التشغيل:** ``pytest tests/unit/tools/test_cbam_client_kit.py -q``
"""

from __future__ import annotations

import csv
import importlib.util
import io
import json
import re
import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
KIT = REPO_ROOT / "docs/commercial/outreach/CBAM_FIRST_CLIENT_KIT_2026-10-22"
README = KIT / "README.md"
EVIDENCE = KIT / "EVIDENCE.csv"
CANDIDATES = KIT / "CANDIDATES.csv"
ECONOMICS = KIT / "CBAM_ECONOMICS.json"
SCRIPT = KIT / "cbam_economics.py"

EVIDENCE_TYPES = frozenset(
    {"FACT_PRIMARY", "FACT_SECONDARY", "FACT_REPO", "MARKET_ESTIMATE", "DERIVED"}
)
CONFIDENCE = frozenset({"HIGH", "MEDIUM", "LOW"})
GATES = frozenset({"PASS", "CONDITIONAL", "FAIL"})
CRITERIA = (
    "buyer_score",
    "currency_score",
    "rail_score",
    "urgency",
    "proof_of_payment",
    "asset_fit",
    "moat",
    "capital_ease",
    "speed",
    "scalability",
)
#: أقصى درجةٍ لكلّ معيار — عشرة معايير × 3 = 30.
CRITERION_MAX = 3
CITATIONS = re.compile(r"\[E(\d{2})\]")


def _module():
    """تحميل الآلة الحسابية من مسارها (اسم المجلّد يحمل شرطات، فلا يُستورد كحزمة)."""
    spec = importlib.util.spec_from_file_location("cbam_economics_kit", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    #: `dataclasses` يقرأ `sys.modules[cls.__module__]` حين يحلّ التعليقات النصّية،
    #: فوحدةٌ مُحمَّلةٌ بلا تسجيلٍ تُسقط استيراد `ProductInputs` بـAttributeError.
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def audit(readme_text: str, evidence_text: str, candidates_text: str) -> list[str]:
    """كلّ ما يجعل العدّة غير قابلةٍ للتسليم — قائمةٌ كاملة لا أوّل خطأ.

    الدالّة تأخذ النصوص لا المسارات، كي تُغذّيها الحالات السلبية بنسخةٍ مُحرَّفة.
    """
    evidence = list(csv.DictReader(io.StringIO(evidence_text)))
    if not evidence:
        return ["EVIDENCE.csv بلا صفوف"]
    candidates = list(csv.DictReader(io.StringIO(candidates_text)))
    if not candidates:
        return [*_evidence_problems(evidence), "CANDIDATES.csv بلا صفوف"]
    return [
        *_evidence_problems(evidence),
        *_citation_problems(readme_text, evidence),
        *_candidate_problems(candidates),
    ]


def _evidence_problems(evidence: list[dict[str, str]]) -> list[str]:
    problems: list[str] = []
    ids = [row.get("id", "") for row in evidence]
    duplicates = sorted({identifier for identifier in ids if ids.count(identifier) > 1})
    if duplicates:
        problems.append(f"معرّفات سندٍ مكرّرة: {duplicates}")
    expected = [f"E{number:02d}" for number in range(1, len(evidence) + 1)]
    if ids != expected:
        problems.append(f"المعرّفات ليست متّصلة من E01: أوّل انحراف عند {ids[:3]}…{ids[-1:]}")
    for row in evidence:
        identifier = row.get("id", "?")
        problems.extend(_evidence_row_problems(identifier, row))
    return problems


def _evidence_row_problems(identifier: str, row: dict[str, str]) -> list[str]:
    problems: list[str] = []
    if row.get("type") not in EVIDENCE_TYPES:
        problems.append(f"{identifier}: نوع سندٍ غير معروف {row.get('type')!r}")
    if row.get("confidence") not in CONFIDENCE:
        problems.append(f"{identifier}: درجة ثقةٍ غير معروفة {row.get('confidence')!r}")
    try:
        date.fromisoformat(row.get("source_date", ""))
    except ValueError:
        problems.append(f"{identifier}: source_date ليس ISO: {row.get('source_date')!r}")
    url = (row.get("url") or "").strip()
    if not (url.startswith(("http://", "https://")) or (url and (REPO_ROOT / url).exists())):
        problems.append(f"{identifier}: رابطٌ لا يبدأ بـhttp ولا يشير إلى مسارٍ موجود: {url!r}")
    return problems


def _citation_problems(readme_text: str, evidence: list[dict[str, str]]) -> list[str]:
    known = set(ids_to_numbers([row.get("id", "") for row in evidence]))
    cited = set(CITATIONS.findall(readme_text))
    problems: list[str] = []
    if missing := sorted(cited - known):
        problems.append(f"`README.md` يستشهد بسنداتٍ غير موجودة: {[f'E{n}' for n in missing]}")
    if unused := sorted(known - cited):
        problems.append(f"سنداتٌ معرَّفة ولا تُستعمل في النصّ: {[f'E{n}' for n in unused]}")
    if "[E?]" in readme_text:
        problems.append("`README.md` يحمل عنصراً ناقصاً [E?] — سندٌ لم يُكتب")
    return problems


def _candidate_problems(candidates: list[dict[str, str]]) -> list[str]:
    problems: list[str] = []
    identifiers = [row.get("id", "") for row in candidates]
    if len(set(identifiers)) != len(identifiers):
        problems.append("معرّفات مرشّحٍ مكرّرة")
    ranks = sorted((row.get("rank", "") for row in candidates), key=_rank_key)
    if ranks != [str(number) for number in range(1, len(candidates) + 1)]:
        problems.append(f"الرتب ليست 1..{len(candidates)} بلا تكرار: {ranks}")
    for row in candidates:
        problems.extend(_candidate_row_problems(row))
    top = max(candidates, key=lambda row: int(row.get("score", 0)))
    if top.get("hard_gate") != "PASS" or top.get("proof_gate") != "PASS":
        problems.append("المرشّح الأعلى درجةً لا يجتاز البوابتين — الترتيب يخالف شرطه")
    return problems


def _candidate_row_problems(row: dict[str, str]) -> list[str]:
    identifier = row.get("id", "?")
    try:
        parts = [int(row[column]) for column in CRITERIA]
    except (KeyError, TypeError, ValueError):
        return [f"{identifier}: معيارٌ مفقود أو غير رقمي"]
    problems: list[str] = []
    if any(part < 0 or part > CRITERION_MAX for part in parts):
        problems.append(f"{identifier}: معيارٌ خارج 0..{CRITERION_MAX}")
    if sum(parts) != int(row.get("score", -1)):
        problems.append(f"{identifier}: الدرجة {row.get('score')} ≠ مجموع المعايير {sum(parts)}")
    for gate in ("hard_gate", "proof_gate"):
        if row.get(gate) not in GATES:
            problems.append(f"{identifier}: {gate} غير معروف {row.get(gate)!r}")
    #: البوابة تُشتقّ من الدليل، فلا تُكتب بيد: PASS ⇔ دليل دفع ≥2، CONDITIONAL ⇔ 1، FAIL ⇔ 0.
    proof = int(row.get("proof_of_payment", -1))
    expected_gate = "PASS" if proof >= 2 else ("CONDITIONAL" if proof == 1 else "FAIL")
    if row.get("proof_gate") != expected_gate:
        problems.append(
            f"{identifier}: proof_gate={row.get('proof_gate')} ولا يطابق دليل الدفع {proof} "
            f"(المتوقّع {expected_gate})"
        )
    return problems


def ids_to_numbers(ids: list[str]) -> list[str]:
    return [identifier[1:] for identifier in ids if identifier.startswith("E")]


def _rank_key(value: str) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 10**6


def _kit_text() -> tuple[str, str, str]:
    return (
        README.read_text(encoding="utf-8"),
        EVIDENCE.read_text(encoding="utf-8"),
        CANDIDATES.read_text(encoding="utf-8"),
    )


def test_the_shipped_kit_is_clean() -> None:
    """العدّة المودَعة تمرّ بكلّ قواعد التسليم."""
    assert audit(*_kit_text()) == []


def test_expected_values_are_reproduced_by_the_calculator() -> None:
    """`--check` في CI: القيم المتوقّعة تُحسب، لا تُنسخ."""
    module = _module()
    assert module.check(module.build_payload()) == []


def test_committed_json_is_the_computed_payload() -> None:
    """`CBAM_ECONOMICS.json` ليس حقيقةً ثانية: هو ناتج الآلة نفسها."""
    module = _module()
    committed = json.loads(ECONOMICS.read_text(encoding="utf-8"))
    assert committed == module.build_payload()


def test_every_source_named_by_the_calculator_exists_in_the_evidence_csv() -> None:
    """كلّ رقمٍ في الآلة يحمل معرّف سند، وكلّ معرّفٍ مذكورٍ موجودٌ فعلاً."""
    module = _module()
    known = {row["id"] for row in csv.DictReader(EVIDENCE.read_text(encoding="utf-8").splitlines())}
    named = set(re.findall(r"(E\d{2})", "\n".join(module.build_payload()["sources_ar"])))
    assert named, "الآلة لا تسمّي أيّ سند"
    assert named <= known, f"الآلة تسمّي سنداتٍ غير موجودة: {sorted(named - known)}"


def test_the_certificate_price_is_the_published_q3_2026_one() -> None:
    """سعر الشهادة مرساةُ كلّ رقم؛ تغيّره بلا تحديث السند يجعل الوفر خيالاً."""
    module = _module()
    assert module.CERTIFICATE_PRICE_EUR_PER_TCO2E == 82.32


def _mutated_evidence(*, duplicate: bool = False, bad_url: bool = False):
    readme, evidence_text, candidates = _kit_text()
    rows = list(csv.DictReader(io.StringIO(evidence_text)))
    if duplicate:
        rows.append(dict(rows[0]))
    if bad_url:
        rows[0]["url"] = "voir la note interne"
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
    return readme, buffer.getvalue(), candidates


def test_citation_of_an_unknown_source_is_caught() -> None:
    """حالة سلبية 1: رقمُ سندٍ في النصّ لا يقابله صفّ في الملفّ."""
    readme, evidence_text, candidates = _kit_text()
    problems = audit(readme + "\nرقمٌ بلا سند [E99]\n", evidence_text, candidates)
    assert any("غير موجودة" in problem for problem in problems)


def test_duplicate_evidence_id_is_caught() -> None:
    """حالة سلبية 2: سندٌ مكرَّر يجعل الاستشهاد غامضاً."""
    problems = audit(*_mutated_evidence(duplicate=True))
    assert any("مكرّرة" in problem for problem in problems)


def test_evidence_without_a_resolvable_source_is_caught() -> None:
    """حالة سلبية 3: سندٌ بلا رابط ولا مسارٍ داخلي ليس سنداً."""
    problems = audit(*_mutated_evidence(bad_url=True))
    assert any("رابطٌ" in problem for problem in problems)


def test_placeholder_citation_is_caught() -> None:
    """حالة سلبية 4: `[E?]` — العنصر الذي حملته المسودّة الأولى فعلاً."""
    readme, evidence_text, candidates = _kit_text()
    problems = audit(readme + "\nسطرٌ بلا سند [E?]\n", evidence_text, candidates)
    assert any("[E?]" in problem for problem in problems)


def _mutated_candidates(mutate) -> str:
    _readme, _evidence, candidates_text = _kit_text()
    rows = list(csv.DictReader(io.StringIO(candidates_text)))
    mutate(rows)
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def test_a_score_that_is_not_the_sum_of_its_criteria_is_caught() -> None:
    """حالة سلبية 5: درجةٌ مكتوبةٌ بيد لا تساوي مجموع معاييرها."""

    def mutate(rows):
        rows[0]["score"] = str(int(rows[0]["score"]) + 3)

    problems = audit(*_kit_text()[:2], _mutated_candidates(mutate))
    assert any("≠ مجموع المعايير" in problem for problem in problems)


def test_a_proof_gate_that_outruns_its_evidence_is_caught() -> None:
    """حالة سلبيّة 6: `PASS` مع دليل دفعٍ ضعيف — الترقية اللفظية التي تمنعها البوّابة."""

    def mutate(rows):
        rows[-1]["proof_gate"] = "PASS"

    problems = audit(*_kit_text()[:2], _mutated_candidates(mutate))
    assert any("لا يطابق دليل الدفع" in problem for problem in problems)
