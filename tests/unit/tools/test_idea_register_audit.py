"""التدقيق الصارم في سجلّ الأفكار — لا ✓ بلا سندٍ مقروء، والبوّابات غير تعويضية.

**لماذا هذا الاختبار موجود.** طلب المالك في 2026-10-27 إكمال العمل «بشكلٍ دقيقٍ معياريٍّ
ميكروسكوبي مع تطبيق معايير قاسية صارمة». والمعيار مكتوبٌ في المستودع قبل هذا الطلب:
``docs/commercial/DECISION_COMMITMENT_ENGINE.md`` (البوّابات غير تعويضية، والاهتمام ليس
ميزانية، والتصريح ليس إثباتاً، وتعذّر الوصول يعني مجهولاً لا تحقّقاً). وحين طُبّق على السجلّ
سقطت كلّ «متأهّلة»: سعرُ بائعٍ كان يُقرأ دافعاً، وموعدٌ تنظيمي كان يُقرأ ألماً، وقائمةٌ قنواتُ
16 من جهاتها العشرين مجهولة كانت تُقرأ جاهزة. وأربعة أنواعٍ من الانحراف تُعيد ذلك بلا أن
يلاحظ أحد:

- ✓ بلا سند، أو بسندٍ لم نقرأه (نقل وكيل، ملخّص بحث، صفحة محجوبة)، أو من نوعٍ لا يحمل
  تلك البوّابة (سعر بائع في G1، موعدٌ وحده في G4، قائمةٌ ناقصة في G5)؛
- «متأهّلة» مع بوّابةٍ جزئية: تعويضُ بوّابةٍ بمزايا أخرى؛
- ألمٌ «حديث» حدثُه أقدم من 365 يوماً عند تاريخ التدقيق؛
- فكرةٌ حيّة بلا تدقيق، أو سندٌ أوّلي بلا مصدرٍ يمكن فتحه.

الحالات السلبية تبرهن أنّ كلّ قاعدةٍ تحمرّ وحدها. الاختبار لا يقرأ الشبكة.

**التشغيل:** ``pytest tests/unit/tools/test_idea_register_audit.py -q``
"""

from __future__ import annotations

import copy
import json
import re
from collections.abc import Callable
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
REGISTER = REPO_ROOT / "docs/archive/commercial/IDEA_REGISTER.json"

GATES = ("G1", "G2", "G3", "G4", "G5")
LIVE_STAGES = {"included", "conditional"}
READ_TIERS = {"P1", "P2"}
RECENCY_DAYS = 365
EVENT_DATE = re.compile(r"^(\d{4}-\d{2}(-\d{2})?|unknown)$")
ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
STRONG_EVIDENCE = {"D2", "D3", "D4", "D5"}


def _register() -> dict:
    return json.loads(REGISTER.read_text(encoding="utf-8"))


def _event_day(value: str) -> date:
    """تاريخ الحدث؛ الشهر وحده يُقرأ آخرَ يومٍ ممكن فيه — لصالح الحداثة لا ضدّها."""
    if len(value) == 7:
        year, month = int(value[:4]), int(value[5:7])
        nxt = date(year + month // 12, month % 12 + 1, 1)
        return date.fromordinal(nxt.toordinal() - 1)
    return date.fromisoformat(value)


def _claim_problems(claims: list[dict], standard: dict) -> list[str]:
    problems: list[str] = []
    ids = [c["id"] for c in claims]
    if duplicates := sorted({i for i in ids if ids.count(i) > 1}):
        problems.append(f"سنداتٌ مكرّرة المعرّف: {duplicates}")
    for claim in claims:
        cid = claim["id"]
        if claim["tier"] not in standard["tiers"]:
            problems.append(f"{cid}: درجةٌ خارج المفردات: {claim['tier']}")
        if claim["kind"] not in standard["kinds"]:
            problems.append(f"{cid}: نوعٌ خارج المفردات: {claim['kind']}")
        if not EVENT_DATE.match(str(claim.get("event_date", ""))):
            problems.append(f"{cid}: تاريخ الحدث ليس YYYY-MM أو YYYY-MM-DD أو unknown")
        if claim["tier"] in READ_TIERS:
            url = str(claim.get("url", ""))
            if url.startswith("repo:"):
                if not (REPO_ROOT / url.removeprefix("repo:")).exists():
                    problems.append(f"{cid}: سندٌ مقروء يشير إلى ملفٍّ غير موجود: {url}")
            elif not url.startswith("https://"):
                problems.append(f"{cid}: سندٌ مقروء بلا مصدرٍ يمكن فتحه")
            if not ISO_DATE.match(str(claim.get("read_on", ""))):
                problems.append(f"{cid}: سندٌ مقروء بلا تاريخ قراءة")
        if not set(claim["gates"]) <= set(GATES):
            problems.append(f"{cid}: بوّابةٌ خارج G1–G5")
    return problems


def _pass_problems(record: dict, gate: str, supporters: list[dict], standard: dict) -> list[str]:
    """✓ تحتاج سنداً مقروءاً من نوعٍ مسموح لتلك البوّابة، وG4 تحتاج حداثته أيضاً."""
    rid = record["id"]
    allowed = set(standard["gate_kinds"][gate])
    qualified = [c for c in supporters if c["tier"] in READ_TIERS and c["kind"] in allowed]
    if not qualified:
        return [f"{rid}: {gate} ✓ بلا سندٍ مقروء من نوعٍ مسموح ({sorted(allowed)})"]
    if gate == "G4":
        audited = date.fromisoformat(record["audit"]["date"])
        fresh = [
            c
            for c in qualified
            if c["event_date"] != "unknown"
            and 0 <= (audited - _event_day(c["event_date"])).days <= RECENCY_DAYS
        ]
        if not fresh:
            return [f"{rid}: G4 ✓ وحدثُ سنده أقدم من {RECENCY_DAYS} يوماً عند التدقيق"]
    return []


def _record_problems(record: dict, claims: dict[str, dict], standard: dict) -> list[str]:
    rid, screening = record["id"], record["screening"]
    audit = record.get("audit")
    if audit is None:
        return [f"{rid}: فكرةٌ حيّة بلا تدقيقٍ صارم"] if screening["stage"] in LIVE_STAGES else []
    problems: list[str] = []
    if audit.get("standard") != standard["id"] or not ISO_DATE.match(str(audit.get("date", ""))):
        problems.append(f"{rid}: تدقيقٌ بلا معيارٍ معلن أو تاريخ")
    if screening["stage"] == "included" and any(screening["gates"][k] != "pass" for k in GATES):
        problems.append(f"{rid}: متأهّلة وبوّابةٌ غير مستوفاة — البوّابات غير تعويضية")
    support = audit.get("support", {})
    for gate, ids in support.items():
        for cid in ids:
            claim = claims.get(cid)
            if claim is None:
                problems.append(f"{rid}: {gate} يستند إلى سندٍ غير موجود: {cid}")
            elif rid not in claim["records"] or gate not in claim["gates"]:
                problems.append(f"{rid}: {gate} يستند إلى {cid} وهو لا يخصّه")
    for gate in GATES:
        if screening["gates"][gate] == "pass":
            supporters = [claims[c] for c in support.get(gate, []) if c in claims]
            problems.extend(_pass_problems(record, gate, supporters, standard))
    if record.get("kind") == "idea" and record["evidence"]["level"] in STRONG_EVIDENCE:
        attached = {cid for ids in support.values() for cid in ids}
        if not any(claims[c]["tier"] == "P1" for c in attached if c in claims):
            problems.append(f"{rid}: الدليل {record['evidence']['level']} بلا سندٍ أوّلي (P1)")
    return problems


def audit(register: dict) -> list[str]:
    """كلّ ما يجعل حكماً في السجلّ أقوى من دليله — قائمةٌ كاملة لا أوّل خطأ."""
    standard = register["audit_standard"]
    claims = {c["id"]: c for c in register["claims"]}
    problems = _claim_problems(register["claims"], standard)
    for record in register["records"]:
        problems.extend(_record_problems(record, claims, standard))
    return problems


def _mutated(transform: Callable[[dict], None]) -> list[str]:
    register = copy.deepcopy(_register())
    transform(register)
    return audit(register)


def _record(register: dict, rid: str) -> dict:
    return next(r for r in register["records"] if r["id"] == rid)


def _claim(register: dict, cid: str) -> dict:
    return next(c for c in register["claims"] if c["id"] == cid)


def test_every_verdict_is_no_stronger_than_its_evidence() -> None:
    """السجلّ المودَع يمرّ: كلّ ✓ مسنودة، ولا متأهّلة ببوّابةٍ جزئية، وكلّ فكرةٍ حيّة مدقّقة."""
    assert audit(_register()) == []


def test_a_vendor_price_cannot_carry_g1() -> None:
    """سعر بائعٍ ليس شراءً: نقلُ سند G1 في B46 من الترسية إلى سعر Systemday يُحمّر."""

    def swap(register: dict) -> None:
        _record(register, "B46")["audit"]["support"]["G1"] = ["C32"]
        _claim(register, "C32")["records"].append("B46")

    assert any("B46: G1 ✓ بلا سندٍ مقروء" in p for p in _mutated(swap))


def test_an_unread_source_cannot_carry_a_pass() -> None:
    """ما لم يُقرأ مجهول: خفضُ سند الترسية إلى نقل وكيل (A) يُحمّر."""
    problems = _mutated(lambda r: _claim(r, "C25").update(tier="A"))
    assert any("B46: G1 ✓ بلا سندٍ مقروء" in p for p in problems)


def test_gates_do_not_compensate() -> None:
    """«متأهّلة» مع بوّابةٍ جزئية تعويضٌ ممنوع."""
    problems = _mutated(lambda r: _record(r, "B52")["screening"].update(stage="included"))
    assert any("B52: متأهّلة وبوّابةٌ غير مستوفاة" in p for p in problems)


def test_stale_pain_cannot_carry_g4() -> None:
    """ألمٌ أقدم من سنة ليس حديثاً: تأريخ سند G4 الوحيد في B38 بـ2025-01-01 يُحمّر."""
    problems = _mutated(lambda r: _claim(r, "C24").update(event_date="2025-01-01"))
    assert any("B38: G4 ✓ وحدثُ سنده أقدم" in p for p in problems)


def test_a_deadline_alone_cannot_carry_g4() -> None:
    """الموعد التنظيمي ليس ألماً: G4 ✓ في B52 بسنداتٍ من نوع الموعد والتسويق يُحمّر."""

    def lift(register: dict) -> None:
        record = _record(register, "B52")
        record["screening"]["gates"]["G4"] = "pass"
        record["audit"]["support"]["G4"] = ["C38", "C39"]

    assert any("B52: G4 ✓ بلا سندٍ مقروء" in p for p in _mutated(lift))


def test_an_incomplete_list_cannot_carry_g5() -> None:
    """قائمةٌ قنواتُ أغلبها مجهولة ليست جاهزة: G5 ✓ في B12 بقائمة D-320 يُحمّر."""

    def lift(register: dict) -> None:
        _record(register, "B12")["screening"]["gates"]["G5"] = "pass"

    assert any("B12: G5 ✓ بلا سندٍ مقروء" in p for p in _mutated(lift))


def test_every_live_idea_is_audited() -> None:
    """فكرةٌ مشروطة بلا تدقيق تعني حكماً لم يُفحص."""
    problems = _mutated(lambda r: _record(r, "B52").pop("audit"))
    assert "B52: فكرةٌ حيّة بلا تدقيقٍ صارم" in problems


def test_strong_evidence_needs_a_primary_source() -> None:
    """D2 بلا سندٍ أوّلي: خفضُ سندات B48 الأوّلية إلى ثانوية يُحمّر."""

    def demote(register: dict) -> None:
        for cid in ("C28", "C29"):
            _claim(register, cid).update(tier="P2")

    assert any("B48: الدليل D2 بلا سندٍ أوّلي" in p for p in _mutated(demote))


def test_a_read_source_must_be_openable() -> None:
    """سندٌ أوّلي بلا رابطٍ يمكن فتحه، أو يشير إلى ملفٍّ محذوف، يُحمّر."""
    no_url = _mutated(lambda r: _claim(r, "C25").update(url="World Bank"))
    gone = _mutated(lambda r: _claim(r, "C03").update(url="repo:docs/commercial/NO_SUCH_FILE.csv"))
    assert any("C25: سندٌ مقروء بلا مصدرٍ يمكن فتحه" in p for p in no_url)
    assert any("C03: سندٌ مقروء يشير إلى ملفٍّ غير موجود" in p for p in gone)


def test_support_must_belong_to_the_record() -> None:
    """سندٌ لا يخصّ الفكرة أو البوّابة لا يسندها."""
    problems = _mutated(lambda r: _record(r, "B51")["audit"]["support"].update(G4=["C24"]))
    assert any("B51: G4 يستند إلى C24 وهو لا يخصّه" in p for p in problems)
