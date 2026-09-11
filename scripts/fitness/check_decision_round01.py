#!/usr/bin/env python3
"""بوابة جولة القرار 01 — تتحقق من أن الأرقام المُعلَنة في DECISION-ROUND-01.md مشتقة من السجلين الآليين.

تُشغَّل من جذر المستودع:  python3 studies/algeria-hard-currency/check_decision_round01.py
لا تقرأ إلا CSV/MD مجاورين؛ صفر تبعيات. الفشل صريح (exit 1) بلا تحذيرات.
"""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STUDY = ROOT / "studies" / "algeria-hard-currency"
LEDGER = STUDY / "decision_ledger_round01.csv"
EVIDENCE = STUDY / "evidence_round01.csv"
ROUND = STUDY / "DECISION-ROUND-01.md"

EXPECTED_HYPOTHESES = 32
EXPECTED_LEVELS = {"E0", "E1", "E2"}
#: معرّف كل فئة في جدول 5.1 — يُقرأ العدد من صفّها مباشرة، بلا هشاشة تطابق كامل.
DECLARED_KEYS = {
    "failed": "فاشلة في التكوين الحالي",
    "held": "معلّقة على دليل لازم",
    "unknown-ground": "مجهولة الأساس",
}


def load(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def bucket_state(state: str) -> str:
    if state.startswith("فاشلة"):
        return "failed"
    if state.startswith("مجهولة"):
        return "unknown-ground"
    if "معلّقة" in state or "معلقة" in state:
        return "held"
    return "other"


def check_ledger(ledger: list[dict[str, str]], failures: list[str]) -> dict[str, int]:
    """بنية السجل: صفّية، تفريد، وبوابة/حالة/قرار لكل فرضية — بلا E2 بلا تفويض."""
    counts = dict.fromkeys(DECLARED_KEYS, 0)
    if len(ledger) != EXPECTED_HYPOTHESES:
        failures.append(f"سجل الفرضيات يحوي {len(ledger)} صفاً، المتوقع {EXPECTED_HYPOTHESES}")
    if len({row["id"] for row in ledger}) != len(ledger):
        failures.append("معرفات الفرضيات غير فريدة")
    bad_level = [row["id"] for row in ledger if not re.fullmatch(r"E[0-4]", row["max_level"])]
    if bad_level:
        failures.append(f"صفوف بلا مستوى التزام صالح (E0..E4): {bad_level}")
    levels = {row["max_level"] for row in ledger if re.fullmatch(r"E[0-4]", row["max_level"])}
    if not levels <= EXPECTED_LEVELS:
        failures.append(f"مستويات التزام خارج E0..E2 معلنة في السجل: {sorted(levels)}")
    for row in ledger:
        key = bucket_state(row["gate_state"])
        if key in counts:
            counts[key] += 1
        if row["max_level"] == "E2" and "تفويض" not in row["decision"]:
            failures.append(f"{row['id']}: E2 بلا شرط تفويض مكتوب — يناقض المحرك §5")
        if not (
            row["binding_gate"]
            and row["gate_state"]
            and row["decision"]
            and row["shared_dependency"]
        ):
            failures.append(
                f"{row['id']}: صف بلا بوابة حاكمة أو حالة بوابة أو قرار أو اعتماد مشترك"
            )
        for field in ("key_claim", "key_test"):
            value = row[field]
            if value != "-" and not re.fullmatch(r"[CT]\d\d( [CT]\d\d)*", value):
                failures.append(
                    f"{row['id']}: عمود {field} يحمل {value!r} — انزياح أعمدة أم معرّف خاطئ؟"
                )
        if not re.search(r":|استبعاد|تأجيل|تعليق|تحويل|إبقاء|مؤهل", row["decision"]):
            failures.append(f"{row['id']}: عمود decision يحمل قراراً غير مصوغ ({row['decision']!r})")
    return counts


def check_declared_counts(round_text: str, counts: dict[str, int], failures: list[str]) -> None:
    """الأعداد المنشورة في جدول 5.1 يجب أن تُعاد إنتاجها من CSV، لا أن تُنسخ."""
    for key, label in DECLARED_KEYS.items():
        rows = [ln for ln in round_text.splitlines() if ln.startswith(f"| **{label}**")]
        found = next((re.search(r"\|\s*\*\*(\d+)\*\*", ln) for ln in rows), None)
        if found is None:
            failures.append(f"لم يُعثر على العدد المعلن لفئة {key!r} في جدول 5.1")
        elif int(found.group(1)) != counts[key]:
            failures.append(
                f"عدد {key}: السجل={counts[key]} مقابل المعلن في الجولة={found.group(1)}"
            )


def check_evidence(evidence: list[dict[str, str]], round_text: str, failures: list[str]) -> None:
    ids = [row["id"] for row in evidence]
    if len(set(ids)) != len(ids):
        failures.append("معرفات أدلة مكررة في evidence_round01.csv")
    used = set(re.findall(r"S\d\d", round_text))
    if dangling := sorted(used - set(ids)):
        failures.append(f"استشهاد بمعرّف غير موجود في سجل الأدلة: {dangling}")
    if unreferenced := sorted(set(ids) - used):
        failures.append(
            f"أدلة في السجل لا تستشهد بها الجولة (إما حذفها أو استعمالها): {unreferenced}"
        )
    for row in evidence:
        if row["url"] != "—" and not row["url"].startswith(("https://", "http://")):
            failures.append(f"{row['id']}: رابط غير صالح {row['url']!r}")
        if not row["as_of"]:
            failures.append(f"{row['id']}: بلا تاريخ «الاطلاع/الراهنية»")
        if "ثانو" in row["status"] and "أولي" in row["status"]:
            failures.append(f"{row['id']}: حالة المصدر متناقضة (ثانوي وأولي معاً)")


def check_claims(round_text: str, failures: list[str]) -> None:
    """كل ادعاء C## مُشار إليه يجب أن يملك سطراً في جدول الادعاءات الحاسمة."""
    for cid in sorted(set(re.findall(r"\bC\d\d\b", round_text))):
        if not re.search(rf"^\|\s*`{cid}`\s*\|", round_text, re.MULTILINE):
            failures.append(f"الادعاء {cid} مُشار إليه بلا سطر في جدول الادعاءات")


def main() -> int:
    for path in (LEDGER, EVIDENCE, ROUND):
        if not path.is_file():
            print(f"❌ ملف مفقود: {path.relative_to(ROOT)}")
            return 1
    failures: list[str] = []
    ledger = load(LEDGER)
    round_text = ROUND.read_text(encoding="utf-8")
    counts = check_ledger(ledger, failures)
    check_declared_counts(round_text, counts, failures)
    check_evidence(load(EVIDENCE), round_text, failures)
    check_claims(round_text, failures)
    e1 = sum(1 for row in ledger if row["max_level"] == "E1")
    if f"**{e1}**" not in round_text:
        failures.append(f"عَدّ المرشحين عند E1 في السجل = {e1} وغير معلن بهذه الصيغة في الجولة")
    if failures:
        print("\n".join(f"❌ {f}" for f in failures))
        print(f"\n❌ check_decision_round01: {len(failures)} انتهاكًا.")
        return 1
    print(
        "✅ جولة القرار 01 متسقة مع سجلها: 32 فرضية، بوابة حاكمة لكل فرضية، لا E2 بلا تفويض، "
        "الأعداد المعلنة مشتقة من CSV، ولا استشهاد معلّق في سجل الأدلة."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
