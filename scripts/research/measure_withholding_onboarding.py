#!/usr/bin/env python3
"""قياسُ انحراف الاستقطاع والتأهيل — WOD (الدفعة الثامنة).

يُولِّد `docs/research/WOD_MEASUREMENTS.json` من `shared/research/withholding_onboarding.py`،
ويفحص انحرافَ الملفّ المودَع عن إعادة الحساب (`--check`).

## ما يُقاس هنا — وماذا لا يُقاس

يُقاس **رَقمان لا يُخلَطان**:

1. ما يبقى من الفاتورة بعد استقطاعِ بلد المشتري، لكلّ (سوق × وصفِ عقد)، مع منعِ
   اقتباسِ كلّ خليةٍ لا يُعرَف نصُّها (`None` بسببٍ منطوق لا صفراً).
2. ما يعبر من فئات المشترين عند خطٍّ أساسيٍّ مُعلن، وأصغرُ حزمةِ قدراتٍ تفتح أكبرَ عددٍ
   منها داخل ميزانيةِ جهدٍ معلنة (بحثٌ شامل، لا تقدير)، ثم سُلَّمُ المرجع بعد الفاتورة.

⛔ لا نموذجَ لغويّ يُشغَّل. ⛔ لا عميلَ يُقاس. ⛔ لا رقمَ ماليّ: الكلفةُ بوحدة جهدٍ (أيام ⚙️)
والحاصلُ **نسبةٌ** لا مبلغ، و`revenue_claim = NONE` حقلٌ في الملفّ.

## الاستعمال

    python3 scripts/research/measure_withholding_onboarding.py            # يكتب الملفّ
    python3 scripts/research/measure_withholding_onboarding.py --check    # يتحقّق من المودَع

حتميٌّ تماماً: لا شبكة، لا ساعة، لا عشوائية — فلا طابعَ زمنٍ يُستثنى.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from shared.research.withholding_onboarding import measure_all

OUTPUT = ROOT / "docs" / "research" / "WOD_MEASUREMENTS.json"

#: الحقولُ التي يُقارَن بها المودَعُ عند `--check`: كلُّ رقمٍ يُعاد حسابه.
_CHECKED_KEYS = ("batch", "as_of", "declared_zeros", "inputs_fingerprint", "results")


def _dump(payload: dict[str, object]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="قياس WOD — انحراف الاستقطاع والتأهيل")
    parser.add_argument(
        "--check",
        action="store_true",
        help="افحص انحراف الملفّ المودَع عن إعادة الحساب بدل توليده",
    )
    args = parser.parse_args()

    payload = measure_all()

    if args.check:
        if not OUTPUT.is_file():
            print(f"❌ ملفُّ القياس مفقود: {OUTPUT.relative_to(ROOT)}")
            return 1
        committed = json.loads(OUTPUT.read_text(encoding="utf-8"))
        drifted = [
            key
            for key in _CHECKED_KEYS
            if json.dumps(committed.get(key), ensure_ascii=False, sort_keys=True)
            != json.dumps(payload.get(key), ensure_ascii=False, sort_keys=True)
        ]
        if drifted:
            print(f"❌ WOD_MEASUREMENTS.json منحرفٌ عن إعادة الحساب في: {drifted}")
            return 1
        results = payload["results"]
        cells = results["cells"]  # type: ignore[index]
        print(
            "✅ WOD_MEASUREMENTS.json مطابقٌ لإعادة الحساب "
            f"({cells['quotable']}/{cells['total']} خليةً قابلةً للاقتباس · "
            f"بصمة {str(payload['inputs_fingerprint'])[:12]}…)."
        )
        return 0

    OUTPUT.write_text(_dump(payload), encoding="utf-8")
    results = payload["results"]
    print(f"✅ كُتب {OUTPUT.relative_to(ROOT)}")
    print(f"   خلايا قابلة للاقتباس: {results['cells']['quotable']}")  # type: ignore[index]
    print(f"   خلايا ممنوعة (نصّ ناقص): {results['cells']['blocked']}")  # type: ignore[index]
    print(f"   فئات المشترين: {results['archetypes']['status_counts']}")  # type: ignore[index]
    print(
        "   خطة الفتح: "
        f"{results['plan']['chosen']} ⇒ {results['plan']['opened']} "  # type: ignore[index]
        f"(جهد {results['plan']['effort_units']})"  # type: ignore[index]
    )
    print(f"   شروط القتل المتحقّقة: {results['kill_switches']}")  # type: ignore[index]
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
