"""سكّةُ العملة الصعبة — FXR (FX Rail).

معرفةٌ جديدة (الدفعة السادسة بعد CDKC وVEP وCND وAHW وDLY):
**القيدُ الحاكمُ ليس «هل يمكن استلام دولار»، بل «أيُّ كيانٍ يستلمه، وكم يسمح له
القانون أن يستلم، ومتى يجب أن يُرحِّله».**

الدفعاتُ الخمس السابقة كلّها قاست **محور العرض** (مقاييس، براهين، نوافذ ضمان).
هذه الدفعة تقيس **محور التحصيل** — وهو المحور الذي سجّلت اللوحةُ التجارية أنّ
العائق فيه، لا في القدرة. كلُّ دالةٍ هنا تُخرج رقماً حتمياً من مُدخلاتٍ مُسندةٍ
بتاريخٍ ومصدر، أو تُخرج `None` عندما لا يُسند المُدخل (قاعدة D-212: عدمُ النضج
لا يُقرأ صفراً).

الحقائقُ المُسنَدة التي تُبنى عليها الحسابات (F = منقول بمصدر، مؤرَّخ)
--------------------------------------------------------------------
F1 · **100% من حصيلة تصدير الخدمات تبقى في حساب العملة الصعبة.**
     التعليمة 06-2021 (29 يونيو 2021) م04، ومُثبَتة ببيان بنك الجزائر 18-07-2021
     الذي نصّ صراحةً على «السلع **والخدمات**» و«بما فيها المؤسسات الناشئة الناشطة
     في اقتصاد المعرفة». التقسيم: 80% لاستيراد ما يلزم النشاط، 20% للترويج،
     والاستخدام «حرٌّ» في الدفع الإلكتروني والحوالات.
F2 · **الإعفاء من التوطين المصرفي** لصادرات الخدمات الرقمية، وخدمات المؤسسات
     الناشئة، و**«المهنيين غير التجّار»** — قرار مجلس النقد والقرض 28 مارس 2021
     (APS، 29-03-2021)، وهو الأساس الذي صدر عنه النظام 01-2021.
F3 · **أجل الترحيل 120 يوماً** من تاريخ إنجاز الخدمة، حتى 180 يوماً فقط بتأمين
     ائتمانٍ مُسبق من الهيئة الوطنية المؤهَّلة، وأجلُ الدفع يجب أن يُنصَّ عليه
     **صراحةً في العقد**، والترحيلُ **يوم دفع العميل** — النظام 26-02 (23 يوليو
     2026)، الجريدة الرسمية ن°58 (12 أوت 2026)، يُعدّل م61 من النظام 07-01
     ويُلغي النظام 16-04 (360 يوماً).
F4 · **سقفُ المقاول الذاتي للخدمات 5.000.000 دج/سنة**، IFU بنسبة 0,5% من
     المحصَّل (م282sexies CIDTA، LF2024)، حدٌّ أدنى 10.000 دج/سنة، CASNOS
     اختيارية جزافية 24.000 دج/سنة (م14 من المرسوم 26-257).
F5 · **م126 من الأمر 03-11 + م08 من النظام 07-01**: يُحظَر على المقيم تكوين أيّ
     أصلٍ (عقاري/منقول/ائتماني/**مصرفي**) بالخارج من أموالٍ مصدرها نشاطُه في
     الجزائر، إلا بإذنٍ صريحٍ من بنك الجزائر. والعقوبة بالأمر 96-22 (المعدَّل
     بـ03-01 و10-03): **سجن 2–7 سنوات، غرامة لا تقلّ عن ضعف المبلغ، والمصادرة.**
F6 · **مسار الاستثمار الخارجي المرخَّص** (الاستثناء الوحيد في م126): ارتباطٌ
     بالنشاط، ≥10% من حقوق التصويت، تمويلٌ ذاتي، بلدٌ ذو نظامٍ جبائيٍّ شفّافٍ
     وتبادل معلومات، ترحيلُ الإيرادات وحصيلة التصفية في الآجال، وتقريرٌ سنويٌّ
     مُصدَّق إلى مديرية الصرف.
F7 · **البنوك مُلزَمة بتوطين عمليات تصدير السلع والخدمات خلال 48 ساعة** من
     تسلّم ملفٍّ كامل (تعليمة أواخر يوليو 2026، سندُها م29 من النظام 07-01).
F8 · **21 عوناً من بنك الجزائر** مُخوَّلون بمعاينة مخالفات الصرف — arrêté
     26 يوليو 2026، **الجريدة الرسمية ن°58 نفسها** التي نُشر فيها النظام 26-02.
F9 · أسعار 2026-09: رسمي USD/DZD ≈ 133,02–133,46 · موازٍ (Square Port-Saïd،
     02-09-2026) شراء 236,00 / بيع 238,33 · الفجوة 76,84% · EUR/DZD ≈ 154,81.
F10 · **Interreg NEXT MED 2021-2027**: 253م€، الجزائر مؤهَّلة (14 ولاية)،
     دعمٌ أوروبي 500أ€–2,5م€ للمشروع، تمويلٌ أوروبي حتى 89%، شراكةٌ من 3 كيانات
     في 3 بلدان منها شريكٌ متوسطي واحد على الأقل.
F11 · **مشتري التقييم المؤسّسي موجود ومُموَّل**: UK AISI تعاقد مع Rethink
     Priorities UK (مؤشَّرة PME) بـ**£5.000.000** (إشعار 037042-2025)، ومع Mila
     بـ**£720.000** (016458-2025)؛ وCAISI الأميركي وسّع فحص النماذج طوعاً (2026-05).

حدودٌ معلنة (تُقرأ مع كل رقمٍ يخرج من هنا)
----------------------------------------
1. **ليست رأياً قانونياً.** هذه الحسابات تُخرج «أيُّ الأرقام يخرق أيَّ نصٍّ
   مُسند»، والحسمُ لمحامٍ ولمديرية الصرف.
2. **لا قياسَ عميل.** كلُّ مُدخلٍ إمّا مُسندٌ بتاريخٍ إلى مصدرٍ منشور أو مُشتقٌّ
   حتمياً منه؛ ⛔ لا يُستعمل أيُّ رقمٍ هنا ادّعاءً عن عقدٍ عند عميلٍ بعينه.
3. **النظام 26-02 مُسندٌ بخمسة مصادر ثانوية متطابقة** (TSA · Express DZ ·
   Maghreb Émergent · DNAlgérie · Observalgérie) تذكر النصَّ ورقم الجريدة
   والتاريخ واسم الموقِّع والإلغاء — **ولم يُقرأ بعد نصُّ الجريدة الرسمية نفسه**.
   لذلك تُخرِج الأداة الحكم تحت **كلا** المرجعَين (120 و360) ولا تنسخ 360.
4. **الأسعار لقطةٌ زمنية** (2026-09-02/10)، والسقفُ الدولاري يُعاد حسابه عند كل
   تغييرٍ في السعر — تُرجعه الأداة دالةً في السعر لا ثابتاً.
5. **الحزمة stdlib فقط** ولا استيراد من `app/`: تُشحن إلى مشترٍ لا يملك تبعياتنا.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import asdict, dataclass, field

__all__ = [
    "AE_CEILING_DZD_SERVICES",
    "FX_SNAPSHOT_2026_09",
    "REPATRIATION_CAP_DAYS",
    "REPATRIATION_INSURED_CAP_DAYS",
    "FxSnapshot",
    "ae_ceiling",
    "ceiling_headroom",
    "entity_ladder",
    "fx_retention",
    "measure_all",
    "purchasing_power_multiple",
    "repatriation_compliance",
    "repatriation_feasible_terms",
    "score_rails",
    "spread_penalty",
]

# ---------------------------------------------------------------------------
# المُدخلات المُسنَدة (F) — لا يُعدَّل رقمٌ هنا بلا مرجعٍ مؤرَّخ
# ---------------------------------------------------------------------------

#: F9 — لقطة أسعار سبتمبر 2026. النطاق لا الوسط: القرار يُتَّخذ على الأسوأ.
FX_SNAPSHOT_2026_09: FxSnapshot = None  # type: ignore[assignment]  # يُبنى أدناه

#: F4 — سقفُ المقاول الذاتي للخدمات (دج/سنة).
AE_CEILING_DZD_SERVICES: int = 5_000_000

#: F3 — أجلُ الترحيل العام من تاريخ إنجاز الخدمة.
REPATRIATION_CAP_DAYS: int = 120

#: F3 — الحدُّ الأقصى المطلق بتأمين ائتمانٍ مُسبق.
REPATRIATION_INSURED_CAP_DAYS: int = 180

#: F3 — المرجعُ السابق (النظام 16-04، أُلغي بالنظام 26-02) — يبقى في الحساب
#: لأنّ مستودعنا لم يقرأ بعد نصَّ الجريدة الرسمية (الحدُّ 4 أدناه).
REPATRIATION_LEGACY_CAP_DAYS: int = 360

#: F4 — نسبُ العبء على المقاول الذاتي.
AE_IFU_RATE: float = 0.005
AE_IFU_MIN_DZD: int = 10_000
AE_CASNOS_FORFAIT_DZD: int = 24_000

#: F1 — تقسيمُ استخدام الرصيد بالعملة الصعبة.
FX_SPLIT_IMPORTS: float = 0.80
FX_SPLIT_PROMOTION: float = 0.20


@dataclass(frozen=True)
class FxSnapshot:
    """لقطةُ أسعارٍ مُسندة بتاريخ. الحقلان الرسمي والموازي **شراء** و**بيع**."""

    as_of: str
    official_usd_dzd_low: float
    official_usd_dzd_high: float
    parallel_usd_dzd_buy: float
    parallel_usd_dzd_sell: float
    eur_dzd: float
    source: str

    @property
    def gap_pct(self) -> float:
        """الفجوةُ **الأسوأ**: أعلى سعرٍ رسمي مقابل **بيع** الموازي.

        تُستعمل في التصميم لأنّ القرار يُتَّخذ على أسوأ زوجٍ متاح، لا على الوسط.
        """
        base = self.official_usd_dzd_high
        return (self.parallel_usd_dzd_sell - base) / base * 100.0

    @property
    def gap_pct_published(self) -> float:
        """الفجوةُ كما ينشرها مؤشّر EXDZ: الرسمي مقابل **شراء** الموازي.

        ⚠️ رقمان لشيءٍ واحد، ولا يُكتب أحدهما فوق الآخر (عرف D-282): المنشور
        يُقارَن بالمنشور، والأسوأ يُستعمل للتصميم.
        """
        base = self.official_usd_dzd_high
        return (self.parallel_usd_dzd_buy - base) / base * 100.0


FX_SNAPSHOT_2026_09 = FxSnapshot(
    as_of="2026-09-02/2026-09-10",
    official_usd_dzd_low=133.02,
    official_usd_dzd_high=133.46,
    parallel_usd_dzd_buy=236.00,
    parallel_usd_dzd_sell=238.33,
    eur_dzd=154.81,
    source=(
        "xe.com mid-market 2026-09-10 (133,021) · exchangedz.com official "
        "reference 2026-09-02 (133,4566) وSquare buy 236,00 / sell 238,33 "
        "(EXDZ: فجوة 76,84%)"
    ),
)


# ---------------------------------------------------------------------------
# 1) سقفُ الكيان: كم يسمح القانون لهذا الكيان أن يستلم بالعملة الصعبة؟
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CeilingResult:
    """ترجمةُ السقف القانوني بالدينار إلى عملةٍ صعبة عند سعرٍ مُسند."""

    ceiling_dzd: int
    usd_per_year_at_official_low: float
    usd_per_year_at_official_high: float
    eur_per_year: float
    usd_per_month_worst: float
    reported_as: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def ae_ceiling(
    ceiling_dzd: int = AE_CEILING_DZD_SERVICES,
    snap: FxSnapshot = FX_SNAPSHOT_2026_09,
) -> CeilingResult:
    """كم دولاراً يسمح سقفُ المقاول الذاتي (F4) باستلامه فعلياً؟

    يُؤخَذ **أسوأ** سعرٍ رسمي (الأعلى، لأنه يُنتج أقلّ دولارات) كرقمٍ للتخطيط.
    """
    usd_low = ceiling_dzd / snap.official_usd_dzd_high
    usd_high = ceiling_dzd / snap.official_usd_dzd_low
    eur = ceiling_dzd / snap.eur_dzd
    return CeilingResult(
        ceiling_dzd=ceiling_dzd,
        usd_per_year_at_official_low=round(usd_low, 2),
        usd_per_year_at_official_high=round(usd_high, 2),
        eur_per_year=round(eur, 2),
        usd_per_month_worst=round(usd_low / 12.0, 2),
        reported_as=("🟢⟨ح⟩ حتمي محسوب من سقفٍ قانونيٍّ مُسند (F4) وسعرٍ مُسند (F9) — لا قياسَ عميل"),
    )


def ceiling_headroom(
    target_usd_per_month: float,
    ceiling_dzd: int = AE_CEILING_DZD_SERVICES,
    snap: FxSnapshot = FX_SNAPSHOT_2026_09,
) -> dict[str, object]:
    """هل يحمل هذا الكيانُ الهدفَ التجاري؟ يُرجع المضاعفَ لا حكماً لغوياً."""
    cap = ae_ceiling(ceiling_dzd, snap)
    allowed_month = cap.usd_per_month_worst
    if allowed_month <= 0:
        return {"fits": None, "ratio": None}
    ratio = target_usd_per_month / allowed_month
    return {
        "target_usd_per_month": target_usd_per_month,
        "allowed_usd_per_month_worst": allowed_month,
        "ratio": round(ratio, 3),
        "fits": ratio <= 1.0,
        "verdict": ("ضمن السقف" if ratio <= 1.0 else f"يتجاوز السقف بمضاعف {round(ratio, 2)}×"),
    }


# ---------------------------------------------------------------------------
# 2) سُلَّمُ الكيانات: متى يُجبرك السقفُ على تغيير الكيان؟
# ---------------------------------------------------------------------------


def entity_ladder(
    fx_usd_per_year: float,
    snap: FxSnapshot = FX_SNAPSHOT_2026_09,
    trigger_ratio: float = 0.70,
) -> list[dict[str, object]]:
    """السُّلَّمُ المُصمَّم: المقاول الذاتي أولاً، ثمّ الشركة عند عتبةٍ رقمية.

    العتبةُ 70% من السقف لا 100%: التجاوزُ يُقاس على **المحصَّل** لا على المُفوتَر،
    وموسمُ فوترةٍ واحدٍ يكفي لكسر السقف قبل أن يُلاحَظ.
    """
    cap = ae_ceiling(AE_CEILING_DZD_SERVICES, snap)
    ceiling_usd = cap.usd_per_year_at_official_low
    trigger_usd = ceiling_usd * trigger_ratio
    ca_dzd = fx_usd_per_year * snap.official_usd_dzd_high
    stage1 = fx_usd_per_year <= trigger_usd
    return [
        {
            "stage": 1,
            "entity": "مقاول ذاتي (ANAE) — IFU 0,5% · بلا محلٍّ ولا سجلٍّ تجاري",
            "legal_basis": "F4 + F2 («المهنيون غير التجّار» مُعفَون من التوطين)",
            "applies": stage1,
            "fx_usd_per_year": round(fx_usd_per_year, 2),
            "trigger_usd_per_year": round(trigger_usd, 2),
            "ceiling_usd_per_year": round(ceiling_usd, 2),
            "ca_dzd_at_official_high": round(ca_dzd, 2),
            "breaches_ceiling": ca_dzd > AE_CEILING_DZD_SERVICES,
        },
        {
            "stage": 2,
            "entity": "EURL/SARL + علامة مؤسسة ناشئة — بلا سقف رقم أعمال",
            "legal_basis": "F1 (100% في حساب العملة) + F2 (إعفاء التوطين)",
            "applies": not stage1,
            "reason": (
                f"المحصَّل {round(fx_usd_per_year, 2)}$ تجاوز عتبة الترحيل "
                f"{round(trigger_usd, 2)}$ (70% من سقف المقاول الذاتي)"
            ),
        },
    ]


# ---------------------------------------------------------------------------
# 3) الاحتفاظُ بالعملة: 100% لا 50%
# ---------------------------------------------------------------------------


def fx_retention(gross_fx_usd: float) -> dict[str, object]:
    """F1 — ما يبقى في حساب العملة الصعبة، وكيف يجوز استعماله."""
    imports = gross_fx_usd * FX_SPLIT_IMPORTS
    promotion = gross_fx_usd * FX_SPLIT_PROMOTION
    return {
        "gross_fx_usd": round(gross_fx_usd, 2),
        "retained_in_fx_account_pct": 100.0,
        "earmarked_imports_of_goods_and_services_usd": round(imports, 2),
        "earmarked_export_promotion_usd": round(promotion, 2),
        "free_use_for_electronic_payments_and_transfers": True,
        "cash_withdrawal": "مقيَّد بحدّ «المعقول» — استثناءٌ لا قناة",
        "legal_basis": "التعليمة 06-2021 م04 + بيان بنك الجزائر 18-07-2021 (F1)",
        "reported_as": "🟢⟨ح⟩ حتمي محسوب من نصٍّ مُسند — لا قياسَ عميل",
    }


# ---------------------------------------------------------------------------
# 4) الفجوة: كلفةُ التحويل مقابل الدفع من حساب العملة مباشرة
# ---------------------------------------------------------------------------


def spread_penalty(snap: FxSnapshot = FX_SNAPSHOT_2026_09) -> dict[str, object]:
    """ماذا يضيع لو حُوِّلت الحصيلة إلى دنانير ثم أُعيد شراؤها في السوق الموازي؟

    ليس رأياً في السعر ولا دعوةً للمسار الموازي (⛔ K1) — بل **حجمُ ما يتجنّبه**
    الدفعُ المباشر من حساب العملة الصعبة، أي القيمةُ الاقتصادية للاحتفاظ بالعملة.
    """
    bought_back = snap.official_usd_dzd_high / snap.parallel_usd_dzd_sell
    return {
        "as_of": snap.as_of,
        "official_usd_dzd_used": snap.official_usd_dzd_high,
        "parallel_sell_used": snap.parallel_usd_dzd_sell,
        "gap_pct_worst_case": round(snap.gap_pct, 2),
        "gap_pct_as_published_exdz": round(snap.gap_pct_published, 2),
        "note_ar": (
            "رقمان لفجوةٍ واحدة ولا يُكتب أحدهما فوق الآخر (عرف D-282): مؤشّرُ "
            "EXDZ ينشر 76,84% من السعر 133,4566 مقابل شراء الموازي 236,00؛ وحسابُنا "
            "من السعر المُقرَّب 133,46 يُعطي الرقم المجاور. أمّا **الأسوأ** "
            "(أعلى رسمي مقابل **بيع** الموازي) فهو المُستعمل في التصميم."
        ),
        "usd_recovered_per_usd_after_round_trip": round(bought_back, 4),
        "purchasing_power_lost_pct": round((1.0 - bought_back) * 100.0, 2),
        "reading_ar": (
            "كل دولارٍ يُدفع منه مباشرةً (خوادم/واجهات برمجية/أدوات) يساوي "
            f"{round(1.0 / bought_back, 3)}× من دولارٍ مرّ بالدورة نفسها — "
            "وهذا هو المبرِّر الاقتصادي لـ«قاعدة الكلفة بالعملة الصعبة»."
        ),
    }


def purchasing_power_multiple(snap: FxSnapshot = FX_SNAPSHOT_2026_09) -> float:
    """مضاعفُ القدرة الشرائية للدفع المباشر من حساب العملة (مقلوب `spread_penalty`)."""
    bought_back = snap.official_usd_dzd_high / snap.parallel_usd_dzd_sell
    return round(1.0 / bought_back, 4)


def fx_cost_base_rule(
    fx_revenue_usd: float,
    fx_denominated_cost_usd: float,
    snap: FxSnapshot = FX_SNAPSHOT_2026_09,
) -> dict[str, object]:
    """كم من الإيراد مُحصَّنٌ من الفجوة لأنّ كلفته مُقوَّمة بالعملة نفسها؟

    القاعدةُ التصميمية: ما يُدفع من الـ80% المخصَّصة للاستيراد (F1) لا يمرّ
    بالفجوة إطلاقاً — فيُرفع سقفُ الكلفة بالعملة الصعبة قبل رفع السعر.
    """
    retained = fx_retention(fx_revenue_usd)
    allowed = retained["earmarked_imports_of_goods_and_services_usd"]
    assert isinstance(allowed, float)
    ratio = fx_denominated_cost_usd / fx_revenue_usd if fx_revenue_usd else None
    return {
        "fx_revenue_usd": round(fx_revenue_usd, 2),
        "fx_denominated_cost_usd": round(fx_denominated_cost_usd, 2),
        "fx_cost_share_of_revenue": round(ratio, 4) if ratio is not None else None,
        "allowed_under_80pct_rule_usd": allowed,
        "within_80pct_rule": (fx_denominated_cost_usd <= allowed if ratio is not None else None),
        "shielded_from_spread_usd": round(min(fx_denominated_cost_usd, allowed), 2),
        "purchasing_power_multiple": purchasing_power_multiple(snap),
    }


# ---------------------------------------------------------------------------
# 5) الساعةُ التنظيمية: أيُّ أجلِ دفعٍ ينجو؟
# ---------------------------------------------------------------------------


def repatriation_feasible_terms(
    candidate_days: Sequence[int] = (0, 15, 30, 45, 60, 90, 120, 150, 180, 270, 360),
    safety_margin_days: int = 30,
) -> list[dict[str, object]]:
    """مجموعةُ آجال الدفع التي تنجو تحت النظام 26-02 (F3)، بهامشٍ معلن.

    القاعدةُ ليست «أقصر = أفضل»: الأجلُ صفر (الدفع المُقدَّم) هو الأقوى تجارياً
    والأقلّ تعرّضاً، وما فوق 180 **ممنوع** لا «مكلف».
    """
    out: list[dict[str, object]] = []
    for days in candidate_days:
        margin = REPATRIATION_CAP_DAYS - days
        insured_ok = REPATRIATION_INSURED_CAP_DAYS - days
        if days <= REPATRIATION_CAP_DAYS:
            status = "COMPLIANT"
            requirement = "لا شيء إضافي — يجب أن يُنصَّ على الأجل صراحةً في العقد"
        elif days <= REPATRIATION_INSURED_CAP_DAYS:
            status = "INSURED_ONLY"
            requirement = (
                "تأمينُ ائتمانٍ مُسبق لدى الهيئة الوطنية المؤهَّلة (CAGEX) — شرطُ نفاذٍ لا بندٌ اختياري"
            )
        else:
            status = "PROHIBITED"
            requirement = "⛔ فوق الحدّ الأقصى المطلق (180) — لا يُصاغ في عقد"
        out.append(
            {
                "payment_term_days": days,
                "status": status,
                "margin_days_to_120": margin,
                "margin_days_to_180": insured_ok,
                "survives_with_margin": margin >= safety_margin_days,
                "requirement": requirement,
                "legacy_360_reference": (
                    "كان مسموحاً تحت النظام 16-04 — أُلغي بالنظام 26-02 (F3)"
                    if days > REPATRIATION_CAP_DAYS
                    else "مسموح تحت المرجعَين"
                ),
            }
        )
    return out


def repatriation_compliance(
    service_realized_day: int,
    client_paid_day: int,
    funds_in_algerian_account_day: int,
    payment_term_in_contract_days: int | None,
) -> dict[str, object]:
    """فحصُ حالةٍ واحدة مقابل F3. يُخرج الخرقَ المُسمّى، لا حكماً عاماً.

    الأيّامُ أعدادٌ صحيحة نسبية (يوم 0 = توقيع العقد). ليست تواريخَ تقويمية:
    الغرضُ فحصُ البنية، لا الحساب التقويمي.
    """
    breaches: list[str] = []
    deadline = service_realized_day + REPATRIATION_CAP_DAYS

    if payment_term_in_contract_days is None:
        breaches.append(
            "CONTRACT_TERM_MISSING — م26-02 يُلزم أن يُنصَّ على أجل الدفع صراحةً في العقد التجاري"
        )
    elif payment_term_in_contract_days > REPATRIATION_INSURED_CAP_DAYS:
        breaches.append(f"TERM_OVER_ABSOLUTE_CAP — {payment_term_in_contract_days} يوم > 180")
    elif payment_term_in_contract_days > REPATRIATION_CAP_DAYS:
        breaches.append(
            f"TERM_NEEDS_CREDIT_INSURANCE — {payment_term_in_contract_days} يوم "
            "يتطلب تأمين ائتمانٍ مُسبق"
        )

    if client_paid_day > deadline:
        breaches.append(f"PAID_AFTER_120 — الدفع يوم {client_paid_day} بعد الحدّ {deadline}")

    if funds_in_algerian_account_day > client_paid_day:
        breaches.append(
            "NOT_REPATRIATED_ON_PAYMENT_DAY — م26-02: «الترحيلُ يوم دفع "
            f"العميل»، والحالة تُظهر {funds_in_algerian_account_day - client_paid_day}"
            " يومَ تأخير"
        )

    return {
        "service_realized_day": service_realized_day,
        "client_paid_day": client_paid_day,
        "funds_in_algerian_account_day": funds_in_algerian_account_day,
        "payment_term_in_contract_days": payment_term_in_contract_days,
        "deadline_day": deadline,
        "compliant": not breaches,
        "breaches": breaches,
        "reported_as": ("🟢⟨ح⟩ فحصُ بنيةٍ مقابل نصٍّ مُسند — ⛔ ليس رأياً قانونياً"),
    }


# ---------------------------------------------------------------------------
# 6) مقارنةُ السكك: ترتيبٌ على معايير مُسندة، لا على راحة
# ---------------------------------------------------------------------------


@dataclass
class RailAssessment:
    """تقييمُ سكّة تحصيلٍ واحدة. كلُّ حقلٍ مُسندٌ أو `None` (لا يُخمَّن)."""

    rail_id: str
    name_ar: str
    legally_sourced: bool
    keeps_fx: bool
    tax_burden_pct: float | None
    ceiling_usd_per_year: float | None
    criminal_exposure: str | None
    legal_basis: str
    blocking_step_ar: str
    score: float = field(init=False, default=0.0)

    def to_dict(self) -> dict[str, object]:
        d = asdict(self)
        d["score"] = round(self.score, 3)
        return d


def _rail_score(rail: RailAssessment) -> float:
    """نقطةٌ واحدة لكل معيارٍ مُسند. لا تُخترَع معاييرُ ترجيح بلا مرجع."""
    score = 0.0
    if rail.legally_sourced:
        score += 1.0
    if rail.keeps_fx:
        score += 1.0
    if rail.criminal_exposure is None:
        score += 1.0
    if rail.tax_burden_pct is not None and rail.tax_burden_pct <= 1.0:
        score += 0.5
    if rail.ceiling_usd_per_year is not None and rail.ceiling_usd_per_year >= 100_000:
        score += 0.5
    return score


def score_rails(snap: FxSnapshot = FX_SNAPSHOT_2026_09) -> list[dict[str, object]]:
    """أربعُ سككٍ مرشَّحة، مرتَّبةً على معايير F1–F6.

    ⛔ سكّةُ «شركة أجنبية يملكها مقيم» (LLC/Mercury) مُدرَجة **كمحظورة** لا
    كبديل: م126 من الأمر 03-11 وم08 من النظام 07-01 (F5).
    """
    cap = ae_ceiling(AE_CEILING_DZD_SERVICES, snap)
    rails = [
        RailAssessment(
            rail_id="R1",
            name_ar="مقاول ذاتي (ANAE) + حساب مهني + تصدير خدمة رقمية",
            legally_sourced=True,
            keeps_fx=True,
            tax_burden_pct=0.5,
            ceiling_usd_per_year=cap.usd_per_year_at_official_low,
            criminal_exposure=None,
            legal_basis="F2 («المهنيون غير التجّار» مُعفَون من التوطين) + F4",
            blocking_step_ar=(
                "بطاقة ANAE ثمّ حسابٌ مهني لدى بنكٍ وسيطٍ معتمَد — وقبل أيّ "
                "عقد: إيداعُ تصريح المشروع المصدَّر (⛔ K2)"
            ),
        ),
        RailAssessment(
            rail_id="R2",
            name_ar="EURL/SARL بعلامة مؤسسة ناشئة + حساب عملة تجاري",
            legally_sourced=True,
            keeps_fx=True,
            tax_burden_pct=None,  # غير مُسند هنا: يعتمد على العلامة والتجديد
            ceiling_usd_per_year=None,  # لا سقفَ رقمَ أعمالٍ مُسند
            criminal_exposure=None,
            legal_basis="F1 (التعليمة 06-2021 م04) + F2",
            blocking_step_ar=(
                "السجلُّ التجاري + العلامة + فتحُ حساب العملة — أطول مساراً من R1 لكنّه الوحيد بلا سقف"
            ),
        ),
        RailAssessment(
            rail_id="R3",
            name_ar="اتحادٌ في مشروع Interreg NEXT MED (تمويلٌ أوروبي لا بيع)",
            legally_sourced=True,
            keeps_fx=True,
            tax_burden_pct=None,
            ceiling_usd_per_year=None,
            criminal_exposure=None,
            legal_basis="F10 — الجزائر مؤهَّلة (14 ولاية)، تمويلٌ حتى 89%",
            blocking_step_ar=(
                "كيانٌ قانوني في إحدى الولايات الـ14 + شريكان أجنبيان على الأقل — "
                "العملةُ هنا **منحةٌ مُتعاقَد عليها** لا إيرادَ بيع"
            ),
        ),
        RailAssessment(
            rail_id="R4",
            name_ar="شريكٌ من الباطن في مناقصة AISI/CAISI لتقييم النماذج",
            legally_sourced=True,
            keeps_fx=True,
            tax_burden_pct=None,
            ceiling_usd_per_year=None,
            criminal_exposure=None,
            legal_basis="F11 — £5,0م مُسنَدة لمُتعاقدٍ مؤشَّر PME",
            blocking_step_ar=(
                "علاقةٌ مع مُتعاقدٍ رئيسي (prime) في UK/EU — الأهليةُ المباشرة "
                "لمناقصات GPA غير مُسندة للجزائر، فالمدخلُ **من الباطن**"
            ),
        ),
        RailAssessment(
            rail_id="X1",
            name_ar="⛔ LLC/Mercury باسم مقيم جزائري (الوصفة المتداولة)",
            legally_sourced=False,
            keeps_fx=False,
            tax_burden_pct=0.0,
            ceiling_usd_per_year=None,
            criminal_exposure=(
                "سجن 2–7 سنوات، غرامة ≥ ضعف المبلغ، مصادرة — الأمر 96-22 (المعدَّل بـ03-01 و10-03)"
            ),
            legal_basis=(
                "F5 — م126 من الأمر 03-11 وم08 من النظام 07-01: الحظرُ صريحٌ على "
                "تكوين أصلٍ مصرفي بالخارج من نشاطٍ في الجزائر"
            ),
            blocking_step_ar=(
                "⛔ لا يُفتح هذا المسار. الاستثناءُ الوحيد هو **الاستثمار الخارجي "
                "المرخَّص** (F6) بشروطه الأحد عشر — لا شركةُ DIY"
            ),
        ),
    ]
    for rail in rails:
        rail.score = _rail_score(rail)
    ranked = sorted(rails, key=lambda r: r.score, reverse=True)
    return [r.to_dict() for r in ranked]


# ---------------------------------------------------------------------------
# 7) المُحصِّلة: كلُّ ما سبق في ملفٍّ واحد قابل لإعادة الإنتاج
# ---------------------------------------------------------------------------


def measure_all(snap: FxSnapshot = FX_SNAPSHOT_2026_09) -> dict[str, object]:
    """المُحصِّلةُ الحتمية الكاملة. لا شبكة، لا ساعة، لا عشوائية."""
    cap = ae_ceiling(AE_CEILING_DZD_SERVICES, snap)
    return {
        "artifact": "FXR_MEASUREMENTS",
        "determinism": "حتمي: لا عشوائية ولا شبكة ولا ساعة في الحساب.",
        "legal_disclaimer_ar": (
            "⛔ ليست رأياً قانونياً. الحسابات تُخرج «أيُّ رقمٍ يخرق أيَّ نصٍّ "
            "مُسند»؛ الحسمُ لمحامٍ ولمديرية الصرف ببنك الجزائر."
        ),
        "fx_snapshot": {
            "as_of": snap.as_of,
            "official_usd_dzd": [snap.official_usd_dzd_low, snap.official_usd_dzd_high],
            "parallel_usd_dzd": [snap.parallel_usd_dzd_buy, snap.parallel_usd_dzd_sell],
            "eur_dzd": snap.eur_dzd,
            "gap_pct_worst_case": round(snap.gap_pct, 2),
            "gap_pct_as_published_exdz": round(snap.gap_pct_published, 2),
            "source": snap.source,
            "correction_ar": (
                "⚠️ تصحيحٌ للوحة 2026-09: الأرقام المستعملة هناك (151 رسمي · 280 "
                "موازٍ · 73%) لا تطابق لقطة سبتمبر 2026 (133,02–133,46 · 236,00–"
                "238,33 · 76,84%). الفرقُ يُغيّر سقفَ الكيان الدولاري."
            ),
        },
        "results": {
            "ae_ceiling": cap.to_dict(),
            "target_fit": {
                "board_target_low_3000": ceiling_headroom(3000.0, snap=snap),
                "board_target_high_8000": ceiling_headroom(8000.0, snap=snap),
            },
            "entity_ladder_at_20k_usd": entity_ladder(20_000.0, snap),
            "entity_ladder_at_30k_usd": entity_ladder(30_000.0, snap),
            "entity_ladder_at_50k_usd": entity_ladder(50_000.0, snap),
            "entity_ladder_note_ar": (
                "30 ألف$/سنة — 80% من السقف القانوني فقط — تكسر **عتبةَ الترحيل** "
                "(70% ≈ 26.225$) فتُوجب الانتقال إلى الشركة، دون أن تكسر السقف. "
                "السقفُ وحده مؤشّرٌ مضلِّل."
            ),
            "fx_retention_on_10k_usd": fx_retention(10_000.0),
            "spread_penalty": spread_penalty(snap),
            "fx_cost_base_rule_at_10k_revenue_6k_cost": fx_cost_base_rule(10_000.0, 6_000.0, snap),
            "contract_terms": repatriation_feasible_terms(),
            "repatriation_case_compliant": repatriation_compliance(
                service_realized_day=30,
                client_paid_day=90,
                funds_in_algerian_account_day=90,
                payment_term_in_contract_days=90,
            ),
            "repatriation_case_breaching": repatriation_compliance(
                service_realized_day=30,
                client_paid_day=200,
                funds_in_algerian_account_day=205,
                payment_term_in_contract_days=None,
            ),
            "rails_ranked": score_rails(snap),
            "demand_channels_outside_sales": [
                {
                    "channel_id": "C1",
                    "name_ar": "مناقصات تقييم النماذج (UK AISI / US CAISI)",
                    "verified_awards": [
                        {
                            "notice": "037042-2025",
                            "buyer": "UK AISI (DESNZ & DSIT Group Commercial)",
                            "subject": "AISI Research and Evals Partner — Cyber and Autonomous Capabilities of AI Foundation Models",
                            "awardee": "Rethink Priorities UK",
                            "awardee_is_sme": True,
                            "total_value_gbp": 5_000_000,
                        },
                        {
                            "notice": "016458-2025",
                            "buyer": "UK AISI",
                            "subject": "Delivery of the 2025/2026 International AI Safety Report",
                            "awardee": "Mila Quebec AI Institute",
                            "awardee_is_sme": False,
                            "total_value_gbp": 720_000,
                        },
                    ],
                    "entry_route_ar": (
                        "من الباطن لدى المتعاقد الرئيسي — الأهليةُ المباشرة لمناقصات "
                        "GPA للكيان الجزائري **غير مُسندة**، فلا تُدَّعى"
                    ),
                    "what_it_changes_ar": (
                        "المشتري المؤسّسي المُموَّل **موجودٌ ومُوثَّق**؛ العائقُ "
                        "علاقةٌ مع prime، لا وجودُ سوق."
                    ),
                    "source": "find-tender.service.gov.uk · politico.com 2026-05-05",
                },
                {
                    "channel_id": "C2",
                    "name_ar": "Interreg NEXT MED — منحةٌ أوروبية لا بيع",
                    "programme_envelope_eur": 253_000_000,
                    "algeria_eligible": True,
                    "eligible_wilayas_count": 14,
                    "eu_support_per_project_eur": [500_000, 2_500_000],
                    "max_eu_cofinancing_pct": 89.0,
                    "min_partners": 3,
                    "min_countries": 3,
                    "requires_med_partner_country": True,
                    "what_it_changes_ar": (
                        "يحوّل «ابحث عن مشترٍ» إلى «ادخل اتحاداً» — والعملةُ "
                        "الأوروبية تدخل بقناةٍ مصمَّمة لها، لا ببيعٍ مُقنِع."
                    ),
                    "source": "enicbcmed.eu · aer.eu · oc-cooperation.org",
                },
            ],
        },
        "kill_conditions_ar": [
            "إن لم تُقرأ بعد نصُّ الجريدة الرسمية ن°58 (26-02) ⇒ يبقى الحكم "
            "مُسنَداً بخمسة مصادر ثانوية متطابقة، ولا تُنسخ 360 ولا تُعلَن 120 "
            "كمرجعٍ وحيد.",
            "إن رفض بنكٌ وسيطٌ معتمَد فتحَ حسابٍ مهني لحامل بطاقة ANAE ⇒ "
            "R1 ساقطة، ويُعاد الترتيب إلى R2 مباشرةً.",
            "إن تبيّن أنّ إعفاء التوطين (F2) يُسقط أيضاً واجب الترحيل (F3) ⇒ "
            "كلُّ حسابات `repatriation_*` هنا باطلةُ الاستعمال وتُعاد من الصفر.",
            "إن تجاوز المحصَّل عتبة 70% من السقف دون انتقالٍ إلى R2 ⇒ الكيانُ "
            "نفسه صار الخطرَ، لا السوق.",
        ],
    }


# ⛔ لا كتلة `__main__` هنا: `shared/` كودُ مكتبة، والـguardrail يمنع `print()` فيه.
# القناةُ المعتمدة لتوليد `FXR_MEASUREMENTS.json` هي
# `scripts/research/measure_fx_rail.py` (وبوّابة انحرافه `--check`).
