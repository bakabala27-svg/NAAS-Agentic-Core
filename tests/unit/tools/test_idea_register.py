"""سجلّ الأفكار الموحّد يحفظ كلّ شيء — يُفحَص كالكود.

**لماذا هذا الاختبار موجود.** قال المالك في 2026-10-26: «نظّم كلّ الأفكار تنظيماً علمياً،
يُحفظ ولا يُحذف». ``docs/archive/commercial/IDEA_REGISTER.json`` يرتّب الأرشيفات المؤرَّخة
ومسارات ``VALUE_CHAIN.json`` في سجلٍّ واحد بأوجهٍ ومراحل غربلةٍ على نمط PRISMA 2020. وأربعة
أنواع من الانحراف تجعل السجلّ يكذب بلا أن يلاحظ أحد:

- فكرةٌ أو وظيفةٌ أو مسارٌ موجودٌ في أصله ويغيب عن السجلّ: الترتيب صار حذفاً؛
- مستبعدةٌ بلا بوّابةٍ ساقطة ولا عائقٍ ولا شرط إعادة فتح: الاستبعاد صار حذفاً مقنَّعاً؛
- قيمة وجهٍ خارج المفردات المعلنة: التصنيف صار نثراً لا يُفرز؛
- أرقام مسار الغربلة أو القراءة العربية لا تطابق السجلّات: نسخةٌ ثانية تتقادم (D-188).

الحالات السلبية تبرهن أنّ كلّ قاعدةٍ تحمرّ وحدها. الاختبار لا يقرأ الشبكة.

**التشغيل:** ``pytest tests/unit/tools/test_idea_register.py -q``
"""

from __future__ import annotations

import collections
import copy
import json
import re
from collections.abc import Callable
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
ARCHIVE = REPO_ROOT / "docs/archive/commercial"
REGISTER = ARCHIVE / "IDEA_REGISTER.json"
READING_VIEW = ARCHIVE / "IDEA_REGISTER_AR.md"
VALUE_CHAIN = REPO_ROOT / "docs/commercial/VALUE_CHAIN.json"

DEFINITION = re.compile(r"^### (B\d{2})\b(.*)$")
JOB_ROW = re.compile(r"^\| (J\d{2}) \|")
ADDENDUM_MARK = "ملحق"
GATE_FAILURES = {"fail", "partial"}


def _source_ids() -> set[str]:
    """كلّ ما عرّفته الأرشيفات المؤرَّخة وسلسلة القيمة — ما يجب ألّا يغيب عن السجلّ."""
    found: set[str] = set()
    for path in sorted(ARCHIVE.glob("OPPORTUNITIES_*_AR.md")):
        for line in path.read_text(encoding="utf-8").splitlines():
            definition = DEFINITION.match(line)
            if definition and ADDENDUM_MARK in definition.group(2):
                definition = None
            if match := definition or JOB_ROW.match(line):
                found.add(match.group(1))
    paths = json.loads(VALUE_CHAIN.read_text(encoding="utf-8")).get("paths", [])
    return found | {str(path["id"]) for path in paths}


def _register() -> dict:
    return json.loads(REGISTER.read_text(encoding="utf-8"))


def _flow(records: list[dict]) -> dict[str, int]:
    """مسار الغربلة محسوباً من السجلّات، لا مكتوباً باليد."""
    screened = [
        r
        for r in records
        if r["kind"] == "idea"
        or (r["kind"] == "value_chain_path" and r["screening"]["stage"] != "governed_elsewhere")
    ]
    stages = collections.Counter(r["screening"]["stage"] for r in screened)
    return {
        "identified_ideas": sum(r["kind"] == "idea" for r in records),
        "identified_jobs": sum(r["kind"] == "job" for r in records),
        "identified_value_chain_paths": sum(r["kind"] == "value_chain_path" for r in records),
        "screened": len(screened),
        "included": stages["included"],
        "conditional": stages["conditional"],
        "excluded": stages["excluded"],
    }


def _vocabulary_problems(record: dict, vocab: dict) -> list[str]:
    rid = record["id"]
    checks = {
        "kind": (record["kind"], "kind"),
        "stage": (record["screening"]["stage"], "stage"),
        "option": (record["option"]["state"], "option_state"),
        "evidence": (record["evidence"]["level"], "evidence_level"),
    }
    if record["kind"] == "idea":
        facets = record["facets"]
        checks |= {
            "domain": (facets["domain"], "domain"),
            "currency": (facets["currency"], "currency"),
            "delivery": (facets["delivery"], "delivery"),
            "constraint": (record["screening"]["binding_constraint"], "constraint"),
        }
    problems = [
        f"{rid}: قيمة {name} خارج المفردات: {value}"
        for name, (value, key) in checks.items()
        if value not in vocab[key]
    ]
    gates = record["screening"]["gates"]
    if set(gates) != {"G1", "G2", "G3", "G4", "G5"} or not set(gates.values()) <= set(
        vocab["gate_verdict"]
    ):
        problems.append(f"{rid}: البوّابات ليست G1–G5 بقيمٍ معلنة")
    return problems


def _screening_problems(record: dict, groups: dict) -> list[str]:
    rid, screening = record["id"], record["screening"]
    problems: list[str] = []
    if screening["stage"] == "excluded":
        if (
            not GATE_FAILURES & set(screening["gates"].values())
            and screening["binding_constraint"] != "channel"
        ):
            problems.append(f"{rid}: مستبعدة ولا بوّابة ساقطة")
        if screening["binding_constraint"] == "none":
            problems.append(f"{rid}: مستبعدة بلا عائقٍ مسمّى")
    if not str(record["option"].get("trigger_ar", "")).strip():
        problems.append(f"{rid}: بلا شرط إعادة فتح ولا اختبارٍ تالٍ")
    if record.get("group") is not None and record["group"] not in groups:
        problems.append(f"{rid}: مجموعة غير معرَّفة: {record['group']}")
    return problems


def _coverage_problems(ids: list[str], source_ids: set[str]) -> list[str]:
    problems = [
        f"المعرّف {rid} مكرَّر {n} مرّات" for rid, n in collections.Counter(ids).items() if n > 1
    ]
    if missing := sorted(source_ids - set(ids)):
        problems.append(f"غائبٌ عن السجلّ وهو في أصله — الترتيب صار حذفاً: {missing}")
    if orphans := sorted(set(ids) - source_ids):
        problems.append(f"في السجلّ بلا أصلٍ مؤرَّخ: {orphans}")
    return problems


def _link_problems(records: list[dict], groups: dict) -> list[str]:
    problems: list[str] = []
    known = {r["id"] for r in records} | set(groups)
    for record in records:
        if stray := [x for x in record.get("related", []) if x not in known]:
            problems.append(f"{record['id']}: يرتبط بغير موجود: {stray}")
    for name, group in groups.items():
        members = sorted(r["id"] for r in records if r.get("group") == name)
        if sorted(group.get("members", [])) != members:
            problems.append(f"المجموعة {name}: قائمة الأعضاء لا تطابق السجلّات")
        if not group.get("kill_ar") or not group.get("next_test_ar"):
            problems.append(f"المجموعة {name}: بلا اختبارٍ تالٍ أو شرط إيقاف")
    return problems


def _view_problems(register: dict, reading_view: str) -> list[str]:
    records = register["records"]
    flow = _flow(records)
    problems: list[str] = []
    if register.get("flow") != flow:
        problems.append(f"أرقام مسار الغربلة مكتوبة لا محسوبة: {register.get('flow')} ≠ {flow}")
    problems.extend(
        f"القراءة العربية لا تذكر {r['id']}"
        for r in records
        if not re.search(rf"^\| {re.escape(r['id'])} \|", reading_view, re.M)
    )
    if (
        f"مستبعدة: {flow['excluded']}" not in reading_view
        or f"المُغربَل: {flow['screened']}" not in reading_view
    ):
        problems.append("أرقام المسار في القراءة العربية لا تطابق السجلّ")
    return problems


def audit(register: dict, source_ids: set[str], reading_view: str) -> list[str]:
    """كلّ ما يجعل السجلّ غير حافظٍ أو غير منظَّم — قائمةٌ كاملة لا أوّل خطأ."""
    records = register["records"]
    problems = _coverage_problems([r["id"] for r in records], source_ids)
    for record in records:
        problems.extend(_vocabulary_problems(record, register["vocabularies"]))
        problems.extend(_screening_problems(record, register["groups"]))
    problems.extend(_link_problems(records, register["groups"]))
    problems.extend(_view_problems(register, reading_view))
    return problems


def _mutated(transform: Callable[[dict], None]) -> list[str]:
    register = copy.deepcopy(_register())
    transform(register)
    return audit(register, _source_ids(), READING_VIEW.read_text(encoding="utf-8"))


def _record(register: dict, rid: str) -> dict:
    return next(r for r in register["records"] if r["id"] == rid)


def test_the_register_preserves_and_organises_everything() -> None:
    """السجلّ المودَع يمرّ: لا غائب ولا يتيم، والمفردات مغلقة، والأرقام محسوبة."""
    assert audit(_register(), _source_ids(), READING_VIEW.read_text(encoding="utf-8")) == []


def test_every_original_idea_job_and_path_is_present() -> None:
    """B01–B43 وJ01–J12 وكلّ مسارات سلسلة القيمة حاضرة."""
    ids = {r["id"] for r in _register()["records"]}
    assert {f"B{n:02d}" for n in range(1, 44)} <= ids
    assert {f"J{n:02d}" for n in range(1, 13)} <= ids
    assert {"OPP-01", "OPP-13", "OPP-19"} <= ids


def test_dropping_a_record_is_red() -> None:
    """إسقاط B05 من السجلّ يحمرّ: الترتيب لا يحذف."""

    def drop(register: dict) -> None:
        register["records"] = [r for r in register["records"] if r["id"] != "B05"]

    assert any("غائبٌ عن السجلّ" in p and "B05" in p for p in _mutated(drop))


def test_an_exclusion_without_a_reason_is_red() -> None:
    """مستبعدةٌ بلا عائقٍ مسمّى تحمرّ."""

    def strip(register: dict) -> None:
        _record(register, "B34")["screening"]["binding_constraint"] = "none"

    assert any("B34" in p and "بلا عائقٍ" in p for p in _mutated(strip))


def test_an_exclusion_with_no_failed_gate_is_red() -> None:
    """مستبعدةٌ وكلّ بوّاباتها مستوفاة تحمرّ."""

    def clean(register: dict) -> None:
        gates = _record(register, "B34")["screening"]["gates"]
        for key in gates:
            gates[key] = "pass"

    assert any("B34" in p and "لا بوّابة ساقطة" in p for p in _mutated(clean))


def test_a_facet_outside_the_vocabulary_is_red() -> None:
    """قيمة وجهٍ غير معلنة تحمرّ."""

    def stray(register: dict) -> None:
        _record(register, "B19")["facets"]["domain"] = "misc"

    assert any("B19" in p and "domain" in p for p in _mutated(stray))


def test_a_hand_written_flow_count_is_red() -> None:
    """رقمٌ في مسار الغربلة لا يطابق السجلّات يحمرّ."""

    def bump(register: dict) -> None:
        register["flow"]["included"] += 1

    assert any("مكتوبة لا محسوبة" in p for p in _mutated(bump))


def test_a_missing_reopen_trigger_is_red() -> None:
    """فكرةٌ بلا شرط إعادة فتحٍ ولا اختبارٍ تالٍ تحمرّ."""

    def blank(register: dict) -> None:
        _record(register, "B42")["option"]["trigger_ar"] = " "

    assert any("B42" in p and "شرط إعادة فتح" in p for p in _mutated(blank))
