"""مؤشرُ البنية البيعية — SSI (Sellability Structure Index).

معرفةٌ جديدة مستقلة (دفعة SSI — الترقيمُ الدستوري محجوزٌ للمالك): **العروضُ القابلة
للتحقّق في السوق تشترك في بنيةٍ خماسيةٍ قابلةٍ للقياس، لا في «جودةٍ» غامضة.**

الأطروحة (قابلةٌ للدحض، لا ادّعاءَ عميل)
----------------------------------------
كلُّ عرضٍ يُباع فعليًا يمكن ترميزه بخمس سماتٍ ثنائية:
  P: سعرٌ ثابتٌ معلن (published fixed price)
  S: نطاقٌ ثابت (fixed scope: ما يدخل وما يخرج)
  T: زمنُ تسليمٍ ثابت (fixed delivery time)
  R: عكسُ مخاطر (risk reversal: استرداد/ضمان/إعادة اختبار)
  F: مدخلٌ مجاني (free entry: عيّنة/قالب/فاحص/استشارة تعريفية)

SSI = (P+S+T+R+F)/5 ∈ {0.0, 0.2, 0.4, 0.6, 0.8, 1.0}

المصدرُ الوحيد للترميز: حالاتُ MF-01 الستُّ والعشرون
(`studies/market-first-sales-reality/evidence_mf_round01.csv` — اطلاع 2026-09-18).
الترميزُ أُجري يدويًا من نصوص البائعين أنفسهم؛ أيُّ سمةٍ لم تُنشَر تُرمَّز 0
(الغيابُ يُقرأ غيابًا لا صفرًا مفترضًا — والفرقُ موثّق في K-SSI01).

حدودٌ معلنة (تُقرأ مع كل رقمٍ يخرج من هنا)
-------------------------------------------
1. العيّنةُ n=26 (منها 19 قابلةٌ للترميز، و7 مراجعُ سوقية بلا SSI) متحيّزةٌ لوب
   الإنجليزية والبحث العام — الغيابُ فيها ليس غيابًا في السوق.
2. الترميزُ بمرمِّزٍ واحد (single coder) — لا يُدَّعى اتفاقُ مرمِّزين حتى يُقاس.
3. SSI يقيس **البنيةَ** لا الطلب: عرضٌ بـSSI=1.0 بلا ردٍّ سوقيٍّ فرضيةٌ مدحوضةُ
   التحويل لا حقيقةُ بيع (H-SSI01 يختبر ذلك بتجارب T-MF01/02/03).
4. الأسعارُ بالدولار التقريبي للمقارنة فقط (EUR→USD بسعرٍ معلنٍ في القياس) —
   لا نتيجةَ صرفٍ تُقتبَس كحقيقة.
5. الحزمة stdlib فقط ولا استيراد من `app/`: تُشحَن إلى عميلٍ لا يملك تبعياتنا.
6. ⛔ صفرُ تشغيلِ نموذج · ⛔ صفرُ قياسٍ على عميل · ⛔ لا خطَّ ثامن.

الاستعمال:
    python3 shared/research/offer_sellability.py --check   # اختباراتٌ ذاتية حتمية
    python3 shared/research/offer_sellability.py --emit    # إصدارُ SSI_MEASUREMENTS.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import dataclass
from typing import Literal

Kind = Literal["offer", "marketplace", "funnel", "anchor", "reference", "labor"]
GRADABLE: frozenset[str] = frozenset({"offer", "marketplace", "funnel", "anchor"})

FEATURES: tuple[str, ...] = ("P", "S", "T", "R", "F")


@dataclass(frozen=True, slots=True)
class Case:
    """حالةُ بيعٍ من MF-01 مرمَّزةً بالسمات الخمس (1=منشورة في مصدر البائع)."""

    id: str
    kind: str
    p: int
    s: int
    t: int
    r: int
    f: int
    note: str = ""


# الترميزُ الكنسي (v1 — 2026-09-18). أيُّ تعديلٍ يغيّر البصمةَ أدناه ويستوجب
# إعادةَ إصدار SSI_MEASUREMENTS.json في نفس التغيير.
CASES: tuple[Case, ...] = (
    Case("S01", "offer", 1, 1, 1, 0, 0, "$12-18K ثابت · نظام واحد · ~أسبوعان"),
    Case("S02", "offer", 1, 1, 1, 1, 0, "$35-55K ثابت · ~4 أسابيع · إعادة اختبار 30 يومًا"),
    Case("S03", "offer", 1, 0, 0, 0, 0, "retainer شهري بلا نطاق/زمن ثابتين"),
    Case("S04", "reference", 0, 0, 0, 0, 0, "نطاقٌ سوقي لا عرضٌ — بلا SSI"),
    Case("S05", "offer", 1, 1, 0, 0, 1, "طبقات $200/$2000 · اشتراك · طبقة مجانية"),
    Case("S06", "offer", 1, 1, 1, 1, 1, "€249 · نطاق ثابت · 24 ساعة · استرداد كامل · قالب مجاني"),
    Case("S07", "offer", 1, 1, 1, 1, 1, "4 حزم · أسابيع ثابتة · استرداد · استشارة مجانية"),
    Case("S08", "offer", 1, 1, 1, 1, 0, "€1250 · نظام واحد · يوما عمل · ضمان استرداد"),
    Case("S09", "offer", 1, 1, 1, 0, 0, "$89-299/شهر · دقائق · متعدد الأطر"),
    Case("S10", "reference", 0, 0, 0, 0, 0, "نطاقاتٌ سوقية لا عرضٌ — بلا SSI"),
    Case("S11", "reference", 0, 0, 0, 0, 0, "بطاقاتُ أجورٍ مجمّعة — بلا SSI"),
    Case("S12", "reference", 0, 0, 0, 0, 0, "أسعارُ وحدةٍ تخطيطية — بلا SSI"),
    Case("S13", "offer", 1, 0, 0, 0, 0, "$4-8/ساعة بلا نطاق ثابت"),
    Case("S14", "marketplace", 1, 1, 0, 1, 0, "نطاقات مشاريع + حماية دفع المنصة"),
    Case("S15", "reference", 0, 0, 0, 0, 0, "شريطُ أجورٍ لا عرضٌ — بلا SSI"),
    Case("S16", "labor", 0, 0, 0, 0, 0, "سوقُ عملٍ (تشتري لا تبيع) — بلا SSI"),
    Case("S17", "marketplace", 0, 1, 0, 0, 0, "$81M دفعاتٌ مثبتة لاحقًا بلا سعرٍ ثابت"),
    Case("S18", "marketplace", 0, 1, 0, 0, 0, "دفعاتٌ مثبتة بلا سعرٍ ثابت"),
    Case(
        "S19", "offer", 1, 1, 1, 1, 1, "$4925 · 5 أيام · 7 أيام تسليم · إعادة اختبار · حاسبة مجانية"
    ),
    Case("S20", "reference", 0, 0, 0, 0, 0, "نطاقاتٌ سوقية لا عرضٌ — بلا SSI"),
    Case("S21", "anchor", 1, 1, 0, 0, 0, "رسومٌ ثابتة معلنة $7-20K لنطاق Type II"),
    Case("S22", "offer", 1, 1, 0, 0, 0, "$0.05+/كلمة لوثائق الأعمال"),
    Case("S23", "offer", 1, 1, 0, 0, 0, "$0.12-0.14/كلمة + شهادة"),
    Case("S24", "offer", 1, 1, 0, 0, 0, "$249/شهر اشتراك"),
    Case("S25", "offer", 1, 1, 0, 0, 1, "$29-39 · نواة مفتوحة/مجانية"),
    Case("S26", "funnel", 0, 1, 1, 0, 1, "فاحصٌ مجاني + PDF في 10-15 دقيقة — إشارةُ طلب"),
)

# سُلَّم الفاتورة الأولى (K-SSI02): عروضُ الدخول ضيقةُ النطاق (نظامٌ واحد،
# تسليمٌ ≤7 أيام) مقابلَ الاشتباكات الكاملة (أسبوعان فأكثر). الأسعارُ بالدولار
# التقريبي (EURUSD=1.08 معلن) — للمقارنة لا للاقتباس.
EURUSD = 1.08
FIRST_INVOICE_TIER: dict[str, float] = {
    "S06": round(249 * EURUSD, 2),  # €249 → ~$269
    "S08": round(1250 * EURUSD, 2),  # €1250 → ~$1350
    "S19": 4925.0,  # $4925 ثابت
    "S14-floor": 500.0,  # أرضيةُ المشاريع المركزة
}
FULL_ENGAGEMENT_TIER: dict[str, float] = {
    "S01-floor": 12000.0,
    "S02-floor": 35000.0,
}
FIRST_INVOICE_CEILING_USD = 5000.0

# البياض AR/FR (K-SSI03): عروضٌ منشورة بسعرٍ ثابت مخصصةٌ للعربية/الفرنسية
# في العيّنة — صفرٌ في العيّنة، وليس صفرًا في السوق.
AR_FR_SPECIFIC_FIXED_PRICE_OFFERS_IN_SAMPLE = 0


def ssi(case: Case) -> float | None:
    """مؤشرُ البنية البيعية — `None` لغير القابل للترميز (لا يُقرأ صفرًا)."""
    if case.kind not in GRADABLE:
        return None
    return (case.p + case.s + case.t + case.r + case.f) / 5.0


def grade(value: float | None) -> str:
    """الدرجةُ البنيوية — عتباتٌ معلنة لا تُحرَّك لاحقًا بلا نسخةٍ جديدة."""
    if value is None:
        return "UNGRADED"
    if value >= 1.0:
        return "STRUCTURALLY_COMPLETE"
    if value >= 0.8:
        return "STRONG"
    if value >= 0.4:
        return "PARTIAL"
    return "WEAK"


def missing_elements(case: Case) -> tuple[str, ...]:
    """السماتُ الغائبة — وهي خطةُ التغليف (كلُّ غيابٍ إجراءٌ واحد)."""
    if case.kind not in GRADABLE:
        return ()
    feats = {"P": case.p, "S": case.s, "T": case.t, "R": case.r, "F": case.f}
    return tuple(k for k in FEATURES if not feats[k])


def audit_offer(name: str, kind: str, p: int, s: int, t: int, r: int, f: int) -> dict:
    """تدقيقُ عرضٍ مرشَّحٍ (لنا أو لعميل): الدرجة + الغياب + إجراءات التغليف."""
    case = Case(name, kind, p, s, t, r, f)
    value = ssi(case)
    actions = {
        "P": "أعلِن سعرًا ثابتًا لنطاقٍ ثابت (أو أرضيةً ثابتة + سقفًا ثابتًا)",
        "S": "ثبِّت النطاق: ما يدخل وما يخرج ومعيارُ القبول — كتابةً",
        "T": "ثبِّت زمنَ التسليم بالأيام — لا «حسب التعقيد» وحده",
        "R": "أضِف عكسَ مخاطر: استردادٌ مشروط أو إعادةُ اختبارٍ أو ضمانُ نطاق",
        "F": "أضِف مدخلًا مجانيًا: عيّنةٌ مجرّدة أو قالبٌ أو فاحصٌ أو استشارةُ نطاق",
    }
    return {
        "offer": name,
        "ssi": value,
        "grade": grade(value),
        "missing": list(missing_elements(case)),
        "packaging_actions": [actions[k] for k in missing_elements(case)],
    }


def aggregates() -> dict:
    """الإحصاءاتُ المشتقّة — كلُّ رقمٍ يُعاد إنتاجُه بـ`--emit`."""
    graded: list[tuple[Case, float]] = [(c, v) for c in CASES if (v := ssi(c)) is not None]
    nums: list[float] = [v for _, v in graded]
    by_id = {c.id: v for c, v in graded}
    feat_freq = {
        feat: round(sum(getattr(c, feat.lower()) for c, _ in graded) / len(graded), 4)
        for feat in FEATURES
    }
    tier1_max = max(FIRST_INVOICE_TIER.values())
    tier2_min = min(FULL_ENGAGEMENT_TIER.values())
    return {
        "n_total": len(CASES),
        "n_graded": len(graded),
        "n_reference_or_labor": len(CASES) - len(graded),
        "ssi_by_id": {k: by_id[k] for k in sorted(by_id)},
        "mean_ssi_graded": round(sum(nums) / len(nums), 4),
        "n_complete_1_0": sum(1 for v in nums if v >= 1.0),
        "complete_ids": sorted([i for i, v in by_id.items() if v >= 1.0]),
        "n_strong_ge_0_8": sum(1 for v in nums if v >= 0.8),
        "feature_frequency": feat_freq,
        "first_invoice_tier_usd": dict(FIRST_INVOICE_TIER),
        "first_invoice_ceiling_usd": FIRST_INVOICE_CEILING_USD,
        "tier1_max_lte_ceiling": tier1_max <= FIRST_INVOICE_CEILING_USD,
        "full_engagement_floor_usd": dict(FULL_ENGAGEMENT_TIER),
        "ladder_gap_tier2_min_over_tier1_max": round(tier2_min / tier1_max, 3),
        "ar_fr_specific_fixed_price_offers_in_sample": (
            AR_FR_SPECIFIC_FIXED_PRICE_OFFERS_IN_SAMPLE
        ),
    }


def input_fingerprint() -> str:
    """بصمةُ المدخلات — أيُّ تغييرٍ في الترميز يكسرها عمدًا."""
    canonical = json.dumps(
        [[c.id, c.kind, c.p, c.s, c.t, c.r, c.f] for c in CASES]
        + [EURUSD, FIRST_INVOICE_CEILING_USD]
        + sorted(FIRST_INVOICE_TIER.items())
        + sorted(FULL_ENGAGEMENT_TIER.items()),
        sort_keys=False,
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def emit_measurements() -> dict:
    """ملفُّ القياس الكامل — يُحفَظ في `docs/research/SSI_MEASUREMENTS.json`."""
    return {
        "instrument": "shared/research/offer_sellability.py",
        "instrument_version": "SSI-v1",
        "as_of": "2026-09-18",
        "evidence_source": "studies/market-first-sales-reality/evidence_mf_round01.csv",
        "eurusd_assumption": EURUSD,
        "model_runs_executed": 0,
        "client_measurements": 0,
        "coder": "single-coder-v1 (inter-rater NOT measured)",
        "sha256_inputs": input_fingerprint(),
        "aggregates": aggregates(),
        "grades": {c.id: {"kind": c.kind, "ssi": ssi(c), "grade": grade(ssi(c))} for c in CASES},
    }


def run_checks() -> int:
    """اختباراتٌ ذاتية حتمية — أيُّ فشلٍ يخرج 1 ويُسمّي السبب."""
    failures: list[str] = []

    def check(name: str, cond: bool, detail: str = "") -> None:
        print(("✅ " if cond else "❌ ") + name + (f" — {detail}" if detail and not cond else ""))
        if not cond:
            failures.append(name)

    # 1) قيمٌ مرجعية ثابتة (تكسر أيَّ انحرافٍ في الترميز أو الحساب)
    by_id = {c.id: c for c in CASES}
    check("S06 SSI=1.0", ssi(by_id["S06"]) == 1.0)
    check("S07 SSI=1.0", ssi(by_id["S07"]) == 1.0)
    check("S19 SSI=1.0", ssi(by_id["S19"]) == 1.0)
    check("S02 SSI=0.8", ssi(by_id["S02"]) == 0.8)
    check("S26 SSI=0.6", ssi(by_id["S26"]) == 0.6)
    check("S10 UNGRADED (reference→None)", ssi(by_id["S10"]) is None)
    check("S16 UNGRADED (labor→None)", ssi(by_id["S16"]) is None)

    # 2) مجاميعٌ ثابتة
    agg = aggregates()
    check("n_total=26", agg["n_total"] == 26, str(agg["n_total"]))
    check("n_graded=19", agg["n_graded"] == 19, str(agg["n_graded"]))
    check("mean=0.5579", agg["mean_ssi_graded"] == 0.5579, str(agg["mean_ssi_graded"]))
    check("complete=3 (S06,S07,S19)", agg["complete_ids"] == ["S06", "S07", "S19"])
    check("strong>=0.8 → 5", agg["n_strong_ge_0_8"] == 5, str(agg["n_strong_ge_0_8"]))
    check("freq P=0.8421", agg["feature_frequency"]["P"] == 0.8421)
    check("freq S=0.8947", agg["feature_frequency"]["S"] == 0.8947)
    check("freq T=0.4211", agg["feature_frequency"]["T"] == 0.4211)
    check("freq R=0.3158", agg["feature_frequency"]["R"] == 0.3158)
    check("freq F=0.3158", agg["feature_frequency"]["F"] == 0.3158)

    # 3) سُلَّم الفاتورة الأولى: الطبقةُ الأولى كلُّها ≤ $5000
    check("tier1 ≤ ceiling", agg["tier1_max_lte_ceiling"] is True)
    check("ladder gap ≥ 2x", agg["ladder_gap_tier2_min_over_tier1_max"] >= 2.0)

    # 4) البياض AR/FR في العيّنة = 0 (حقيقةُ عيّنةٍ لا حقيقةُ سوق)
    check("AR/FR in-sample = 0", agg["ar_fr_specific_fixed_price_offers_in_sample"] == 0)

    # 5) الحتمية: الإصدارُ المزدوج متطابقٌ والبصمةُ ثابتةُ الطول
    a = json.dumps(emit_measurements(), sort_keys=True)
    b = json.dumps(emit_measurements(), sort_keys=True)
    check("deterministic emit", a == b)
    check("fingerprint 64-hex", len(input_fingerprint()) == 64)

    # 6) تدقيقُ عروضنا المرشحة (EXT-01..03 كما هي اليوم قبل التغليف)
    ext01 = audit_offer("EXT-01", "offer", 0, 0, 0, 0, 0)  # قبل التغليف: لا شيء معلن
    check("EXT-01 today SSI=0.0", ext01["ssi"] == 0.0)
    ext01_packed = audit_offer("EXT-01-packed", "offer", 1, 1, 1, 1, 1)
    check("EXT-01 packed SSI=1.0", ext01_packed["ssi"] == 1.0)

    if failures:
        print(f"\n❌ SSI self-check: {len(failures)} فشلًا")
        return 1
    print("\n✅ SSI self-check: كلُّ الفحوصات خضراء (حتمية + قيم مرجعية + سلم + بياض)")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="مؤشر البنية البيعية SSI")
    parser.add_argument("--check", action="store_true", help="اختبارات ذاتية حتمية")
    parser.add_argument("--emit", action="store_true", help="إصدار SSI_MEASUREMENTS.json")
    args = parser.parse_args(argv)
    if args.emit:
        print(json.dumps(emit_measurements(), ensure_ascii=False, indent=2))
        return 0
    return run_checks()


if __name__ == "__main__":
    sys.exit(main())
