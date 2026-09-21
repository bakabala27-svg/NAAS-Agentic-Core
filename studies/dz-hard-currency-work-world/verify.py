#!/usr/bin/env python3
"""فارضُ دراسة «عالم العمل بالعملة الصعبة» — يُشغَّل يدوياً (غير مربوط بـCI).

**لماذا وُجد:** في هذا المستودع، رقمٌ مكتوب في نثرٍ بلا فارضٍ آلي يُنسى أو يُنسَخ خطأً
(صنف ISS-186). الدراسة تحمل أرقاماً مشتقّة (سقف ANAE باليورو، فارق السوق الموازي، كلفة
قناة الدفع) وأرقاماً منقولة (سعر بنك الجزائر، نسبة IFU، شرط الوثيقة البنكية). هذه الأداة
تفرض شيئين لا ثالث:

1. **كل رقم منقول يحمل مصدراً وتاريخاً ونوعاً من سُلَّم معلوم** — سندٌ بلا تاريخ ليس سنداً.
2. **كل رقم مشتقّ يُعاد حسابه من مدخلاته المعلنة** — فلا يمرّ رقمٌ مُعدَّل يدوياً.

⛔ **ما لا تفعله:** لا تتحقّق من صحة المصادر نفسها (لا إنترنت هنا)، ولا تُدّعي أكثر من
الهيكل والحساب. صدقُها في حدّها المعلن، على عرف D-208 §6.

الاستعمال:  python3 studies/dz-hard-currency-work-world/verify.py
Exit 0 = نظيف · 1 = انتهاك (مع قائمة صريحة).
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CLAIMS = HERE / "claims_2026-09-21.csv"
CHANNELS = HERE / "channels_2026-09-21.csv"

CLAIM_COLUMNS = {
    "id",
    "claim",
    "value",
    "unit",
    "type",
    "confidence",
    "source",
    "source_date",
    "note",
}
CHANNEL_COLUMNS = {
    "rail",
    "type",
    "available_in_dz",
    "evidence",
    "evidence_source",
    "evidence_date",
    "fees_published",
    "trap",
    "status",
}

#: سُلَّم نوع الدليل — مغلقٌ عن قصد. نوعٌ جديد يُضاف بقرار، لا بكتابةٍ عابرة.
ALLOWED_TYPES = {
    "official",
    "official_regulation",
    "press",
    "provider",
    "community",
    "computed",
    "open",
    "contradiction",
}
ALLOWED_CONFIDENCE = {"high", "medium_high", "medium", "low"}
#: حالات قناة الدفع — مغلقة كذلك. «depends» ليست حالة، بل غياب قرار.
ALLOWED_RAIL_STATUS = {
    "usable",
    "usable_with_caution",
    "read_only",
    "open",
    "prohibited",
    "prohibited_as_base",
}

#: مدخلات الحساب — كلٌّ منها يعيش في صفٍّ من claims يحمل مصدره.
OFFICIAL_RATE = 154.19  # RATE-OFF-01
PARALLEL_RATE = 276.67  # RATE-PAR-01
CEILING_DZD = 5_000_000  # ANAE-01
IFU_RATE = 0.005  # ANAE-04
PAYONEER_LOW, PAYONEER_HIGH = 0.012, 0.04  # FEE-01

#: المتوقَّع صراحةً: id → (القيمة العددية أو المدى، الوحدة)
EXPECTED_COMPUTED = {
    "ANAE-02": (round(CEILING_DZD / OFFICIAL_RATE, 1), "EUR/year"),
    "ANAE-03": (round(CEILING_DZD / OFFICIAL_RATE / 12, 1), "EUR/month"),
    "GAP-01": (round((PARALLEL_RATE - OFFICIAL_RATE) / OFFICIAL_RATE * 100, 1), "percent"),
    "LOSS-01": (round((1 - OFFICIAL_RATE / PARALLEL_RATE) * 100, 1), "percent"),
    "IFU-01": (round(CEILING_DZD * IFU_RATE, 1), "DZD/year"),
    "FEE-03": (
        (
            round(CEILING_DZD / OFFICIAL_RATE * PAYONEER_LOW),
            round(CEILING_DZD / OFFICIAL_RATE * PAYONEER_HIGH),
        ),
        "EUR/year",
    ),
}


def read_csv(path: Path, columns: set[str], failures: list[str]) -> list[dict[str, str]]:
    if not path.exists():
        failures.append(f"الملف مفقود: {path.name}")
        return []
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        header = set(reader.fieldnames or [])
        if header != columns:
            missing, extra = columns - header, header - columns
            failures.append(
                f"{path.name}: أعمدة غير مطابقة (ناقص={sorted(missing)} زائد={sorted(extra)})"
            )
            return []
        return list(reader)


def as_number(value: str) -> float | None:
    try:
        return float(value)
    except ValueError:
        return None


def check_claims(rows: list[dict[str, str]], failures: list[str]) -> dict[str, dict[str, str]]:
    by_id: dict[str, dict[str, str]] = {}
    for row in rows:
        rid = row["id"].strip()
        if not rid:
            failures.append("صفٌّ بلا معرّف")
            continue
        if rid in by_id:
            failures.append(f"معرّف مكرّر: {rid}")
        by_id[rid] = row

        for field in ("claim", "value", "unit", "source", "source_date"):
            if not (row.get(field) or "").strip():
                failures.append(f"{rid}: الحقل «{field}» فارغ — سندٌ بلا قيمة أو تاريخ ليس سنداً")
        if row["type"] not in ALLOWED_TYPES:
            failures.append(f"{rid}: نوع دليل خارج السُّلَّم: {row['type']!r}")
        if row["confidence"] not in ALLOWED_CONFIDENCE:
            failures.append(f"{rid}: درجة ثقة خارج السُّلَّم: {row['confidence']!r}")
        if row["type"] == "computed" and "مشتق" not in row["source"]:
            failures.append(f"{rid}: رقمٌ مُعلَن كمشتقّ ولا يُصرّح بصيغته في المصدر")
        if row["type"] == "open" and row["confidence"] != "low":
            failures.append(f"{rid}: بندٌ مفتوح بثقة عالية — المفتوح لا يُمنح ثقة")
    return by_id


def check_computed(by_id: dict[str, dict[str, str]], failures: list[str]) -> list[str]:
    checked: list[str] = []
    for rid, (expected, unit) in EXPECTED_COMPUTED.items():
        row = by_id.get(rid)
        if row is None:
            failures.append(f"رقم مشتقّ مفقود من السجل: {rid}")
            continue
        if row["unit"] != unit:
            failures.append(f"{rid}: الوحدة {row['unit']!r} والمتوقَّع {unit!r}")
        if isinstance(expected, tuple):
            low, high = (
                as_number(row["value"].split("-")[0]),
                as_number(row["value"].split("-")[-1]),
            )
            if low is None or high is None or (low, high) != expected:
                failures.append(f"{rid}: المدى المسجَّل {row['value']!r} ≠ المحسوب {expected}")
        else:
            got = as_number(row["value"])
            if got is None or abs(got - expected) > 0.05:
                failures.append(f"{rid}: القيمة المسجَّلة {row['value']!r} ≠ المحسوبة {expected}")
        checked.append(rid)
    return checked


def check_channels(rows: list[dict[str, str]], failures: list[str]) -> int:
    for row in rows:
        rail = row["rail"].strip() or "<بلا اسم>"
        if row["status"] not in ALLOWED_RAIL_STATUS:
            failures.append(f"{rail}: حالة خارج السُّلَّم: {row['status']!r}")
        for field in ("evidence", "evidence_source", "evidence_date", "trap"):
            if not (row.get(field) or "").strip():
                failures.append(f"{rail}: الحقل «{field}» فارغ — قناة بلا فخّ معلن فخُّها مجهول")
        if row["available_in_dz"] == "yes" and not row["evidence_source"].strip():
            failures.append(f"{rail}: مُعلَنة متاحة بلا مصدر")
        if (
            row["status"] in {"prohibited", "prohibited_as_base"}
            and "prohibited" not in row["available_in_dz"]
        ):
            failures.append(f"{rail}: حالة «ممنوعة» مع توفّر مُعلَن — تناقض داخلي")
    names = [r["rail"] for r in rows]
    if len(names) != len(set(names)):
        failures.append("قنوات مكرّرة في السجل")
    return len(rows)


def main() -> int:
    failures: list[str] = []
    claims = read_csv(CLAIMS, CLAIM_COLUMNS, failures)
    channels = read_csv(CHANNELS, CHANNEL_COLUMNS, failures)
    by_id = check_claims(claims, failures)
    checked = check_computed(by_id, failures)
    n_channels = check_channels(channels, failures)

    if failures:
        print("❌ فرض دراسة العملة الصعبة: انتهاكات صريحة")
        for item in failures:
            print(f"  - {item}")
        return 1

    print(
        "✅ سجل الأدلة سليم: "
        f"{len(claims)} ادعاءً (منها {len(checked)} رقماً مشتقاً أُعيد حسابه حتمياً) · "
        f"{n_channels} قناة دفع بحالة معلَنة وفخّ مكتوب."
    )
    print(
        "   الأرضية المحسوبة: سقف ANAE = "
        f"{CEILING_DZD / OFFICIAL_RATE:,.1f} €/سنة · فارق السوق الموازي = "
        f"{(PARALLEL_RATE - OFFICIAL_RATE) / OFFICIAL_RATE * 100:.1f}% · "
        f"خسارة التحويل الرسمي = {(1 - OFFICIAL_RATE / PARALLEL_RATE) * 100:.1f}%"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
