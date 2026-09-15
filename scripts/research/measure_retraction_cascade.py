#!/usr/bin/env python3
"""قياسُ تتالي السحب — RCL (الدفعة الحادية عشرة).

يُولِّد `docs/research/RCL_MEASUREMENTS.json` من
`shared/research/retraction_cascade.py`، ويفحص انحرافَ الملفّ المودَع عن إعادة
الحساب (`--check`).

## ما يُقاس هنا — وماذا لا يُقاس

يُقاس **سطحُ الاقتباس**: بعد أن سحبت `FCM` (2026-09-15) نموذجَ ميزانية الأيام،
أيُّ ادّعاءٍ في أيّ ملفّ قياسٍ صار غيرَ قابلٍ للاقتباس، وأيٌّ نجا مضيَّقاً، وأيٌّ
أُعيد تصنيفُه. ومعها **القيدُ البديل** محسوباً، و**المسارُ الحرج** إلى أوّل عرضٍ
قابلٍ للإرسال مصنَّفاً بحسب مَن يُغلق البطاقة.

⛔ لا نموذجَ لغويّ يُشغَّل. ⛔ لا عميلَ يُقاس. ⛔ لا رقمَ إيراد
(`revenue_claim = NONE` حقلٌ في الملفّ). ⛔ لا رأيَ قانوني.

## الاستعمال

    python3 scripts/research/measure_retraction_cascade.py            # يكتب الملفّ
    python3 scripts/research/measure_retraction_cascade.py --check    # يتحقّق من المودَع

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

from shared.research.retraction_cascade import measure_all

OUTPUT = ROOT / "docs" / "research" / "RCL_MEASUREMENTS.json"

#: الحقولُ التي يُقارَن بها المودَعُ عند `--check`: كلُّ رقمٍ يُعاد حسابه.
_CHECKED_KEYS = ("batch", "as_of", "declared_zeros", "inputs_fingerprint", "results", "limits_ar")


def _dump(payload: dict[str, object]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="قياس RCL — تتالي السحب وسطحُ الاقتباس")
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

    if not OUTPUT.exists():
        print(f"❌ {OUTPUT.relative_to(ROOT)} غير موجود — شغّل الأداة بلا `--check` أوّلاً")
        return 1

    try:
        filed = json.loads(OUTPUT.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        print(f"❌ الملفّ المودَع ليس JSON صالحاً: {error}")
        return 1

    drift = [key for key in _CHECKED_KEYS if filed.get(key) != payload.get(key)]
    if drift:
        print(f"❌ انحرافٌ في: {', '.join(drift)}")
        print("   الملفّ المودَع لا يطابق إعادة الحساب — ⛔ البصمةُ المكتوبةُ باليد ادّعاء.")
        return 1

    surface = payload["results"]["quotable_surface"]
    path = payload["results"]["sendable_path"]
    print(
        f"✅ لا انحراف — بصمة {payload['inputs_fingerprint']} · "
        f"{surface['by_state']['QUOTABLE']}/{surface['total']} ادّعاءً قابلٌ للاقتباس · "
        f"المسارُ الحرج {path['length']} بطاقات (owner_free={path['owner_free']})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
