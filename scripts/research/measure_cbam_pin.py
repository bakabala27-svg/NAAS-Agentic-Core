#!/usr/bin/env python3
"""قياسُ دبوس CBAM — CPN (الدفعة الثانية عشرة).

يُولِّد `docs/research/CPN_MEASUREMENTS.json` من `shared/research/cbam_pin.py`،
ويفحص انحرافَ الملفّ المودَع عن إعادة الحساب (`--check`).

## ما يُقاس هنا — وماذا لا يُقاس

يُقاس **رسمُ المسار**: الفرقُ بين مرجع CBAM المستعمل حين تُعلَن القيم الافتراضية
(العمود B) والمرجع المستعمل حين تُعلَن البيانات الفعلية (العمود A)، مضروباً في
معامل CBAM وعامل التصحيح عبر القطاعات. ومنه **عتبةُ العبور** لكلّ رمزٍ مدبوس،
و**أوّلُ سنةٍ غيرِ مشروطة** يصبح فيها الانتقالُ مربحاً بلا أيّ خفضِ انبعاث.

⛔ لا نموذجَ لغويّ يُشغَّل. ⛔ لا منشأةَ تُقاس — انبعاثُ المنشأة مُدخَلُ المشتري
لا مخرَجُنا. ⛔ لا رقمَ إيراد (`revenue_claim = NONE` حقلٌ في الملفّ). ⛔ لا رأيَ
قانونيّ: الصيغةُ محسوبةٌ مقابل مراجعَ مُسندة، وملحقُ IR 2025/2620 الحرفيّ لم
يُستخرج (K4/S4 درجة ب).

## الاستعمال

    python3 scripts/research/measure_cbam_pin.py            # يكتب الملفّ
    python3 scripts/research/measure_cbam_pin.py --check    # يتحقّق من المودَع

حتميٌّ تماماً: لا شبكة، لا ساعة، لا عشوائية. كلّ دبوسٍ ثابتٌ في الوحدة.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from shared.research.cbam_pin import measure_all

OUTPUT = ROOT / "docs" / "research" / "CPN_MEASUREMENTS.json"

#: الحقولُ التي يُقارَن بها المودَعُ عند `--check`: كلُّ رقمٍ يُعاد حسابه.
_CHECKED_KEYS = ("batch", "as_of", "declared_zeros", "inputs_fingerprint", "results", "limits_ar")


def _dump(payload: dict[str, object]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True, default=str) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="قياس CPN — دبوسُ القيم الافتراضية ورسمُ المسار")
    parser.add_argument(
        "--check",
        action="store_true",
        help="افحص انحراف الملفّ المودَع عن إعادة الحساب بدل توليده",
    )
    args = parser.parse_args()

    payload = measure_all()

    if not args.check:
        OUTPUT.write_text(_dump(payload), encoding="utf-8")
        fingerprint = payload["inputs_fingerprint"]
        print(f"✅ كُتب {OUTPUT.relative_to(ROOT)} — بصمة المُدخَلات {fingerprint}")
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

    results = payload["results"]
    closure = results["closure_audit"]
    reversals = results["decision_reversals"]
    flips = sum(1 for item in reversals if item["overstatement_2026"]["ratio"] is None)
    print(
        f"✅ لا انحراف — بصمة {payload['inputs_fingerprint']} · "
        f"{results['rankable_count']}/{len(results['pin_inventory'])} رمزاً قابلٌ للترتيب · "
        f"{flips} من {len(reversals)} حالةً انقلبت إشارتُها · "
        f"{closure['rows_open']} صفوفٍ رسميةٍ لا تُغلق"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
