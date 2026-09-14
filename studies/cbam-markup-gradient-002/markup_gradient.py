"""إعادة حساب القيمة المعرّضة للخطر في CBAM باستخدام تدرّج العلاوة.

دراسة 002 — بدون اعتماديات خارجية. لا يقرأ ولا يكتب ملفات.

الفكرة المركزية:
    الوفر الذي يحصل عليه المستورد من استبدال القيمة الافتراضية ببيانات فعلية =
    (القيمة الافتراضية × (1 + العلاوة) - الانبعاث الفعلي) × الطنّية × سعر الشهادة × معامل CBAM

    وهذا يبيّن أن العلاوة — وليس الفجوة وحدها — هي ما يولّد الدافع للشراء.

كل المدخلات أدناه مُعلنة وقابلة للاستبدال؛ ليست وقائع مثبتة لمنشأة بعينها.
"""

from __future__ import annotations

# --- مدخلات معلنة (افتراضات، ليست وقائع) ---

CERT_PRICE_EUR = 75.28  # €/tCO2e — مرجع المستودع (الربع الثاني 2026)

CBAM_FACTOR = {2026: 0.975, 2027: 0.95, 2028: 0.9, 2029: 0.775}

# العلاوة المطبّقة على القيم الافتراضية (مصادر ثانوية — ادعاء من الدرجة ب)
MARKUP = {
    "iron_steel": {2026: 0.10, 2027: 0.20, 2028: 0.30, 2029: 0.30},
    "aluminium": {2026: 0.10, 2027: 0.20, 2028: 0.30, 2029: 0.30},
    "cement": {2026: 0.10, 2027: 0.20, 2028: 0.30, 2029: 0.30},
    "fertiliser": {2026: 0.01, 2027: 0.01, 2028: 0.01, 2029: 0.01},
}

# افتراض عام: انخفاض القيم الافتراضية الأساسية بموجب 2026/1740
DEFAULT_VALUE_REDUCTION = 0.68  # منتصف مدى 63-74%


def savings_per_tonne(
    old_default_tco2e: float,
    actual_tco2e: float,
    sector: str,
    year: int,
    reduction: float = DEFAULT_VALUE_REDUCTION,
    cert_price: float = CERT_PRICE_EUR,
) -> dict:
    """يرجع مقارنة بين النموذج القديم (فجوة فقط) والنموذج المصحّح."""
    factor = CBAM_FACTOR[year]
    markup = MARKUP[sector][year]

    # النموذج القديم في المستودع: الفجوة مقابل القيمة القديمة، بلا علاوة ولا معامل
    legacy = max(0.0, old_default_tco2e - actual_tco2e) * cert_price

    # النموذج المصحّح
    new_default = old_default_tco2e * (1.0 - reduction)
    charged = new_default * (1.0 + markup)
    corrected = max(0.0, charged - actual_tco2e) * cert_price * factor

    # كم من الوفر المصحّح يعود للعلاوة وحدها؟
    markup_only = new_default * markup * cert_price * factor

    return {
        "sector": sector,
        "year": year,
        "new_default_tco2e": round(new_default, 4),
        "charged_tco2e": round(charged, 4),
        "legacy_eur_per_t": round(legacy, 2),
        "corrected_eur_per_t": round(corrected, 2),
        "markup_share_eur_per_t": round(markup_only, 2),
        "legacy_overstatement_x": round(legacy / corrected, 2) if corrected > 0 else None,
    }


def value_at_stake(tonnes: float, **kw) -> dict:
    """القيمة المعرّضة للخطر لشحنة/منشأة بكاملها."""
    unit = savings_per_tonne(**kw)
    unit["tonnes"] = tonnes
    unit["legacy_eur_total"] = round(unit["legacy_eur_per_t"] * tonnes, 2)
    unit["corrected_eur_total"] = round(unit["corrected_eur_per_t"] * tonnes, 2)
    return unit


def demo() -> None:
    """سيناريو توضيحي بمدخلات مخترعة معلنة — ليس ادعاءً عن منشأة حقيقية."""
    # القيم القديمة والفعلية افتراضية بالكامل (tCO2e لكل طن منتج)
    scenarios = [
        ("iron_steel", 2.10, 1.85),
        ("fertiliser", 2.60, 2.20),
    ]
    for year in (2026, 2027, 2028):
        for sector, old_def, actual in scenarios:
            r = value_at_stake(
                tonnes=100_000,
                old_default_tco2e=old_def,
                actual_tco2e=actual,
                sector=sector,
                year=year,
            )
            print(
                f"{r['year']} {r['sector']:<11} "
                f"markup_share={r['markup_share_eur_per_t']:>7} EUR/t  "
                f"corrected_total={r['corrected_eur_total']:>12} EUR  "
                f"legacy_total={r['legacy_eur_total']:>12} EUR"
            )


if __name__ == "__main__":
    demo()
