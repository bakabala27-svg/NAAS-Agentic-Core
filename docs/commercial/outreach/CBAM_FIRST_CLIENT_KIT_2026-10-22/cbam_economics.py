#!/usr/bin/env python3
"""آلة حساب اقتصاد CBAM — حتمية، stdlib فقط، بلا شبكة وبلا نموذج لغوي.

**لماذا وُجدت:** المستودع سحب من الواجهة calculator CBAM القديم لأنّه حمل معامل
0.025 خطأً (≈71×) وانبعاثاتِ مصانعَ مُختلَقة (انظر `tools/hard_currency_engine/cli.py`).
هذه الأداة تعيد بناء الحساب من الصفر، بمدخلاتٍ منشورةٍ مؤرَّخة، وبصيغةٍ مكتوبةٍ
قابلةٍ للفحص، وبلا أيّ رقمِ مصنعٍ مُخترَع. كل مدخل يحمل معرّف سندٍ من
`EVIDENCE.csv`؛ وكل رقم مشتقّ يُحسب هنا ولا يُنسخ.

**الصيغة (لكلّ طنٍّ من السلعة):**
    adjusted_embedded = embedded × (1 + default_markup)      # مسار القيم الافتراضية فقط
    free_allocation   = benchmark × (1 − cbam_factor)        # التخصيص المجاني المتبقّي
    certificates      = max(0, adjusted_embedded − free_allocation)
    cost              = certificates × certificate_price

**لماذا `max(0, …)`:** لا تُصدر شهادةٌ سالبة. المصنع الذي تقلّ انبعاثاته عن
التخصيص المجاني لا يدفع شيئاً في تلك السنة، ولا يُقاصّ الفرق. إغفال هذا الحدّ
هو ما يجعل بعض التقديرات المنشورة تبالغ في «الوفر».

**ما لا تفعله:** لا تختار القيمة الافتراضية الصحيحة لصنفٍ جزائري بعينه. القيمة
المستعملة هنا (2.310 tCO2e/t لـCN 7207 11 14، صفّ «Other countries») هي مثالٌ
منشور؛ قبل أيّ عرضٍ لعميلٍ يجب قراءة Annex I للائحة (EU) 2025/2621 للصنف
والمنشأ الفعليين. الأداة تحسب ما تُعطى، لا أكثر.

الاستعمال:
    python3 docs/commercial/outreach/CBAM_FIRST_CLIENT_KIT_2026-10-22/cbam_economics.py
    python3 docs/commercial/outreach/CBAM_FIRST_CLIENT_KIT_2026-10-22/cbam_economics.py --check
    python3 docs/commercial/outreach/CBAM_FIRST_CLIENT_KIT_2026-10-22/cbam_economics.py --json

Exit 0 = سليم · 1 = انحراف عن القيم المتوقّعة.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

# ---------------------------------------------------------------------------
# المدخلات المنشورة — كلٌّ بمعرّف سنده في EVIDENCE.csv
# ---------------------------------------------------------------------------

#: سعر الشهادة، الربع الثالث 2026 (المفوضية الأوروبية، 2026-10-05) — E05
CERTIFICATE_PRICE_EUR_PER_TCO2E = 82.32

#: علامة القيمة الافتراضية 2026 (IR (EU) 2025/2621) — E06
DEFAULT_MARKUP_2026 = 0.10

#: القيمة الافتراضية للصلب نصف المصنّع CN 7207 11 14، صفّ «Other countries» — E44
DEFAULT_EMBEDDED_TCO2E_PER_T = 2.310

#: معيار الصلب Column B (Implementing Regulation (EU) 2025/2620) — E44
BENCHMARK_TCO2E_PER_T = 1.364

#: حصة التخصيص المجاني المتبقّي في 2026 = 97.5% ⇒ معامل CBAM = 2.5% — E45
CBAM_FACTOR_2026 = 0.025

#: سيناريوهات الانبعاثات الفعلية المُتحقَّقة (tCO2e/t). ليست قياساً لمصنعٍ بعينه.
ACTUAL_SCENARIOS = (0.80, 1.00, 1.20, 1.50, 2.00, 2.31)

#: كلفة التحقق المنشورة (تقديرات سوق، لا تعرفة تنظيمية) — E11
VERIFICATION_FEE_LOW = 5_000
VERIFICATION_FEE_HIGH = 50_000
VERIFICATION_FEE_MID = 15_000

#: حجم تصدير توضيحي للصلب الطويل الجزائري إلى EU في 2024 — E14
ILLUSTRATIVE_VOLUME_T = 350_000

#: مسار التخلص التدريجي من التخصيص المجاني (حصة محتفَظ بها) — E45
FREE_ALLOCATION_RETAINED = {
    2026: 0.975,
    2027: 0.950,
    2028: 0.900,
    2029: 0.775,
    2030: 0.515,
    2031: 0.390,
    2032: 0.265,
    2033: 0.140,
    2034: 0.000,
}

#: القيم المتوقّعة التي يفحصها --check (محسوبة يدوياً ومكتوبة صراحةً)
EXPECTED = {
    "default_with_markup": 2.541,
    "free_allocation_2026": 1.3299,
    "certificates_default_2026": 1.2111,
    "cost_default_2026": 99.70,
    "cost_actual_1_0_2026": 0.0,
    "saving_actual_1_0_2026": 99.70,
    "payback_tonnes_mid_fee_actual_1_0": 150.5,
}


@dataclass(frozen=True)
class ProductInputs:
    """مدخلات صنفٍ واحد. القيم كلّها منشورة أو معلنة، لا مُختلَقة."""

    cn_code: str
    label_ar: str
    default_embedded: float
    benchmark: float
    certificate_price: float
    default_markup: float
    cbam_factor: float

    @property
    def default_with_markup(self) -> float:
        return self.default_embedded * (1.0 + self.default_markup)

    @property
    def free_allocation(self) -> float:
        return self.benchmark * (1.0 - self.cbam_factor)

    def certificates(self, embedded: float) -> float:
        """شهادات لكلّ طنٍّ؛ لا تُصدر سالبة."""
        return max(0.0, embedded - self.free_allocation)

    def cost(self, embedded: float) -> float:
        return self.certificates(embedded) * self.certificate_price

    def default_cost(self) -> float:
        return self.cost(self.default_with_markup)

    def saving(self, actual_embedded: float) -> float:
        """الوفر لكلّ طنٍّ = كلفة الافتراضي − كلفة الفعلي. لا يتجاوز كلفة الافتراضي."""
        return self.default_cost() - self.cost(actual_embedded)

    def payback_tonnes(self, fee: float, actual_embedded: float) -> float | None:
        """الطنونات اللازمة لاسترداد كلفة التحقق. None إذا كان الوفر صفراً."""
        per_tonne = self.saving(actual_embedded)
        if per_tonne <= 0:
            return None
        return fee / per_tonne


def _r(value: float, digits: int = 4) -> float:
    return round(value, digits)


def build_payload() -> dict:
    steel = ProductInputs(
        cn_code="7207 11 14",
        label_ar="صلب نصف مصنّع (حديد/صلب) — صفّ «Other countries»",
        default_embedded=DEFAULT_EMBEDDED_TCO2E_PER_T,
        benchmark=BENCHMARK_TCO2E_PER_T,
        certificate_price=CERTIFICATE_PRICE_EUR_PER_TCO2E,
        default_markup=DEFAULT_MARKUP_2026,
        cbam_factor=CBAM_FACTOR_2026,
    )

    scenarios = []
    for actual in ACTUAL_SCENARIOS:
        scenarios.append(
            {
                "actual_embedded_tco2e_per_t": actual,
                "certificates_per_t": _r(steel.certificates(actual)),
                "cost_eur_per_t": _r(steel.cost(actual), 2),
                "saving_eur_per_t": _r(steel.saving(actual), 2),
                "payback_tonnes_fee_5000": _r(steel.payback_tonnes(5_000, actual) or 0.0, 1),
                "payback_tonnes_fee_15000": _r(steel.payback_tonnes(15_000, actual) or 0.0, 1),
                "payback_tonnes_fee_50000": _r(steel.payback_tonnes(50_000, actual) or 0.0, 1),
                "annual_saving_eur_350kt": _r(steel.saving(actual) * ILLUSTRATIVE_VOLUME_T, 0),
            }
        )

    phase_in = []
    for year, retained in FREE_ALLOCATION_RETAINED.items():
        product = ProductInputs(
            cn_code=steel.cn_code,
            label_ar=steel.label_ar,
            default_embedded=steel.default_embedded,
            benchmark=steel.benchmark,
            certificate_price=steel.certificate_price,
            default_markup=0.30 if year >= 2028 else (0.20 if year == 2027 else 0.10),
            cbam_factor=1.0 - retained,
        )
        phase_in.append(
            {
                "year": year,
                "free_allocation_retained": retained,
                "default_markup": product.default_markup,
                "cost_default_eur_per_t": _r(product.default_cost(), 2),
                "cost_actual_1_0_eur_per_t": _r(product.cost(1.0), 2),
                "saving_actual_1_0_eur_per_t": _r(product.saving(1.0), 2),
                "saving_actual_1_5_eur_per_t": _r(product.saving(1.5), 2),
            }
        )

    return {
        "$schema_version": 1,
        "purpose_ar": (
            "اقتصاد CBAM لصنفٍ واحد، بصيغةٍ معلنة ومدخلاتٍ منشورة. "
            "ليس تقييماً لمصنعٍ بعينه، ولا عرضاً تجارياً، ولا ادّعاءَ تحقّق."
        ),
        "as_of": "2026-10-22",
        "inputs": {
            **asdict(steel),
            "verification_fee_low_eur": VERIFICATION_FEE_LOW,
            "verification_fee_mid_eur": VERIFICATION_FEE_MID,
            "verification_fee_high_eur": VERIFICATION_FEE_HIGH,
            "illustrative_volume_t": ILLUSTRATIVE_VOLUME_T,
        },
        "derived_2026": {
            "default_with_markup_tco2e_per_t": _r(steel.default_with_markup),
            "free_allocation_tco2e_per_t": _r(steel.free_allocation),
            "certificates_default_per_t": _r(steel.certificates(steel.default_with_markup)),
            "cost_default_eur_per_t": _r(steel.default_cost(), 2),
        },
        "scenarios": scenarios,
        "phase_in": phase_in,
        "limits_ar": [
            "القيمة الافتراضية تختلف بحسب رمز CN والمنشأ؛ هذه قيمة مثال منشورة.",
            "سعر الشهادة يتغيّر كلّ ربع سنة؛ استُعمل سعر Q3 2026 فقط.",
            "الوفر يقع لصالح المُصرِّح الأوروبي (من يشتري الشهادات)، لا لصالح المصدّر الجزائري تلقائياً.",
            "مسار التخلص التدريجي من التخصيص المجاني قد يتغيّر تشريعياً؛ الجدول هنا منشور ثانوي.",
            "لا تدخل هنا كلفةَ قياسٍ ولا كلفةَ تدقيقٍ داخلي ولا أثرَ ضريبة الكربون الجزائرية (غير موجودة).",
            "جدول التدرّج 2026–2034 يثبّت سعر الشهادة عند 82.32 EUR لكلّ السنوات — للتوضيح لا للتنبؤ.",
        ],
        "sources_ar": [
            "E05 سعر شهادة CBAM، Q3 2026 = 82.32 EUR — المفوضية الأوروبية، 2026-10-05",
            "E06 علامة القيمة الافتراضية 2026 = 10% — IR (EU) 2025/2621",
            "E44 القيمة الافتراضية 2.310 والمعيار 1.364 — Annex I / IR (EU) 2025/2620",
            "E45 معامل CBAM 2026 = 2.5% وجدول التخلص التدريجي",
            "E11 كلفة التحقق 5,000–50,000 EUR — تقديرات سوق منشورة، لا تعرفة",
            "E14 حجم توضيحي 350,000 t صلب طويل إلى EU في 2024 — Sandbag",
        ],
    }


def _flatten(payload: dict) -> dict:
    flat = {
        "default_with_markup": payload["derived_2026"]["default_with_markup_tco2e_per_t"],
        "free_allocation_2026": payload["derived_2026"]["free_allocation_tco2e_per_t"],
        "certificates_default_2026": payload["derived_2026"]["certificates_default_per_t"],
        "cost_default_2026": payload["derived_2026"]["cost_default_eur_per_t"],
    }
    for row in payload["scenarios"]:
        key = str(row["actual_embedded_tco2e_per_t"]).replace(".", "_")
        flat[f"cost_actual_{key}_2026"] = row["cost_eur_per_t"]
        flat[f"saving_actual_{key}_2026"] = row["saving_eur_per_t"]
        flat[f"payback_tonnes_mid_fee_actual_{key}"] = row["payback_tonnes_fee_15000"]
    return flat


def check(payload: dict) -> list[str]:
    flat = _flatten(payload)
    failures: list[str] = []
    for key, expected in EXPECTED.items():
        got = flat.get(key)
        if got is None:
            failures.append(f"❌ مفتاح مفقود: {key}")
        elif abs(float(got) - float(expected)) > 0.02:
            failures.append(f"❌ {key}: متوقّع {expected} · محسوب {got}")
    return failures


def _say(line: str = "") -> None:
    """مخرجُ الطرفية لهذه الأداة واجهتُها — والكتابة المباشرة تحترم حظر `print` في هذا المستودع."""
    sys.stdout.write(f"{line}\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="إخراج JSON كامل")
    parser.add_argument("--check", action="store_true", help="فحص القيم المتوقّعة")
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).resolve().parent / "CBAM_ECONOMICS.json",
        help="مسار كتابة JSON (افتراضي: بجانب السكربت)",
    )
    args = parser.parse_args()

    payload = build_payload()
    args.out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if args.check:
        failures = check(payload)
        if failures:
            for line in failures:
                _say(line)
            return 1
        _say("✅ اقتصاد CBAM متّسق: كل قيمة متوقّعة مطابقة.")
        return 0

    if args.json:
        _say(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    d = payload["derived_2026"]
    _say("CBAM — صلب نصف مصنّع CN 7207 11 14 (مثال منشور)")
    _say(f"  القيمة الافتراضية + العلامة: {d['default_with_markup_tco2e_per_t']} tCO2e/t")
    _say(f"  التخصيص المجاني المتبقّي:    {d['free_allocation_tco2e_per_t']} tCO2e/t")
    _say(f"  الشهادات لكلّ طنّ:            {d['certificates_default_per_t']}")
    _say(f"  الكلفة لكلّ طنّ:              €{d['cost_default_eur_per_t']}")
    _say()
    _say("  الفعلي | كلفة/طنّ | وفر/طنّ | استرداد €15k | وفر 350kt")
    for row in payload["scenarios"]:
        _say(
            f"  {row['actual_embedded_tco2e_per_t']:>6} | "
            f"€{row['cost_eur_per_t']:>7} | "
            f"€{row['saving_eur_per_t']:>7} | "
            f"{row['payback_tonnes_fee_15000']:>10} t | "
            f"€{row['annual_saving_eur_350kt']:>12,.0f}"
        )
    _say()
    _say(f"  كُتب: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
