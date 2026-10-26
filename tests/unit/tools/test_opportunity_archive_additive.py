"""أرشيف الفرص يُضاف إليه ولا يُحذف منه شيء — يُفحَص كالكود.

**لماذا هذا الاختبار موجود.** قال المالك في 2026-10-26: «أضف فرصاً جديدة ولا تحذف القديم،
يعني إضافة فقط دون حذف». الأرشيف في ``docs/archive/commercial/`` يحفظ كلّ فكرةٍ (B01…)
وكلّ وظيفةٍ (J01…) تناولتها المحادثات، والمختار منها وغير المختار. وثلاثة أنواع من الانحراف
تجعله يكذب بلا أن يلاحظ أحد:

- حذفُ فكرةٍ قديمة: يظهر ثقباً في الترقيم (B05 تختفي فيصير التسلسل B04 ثمّ B06)؛
- إعادةُ استعمال رقمٍ قديم لفكرةٍ جديدة: يمحو الأصل بالمعنى ولو بقي نصّه؛
- فكرةٌ جديدة بلا مصدرٍ ولا تاريخ: تخالف قاعدة الحداثة التي وُلد بها الأرشيف الثاني.

والملحق (عنوانٌ فيه «ملحق») يضيف أدلّةً جديدة لفكرةٍ قديمة دون تحرير أصلها، فيجب أن يشير
إلى فكرةٍ معرَّفةٍ في أرشيفٍ أسبق أو إلى مسارٍ في ``VALUE_CHAIN.json``.

الاختبار لا يقرأ الشبكة ولا ساعة الحائط. الحالات السلبية تُبرهن أنّ كلّ قاعدةٍ تحمرّ وحدها.

**التشغيل:** ``pytest tests/unit/tools/test_opportunity_archive_additive.py -q``
"""

from __future__ import annotations

import json
import re
from collections.abc import Callable
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
ARCHIVE = REPO_ROOT / "docs/archive/commercial"
VALUE_CHAIN = REPO_ROOT / "docs/commercial/VALUE_CHAIN.json"

#: أرشيفات الفرص فقط؛ التاريخ في الاسم يحدّد الترتيب.
ARCHIVE_NAME = re.compile(r"^OPPORTUNITIES_.*_(\d{4}-\d{2}-\d{2})_AR\.md$")
#: قاعدة «مصدرٌ وتاريخٌ لكلّ فكرةٍ جديدة» وُلدت مع أرشيف هذا اليوم؛ ما قبله يُحفظ كما كُتب.
DATED_SOURCES_SINCE = "2026-10-26"

HEADING = re.compile(r"^### (B\d{2}|OPP-\d{2})\b(.*)$")
JOB_ROW = re.compile(r"^\| (J\d{2}) \|")
ISO_DATE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")
ADDENDUM_MARK = "ملحق"


def _sections(text: str) -> dict[str, str]:
    """كلّ عنوانٍ من المستوى الثالث يبدأ بمعرّف ← نصّه حتى العنوان التالي."""
    sections: dict[str, str] = {}
    current: str | None = None
    lines: list[str] = []
    for line in text.splitlines():
        if line.startswith(("### ", "## ")):
            if current is not None:
                sections[current] = "\n".join(lines)
            current, lines = None, []
            if line.startswith("### "):
                current = line
                continue
        if current is not None:
            lines.append(line)
    if current is not None:
        sections[current] = "\n".join(lines)
    return sections


def _parse(text: str) -> tuple[list[str], list[tuple[str, str]], list[str], dict[str, str]]:
    """(تعريفات الأفكار، الملاحق مع عناوينها، الوظائف، نصّ كلّ تعريف)."""
    definitions: list[str] = []
    addenda: list[tuple[str, str]] = []
    bodies: dict[str, str] = {}
    for heading, body in _sections(text).items():
        match = HEADING.match(heading)
        if not match:
            continue
        identifier, rest = match.group(1), match.group(2)
        if ADDENDUM_MARK in rest:
            addenda.append((identifier, heading))
        else:
            definitions.append(identifier)
            bodies[identifier] = body
    jobs = [m.group(1) for line in text.splitlines() if (m := JOB_ROW.match(line))]
    return definitions, addenda, jobs, bodies


def _gaps(identifiers: list[str], prefix: str) -> list[str]:
    numbers = sorted(int(identifier[len(prefix) :]) for identifier in set(identifiers))
    expected = list(range(1, numbers[-1] + 1)) if numbers else []
    return [f"{prefix}{number:02d}" for number in expected if number not in numbers]


def audit(archives: list[tuple[str, str]], known_paths: set[str]) -> list[str]:
    """كلّ ما يجعل الأرشيف غير إضافيّ — قائمةٌ كاملة لا أوّل خطأ.

    ``archives`` أزواج (تاريخ الملفّ، نصّه) بأيّ ترتيب؛ تأخذ الدالّة النصوص لا المسارات
    كي تُغذّيها الحالات السلبية بنسخةٍ مُحرَّفة.
    """
    problems: list[str] = []
    seen: dict[str, str] = {}
    all_ideas: list[str] = []
    all_jobs: list[str] = []
    for stamp, text in sorted(archives):
        definitions, addenda, jobs, bodies = _parse(text)
        problems.extend(_reuse_problems(stamp, definitions + jobs, seen))
        problems.extend(_addendum_problems(stamp, addenda, seen, known_paths))
        if stamp >= DATED_SOURCES_SINCE:
            problems.extend(_dated_source_problems(stamp, bodies))
        all_ideas.extend(definitions)
        all_jobs.extend(jobs)
    for prefix, identifiers in (("B", all_ideas), ("J", all_jobs)):
        if missing := _gaps(identifiers, prefix):
            problems.append(f"ثقبٌ في الترقيم — حُذف أو لم يُكتب: {missing}")
    return problems


def _reuse_problems(stamp: str, identifiers: list[str], seen: dict[str, str]) -> list[str]:
    """رقمٌ عُرِّف في أرشيفٍ سابق (أو قبله في الملفّ نفسه) لا يُعاد استعماله؛ تُحدِّث ``seen``."""
    problems: list[str] = []
    for identifier in identifiers:
        if identifier in seen:
            problems.append(
                f"{stamp}: المعرّف {identifier} معرَّفٌ قبلُ في {seen[identifier]} — "
                "رقمٌ قديم لا يُعاد استعماله"
            )
        else:
            seen[identifier] = stamp
    return problems


def _addendum_problems(
    stamp: str, addenda: list[tuple[str, str]], seen: dict[str, str], known_paths: set[str]
) -> list[str]:
    """الملحق يشير إلى فكرةٍ عُرِّفت في أرشيفٍ أسبق، أو إلى مسارٍ في سلسلة القيمة."""
    problems: list[str] = []
    for identifier, heading in addenda:
        if identifier.startswith("OPP-"):
            if identifier not in known_paths:
                problems.append(f"{stamp}: ملحقٌ لمسارٍ غير موجود في VALUE_CHAIN: {heading}")
            continue
        earlier = seen.get(identifier)
        if earlier is None or earlier >= stamp:
            problems.append(f"{stamp}: ملحقٌ لفكرةٍ لم تُعرَّف في أرشيفٍ أسبق: {heading}")
    return problems


def _dated_source_problems(stamp: str, bodies: dict[str, str]) -> list[str]:
    """كلّ فكرةٍ جديدة تحمل مصدراً يبدأ بـhttps وتاريخاً بصيغة ISO."""
    problems: list[str] = []
    for identifier, body in bodies.items():
        if "https://" not in body:
            problems.append(f"{stamp}: {identifier} بلا مصدرٍ يبدأ بـhttps")
        if not ISO_DATE.search(body):
            problems.append(f"{stamp}: {identifier} بلا تاريخٍ بصيغة YYYY-MM-DD")
    return problems


def _archives() -> list[tuple[str, str]]:
    found = []
    for path in sorted(ARCHIVE.glob("OPPORTUNITIES_*_AR.md")):
        match = ARCHIVE_NAME.match(path.name)
        if match:
            found.append((match.group(1), path.read_text(encoding="utf-8")))
    return found


def _known_paths() -> set[str]:
    payload = json.loads(VALUE_CHAIN.read_text(encoding="utf-8"))
    return {str(path.get("id")) for path in payload.get("paths", [])}


def _replace_once(text: str, old: str, new: str) -> str:
    assert text.count(old) == 1, f"نصّ الحالة السلبية غير فريد: {old!r}"
    return text.replace(old, new)


def _with(stamp: str, transform: Callable[[str], str]) -> list[tuple[str, str]]:
    return [(s, transform(t) if s == stamp else t) for s, t in _archives()]


def test_the_archives_are_additive() -> None:
    """الأرشيفات المودَعة تمرّ: لا ثقب ولا تكرار، والملاحق تشير إلى موجود، والجديد مؤرَّخ."""
    archives = _archives()
    assert len(archives) >= 2, "يُتوقَّع أرشيفان على الأقلّ (2026-10-22 و2026-10-26)"
    assert audit(archives, _known_paths()) == []


def test_old_ideas_and_jobs_are_all_still_present() -> None:
    """أفكار الأرشيف الأوّل B01–B18 ووظائفه J01–J09 كلّها باقية."""
    definitions: list[str] = []
    jobs: list[str] = []
    for _, text in _archives():
        parsed = _parse(text)
        definitions.extend(parsed[0])
        jobs.extend(parsed[2])
    assert {f"B{n:02d}" for n in range(1, 19)} <= set(definitions)
    assert {f"J{n:02d}" for n in range(1, 10)} <= set(jobs)


def test_a_deleted_old_idea_is_red() -> None:
    """حذف B05 من الأرشيف الأوّل يُظهر ثقباً."""
    archives = _with("2026-10-22", lambda t: _replace_once(t, "### B05 —", "### ملغاة —"))
    assert any("ثقبٌ في الترقيم" in p and "B05" in p for p in audit(archives, _known_paths()))


def test_a_deleted_old_job_is_red() -> None:
    """حذف J04 من جدول الوظائف يُظهر ثقباً."""
    archives = _with("2026-10-22", lambda t: _replace_once(t, "| J04 |", "| — |"))
    assert any("ثقبٌ في الترقيم" in p and "J04" in p for p in audit(archives, _known_paths()))


def test_reusing_an_old_number_is_red() -> None:
    """فكرةٌ جديدة تحمل رقماً قديماً تُرفض."""
    archives = _with("2026-10-26", lambda t: _replace_once(t, "### B28 —", "### B07 —"))
    problems = audit(archives, _known_paths())
    assert any("B07" in p and "لا يُعاد استعماله" in p for p in problems)


def test_an_addendum_to_an_unknown_idea_is_red() -> None:
    """ملحقٌ لفكرةٍ لا وجود لها في أرشيفٍ أسبق يُرفض."""
    archives = _with(
        "2026-10-26",
        lambda t: _replace_once(t, "### B03 (CBAM) — ملحق", "### B99 (CBAM) — ملحق"),
    )
    assert any("ملحقٌ لفكرةٍ لم تُعرَّف" in p for p in audit(archives, _known_paths()))


def test_an_addendum_to_an_unknown_value_chain_path_is_red() -> None:
    """ملحقٌ لمسارٍ غير موجود في سلسلة القيمة يُرفض."""
    archives = _with(
        "2026-10-26",
        lambda t: _replace_once(t, "### OPP-13 (EAA) — ملحق", "### OPP-98 (EAA) — ملحق"),
    )
    assert any("VALUE_CHAIN" in p for p in audit(archives, _known_paths()))


def test_a_new_idea_without_a_source_or_date_is_red() -> None:
    """فكرةٌ جديدة بلا رابطٍ ولا تاريخ تُرفض مرّتين — مرّةً لكلّ قاعدة."""
    stub = "### B29 — فكرةٌ بلا دليل\n\n- ألمٌ مزعوم بلا مصدر.\n\n"
    archives = _with("2026-10-26", lambda t: _replace_once(t, "## 5. ", stub + "## 5. "))
    problems = audit(archives, _known_paths())
    assert any("B29 بلا مصدرٍ" in p for p in problems)
    assert any("B29 بلا تاريخٍ" in p for p in problems)
