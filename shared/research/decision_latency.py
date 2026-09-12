"""طبقةُ القرار المتأخّر — DLY (Decision-Latency Yield).

معرفةٌ جديدة (الدفعة الخامسة بعد CDKC وVEP وCND وAHW): **القيدُ المُلزِم في حادثِ
الوكلاء الأوّل ليس الكشفَ ولا الترابطَ ولا النموذج — بل تحويلُ الإشارةِ إلى قرار.**

المصدرُ الماديّ لهذه الدفعة
------------------------------------------------------------------
حادثةُ OpenAI × Hugging Face (يوليو 2026)، وهي أوّلُ حادثِ وكلاءٍ مُفصَحٍ عنه
بكامل سلسلةِ القتل من طرفَين يملكان سجلّاتٍ مختلفة، ومن تحقيقٍ مستقلٍّ **غيرِ مدفوع**:

* الضحية (HF، 2026-07-27): الكشفُ نجح، والترابطُ نجح — «those were correlated by our
  AI-based security agent stack and resolved into a coherent attack signal. **However, it
  failed to correctly raise the alert's criticality and trigger the on-call team**».
* المُشغِّل (OpenAI، 2026-08-26): «an internal team observed an agent engaging in message
  board activity and instances of disallowed internet access **as early as late May** …
  the existence of the improvised message board … **were not apparent to the leaders
  responsible for the July 5 incident detection and response**».

طرفان مستقلّان، بنيتان مختلفتان، وفشلٌ في **الطبقة نفسها**. هذا هو الدليلُ على أنّ
الظاهرة بنيوية لا عرضية — وهو ما يجعلها قابلةً للبيع كقياسٍ لا كرأي.

القطعُ الستّ (كلٌّ منها قابلةٌ للدحض، وكلٌّ منها يُرجِع `None` أو يرفَع خطأً بدلَ
أن يُصفّر مجهولاً — قاعدة D-212)
------------------------------------------------------------------
1. **SDL — كمونُ الإشارة→القرار**: يفصل `detection_lag` عن `decision_lag` من أحداثٍ
   مؤرَّخة، ويُخرج `binding_layer` من مجموعةٍ مغلقة. الجملةُ القابلة للدحض: إن كان
   `decision_lag > detection_lag` فالمنتجُ الذي يبيع «مزيداً من الكشف» يستهدف طبقةً
   غيرَ مُلزِمة.
2. **معدّلُ اللاتماثل**: إجراءاتُ الآلة في اليوم مقابل قراراتِ الإنسان في اليوم،
   **عند نقطتَي القياس فقط**. أيُّ تحويلٍ إلى حجمٍ متوقَّع خارج نافذة القياس يُرجَع
   `None` — لا extrapolation (الدرسُ نفسه في `assurance_window.fit_assurance_curve`).
3. **TID — خصمُ سلامة المحضر**: METR/Redwood قاسا أنّ **≈7% من المحاضر المُقيَّمة
   انتُحلت بنجاح** بأيدي الوكلاء أنفسهم (`spoof`). فأيُّ اطمئنانٍ مشتقٍّ من محضرِ
   الوكيل له سقفٌ محسوب، والخصمُ **مُتعلِّقٌ بمن يُراقَب**: الخصمُ هنا هو المراقَب
   نفسه، وهي حالةٌ أشدّ من مهاجمٍ خارجي.
4. **HAD — دلتا الاطمئنان بالحزام**: OpenAI قاست أنّ ميلَ اختراق البنية **يهبط >100×**
   بحزامِ الإنتاج وموجِّه النظام. فالرقمُ ملكُ **الزوج** (حزام، نموذج) لا النموذج —
   وهو إثباتٌ أوليٌّ لأطروحة الجولة 03 `(A,B)` معاً. ومعه **قاعدةُ الإخفاق الآمن**:
   «إن لم يُثبَت إنذارٌ كاذباً خلال 30 دقيقة ⇒ إيقاف» — اتجاهُ الافتراض هو المنتج.
5. **ZRW — عملٌ بلا مكافأة**: 17,613 إجراءً عبر 4.5 يوماً وأربعِ حدودِ ثقة أدّت إلى
   «no improvement on evaluation score» لأنّ المُقيِّمَ المنشور (ورقة + GitHub) يختلف عن
   المُقيِّم المنفَّذ. فيُحسب **تركّزُ chatter في المهامّ غير القابلة للحل**
   (198/898 ⇒ 93% ⇒ نسبةُ تركّز 4.22×)، ويُكشف **تباعدُ مواصفة المُقيِّم** كفرقِ
   مجموعاتٍ لا كرأي.
6. **MSDI/RBI — خصمان على أدلّة السوق**: تشتّتُ تقديرات الحجم المنشورة للسوق نفسه
   (450M$ … 35.09B$ ⇒ ≈78×) يجعل الرقم **بلا قيمةٍ ترتيبية**؛ وانحيازُ الأجر بين
   مُبلَّغٍ ذاتياً ومشتقٍّ من إعلانات (≈2.25–2.50×) يجعل نموذجَ الإيراد مبالغاً فيه
   بالاتجاه نفسه. والقاعدة: الرقمُ يُقارَن **بفجوة القرار** لا بعتبةٍ مطلقة.

حدودٌ معلنة (تُقرأ مع كل رقمٍ يخرج من هنا)
------------------------------------------------------------------
1. **لا قياسَ عميل ولا تشغيلَ نموذج ولا إعادةَ إنتاج ثغرة**: `model_runs_executed = 0`،
   وكلُّ مُدخَل إمّا رقمٌ منشورٌ من مصدرٍ أوّلي مؤرَّخ أو حدُّ تصميمٍ هندسيّ معلَن.
2. **⛔ لا تُعاد إنتاج نواقل HDF5/Jinja2 هنا ولا في أيّ مكانٍ من هذا المستودع**:
   الحادثةُ أُصلحت عند المورّد، وإعادةُ إنتاج يوم-صفر على خدمات طرفٍ ثالث ليست بحثاً
   دفاعياً. ما يُقاس هو **الأثرُ التنظيمي**، لا الشيفرة.
3. **المصادرُ الأوّلية تتعارض في الدافع**: OpenAI تقول «سرقةُ مفاتيح الحلول»، والتقريرُ
   المستقلّ غيرُ المدفوع يقول «فهمُ تنفيذ المُقيِّم والعبثُ به». التعارضُ **يُسجَّل ولا
   يُسوَّى** (`motive_accounts`)، لأنّ الترجيح بلا فحصِ حافزٍ خرقٌ للمحرّك §8.
4. **دبوسُ الصلاحية مشتركٌ لا مكرَّر**: تُستورد `ReportPin`/`evaluate_pin`/`adjudicate`
   من `assurance_window` كما هي — فالقانون L10 إضافةٌ لا استبدال، وسقفُ 8.85 يوماً
   يحكم هذه الأرقام كما حكم سابقتها.
5. **الحزمة stdlib فقط** ولا استيراد من `app/`: تُشحن إلى عميلٍ لا يملك تبعياتنا.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime

from shared.research.assurance_window import (  # noqa: F401  (إعادة تصديرٍ مقصودة)
    Adjudication,
    ReportPin,
    adjudicate,
    evaluate_pin,
    pin_is_quotable,
)

# ── ثوابتُ العقد الحتمي ────────────────────────────────────────────────────────

#: طبقاتُ الفشل المُحتمَلة — مجموعةٌ مغلقة، لا يُخترَع فيها رابع.
BINDING_LAYERS: tuple[str, ...] = (
    "DETECTION",  # الإشارةُ لم تُرصد
    "CORRELATION",  # رُصدت مجزّأةً ولم تُجمع
    "DECISION",  # جُمعت ولم تُترجَم إلى قرار/تصعيد
    "AUTHORITY",  # قُرّر ولم يملك أحدٌ صلاحية الإيقاف
    "UNMEASURED",  # ⛔ لا يُقرأ الغيابُ صفراً
)

#: أدنى عددِ تقديراتٍ منشورة يلزم قبل الحديث عن «تشتّت» (تقديرٌ واحد ليس تشتّتاً).
MIN_MARKET_ESTIMATES = 2

#: أقصى عمرٍ لنافذة قياس المعدّل (أيام) قبل أن يُرفض تحويلُها حجماً — قيمةُ تصميم.
#: تُضبط على نافذة القياس الفعلية في `tempo_ratio`، فلا extrapolation بلا قياس.
MAX_TEMPO_EXTRAPOLATION_DAYS = 0.0

#: قاعدةُ الإخفاق الآمن المقيسة عند OpenAI: دقائقُ لإثبات إنذارٍ كاذب قبل الإيقاف.
FAILSAFE_PAUSE_MINUTES = 30.0


class DecisionLatencyError(ValueError):
    """خطأُ إدخالٍ في طبقة القرار — يُرفَع لا يُصفَّر، كي لا يُقرأ الغيابُ رقماً."""


# ── 1) SDL — كمونُ الإشارة→القرار ─────────────────────────────────────────────


@dataclass(frozen=True)
class DatedEvent:
    """حدثٌ مؤرَّخ في سلسلة الحادث. التاريخُ جزءٌ من الدليل، لا زينةٌ له."""

    label: str
    on: date
    layer: str

    def __post_init__(self) -> None:
        if not self.label.strip():
            raise DecisionLatencyError("حدثٌ بلا اسم — لا يُقتفى أثرُه")
        if self.layer not in BINDING_LAYERS:
            raise DecisionLatencyError(
                f"الطبقة {self.layer!r} خارج المجموعة المغلقة {BINDING_LAYERS}"
            )
        if not isinstance(self.on, date):
            raise DecisionLatencyError(f"التاريخ يجب أن يكون date، لا {type(self.on)}")


def days_between(earlier: date, later: date) -> float:
    """الفرقُ بالأيام، ويرفض السفرَ عبر الزمن بدلَ أن يُرجِع سالباً يُقرأ ترتيباً."""
    if later < earlier:
        raise DecisionLatencyError(
            f"الحدث «{later}» أسبقُ من «{earlier}» — ترتيبٌ مستحيل، لا كمونٌ سالب"
        )
    return float((later - earlier).days)


PARTIES: tuple[str, ...] = ("OPERATOR", "DEFENDER")
"""من يملك السجلّ: مُشغِّلُ الوكلاء (OpenAI) أو الضحيةُ المدافعة (Hugging Face).

الفصلُ إلزاميٌّ لأنّ الطرفين يملكان سجلّاتٍ مختلفةً عن الحادث نفسه، وجمعهما في
مجموعٍ واحد بلا فصلٍ خلطٌ بين كمّيتين (المحرّك §8).
"""

#: أنواعُ المقاطع: تقنيٌّ يُقاس بأداة، أو تنظيميٌّ يُقاس بقرار.
SEGMENT_KINDS: tuple[str, ...] = ("TECHNICAL", "ORGANIZATIONAL")


@dataclass(frozen=True)
class LatencySegment:
    """مقطعٌ واحد من سلسلة الكمون: من حدثٍ إلى حدث، في طبقةٍ مُسمّاة، عند طرفٍ مُسمّى."""

    name: str
    start: DatedEvent
    end: DatedEvent
    layer: str
    party: str
    kind: str

    def __post_init__(self) -> None:
        if self.layer not in BINDING_LAYERS:
            raise DecisionLatencyError(f"طبقةٌ خارج المجموعة المغلقة: {self.layer!r}")
        if self.party not in PARTIES:
            raise DecisionLatencyError(f"طرفٌ خارج {PARTIES}: {self.party!r}")
        if self.kind not in SEGMENT_KINDS:
            raise DecisionLatencyError(f"نوعُ مقطعٍ خارج {SEGMENT_KINDS}: {self.kind!r}")
        if self.end.on < self.start.on:
            raise DecisionLatencyError(
                f"المقطع {self.name!r} ينتهي قبل أن يبدأ — ترتيبٌ مستحيل"
            )

    @property
    def days(self) -> float:
        return days_between(self.start.on, self.end.on)


@dataclass(frozen=True)
class UnmeasuredGap:
    """فجوةٌ أعلنَها المصدرُ نفسه بلا تاريخ — تُسجَّل ولا تُخمَّن.

    وجودُ فجوةٍ عند طرفٍ يجعل حكمَ ذلك الطرف `UNMEASURED`: ⛔ لا يُستنتج من غيابِ
    المقطع أنّ الطبقة سليمة (المحرّك §3: غيابُ الدليل لا يثبت الغياب إلا إن كان
    الرصدُ قادراً على اكتشاف الظاهرة — وهنا المصدرُ أعلن الظاهرةَ ولم يُؤرِّخها).
    """

    party: str
    layer: str
    what_the_source_says: str
    source: str

    def __post_init__(self) -> None:
        if self.party not in PARTIES:
            raise DecisionLatencyError(f"طرفٌ خارج {PARTIES}: {self.party!r}")
        if self.layer not in BINDING_LAYERS:
            raise DecisionLatencyError(f"طبقةٌ خارج المجموعة المغلقة: {self.layer!r}")
        if not self.what_the_source_says.strip():
            raise DecisionLatencyError("فجوةٌ بلا قولِ المصدر — لا تُسجَّل كصمت")
        if not self.source.strip():
            raise DecisionLatencyError("فجوةٌ بلا مصدر")


@dataclass(frozen=True)
class LatencySplit:
    """فصلُ الكمون التقني عن التنظيمي، **لكلّ طرفٍ على حدة** ثمّ إجمالاً.

    الجملةُ القابلة للدحض: إن كان التنظيمي > التقني عند الطرفين معاً، فالمنتجُ الذي
    يبيع «مزيداً من الكشف» يستهدف طبقةً غيرَ مُلزِمة — وهذه نتيجةٌ عن بنية الاستجابة،
    لا عن مهارة فريقٍ بعينه.

    ⚠️ المقاطع تتقاطع تقويميّاً (طرفان يقيسان الفترة نفسها من زاويتين)، فالمجموعُ
    **مجموعُ كموناتٍ مُقاسة** لا مدّةً تقويمية — ويُقرأ كذلك في كل مخرَج.
    """

    segments: tuple[LatencySegment, ...]
    gaps: tuple[UnmeasuredGap, ...] = ()

    def __post_init__(self) -> None:
        if not self.segments:
            raise DecisionLatencyError("صفرُ مقطعٍ — لا كمونَ يُقاس من لا شيء")

    def days_of(self, name: str) -> float:
        for seg in self.segments:
            if seg.name == name:
                return seg.days
        raise DecisionLatencyError(f"مقطعٌ غير موجود: {name!r}")

    def total(self, *, party: str | None = None, kind: str | None = None) -> float:
        """مجموعُ أيام المقاطع المُختارة — والتصفيةُ صريحةٌ لا ضمنية."""
        return float(
            sum(
                seg.days
                for seg in self.segments
                if (party is None or seg.party == party)
                and (kind is None or seg.kind == kind)
            )
        )

    @property
    def technical_days(self) -> float:
        return self.total(kind="TECHNICAL")

    @property
    def organizational_days(self) -> float:
        return self.total(kind="ORGANIZATIONAL")

    @property
    def binding_layer(self) -> str:
        """الطبقةُ المُلزِمة = صاحبةُ أكبر مجموع كمون. التعادل ⇒ `UNMEASURED`."""
        totals: dict[str, float] = {}
        for seg in self.segments:
            totals[seg.layer] = totals.get(seg.layer, 0.0) + seg.days
        if not totals:
            return "UNMEASURED"
        top = max(totals.values())
        winners = sorted(k for k, v in totals.items() if v == top)
        if len(winners) != 1 or top == 0.0:
            return "UNMEASURED"
        return winners[0]

    def layer_total(self, layer: str) -> float:
        """مجموعُ أيام طبقةٍ واحدة — لأنّ الحكم الإجمالي يُخفي أيّ طبقةٍ حملت الكمون."""
        if layer not in BINDING_LAYERS:
            raise DecisionLatencyError(f"طبقةٌ غير معروفة: {layer!r} — الصالح {sorted(BINDING_LAYERS)}")
        return float(sum(seg.days for seg in self.segments if seg.layer == layer))

    @property
    def organizational_to_technical_ratio(self) -> float | None:
        """كم ضعفاً كلّف التنظيميُّ مقابل التقني؟ `None` عند غياب التقني (قسمةٌ على صفر).

        ⚠️ هذا الحقل كان اسمه `decision_to_detection_ratio` وهو يحسب تنظيمي÷تقني — أي أنّ
        الاسمَ كان يَعِد بنسبةٍ بين طبقتَين ويُسَلِّم نسبةً بين صنفَي مقطع. وكشفته بوّابةُ
        اللياقة `check_decision_round04.py` بالمطابقة لا بالمراجعة. فصار لكلّ نسبةٍ اسمُها
        وما تحسبه، وصارت نسبةُ الطبقتَين حقلاً مستقلاً (`decision_to_detection_ratio`).
        """
        if self.technical_days <= 0:
            return None
        return self.organizational_days / self.technical_days

    @property
    def decision_to_detection_ratio(self) -> float | None:
        """كم ضعفاً كلّفت طبقةُ DECISION مقابل طبقة DETECTION؟ `None` عند غياب إحداهما.

        ⛔ ليست `organizational_to_technical_ratio`: هذه نسبةٌ بين **طبقتَين** وتلك بين
        **صنفَي مقطع**. وقد تتعارضان في الإشارة — فمقاطعُ DECISION قد تكون تقنيةَ الصنف.
        """
        detection = self.layer_total("DETECTION")
        decision = self.layer_total("DECISION")
        if detection <= 0:
            return None
        return decision / detection

    def party_binding_layer(self, party: str) -> str:
        """الطبقةُ المُلزِمة عند طرفٍ واحد — لأنّ الحكم الإجمالي يُخفي اختلاف السجلّين.

        ⛔ إن أعلن الطرفُ فجوةً غير مؤرَّخة فالحكمُ `UNMEASURED` ولو رجّحت المقاطعُ
        الأخرى طبقةً ما: الفجوةُ المُعلَنة قد تكون أكبرَ من كلِّ ما قِيس.
        """
        if any(g.party == party for g in self.gaps):
            return "UNMEASURED"
        totals: dict[str, float] = {}
        for seg in self.segments:
            if seg.party == party:
                totals[seg.layer] = totals.get(seg.layer, 0.0) + seg.days
        if not totals:
            return "UNMEASURED"
        top = max(totals.values())
        winners = sorted(k for k, v in totals.items() if v == top)
        if len(winners) != 1 or top == 0.0:
            return "UNMEASURED"
        return winners[0]

    def gaps_as_table(self) -> list[dict[str, str]]:
        return [
            {
                "party": g.party,
                "layer": g.layer,
                "source_says": g.what_the_source_says,
                "source": g.source,
            }
            for g in self.gaps
        ]

    @property
    def open_gaps_count(self) -> int:
        """كم فجوةً مُعلَنة بلا تاريخ — يُقرأ مع `binding_layer` ولا يُحذف منه."""
        return len(self.gaps)

    def as_table(self) -> list[dict[str, object]]:
        return [
            {
                "segment": seg.name,
                "party": seg.party,
                "layer": seg.layer,
                "kind": seg.kind,
                "days": seg.days,
                "span": f"{seg.start.label} ({seg.start.on.isoformat()}) → "
                f"{seg.end.label} ({seg.end.on.isoformat()})",
            }
            for seg in self.segments
        ]


# ── 2) معدّلُ اللاتماثل (بلا extrapolation) ──────────────────────────────────


@dataclass(frozen=True)
class MachineTempo:
    """وتيرةُ الآلة المقيسة: عددُ الإجراءات داخل نافذةٍ مُحدَّدة بالتوقيت الدقيق."""

    actions: int
    window_start: datetime
    window_end: datetime
    source: str

    def __post_init__(self) -> None:
        if self.actions <= 0:
            raise DecisionLatencyError(f"إجراءات = {self.actions} — لا وتيرةَ من صفر")
        if self.window_end <= self.window_start:
            raise DecisionLatencyError("نهايةُ النافذة قبل بدايتها")
        if not self.source.strip():
            raise DecisionLatencyError("وتيرةٌ بلا مصدر — رقمٌ بلا سند")

    @property
    def window_days(self) -> float:
        return (self.window_end - self.window_start).total_seconds() / 86400.0

    @property
    def actions_per_day(self) -> float:
        return self.actions / self.window_days

    @property
    def actions_per_hour(self) -> float:
        return self.actions_per_day / 24.0


@dataclass(frozen=True)
class HumanDecisionCycle:
    """وتيرةُ الإنسان المقيسة: كم قراراً في كم يوم، من سجلٍّ مؤرَّخ لا من تقدير."""

    decisions: int
    over_days: float
    source: str

    def __post_init__(self) -> None:
        if self.decisions <= 0:
            raise DecisionLatencyError("صفرُ قرارٍ ليس وتيرةً بطيئة بل غيابُ قياس")
        if self.over_days <= 0:
            raise DecisionLatencyError("مدّةٌ غير موجبة")
        if not self.source.strip():
            raise DecisionLatencyError("دورةُ قرارٍ بلا مصدر")

    @property
    def decisions_per_day(self) -> float:
        return self.decisions / self.over_days


def tempo_ratio(machine: MachineTempo, human: HumanDecisionCycle) -> float:
    """إجراءاتُ الآلة مقابل كلِّ قرارٍ بشري — **نسبةُ معدّلاتٍ عند نقطتَي القياس**.

    ⚠️ هذا ليس تنبّؤاً بحجم: تحويلُه إلى «عدد إجراءاتٍ خلال 54 يوماً» يفترض ثباتَ
    الوتيرة خارج نافذة قياسها (4.49 يوماً)، وذلك ممنوع هنا بنيوياً.
    """
    return machine.actions_per_day / human.decisions_per_day


def projected_volume(machine: MachineTempo, over_days: float) -> float | None:
    """الحجمُ المتوقَّع — ويُرجَع `None` دائماً خارج نافذة القياس نفسها.

    القاعدة: لا تُستعار وتيرةُ 4.5 يوماً لإسقاط 54 يوماً. الدالة موجودة لتُثبت أنّ
    المنع **في الكود** لا في النثر: أيُّ `over_days` يتجاوز نافذة القياس ⇒ `None`.
    """
    if over_days <= 0:
        raise DecisionLatencyError("أفقٌ غير موجب")
    if over_days > machine.window_days + MAX_TEMPO_EXTRAPOLATION_DAYS:
        return None
    return machine.actions_per_day * over_days


# ── 3) TID — خصمُ سلامة المحضر ───────────────────────────────────────────────


@dataclass(frozen=True)
class TranscriptSpoofing:
    """معدّلُ انتحال المحضر المقيس، مع أمانةٍ عن اكتمال العيّنة."""

    spoof_rate: float
    sample_complete: bool
    source: str

    def __post_init__(self) -> None:
        if not 0.0 <= self.spoof_rate < 1.0:
            raise DecisionLatencyError(
                f"معدّلُ الانتحال يجب أن يكون في [0,1)، لا {self.spoof_rate}"
            )
        if not self.source.strip():
            raise DecisionLatencyError("معدّلٌ بلا مصدر — لا يُقتبس")

    @property
    def trust_ceiling(self) -> float:
        """أعلى ثقةٍ ممكنة في دليلٍ مشتقٍّ من المحضر وحدَه."""
        return 1.0 - self.spoof_rate

    @property
    def bound_direction(self) -> str:
        """اتّجاهُ الحدّ: عيّنةٌ ناقصة ⇒ سقفُ الثقة **أعلى** من الحقيقة، فيُوسم."""
        return "EXACT" if self.sample_complete else "UPPER_BOUND_ON_TRUST"

    @property
    def requires_out_of_band(self) -> bool:
        """هل يكفى المحضرُ وحدَه دليلَ ضمان؟ أيُّ انتحالٍ مُقاس ⇒ لا."""
        return self.spoof_rate > 0.0


def transcript_evidence_share(spoofing: TranscriptSpoofing) -> dict[str, object]:
    """يُخرج الخصم مع اتجاهه ووسمه — ⛔ لا يُقتطع رقمٌ منها (قاعدة AHW)."""
    return {
        "spoof_rate": spoofing.spoof_rate,
        "trust_ceiling": spoofing.trust_ceiling,
        "bound_direction": spoofing.bound_direction,
        "sample_complete": spoofing.sample_complete,
        "requires_out_of_band_evidence": spoofing.requires_out_of_band,
        "adversary_is_the_monitored": True,
        "source": spoofing.source,
    }


def adversary_is_self(spoofing: TranscriptSpoofing) -> bool:
    """هل الخصمُ هو المراقَب؟ في حادثتنا نعم — وهذا أشدّ من مهاجمٍ خارجي.

    الجملةُ القابلة للدحض: أيُّ تصميمِ رصدٍ يفترض أنّ المُسجِّل محايدٌ يسقط حين يكون
    المُسجِّل هو الطرفُ الذي يملك حافزاً وقدرةً على تعديل سجلّه.
    """
    return spoofing.requires_out_of_band


# ── 4) HAD — دلتا الاطمئنان بالحزام + قاعدةُ الإخفاق الآمن ────────────────────


@dataclass(frozen=True)
class HarnessDelta:
    """دلتا الحزام: كم ضعفاً يهبط السلوكُ الخطر بحزام الإنتاج؟ حدٌّ أدنى لا نقطة."""

    at_least_factor: float
    harness: str
    model: str
    source: str

    def __post_init__(self) -> None:
        if self.at_least_factor <= 1.0:
            raise DecisionLatencyError(
                f"عاملٌ ≤ 1 ليس دلتا حماية، لا {self.at_least_factor}"
            )
        if not self.harness.strip() or not self.model.strip():
            raise DecisionLatencyError(
                "⛔ دلتا بلا اسم الحزام والنموذج معاً: الرقمُ ملكُ الزوج لا المكوّن"
            )
        if not self.source.strip():
            raise DecisionLatencyError("دلتا بلا مصدر")

    @property
    def pair_stated(self) -> bool:
        """هل صُرِّح بالزوج؟ — الحارسُ الذي يمنع «النموذج آمن» من رقمٍ عن الحزام."""
        return bool(self.harness.strip() and self.model.strip())


def assurance_requires_pair(delta: HarnessDelta) -> bool:
    """لا يُقبل ادّعاءُ اطمئنانٍ عن مكوّنٍ منفرد. تُرجع `True` حين الزوجُ مُصرَّح."""
    return delta.pair_stated


def lead_time_days(alert_lead_hours_at_least: float) -> float:
    """قيمةُ الرصد بالأيام: كم يوماً قبل الاختراق كان الإنذار سيصل؟"""
    if alert_lead_hours_at_least < 0:
        raise DecisionLatencyError("زمنُ سبقٍ سالب")
    return alert_lead_hours_at_least / 24.0


@dataclass(frozen=True)
class EscalationPolicy:
    """سياسةُ التصعيد: ما الافتراضُ عند الصمت؟ — الاتجاهُ هو المنتج، لا المدة."""

    decide_within_minutes: float
    default_on_silence: str
    source: str

    def __post_init__(self) -> None:
        if self.decide_within_minutes <= 0:
            raise DecisionLatencyError("مهلةٌ غير موجبة")
        if self.default_on_silence not in {"PAUSE", "CONTINUE"}:
            raise DecisionLatencyError(
                f"افتراضٌ غير مُعرَّف: {self.default_on_silence!r} — يجب PAUSE أو CONTINUE"
            )
        if not self.source.strip():
            raise DecisionLatencyError("سياسةٌ بلا مصدر — لا تُقتبس مهلةً تعاقدية")

    @property
    def failsafe(self) -> bool:
        """الإخفاقُ الآمن = الصمتُ يُوقف. `CONTINUE` عند الصمت ليس سياسةً آمنة."""
        return self.default_on_silence == "PAUSE"


def failsafe_gap(policy: EscalationPolicy) -> dict[str, object]:
    """يُسمّي الخللَ البنيوي في سياسةٍ غير آمنة بدلَ أن يُجمّله."""
    return {
        "decide_within_minutes": policy.decide_within_minutes,
        "default_on_silence": policy.default_on_silence,
        "failsafe": policy.failsafe,
        "source": policy.source,
        "defect": None
        if policy.failsafe
        else "الصمتُ يُفسَّر إذناً — وهو بالضبط ما حدث حين قرّر المناوب ألّا يوقف التشغيل",
    }


# ── 5) ZRW — عملٌ بلا مكافأة + تباعدُ مواصفة المُقيِّم ───────────────────────


@dataclass(frozen=True)
class RewardOutcome:
    """حصيلةُ الجهد: كم إجراءً مقابل كم كسبٍ في الهدف المُعلن؟"""

    actions: int
    objective_gain: float
    objective_name: str
    source: str

    def __post_init__(self) -> None:
        if self.actions <= 0:
            raise DecisionLatencyError("صفرُ إجراءٍ ليس جهداً")
        if self.objective_gain < 0:
            raise DecisionLatencyError("كسبٌ سالب")
        if not self.objective_name.strip():
            raise DecisionLatencyError("هدفٌ بلا اسم — لا يُفحص تباعده")

    @property
    def wasted(self) -> bool:
        """هل بُذل الجهدُ كلّه بلا كسب؟ — الحالةُ المقيسة في حادثتنا."""
        return self.objective_gain == 0.0

    @property
    def actions_per_unit_gain(self) -> float | None:
        """⛔ لا يُصفَّر: القسمةُ على صفر كسبٍ تُرجَع `None` لا `inf` ولا `0`."""
        if self.wasted:
            return None
        return self.actions / self.objective_gain


def unsolvable_concentration(
    unsolvable_tasks: int, total_tasks: int, chatter_share: float
) -> dict[str, float]:
    """تركّزُ الحديث السرّي في المهامّ غير القابلة للحل.

    نسبةُ التركيز = حصّةُ الحديث ÷ حصّةُ المهامّ. >1 يعني أنّ الخطر تركّز في
    المستحيل: **المُحرِّك السببي هو استحالةُ المهمة، لا خبثُ النموذج**.
    """
    if total_tasks <= 0 or unsolvable_tasks < 0:
        raise DecisionLatencyError("عدُّ مهامٍّ غير صالح")
    if unsolvable_tasks > total_tasks:
        raise DecisionLatencyError("غيرُ قابلٍ للحلّ أكثرُ من الكلّ — تعريفٌ متناقض")
    if not 0.0 <= chatter_share <= 1.0:
        raise DecisionLatencyError(f"حصّةُ حديثٍ خارج [0,1]: {chatter_share}")
    base = unsolvable_tasks / total_tasks
    if base == 0:
        raise DecisionLatencyError(
            "صفرُ مهمةٍ غير قابلة للحلّ ⇒ لا تركّزَ يُقاس؛ المسألةُ مسألةُ مهامٍّ لا استحالة"
        )
    return {
        "unsolvable_share": base,
        "chatter_share": chatter_share,
        "concentration_ratio": chatter_share / base,
    }


def grader_spec_divergence(
    documented_checks: frozenset[str], deployed_checks: frozenset[str]
) -> dict[str, object]:
    """تباعدُ مواصفة المُقيِّم: ما هو مُوثَّقٌ أمام الوكيل مقابل ما يُنفَّذ فعلاً.

    هذا هو **جذرُ الحادث** عند التقرير المستقلّ: الوكيلُ قرأ الورقةَ والمستودع، فرأى
    شرطَين، بينما المنفَّذ شرطٌ واحد — فبذل حملةً كاملةً لشرطٍ لا وجود له.
    """
    if not documented_checks:
        raise DecisionLatencyError("مواصفةٌ مُوثَّقة فارغة — لا شيء ليُقابَل")
    phantom = documented_checks - deployed_checks
    undeclared = deployed_checks - documented_checks
    return {
        "documented_only": sorted(phantom),
        "deployed_only": sorted(undeclared),
        "divergent": bool(phantom or undeclared),
        "phantom_requirements": len(phantom),
        "reading": (
            "الوكيلُ يُحسِّن ضدّ مواصفةٍ منشورة لا تُنفَّذ ⇒ الجهدُ يُبذل بلا كسب،"
            " والمخاطرةُ تقع على طرفٍ ثالث لم يوقّع على تلك المواصفة"
            if phantom
            else "لا شرطَ شبحيّاً؛ التباعدُ في الاتجاه الآخر (شرطٌ مُنفَّذ بلا توثيق)"
            if undeclared
            else "لا تباعد — المواصفةُ والمنفَّذ متطابقان"
        ),
    }


# ── 6) MSDI/RBI — خصمان على أدلّة السوق ──────────────────────────────────────


@dataclass(frozen=True)
class MarketEstimate:
    """تقديرٌ منشور لحجم سوق، باسمٍ ومصدرٍ وسنةِ أساس — لأنّ الاسمَ جزءٌ من القياس."""

    market_name: str
    base_year: int
    value_usd: float
    source: str
    as_of: date

    def __post_init__(self) -> None:
        if self.value_usd <= 0:
            raise DecisionLatencyError(f"حجمٌ غير موجب: {self.value_usd}")
        if not self.market_name.strip():
            raise DecisionLatencyError("سوقٌ بلا اسم — لا يُقارن بما لا يُسمّى")
        if not self.source.strip():
            raise DecisionLatencyError("تقديرٌ بلا مصدر")


def market_dispersion(estimates: tuple[MarketEstimate, ...]) -> dict[str, object]:
    """تشتّتُ تقديرات **الكمية المُسمّاة نفسها** في **سنة الأساس نفسها**.

    ⛔ لا يُدمج اسمان («securing AI» ≠ «AI agent security»): المحرّك §8 يمنع
    المتوسّط بين وقائع غير قابلة للمقارنة. أيُّ تقديرٍ خارج الاسم/السنة يُستبعد
    ويُبلَّغ عنه في `excluded` بدلَ أن يُبتلع صمتاً.
    """
    if len(estimates) < MIN_MARKET_ESTIMATES:
        raise DecisionLatencyError(
            f"تقديرٌ واحد ليس تشتّتاً (الحدّ الأدنى {MIN_MARKET_ESTIMATES})"
        )
    names = {(e.market_name.strip().lower(), e.base_year) for e in estimates}
    if len(names) != 1:
        raise DecisionLatencyError(
            f"⛔ المقارنة عبر أسماء/سنواتٍ مختلفة: {sorted(names)} — لا تشتّتَ بين كمّيتين"
        )
    values = sorted(e.value_usd for e in estimates)
    ratio = values[-1] / values[0]
    contradictions = _self_contradictions(estimates)
    return {
        "market_name": estimates[0].market_name,
        "base_year": estimates[0].base_year,
        "n_estimates": len(estimates),
        "min_usd": values[0],
        "max_usd": values[-1],
        "dispersion_ratio": ratio,
        "same_source_self_contradictions": contradictions,
        "sources": sorted({e.source for e in estimates}),
    }


def _self_contradictions(estimates: tuple[MarketEstimate, ...]) -> list[dict[str, object]]:
    """مصدرٌ واحد يُبلّغ قيمتَين للكمية نفسها — يُسمّى لا يُتجاهل."""
    by_source: dict[str, list[float]] = {}
    for e in estimates:
        by_source.setdefault(e.source, []).append(e.value_usd)
    out: list[dict[str, object]] = []
    for src, vals in sorted(by_source.items()):
        if len(set(vals)) > 1:
            out.append({"source": src, "values_usd": sorted(vals), "spread_ratio": max(vals) / min(vals)})
    return out


def dispersion_is_decision_grade(dispersion_ratio: float, decision_gap_ratio: float) -> bool:
    """هل يستطيع الرقمُ أن يُرتّب بديلَين؟ — العتبةُ **فجوةُ القرار** لا ثابتٌ مطلق.

    إن كان التشتّتُ أوسعَ من الفجوة بين البديلَين، فالرقمُ لا يميّزهما: أيُّ ترتيبٍ
    يُبنى عليه انقلابٌ محتمل بمجرد اختيار مصدرٍ آخر.
    """
    if dispersion_ratio < 1.0:
        raise DecisionLatencyError(f"تشتّتٌ < 1 مستحيلٌ بحساب الحدّ الأقصى/الأدنى: {dispersion_ratio}")
    if decision_gap_ratio <= 1.0:
        raise DecisionLatencyError(
            f"فجوةُ قرار ≤ 1 ليست فجوة: {decision_gap_ratio} — البديلان متطابقان فلا قرار"
        )
    return dispersion_ratio < decision_gap_ratio


@dataclass(frozen=True)
class RateAnchor:
    """مرساةُ أجرٍ بنوعِ قياسها — لأنّ «مُبلَّغاً ذاتياً» ليس «مُعلَناً» ليس «محقَّقاً»."""

    label: str
    usd_per_hour: float
    measurement_kind: str  # SELF_REPORTED_ASKED | POSTING_DERIVED_OFFERED | REALIZED_INVOICED
    source: str
    as_of: date

    def __post_init__(self) -> None:
        if self.usd_per_hour <= 0:
            raise DecisionLatencyError(f"أجرٌ غير موجب: {self.usd_per_hour}")
        allowed = {"SELF_REPORTED_ASKED", "POSTING_DERIVED_OFFERED", "REALIZED_INVOICED"}
        if self.measurement_kind not in allowed:
            raise DecisionLatencyError(
                f"نوعُ قياسٍ خارج المجموعة {sorted(allowed)}: {self.measurement_kind!r}"
            )


def rate_bias(anchors: tuple[RateAnchor, ...]) -> dict[str, object]:
    """انحيازُ الأجر بين أنواع القياس، مع **اتّجاهه** — لا متوسّطَ بينهما.

    ⛔ لا يُؤخذ متوسّط: مُتوسّطُ «مطلوب» و«مُعلَن» ليس «محقَّقاً». ما يُخرج هو
    نطاقٌ واتّجاهُ انحيازٍ ووسمُ `REALIZED_INVOICED` إن وُجد، وإلّا فالحالة مجهولة.
    """
    if len(anchors) < MIN_MARKET_ESTIMATES:
        raise DecisionLatencyError("مرساةٌ واحدة لا تُنتج انحيازاً")
    values = sorted(a.usd_per_hour for a in anchors)
    realized = [a for a in anchors if a.measurement_kind == "REALIZED_INVOICED"]
    asked = [a for a in anchors if a.measurement_kind == "SELF_REPORTED_ASKED"]
    offered = [a for a in anchors if a.measurement_kind == "POSTING_DERIVED_OFFERED"]
    bias = None
    if asked and offered:
        bias = max(a.usd_per_hour for a in asked) / min(o.usd_per_hour for o in offered)
    return {
        "band_usd_per_hour": [values[0], values[-1]],
        "self_report_bias_factor": bias,
        "bias_direction": (
            "SELF_REPORT_HIGHER" if bias and bias > 1.0 else "FLAT_OR_LOWER" if bias else "UNMEASURED"
        ),
        "realized_anchor_present": bool(realized),
        "planning_rule": (
            "⛔ لا يُخطَّط على الأعلى؛ يُخطَّط على الأدنى حتى توجد مرساةُ REALIZED_INVOICED"
            if not realized
            else "توجد مرساةُ فاتورةٍ محقَّقة — تُستعمل هي وحدها للتخطيط"
        ),
        "n_anchors": len(anchors),
    }


# ── 7) عبثيةُ قائمة الحجب + فصلُ الضرر عن كلفة الاستجابة ─────────────────────


def blocklist_yield(n_transports: int, blocked: int, envelope_invariant: bool) -> float:
    """كم يُخفض حجبُ `blocked` قناةً من قدرة التواصل؟

    إن كان الغلافُ البروتوكولي ثابتاً عبر القنوات (وهو مقيسٌ في الحادث: «closing any one
    channel did not break communication»)، فحجبُ **أيّ عددٍ دون الكلّ** ⇒ صفرُ أثر.
    هذه ليست استعارة: إنها جملةٌ حتمية عن بنيةٍ مُقاسة.
    """
    if n_transports <= 0:
        raise DecisionLatencyError("صفرُ قناةٍ — لا شيء ليُحجب")
    if not 0 <= blocked <= n_transports:
        raise DecisionLatencyError(f"محجوبٌ ({blocked}) خارج نطاق القنوات ({n_transports})")
    if envelope_invariant and blocked < n_transports:
        return 0.0
    if envelope_invariant:
        return 1.0
    return blocked / n_transports


@dataclass(frozen=True)
class LossSplit:
    """فصلُ الضرر المؤكَّد عن كلفة الاستجابة — لأنّ ما يُؤمَّن عليه ليس ما يُدفع.

    ⚠️ «ضررٌ مؤكَّد» وحده لا يُنتج خسارةً قابلةً للتأمين: يلزم أن يقع الضررُ على **أصلٍ
    محميٍّ عائدٍ لطرفٍ ثالث** (بيانات عميل/شريك). وإلّا فالخسارةُ الواقعية هي كلفةُ
    الاستجابة، وهي منتجٌ مختلفٌ بمشتريٍ مختلف (CFO/CISO لا وكيلُ تأمين).
    """

    confirmed_damage_items: tuple[str, ...]
    response_cost_items: tuple[str, ...]
    controls_that_held: tuple[str, ...]
    third_party_protected_asset_affected: bool
    third_party_source: str

    def __post_init__(self) -> None:
        if not self.response_cost_items and not self.confirmed_damage_items:
            raise DecisionLatencyError(
                "لا ضررَ ولا كلفةَ استجابة — ⛔ لا يُقرأ الغيابُ «حادثاً بلا أثر»"
            )
        if self.third_party_protected_asset_affected and not self.confirmed_damage_items:
            raise DecisionLatencyError(
                "إصابةُ أصلِ طرفٍ ثالث بلا بند ضررٍ مُسمّى — ادّعاءٌ بلا مفردة"
            )
        if not self.third_party_source.strip():
            raise DecisionLatencyError("حكمٌ على أصلِ طرفٍ ثالث بلا مصدر")

    @property
    def damage_confirmed(self) -> bool:
        return bool(self.confirmed_damage_items)

    @property
    def insurable_loss_present(self) -> bool:
        """هل توجد خسارةٌ من النوع الذي تُؤمَّن؟ ضررٌ داخليٌّ وحدَه لا يكفي."""
        return self.damage_confirmed and self.third_party_protected_asset_affected

    @property
    def sellable_unit(self) -> str:
        """وحدةُ البيع التي يبرّرها الدليل، لا التي تُشتهى."""
        if self.insurable_loss_present:
            return "LOSS_INDEMNITY_OR_PREVENTION"
        if self.response_cost_items:
            return "RESPONSE_COST_REDUCTION"
        return "UNMEASURED"


def controls_held_share(split: LossSplit) -> float | None:
    """حصّةُ الضوابط التي صمدت — ⛔ لا تُقرأ «صفر ضرر» كـ«صفر خطر»."""
    total = len(split.controls_that_held) + len(split.confirmed_damage_items)
    if total == 0:
        return None
    return len(split.controls_that_held) / total


# ── 8) الملخّص الهندسي (بلا لغةٍ بيعية) ─────────────────────────────────────


def summarize(
    split: LatencySplit,
    machine: MachineTempo,
    human: HumanDecisionCycle,
    spoofing: TranscriptSpoofing,
    delta: HarnessDelta,
    policy: EscalationPolicy,
    reward: RewardOutcome,
    concentration: dict[str, float],
    divergence: dict[str, object],
    dispersion: dict[str, object],
    decision_gap_ratio: float,
    bias: dict[str, object],
    transports: int,
    blocked: int,
    losses: LossSplit,
) -> dict[str, object]:
    """يُخرج حقولَ القرار فقط — لا صفةَ تسويق ولا رقماً بلا وسم."""
    return {
        "binding_layer": split.binding_layer,
        "open_gaps": split.open_gaps_count,
        "operator_binding_layer": split.party_binding_layer("OPERATOR"),
        "defender_binding_layer": split.party_binding_layer("DEFENDER"),
        "technical_days": split.technical_days,
        "organizational_days": split.organizational_days,
        "organizational_to_technical_ratio": split.organizational_to_technical_ratio,
        "decision_to_detection_ratio": split.decision_to_detection_ratio,
        "machine_actions_per_day": machine.actions_per_day,
        "machine_actions_per_hour": machine.actions_per_hour,
        "tempo_ratio_actions_per_human_decision": tempo_ratio(machine, human),
        "projected_volume_outside_measurement_window": projected_volume(
            machine, human.over_days
        ),
        "transcript_trust_ceiling": spoofing.trust_ceiling,
        "transcript_bound_direction": spoofing.bound_direction,
        "requires_out_of_band_evidence": spoofing.requires_out_of_band,
        "adversary_is_the_monitored": adversary_is_self(spoofing),
        "harness_delta_at_least": delta.at_least_factor,
        "harness_pair_stated": assurance_requires_pair(delta),
        "failsafe": policy.failsafe,
        "reward_wasted": reward.wasted,
        "actions_per_unit_gain": reward.actions_per_unit_gain,
        "unsolvable_concentration_ratio": concentration["concentration_ratio"],
        "grader_divergent": divergence["divergent"],
        "phantom_requirements": divergence["phantom_requirements"],
        "market_dispersion_ratio": dispersion["dispersion_ratio"],
        "market_number_is_decision_grade": dispersion_is_decision_grade(
            float(dispersion["dispersion_ratio"]), decision_gap_ratio
        ),
        "self_report_bias_factor": bias["self_report_bias_factor"],
        "blocklist_yield_of_partial_block": blocklist_yield(transports, blocked, True),
        "sellable_unit": losses.sellable_unit,
        "controls_held_share": controls_held_share(losses),
    }
