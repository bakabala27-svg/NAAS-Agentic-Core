#!/usr/bin/env python3
"""قياسُ التحقق عبر الفاتورة الأولى — FIV (الدفعة العاشرة).

يُولِّد `docs/research/FIV_MEASUREMENTS.json` من `shared/research/first_invoice.py`،
ويفحص انحرافَ الملفّ المودَع عن إعادة الحساب (`--check`).

## ما يُقاس هنا — وماذا لا يُقاس

يُقاس **شروطُ التسوية المُعلَنة** لخمس قنوات تحصيلٍ مرشّحة كما نشرتها مصادرُها
الأولية بتاريخ 2026-09-15: مسارُ الدفع (مُعلَنٌ في 2 من 5) · الرسمُ (مُعلَنٌ لفئةٍ
واحدةٍ من ثلاث) · بوّابةُ الدخول · نطاقُ أمثلة الإدراج الستة (⛔ أمثلةٌ لا مبيعات).

⛔ لا نموذجَ لغويّ يُشغَّل. ⛔ لا عميلَ يُقاس. ⛔ لا عقدَ مُسوّى يُدَّعى
(`settled_contracts = 0` · `revenue_claim = NONE` حقلان في الملفّ).

## الاستعمال

    python3 scripts/research/measure_first_invoice.py            # يكتب الملفّ
    python3 scripts/research/measure_first_invoice.py --check    # يتحقّق من المودَع

حتميٌّ تماماً: لا شبكة، لا ساعة، لا عشوائية.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from shared.research.first_invoice import measure_all

OUTPUT = ROOT / "docs" / "research" / "FIV_MEASUREMENTS.json"

#: الحقولُ التي يُقارَن بها المودَعُ عند `--check`: كلُّ رقمٍ يُعاد حسابه.
_CHECKED_KEYS = ("batch", "as_of", "declared_zeros", "inputs_fingerprint", "results")


def _dump(payload: dict[str, object]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="قياس FIV — التحقق عبر الفاتورة الأولى")
    parser.add_argument(
        "--check",
        action="store_true",
        help="افحص انحراف الملفّ المودَع عن إعادة الحساب بدل توليده",
    )
    args = parser.parse_args()

    payload = measure_all()

    if not args.check:
        OUTPUT.write_text(_dump(payload), encoding="utf-8")
        print(f"✅ كُتب {OUTPUT.relative_to(ROOT)} — بصمة المُدخَلات {payload['inputs_fingerprint']}")
        return 0

    if not OUTPUT.is_file():
        print(f"❌ ملفّ القياس مفقود: {OUTPUT.relative_to(ROOT)}")
        return 1
    try:
        stored = json.loads(OUTPUT.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"❌ ملفّ القياس ليس JSON صالحاً: {exc}")
        return 1

    failures: list[str] = []
    for key in _CHECKED_KEYS:
        if stored.get(key) != payload.get(key):
            failures.append(f"انحرافٌ في `{key}`: المودَع ≠ إعادة الحساب")
    if "Infinity" in OUTPUT.read_text(encoding="utf-8") or "NaN" in OUTPUT.read_text(
        encoding="utf-8"
    ):
        failures.append("⛔ `Infinity`/`NaN` في الملفّ — الغيابُ لا يُلاعَن (D-212)")

    if failures:
        print("\n".join(f"❌ {failure}" for failure in failures))
        return 1
    print(f"✅ FIV_MEASUREMENTS.json يطابق إعادة الحساب — بصمة {payload['inputs_fingerprint']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
