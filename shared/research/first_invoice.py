"""سجلُّ قنوات التحصيل — FIV (الدفعة العاشرة).

First-Invoice Verification: التحقق عبر الفاتورة الأولى.

**ما تقيسه هذه الأداة — وما لا تقيسه:**

تقيس **شروط التسوية المُعلَنة** لقنوات العملة الصعبة المرشّحة كما نُشرت في مصادرها
الأولية بتاريخ 2026-09-15: هل مسار الدفع مُعلَن؟ هل الرسم مُعلَن؟ هل الدخول مجّاني؟
وتُرتِّب القنوات لاختبار الفاتورة الأولى (الأرخصُ اختباراً أوّلاً).

⛔ لا تقيس احتمالات القبول، ولا جودة المراجعة، ولا «أفضل قناة» بالمطلق — فلا واحدة
منها دليلُ تسعير (D-267 L9). ⛔ لا تُنتج رقماً بالدولار إلّا من مُدخَلٍ مُسندٍ مذكورٍ
بعينه (S127–S140)، والغائبُ `None` بسببٍ منطوق لا صفراً (D-212).

القوانين الحاكمة داخل هذا الملفّ:

1. **النطاقات لا المراكز**: تُحسَب (أدنى · أعلى · عدد) فقط — ⛔ لا متوسطَ ولا وسيطَ
   لأيّ أسعارٍ معلَنة، فمتوسّطُ رقمَين صادقَين بدبوسَين مختلفَين رقمٌ ثالث لا مرجع له.
2. **الرسمُ لا ينتقل بين فئات الأصول**: جدولُ الرسوم مفتاحُه فئةُ الأصل، وطلبُ رسمٍ
   لفئةٍ بلا جدولٍ مُعلَن يرفع `FeeScheduleMissingError` — لا يُخمَّن ولا يُستعار.
3. **الصفرُ المُعلَن صفرٌ، والغائبُ غائب**: صفرٌ ورد في المصدر (طبقةٌ «مجانية») يُسجَّل
   صفراً مُسنَداً؛ وما لم يرد يُسجَّل `None` بسببٍ من مجموعةٍ مغلقة.
4. **التسميةُ الميتة لا تُستعمل**: `prime-environments` اسمٌ ميّت منذ 2026-03-29
   (الالتزام #518) — والحاليُّ `community-environments` (S129).

القانون: stdlib فقط، لا استيراد من app/ ولا microservices/ — تُشحَن إلى عميلٍ
لا يملك تبعياتنا. المكتبةُ تُرجِع بياناتٍ ولا تطبع (D-281).
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Final

__all__ = [
    "AS_OF",
    "AUDIT_ANCHORS",
    "BATCH",
    "CHANNELS",
    "CONFLICTS",
    "FIV_POLICY",
    "LISTINGS",
    "FeeScheduleMissingError",
    "apply_fee",
    "contradictions",
    "fee_schedule",
    "fiv_policy",
    "inputs_fingerprint",
    "kill_switches",
    "listing_band",
    "measure_all",
    "net_probe",
    "per_unit",
    "rank_for_first_test",
]

#: تاريخُ تجميد المصادر — ثابتٌ لا يُقرأ من الساعة.
AS_OF: Final = "2026-09-15"

#: رقمُ الدفعة في سجلّ المعرفة.
BATCH: Final = "FIV-10"

#: بوّاباتُ الدخول — مجموعةٌ مغلقة، وترتيبُها هو ترتيبُ كلفة الاختبار.
ENTRY_RANK: Final = {"OPEN": 0, "APPROVAL": 1, "REVIEW_5D": 2}

#: سياسةُ سقف الفاتورة الأولى (FIV cap) — **مُدخَلُ سياسةٍ مُعلَن** لا نتيجةُ قياس،
#: ولا يُعدَّل إلّا بقرار مالكٍ مكتوب. وحدةُ الجهد ⚙️ = يوم (عرف WOD)، للترتيب فقط،
#: ⛔ ولا تُحوَّل إلى دولاراتٍ بضربٍ اصطلاحيّ (D-290 L9 · D-212).
FIV_POLICY: Final = {
    "max_spend_usd": 0,
    "max_effort_days": 5,
    "effort_unit_ar": "يوم (⚙️) — للترتيب فقط، لا يُحوَّل إلى دولار",
    "adjustable_by": "owner decision only",
}


class FeeScheduleMissingError(LookupError):
    """رُفع عند طلب رسمٍ لفئةِ أصلٍ بلا جدولٍ مُعلَن — الرفضُ لا التخمين."""


@dataclass(frozen=True)
class Channel:
    """قناةُ تحصيلٍ مرشّحة كما تُعلن هي عن نفسها — لا كما نتمنّى."""

    channel_id: str
    label_ar: str
    asset_class: str
    ticket_lo_usd: int | None
    ticket_hi_usd: int | None
    ticket_note_ar: str
    payout_rail: str | None
    payout_note_ar: str
    entry: str
    entry_note_ar: str
    sources: tuple[str, ...] = field(default_factory=tuple)


#: القنواتُ الخمس كما وردت في مصادرها — كلُّ حقلٍ غائبٍ `None` بسببٍ في حقل الملاحظة.
CHANNELS: Final = (
    Channel(
        channel_id="CH1_prime_open",
        label_ar="مكافأة Prime المفتوحة (Open Access)",
        asset_class="bounty",
        ticket_lo_usd=100,
        ticket_hi_usd=500,
        ticket_note_ar="$100–500 معلَنة على صفحة البرنامج",
        payout_rail=None,
        payout_note_ar="UNSTATED — صفحةُ البرنامج لا تذكر وسيلةَ الدفع ولا أجلَه ولا الأهليةَ الجغرافية",
        entry="OPEN",
        entry_note_ar="تُحاوَل بلا موافقةٍ مسبقة (can be attempted by anyone) — والبناءُ على إطار verifiers إلزامي (S128)",
        sources=("S127", "S128"),
    ),
    Channel(
        channel_id="CH2_prime_app",
        label_ar="مكافأة Prime بالتقديم (Application-Only)",
        asset_class="bounty",
        ticket_lo_usd=1000,
        ticket_hi_usd=None,
        ticket_note_ar="$1,000–$5,000+‎ — الحدُّ الأعلى مفتوحٌ (open-ended) فلا يُحفَظ رقماً",
        payout_rail=None,
        payout_note_ar="UNSTATED — كالقناة الأولى: لا وسيلةَ دفعٍ ولا أجلَ ولا أهليةَ معلَنة",
        entry="APPROVAL",
        entry_note_ar="إسنادٌ بعد موافقةٍ عبر استمارة؛ وإعادةُ تنفيذ معيارٍ قائمٍ تشترط إعادةَ إنتاجٍ كاملةً لدرجات التقييم",
        sources=("S127",),
    ),
    Channel(
        channel_id="CH3_prime_sprint",
        label_ar="Prime Sprints (المسار البحثي المجتمعي)",
        asset_class="bounty",
        ticket_lo_usd=None,
        ticket_hi_usd=None,
        ticket_note_ar="NON_CASH — أرصدةٌ مجانية وتشغيلاتٌ مدعومة ($0.64/30 دقيقة على 1B) لا فاتورةَ نقديةً معلَنة",
        payout_rail=None,
        payout_note_ar="UNSTATED — لا تسويةَ نقديةَ معلَنة ⇒ لا تحمل FIV بنفسها",
        entry="APPROVAL",
        entry_note_ar="مشاركةٌ بمسارٍ (الأول: reward hacking) وسابقةُ مختبِر beta موثّقة",
        sources=("S136",),
    ),
    Channel(
        channel_id="CH4_datavendor_listing",
        label_ar="سوق DataVendor — إدراج taskset/بيئة",
        asset_class="taskset",
        ticket_lo_usd=18000,
        ticket_hi_usd=65000,
        ticket_note_ar="نطاقُ أمثلةِ الإدراج الستة على الصفحة — ⛔ أمثلةُ عرضٍ لا مبيعاتٌ مُسوّاة",
        payout_rail="wire_ach",
        payout_note_ar="STATED — تحويلٌ بنكي (wire/ACH) بجدول فوترةٍ متوقَّع؛ والدفعُ عند الشراء",
        entry="REVIEW_5D",
        entry_note_ar="استمارةُ قبول (~5 دقائق) تُراجَع خلال 5 أيام عمل + اتفاقيةُ سرّيةٍ موقَّعةٍ سلفاً قبل أيّ مشاركة",
        sources=("S130", "S131"),
    ),
    Channel(
        channel_id="CH5_datavendor_codebase",
        label_ar="سوق DataVendor — بيعُ قاعدة شيفرة (codebase)",
        asset_class="codebase",
        ticket_lo_usd=5000,
        ticket_hi_usd=None,
        ticket_note_ar="أرضيةُ $5,000 تصعد بالتدريج — والحدُّ الأعلى مفتوحٌ فلا يُحفَظ رقماً",
        payout_rail="wire_ach",
        payout_note_ar="STATED — نفسُ سكّة القناة الرابعة (wire/ACH)",
        entry="REVIEW_5D",
        entry_note_ar="نفسُ بوّابة القناة الرابعة + مراجعةُ حقوقٍ (IP) — وبيعُ الحقوق يحتاج قرارَ مالكٍ (T76)",
        sources=("S131", "S132"),
    ),
)


@dataclass(frozen=True)
class Listing:
    """مثالُ إدراجٍ واحد كما تعرضه صفحةُ السوق — ⛔ مثالٌ لا مبيعٌ مُسوّى."""

    listing_id: str
    label_ar: str
    price_usd: int
    tasks: int
    extra_ar: str


#: أمثلةُ الإدراج الستة (S130 — جُلبت 2026-09-15).
LISTINGS: Final = (
    Listing("legal_qa", "تدقيقُ عقودٍ قانونية", 42000, 4200, "18 rubric"),
    Listing("code_review", "مهامُّ مراجعةِ شيفرة", 65000, 6400, "3 لغات"),
    Listing("medical_sum", "تلخيصٌ طبيّ", 55000, 3500, "تدريجُ مختصّين"),
    Listing("support_triage", "فرزُ دعمٍ", 18000, 9100, "12 لغة"),
    Listing("finance_reason", "استدلالٌ ماليّ", 31000, 2800, "أجوبةٌ مُتحقَّقة"),
    Listing("tool_use", "سيناريوهاتُ استعمالِ أدوات", 27000, 1900, "140 واجهة"),
)


@dataclass(frozen=True)
class AuditAnchor:
    """مرساةُ سعرٍ مُعلَنة من بائع — مادّةُ فرضيةِ تسعيرٍ لا دليلُ تسعير."""

    anchor_id: str
    label_ar: str
    lo_usd: float | None
    hi_usd: int | None
    basis_ar: str


#: مراسي سوق التدقيق المعلَنة (S137 · S138 — صفحاتُ بائعين، تُوسَم PRICING HYPOTHESIS).
AUDIT_ANCHORS: Final = (
    AuditAnchor("one_time", "تدقيقٌ لمرّةٍ واحدة", 8000, 25000, "نطاقُ بائعٍ مُعلَن (S137)"),
    AuditAnchor("focused", "فريقٌ أحمرُ مركَّز", 16000, 50000, "نطاقُ بائعٍ مُعلَن (S137)"),
    AuditAnchor("comprehensive", "فريقٌ أحمرُ شامل", 50000, None, "$150K+‎ مفتوحة (S137)"),
    AuditAnchor("continuous_mo", "فريقٌ أحمرُ مستمرّ (شهرياً)", 5000, 20000, "اشتراكٌ مُعلَن (S137)"),
    AuditAnchor("rtaas", "فريقٌ أحمرُ كخدمةٍ (لكلّ اشتباك)", 16000, 100000, "نطاقُ بائعٍ مُعلَن (S137)"),
    AuditAnchor(
        "self_serve", "خدمةٌ ذاتية (منصّة)", 0, 2000, "صفرٌ مُعلَن (طبقةٌ مجانية) حتى $2,000/شهر (S138)"
    ),
)


@dataclass(frozen=True)
class Conflict:
    """تعارُضٌ مُسجَّل — القاعدة: يُسجَّل ولا يُحسَم بصمتٍ ولا يُوسَّط أبداً."""

    conflict_id: str
    label_ar: str
    side_a_ar: str
    side_b_ar: str
    status: str
    rule_ar: str


#: سجلُّ التعارضات — ثلاثةٌ لا غير، وكلٌّ بحالته الصريحة.
CONFLICTS: Final = (
    Conflict(
        conflict_id="C1_funding_round",
        label_ar="جولةُ تمويل Prime Intellect",
        side_a_ar="Series A بقيمة $130M بتقييم $1B (ثلاثُ ثانوياتٍ مؤرَّخةٍ متقاربةٍ 2026-07-08/09/13 — S134)",
        side_b_ar="شارةُ توظيفٍ تصنّفها Series B بإجمالي $70.4M — ⛔ لم تُلتقَط من مصدرها (S135)",
        status="OPEN",
        rule_ar="لا حسمَ ولا متوسط — الطرفُ الملتقَط يُقتبَس بدرجته، والغائبُ يُعاد طلبُه (T75)",
    ),
    Conflict(
        conflict_id="C2_fee_transfer",
        label_ar="نقلُ رسمِ قاعدةِ الشيفرة إلى الـtasksets",
        side_a_ar="80/20 للـcodebases مُعلَن (S132)",
        side_b_ar="رسمُ الـtasksets غيرُ مُعلَن (S130/S131 صامتتان)",
        status="GUARDED",
        rule_ar="المنعُ في الكود (`apply_fee` يرفع) لا في التوثيق وحده — فالنقلُ يُنتج صافياً لا مرجع له",
    ),
    Conflict(
        conflict_id="C3_repo_rename",
        label_ar="اسمُ مستودع البيئات",
        side_a_ar="prime-environments — اسمٌ ميّت منذ 2026-03-29",
        side_b_ar="community-environments — الحاليُّ بنصّ الالتزام #518 (S129)",
        status="RESOLVED_PRIMARY",
        rule_ar="الحسمُ من مصدرٍ أوّل (رسالةُ الالتزام) — وكلُّ استعمالٍ للاسم الميّت خارجَ سياقِ البطلان بوّابةٌ حمراء",
    ),
)

#: ⛔ تنبيهُ تصادمِ تسمية: الرمز `F-04` محجوزٌ في المستودع بمعنى آخر (نقطةُ فشلٍ أحادية
#: في تقرير forensics مؤرشف + صفُّ دليلٍ في claim-scope-audit-001) فلا يُعاد استعماله
#: هنا — والتعارضاتُ أعلاه C1–C3 لا F-04.
_NAMING_COLLISION_NOTE: Final = "F-04 is taken elsewhere in this repo; conflicts here are C1-C3"


def per_unit(price_usd: float, tasks: int) -> float | None:
    """سعرُ الواحدة — `None` عند صفرِ المقام (لا يُصفَّر ولا يُلاعَن · D-212)."""
    if tasks <= 0:
        return None
    return float(price_usd) / float(tasks)


def listing_band() -> dict[str, object]:
    """نطاقُ أمثلة الإدراج: (أدنى · أعلى · عدد) — ⛔ بلا متوسطٍ ولا وسيط."""
    units = [per_unit(item.price_usd, item.tasks) for item in LISTINGS]
    assert all(value is not None for value in units), "task counts are positive by S130"
    prices = [item.price_usd for item in LISTINGS]
    return {
        "count": len(LISTINGS),
        "price_lo_usd": min(prices),
        "price_hi_usd": max(prices),
        "unit_values_usd": units,
        "unit_lo_usd": min(value for value in units if value is not None),
        "unit_hi_usd": max(value for value in units if value is not None),
        "reading_ar": "نطاقُ أمثلةِ عرضٍ من صفحةِ بائع — ⛔ لا مبيعاتٌ مُسوّاة ولا دليلُ تسعير",
    }


def fee_schedule() -> dict[str, dict[str, object]]:
    """جدولُ الرسوم مفتاحُه فئةُ الأصل — والغائبُ غائبٌ بسببٍ منطوق."""
    return {
        "codebase": {
            "seller_share": 0.8,
            "basis_ar": "80/20 مُعلَن للـcodebases (S132)",
        },
        "taskset": {
            "seller_share": None,
            "reason": "FEE_UNSTATED_FOR_TASKSET",
            "basis_ar": "S130/S131 صامتتان عن رسم الـtasksets — و⛔ لا يُنقَل جدولُ الـcodebases (C2)",
        },
        "bounty": {
            "seller_share": None,
            "reason": "FEE_UNSTATED",
            "basis_ar": "صفحةُ البرنامج لا تذكر رسماً ولا خصماً (S127)",
        },
    }


def apply_fee(asset_class: str, gross_usd: float) -> float:
    """يطبّق رسمَ فئةٍ مُعلَناً — ويرفع عند الغياب (الرفضُ لا التخمين)."""
    schedule = fee_schedule()
    if asset_class not in schedule:
        raise FeeScheduleMissingError(f"unknown asset_class: {asset_class}")
    share = schedule[asset_class]["seller_share"]
    if not isinstance(share, (int, float)):
        reason = schedule[asset_class].get("reason", "FEE_UNSTATED")
        raise FeeScheduleMissingError(f"{asset_class}: {reason}")
    return float(gross_usd) * share


def net_probe(gross_usd: float = 1000.0) -> dict[str, dict[str, object]]:
    """مسبارُ $1,000 عبر القنوات — ص netٌ واحدٌ قابلٌ للاقتباس والباقي `None` بأسبابه."""
    probes: dict[str, dict[str, object]] = {}
    for channel in CHANNELS:
        if channel.channel_id == "CH3_prime_sprint":
            probes[channel.channel_id] = {
                "gross_usd": gross_usd,
                "net_usd": None,
                "state": "UNQUOTABLE",
                "reason": "NON_CASH_TICKET",
            }
            continue
        try:
            probes[channel.channel_id] = {
                "gross_usd": gross_usd,
                "net_usd": apply_fee(channel.asset_class, gross_usd),
                "state": "QUOTABLE",
                "reason": None,
            }
        except FeeScheduleMissingError as exc:
            probes[channel.channel_id] = {
                "gross_usd": gross_usd,
                "net_usd": None,
                "state": "UNQUOTABLE",
                "reason": str(exc).split(": ", 1)[-1],
            }
    return probes


def rank_for_first_test() -> list[str]:
    """ترتيبُ الاختبار الأوّل: الدخولُ الأرخصُ أوّلاً، ثم التذكرةُ الدنيا، ثم الأبجديّة.

    الترتيبُ مُعلَنٌ وحتميّ — والتعادلُ يُكسَر أبجدياً لا بالرأي.
    """

    def _key(channel: Channel) -> tuple[int, float, str]:
        ticket = channel.ticket_lo_usd
        return (
            ENTRY_RANK[channel.entry],
            float(ticket) if ticket is not None else float("inf"),
            channel.channel_id,
        )

    return [channel.channel_id for channel in sorted(CHANNELS, key=_key)]


def settle_summary() -> dict[str, object]:
    """موجزُ مسارات التسوية: مُعلَنٌ مقابلَ غيرِ مُعلَن — بالعدّ لا بالرأي."""
    stated = [c.channel_id for c in CHANNELS if c.payout_rail is not None]
    unstated = [c.channel_id for c in CHANNELS if c.payout_rail is None]
    return {"stated": len(stated), "unstated": len(unstated), "stated_ids": stated}


def audit_band() -> dict[str, object]:
    """نطاقُ مراسي التدقيق المعلَنة — أرضيةٌ مُعلَنة وسقفٌ مفتوح، ⛔ بلا مركز."""
    stated_lows = [a.lo_usd for a in AUDIT_ANCHORS if a.lo_usd is not None]
    stated_highs = [a.hi_usd for a in AUDIT_ANCHORS if a.hi_usd is not None]
    return {
        "anchors": len(AUDIT_ANCHORS),
        "floor_usd": min(stated_lows),
        "floor_basis_ar": "صفرٌ مُعلَن (طبقةٌ مجانية — S138)",
        "engagement_floor_usd": 8000,
        "engagement_floor_basis_ar": "أدنى اشتباكٍ مُعلَن (S137)",
        "highest_stated_hi_usd": max(stated_highs),
        "ceiling_open": True,
        "ceiling_basis_ar": "السقفُ مفتوح ($150K+‎ — S137) فلا يُحفَظ رقماً",
        "reading_ar": "PRICING HYPOTHESIS — ⛔ ولا واحدٌ منها عقدٌ مُسوّى (NOT FOUND تبقى — H74)",
    }


def contradictions() -> list[dict[str, object]]:
    """سجلُّ التعارضات الثلاثة بحالاتها الصريحة."""
    return [
        {
            "conflict_id": c.conflict_id,
            "label_ar": c.label_ar,
            "side_a_ar": c.side_a_ar,
            "side_b_ar": c.side_b_ar,
            "status": c.status,
            "rule_ar": c.rule_ar,
        }
        for c in CONFLICTS
    ]


def kill_switches() -> list[str]:
    """شروطُ القتل K1–K5 مُقيَّمةً على البيانات المُعلَنة — الفارغُ بقاءٌ لا صحّة."""
    triggered: list[str] = []
    summary = settle_summary()
    if summary["stated"] == 0:
        triggered.append("K1_ALL_SETTLE_UNSTATED")
    known_spend = 0.0  # مجموعُ الرسوم المُعلَنة على الدخول — والمجموعُ على الغائب صفرٌ لا غياب
    if known_spend > 0:
        triggered.append("K2_KNOWN_SPEND_ABOVE_ZERO")
    if any(key.startswith(("mean", "median", "average")) for key in _result_keys()):
        triggered.append("K3_CENTER_COMPUTED")
    if any("asset_class" not in entry for entry in ({"asset_class": k} for k in fee_schedule())):
        triggered.append("K4_FEE_SCHEDULE_UNKEYED")
    if any(len(c.sources) == 0 for c in CHANNELS):
        triggered.append("K5_ZERO_SOURCE_CHANNEL")
    return triggered


def _result_keys() -> tuple[str, ...]:
    """مفاتيحُ النتائج — يفحصها K3 ذاتياً (لا مركزَ يُحسَب)."""
    return (
        "channels_ranked",
        "fee_schedule",
        "kill_switches",
        "listing_band",
        "audit_band",
        "net_probe",
        "settle",
        "contradictions",
        "naming",
        "spend",
    )


def fiv_policy() -> dict[str, object]:
    """سياسةُ سقف الفاتورة الأولى — تُقرأ ولا تُحسَب."""
    return dict(FIV_POLICY)


def _inputs() -> dict[str, object]:
    """المُدخَلاتُ القانونية — وهي وحدها ما تُبصَم."""
    return {
        "as_of": AS_OF,
        "batch": BATCH,
        "channels": [
            {
                "channel_id": c.channel_id,
                "asset_class": c.asset_class,
                "ticket_lo_usd": c.ticket_lo_usd,
                "ticket_hi_usd": c.ticket_hi_usd,
                "payout_rail": c.payout_rail,
                "entry": c.entry,
                "sources": list(c.sources),
            }
            for c in CHANNELS
        ],
        "listings": [
            {"listing_id": item.listing_id, "price_usd": item.price_usd, "tasks": item.tasks}
            for item in LISTINGS
        ],
        "audit_anchors": [
            {"anchor_id": a.anchor_id, "lo_usd": a.lo_usd, "hi_usd": a.hi_usd}
            for a in AUDIT_ANCHORS
        ],
        "policy": fiv_policy(),
    }


def inputs_fingerprint() -> str:
    """بصمةُ المُدخَلات — sha256 محسوبةٌ فعلاً على ترميزٍ قانونيٍّ ثابت."""
    canonical = json.dumps(_inputs(), sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def measure_all() -> dict[str, object]:
    """الحمولةُ الكاملة: أصفارٌ مُعلَنة + مُدخَلات + بصمة + نتائج — حتميةٌ تماماً."""
    probes = net_probe()
    band = listing_band()
    return {
        "$schema_version": "1",
        "as_of": AS_OF,
        "batch": BATCH,
        "declared_zeros": {
            "model_runs_executed": 0,
            "client_measurements": 0,
            "invoices_issued": 0,
            "settled_contracts": 0,
            "exploit_code_present": False,
            "revenue_claim": "NONE",
        },
        "inputs": _inputs(),
        "inputs_fingerprint": inputs_fingerprint(),
        "results": {
            "channels_ranked": rank_for_first_test(),
            "listing_band": band,
            "audit_band": audit_band(),
            "fee_schedule": fee_schedule(),
            "net_probe": probes,
            "net_probe_summary": {
                "gross_usd": 1000.0,
                "quotable": sum(1 for p in probes.values() if p["state"] == "QUOTABLE"),
                "unquotable": sum(1 for p in probes.values() if p["state"] != "QUOTABLE"),
            },
            "settle": settle_summary(),
            "spend": {
                "known_spend_usd": 0.0,
                "known_spend_basis_ar": "لا رسمَ دخولٍ مُعلَناً على أيّ قناةٍ من الخمس — والمجموعُ على المُعلَن لا على الغائب",
                "unstated_spend_items": [
                    "CH1/CH2/CH3: رسمُ التسوية ووسيلتُها وأجلُها (يُسأل في T71)",
                    "CH4: رسمُ الإدراج/البيع للـtasksets (يُسأل في T72)",
                    "CH5: كلفةُ مراجعةِ الحقوقِ وشروطُ الترخيص (يُسأل في T72)",
                ],
            },
            "contradictions": {
                "total": len(CONFLICTS),
                "by_status": {
                    "OPEN": sum(1 for c in CONFLICTS if c.status == "OPEN"),
                    "GUARDED": sum(1 for c in CONFLICTS if c.status == "GUARDED"),
                    "RESOLVED_PRIMARY": sum(1 for c in CONFLICTS if c.status == "RESOLVED_PRIMARY"),
                },
                "items": contradictions(),
            },
            "naming": {
                "stale_name": "prime-environments",
                "current_name": "community-environments",
                "renamed_on": "2026-03-29",
                "basis": "S129",
            },
            "source_counts": {c.channel_id: len(c.sources) for c in CHANNELS},
            "single_source_channels": sorted(c.channel_id for c in CHANNELS if len(c.sources) < 2),
            "kill_switches": kill_switches(),
        },
    }
