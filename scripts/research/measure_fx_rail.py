#!/usr/bin/env python3
"""قياسُ سكّة العملة الصعبة — FXR.

يُولِّد `docs/research/FXR_MEASUREMENTS.json` من `shared/research/fx_rail.py`،
ويفحص انحرافَ الملف المودَع عن إعادة الحساب (`--check`).

    # التوليد
    python3 scripts/research/measure_fx_rail.py
    # بوّابة الانحراف (تفشل إن كان المودَع ≠ المحسوب)
    python3 scripts/research/measure_fx_rail.py --check

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

from shared.research.fx_rail import measure_all

OUTPUT = ROOT / "docs" / "research" / "FXR_MEASUREMENTS.json"


def main() -> int:
    parser = argparse.ArgumentParser(description="قياس FXR — سكّة العملة الصعبة")
    parser.add_argument(
        "--check",
        action="store_true",
        help="افحص انحراف الملف المودَع عن إعادة الحساب بدل توليده",
    )
    args = parser.parse_args()

    payload = measure_all()

    if args.check:
        if not OUTPUT.is_file():
            print(f"❌ ملفّ القياس غير مودَع: {OUTPUT.relative_to(ROOT)}")
            return 1
        committed = json.loads(OUTPUT.read_text(encoding="utf-8"))
        if committed != payload:
            drifted = sorted(
                key
                for key in set(committed) | set(payload)
                if committed.get(key) != payload.get(key)
            )
            print(f"❌ FXR_MEASUREMENTS.json منحرفٌ عن إعادة الحساب في: {drifted}")
            print("   أعد التوليد: python3 scripts/research/measure_fx_rail.py")
            return 1
        results = payload["results"]
        cap = results["ae_ceiling"]
        print("✅ FXR_MEASUREMENTS.json مطابقٌ لإعادة الحساب.")
        print(
            f"   سقفُ المقاول الذاتي: {cap['ceiling_dzd']} دج = "
            f"{cap['usd_per_year_at_official_low']}–"
            f"{cap['usd_per_year_at_official_high']} $/سنة "
            f"({cap['usd_per_month_worst']} $/شهر في الأسوأ)"
        )
        fit_high = results["target_fit"]["board_target_high_8000"]
        print(f"   هدف 8000$/شهر: {fit_high['verdict']} (مضاعف {fit_high['ratio']}×)")
        print(
            f"   السكك: {len(results['rails_ranked'])} مُرتَّبة · "
            f"الآجال: {len(results['contract_terms'])} مُفحوصة"
        )
        return 0

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    results = payload["results"]
    cap = results["ae_ceiling"]
    print(f"✅ كُتب ملف القياس: {OUTPUT.relative_to(ROOT)}")
    print(
        f"   سقفُ الكيان: {cap['ceiling_dzd']} دج → "
        f"{cap['usd_per_year_at_official_low']}–{cap['usd_per_year_at_official_high']} $/سنة"
    )
    print(
        f"   الفجوة: {payload['fx_snapshot']['gap_pct_worst_case']}% (أسوأ) / "
        f"{payload['fx_snapshot']['gap_pct_as_published_exdz']}% (منشور)"
    )
    pen = results["spread_penalty"]
    print(
        f"   ما يبقى بعد دورة التحويل: {pen['usd_recovered_per_usd_after_round_trip']} $ "
        f"لكل $ ⇒ مضاعفُ الدفع المباشر {round(1 / pen['usd_recovered_per_usd_after_round_trip'], 3)}×"
    )
    print(
        f"   السكك: {len(results['rails_ranked'])} · "
        f"قنواتُ الطلب خارج البيع: {len(results['demand_channels_outside_sales'])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
