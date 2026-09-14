"""الدفعة الثامنة — WOD: انحرافُ الاستقطاع والتأهيل (Withholding–Onboarding Divergence).

## لماذا هذه الوحدة موجودة

الدفعاتُ السبع السابقة قاست **العرض**: معاملات معرفة (CDKC)، براهين قابلة للحمل (VEP)،
تباعدَ البطلان (CND)، نوافذَ الضمان (AHW)، كمونَ القرار (DLY)، سكّةَ العملة الصعبة (FXR)،
وحدودَ المُتحقِّق (VBT). وكلُّها تفترض أن الوصول إلى المشتري **واقعٌ لا متغيّر**، ولا واحدةَ
منها تقيس طبقةَ المشتري: ما يقتطعه نظامُ الضرائب في بلد المشتري، وما تفرضه حزمةُ تأهيل
المورّد عنده. هذه الوحدة تقيس الطبقةَ المفقودة وتُنتج رقماً واحداً قابلاً للمقارنة:

    الالتقاطُ الصافي = قابليةُ العبور (0/1) × (1 − الاستقطاع)

## المعرفة الجديدة في ثلاث جمل

1. **الاستقطاع يتبع بنيةَ العقد لا جودةَ العمل**: الدفعةُ نفسها، من الشركة نفسها، إلى السوق
   نفسها، تُقتطع 0% أو 30% بحسب وصفها — *خدمةٌ أُدّيت في الجزائر* مقابل *إتاوةُ ترخيصِ حقٍّ
   يُستعمل في بلد المشتري*. والوجهُ يختلف بين الأسواق اختلافاً يُبطِل الوصفةَ الواحدة:
   الولايات المتحدة وبريطانيا وألمانيا وكندا **تُعفين الخدمة وتُعاقبن الترخيص** (حتى 30% في
   الولايات المتحدة بلا معاهدة)، بينما فرنسا (م182 CGI) وإسبانيا **لا تُعفون الخدمة نفسها**
   (33⅓% و24%) وتُسقِفان الترخيصَ بمعاهدة. ⇒ الافتراضُ الأنسبُ في سوقٍ هو الأسوأُ في آخر،
   والبنيةُ تُصمَّم لكلّ سوق وتُقاس **قبل** الفاتورة.
2. **غيابُ النصّ ليس صفراً**: خليةٌ لا يُعرَف فيها نصُّ المعاهدة على الوصف تُرجِع `None`
   بسببٍ منطوق (`TREATY_COVERAGE_UNSTATED`) ولا تُقتبس ولا تُسعَّر. وقاعدةُ الوحدة الحاكمة:
   **خليةٌ معدّلها الداخلي صفر لا تحتاج معاهدةً لتُقتبس** — فالمعاهدةُ حاملةٌ فقط حيث يكون
   المعدّل الداخلي موجباً. هذا يُفرّق بين «مجهول» و«معفى» تفريقاً لا يُخفي أحدهما بالآخر.
3. **قابليةُ العبور مسألةُ تغطيةٍ تُحلّ بالحساب لا بالتقدير**: «أيُّ حزمةِ متطلَّباتٍ تفتح
   أكبرَ عددٍ من المشترين بأقلّ جهد» مسألةُ تغطيةٍ صغيرة تُقاس **بالبحث الشامل**، والتسلسلُ
   محكومٌ بحلقةٍ لا تُسرَق: المرجعُ التجاري لا يُملَك إلّا بعد أول فاتورة ⇒ فالفئةُ التي
   تطلبه **لا يمكن أن تكون** مشتريَ الفاتورة الأولى، وفتحُها قرارٌ منفصلٌ له ثمنُه.

## ما ليست هذه الوحدة

⛔ ليست رأياً ضريبياً ولا قانونياً ولا محاسبياً. ⛔ لا تُشغِّل نموذجاً لغوياً ولا تقيس عميلاً.
⛔ ولا تُنتج رقماً بالدولار: كلُّ كلفةٍ هنا **وحدةُ جهدٍ معلنة** (أيام ⚙️)، لأن اختراعَ سعرٍ
يُفسد ما بعده (D-212 · L9). وكلُّ معدّلٍ هنا من نظامِ بلدِ المشتري على دافعٍ مقيمٍ في الجزائر،
مع إعلان درجةِ إسناده وحدوده — وما لم يُقرأ نصُّه يبقى `None`.
"""

from __future__ import annotations

import ast
import hashlib
import json
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from datetime import date
from enum import Enum
from itertools import combinations
from pathlib import Path
from types import MappingProxyType

#: سقفُ النسبة بمعدّل الأساس (10,000 = 100%).
BP_SCALE = 10_000

#: تاريخُ الاطلاع — كلُّ عمرٍ يُحسب منه لا من تاريخ التشغيل.
AS_OF = date(2026, 9, 14)


# ══════════════════════════════════════════════════════════════════════════════
# 1) طبقةُ الاستقطاع — بنيةُ العقد داخل السوق
# ══════════════════════════════════════════════════════════════════════════════


class Characterization(str, Enum):
    """وصفُ الدفعة: خدمةٌ أُدّيت لدى المصدر، أو إتاوةٌ/ترخيصُ حقٍّ يُستعمل عند المشتري."""

    SERVICE = "SERVICE"
    ROYALTY = "ROYALTY"


class RateBasis(str, Enum):
    """أساسُ المعدّل المُشتَقّ — يُقرأ في كلّ مُخرَج فلا يُخلَط معدّلٌ بمعدّل."""

    #: المعدّلُ الداخلي صفر ⇒ المعاهدةُ غيرُ حاملة (لا تُطلَب بياناتُها).
    DOMESTIC_ZERO = "DOMESTIC_ZERO"
    #: المعدّلُ الداخلي موجب ولا معاهدة ⇒ المعدّلُ الداخلي هو الحاكم.
    DOMESTIC_NO_TREATY = "DOMESTIC_NO_TREATY"
    #: المعدّلُ الداخلي موجب ومعاهدةٌ سارية ⇒ سقفُ المعاهدة.
    TREATY_CAP = "TREATY_CAP"
    #: معدّلٌ داخلي موجب ولا يُعرَف نصُّ المعاهدة على هذا الوصف ⇒ منعٌ لا صفر.
    TREATY_COVERAGE_UNSTATED = "TREATY_COVERAGE_UNSTATED"
    #: المعدّلُ الداخلي نفسه غيرُ مُسند ⇒ منعٌ لا صفر.
    DOMESTIC_UNSTATED = "DOMESTIC_UNSTATED"


class TreatyState(str, Enum):
    """حالةُ المعاهدة الجبائية بين الجزائر وسوقِ المشتري."""

    NONE = "NONE"
    IN_FORCE = "IN_FORCE"
    UNSTATED = "UNSTATED"


@dataclass(frozen=True, slots=True)
class Jurisdiction:
    """سوقُ المشتري: حالتُه التعاهدية ومعدّلاتُه، بدرجةِ إسنادٍ في كلّ خلية."""

    code: str
    label_ar: str
    treaty: TreatyState
    treaty_note_ar: str
    #: المعدّل الداخلي على مقابل الخدمات المدفوع لمقيمٍ غير مقيم (بمعدّل الأساس).
    service_domestic_bp: int | None
    #: سقفُ المعاهدة على الخدمات إن نصَّت عليه (وإلّا `None` = غيرُ مُسند).
    service_treaty_bp: int | None
    #: المعدّل الداخلي على الإتاوات/الترخيص (بمعدّل الأساس).
    royalty_domestic_bp: int | None
    #: سقفُ المعاهدة الأدنى والأعلى على الإتاوات (قد يكون نطاقاً لا رقماً).
    royalty_treaty_bp: int | None
    royalty_treaty_alt_bp: int | None
    service_note_ar: str
    royalty_note_ar: str
    source_ar: str

    def __post_init__(self) -> None:
        for value in (
            self.service_domestic_bp,
            self.service_treaty_bp,
            self.royalty_domestic_bp,
            self.royalty_treaty_bp,
            self.royalty_treaty_alt_bp,
        ):
            if value is not None and not 0 <= value < BP_SCALE:
                raise ValueError(f"{self.code}: معدّلٌ خارج [0, 10000) بمعدّل الأساس: {value}")
        if (
            self.royalty_treaty_bp is not None
            and self.royalty_treaty_alt_bp is not None
            and self.royalty_treaty_alt_bp < self.royalty_treaty_bp
        ):
            raise ValueError(f"{self.code}: نطاقُ الإتاوات مقلوب (الأدنى أكبرُ من الأعلى)")


@dataclass(frozen=True, slots=True)
class RateVerdict:
    """حكمُ خليةٍ واحدة (سوق × وصفُ دفعة): معدّلٌ قابلٌ للاقتباس أو منعٌ بسببٍ معلن."""

    market: str
    characterization: Characterization
    rate_bp_lo: int | None
    rate_bp_hi: int | None
    basis: RateBasis
    reason_ar: str

    @property
    def is_quotable(self) -> bool:
        """هل يُقتبس رقمُ هذه الخلية؟ المنعُ (`None`) ليس صفراً."""
        return self.rate_bp_lo is not None

    @property
    def rate_pct_lo(self) -> float | None:
        return None if self.rate_bp_lo is None else self.rate_bp_lo / 100

    @property
    def rate_pct_hi(self) -> float | None:
        return None if self.rate_bp_hi is None else self.rate_bp_hi / 100

    def net_multiplier_lo(self) -> float | None:
        """أدنى صافٍ مقابل وحدةٍ إجمالية مُفوتَرة (الأسوأ للمصدِّر)."""
        if self.rate_bp_hi is None:
            return None
        return (BP_SCALE - self.rate_bp_hi) / BP_SCALE

    def net_multiplier_hi(self) -> float | None:
        """أعلى صافٍ مقابل وحدةٍ إجمالية مُفوتَرة (الأفضل للمصدِّر)."""
        if self.rate_bp_lo is None:
            return None
        return (BP_SCALE - self.rate_bp_lo) / BP_SCALE

    def uplift_required(self) -> float | None:
        """الزيادةُ على السعر الإجمالي المطلوبةُ لبلوغ الصافي نفسه عند **أعلى** معدّل.

        مثالٌ محسوب: 30% ⇒ 30 ÷ 70 = **0.428571** ⇒ +42.86% على الفاتورة.
        """
        if self.rate_bp_hi is None or self.rate_bp_hi >= BP_SCALE:
            return None
        return round(self.rate_bp_hi / (BP_SCALE - self.rate_bp_hi), 6)


def effective_rate(jurisdiction: Jurisdiction, characterization: Characterization) -> RateVerdict:
    """يُشتقّ معدّلُ الاستقطاع الفعّال لخليةٍ (سوق × وصف) بلا استعارات.

    القواعدُ غيرُ القابلة للتفاوض:

    * معدّلٌ داخلي **صفر** ⇒ `DOMESTIC_ZERO`، والمعاهدةُ غيرُ حاملةٍ فلا يُشترط نصُّها.
    * معدّلٌ داخلي **موجب** و**لا معاهدة** ⇒ `DOMESTIC_NO_TREATY`، ولا تخفيفَ بلا سند.
    * معدّلٌ داخلي **موجب** ومعاهدةٌ **سارية** ونصُّ الوصف **غائب** ⇒ `None`
      (`TREATY_COVERAGE_UNSTATED`): الغيابُ لا يُصغَّر ولا يُصفَّر.
    * معدّلٌ داخلي **غيرُ مُسند** ⇒ `None` (`DOMESTIC_UNSTATED`) ولو وُجدت معاهدة.
    """
    if characterization is Characterization.SERVICE:
        domestic = jurisdiction.service_domestic_bp
        treaty_cap = jurisdiction.service_treaty_bp
        note = jurisdiction.service_note_ar
    else:
        domestic = jurisdiction.royalty_domestic_bp
        treaty_cap = jurisdiction.royalty_treaty_bp
        alt_cap = jurisdiction.royalty_treaty_alt_bp
        note = jurisdiction.royalty_note_ar

    if domestic is None:
        return RateVerdict(
            market=jurisdiction.code,
            characterization=characterization,
            rate_bp_lo=None,
            rate_bp_hi=None,
            basis=RateBasis.DOMESTIC_UNSTATED,
            reason_ar=(
                f"{jurisdiction.code}: المعدّل الداخلي على {characterization.value} غيرُ مُسند "
                f"في هذه الوحدة — ⛔ لا يُفترض صفراً ولا يُقتبس رقم. {note}"
            ),
        )
    if domestic == 0:
        return RateVerdict(
            market=jurisdiction.code,
            characterization=characterization,
            rate_bp_lo=0,
            rate_bp_hi=0,
            basis=RateBasis.DOMESTIC_ZERO,
            reason_ar=(
                f"{jurisdiction.code}: لا استقطاع داخلي على {characterization.value} ⇒ صفرٌ "
                f"مُسند، والمعاهدةُ غيرُ حاملة هنا. {note}"
            ),
        )
    if jurisdiction.treaty is TreatyState.NONE:
        return RateVerdict(
            market=jurisdiction.code,
            characterization=characterization,
            rate_bp_lo=domestic,
            rate_bp_hi=domestic,
            basis=RateBasis.DOMESTIC_NO_TREATY,
            reason_ar=(
                f"{jurisdiction.code}: لا معاهدة ⇒ المعدّل الداخلي {domestic / 100:.2f}% هو "
                f"الحاكم، ولا تخفيفَ بلا سند. {note}"
            ),
        )
    if jurisdiction.treaty is TreatyState.UNSTATED or treaty_cap is None:
        return RateVerdict(
            market=jurisdiction.code,
            characterization=characterization,
            rate_bp_lo=None,
            rate_bp_hi=None,
            basis=RateBasis.TREATY_COVERAGE_UNSTATED,
            reason_ar=(
                f"{jurisdiction.code}: معدّلٌ داخلي موجب ({domestic / 100:.2f}%) ولا يُعرَف نصُّ "
                f"المعاهدة على {characterization.value} ⇒ ⛔ لا صافٍ قبل تحقّقٍ كتابيّ. {note}"
            ),
        )
    if characterization is Characterization.ROYALTY:
        upper = max(treaty_cap, alt_cap) if alt_cap is not None else treaty_cap
    else:
        upper = treaty_cap
    return RateVerdict(
        market=jurisdiction.code,
        characterization=characterization,
        rate_bp_lo=treaty_cap,
        rate_bp_hi=upper,
        basis=RateBasis.TREATY_CAP,
        reason_ar=(
            f"{jurisdiction.code}: سقفُ المعاهدة {treaty_cap / 100:.2f}%"
            + (f"–{upper / 100:.2f}%" if upper != treaty_cap else "")
            + f" دون الداخلي ({domestic / 100:.2f}%). {note}"
        ),
    )


class InversionState(str, Enum):
    """وجهُ التعرّض في هذا السوق: أيُّ وصفٍ يُستقطع، وأيُّهما يُعفى؟

    الحالاتُ الخمسُ لا تقبل الخلط، لأنّ علاجَها مختلف:

    * `ROYALTY_WORSE` — الخدمةُ معفاةٌ والترخيصُ مكلَّفٌ (الولايات المتحدة، بريطانيا، ألمانيا،
      كندا…) ⇒ الخطرُ في **وصف العقد** لا في السوق.
    * `SERVICE_WORSE` — العكسُ (الترخيصُ أرخصُ من الخدمة) ⇒ لا يُوصف العملُ خدمةً بلا حساب.
    * `BOTH_EXPOSED` — لا إعفاءَ داخليّاً في الوصفين معاً (فرنسا 33⅓%، إسبانيا 24%) ⇒
      **علاجُ السوق تحقّقٌ كتابيٌّ قبل الفاتورة**، لا تغييرُ وصفٍ داخل العقد.
    * `BOTH_ZERO` — السوقُ لا يستقطع في الوصفين (هولندا، سويسرا، الإمارات) ⇒ سوقُ تصفيرِ
      خطرِ الاستقطاع، لكنّه لا يقول شيئاً عن قابلية العبور.
    * `UNSTATED` — نصٌّ ناقصٌ ⇒ منعٌ لا تقدير.
    """

    ROYALTY_WORSE = "ROYALTY_WORSE"
    SERVICE_WORSE = "SERVICE_WORSE"
    BOTH_EXPOSED = "BOTH_EXPOSED"
    BOTH_ZERO = "BOTH_ZERO"
    UNSTATED = "UNSTATED"


def characterization_inversion(
    jurisdiction: Jurisdiction, *, use_domestic: bool = False
) -> InversionState:
    """يقارن استقطاعَ الخدمة باستقطاع الترخيص في السوق نفسه.

    `use_domestic=True` يقارن **المعدّلَين الداخليَّين** قبل أيّ معاهدة، وهو المقارنةُ التي
    تكشف انقلابَ الإشارة بين الأسواق حتى حين يكون سقفُ المعاهدة غيرَ مُسند.
    """
    if use_domestic:
        service = jurisdiction.service_domestic_bp
        royalty = jurisdiction.royalty_domestic_bp
    else:
        service = effective_rate(jurisdiction, Characterization.SERVICE).rate_bp_hi
        royalty = effective_rate(jurisdiction, Characterization.ROYALTY).rate_bp_hi
    if service is None or royalty is None:
        return InversionState.UNSTATED
    if service == royalty:
        return InversionState.BOTH_ZERO if service == 0 else InversionState.BOTH_EXPOSED
    if service > royalty:
        return InversionState.SERVICE_WORSE
    return InversionState.ROYALTY_WORSE


def matrix(jurisdictions: Sequence[Jurisdiction]) -> tuple[RateVerdict, ...]:
    """كلّ خلايا (سوق × وصف) بترتيبٍ ثابت — لا اعتمادَ على ترتيب المُدخَل."""

    rows: list[RateVerdict] = []
    for jurisdiction in sorted(jurisdictions, key=lambda item: item.code):
        for characterization in (Characterization.SERVICE, Characterization.ROYALTY):
            rows.append(effective_rate(jurisdiction, characterization))
    return tuple(rows)


# ══════════════════════════════════════════════════════════════════════════════
# 2) طبقةُ تأهيل المورّد — مسألةُ تغطية
# ══════════════════════════════════════════════════════════════════════════════


class Doctrine(str, Enum):
    """حكمُ العقيدة على القدرة: مباحة، أو ممنوعةٌ بنصّ."""

    ALLOWED = "ALLOWED"
    #: K1 — ⛔ لا استلام إيرادات بعملاتٍ مشفّرة.
    FORBIDDEN_K1 = "FORBIDDEN_K1"
    #: K5 — ⛔ لا كيان/حساب أجنبي يملكه مقيمٌ جزائري بلا إذن بنك الجزائر.
    FORBIDDEN_K5 = "FORBIDDEN_K5"


class RequirementKind(str, Enum):
    """طبيعةُ المتطلَّب: نصٌّ قانوني، أو عرفُ شراء، أو قاعدةُ عقيدةٍ داخلية."""

    LEGAL = "LEGAL"
    COMMERCIAL = "COMMERCIAL"
    DOCTRINE = "DOCTRINE"


@dataclass(frozen=True, slots=True)
class Requirement:
    """متطلَّبٌ واحدٌ في حزمة تأهيل المشتري."""

    id: str
    label_ar: str
    kind: RequirementKind
    satisfied_by: tuple[str, ...]
    note_ar: str = ""


@dataclass(frozen=True, slots=True)
class Capability:
    """قدرةٌ يمكن امتلاكها؛ `effort_units` وحداتُ جهدٍ مُعلنة (أيام ⚙️) لا مال."""

    id: str
    label_ar: str
    effort_units: int
    satisfies: tuple[str, ...]
    doctrine: Doctrine = Doctrine.ALLOWED
    #: لا تُملَك إلّا بعد أوّل تعاملٍ مدفوعٍ مُكتمل (حلقةُ المرجع).
    after_first_invoice: bool = False
    note_ar: str = ""

    def __post_init__(self) -> None:
        if self.effort_units < 0:
            raise ValueError(f"{self.id}: جهدٌ سالب")
        if self.after_first_invoice and self.effort_units != 0:
            raise ValueError(f"{self.id}: قدرةٌ بعد الفاتورة لا تحمل جهداً مُخطَّطاً")


@dataclass(frozen=True, slots=True)
class Archetype:
    """فئةُ مشترٍ: سوقُها + متطلباتُها الإلزامية + ملاحظةُ قناة التسوية."""

    id: str
    market: str
    label_ar: str
    mandatory: tuple[str, ...]
    rail_note_ar: str = ""

    def __post_init__(self) -> None:
        if not self.mandatory:
            raise ValueError(f"{self.id}: فئةٌ بلا متطلّبات ⇒ عبورٌ مجانيّ غيرُ ذي معنى")


class AbStatus(str, Enum):
    """حالةُ العبور لفئة مشترٍ عند خطٍّ أساسيّ مُعلن."""

    PASS = "PASS"
    UNLOCKABLE = "UNLOCKABLE"
    AFTER_FIRST_INVOICE = "AFTER_FIRST_INVOICE"
    BLOCKED_DOCTRINE = "BLOCKED_DOCTRINE"
    BLOCKED_UNSATISFIABLE = "BLOCKED_UNSATISFIABLE"


@dataclass(frozen=True, slots=True)
class ArchetypeVerdict:
    """حكمُ فئةٍ واحدة: الحالة، المتطلَّباتُ الناقصة، الجهدُ المعلن، والسببُ المنطوق."""

    archetype: str
    status: AbStatus
    missing: tuple[str, ...]
    reason_ar: str
    effort_units: int | None


@dataclass(frozen=True, slots=True)
class Catalog:
    """فهرسُ المتطلَّبات والقدرات — يُبنى ويُتحقَّق مرّةً واحدة."""

    requirements: Mapping[str, Requirement]
    capabilities: Mapping[str, Capability]

    def __post_init__(self) -> None:
        unknown: list[str] = []
        for capability in self.capabilities.values():
            for requirement_id in capability.satisfies:
                if requirement_id not in self.requirements:
                    unknown.append(f"{capability.id}→{requirement_id}")
        if unknown:
            raise ValueError(f"قدراتٌ تُشير إلى متطلَّباتٍ غير معرَّفة: {sorted(unknown)}")
        for requirement in self.requirements.values():
            if not requirement.satisfied_by:
                raise ValueError(f"{requirement.id}: متطلَّبٌ بلا قابِلٍ للإرضاء ⇒ منعٌ أبديّ")
            if not set(requirement.satisfied_by) <= set(self.capabilities):
                raise ValueError(f"{requirement.id}: قابِلٌ غيرُ مُعرَّف في الفهرس")


def held_capabilities(
    catalog: Catalog, *, held: Iterable[str], allow_after_first_invoice: bool = False
) -> frozenset[str]:
    """الخطُّ الأساسيّ: القدراتُ المملوكةُ فعلاً، مع خيار ضمّ ما بعد الفاتورة."""

    result: set[str] = set()
    for capability_id in held:
        capability = catalog.capabilities.get(capability_id)
        if capability is None:
            raise KeyError(f"قدرةٌ غيرُ معرَّفة في الفهرس: {capability_id}")
        if capability.after_first_invoice and not allow_after_first_invoice:
            continue
        result.add(capability_id)
    return frozenset(result)


def _satisfiers(requirement_id: str, catalog: Catalog) -> tuple[Capability, ...]:
    return tuple(
        sorted(
            (cap for cap in catalog.capabilities.values() if requirement_id in cap.satisfies),
            key=lambda cap: cap.id,
        )
    )


def evaluate(archetype: Archetype, catalog: Catalog, held: frozenset[str]) -> ArchetypeVerdict:
    """يُقيّم فئةً عند خطٍّ أساسيّ: عبورٌ الآن، فتحٌ ممكن، تأجيلٌ لمرجع، أو منعٌ مسند.

    المنعُ مسندٌ لا عقليّ: متطلَّبٌ لا يُرضيه إلّا قدرةٌ **محظورةٌ بعقيدة** ⇒
    `BLOCKED_DOCTRINE`؛ ومتطلَّبٌ لا يُرضيه شيءٌ في الفهرس ⇒ `BLOCKED_UNSATISFIABLE`.
    وفئةٌ فيها متطلَّبٌ لا يُملَك إلّا **بعد** أول فاتورة ⇒ `AFTER_FIRST_INVOICE` ولو كان
    بعضُ متطلَّباتها قابلاً للفتح الآن — لأنّ الترتيبَ جزءٌ من الحكم لا حاشيةٌ عليه.
    """
    missing: list[str] = []
    doctrine_blocked: list[str] = []
    after_first: list[str] = []
    unsatisfiable: list[str] = []
    effort = 0
    for requirement_id in sorted(archetype.mandatory):
        if any(cap in held for cap in catalog.requirements[requirement_id].satisfied_by):
            continue
        missing.append(requirement_id)
        satisfiers = _satisfiers(requirement_id, catalog)
        if not satisfiers:
            unsatisfiable.append(requirement_id)
            continue
        allowed = [cap for cap in satisfiers if cap.doctrine is Doctrine.ALLOWED]
        if not allowed:
            doctrine_blocked.append(requirement_id)
            continue
        if all(cap.after_first_invoice for cap in allowed):
            after_first.append(requirement_id)
            continue
        effort += min(cap.effort_units for cap in allowed if not cap.after_first_invoice)
    if unsatisfiable:
        return ArchetypeVerdict(
            archetype=archetype.id,
            status=AbStatus.BLOCKED_UNSATISFIABLE,
            missing=tuple(missing),
            reason_ar=(
                "متطلَّباتٌ بلا قابِلٍ في فهرسنا (تحتاج تحقّقاً كتابياً أو وسيطاً غير مُنمذَج): "
                + ", ".join(unsatisfiable)
            ),
            effort_units=None,
        )
    if doctrine_blocked:
        return ArchetypeVerdict(
            archetype=archetype.id,
            status=AbStatus.BLOCKED_DOCTRINE,
            missing=tuple(missing),
            reason_ar=(
                "الفئةُ تُرضي متطلَّباتها بوسائل محظورةٍ نصّاً (K1/K5) ⇒ ⛔ تُترك ولا يُنفق "
                "عليها وقت: " + ", ".join(doctrine_blocked)
            ),
            effort_units=None,
        )
    if not missing:
        return ArchetypeVerdict(
            archetype=archetype.id,
            status=AbStatus.PASS,
            missing=(),
            reason_ar="كلُّ المتطلَّبات الإلزامية مُرضاةٌ بالخطّ الأساسيّ ⇒ فئةُ الفاتورة الأولى.",
            effort_units=0,
        )
    if after_first:
        return ArchetypeVerdict(
            archetype=archetype.id,
            status=AbStatus.AFTER_FIRST_INVOICE,
            missing=tuple(missing),
            reason_ar=(
                "الفئةُ تطلب مرجعاً تجارياً، والمرجعُ لا يُملَك إلّا بعد أول فاتورة ⇒ ⛔ لا تصلح "
                "للفاتورة الأولى. وما تبقّى قابلاً للفتح الآن يكلّف ≈ "
                f"{effort} وحدة: " + ", ".join(after_first)
            ),
            effort_units=effort,
        )
    return ArchetypeVerdict(
        archetype=archetype.id,
        status=AbStatus.UNLOCKABLE,
        missing=tuple(missing),
        reason_ar=f"تُفتَح بجهدٍ مُعلن ≈ {effort} وحدة: " + ", ".join(missing),
        effort_units=effort,
    )


@dataclass(frozen=True, slots=True)
class UnlockPlan:
    """خطةُ فتحٍ: قدراتٌ مختارةٌ، فئاتٌ تُفتَح بسببها، وجهدُها الإجمالي."""

    chosen: tuple[str, ...]
    opened: tuple[str, ...]
    passed_after: tuple[str, ...]
    effort_units: int
    reason_ar: str


def _allowed_candidates(
    catalog: Catalog, held: frozenset[str], *, include_after_first_invoice: bool
) -> tuple[Capability, ...]:
    return tuple(
        sorted(
            (
                cap
                for cap in catalog.capabilities.values()
                if cap.id not in held
                and cap.doctrine is Doctrine.ALLOWED
                and (include_after_first_invoice or not cap.after_first_invoice)
            ),
            key=lambda cap: cap.id,
        )
    )


def minimum_unlock_set(
    archetypes: Sequence[Archetype],
    catalog: Catalog,
    held: frozenset[str],
    *,
    budget_units: int,
    include_after_first_invoice: bool = False,
) -> UnlockPlan:
    """أصغرُ حزمةِ قدراتٍ (بالجهد المعلن) تُدخل أكبرَ عددٍ من الفئات داخل العبور.

    تُحلّ **بالبحث الشامل** لا بالتقدير: عددُ القدرات المرشَّحة محدودٌ ومعلن، فالفضاءُ
    يُقاس كاملاً. والترتيبُ عند التعادل مُعلن: أكثرُ فئاتٍ مفتوحة، ثم أقلُّ جهد، ثم أبجديّاً
    — فلا اعتمادَ على ترتيب المُدخَل ولا على عشوائية.
    """
    if budget_units < 0:
        raise ValueError("ميزانيةٌ سالبة")
    candidates = _allowed_candidates(
        catalog, held, include_after_first_invoice=include_after_first_invoice
    )
    baseline_ids = {
        verdict.archetype
        for verdict in (evaluate(archetype, catalog, held) for archetype in archetypes)
        if verdict.status is AbStatus.PASS
    }
    best: tuple[tuple[int, int, tuple[str, ...]], UnlockPlan] | None = None
    for size in range(0, len(candidates) + 1):
        for subset in combinations(candidates, size):
            effort = sum(cap.effort_units for cap in subset)
            if effort > budget_units:
                continue
            extended = frozenset(held | {cap.id for cap in subset})
            opened: list[str] = []
            passed: list[str] = []
            for archetype in sorted(archetypes, key=lambda item: item.id):
                verdict = evaluate(archetype, catalog, extended)
                if verdict.status is AbStatus.PASS:
                    passed.append(archetype.id)
                    if archetype.id not in baseline_ids:
                        opened.append(archetype.id)
            chosen = tuple(cap.id for cap in subset)
            key = (-len(opened), effort, chosen)
            plan = UnlockPlan(
                chosen=chosen,
                opened=tuple(opened),
                passed_after=tuple(passed),
                effort_units=effort,
                reason_ar=(
                    f"حزمةٌ بجهد {effort} تفتح {len(opened)} فئةً: "
                    + (", ".join(opened) if opened else "لا شيء")
                ),
            )
            if best is None or key < best[0]:
                best = (key, plan)
    if best is None:
        raise RuntimeError("تعذّر إيجاد خطة — فضاءُ البحث فارغ")
    return best[1]


def entry_frontier(
    archetypes: Sequence[Archetype], catalog: Catalog, held: frozenset[str]
) -> tuple[ArchetypeVerdict, ...]:
    """فئاتُ الفاتورة الأولى: ما يعبر اليوم بلا فتحٍ وبلا مرجع."""

    verdicts = [evaluate(archetype, catalog, held) for archetype in archetypes]
    return tuple(
        sorted((v for v in verdicts if v.status is AbStatus.PASS), key=lambda item: item.archetype)
    )


def reference_ladder(
    archetypes: Sequence[Archetype], catalog: Catalog, held: frozenset[str]
) -> tuple[tuple[str, ...], tuple[ArchetypeVerdict, ...]]:
    """حلقةُ المرجع: بعد أول فاتورة تُضاف قدراتُ «ما بعد الفاتورة» ويُعاد التقييم.

    تُرجِع (فئاتُ الجولة الأولى، أحكامُ الجولة الثانية على الخطّ نفسه بعد إضافة المراجع).
    """
    first_round = entry_frontier(archetypes, catalog, held)
    if not first_round:
        return (), ()
    extended = held | frozenset(
        cap.id for cap in catalog.capabilities.values() if cap.after_first_invoice
    )
    second_round = tuple(
        sorted(
            (evaluate(archetype, catalog, extended) for archetype in archetypes),
            key=lambda item: item.archetype,
        )
    )
    return tuple(v.archetype for v in first_round), second_round


@dataclass(frozen=True, slots=True)
class NetCapture:
    """الالتقاطُ الصافي: عبورٌ × (1 − استقطاع)، أو `None` بسببٍ معلن."""

    archetype: str
    market: str
    characterization: Characterization
    passable: bool
    rate_bp_lo: int | None
    rate_bp_hi: int | None
    net_capture: float | None
    reason_ar: str


def net_capture(
    archetype: Archetype,
    verdict: ArchetypeVerdict,
    jurisdictions: Mapping[str, Jurisdiction],
    *,
    characterization: Characterization,
    rail_conflict: str | None = None,
) -> NetCapture:
    """يضرب قابليةَ العبور في الصافي الباقي بعد الاستقطاع — الرقمُ الواحد للمقارنة.

    ⛔ لا يُبنى رقمٌ على خليةٍ غيرِ مُسندة: معدّلٌ `None` ⇒ نتيجةُ `None`.
    ⛔ ولا يُبنى رقمٌ على قناةٍ في خرقٍ بنيويّ (وسيطٌ يحتفظ بحصيلةٍ تتجاوز سقف النظام
    26-02 — نتيجةٌ من دفعة RSM): العبورُ الذي يُنتج خرقاً ليس عبوراً.
    """
    jurisdiction = jurisdictions.get(archetype.market)
    if jurisdiction is None:
        return NetCapture(
            archetype=archetype.id,
            market=archetype.market,
            characterization=characterization,
            passable=False,
            rate_bp_lo=None,
            rate_bp_hi=None,
            net_capture=None,
            reason_ar=f"سوقٌ غيرُ مُعرَّف في الوحدة: {archetype.market}",
        )
    rate = effective_rate(jurisdiction, characterization)
    if verdict.status is not AbStatus.PASS:
        return NetCapture(
            archetype=archetype.id,
            market=archetype.market,
            characterization=characterization,
            passable=False,
            rate_bp_lo=rate.rate_bp_lo,
            rate_bp_hi=rate.rate_bp_hi,
            net_capture=0.0,
            reason_ar=(
                f"غيرُ عابرةٍ الآن ({verdict.status.value}) ⇒ الالتقاطُ صفرٌ بالعبور لا بالسعر. "
                + verdict.reason_ar
            ),
        )
    if rail_conflict is not None:
        return NetCapture(
            archetype=archetype.id,
            market=archetype.market,
            characterization=characterization,
            passable=True,
            rate_bp_lo=rate.rate_bp_lo,
            rate_bp_hi=rate.rate_bp_hi,
            net_capture=None,
            reason_ar=f"قناةٌ في خرقٍ بنيويّ مُعلن ⇒ ⛔ لا رقمَ قبل إصلاح السكّة: {rail_conflict}",
        )
    if not rate.is_quotable:
        return NetCapture(
            archetype=archetype.id,
            market=archetype.market,
            characterization=characterization,
            passable=True,
            rate_bp_lo=None,
            rate_bp_hi=None,
            net_capture=None,
            reason_ar=rate.reason_ar,
        )
    return NetCapture(
        archetype=archetype.id,
        market=archetype.market,
        characterization=characterization,
        passable=True,
        rate_bp_lo=rate.rate_bp_lo,
        rate_bp_hi=rate.rate_bp_hi,
        net_capture=rate.net_multiplier_lo(),
        reason_ar=rate.reason_ar,
    )


# ══════════════════════════════════════════════════════════════════════════════
# 3) البوّابات وشروطُ القتل
# ══════════════════════════════════════════════════════════════════════════════


class KillSwitch(str, Enum):
    """شروطُ القتل: متى نُعلن أنّ هذه المعرفة لا تخدم قراراً (وقتلُ البحث نجاحٌ منهجيّ)."""

    #: لو استوى معدّلُ الوصفين في كلّ سوق لسقط معنى مصفوفة بنية العقد.
    K1_NO_CHARACTERIZATION_EFFECT = "K1_NO_CHARACTERIZATION_EFFECT"
    #: لو لم يُظهر أيُّ سوقٍ تعرّضاً على **الخدمة** (لا على الترخيص وحده) لسقطت أطروحةُ
    #: «الوصفةُ الافتراضية — بيعُ خدمة — ليست آمنةً في كلّ سوق».
    K2_NO_INVERSION_ANYWHERE = "K2_NO_INVERSION_ANYWHERE"
    #: لو عبَرت كلُّ الفئات بالخطّ الأساسيّ لسقط معنى حزمة التأهيل كلُّها.
    K3_EVERYTHING_PASSES = "K3_EVERYTHING_PASSES"
    #: لو لم تُفتح فئةٌ واحدة داخل الميزانية المعلنة لسقط مسار الفاتورة الأولى.
    K4_NO_UNLOCK_WITHIN_BUDGET = "K4_NO_UNLOCK_WITHIN_BUDGET"
    #: لو تعذّر اقتباسُ رقمٍ في كلّ سوق لسقط المقياس كلُّه إلى «مجهول».
    K5_ALL_RATES_UNSTATED = "K5_ALL_RATES_UNSTATED"


def kill_switches(
    jurisdictions: Sequence[Jurisdiction],
    archetypes: Sequence[Archetype],
    catalog: Catalog,
    held: frozenset[str],
    *,
    budget_units: int,
) -> tuple[KillSwitch, ...]:
    """يفحص شروطَ القتل الخمسة ويُرجِع ما تحقّق منها."""

    fired: list[KillSwitch] = []
    service_rates = {
        effective_rate(item, Characterization.SERVICE).rate_bp_hi for item in jurisdictions
    }
    royalty_rates = {
        effective_rate(item, Characterization.ROYALTY).rate_bp_hi for item in jurisdictions
    }
    if service_rates == royalty_rates and None not in service_rates:
        fired.append(KillSwitch.K1_NO_CHARACTERIZATION_EFFECT)
    inversions = {characterization_inversion(item, use_domestic=True) for item in jurisdictions}
    if not inversions & {InversionState.SERVICE_WORSE, InversionState.BOTH_EXPOSED}:
        fired.append(KillSwitch.K2_NO_INVERSION_ANYWHERE)
    verdicts = [evaluate(archetype, catalog, held) for archetype in archetypes]
    if verdicts and all(item.status is AbStatus.PASS for item in verdicts):
        fired.append(KillSwitch.K3_EVERYTHING_PASSES)
    plan = minimum_unlock_set(archetypes, catalog, held, budget_units=budget_units)
    if not plan.opened:
        fired.append(KillSwitch.K4_NO_UNLOCK_WITHIN_BUDGET)
    if not any(row.is_quotable for row in matrix(jurisdictions)):
        fired.append(KillSwitch.K5_ALL_RATES_UNSTATED)
    return tuple(sorted(fired, key=lambda item: item.value))


def summarize(
    jurisdictions: Sequence[Jurisdiction],
    archetypes: Sequence[Archetype],
    catalog: Catalog,
    held: frozenset[str],
    *,
    budget_units: int,
    rail_conflicts: Mapping[str, str] | None = None,
) -> dict[str, object]:
    """ملخّصٌ حتميّ يصلح للقياس المودَع: أعدادٌ لا تتجاوز مجموعَها، ومنعٌ لا يُصفَّر.

    التسلسلُ مُعلن: (1) خطةُ الفتح على الخطّ الأساسيّ، (2) ثم السُّلَّمُ على الخطّ **بعد**
    الخطة — لأنّ المرجعَ ثمرةُ عبورٍ سابق لا رأسُ مالٍ أوّليّ.
    """
    rows = matrix(jurisdictions)
    by_code = {item.code: item for item in jurisdictions}
    verdicts = sorted(
        (evaluate(archetype, catalog, held) for archetype in archetypes),
        key=lambda item: item.archetype,
    )
    plan = minimum_unlock_set(archetypes, catalog, held, budget_units=budget_units)
    stack_after_plan = frozenset(held | set(plan.chosen))
    first_round, second_round = reference_ladder(archetypes, catalog, stack_after_plan)
    conflicts = dict(rail_conflicts or {})

    captures: list[dict[str, object]] = []
    for archetype in sorted(archetypes, key=lambda item: item.id):
        verdict = evaluate(archetype, catalog, held)
        for characterization in (Characterization.SERVICE, Characterization.ROYALTY):
            item = net_capture(
                archetype,
                verdict,
                by_code,
                characterization=characterization,
                rail_conflict=conflicts.get(archetype.id),
            )
            rate_verdict = effective_rate(by_code[item.market], item.characterization)
            captures.append(
                {
                    "archetype": item.archetype,
                    "market": item.market,
                    "characterization": item.characterization.value,
                    "passable": item.passable,
                    "rate_bp_lo": item.rate_bp_lo,
                    "rate_bp_hi": item.rate_bp_hi,
                    "net_if_passable": rate_verdict.net_multiplier_lo(),
                    "net_capture": item.net_capture,
                    "reason_ar": item.reason_ar,
                }
            )

    status_counts: dict[str, int] = {}
    for verdict in verdicts:
        status_counts[verdict.status.value] = status_counts.get(verdict.status.value, 0) + 1
    basis_counts: dict[str, int] = {}
    for row in rows:
        basis_counts[row.basis.value] = basis_counts.get(row.basis.value, 0) + 1

    return {
        "cells": {
            "total": len(rows),
            "quotable": sum(1 for row in rows if row.is_quotable),
            "blocked": sum(1 for row in rows if not row.is_quotable),
            "basis_counts": dict(sorted(basis_counts.items())),
        },
        "archetypes": {
            "total": len(verdicts),
            "status_counts": dict(sorted(status_counts.items())),
            "entry_frontier": [
                item.archetype for item in entry_frontier(archetypes, catalog, held)
            ],
            "verdicts": [
                {
                    "archetype": verdict.archetype,
                    "status": verdict.status.value,
                    "missing": list(verdict.missing),
                    "effort_units": verdict.effort_units,
                    "reason_ar": verdict.reason_ar,
                }
                for verdict in verdicts
            ],
        },
        "plan": {
            "budget_units": budget_units,
            "chosen": list(plan.chosen),
            "opened": list(plan.opened),
            "passed_after": list(plan.passed_after),
            "effort_units": plan.effort_units,
            "reason_ar": plan.reason_ar,
        },
        "ladder": {
            "stack": sorted(stack_after_plan),
            "first_round": list(first_round),
            "second_round_pass": [
                item.archetype for item in second_round if item.status is AbStatus.PASS
            ],
            "newly_opened_by_reference": sorted(
                {item.archetype for item in second_round if item.status is AbStatus.PASS}
                - set(first_round)
            ),
        },
        "inversions": {
            "domestic": {
                item.code: characterization_inversion(item, use_domestic=True).value
                for item in sorted(jurisdictions, key=lambda entry: entry.code)
            },
            "effective": {
                item.code: characterization_inversion(item).value
                for item in sorted(jurisdictions, key=lambda entry: entry.code)
            },
        },
        "captures": captures,
        "kill_switches": [
            switch.value
            for switch in kill_switches(
                jurisdictions, archetypes, catalog, held, budget_units=budget_units
            )
        ],
    }


# ══════════════════════════════════════════════════════════════════════════════
# 4) حرّاسُ النزاهة
# ══════════════════════════════════════════════════════════════════════════════

#: الوحداتُ المسموح استيرادُها في هذه الحزمة: قياسيّاتٌ خالصة (حراسةُ AST في الاختبارات).
STDLIB_ONLY: frozenset[str] = frozenset(
    {
        "__future__",
        "argparse",
        "ast",
        "collections",
        "dataclasses",
        "datetime",
        "hashlib",
        "json",
        "enum",
        "itertools",
        "pathlib",
        "types",
        "typing",
    }
)


def module_imports(path: Path | str) -> tuple[str, ...]:
    """أسماءُ الوحدات المستوردة في ملفٍّ ما — لحراسة «stdlib فقط، بلا `app/`»."""

    tree = ast.parse(Path(path).read_text(encoding="utf-8"))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            names.add(node.module.split(".")[0])
    return tuple(sorted(names))


# ══════════════════════════════════════════════════════════════════════════════
# 5) البيانات المُسندة — أسواقٌ وحزمٌ وفئات
# ══════════════════════════════════════════════════════════════════════════════

#: مصدرُ شبكة المعاهدات الجزائرية (جدول «DTT rates» في PwC) — يُقرأ في كلّ سوق.
SRC_TREATY_NETWORK = (
    "PwC Tax Summaries — Algeria: Corporate — Withholding taxes (جدول معدّلات المعاهدات، "
    "قراءة 2026-09-14) + BOFiP BOI-INT-CVB-DZA (نصّ المعاهدة الفرنسية)"
)
SRC_IRS_515 = (
    "IRS Publication 515 (2026) — Withholding of Tax on Nonresident Aliens: مبدأُ المصدر "
    "«مكان أداء الخدمة» + معدّل 30% النظامي على FDAP"
)
SRC_FR_182B = "CGI art. 182 B + BOFiP BOI-INT-DG-20-20-30 (استقطاع 33⅓% على prestations)"
SRC_ES_IRNR = "IRNR art. 25 (24% على الإتاوات والخدمات التقنية) — سندٌ ثانويّ متقاطع"
SRC_DE_50A = "§50a EStG (15% + 5.5% تضامن = 15.825% على الإتاوات؛ الخدمات الحقيقية خارجُ نطاقه)"
SRC_UK_ROYALTY = (
    "UK: استقطاع 20% على الإتاوات — جدولٌ ثانويّ متقاطع؛ لا استقطاع بريطاني على مقابل الخدمات"
)
SRC_NL_ZERO = "هولندا: لا استقطاع على الإتاوات ولا على الخدمات — جدولٌ ثانويّ متقاطع"
SRC_CH_ZERO = "سويسرا: لا استقطاع على الإتاوات/الخدمات لغير المقيمين — جدولٌ ثانويّ متقاطع"
SRC_CA_105 = (
    "Canada Regulation 105: استقطاع 15% على مقابل خدماتٍ **مؤدّاةٍ في كندا** فقط؛ "
    "وما يُؤدّى خارجها لا استقطاعَ عليه"
)
SRC_AE_ZERO = "الإمارات: لا استقطاع على الإتاوات ولا على الخدمات"
SRC_SA_WHT = "السعودية: 15% على الإتاوات داخلياً؛ سقفُ المعاهدة 7% (جدول الجزائر)"


def algeria_markets() -> tuple[Jurisdiction, ...]:
    """أسواقُ المشترين العشرة + إشارةُ إسنادٍ لكلّ خلية.

    ⛔ ما لم يُقرأ نصُّه يبقى `None`: لا يُخترع معدّلٌ ولا يُفترض صفرٌ غائب.
    """
    return (
        Jurisdiction(
            code="US",
            label_ar="الولايات المتحدة",
            treaty=TreatyState.NONE,
            treaty_note_ar=(
                "لا معاهدة جبائية بين الجزائر والولايات المتحدة: جدولُ الجزائر لا يُدرجها، "
                "وقائمةُ المعاهدات الأمريكية لا تضمّها (FATCA اتفاقيةُ تبادلِ معلوماتٍ لا معاهدةُ ضرائب)."
            ),
            service_domestic_bp=0,
            service_treaty_bp=None,
            royalty_domestic_bp=3000,
            royalty_treaty_bp=None,
            royalty_treaty_alt_bp=None,
            service_note_ar=(
                "🟢 الخدمةُ المؤدّاة كليّاً خارج الولايات المتحدة دخلٌ أجنبيّ المصدر ⇒ لا استقطاعَ "
                "الفصل الثالث. القيد الحاسم: ألّا يُوصَف العملُ بأنّه إتاوةُ ترخيص."
            ),
            royalty_note_ar=(
                "🟢 الإتاوةُ دخلٌ أمريكيُّ المصدر ⇒ 30% نظامياً وبلا معاهدة ⇒ لا تخفيف. "
                "الزيادةُ المطلوبةُ على الفاتورة لبلوغ الصافي نفسه: +42.86%."
            ),
            source_ar=f"{SRC_TREATY_NETWORK} · {SRC_IRS_515}",
        ),
        Jurisdiction(
            code="FR",
            label_ar="فرنسا",
            treaty=TreatyState.IN_FORCE,
            treaty_note_ar=(
                "معاهدةُ 1974 المعدَّلة سارية (BOFiP BOI-INT-CVB-DZA). ملاحظةُ عدمِ تناظر: "
                "المعدّلاتُ تختلف بحسب اتجاه المصدر."
            ),
            service_domestic_bp=3333,
            service_treaty_bp=None,
            royalty_domestic_bp=3333,
            royalty_treaty_bp=500,
            royalty_treaty_alt_bp=1000,
            service_note_ar=(
                "🟢 م182 CGI: استقطاعُ 33⅓% على «prestations fournies ou utilisées en France». "
                "⚠️ وخلافاً للولايات المتحدة، الخدمةُ **ليست** معفاةً داخلياً. وهل تُحصّنها المعاهدة؟ "
                "⛔ غيرُ مُسند في هذه الوحدة ⇒ الخليةُ تُمنع ولا تُقتبس."
            ),
            royalty_note_ar=(
                "🟢 سقفُ المعاهدة: 5% لحقوق المؤلف الأدبي/الفني/العلمي، و10% في غيرها حين يكون "
                "المصدرُ فرنسا (م5 من الملاحظات). ⚙️ وشمولُ البرمجيات لعبارة «مؤلف علمي» مسألةُ "
                "وصفٍ تُحسم بكتابٍ لا بافتراض."
            ),
            source_ar=f"{SRC_TREATY_NETWORK} · {SRC_FR_182B}",
        ),
        Jurisdiction(
            code="ES",
            label_ar="إسبانيا",
            treaty=TreatyState.IN_FORCE,
            treaty_note_ar="معاهدةٌ سارية (جدول الجزائر: 7/14% على الإتاوات)",
            service_domestic_bp=2400,
            service_treaty_bp=None,
            royalty_domestic_bp=2400,
            royalty_treaty_bp=700,
            royalty_treaty_alt_bp=1400,
            service_note_ar=(
                "⚠️ سندٌ ثانويّ متقاطع: 24% على «الخدمات التقنية» لغير المقيمين. السعودُ "
                "الأوّليةُ لصياغة الخدمة غيرُ مقروءةٍ هنا ⇒ الخليةُ تُمنع."
            ),
            royalty_note_ar=(
                "⚠️ 24% داخلياً، وسقفُ المعاهدة 7%–14% بحسب الوصف والمالك المنتفع ⇒ نطاقٌ لا رقم."
            ),
            source_ar=f"{SRC_TREATY_NETWORK} · {SRC_ES_IRNR}",
        ),
        Jurisdiction(
            code="IT",
            label_ar="إيطاليا",
            treaty=TreatyState.IN_FORCE,
            treaty_note_ar="معاهدةٌ سارية (جدول الجزائر: 5/15% على الإتاوات)",
            service_domestic_bp=None,
            service_treaty_bp=None,
            royalty_domestic_bp=3000,
            royalty_treaty_bp=500,
            royalty_treaty_alt_bp=1500,
            service_note_ar=(
                "⛔ المعدّلُ الداخلي على مقابل الخدمات لم يُقرأ نصُّه ⇒ `None`: لا صفرٌ مفترضٌ "
                "ولا استنتاجٌ من معاملة الإتاوات."
            ),
            royalty_note_ar="⚠️ 30% داخلياً (سندٌ ثانويّ) وسقفُ المعاهدة 5%–15% ⇒ نطاق.",
            source_ar=f"{SRC_TREATY_NETWORK}",
        ),
        Jurisdiction(
            code="DE",
            label_ar="ألمانيا",
            treaty=TreatyState.IN_FORCE,
            treaty_note_ar="معاهدةٌ سارية (جدول الجزائر: 10% على الإتاوات)",
            service_domestic_bp=0,
            service_treaty_bp=None,
            royalty_domestic_bp=1583,
            royalty_treaty_bp=1000,
            royalty_treaty_alt_bp=None,
            service_note_ar=(
                "🟢 §50a EStG لا يشمل «مقابلَ خدمةٍ حقيقيّ»؛ رسومُ الإدارة والخدمات مُستبعَدةٌ "
                "من الاستقطاع ⇒ صفرٌ مُسند."
            ),
            royalty_note_ar="🟢 15% + 5.5% تضامن = 15.825%؛ سقفُ المعاهدة مع الجزائر 10%.",
            source_ar=f"{SRC_TREATY_NETWORK} · {SRC_DE_50A}",
        ),
        Jurisdiction(
            code="UK",
            label_ar="المملكة المتحدة",
            treaty=TreatyState.IN_FORCE,
            treaty_note_ar=(
                "معاهدةٌ دخلت حيّز النفاذ في الجزائر 2017-01-01 (حاشية 6 في جدول الجزائر)"
            ),
            service_domestic_bp=0,
            service_treaty_bp=None,
            royalty_domestic_bp=2000,
            royalty_treaty_bp=1000,
            royalty_treaty_alt_bp=None,
            service_note_ar=(
                "⚙️ لا نظامَ استقطاعٍ بريطانيٌّ على مقابل الخدمات المدفوع لغير مقيم (الاستقطاعُ "
                "يقع على الإتاوات والفوائد والمدفوعات السنوية) ⇒ صفرٌ بنيويّ يُطلب له تأكيدٌ كتابيّ "
                "قبل أول فاتورة."
            ),
            royalty_note_ar="⚠️ 20% داخلياً، وسقفُ المعاهدة 10% (جدول الجزائر).",
            source_ar=f"{SRC_TREATY_NETWORK} · {SRC_UK_ROYALTY}",
        ),
        Jurisdiction(
            code="NL",
            label_ar="هولندا",
            treaty=TreatyState.UNSTATED,
            treaty_note_ar=(
                "⚠️ تعارضٌ مُعلن: جدولُ الجزائر (PwC) لا يُدرج هولندا، ومصادرُ عامّة تتحدث عن "
                "معاهدة ⇒ يُسجَّل التعارض ولا يُحسم بمتوسط. والأثرُ منعدمٌ هنا لأن المعدّلَ الداخلي صفر."
            ),
            service_domestic_bp=0,
            service_treaty_bp=None,
            royalty_domestic_bp=0,
            royalty_treaty_bp=None,
            royalty_treaty_alt_bp=None,
            service_note_ar="⚙️ لا استقطاعَ هولندياً على مقابل الخدمات ⇒ صفرٌ مستقلٌّ عن المعاهدة.",
            royalty_note_ar=(
                "🟢 لا استقطاعَ هولندياً على الإتاوات ⇒ الخليةُ قابلةٌ للاقتباس رغم تعارض "
                "حالة المعاهدة — وهذا هو حدُّ «الصفرِ لا يحتاج معاهدة»."
            ),
            source_ar=f"{SRC_NL_ZERO} · {SRC_TREATY_NETWORK}",
        ),
        Jurisdiction(
            code="CH",
            label_ar="سويسرا",
            treaty=TreatyState.IN_FORCE,
            treaty_note_ar="معاهدةٌ سارية (جدول الجزائر: 10% على الإتاوات)",
            service_domestic_bp=0,
            service_treaty_bp=None,
            royalty_domestic_bp=0,
            royalty_treaty_bp=None,
            royalty_treaty_alt_bp=None,
            service_note_ar="⚙️ لا استقطاعَ سويسرياً على مقابل الخدمات.",
            royalty_note_ar="🟢 لا استقطاعَ سويسرياً على الإتاوات (الاستقطاعُ على التوزيعات/الفوائد).",
            source_ar=f"{SRC_CH_ZERO} · {SRC_TREATY_NETWORK}",
        ),
        Jurisdiction(
            code="CA",
            label_ar="كندا",
            treaty=TreatyState.IN_FORCE,
            treaty_note_ar="معاهدةٌ سارية (جدول الجزائر: 15% على الإتاوات)",
            service_domestic_bp=0,
            service_treaty_bp=None,
            royalty_domestic_bp=2500,
            royalty_treaty_bp=1500,
            royalty_treaty_alt_bp=None,
            service_note_ar=(
                "🟢 النظام 105 يقع على مقابل خدماتٍ **مؤدّاةٍ في كندا**؛ وما يُؤدّى خارجها لا "
                "استقطاعَ عليه ⇒ صفرٌ مُسند بشرطِ ألّا يُؤدّى العملُ على الأرض الكندية."
            ),
            royalty_note_ar="🟢 25% داخلياً وسقفُ المعاهدة 15%.",
            source_ar=f"{SRC_TREATY_NETWORK} · {SRC_CA_105}",
        ),
        Jurisdiction(
            code="AE",
            label_ar="الإمارات",
            treaty=TreatyState.IN_FORCE,
            treaty_note_ar="معاهدةٌ سارية (جدول الجزائر: 10% على الإتاوات — أي سقفُ ما تستقطعه الجزائر)",
            service_domestic_bp=0,
            service_treaty_bp=None,
            royalty_domestic_bp=0,
            royalty_treaty_bp=None,
            royalty_treaty_alt_bp=None,
            service_note_ar="⚙️ لا استقطاعَ إماراتياً على مقابل الخدمات.",
            royalty_note_ar="🟢 لا استقطاعَ إماراتياً على الإتاوات.",
            source_ar=f"{SRC_AE_ZERO} · {SRC_TREATY_NETWORK}",
        ),
        Jurisdiction(
            code="SA",
            label_ar="السعودية",
            treaty=TreatyState.IN_FORCE,
            treaty_note_ar="معاهدةٌ سارية (جدول الجزائر: 7% على الإتاوات)",
            service_domestic_bp=None,
            service_treaty_bp=None,
            royalty_domestic_bp=1500,
            royalty_treaty_bp=700,
            royalty_treaty_alt_bp=None,
            service_note_ar=(
                "⛔ المعدّلُ الداخلي على مقابل الخدمات لم يُقرأ نصُّه ⇒ `None` ولا افتراض."
            ),
            royalty_note_ar="⚠️ 15% داخلياً وسقفُ المعاهدة 7%.",
            source_ar=f"{SRC_TREATY_NETWORK} · {SRC_SA_WHT}",
        ),
    )


def wod_catalog() -> Catalog:
    """فهرسُ المتطلَّبات والقدرات: كلُّ قدرةٍ مباحة إلّا ما حظرته العقيدةُ نصّاً."""

    requirements = (
        Requirement(
            "legal_capacity",
            "أهليةُ التعاقد (شخصٌ طبيعي/ANAE)",
            RequirementKind.LEGAL,
            ("contract_capacity", "an_ae_registration"),
        ),
        Requirement(
            "export_declaration",
            "تصريحُ المشروع المصدَّر مودَعٌ لدى المصرف قبل التوقيع (K2)",
            RequirementKind.DOCTRINE,
            ("bank_export_declaration",),
        ),
        Requirement(
            "supplier_tax_form",
            "استمارةُ المورّد الضريبية (W-8BEN/W-8BEN-E وإقرارُ الإقامة)",
            RequirementKind.LEGAL,
            ("form_filling",),
        ),
        Requirement(
            "sanctions_screen",
            "فحصُ العقوبات وقوائمُ PEP",
            RequirementKind.LEGAL,
            ("form_filling",),
        ),
        Requirement(
            "treaty_certificate",
            "شهادةُ الإقامة الجبائية لمنح سقف المعاهدة",
            RequirementKind.LEGAL,
            ("tax_residence_certificate",),
        ),
        Requirement(
            "contract_paperwork",
            "مراجعةُ اتفاقية الخدمة/السرّية (MSA/NDA/SOW)",
            RequirementKind.COMMERCIAL,
            ("msa_nda_review",),
        ),
        Requirement(
            "payment_rail",
            "سكّةُ الدفع المقبولةُ عند المشتري",
            RequirementKind.COMMERCIAL,
            (
                "wire_details_swift",
                "marketplace_mor_rail",
                "us_local_bank_account",
                "crypto_settlement",
            ),
        ),
        Requirement(
            "data_protection",
            "اتفاقيةُ معالجة بيانات (م28 GDPR) + شروطٌ نموذجيةٌ للتحويل (م46)",
            RequirementKind.LEGAL,
            ("dpa_sccs_pack",),
        ),
        Requirement(
            "security_review",
            "استبيانُ أمنِ المورّد (بنودُ التشفير والوصول والحوادث)",
            RequirementKind.COMMERCIAL,
            ("security_questionnaire_pack",),
        ),
        Requirement(
            "tax_clearance",
            "تحقّقٌ كتابيٌّ من معاملةٍ ضريبية قبل الفاتورة (حيث الخلية غيرُ مُسندة)",
            RequirementKind.LEGAL,
            ("tax_ruling_clearance",),
        ),
        Requirement(
            "public_eligibility",
            "ملفُّ أهليةٍ لمناقصةٍ عامّة (إقرارُ المشغّل الاقتصادي وتأهيلُه)",
            RequirementKind.COMMERCIAL,
            ("public_procurement_dossier",),
        ),
        Requirement(
            "local_agent",
            "وكيلٌ محلّيٌّ أو شريكٌ مسجَّلٌ عند المشتري الخليجي",
            RequirementKind.COMMERCIAL,
            ("local_agent_agreement",),
        ),
        Requirement(
            "indemnity_insurance",
            "تأمينُ مسؤوليةٍ مهنية (سقفٌ تعاقدي) — كلفتُه المالية خارج نطاق هذه الوحدة",
            RequirementKind.COMMERCIAL,
            ("insurance_pi_1m",),
        ),
        Requirement(
            "certification_soc2",
            "شهادةُ تدقيقٍ تقني (SOC 2/ISO 27001)",
            RequirementKind.COMMERCIAL,
            ("soc2_type1",),
        ),
        Requirement(
            "commercial_reference",
            "مرجعٌ تجاريٌّ قابلٌ للتحقّق",
            RequirementKind.COMMERCIAL,
            ("reference_1", "reference_2"),
        ),
        Requirement(
            "psp_jurisdiction_support",
            "ولايةٌ تدعمها منصّةُ الدفع (شرطُ وسيطِ التسجيل)",
            RequirementKind.COMMERCIAL,
            ("psp_supported_entity",),
        ),
    )

    capabilities = (
        Capability("contract_capacity", "قدرةُ التعاقد باسم ANAE", 0, ("legal_capacity",)),
        Capability("an_ae_registration", "سجلُّ المقاول الذاتي (ANAE)", 0, ("legal_capacity",)),
        Capability(
            "bank_export_declaration",
            "تصريحُ التصدير المُودَع (شرطُ الإعفاء من التوطين)",
            0,
            ("export_declaration",),
            note_ar="K2: لا عقدَ قبل إيداع التصريح — شرطٌ لا بندٌ اختياري.",
        ),
        Capability("wire_details_swift", "حسابٌ بالعملة الصعبة + SWIFT", 0, ("payment_rail",)),
        Capability(
            "form_filling",
            "تعبئةُ النماذج (W-8BEN، فحصُ العقوبات، الإقرارات)",
            0,
            ("supplier_tax_form", "sanctions_screen"),
        ),
        Capability(
            "tax_residence_certificate",
            "شهادةُ إقامةٍ جبائية جزائرية",
            2,
            ("treaty_certificate",),
            note_ar="⚠️ لا تُفتح بها فئةٌ اليوم: لا فئةَ تطلبها في هذه النسخة — تُسجَّل لأن سقفَ "
            "المعاهدة لا يُمنح بلا شهادة.",
        ),
        Capability(
            "msa_nda_review",
            "مراجعةُ MSA/NDA/SOW بنموذجٍ جاهز",
            2,
            ("contract_paperwork",),
        ),
        Capability(
            "dpa_sccs_pack",
            "حزمةُ م28 + م46 (DPA وشروطٌ نموذجية)",
            3,
            ("data_protection",),
            note_ar="م28(3) يفرض عقداً مكتوباً مع أيّ معالج، وم46 يفرض آليةً للتحويل خارج EEA.",
        ),
        Capability(
            "security_questionnaire_pack",
            "حزمةُ أجوبةِ استبيان أمنِ المورّد",
            4,
            ("security_review",),
        ),
        Capability(
            "public_procurement_dossier",
            "ملفُّ أهليةِ المناقصات (ESPD/إقرارات)",
            6,
            ("public_eligibility",),
        ),
        Capability(
            "local_agent_agreement",
            "اتفاقُ وكيلٍ محلّي مسجَّل",
            6,
            ("local_agent",),
        ),
        Capability(
            "tax_ruling_clearance",
            "تحقّقٌ كتابيٌّ مسبقٌ من المعاملة الضريبية",
            6,
            ("tax_clearance",),
            note_ar="يُطلَب حيث تكون الخلية `TREATY_COVERAGE_UNSTATED` — والتحقّق قبل الفاتورة "
            "أرخصُ من تصحيحها بعدها.",
        ),
        Capability(
            "insurance_pi_1m",
            "تأمينُ مسؤوليةٍ مهنية",
            8,
            ("indemnity_insurance",),
            note_ar="⛔ الكلفةُ المالية غيرُ منمذَجة: رفضُ اختراعِ رقمٍ ماليٍّ شرطٌ منهجيّ (L9).",
        ),
        Capability(
            "soc2_type1",
            "شهادةُ SOC 2 Type I",
            20,
            ("certification_soc2",),
            note_ar="⛔ الكلفةُ المالية والجهةُ المدقّقة خارج النموذج: تُقاس الأيامُ لا الدولارات.",
        ),
        Capability(
            "marketplace_mor_rail",
            "قناةُ وسيطِ التسجيل (MoR)",
            1,
            ("payment_rail",),
            note_ar="⚠️ تُفتح سريعاً لكنّ احتياطيَّ الوسيط المتدحرج يضع الحصيلة في خرق النظام 26-02 "
            "(نتيجةُ دفعة RSM) ⇒ تُوسَم خرقاً في القياس.",
        ),
        Capability(
            "reference_1",
            "مرجعٌ تجاريّ أوّل",
            0,
            ("commercial_reference",),
            after_first_invoice=True,
        ),
        Capability(
            "reference_2",
            "مرجعٌ تجاريّ ثانٍ",
            0,
            ("commercial_reference",),
            after_first_invoice=True,
        ),
        Capability(
            "us_local_bank_account",
            "حسابٌ مصرفيٌّ أمريكي/كيانٌ أجنبي",
            4,
            ("payment_rail",),
            doctrine=Doctrine.FORBIDDEN_K5,
            note_ar="K5: م126 الأمر 03-11 وم08 النظام 07-01 ⇒ ⛔ محظورٌ بنصّ، لا «مكلف».",
        ),
        Capability(
            "crypto_settlement",
            "تسويةٌ بعملاتٍ مشفّرة",
            1,
            ("payment_rail",),
            doctrine=Doctrine.FORBIDDEN_K1,
            note_ar="K1: تداولُ العملات المشفّرة محظورٌ في الجزائر ⇒ ⛔ لا يُستعمل ولو سهُل.",
        ),
        Capability(
            "psp_supported_entity",
            "كيانٌ في ولايةٍ تدعمها المنصّة",
            6,
            ("psp_jurisdiction_support",),
            doctrine=Doctrine.FORBIDDEN_K5,
            note_ar="الوصفةُ الشائعة (LLC/Mercury/Stripe) محظورةٌ نصّاً على المقيم ⇒ الفئةُ تُترك.",
        ),
    )

    return Catalog(
        requirements={item.id: item for item in requirements},
        capabilities={item.id: item for item in capabilities},
    )


def wod_archetypes() -> tuple[Archetype, ...]:
    """فئاتُ المشترين: متطلَّباتٌ إلزاميةٌ معلنة، وسوقٌ واحدٌ لكلّ فئة."""

    return (
        Archetype(
            id="A0_us_startup_pilot",
            market="US",
            label_ar="شركةٌ ناشئةٌ أمريكية تشتري دفعةً تجريبية صغيرة بعقدٍ قصير",
            mandatory=(
                "legal_capacity",
                "export_declaration",
                "supplier_tax_form",
                "sanctions_screen",
                "payment_rail",
            ),
            rail_note_ar="تحويلٌ بنكيٌّ مباشر إلى الحساب بالعملة الصعبة — بلا وسيط.",
        ),
        Archetype(
            id="A1_us_lab_eval",
            market="US",
            label_ar="مختبرُ نماذج/فريقُ تقييمٍ أمريكي (حزمةُ تقييمٍ أو بيانات)",
            mandatory=(
                "legal_capacity",
                "export_declaration",
                "supplier_tax_form",
                "sanctions_screen",
                "payment_rail",
                "contract_paperwork",
                "security_review",
            ),
        ),
        Archetype(
            id="A2_us_enterprise_sec",
            market="US",
            label_ar="شركةٌ أمريكية متوسطة/كبيرة: فريقُ أمنٍ ومشترياتٌ منظَّمة",
            mandatory=(
                "legal_capacity",
                "export_declaration",
                "supplier_tax_form",
                "sanctions_screen",
                "payment_rail",
                "contract_paperwork",
                "security_review",
                "indemnity_insurance",
                "commercial_reference",
            ),
        ),
        Archetype(
            id="A3_uk_private",
            market="UK",
            label_ar="جهةٌ بريطانية خاصة (حاكميةُ ذكاءٍ اصطناعي أو تقييم)",
            mandatory=(
                "legal_capacity",
                "export_declaration",
                "sanctions_screen",
                "payment_rail",
                "contract_paperwork",
                "data_protection",
            ),
        ),
        Archetype(
            id="A4_de_private",
            market="DE",
            label_ar="شركةٌ ألمانية خاصة (مشترياتٌ منظَّمة، مشهدٌ أوروبي)",
            mandatory=(
                "legal_capacity",
                "export_declaration",
                "sanctions_screen",
                "payment_rail",
                "contract_paperwork",
                "data_protection",
            ),
        ),
        Archetype(
            id="A5_fr_enterprise",
            market="FR",
            label_ar="شركةٌ فرنسية: خدمةٌ تُستعمل في فرنسا ⇒ خليةُ استقطاعٍ غيرِ مُسندة",
            mandatory=(
                "legal_capacity",
                "export_declaration",
                "sanctions_screen",
                "payment_rail",
                "contract_paperwork",
                "data_protection",
                "tax_clearance",
            ),
            rail_note_ar="الدافعُ الفرنسي هو من يقتطع عند المصدر — لا المصدِّر.",
        ),
        Archetype(
            id="A6_eu_public_body",
            market="DE",
            label_ar="جهةٌ عامّةٌ أوروبية (مناقصة): أهليةٌ ومراجعُ وتأمين",
            mandatory=(
                "legal_capacity",
                "export_declaration",
                "sanctions_screen",
                "payment_rail",
                "contract_paperwork",
                "public_eligibility",
                "indemnity_insurance",
                "commercial_reference",
            ),
        ),
        Archetype(
            id="A7_ae_enterprise",
            market="AE",
            label_ar="مؤسسةٌ خليجية (الإمارات): وكيلٌ محلّيٌّ مسجَّل",
            mandatory=(
                "legal_capacity",
                "export_declaration",
                "sanctions_screen",
                "payment_rail",
                "contract_paperwork",
                "local_agent",
            ),
        ),
        Archetype(
            id="A8_us_soc2_enterprise",
            market="US",
            label_ar="مؤسسةٌ أمريكية تشترط شهادة تدقيقٍ تقني (SOC 2)",
            mandatory=(
                "legal_capacity",
                "export_declaration",
                "supplier_tax_form",
                "sanctions_screen",
                "payment_rail",
                "contract_paperwork",
                "security_review",
                "certification_soc2",
            ),
        ),
        Archetype(
            id="A9_marketplace_mor",
            market="US",
            label_ar="منصّةُ وسيطِ تسجيل (MoR) تبيع بالنيابة",
            mandatory=(
                "legal_capacity",
                "export_declaration",
                "supplier_tax_form",
                "payment_rail",
                "psp_jurisdiction_support",
            ),
            rail_note_ar=(
                "⚠️ القناةُ نفسها موضعُ الخرق: احتياطيُّ الوسيط المتدحرج يتجاوز سقف 120 يوماً "
                "(دفعة RSM) ⇒ العبورُ لا يُنتج نقداً سليماً."
            ),
        ),
        Archetype(
            id="A10_ca_private",
            market="CA",
            label_ar="جهةٌ كندية خاصة (تقييمٌ أو حاكمية)",
            mandatory=(
                "legal_capacity",
                "export_declaration",
                "sanctions_screen",
                "payment_rail",
                "contract_paperwork",
            ),
        ),
        Archetype(
            id="A11_nl_reference_buyer",
            market="NL",
            label_ar="جهةٌ هولندية تشترط مرجعاً تجارياً قبل التوقيع",
            mandatory=(
                "legal_capacity",
                "export_declaration",
                "sanctions_screen",
                "payment_rail",
                "contract_paperwork",
                "commercial_reference",
            ),
        ),
    )


#: الخطُّ الأساسيّ المعلن: ما نملكه فعلاً اليوم — لا ما نستطيع تعبئته.
DEFAULT_HELD: tuple[str, ...] = (
    "contract_capacity",
    "an_ae_registration",
    "bank_export_declaration",
    "wire_details_swift",
    "form_filling",
)

#: خرقُ السكّة المعلن (من دفعة RSM): فئةٌ عابرةٌ لكن قناتُها تُنتج خرقاً نظاميّاً.
DEFAULT_RAIL_CONFLICTS: Mapping[str, str] = MappingProxyType(
    {
        "A9_marketplace_mor": (
            "احتياطيٌّ متدحرج 10%–25% بنافذة 90–180 يوماً يتجاوز سقف 120 يوماً في النظام 26-02 "
            "(نموذج RSM: 11 من 24 تركيبة في خرق) ⇒ ⛔ لا يُبنى رقمٌ على هذه القناة قبل حسم النافذة."
        )
    }
)

#: ميزانيةُ الفتح المعلنة في القياس (وحدةُ جهدٍ = يوم ⚙️).
DEFAULT_UNLOCK_BUDGET = 8


def catalog_view(catalog: Catalog) -> dict[str, dict[str, object]]:
    """عرضٌ قابلٌ للتسلسل يُستعمل في ملفّ القياس (لا يُعدّل الفهرس)."""

    return {
        "requirements": {
            key: {
                "label_ar": value.label_ar,
                "kind": value.kind.value,
                "satisfied_by": list(value.satisfied_by),
                "note_ar": value.note_ar,
            }
            for key, value in sorted(catalog.requirements.items())
        },
        "capabilities": {
            key: {
                "label_ar": value.label_ar,
                "effort_units": value.effort_units,
                "satisfies": list(value.satisfies),
                "doctrine": value.doctrine.value,
                "after_first_invoice": value.after_first_invoice,
                "note_ar": value.note_ar,
            }
            for key, value in sorted(catalog.capabilities.items())
        },
    }


def jurisdiction_view(jurisdiction: Jurisdiction) -> dict[str, object]:
    """تسلسلُ سوقٍ واحدٍ بكلّ ما يلزم لإعادة الحساب دون قراءة هذه الوحدة."""

    return {
        "code": jurisdiction.code,
        "label_ar": jurisdiction.label_ar,
        "treaty": jurisdiction.treaty.value,
        "treaty_note_ar": jurisdiction.treaty_note_ar,
        "service_domestic_bp": jurisdiction.service_domestic_bp,
        "service_treaty_bp": jurisdiction.service_treaty_bp,
        "royalty_domestic_bp": jurisdiction.royalty_domestic_bp,
        "royalty_treaty_bp": jurisdiction.royalty_treaty_bp,
        "royalty_treaty_alt_bp": jurisdiction.royalty_treaty_alt_bp,
        "service_note_ar": jurisdiction.service_note_ar,
        "royalty_note_ar": jurisdiction.royalty_note_ar,
        "source_ar": jurisdiction.source_ar,
    }


def inputs_fingerprint(payload: Mapping[str, object]) -> str:
    """بصمةُ المُدخلات: تغيّرُ أيّ معدّلٍ أو أيّ متطلَّبٍ يُغيّر البصمة (قاعدةُ إعادة الحساب)."""

    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def measure_all() -> dict[str, object]:
    """القياسُ الكامل: مُدخلاتٌ مُسندة + نتائجُ حتميّة + شروطُ قتل — بلا شبكةٍ ولا ساعة."""

    markets = algeria_markets()
    catalog = wod_catalog()
    archetypes = wod_archetypes()
    held = held_capabilities(catalog, held=DEFAULT_HELD)
    inputs = {
        "as_of": AS_OF.isoformat(),
        "budget_units": DEFAULT_UNLOCK_BUDGET,
        "held_stack": sorted(held),
        "jurisdictions": [jurisdiction_view(item) for item in markets],
        "catalog": catalog_view(catalog),
        "archetypes": [
            {
                "id": item.id,
                "market": item.market,
                "label_ar": item.label_ar,
                "mandatory": list(item.mandatory),
                "rail_note_ar": item.rail_note_ar,
            }
            for item in archetypes
        ],
        "rail_conflicts": dict(DEFAULT_RAIL_CONFLICTS),
    }
    results = summarize(
        markets,
        archetypes,
        catalog,
        held,
        budget_units=DEFAULT_UNLOCK_BUDGET,
        rail_conflicts=DEFAULT_RAIL_CONFLICTS,
    )
    return {
        "$schema_version": "1",
        "batch": "WOD-8",
        "as_of": AS_OF.isoformat(),
        "declared_zeros": {
            "model_runs_executed": 0,
            "client_measurements": 0,
            "invoices_issued": 0,
            "revenue_claim": "NONE",
        },
        "inputs": inputs,
        "inputs_fingerprint": inputs_fingerprint(inputs),
        "results": results,
        "limits_ar": [
            "⛔ ليست رأياً ضريبياً ولا قانونياً: المعاملةُ الفعلية تُحسم بكتابٍ من الجهة المختصة.",
            "⛔ لا يُنمذَج أثرُ الاستقطاع على الإقرار الجزائري (الخصمُ/الائتمانُ الضريبي): خارج النطاق.",
            "⛔ لا أرقامَ ماليةٍ مُخترعة: كلُّ كلفةٍ بوحدة جهدٍ معلنة (أيام ⚙️)، والحاصلُ نسبتٌ لا مبلغ.",
            "⚠️ السوقُ الإسبانية والإيطالية والسعودية على جانب الخدمات غيرُ مُسندةٍ نصّاً ⇒ `None`.",
            "⚠️ تعارضُ حالة هولندا التعاهدية مُعلنٌ لا محسوم؛ والخليةُ قابلةٌ للاقتباس لأن صفرَها داخليّ.",
        ],
    }


__all__ = [
    "AS_OF",
    "BP_SCALE",
    "DEFAULT_HELD",
    "DEFAULT_RAIL_CONFLICTS",
    "DEFAULT_UNLOCK_BUDGET",
    "STDLIB_ONLY",
    "AbStatus",
    "Archetype",
    "ArchetypeVerdict",
    "Capability",
    "Catalog",
    "Characterization",
    "Doctrine",
    "InversionState",
    "Jurisdiction",
    "KillSwitch",
    "NetCapture",
    "RateBasis",
    "RateVerdict",
    "Requirement",
    "RequirementKind",
    "TreatyState",
    "UnlockPlan",
    "algeria_markets",
    "catalog_view",
    "characterization_inversion",
    "effective_rate",
    "entry_frontier",
    "evaluate",
    "held_capabilities",
    "inputs_fingerprint",
    "jurisdiction_view",
    "kill_switches",
    "matrix",
    "measure_all",
    "minimum_unlock_set",
    "module_imports",
    "net_capture",
    "reference_ladder",
    "summarize",
    "wod_archetypes",
    "wod_catalog",
]
