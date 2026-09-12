#!/usr/bin/env python3
"""بوّابة جولة القرار 02 — أرقامُ الجولة مشتقّة، وأرقامُ الأداة مطابقة لملفّ القياس.

**لماذا بوّابة ثانية بعد `check_decision_round01.py`:** الجولة 02 تُدخل صنفاً جديداً من الادّعاء
لم يكن في الجولة 01 — **رقمٌ عن أداة قياس**. ورقمُ الأداة أخطرُ من رقم السوق: فهو يُقرأ
قياساً على نموذجٍ بينما هو قياسٌ على الأداة نفسها (صفرُ محاكمات). فهذه البوّابة تفرض ثلاثة
أشياء لا تقبل التأويل:

1. **الاشتقاق:** كلّ رقمٍ في §4 من الجولة يُطابَق مع `docs/research/CND_MEASUREMENTS.json`
   بمسارٍ مُسمّى — فكتابة «93 مسباراً» باليد بينما الملفّ يقول 90 صارت فشلاً لا رأياً.
2. **حدُّ القول:** `empty_run_cells.flips_total` يجب أن يبقى صفراً ما لم تحمل الجولة إذناً
   وسقف خسارة؛ و`مستوى الالتزام` لا يتجاوز E1؛ وعبارة «لا يوجد سقف خسارة معتمد» حاضرة.
3. **المحرّمات:** ثماني عباراتٍ تُدحض بأدلّة الجولة (§9) ممنوعةٌ خارج سياق منعٍ صريح، في
   وثائق القرار والمعرفة والعرض والجرد والحالة — فالعبارة المدحوضة تعود إلى النصوص بسهولة
   أكبر ممّا تعود إلى الأرقام.

⛔ لا تقرأ هذه البوّابة شبكةً ولا نموذجاً؛ صفرُ تبعيات خارج المكتبة القياسية.
تُشغَّل من جذر المستودع: `python3 scripts/fitness/check_decision_round02.py` (exit 0/1).
"""

from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STUDY = ROOT / "studies" / "algeria-hard-currency"
LEDGER = STUDY / "decision_ledger_round02.csv"
EVIDENCE = STUDY / "evidence_round02.csv"
ROUND = STUDY / "DECISION-ROUND-02.md"
ARTIFACT = ROOT / "docs" / "research" / "CND_MEASUREMENTS.json"
CATALOG = ROOT / "docs" / "commercial" / "OFFER_CATALOG.json"
OFFER_DOC = ROOT / "docs" / "commercial" / "CND_EXPORTABLE_EVAL_OFFER.md"

#: الوثائق التي تُفحص فيها المحرّمات — كلّ نصٍّ يمكن أن يُقتبس منه ادّعاءٌ مدحوض.
SCANNED_DOCS = (
    ROUND,
    ROOT / "docs" / "research" / "HARD_CURRENCY_NEW_KNOWLEDGE_CND.md",
    ROOT / "docs" / "research" / "AR_FR_SAFETY_BENCHMARK_INVENTORY.md",
    OFFER_DOC,
    ROOT / ".memory" / "cnd_null_invariance_truth.md",
)

EXPECTED_HYPOTHESES = 8
#: ⛔ E2 فأعلى ممنوعة في هذه الجولة: لا سقف خسارة معتمداً ولا إذن تشغيل نموذج (محرك §5).
EXPECTED_LEVELS = {"E0", "E1"}
DECLARED_KEYS = {
    "failed": "فاشلة في التكوين الحالي",
    "held": "معلّقة على دليل لازم",
    "unknown-ground": "مجهولة الأساس",
}

#: عبارةُ عدم الإنفاق — غيابُها يعني أنّ الجولة صارت توصي بإنفاقٍ بلا سقف.
NO_SPEND_PHRASE = "لا يوجد سقف خسارة معتمد"

#: عباراتٌ تدحضها أدلّةُ الجولة (§3 و§9): ممنوعةٌ خارج سياق منعٍ صريح.
FORBIDDEN_CLAIMS = (
    "لا يوجد معيار",
    "لا معيارَ سلامة",
    "اكتشفنا",
    "نحن وحدنا",
    "نضمن الامتثال",
    "معدّل تسريب النموذج",
    "مُثبتُ الجدّة",
    "مُثبت الجدّة",
)
#: سياقُ المنع: سطرٌ يحمل علامة المنع أو كلمة نفي/تحريم صريحة.
NEGATION_MARKERS = ("⛔", "ممنوع", "لا يجوز", "كذب", "محرّم", "منقوض", "منقوضة", "يدحض")


def load_csv(path: Path) -> list[dict[str, str]]:
    """يقرأ سجلاً CSV — والفشلُ صريحٌ لا قائمةٌ فارغة تُقرأ نجاحاً."""
    with path.open(encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def bucket_state(state: str) -> str:
    """تصنيفُ حالة البوابة كما في الجولة 01 — المصدرُ `gate_state` لا نصٌّ يدوي."""
    if state.startswith("فاشلة"):
        return "failed"
    if state.startswith("مجهولة"):
        return "unknown-ground"
    if "معلّقة" in state or "معلقة" in state:
        return "held"
    return "other"


def check_ledger(ledger: list[dict[str, str]], failures: list[str]) -> dict[str, int]:
    """بنيةُ السجل: صفّية، تفريد، بوابة/حالة/قرار لكلّ فرضية، ⛔ ولا مستوى فوق E1."""
    counts = dict.fromkeys(DECLARED_KEYS, 0)
    if len(ledger) != EXPECTED_HYPOTHESES:
        failures.append(f"سجلّ الجولة 02 يحوي {len(ledger)} صفاً، والمتوقّع {EXPECTED_HYPOTHESES}")
    if len({row["id"] for row in ledger}) != len(ledger):
        failures.append("معرّفات الفرضيات غير فريدة")
    bad_level = [row["id"] for row in ledger if not re.fullmatch(r"E[0-4]", row["max_level"])]
    if bad_level:
        failures.append(f"صفوف بلا مستوى التزام صالح (E0..E4): {bad_level}")
    levels = {row["max_level"] for row in ledger if re.fullmatch(r"E[0-4]", row["max_level"])}
    if not levels <= EXPECTED_LEVELS:
        failures.append(
            f"مستويات التزام خارج E0/E1 معلَنة في السجل: {sorted(levels - EXPECTED_LEVELS)} — "
            f"⛔ {NO_SPEND_PHRASE}، فلا E2 في هذه الجولة (محرك الالتزام §5)"
        )
    for row in ledger:
        key = bucket_state(row["gate_state"])
        if key in counts:
            counts[key] += 1
        if row["max_level"] not in {"E0", "E1", "E2", "E3", "E4"}:
            failures.append(f"{row['id']}: مستوى التزام غير معروف")
        if not (row["binding_gate"] and row["gate_state"] and row["decision"]):
            failures.append(f"{row['id']}: صفٌّ بلا بوّابة حاكمة أو حالة أو قرار")
        if not row["shared_dependency"]:
            failures.append(f"{row['id']}: صفٌّ بلا اعتماد مشترك — «محفظة متنوّعة» بلا فحص العُقد")
        for field in ("key_claim", "key_test"):
            value = row[field]
            if value != "-" and not re.fullmatch(r"[CT]\d\d( [CT]\d\d)*", value):
                failures.append(
                    f"{row['id']}: عمود {field} يحمل {value!r} — انزياحُ أعمدة أم معرّف خاطئ؟"
                )
        if not re.search(r":|استبعاد|تأجيل|تعليق|تحويل|إبقاء|مؤهل", row["decision"]):
            failures.append(f"{row['id']}: عمود decision يحمل قراراً غير مصوغ ({row['decision']!r})")
    return counts


def check_declared_counts(
    round_text: str,
    ledger: list[dict[str, str]],
    counts: dict[str, int],
    failures: list[str],
) -> None:
    """الأعدادُ المنشورة في §5.1 تُعاد إنتاجها من CSV، ولا تُنسخ."""
    for key, label in DECLARED_KEYS.items():
        rows = [line for line in round_text.splitlines() if line.startswith(f"| **{label}**")]
        found = next((re.search(r"\|\s*\*\*(\d+)\*\*", line) for line in rows), None)
        if found is None:
            failures.append(f"لم يُعثر على العدد المعلَن لفئة {key!r} في جدول §5.1")
        elif int(found.group(1)) != counts[key]:
            failures.append(
                f"عدد {key}: السجلّ={counts[key]} مقابل المعلَن في الجولة={found.group(1)}"
            )
    e1 = sum(1 for row in ledger if row["max_level"] == "E1")
    if f"**{e1}**" not in round_text:
        failures.append(f"عَدّ المرشّحين عند E1 في السجلّ = {e1} وغيرُ معلَن بهذه الصيغة في الجولة")
    e2 = sum(1 for row in ledger if row["max_level"] == "E2")
    rows = [line for line in round_text.splitlines() if line.startswith("| **مؤهَّلة لـ E2")]
    found = next((re.search(r"\|\s*\*\*(\d+)\*\*", line) for line in rows), None)
    if found is None:
        failures.append("صفّ «مؤهَّلة لـ E2 عند تفويض» مفقود من §5.1 — الصفرُ يجب أن يُقال")
    elif int(found.group(1)) != e2:
        failures.append(f"عدد المؤهَّلين لـE2: السجلّ={e2} مقابل المعلَن={found.group(1)}")


def check_evidence(evidence: list[dict[str, str]], round_text: str, failures: list[str]) -> None:
    """سجلُّ الأدلة: لا استشهاد معلّق، ولا دليلٌ غير مستعمل، ولا تاريخٌ غائب."""
    ids = [row["id"] for row in evidence]
    if len(set(ids)) != len(ids):
        failures.append("معرّفات أدلة مكرّرة في evidence_round02.csv")
    used = set(re.findall(r"S\d\d", round_text))
    if dangling := sorted(used - set(ids)):
        failures.append(f"استشهادٌ بمعرّف غير موجود في سجلّ الأدلة: {dangling}")
    if unreferenced := sorted(set(ids) - used):
        failures.append(f"أدلّةٌ في السجلّ لا تستشهد بها الجولة: {unreferenced}")
    for row in evidence:
        if row["url"] != "—" and not row["url"].startswith(("https://", "http://")):
            failures.append(f"{row['id']}: رابطٌ غير صالح {row['url']!r}")
        if not row["as_of"]:
            failures.append(f"{row['id']}: بلا تاريخ «الاطلاع/الراهنية»")
        if not row["independence_note"]:
            failures.append(f"{row['id']}: بلا ملاحظة استقلال — السندُ بلا نسبةٍ يُقرأ حيادياً")
        if "ثانو" in row["status"] and "أولي" in row["status"]:
            failures.append(f"{row['id']}: حالةُ المصدر متناقضة (ثانوي وأولي معاً)")


def check_claims(round_text: str, failures: list[str]) -> None:
    """كلّ ادّعاء `C##` مُشار إليه يملك سطراً في جدول §6."""
    for cid in sorted(set(re.findall(r"\bC\d\d\b", round_text))):
        if not re.search(rf"^\|\s*`{cid}`\s*\|", round_text, re.MULTILINE):
            failures.append(f"الادّعاء {cid} مُشارٌ إليه بلا سطر في جدول الادّعاءات الحاسمة")


def _split_path(path: str) -> list[str]:
    """يفصل المسار على النقاط **خارج الأقواس** — `a[b=0.02].c` قطعةٌ واحدة قبل النقطة."""
    segments: list[str] = []
    depth = 0
    current: list[str] = []
    for char in path:
        if char == "[":
            depth += 1
        elif char == "]":
            depth -= 1
        if char == "." and depth == 0:
            segments.append("".join(current))
            current = []
            continue
        current.append(char)
    segments.append("".join(current))
    return [segment for segment in segments if segment]


_SEGMENT = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)((?:\[[^\]]*\])*)$")
_FILTER = re.compile(r"\[([A-Za-z_][A-Za-z0-9_]*)=([^\]]*)\]")


def _scalar_matches(actual: object, declared: str) -> bool:
    """مقارنةٌ متسامحة مع النوع: `0.02` في المسار تساوي 0.02 في JSON."""
    lowered = declared.strip().lower()
    if lowered in {"true", "false"}:
        return actual is (lowered == "true")
    try:
        return float(declared) == float(str(actual))
    except (TypeError, ValueError):
        return str(actual) == declared.strip()


def _resolve(artifact: object, path: str) -> object:
    """يحلّ مساراً مثل `maturity_gap[scope=x][kind=y].pairs` — والفشل `KeyError` صريح."""
    node = artifact
    for segment in _split_path(path):
        match = _SEGMENT.match(segment)
        if match is None:
            raise KeyError(f"قطعةُ مسار غير صالحة في {path!r}: {segment!r}")
        name, filters = match.group(1), match.group(2)
        if not isinstance(node, dict) or name not in node:
            raise KeyError(f"المفتاح {name!r} غير موجود في الملفّ (المسار {path!r})")
        node = node[name]
        conditions = _FILTER.findall(filters)
        if not conditions:
            continue
        if not isinstance(node, list):
            raise KeyError(f"المرشِّح [{conditions[0][0]}=…] يتطلّب قائمة عند {path!r}")
        # المرشِّحات المتسلسلة شرطُها واحد: تُطبَّق كلّها على القائمة نفسها (صفٌّ واحد يطابقها)
        matches = [
            item
            for item in node
            if isinstance(item, dict)
            and all(key in item and _scalar_matches(item[key], value) for key, value in conditions)
        ]
        if len(matches) != 1:
            rendered = "".join(f"[{key}={value}]" for key, value in conditions)
            raise KeyError(f"المرشِّح {rendered} أعطى {len(matches)} نتيجة عند {path!r}")
        node = matches[0]
    return node


def _parse_declared(raw: str) -> object:
    """يقرأ القيمة المعلَنة: JSON إن أمكن (`93` · `true` · `[]`) وإلا نصّاً."""
    text = raw.strip().strip("`")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text


def _equal(actual: object, declared: object) -> bool:
    if isinstance(actual, bool) or isinstance(declared, bool):
        return actual is declared
    if isinstance(actual, (int, float)) and isinstance(declared, (int, float)):
        return abs(float(actual) - float(declared)) < 1e-9
    return actual == declared


def measurement_section(round_text: str) -> str:
    """يقطع §4 وحدها — فجدولُ الادّعاءات (§6) وجدولُ الاختبارات (§7) يحملان خلايا مُعكَّسة أيضاً."""
    start = round_text.find("\n## 4.")
    if start < 0:
        return ""
    rest = round_text[start:]
    end = re.search(r"\n## \d", rest[1:])
    return rest[: end.start() + 1 if end else len(rest)]


def check_measurements(round_text: str, failures: list[str]) -> tuple[dict[str, object], int]:
    """كلُّ رقمٍ عن الأداة في §4 يُطابَق مع ملفّ القياس بمسارٍ مُسمّى."""
    if not ARTIFACT.is_file():
        failures.append(
            f"ملفّ القياس مفقود: {ARTIFACT.relative_to(ROOT)} — شغّل measure_cnd_instrument.py"
        )
        return {}, 0
    try:
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        failures.append(f"`CND_MEASUREMENTS.json` ليس JSON صالحاً: {error}")
        return {}, 0

    section = measurement_section(round_text)
    rows = re.findall(r"^\|\s*`([^`]+)`\s*\|\s*([^|]+?)\s*\|$", section, re.MULTILINE)
    if len(rows) < 10:
        failures.append(
            f"جدول §4 يحمل {len(rows)} صفّاً فقط — الأرقامُ المشتقّة يجب أن تُعلَن بمساراتها (≥10)"
        )
    for path, declared_raw in rows:
        declared = _parse_declared(declared_raw)
        try:
            actual = _resolve(artifact, path)
        except KeyError as error:
            failures.append(f"§4: مسارٌ غير قابل للحلّ في ملفّ القياس — {error}")
            continue
        if not _equal(actual, declared):
            failures.append(f"§4: `{path}` = {actual!r} في ملفّ القياس مقابل {declared!r} معلَناً")
    if "⛔" not in str(artifact.get("what_this_is_not_ar", "")):
        failures.append("ملفّ القياس فقد حارسَ الاستشهاد الكاذب (`what_this_is_not_ar` بلا ⛔)")
    return artifact, len(rows)


def check_no_model_run(artifact: dict[str, object], round_text: str, failures: list[str]) -> None:
    """صفرُ محاكمات ⇒ صفرُ ادّعاء أثر؛ وإن شُغِّل نموذجٌ فإذنٌ وسقف خسارة مكتوبان.

    الحارسُ نفسه (`empty_run_cells`) يجب أن يبقى في ملفّ القياس: حذفُه يُسكت الشاهد
    بدل أن يُقنعه — وهذا أسوأ من غيابه أصلاً.
    """
    if not artifact:
        return
    try:
        flips = int(str(_resolve(artifact, "empty_run_cells.flips_total")))
    except (KeyError, ValueError):
        failures.append("ملفّ القياس فقد `empty_run_cells.flips_total` — حارسُ صفرِ المحاكمات مفقود")
        return
    authorized = "إذنُ تشغيل" in round_text and NO_SPEND_PHRASE not in round_text
    if flips > 0 and not authorized:
        failures.append(
            f"empty_run_cells.flips_total = {flips} بلا إذن تشغيل وسقف خسارة — "
            "رقمُ انقلابٍ في مستودعٍ لم يشغّل نموذجاً هو استشهادٌ كاذب"
        )
    if flips == 0 and "صفر محاكمات" not in round_text and "صفرُ محاكمات" not in round_text:
        failures.append("الجولة لا تقول صراحةً إنّ صفرَ محاكماتٍ جرى — الصمتُ يُقرأ قياساً")


def check_no_spend(round_text: str, failures: list[str]) -> None:
    """عدمُ الإنفاق يُقال نصّاً: غيابُ العبارة يعني توصيةً بلا سقف."""
    if NO_SPEND_PHRASE not in round_text:
        failures.append(
            f"الجولة لا تحمل العبارة الإلزامية {NO_SPEND_PHRASE!r} — ⛔ توصيةٌ بلا سقف خسارة"
        )


def _display(path: Path) -> str:
    """مسارٌ نسبيٌّ إن أمكن — ومسارٌ خارج الشجرة يُقال كما هو ولا يُسقط الفحص.

    ⛔ `relative_to` ترفع `ValueError` على مسارٍ خارج الجذر؛ ولو تُركت لرفعت الفحصُ
    استثناءً بدل أن يُبلّغ انتهاكاً — والاستثناءُ يُقرأ عطلاً في البوّابة لا كذباً في النصّ.
    """
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def check_forbidden_claims(failures: list[str]) -> None:
    """عباراتٌ تدحضها أدلّةُ الجولة: ممنوعةٌ خارج سطرِ منعٍ صريح."""
    for document in SCANNED_DOCS:
        if not document.is_file():
            failures.append(f"وثيقةٌ مفقودة في فحص المحرّمات: {_display(document)}")
            continue
        for number, line in enumerate(document.read_text(encoding="utf-8").splitlines(), start=1):
            if any(marker in line for marker in NEGATION_MARKERS):
                continue
            hits = [claim for claim in FORBIDDEN_CLAIMS if claim in line]
            if hits:
                failures.append(
                    f"{_display(document)}:{number}: عبارةٌ مدحوضة خارج سياق منع {hits} — «{line.strip()[:90]}»"
                )


def check_offer_lines(failures: list[str]) -> None:
    """لا خطَّ عرضٍ وهميّ ولا ثامن: كلّ معرّف يُسمّى في العرض موجود، ولا معرّفَ لأداتنا."""
    if not OFFER_DOC.is_file() or not CATALOG.is_file():
        failures.append("وثيقةُ العرض أو كتالوج العروض مفقود — لا فحص لخطوط العرض")
        return
    try:
        catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        failures.append(f"`OFFER_CATALOG.json` ليس JSON صالحاً: {error}")
        return
    known = {offer.get("id") for offer in catalog.get("offers", [])}
    cited = set(
        re.findall(r"`([a-z][a-z0-9]*(?:-[a-z0-9]+)+)`", OFFER_DOC.read_text(encoding="utf-8"))
    )
    if phantom := sorted(cited - known):
        failures.append(f"العرضُ يسمّي خطوطاً غير موجودة في الكتالوج: {phantom} — خطٌّ وهمي يُقرأ مصرَّحاً")
    if eighth := sorted(name for name in known if name and ("cnd" in name or "null" in name)):
        failures.append(f"خطُّ عرضٍ ثامن لأداتنا في الكتالوج: {eighth} — ⛔ D-290 L8")


def main() -> int:
    for path in (LEDGER, EVIDENCE, ROUND, ARTIFACT):
        if not path.is_file():
            print(f"❌ ملفٌّ مفقود: {path.relative_to(ROOT)}")
            return 1
    failures: list[str] = []
    ledger = load_csv(LEDGER)
    round_text = ROUND.read_text(encoding="utf-8")

    counts = check_ledger(ledger, failures)
    check_declared_counts(round_text, ledger, counts, failures)
    check_evidence(load_csv(EVIDENCE), round_text, failures)
    check_claims(round_text, failures)
    artifact, measured_rows = check_measurements(round_text, failures)
    check_no_model_run(artifact, round_text, failures)
    check_no_spend(round_text, failures)
    check_forbidden_claims(failures)
    check_offer_lines(failures)

    if failures:
        print("\n".join(f"❌ {failure}" for failure in failures))
        print(f"\n❌ check_decision_round02: {len(failures)} انتهاكاً.")
        return 1
    print(
        "✅ جولة القرار 02 متّسقة: "
        f"{len(ledger)} فرضيات مشتقّة من سجلّها، ⛔ لا مستوى فوق E1، "
        f"و{measured_rows} رقماً عن الأداة في §4 مطابقةٌ لملفّ القياس الحتمي، "
        "وصفرُ محاكماتٍ معلَن، وصفرُ استشهادٍ معلّق، وصفرُ عبارةٍ مدحوضة خارج منعٍ صريح."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
