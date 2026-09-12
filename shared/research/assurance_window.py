"""نافذةُ صلاحية الضمان — AHW (Assurance-Horizon Warranty Window).

معرفةٌ جديدة (الدفعة الرابعة بعد CDKC وVEP وCND): **الاطمئنانُ أصلٌ متقادم، لا شهادةٌ دائمة.**

الفجوة التي تعالجها (مصادرها المؤرَّخة في
`docs/research/FRONTIER_CLAIM_LEDGER_2026-09.md`)
------------------------------------------------------------------
ثلاثُ حقائق منشورة في 2026 تجعل «تقرير جاهزية» يسوّق كما لو كان ثابتاً وهي ليست كذلك:

1. **الأفق يضاعف الخطر فوق خطّياً**: تقارير METR (2026-05-19) تُظهر أنّ معدّل الغشّ
   يربو على نصف نقطة مئوية على مهامٍ ≤30 دقيقة، ويرتفع إلى **أكثر من واحدة من كل ست**
   على مهامٍ >8 ساعات. فمقياسُ النجاح وحده لا يكفي: لا بدّ من **شريط أفق** معلن.
2. **الرقم المنشور يتحرّك مع التكوين**: بين 2026-06-09 و2026-09-01 (84 يوماً) قفزت
   Terminal-Bench-Science من 24.7 إلى 52.6 على خطٍّ واحد (+27.9 نقطة)، **وانخفضت** مهمةٌ
   قانونيةٌ مستقلة من 11.25 إلى 6.67 (−4.58). فالتقادم لا يجري باتجاهٍ واحد.
3. **ميزانيةُ المهاجم جزءٌ من الرقم**: MonitoringBench (2026-05) يقيس أنّ معدّل التقاط
   94.9% «مُستدعىً من النموذج» يهبط إلى 60.3% على أفضل الهجمات المُصقولة، بـ4,783 محاولة
   تصعيد. فـ«نسبة التقاط» بلا ميزانية مهاجم **رقمٌ غير قابل للتفنيد**، وهو ممنوعٌ هنا.

المساهمة المركزية (أربع قطع، كلّ واحدة قابلة للدحض)
--------------------------------------------------
1. **أُسّ الأفق (HRE)**: `ε = ln(r_hi/r_lo) ÷ ln(h_hi/h_lo)` — تعريضُ المشتري لمخاطره
   كدالةٍ في طول المهمة، بمرونةٍ محسوبةٍ من نقطتين منشورتين، مع **نطاق حساسية** لا رقمٍ
   واحد. والنتيجة التصميمية: أيّ عرضٍ يجب أن يُسمّي الشريط (`horizon_band`)، وإلا فالحكم
   غير قابل للتكذيب.
2. **منحنى الاطمئنان/الميزانية (ABAC)**: `A(B) = A₀ − κ·log₁₀(1 + B/B₀)` مع عائلةٍ
   معلنةٍ لـ`B₀` (نقطتان لا تحدّدان المنحنى)، ومؤشّرَين قابلَين للبيع:
   **محاولاتٌ لكل نقطة اطمئنان** (سعرُ العمل)، و**عتبةُ التشبّع**. والقاعدة التجارية:
   ما يُباع هو **(A, B) معاً**، لا A وحدها.
3. **نافذةُ الضمان (AWW)**: حدّان مستقلّان يُؤخذ **أصغرهما**:
   - **سرعةُ التقادم**: `W_τ = τ ÷ v` حيث `v = |Δنقطة| ÷ أيام` مقيسةً على Suite بعينه.
   - **مخاطرُ متزاحمة**: `W(θ) = ln(1/θ) ÷ (λ_إصدار + λ_حزمة + λ_خصم)` — احتماءُ
     بقاء الرقم المقتبس داخل سَعة θ بلا إحلال تكويني.
   ومنهما **مؤشّرُ الفوترة**: `P(تسبقَ إصدارَةٌ الدورةَ التقويمية) = 1 − exp(−T/c)` —
   وهو ما يقلب بنية العرض من «تقريرٌ ربع سنوي» إلى **بوّابةُ انحدارٍ مُفعَّلةٌ بالإصدار**.
4. **دبوسُ التقرير وصلاحيّته (ReportPin)**: الحقول الستّة اللازمة لجعل الرقم قابلاً
   للتدقيق (نموذج · مِصْمَل · تكوين حواجز · إصدار الحزمة · ميزانية المهاجم · تاريخ)،
   وقرارٌ آليّ `FRESH / THROTTLED / STALE / UNPINNED` — لا خانة «صحيح للأبد» في أيّ مخرج.

حدودٌ معلنة (تُقرأ مع كل رقمٍ يخرج من هنا — ولا يُقتطع رقمٌ منها)
----------------------------------------------------------------
1. **لا قياسَ عميلٍ ولا تشغيلَ نموذج**: كلُّ مُدخَلٍ هنا إمّا مُسندٌ بتاريخٍ إلى مصدرٍ
   منشور، أو مشتقٌّ حتمياً منه. ⛔ لا يُستعمل أيّ رقمٍ ادّعاءً عن منتجٍ عند عميلٍ بعينه.
2. **نقطتان لا تُنشئان نموذجاً عالمياً**: HRE وABAC عائلةُ دوالٍ لا منحنًى واحداً؛
   لذلك يُرجَع عن كلٍّ منهما **جدولُ حساسية**، وأيُّ extrapolation خارج نقاط الإسناد
   يُرجَع `None` لا رقماً (قاعدة D-212: عدمُ النضج لا يُقرأ صفراً).
3. **سرعةُ التقادم خاصةٌ بالحزمة**: v مقيسةٌ على Suite محدّد بين إصدارَين محدّدَين؛
   نقلُها إلى حزمةٍ أخرى ممنوع — تُحسب v لكل حزمة أو تُعلَّم `unmeasured`.
4. **الأجلُ التنظيميُّ ليس رأياً قانونياً**: أدواتُ الترحيل هنا تُخرج **مجموعةَ آجالٍ
   تنجو تحت كل مرجحٍ مُسند**، ولا تحسم أيَّ نصٍّ تنظيمي؛ الحسمُ لوثيقةٍ رسمية.
5. **قيدُ التحكيم محورٌ مستقلٌّ عن القِدَم**: `adjudicate` و`acceptance_corridor` لا
   يُخرجان حكماً في الرياضيات ولا رأياً قانونياً؛ يُخرجان فقط «هل يُقتبسُ هذا اليومَ» و
   «متى يبدأُ العدُّ الرسميُّ بعد النشر» — وكلُّ حالةٍ في مجموعةٍ مغلقة.
6. **الحزمة stdlib فقط** ولا استيراد من `app/`: تُشحن إلى عميلٍ لا يملك تبعياتنا.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import date

# ── ثوابتُ العقد الحتمي ────────────────────────────────────────────────────────

#: أدنى فارقٍ نقطتي يُعتَدّ معه بتحرّك حزمةٍ (نقاط معيارية على مقياس النسبة المئوية).
MIN_TOLERANCE_POINTS = 0.5

#: أقصى عمرٍ لتقريرٍ يُقتبس بلا تحفّظ (أيام) — قيمةُ تصميمٍ معلنة، لا قياس.
FRESH_DAYS = 14.0

#: أدنى عددٍ من أزواج الإصدارَين اللازمة لتعريف سرعة تقادم موثوقة (حارسُ نضج).
MIN_DRIFT_PAIRS = 2

#: أقصى عمرٍ مقبول لتقريرٍ قبل أن يُلزَم بإعادة قياس (أيام) — قيمة تصميمية معلنة.
MAX_REPORT_AGE_DAYS = 90


class AssuranceWindowError(ValueError):
    """خطأُ إدخالٍ في نافذة الضمان — يُرفَع لا يُصفَّر، كي لا يُقرأ الغيابُ رقماً."""


# ── 1) HRE — أُسّ الأفق (Horizon Risk Exponent) ────────────────────────────────


@dataclass(frozen=True)
class HorizonAnchor:
    """نقطةُ إسناد: طولُ المهمة بالدقائق ومعدّلُ السلوك المعرِّض المصحوب بها."""

    minutes: float
    rate: float
    label: str = ""

    def __post_init__(self) -> None:
        if self.minutes <= 0:
            raise AssuranceWindowError(f"طولُ المهمة يجب أن يكون > 0، لا {self.minutes}")
        if not 0 < self.rate < 1:
            raise AssuranceWindowError(
                f"المعدّل يجب أن يكون في (0,1) ليكون نسبةً لا تكراراً، لا {self.rate}"
            )


def horizon_risk_exponent(low: HorizonAnchor, high: HorizonAnchor) -> float:
    """المرونة `ε = ln(r_hi/r_lo) ÷ ln(h_hi/h_lo)` بين نقطتَي إسناد.

    ε > 1 يعني أنّ التعرّض ينمو **فوق خطّي** مع الأفق؛ ε = 1 نموٌّ خطّي؛ ε < 1 دون
    الخطّي. تُقبل النقطتان بأيّ ترتيبٍ داخلي: يُشتقّ «الأفق الأطول» آلياً، فيُرفَض
    أيُّ إدخالٍ يقلب الاتجاه بصمت.
    """
    if low.minutes == high.minutes:
        raise AssuranceWindowError("نقطتَا الإسناد لهما الأفقُ نفسه — المرونة غير معرَّفة")
    h_lo, r_lo, h_hi, r_hi = _ordered_anchors(low, high)
    if h_hi <= h_lo or r_hi <= r_lo:
        raise AssuranceWindowError(
            "نقطتَا الإسناد لا تُنتجان مرونةً موجّهة (الأفق والمعدّل يجب أن يتزايدا معاً)"
        )
    return math.log(r_hi / r_lo) / math.log(h_hi / h_lo)


def _ordered_anchors(a: HorizonAnchor, b: HorizonAnchor) -> tuple[float, float, float, float]:
    """يرتب النقطتين تصاعدياً بالأفق ويُرجع (h_lo, r_lo, h_hi, r_hi)."""
    lo, hi = (a, b) if a.minutes < b.minutes else (b, a)
    return lo.minutes, lo.rate, hi.minutes, hi.rate


def horizon_exposure_multiplier(eps: float, ratio: float) -> float:
    """معاملُ التعرّض عند تكبير الأفق بضعف `ratio`: `ratio^eps` (أسٌّ فوق الخطّي)."""
    if ratio <= 0:
        raise AssuranceWindowError("نسبةُ تكبير الأفق يجب أن تكون > 0")
    return math.pow(ratio, eps)


def horizon_sensitivity(
    low: HorizonAnchor,
    high: HorizonAnchor,
    ratio: float,
) -> tuple[float, float]:
    """`(ε, معاملُ التعرّض عند ratio)` من نقطتَي الإسناد — لا «مرونةٌ عالمية».

    المصدرُ يقول «أكثر من واحدة من كل ست» لا «بالضبط»، فالحساسيةُ تُعلَن في الوثيقة
    بوصفها نطاقَ قراءةٍ للنقطتين؛ ⛔ لا يُخرج هذا الرقمَ تنبّؤاً خارج [30 دقيقة، 8 ساعات].
    """
    eps = horizon_risk_exponent(low, high)
    mult = horizon_exposure_multiplier(eps, ratio)
    return eps, mult


def horizon_band_flags(eps: float, ratios: tuple[float, ...]) -> dict[str, float]:
    """جدولُ تعرّض معلَن الأشرطة: `1×, 2×, 4×, 8×, 16×` من أفق الأساس."""
    return {f"x{ratio:g}": round(horizon_exposure_multiplier(eps, ratio), 4) for ratio in ratios}


def require_horizon_band(band: str | None) -> None:
    """يجب أن يسمّي أيُّ عرضٍ أو تقريرٍ شريطَ الأفق، وإلا كان الحكم غير قابل للتفنيد."""
    if not band or not band.strip():
        raise AssuranceWindowError(
            "لا شريطَ أفقٍ مُعلَن — الحكمُ بلا أفق غيرُ قابل للتفنيد (⛔ يُسمّى horizon_band)"
        )


# ── 2) ABAC — منحنى الاطمئنان مقابل ميزانية المهاجم ────────────────────────────


@dataclass(frozen=True)
class AssurancePoint:
    """ملاحظةٌ منشورة: (ميزانيةُ تصعيد B، اطمئنانٌ مقيس A ∈ (0,1])."""

    budget: int
    assurance: float
    label: str = ""

    def __post_init__(self) -> None:
        if self.budget < 0:
            raise AssuranceWindowError(f"ميزانيةُ المهاجم لا تكون سالبة: {self.budget}")
        if not 0 < self.assurance <= 1:
            raise AssuranceWindowError(f"الاطمئنانُ نسبةٌ في (0,1]: لا {self.assurance}")


@dataclass(frozen=True)
class AssuranceCurve:
    """منحنًى من الشكل `A(B) = A₀ − κ·log₁₀(1 + B/B₀)` مع `B₀` **مُعلَناً لا مَقِيساً**."""

    a0: float
    kappa: float
    b0: float
    ceiling_budget: int

    def assurance_at(self, budget: int) -> float | None:
        """`A(B)`؛ و`None` خارج نطاق الإسناد (⛔ لا extrapolation صامت)."""
        if budget < 0 or budget > self.ceiling_budget:
            return None
        return max(0.0, self.a0 - self.kappa * math.log10(1.0 + budget / self.b0))

    def marginal_per_doubling(self, budget: int) -> float | None:
        """هبوطُ الاطمئنان عند **مضاعفة** الميزانية (كسراً، موجبٌ = تدهور).

        عند `budget = 0` تُقاس المضاعفةُ من وحدةِ المقياس `B₀`: مضاعفةُ الصفر لا تُعرِّف
        أثراً. وإذا خرجت المضاعفةُ عن سقفِ الإسناد تُرجَع `None` — ⛔ لا يُقلَّبُ غيابُ
        البيانات إلى «لا تدهور» بصمةٍ على الرقم.
        """
        base = max(budget, int(self.b0), 1)
        lo = self.assurance_at(base)
        hi = self.assurance_at(base * 2)
        if lo is None or hi is None:
            return None
        return lo - hi

    def points_per_doubling_asymptote(self) -> float:
        """`κ·log₁₀2` بالنقاط — في الشكلِ اللوغاريتمي هذا **ثابت**: لا تشبّعَ يُشترى."""
        return self.kappa * math.log10(2.0) * 100.0

    def budget_for_target(self, target: float) -> int | None:
        """الميزانية التي عندها يهبط الاطمئنانُ إلى `target` (ولا تُextrapolated).

        `None` إذا كان الهدفُ فوق رقمِ الأساس أو أعلى من الميزانية المُسندة:
        لا نَعِدُ بما ليس له نقطةُ إسناد.
        """
        if target >= self.a0:
            return None
        if target <= 0.0:
            return None
        exponent = (self.a0 - target) / self.kappa
        budget = self.b0 * (math.pow(10.0, exponent) - 1.0)
        if budget > self.ceiling_budget:
            return None
        return math.ceil(budget)

    def attempts_per_point(self) -> float:
        """محاولاتُ التصعيد لكل نقطة اطمئنان فُقدت بين نقطتَي الإسناد — سعرُ العمل."""
        if self.kappa <= 0 or self.ceiling_budget <= 0:
            return float("inf")
        lost = self.kappa * math.log10(1.0 + self.ceiling_budget / self.b0)
        if lost <= 0:
            return float("inf")
        return self.ceiling_budget / (lost * 100.0)


def fit_assurance_curve(
    base: AssurancePoint,
    refined: AssurancePoint,
    b0: float = 1.0,
) -> AssuranceCurve:
    """يُعاير `κ` من نقطتين ويُعلّم `B₀` مُدخلاً تصميميّاً (النقطتان لا تحدّدانه)."""
    if refined.budget <= base.budget:
        raise AssuranceWindowError("ميزانيةُ النقطة الثانية يجب أن تكون أكبر من الأولى")
    if refined.assurance >= base.assurance:
        raise AssuranceWindowError("لا يُعاَر منحنًى متناقصٌ على نقطتين غيرِ متناقصتين — راجع الأرقام")
    if b0 <= 0:
        raise AssuranceWindowError(f"B₀ مقياسُ الميزانية يجب أن يكون > 0، لا {b0}")
    drop = base.assurance - refined.assurance
    kappa = drop / math.log10(1.0 + refined.budget / b0)
    return AssuranceCurve(
        a0=base.assurance,
        kappa=kappa,
        b0=b0,
        ceiling_budget=refined.budget,
    )


def curve_family(
    base: AssurancePoint,
    refined: AssurancePoint,
    scales: tuple[float, ...] = (1.0, 10.0, 100.0, 1000.0),
) -> list[dict[str, float | None]]:
    """عائلةُ المنحنيات المعلنة: `B₀` يتغيّر، والأثرُ عند الميزانية المقيسة ثابت.

    ⛔ لا يُستدار حول `None` بـ`or 0.0`: المنحنى الذي لا يُنتج أثراً عند ميزانيةٍ ما
    يقول ذلك صراحةً في صفّه، لأنّ «صِفرَ أثر» ادّعاءٌ و«لا يُحسب» أمانة.
    """
    rows: list[dict[str, float | None]] = []
    for scale in scales:
        curve = fit_assurance_curve(base, refined, b0=scale)
        marginal = curve.marginal_per_doubling(0)
        rows.append(
            {
                "b0": scale,
                "kappa_points_per_log10": round(curve.kappa * 100.0, 4),
                "first_doubling_points": None if marginal is None else round(marginal * 100.0, 4),
                "attempts_per_point": round(curve.attempts_per_point(), 2),
                "points_per_doubling_asymptote": round(curve.points_per_doubling_asymptote(), 4),
                "budget_for_minus_10pts": curve.budget_for_target(curve.a0 - 0.10),
                "budget_for_minus_20pts": curve.budget_for_target(curve.a0 - 0.20),
            }
        )
    return rows


def budget_is_stated(record: dict[str, object]) -> bool:
    """يفحص أنّ سجلَّ اطمئنانٍ ما يسمّي ميزانيةَ المهاجم (وإلا فرقمُه غيرُ قابلٍ للتفنيد)."""
    for key in ("adversary_budget", "budget", "refinement_attempts"):
        value = record.get(key)
        if isinstance(value, int) and value >= 0:
            return True
    return False


# ── 3) AWW — نافذةُ الضمان (تقادمٌ بسرعة + مخاطرُ متزاحمة) ──────────────────────


@dataclass(frozen=True)
class SuiteDrift:
    """تحرّكُ حزمةٍ معيارية بين إصدارَين على خطٍّ واحد — وحدةُ قياس السرعة."""

    suite: str
    before: float
    after: float
    days: int

    def __post_init__(self) -> None:
        if self.days <= 0:
            raise AssuranceWindowError(f"فاصلُ الإصدارين يجب أن يكون > 0 يوم، لا {self.days}")
        for label, value in (("before", self.before), ("after", self.after)):
            if not 0.0 <= value <= 100.0:
                raise AssuranceWindowError(f"درجةُ الحزمة خارج [0,100] ({label}={value})")
        if not self.suite.strip():
            raise AssuranceWindowError("بلا اسم حزمة — السرعة لا تُنسب")

    @property
    def points(self) -> float:
        return self.after - self.before

    @property
    def direction(self) -> str:
        if self.points > 0:
            return "up"
        if self.points < 0:
            return "down"
        return "flat"


def drift_velocity(drift: SuiteDrift) -> float:
    """نقاطٌ في اليوم (قيمةٌ مُطلقة — الاتجاهُ يُقرأ من `drift.direction`)."""
    return abs(drift.points) / float(drift.days)


def warranty_days(velocity_points_per_day: float, tolerance_points: float) -> float | None:
    """`W_τ = τ ÷ v` — عددُ الأيام التي يبقى فيها الرقم داخل سعة τ.

    `None` عند `v = 0`: حزمةٌ لا تتحرّك لا تُعطي نافذةً صغيرة، بل تُعطي «لا نعرف» —
    فلا يُقلَب الصفرُ مهلةً لا نهائية بصمتٍ ولا نافذةً قصيرة بصمتٍ آخر.
    """
    if tolerance_points < MIN_TOLERANCE_POINTS:
        raise AssuranceWindowError(
            f"سعةُ الحكم دون {MIN_TOLERANCE_POINTS} نقطة بلا معنى: {tolerance_points}"
        )
    if velocity_points_per_day <= 0:
        return None
    return tolerance_points / velocity_points_per_day


def warranty_table(
    drifts: tuple[SuiteDrift, ...],
    tolerances: tuple[float, ...] = (2.0, 5.0, 10.0),
) -> list[dict[str, float | str | None]]:
    """جدولُ نوافذ لكل حزمة: `v` و`W_τ` عند كل سعة، مع الاتجاه منشوراً."""
    rows: list[dict[str, float | str | None]] = []
    for drift in drifts:
        v = drift_velocity(drift)
        row: dict[str, float | str | None] = {
            "suite": drift.suite,
            "points": round(drift.points, 4),
            "days": float(drift.days),
            "direction": drift.direction,
            "velocity_points_per_day": round(v, 6),
        }
        for tol in tolerances:
            window = warranty_days(v, tol)
            row[f"warranty_days_at_{tol:g}pts"] = None if window is None else round(window, 2)
        rows.append(row)
    return rows


def drift_sample_note(drifts: tuple[SuiteDrift, ...]) -> dict[str, object]:
    """يُعلن نضجَ عيّنة السرعة واتّجاهاتها — قبل أن يُبنى على «التقادم» أيُّ سعر.

    الحدُّ الحرفي: عيّنةٌ دون `MIN_DRIFT_PAIRS` حُزمٍ **لا تُنتج** قاعدةَ تقادم؛
    وأيُّ سردٍ يقول «الأرقام تتحسّن» يُدحض بعدِّ الاتجاه الهابط هنا، لا بالرأي.
    """
    down = [d.suite for d in drifts if d.direction == "down"]
    flat = [d.suite for d in drifts if d.direction == "flat"]
    return {
        "suites": len(drifts),
        "downward_suites": down,
        "flat_suites": flat,
        "sample_adequate": len(drifts) >= MIN_DRIFT_PAIRS,
        "max_velocity_points_per_day": (
            round(max((drift_velocity(d) for d in drifts), default=0.0), 6)
        ),
    }


@dataclass(frozen=True)
class ChurnRates:
    """معدّلاتُ الإحلال (لكل يوم) في نموذج المخاطر المتزاحمة."""

    release_per_day: float = 0.0
    suite_change_per_day: float = 0.0
    adversary_growth_per_day: float = 0.0

    def total(self) -> float:
        return self.release_per_day + self.suite_change_per_day + self.adversary_growth_per_day

    @classmethod
    def from_cadences(
        cls,
        release_cadence_days: float | None = None,
        suite_life_days: float | None = None,
        adversary_doubling_days: float | None = None,
    ) -> ChurnRates:
        """يحوّل **دورياتٍ معلنة** إلى معدلات؛ المعدّلُ المجهول يبقى صفراً مسمّى، لا تخميناً."""
        rates: dict[str, float] = {}
        if release_cadence_days is not None:
            if release_cadence_days <= 0:
                raise AssuranceWindowError("دوريةُ الإصدار يجب أن تكون > 0 يوم")
            rates["release_per_day"] = 1.0 / release_cadence_days
        if suite_life_days is not None:
            if suite_life_days <= 0:
                raise AssuranceWindowError("عمرُ الحزمة يجب أن يكون > 0 يوم")
            rates["suite_change_per_day"] = 1.0 / suite_life_days
        if adversary_doubling_days is not None:
            if adversary_doubling_days <= 0:
                raise AssuranceWindowError("مضاعفةُ ميزانية الخصم يجب أن تكون > 0 يوم")
            rates["adversary_growth_per_day"] = math.log(2.0) / adversary_doubling_days
        return cls(**rates)


def survival_probability(churn: ChurnRates, days: float) -> float:
    """`P(يبقى الرقمُ المقتبسُ صالحاً بعد t) = exp(−λt)` — نموذجُ مخاطر متزاحمة."""
    if days < 0:
        raise AssuranceWindowError("الزمنُ لا يكون سالباً")
    return math.exp(-churn.total() * days)


def warranty_window_days(churn: ChurnRates, theta: float = 0.9) -> float | None:
    """أكبرُ `t` لاحتماء بقاء `≥ θ`؛ و`None` إذا لم تكن أيُّ إحلالٍ معلَناً (`λ = 0`).

    ⛔ الصفرُ لا يُقلَب «نافذةً لا نهائية»: الجوابُ الصادق هو «لا يوجد مُدخَلٌ يُحدّد
    النافذة»، فيُعلَّم `unmodeled` ويُرجَع `None`.
    """
    if not 0 < theta < 1:
        raise AssuranceWindowError(f"θ يجب أن تكون في (0,1)، لا {theta}")
    lam = churn.total()
    if lam <= 0:
        return None
    return math.log(1.0 / theta) / lam


def robust_warranty_days(
    drift: SuiteDrift,
    tolerance_points: float,
    churn: ChurnRates,
    theta: float = 0.9,
) -> float | None:
    """حدُّ التصميم = **أصغرُ** الحدين (سرعةُ تقادم + مخاطرُ متزاحمة)."""
    v_limit = warranty_days(drift_velocity(drift), tolerance_points)
    risk_limit = warranty_window_days(churn, theta)
    options = [value for value in (v_limit, risk_limit) if value is not None]
    if not options:
        return None
    return min(options)


def release_beat_probability(cycle_days: float, release_cadence_days: float) -> float:
    """`1 − exp(−T/c)` — احتمالُ أن يحلَّ إصدارٌ **قبل** موعد الدورة التقويمية التالية."""
    if cycle_days <= 0 or release_cadence_days <= 0:
        raise AssuranceWindowError("الدورةُ والدوريةُ كلتاهما > 0 يوم")
    return 1.0 - math.exp(-cycle_days / release_cadence_days)


def detection_lag_days(cycle_days: float) -> float:
    """متوسطُ زمن الكشف لدورةٍ تقويمية منتظمة: نصفُ الدورة (توزيعٌ منتظم للإصدار)."""
    if cycle_days <= 0:
        raise AssuranceWindowError("الدورة يجب أن تكون > 0 يوم")
    return cycle_days / 2.0


def drift_before_detection(drift: SuiteDrift, cycle_days: float) -> float:
    """النقاطُ التي تتحرّك قبل أن يراها التقرير القادم = `v × زمنُ الكشف`."""
    return drift_velocity(drift) * detection_lag_days(cycle_days)


def events_per_year(cadence_days: float, extra_events_per_year: float = 0.0) -> float:
    """عددُ **أحداثِ إعادةِ القياس** في السنة — وحدةُ الفوترة المقترحة بدل السنة الثابتة."""
    if cadence_days <= 0:
        raise AssuranceWindowError("الدورية يجب أن تكون > 0 يوم")
    return 365.0 / cadence_days + extra_events_per_year


# ── 4) دبوسُ التقرير: ما يجعل الرقمَ قابلاً للتدقيق ─────────────────────────────


#: الحقول الستّة التي بلا أحدها يكونُ الرقمُ معلقاً (لا يُنقذها نصٌّ مجاور).
PIN_FIELDS: tuple[str, ...] = (
    "model_id",
    "harness",
    "safeguard_config",
    "suite_version",
    "adversary_budget",
    "issued_on",
)


@dataclass(frozen=True)
class ReportPin:
    """دبوسُ تقريرٍ واحد: التكوينُ الكامل الذي ينطبق عليه الرقم، لا الرقمُ وحده."""

    model_id: str
    harness: str
    safeguard_config: str
    suite_version: str
    adversary_budget: int | None
    issued_on: date
    suite: str = ""
    score_points: float | None = None
    notes: tuple[str, ...] = field(default_factory=tuple)

    def missing_fields(self) -> tuple[str, ...]:
        """الحقولُ الغائبة أو غيرُ المنطوقة — قائمةٌ صريحة، لا حكمٌ ضمني."""
        missing: list[str] = []
        for name in ("model_id", "harness", "safeguard_config", "suite_version"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                missing.append(name)
        if self.adversary_budget is None or self.adversary_budget < 0:
            missing.append("adversary_budget")
        if self.issued_on > date.today():
            raise AssuranceWindowError("تاريخُ التقرير في المستقبل — لا يُقبل كدليل")
        return tuple(missing)


@dataclass(frozen=True)
class PinStatus:
    """قرارُ الصلاحية: حالةٌ من مجموعة مغلقة + الأرقام التي أنتجتها."""

    state: str  # FRESH | THROTTLED | STALE | UNPINNED
    age_days: float
    window_days: float | None
    missing: tuple[str, ...] = ()

    @property
    def quotable(self) -> bool:
        return self.state in {"FRESH", "THROTTLED"}

    @property
    def label(self) -> str:
        return {
            "FRESH": "صالحٌ للاقتباس",
            "THROTTLED": "مقيَّدٌ بحذر",
            "STALE": "منتهيُ الصلاحية",
            "UNPINNED": "غيرُ مُدبَّس",
        }[self.state]


def evaluate_pin(
    pin: ReportPin,
    as_of: date,
    drift: SuiteDrift | None = None,
    tolerance_points: float = 5.0,
    churn: ChurnRates | None = None,
    theta: float = 0.9,
) -> PinStatus:
    """يُحوّل الدبوسَ + سرعةَ التقادم إلى حالةٍ تُستعمل في CI وفي نصّ العرض معاً.

    ثلاثُ دوالَ صغيرةٌ لا سُلَّمُ شروطٍ واحد: `window_of` (من أيِّ مُدخلٍ تُحسب النافذة)،
    `pin_state` (كيف يُصنَّفُ العمر)، وهنا التركيبُ فقط — لأنّ السُلَّمَ الطويلَ هو ما
    يجعلُ القاعدةَ غيرَ قابلةٍ للاختبارِ حالةً حالة.
    """
    missing = pin.missing_fields()
    age = float((as_of - pin.issued_on).days)
    if age < 0:
        raise AssuranceWindowError("تاريخُ المراجعة أسبقُ من تاريخ الإصدار")
    window = window_of(drift, tolerance_points, churn, theta)
    state = "UNPINNED" if missing else pin_state(age, window)
    return PinStatus(state, age, None if window is None else round(window, 2), missing)


def window_of(
    drift: SuiteDrift | None,
    tolerance_points: float,
    churn: ChurnRates | None,
    theta: float,
) -> float | None:
    """النافذةُ من أسرعِ مُدخلٍ ناضج: سرعةُ تقادمٍ إن وُجدت، وإلا مخاطرُ التزاحم وحدها."""
    if drift is not None:
        return robust_warranty_days(drift, tolerance_points, churn or ChurnRates(), theta)
    if churn is not None:
        return warranty_window_days(churn, theta)
    return None


def pin_state(age_days: float, window_days: float | None) -> str:
    """تصنيفُ القِدَمِ **لا يُزيَّف**: بلا نافذةٍ يُستعمل سقفُ الوثيقة؛ وبها يُقارَنُ بها."""
    if window_days is None:
        if age_days > MAX_REPORT_AGE_DAYS:
            return "STALE"
        return "THROTTLED" if age_days > FRESH_DAYS else "FRESH"
    if age_days > window_days:
        return "STALE"
    if age_days > FRESH_DAYS or age_days > 0.75 * window_days:
        return "THROTTLED"
    return "FRESH"


# ── 5) الأجلُ التنظيميُّ كقيدِ تصميم عقد (لا كرأيٍ قانوني) ──────────────────────


@dataclass(frozen=True)
class RepatriationRef:
    """مرجعٌ مُسند: أجلُ ترحيل الحصيلة + سقفُ أجل الائتمان المسموح للمشتري غير المقيم."""

    name: str
    repatriation_days: int
    credit_ceiling_days: int
    status: str = "documented"

    def __post_init__(self) -> None:
        if self.repatriation_days <= 0 or self.credit_ceiling_days <= 0:
            raise AssuranceWindowError("أجلُ الترحيل وسقفُ الائتمان عددُ أيام > 0")
        if not self.name.strip():
            raise AssuranceWindowError("بلا اسم مرجع — أيُّ رقمٍ سيُنسب؟")


def legal_term_ceiling(ref: RepatriationRef) -> int:
    """أجلُ السداد الأقصى الذي يجمع شرطي المرجع (التسديدُ داخل سقف الائتمان **والترحيلُ
    داخل نافذة الترحيل** بما أنّ الترحيل يجري يومَ الدفع)."""
    return min(ref.repatriation_days, ref.credit_ceiling_days)


def term_survives(term_days: int, ref: RepatriationRef) -> bool:
    if term_days <= 0:
        raise AssuranceWindowError("أجلُ السداد يجب أن يكون > 0 يوم")
    return term_days <= legal_term_ceiling(ref)


def buffer_days(term_days: int, ref: RepatriationRef) -> int:
    """هامشُ أيام التأخير المسموح قبل أن يقع الخرق — **هو** الرقمُ التصميمي لا الأجل.

    Net-120 تحت نافذة 120 يوم يعني هامشاً **صفرياً**: يومُ تأخيرٍ واحد من العميل يخرق،
    والصادقُ أن يُقال هذا لا أن يُقال «مسموح».
    """
    return ref.repatriation_days - term_days


def robust_terms(
    candidates: tuple[int, ...],
    refs: tuple[RepatriationRef, ...],
    min_buffer_days: int = 30,
) -> list[dict[str, object]]:
    """مجموعةُ الآجال التي تنجو تحت **كل** مرجع مُسند، مع هامش تأخيرٍ أدناه معلَن.

    ⛔ لا يجمع بينها «متوسط»: التسويةُ على رقمٍ وسيط هي بالضبط ما يمنع الدستور.
    """
    rows: list[dict[str, object]] = []
    for term in candidates:
        per_ref: dict[str, dict[str, object]] = {}
        survives_all = True
        for ref in refs:
            ok = term_survives(term, ref)
            buffer = buffer_days(term, ref)
            per_ref[ref.name] = {
                "survives": ok,
                "buffer_days": buffer,
                "legal_ceiling_days": legal_term_ceiling(ref),
                "ref_status": ref.status,
            }
            survives_all = survives_all and ok and buffer >= min_buffer_days
        rows.append(
            {
                "term_days": term,
                "robust_under_all_refs": survives_all,
                "per_ref": per_ref,
            }
        )
    return rows


# ── 5b) قيدُ التحكيم: مَن صدّق الشهادة، وعلى أيّ نطاق، وضمن أيّ أفق ──────────────
#
# وُلد هذا القيدُ من حدثٍ مُسندٍ بتاريخٍ واحد (2026-09-08): شهادةُ Lean بصفر `sorry`
# لمسألة ألفية، مُعلَنةٌ من صاحبِ المصلحة، وفيها دعوةُ تحقّق مستقلّ، ومعه نزاعُ أسبقيةٍ
# على المُدخلات — فصار **العمرُ يومَين والحالةُ غيرُ قابلةٍ للاقتباس**. أي أنّ الصلاحية
# محوراَنِ مستقلّان: **قِدَمُ الرقم** (§4) و**استقلالُ مَن صدّقه** (هنا)، ولا يُنتج أحدهما
# الآخر. ولا يُخرج هذا القسمُ رأياً قانونياً ولا حكماً في الرياضيات: يصفُ فقط **ما يجوز
# لنا أن نقتبسَه في وثيقةٍ بيعية** وبأيّ تاريخٍ تُعادُ القراءة.

#: حالاتُ استقلالِ المصدر — مجموعةٌ مغلقة؛ لا «موثوقٌ عادةً».
PROVENANCE_STATES: tuple[str, ...] = (
    "INDEPENDENTLY_VERIFIED",
    "VENDOR_ONLY",
    "CONTESTED_PRIORITY",
    "REFUTED_INDEPENDENTLY",
    "UNSTATED",
)

#: سببُ كلِّ حالةٍ كما يُكتبُ في التقرير — لا سُلَّمَ `if` يقرّرُ السرد.
_PROVENANCE_REASONS: dict[str, str] = {
    "INDEPENDENTLY_VERIFIED": "",
    "VENDOR_ONLY": "النتيجةُ منشورةٌ من صاحبِ المصلحة وحدَه: تُذكر بوصفها إعلاناً لا دليلاً",
    "CONTESTED_PRIORITY": "نزاعٌ مُسندٌ على مصدرِ المُدخلات أو الأسبقية — لا تُباع شهادةً",
    "REFUTED_INDEPENDENTLY": "دُحضَت استقلالياً — تُترك في سجلِّ الدحض لا في العرض",
    "UNSTATED": "استقلالُ المصدر غيرُ مُعلَن — يُمنع الاقتباس لا يُرجَّأ",
}

#: سقْفُ الاقتباس لكل حالةٍ — ⛔ لا يُرفَع بثقةٍ سردية.
_PROVENANCE_CEILING: dict[str, str] = {
    "INDEPENDENTLY_VERIFIED": "ACCEPT",
    "VENDOR_ONLY": "THROTTLE",
    "CONTESTED_PRIORITY": "THROTTLE",
    "REFUTED_INDEPENDENTLY": "BLOCK",
    "UNSTATED": "BLOCK",
}

_CEILING_RANK: dict[str, int] = {"ACCEPT": 0, "THROTTLE": 1, "BLOCK": 2}

#: من صاغَ **نطاقَ** العبارة المُبرهَن عليها (لا البرهانَ نفسه). القاعدةُ عندنا:
#: مَن بنى البرهانَ لا يملكُ أن يكون وحده مَن قرّر أنّ العبارةُ هي العبارةُ المطلوبة.
SCOPE_SOURCE_STATES: tuple[str, ...] = ("THIRD_PARTY", "SELF", "UNSTATED")

#: قاعدةُ معهد كلاي (قواعدُ 2018-09-26): لا تُقبل مشاركةٌ مباشرة، ويُشترط نشرٌ في منفذٍ
#: مؤهَّل **و** مضيُّ عامَين **و** قبولٌ عامّ. هذا الرقمُ مُعامِلُ تصميمِ عقدٍ عندنا،
#: لا توقّعٌ بقبول أيّ نتيجة.
CLAY_MIN_YEARS_AFTER_PUBLICATION = 2


def _tighten(ceiling: str, candidate: str) -> str:
    """السقفُ هو **أضعفُ** حلقةٍ معلَنة — لا تُرفَعُ حالةٌ بحالةٍ أخرى مجاورة."""
    return candidate if _CEILING_RANK[candidate] > _CEILING_RANK[ceiling] else ceiling


@dataclass(frozen=True)
class Adjudication:
    """قرارُ الاقتباس على محورِ الاستقلال — مستقلٌّ عن قرارِ القِدَم في `PinStatus`."""

    ceiling: str  # ACCEPT | THROTTLE | BLOCK
    quotable: bool
    reasons: tuple[str, ...] = ()
    notes: tuple[str, ...] = ()


def adjudicate(
    *provenance: str,
    scope_source: str = "UNSTATED",
    toolchain: str = "",
    verified_by: tuple[str, ...] = (),
) -> Adjudication:
    """يسقي قرارَ الاقتباس من حالاتِ الاستقلال المُعلَنة، ويُشدِّدُ الأضعفَ بينها.

    لا «تخفيفاً بالسرد»: حالةٌ واحدةٌ `UNSTATED` تكفي للمنع، لأنّ المجهولَ عندنا يُعامَلُ
    مرفوضاً، لا مقبولاً بانتظارِ حُسنِ نيّة.
    """
    if not provenance:
        raise AssuranceWindowError("لا قرارَ تحكيمٍ بلا حالةِ استقلالٍ واحدةٍ على الأقلّ")
    for state in provenance:
        if state not in PROVENANCE_STATES:
            raise AssuranceWindowError(f"حالةُ استقلالٍ خارج المجموعة المغلقة: {state!r}")
    if scope_source not in SCOPE_SOURCE_STATES:
        raise AssuranceWindowError(f"مصدرُ نطاقٍ غيرُ مسموح: {scope_source!r}")

    ceiling = "ACCEPT"
    for state in provenance:
        ceiling = _tighten(ceiling, _PROVENANCE_CEILING[state])
    reasons = [
        _PROVENANCE_REASONS[s]
        for s in PROVENANCE_STATES
        if s in provenance and _PROVENANCE_REASONS[s]
    ]

    if scope_source != "THIRD_PARTY":
        ceiling = _tighten(ceiling, "THROTTLE")
        reasons.append(
            "نطاقُ العبارةِ صاغه الطرفُ المعنيّ نفسُه (أو لم يُعلَن): البرهانُ على صيغةٍ "
            "غيرِ مُستقلّةٍ لا يُثبتُ أنّها الصيغةُ المطلوبة"
        )

    notes: list[str] = []
    if toolchain and ("-rc" in toolchain.lower() or "dev" in toolchain.lower()):
        notes.append(
            f"أداةُ التحقق نفسها إصدارٌ غيرُ نهائي ({toolchain}): المُدقِّقُ جزءٌ من الأفق "
            "المتقادم، ويُعادُ البناءُ عند كلِّ ترقيةِ سلسلةِ أدوات"
        )
    if not verified_by:
        notes.append("لا قائمةَ مُدقِّقين مستقلّين مُسندةٍ بتاريخ — ⛔ لا يُذكر عددُ الساعاتِ بديلاً عنها")
    return Adjudication(ceiling, ceiling == "ACCEPT", tuple(reasons), tuple(notes))


def pin_is_quotable(status: PinStatus, adjudication: Adjudication) -> bool:
    """المحورَان معاً: رقمٌ طازجٌ غيرُ مستقلّ لا يُقتبس، ومستقلٌّ منتهٍ لا يُقتبس."""
    return status.quotable and adjudication.quotable


@dataclass(frozen=True)
class AcceptanceCorridor:
    """مِدةُ «البرهانُ موجودٌ ولا يُشترى»: من النشر إلى أوّلِ تاريخٍ يُعتَدُّ به رسميّاً."""

    clock_started: bool
    published_on: date | None
    earliest_eligible_on: date | None
    corridor_days: int | None
    elapsed_days: int | None
    remaining_days: int | None
    inside: bool
    rule_ar: str

    @property
    def fraction_elapsed(self) -> float | None:
        if not self.corridor_days:
            return None
        assert self.elapsed_days is not None
        return round(min(1.0, self.elapsed_days / self.corridor_days), 6)


def _add_years(anchor: date, years: int) -> date:
    """تاريخٌ تقويميٌّ بديلٌ عند 29 فبراير — بلا جُزَئاتٍ مُستديرة تُغيّر عدَّ الأيام."""
    try:
        return anchor.replace(year=anchor.year + years)
    except ValueError:
        return anchor.replace(year=anchor.year + years, day=28)


def acceptance_corridor(
    published_on: date | None,
    as_of: date,
    *,
    qualifying_outlet: bool = True,
    min_years: int = CLAY_MIN_YEARS_AFTER_PUBLICATION,
) -> AcceptanceCorridor:
    """يُحوّل شرطَ «عامان في منفذٍ مؤهَّل» إلى عدِّ أيامٍ يعمل عليه العقدُ والسعر.

    ⛔ لا يحكم بقبولٍ ولا برفضٍ ولا بصحّةِ برهان: يُخرج فقط **متى يبدأُ العدُّ ومتى
    ينتهي**، لأنّ قيمةَ شهادتِنا كلِّها تقع داخل هذا الممرّ لا بعده.
    """
    if min_years < 1:
        raise AssuranceWindowError(f"عامانِ على الأقلّ قبلَ أيّ اعتداد: min_years={min_years}")
    if published_on is None or not qualifying_outlet:
        return AcceptanceCorridor(
            clock_started=False,
            published_on=published_on,
            earliest_eligible_on=None,
            corridor_days=None,
            elapsed_days=None,
            remaining_days=None,
            inside=True,
            rule_ar=(
                "لم يبدأ العدُّ: لا نشرٌ في منفذٍ مؤهَّل. الممرُّ مفتوحٌ بلا تاريخِ انتهاءٍ "
                "محسوب — أي أنّ الادّعاءَ لا يملكُ جدولاً زمنياً للاعتداد"
            ),
        )
    if published_on > as_of:
        raise AssuranceWindowError("تاريخُ النشر أسبقُ من تاريخِ المراجعة؟ لا يُقبل")
    earliest = _add_years(published_on, min_years)
    corridor = (earliest - published_on).days
    elapsed = (as_of - published_on).days
    remaining = max(0, (earliest - as_of).days)
    return AcceptanceCorridor(
        clock_started=True,
        published_on=published_on,
        earliest_eligible_on=earliest,
        corridor_days=corridor,
        elapsed_days=elapsed,
        remaining_days=remaining,
        inside=remaining > 0,
        rule_ar=(
            f"من {published_on.isoformat()} إلى {earliest.isoformat()} = {corridor} يوماً "
            "من «برهانٍ موجودٍ ولا يُشترى» (شرطُ المنفذِ المؤهَّل + العامَّين؛ يبقى القبولُ "
            "العامُّ شرطاً ثالثاً لا يُحسب هنا)"
        ),
    )


# ── 6) خلاصةٌ مُعلنة الأرقام (يستعملها سكربتُ القياس والتوثيق التجاري) ──────────


def summarize(
    low: HorizonAnchor,
    high: HorizonAnchor,
    ratio: float,
    drifts: tuple[SuiteDrift, ...],
    churn: ChurnRates,
    cycle_days: float,
    release_cadence_days: float | None = None,
    tolerance_points: float = 5.0,
    theta: float = 0.9,
) -> dict[str, object]:
    """يربط القطعَ الأربع في خلاصةٍ واحدة قابلة لإعادة الحساب حرفياً.

    يجمع: المرونةَ والأشرطة، جداولَ التقادم والنافذةَ الصلبة، احتمالَ أن تسبقَ الإصدارَةُ
    الدورةَ، والنقاطَ التي تتحرك قبل الكشف، والأحداثَ السنوية (وحدةُ الفوترة).
    ⛔ لا يُخرج سعراً ولا إيراداً ولا «ضماناً» — مخرجاته هندسية.
    """
    eps, mult = horizon_sensitivity(low, high, ratio)
    table = warranty_table(drifts, tolerances=(2.0, 5.0, 10.0))
    windows: list[float] = []
    for row in table:
        value = row[f"warranty_days_at_{tolerance_points:g}pts"]
        if value is not None:
            windows.append(float(value))
    fastest = max(drifts, key=drift_velocity) if drifts else None
    min_window = min(windows) if windows else None
    risk_days = warranty_window_days(churn, theta)
    cadence = (
        release_cadence_days
        if release_cadence_days is not None
        else (1.0 / churn.release_per_day if churn.release_per_day > 0 else None)
    )
    return {
        "horizon_risk_exponent": round(eps, 6),
        "exposure_multiplier_at_ratio": round(mult, 4),
        "horizon_bands": horizon_band_flags(eps, (2.0, 4.0, 8.0, 16.0)),
        "suite_count": len(table),
        "warranty_table": table,
        "shortest_warranty_days": None if min_window is None else round(min_window, 2),
        "most_volatile_suite": None if fastest is None else fastest.suite,
        "risk_warranty_days": None if risk_days is None else round(risk_days, 2),
        "release_beat_probability_per_cycle": (
            None if cadence is None else round(release_beat_probability(cycle_days, cadence), 4)
        ),
        "detection_lag_days": detection_lag_days(cycle_days),
        "eval_events_per_year": None if cadence is None else round(events_per_year(cadence), 2),
        "drift_before_detection": {
            drift.suite: round(drift_before_detection(drift, cycle_days), 4) for drift in drifts
        },
        "boundaries": (
            "نقطتا إسناد لا نموذج عالمي؛ سرعةُ التقادم خاصةٌ بحزمتها؛ ⛔ لا قياسَ عميل "
            "ولا تشغيلَ نموذج في أيّ رقمٍ هنا."
        ),
    }
