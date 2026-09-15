"""تتالي السحب — RCL (الدفعة الحادية عشرة).

Retraction Cascade Ledger: أيُّ رقمٍ ما زال يُقتبَس بعد أن سُحِب نموذجُه؟

**المشكلةُ التي تقيسها هذه الأداة.**

عشرُ دفعاتٍ أنتجت أرقاماً، والدفعةُ `FCM` (2026-09-15) سحبت نموذجاً واحداً كان
أربعةٌ منها مبنيّةً عليه. المستودعُ يملك عرفاً صارماً للسحب («إضافةٌ لا حذف» —
يُكتب التصحيحُ مؤرَّخاً ويبقى النصّ)، لكنّه **لا يملك أداةً تُجيب السؤال التالي**:

    إن سُحِب النموذج X، فأيُّ ادّعاءٍ في أيّ ملفٍّ قياسٍ صار غيرَ قابلٍ للاقتباس؟

بلا هذه الأداة يكون السحبُ **محلّياً**: يُصحَّح في مكانه، وتبقى الأرقامُ المشتقّةُ
منه حيّةً في ملفاتٍ أخرى وفي وثائقِ البيع. وهذا أسوأ من عدم السحب: وثيقةُ عرضٍ
تقتبس رقماً مسحوباً تُسقِط الصفقةَ **و** المصداقيةَ معاً (D-290 L3).

**ما تقيسه — وما لا تقيسه.**

تقيس ثلاثةَ أشياء، كلّها حتميةٌ من القرص:

1. **سطحُ الاقتباس** (`ledger`): لكلّ ادّعاءٍ مُسندٍ حكمٌ من مجموعةٍ مغلقة —
   `QUOTABLE` · `VOID_WITHDRAWN` · `RECLASSIFIED` · `SURVIVES_NARROWER_GROUND` ·
   `BLOCKED_PENDING_TEXT`. الحكمُ دالةٌ في (ما يعتمد عليه الادّعاء) ∩ (ما سُحِب)،
   ⛔ لا في أهمية الادّعاء ولا في جهد إنتاجه.
2. **القيدُ البديل** (`replacement_constraints`): ما الذي يحلّ محلّ النموذج المسحوب.
   السحبُ بلا بديلٍ ثقبٌ؛ والبديلُ هنا مُسندٌ بالمادة نفسها التي سحبت.
3. **المسارُ الحرج** (`sendable_path`): تصنيفُ البطاقات المفتوحة بحسب **مَن يُغلقها**
   (مالك · باحث · عالم)، ثم حسابُ أصغر مجموعةٍ تجعل أوّلَ عرضٍ قابلاً للإرسال.

⛔ لا تقيس: احتمالات القبول · التسعير · أيَّ رقم إيراد. ⛔ لا تُخرج رأياً قانونياً —
كلُّ حكمٍ تنظيميٍّ هنا موسومٌ بمرجعِه وحالتِه، والنصُّ الحرفيُّ للجريدة الرسمية لم
يُستخرج بعد (بوّابة FCM §5 قائمة).

**القوانين الحاكمة داخل هذا الملفّ.**

1. **السحبُ يُبطل الاشتقاق لا الأصل**: ادّعاءٌ يستند إلى نموذجٍ مسحوب **و** إلى سندٍ
   مستقلّ ⇒ `SURVIVES_NARROWER_GROUND`، ويُعاد إسنادُه لا حذفُه.
2. **الفراغُ `None` لا صفر**: الهامشُ المسحوب ليس «هامشاً صفرياً» — بل كميةٌ
   **غيرُ معرَّفة**. `repatriation_slack_days()` تُرجع `None` بسببٍ منطوق (D-212)،
   و`buffer_days()` ترفع `WithdrawnModelError` لأنّ طلبَها في كودٍ بيعيٍّ خطأٌ لا التباس.
3. **إعادةُ التصنيف ليست حذفاً**: نموذجٌ صحيحٌ في سؤالٍ وخاطئٌ في آخر ⇒
   `RECLASSIFIED` مع تسميةِ السؤالَين، لا إسقاطٌ ولا إبقاء.
4. **المُنفِّذ جزءٌ من القياس**: بطاقةٌ لا يُغلقها الباحث ليست على مساره مهما كانت
   صغيرة؛ ولهذا يُحسَب المسارُ على **المُنفِّذ** لا على الجهد.

القانون: stdlib فقط، لا استيراد من app/ ولا microservices/ — تُشحَن إلى عميلٍ لا يملك
تبعياتنا. المكتبةُ تُرجِع بياناتٍ ولا تطبع (D-281).
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Final

__all__ = [
    "AS_OF",
    "BATCH",
    "CARDS",
    "CLAIMS",
    "CREDIT_CAP_DAYS",
    "CREDIT_INSURED_CAP_DAYS",
    "REPLACEMENT_CONSTRAINTS",
    "WITHDRAWALS",
    "ClaimState",
    "Executor",
    "RetractionError",
    "WithdrawnModelError",
    "adjudicate",
    "buffer_days",
    "card_ledger",
    "credit_term_admissibility",
    "inputs_fingerprint",
    "kill_switches",
    "ledger",
    "closure",
    "measure_all",
    "rail_readiness_gate",
    "repatriation_slack_days",
    "sendable_path",
]

#: تاريخُ تجميد المصادر — ثابتٌ لا يُقرأ من الساعة.
AS_OF: Final = "2026-09-15"

#: رقمُ الدفعة في سجلّ المعرفة (FIV كانت العاشرة — `FIV_MEASUREMENTS.json`).
BATCH: Final = "RCL-11"


class RetractionError(ValueError):
    """قاعدةُ الخطأ في هذه الأداة."""


class WithdrawnModelError(RetractionError):
    """رُفع عند طلب عمليةٍ حسابيةٍ على نموذجٍ مسحوب — الرفضُ لا التقريب.

    لماذا رفعٌ لا `None`؟ لأنّ `None` يُقرأ «لا نعرف بعد»، بينما المطلوبُ هنا
    «هذا السؤالُ لم يعد له جوابٌ صالح». الخلطُ بينهما هو ما يُنتج أرقاماً
    مسحوبةً في وثائقَ بيعية.
    """


# ── 1) أحداثُ السحب — مجموعةٌ مغلقة، كلٌّ بتاريخٍ ومصدرٍ على القرص ───────────────


@dataclass(frozen=True)
class Withdrawal:
    """حدثُ سحبٍ واحد: نموذجٌ أُبطل، بتاريخ، من مصدرٍ على القرص، وببديلٍ مسمّى."""

    withdrawal_id: str
    voided_model: str
    withdrawn_on: str
    source: str
    quote: str
    replaced_by: str | None

    def __post_init__(self) -> None:
        if not self.withdrawal_id.strip() or not self.voided_model.strip():
            raise RetractionError("سحبٌ بلا معرّفٍ أو بلا نموذجٍ مُسمّى — لا يُقتفى أثره.")
        if not self.source.strip():
            raise RetractionError("سحبٌ بلا مصدرٍ على القرص — ادّعاءٌ لا حدث.")


#: أحداثُ السحب المقروءة من القرص. ⛔ لا يُضاف حدثٌ بلا نصٍّ مقتبسٍ ومصدر.
WITHDRAWALS: Final = (
    Withdrawal(
        withdrawal_id="W1",
        voided_model="RSM_DAY_BUDGET",
        withdrawn_on="2026-09-15",
        source="research/fx-hard-currency/FCM.md §2.1",
        quote=(
            "The `gap = 120 - sum(days)` model and its 24-combination table are "
            "**withdrawn**. Article 61 grants no day budget."
        ),
        replaced_by="S_B",
    ),
    Withdrawal(
        withdrawal_id="W2",
        voided_model="RSM_NET60_CEILING",
        withdrawn_on="2026-09-15",
        source="research/fx-hard-currency/FCM.md §2.2",
        quote='The "practical net-60 ceiling" is **withdrawn** as a quantitative inference.',
        replaced_by="S_A",
    ),
    Withdrawal(
        withdrawal_id="W3",
        voided_model="RSM_PENALTY_MULTIPLE",
        withdrawn_on="2026-09-15",
        source="research/fx-hard-currency/FCM.md §2.3",
        quote=(
            "The speculative penalty of 1x-2x the amount is **withdrawn**, replaced "
            "by finding 3."
        ),
        replaced_by="S_D",
    ),
    Withdrawal(
        withdrawal_id="W4",
        voided_model="RSM_48H_DOMICILIATION",
        withdrawn_on="2026-09-15",
        source="research/fx-hard-currency/FCM.md §2.4",
        quote=(
            "The 48-hour domiciliation rule **does not apply** to the exporter class "
            "in question."
        ),
        replaced_by="S_C",
    ),
    Withdrawal(
        withdrawal_id="W5",
        voided_model="RETENTION_50_PERCENT",
        withdrawn_on="2026-09-13",
        source="docs/research/ASSURANCE_CONVERGENCE_SPEC_v1.md C1",
        quote=(
            "instruction 06-2021 art. 4 + Bank of Algeria communiqué 2021-07-18 state "
            "**100%**, services and startups explicitly covered — recorded as **REFUTED**"
        ),
        replaced_by="S_F",
    ),
    Withdrawal(
        withdrawal_id="W6",
        voided_model="NO_MILLENNIUM_VERDICT",
        withdrawn_on="2026-09-12",
        source="docs/research/FRONTIER_CLAIM_LEDGER_2026-09.md A3 ⟦تصحيحٌ مؤرَّخ⟧",
        quote="العبارةُ «⛔ لا مسائل الألفية» في هذا الصفّ **خاطئةٌ يومَ كُتبت**",
        replaced_by=None,
    ),
)

_WITHDRAWN_MODELS: Final = frozenset(w.voided_model for w in WITHDRAWALS)


# ── 2) القيودُ البديلة — ما يحلّ محلّ المسحوب، بالمادة نفسها ────────────────────


@dataclass(frozen=True)
class ReplacementConstraint:
    """قيدٌ نافذٌ بعد السحب: نصٌّ، ومرجع، وما يغيّره في التصميم."""

    constraint_id: str
    statement_ar: str
    source: str
    ref_status: str
    design_consequence_ar: str

    def __post_init__(self) -> None:
        if not self.constraint_id.strip():
            raise RetractionError("قيدٌ بلا معرّف — كيف يُسند إليه ادّعاء؟")


#: حالةُ الإسناد — مجموعةٌ مغلقة (لا «موثوقٌ عادةً»).
REF_STATES: Final = (
    "documented-official",
    "secondary-source-quoting-official",
    "press-reported-awaiting-official-text",
)

REPLACEMENT_CONSTRAINTS: Final = (
    ReplacementConstraint(
        constraint_id="S_A",
        statement_ar="سقفُ أجل الائتمان للمشتري غير المقيم 120 يوماً، و180 بتأمين ائتمانٍ مُسبق",
        source="النظام 26-02 م2 · الجريدة ن°58 (2026-08-12) — منقولٌ في FCM §1 وREADME_NEW_KNOWLEDGE:348",
        ref_status="secondary-source-quoting-official",
        design_consequence_ar=(
            "قيدٌ على **بند العقد** لا على توقيت الترحيل: الآجالُ المقبولة "
            "{t ≤ 120} ∪ {120 < t ≤ 180 ∧ مؤمَّن}. ⛔ لا يستلزم «أقصر = أفضل»."
        ),
    ),
    ReplacementConstraint(
        constraint_id="S_B",
        statement_ar="الترحيلُ مستحقٌّ **يوم يدفع العميلُ غير المقيم**، لا ضمن ميزانية أيام",
        source="النظام 26-02 م2 (يعيد صياغة م61 من النظام 07-01، الفقرة الأخيرة) — FCM §1 نتيجة 1",
        ref_status="secondary-source-quoting-official",
        design_consequence_ar=(
            "الالتزامُ يلحق بلحظةٍ يتحكّم فيها **المشتري** لا البائع ⇒ المتغيّرُ التصميمي "
            "ليس أجل الدفع بل **جاهزيةُ السكّة قبل أن يتمكّن المشتري من الدفع**."
        ),
    ),
    ReplacementConstraint(
        constraint_id="S_C",
        statement_ar="الخدماتُ الرقمية عبر الإنترنت وخدماتُ المؤسسات الناشئة و«المهنيون غير التجّار» مُعفَون من التوطين البنكي، ويُستعاض عنه بتصريح",
        source="النظام 07-01 م57 معدَّلاً بالنظام 21-01 — FCM §1 نتيجة 2",
        ref_status="secondary-source-quoting-official",
        design_consequence_ar=(
            "بوّابةُ الدخول إلى السكّة **تصريحٌ** (وصفُ المشروع + سعرُ الوحدة + تاريخُ "
            "النشر الإلكتروني) لا فتحُ حسابٍ مُسبق — وهذا يُخفّض كلفةَ الاختبار لا أجلَه."
        ),
    ),
    ReplacementConstraint(
        constraint_id="S_D",
        statement_ar="جزاءُ الحصيلة غير الموطَّنة أو المتأخّرة **تحصيلٌ بالدينار**، لا غرامةٌ نقدية",
        source="النظام 07-01 م67 معدَّلاً بالنظام 21-01 — FCM §1 نتيجة 3",
        ref_status="secondary-source-quoting-official",
        design_consequence_ar=(
            "الخطرُ ليس غرامةً قابلةً للتقدير، بل **فقدانُ العملة الصعبة نفسه** — أي أنّ "
            "الخرقَ يُحوِّل الإيرادَ الصَّعب إلى إيرادٍ محليّ (محرَّمٌ هدفاً، §04 D-273)."
        ),
    ),
    ReplacementConstraint(
        constraint_id="S_E",
        statement_ar="النصُّ الحرفيُّ للجريدة الرسمية لم يُستخرج بعد — وكلُّ رقمٍ هنا مشروطٌ بنقل مصدرٍ ثانوي",
        source="research/fx-hard-currency/FCM.md §5 (بوّابةٌ حاجبة قبل أيّ بيع)",
        ref_status="press-reported-awaiting-official-text",
        design_consequence_ar=(
            "⛔ لا يُقتبَس أيُّ رقمٍ تنظيميٍّ في وثيقةِ عرضٍ قبل استخراج نصّ م61 من "
            "`joradp.dz` — والبوّابةُ تُغلَق بالتقاطٍ لا برأي."
        ),
    ),
    ReplacementConstraint(
        constraint_id="S_F",
        statement_ar="نسبةُ الاحتفاظ 100% لا 50%، وتشمل الخدمات والمؤسسات الناشئة نصّاً",
        source="التعليمة 06-2021 م4 + بيانُ بنك الجزائر 2021-07-18 — README_NEW_KNOWLEDGE:350",
        ref_status="secondary-source-quoting-official",
        design_consequence_ar=(
            "«الاحتفاظُ 100%» ليس حريةَ تصرّف: التعليمةُ تُبقيه في حسابٍ بالعملة الصعبة "
            "مقسوماً 80% استيراد / 20% ترقيةُ صادرات — قيدُ **إنفاق** لا قيدُ نسبة."
        ),
    ),
)

_CONSTRAINT_IDS: Final = frozenset(c.constraint_id for c in REPLACEMENT_CONSTRAINTS)

#: سقفُ أجل الائتمان (أيام) — ثابتٌ مسنود، يُقرأ ولا يُخمَّن.
CREDIT_CAP_DAYS: Final = 120
CREDIT_INSURED_CAP_DAYS: Final = 180


# ── 3) سطحُ الاقتباس — ادّعاءٌ، فحكم ─────────────────────────────────────────────


class ClaimState(StrEnum):
    """حالةُ الادّعاء — مجموعةٌ مغلقة. ⛔ لا «موثوقٌ عموماً»."""

    QUOTABLE = "QUOTABLE"
    VOID_WITHDRAWN = "VOID_WITHDRAWN"
    RECLASSIFIED = "RECLASSIFIED"
    SURVIVES_NARROWER_GROUND = "SURVIVES_NARROWER_GROUND"
    BLOCKED_PENDING_TEXT = "BLOCKED_PENDING_TEXT"


@dataclass(frozen=True)
class Claim:
    """ادّعاءٌ مُسندٌ على القرص: أين هو، وعلى ماذا يعتمد، وبأيّ سندٍ مستقلّ."""

    claim_id: str
    batch: str
    artifact: str
    quantity: str
    depends_on: tuple[str, ...]
    independent_grounds: tuple[str, ...] = ()
    reclassified_to: str | None = None
    needs_official_text: bool = False

    def __post_init__(self) -> None:
        if not self.claim_id.strip() or not self.artifact.strip():
            raise RetractionError("ادّعاءٌ بلا معرّفٍ أو بلا موضع — لا يُدقَّق.")
        unknown = set(self.depends_on) - _WITHDRAWN_MODELS - _CONSTRAINT_IDS
        if unknown:
            raise RetractionError(
                f"{self.claim_id}: يعتمد على معرّفاتٍ غير معلَنة: {sorted(unknown)}"
            )
        if self.reclassified_to is not None and not self.reclassified_to.strip():
            raise RetractionError(f"{self.claim_id}: إعادةُ تصنيفٍ بلا هدفٍ مسمّى.")


#: الادّعاءات المُدقَّقة — كلٌّ بموضعه الحرفي على القرص.
CLAIMS: Final = (
    Claim(
        claim_id="C1",
        batch="AHW-4",
        artifact="docs/research/AHW_MEASUREMENTS.json → results.contract_terms.rows[*].per_ref[*].buffer_days",
        quantity="هامشُ أيام التأخير المسموح = سقفُ الترحيل − أجلُ السداد",
        depends_on=("RSM_DAY_BUDGET",),
    ),
    Claim(
        claim_id="C2",
        batch="AHW-4",
        artifact="docs/research/AHW_MEASUREMENTS.json → results.contract_terms.rows[*].robust_under_all_refs",
        quantity="الآجالُ التي تنجو تحت كلِّ مرجع (محسوبٌ بـ AND على الهامش)",
        depends_on=("RSM_DAY_BUDGET",),
        independent_grounds=("S_A",),
    ),
    Claim(
        claim_id="C3",
        batch="AHW-4",
        artifact="shared/research/assurance_window.py:634 buffer_days()",
        quantity="الدالةُ التي تُنتج C1",
        depends_on=("RSM_DAY_BUDGET",),
    ),
    Claim(
        claim_id="C4",
        batch="FXR-6",
        artifact="shared/research/fx_rail.py:375→392 margin_days_to_120",
        quantity="الهامشُ إلى الـ120 يوم لكلّ أجلٍ مرشَّح",
        depends_on=("RSM_DAY_BUDGET",),
    ),
    Claim(
        claim_id="C5",
        batch="FXR-6",
        artifact="shared/research/fx_rail.py:377-390 → status ∈ {COMPLIANT, INSURED_ONLY, PROHIBITED}",
        quantity="تصنيفُ الأجل ضدّ سقف الائتمان",
        depends_on=("S_A",),
        needs_official_text=True,
    ),
    Claim(
        claim_id="C6",
        batch="FXR-6",
        artifact="shared/research/fx_rail.py:418 → deadline = service_realized_day + 120 · breach PAID_AFTER_120",
        quantity="موعدٌ نهائيٌّ يبدأ من تاريخ إنجاز الخدمة",
        depends_on=("RSM_DAY_BUDGET",),
    ),
    Claim(
        claim_id="C7",
        batch="FXR-6",
        artifact="shared/research/fx_rail.py:437 breach NOT_REPATRIATED_ON_PAYMENT_DAY",
        quantity="الترحيلُ يجب أن يقع يومَ الدفع",
        depends_on=("S_B",),
        needs_official_text=True,
    ),
    Claim(
        claim_id="C8",
        batch="VERA-2",
        artifact="shared/research/portable_trust.py:383 repatriation_breach_risk()",
        quantity="P(السداد > الأجل) تحت لوغاريتميٍّ طبيعي مُعلَن",
        depends_on=("RSM_DAY_BUDGET",),
        reclassified_to="مقياسُ خطرِ تدفّقٍ نقدي (متى يدفع المشتري) — ⛔ ليس مقياسَ امتثال",
    ),
    Claim(
        claim_id="C9",
        batch="VERA-2",
        artifact="shared/research/portable_trust.py:424 contract_term_ceiling()",
        quantity="أقصى p50 سدادٍ يُبقي خطر الخرق دون الهدف",
        depends_on=("RSM_DAY_BUDGET",),
        reclassified_to="سقفُ تفاوضٍ نقدي — ⛔ ليس «الرقمَ الذي يُكتب في العقد» امتثالاً",
    ),
    Claim(
        claim_id="C10",
        batch="VERA-2",
        artifact=".memory/vera_remote_acceptance_truth.md N5",
        quantity="«عقودُ خدمات ≤ ٤٥ يوماً صامدة تحت الرقمين (١٢٠ و٣٠٦)»",
        depends_on=("RSM_DAY_BUDGET",),
        independent_grounds=("S_A",),
    ),
    Claim(
        claim_id="C11",
        batch="WOD-8",
        artifact="docs/research/WOD_MEASUREMENTS.json:694 → A9_marketplace_mor",
        quantity="«نموذج RSM: 11 من 24 تركيبة في خرق»",
        depends_on=("RSM_DAY_BUDGET",),
        independent_grounds=("K5_foreign_entity",),
    ),
    Claim(
        claim_id="C12",
        batch="WOD-8",
        artifact="docs/research/WOD_MEASUREMENTS.json → A9 status = BLOCKED_DOCTRINE",
        quantity="حكمُ المنع على فئة وسيط MoR",
        depends_on=("RSM_DAY_BUDGET",),
        independent_grounds=("K5_foreign_entity",),
    ),
    Claim(
        claim_id="C13",
        batch="FXR-6",
        artifact="docs/research/FXR_MEASUREMENTS.json → fx_retention",
        quantity="نسبةُ الاحتفاظ بالعملة الصعبة",
        depends_on=("S_F",),
        needs_official_text=True,
    ),
    Claim(
        claim_id="C14",
        batch="AHW-4",
        artifact="docs/research/AHW_MEASUREMENTS.json → results.contract_terms.min_buffer_days",
        quantity="الهامشُ الأدنى المعلَن = 30 يوماً",
        depends_on=("RSM_DAY_BUDGET",),
    ),
    Claim(
        claim_id="C15",
        batch="WOD-8",
        artifact="docs/research/WOD_MEASUREMENTS.json → A0_us_startup_pilot · effort_units 0 · PASS",
        quantity="الفئةُ الوحيدةُ القابلةُ للفاتورة الأولى",
        depends_on=(),
    ),
)

#: الأسانيدُ المستقلّة المقبولة (خارج نماذج السحب وخارج القيود) — مجموعةٌ مغلقة.
INDEPENDENT_GROUNDS: Final = frozenset({"K5_foreign_entity"})


@dataclass(frozen=True)
class ClaimVerdict:
    """حكمُ ادّعاءٍ واحد: حالة + سببٌ منطوق + ما يُفعل به."""

    claim_id: str
    state: ClaimState
    voided_by: tuple[str, ...]
    surviving_grounds: tuple[str, ...]
    reason_ar: str
    action_ar: str

    def as_dict(self) -> dict[str, object]:
        return {
            "claim_id": self.claim_id,
            "state": str(self.state),
            "voided_by": list(self.voided_by),
            "surviving_grounds": list(self.surviving_grounds),
            "reason_ar": self.reason_ar,
            "action_ar": self.action_ar,
        }


def adjudicate(
    claim: Claim,
    withdrawals: tuple[Withdrawal, ...] = WITHDRAWALS,
) -> ClaimVerdict:
    """حكمُ ادّعاءٍ واحد — دالةٌ حتمية، ⛔ لا وزنَ لأهمية الادّعاء ولا لجهد إنتاجه.

    الترتيبُ مُلزم (لا يُعاد ترتيبه):

    1. لا اعتمادَ على أيّ نموذج ⇒ `QUOTABLE`.
    2. إعادةُ تصنيفٍ معلَنة ⇒ `RECLASSIFIED` — فإعادةُ التصنيف **هي** السندُ الباقي:
       النموذجُ لم يمت، بل تبيّن أنّه يجيب سؤالاً آخر.
    3. اعتمادٌ على مسحوبٍ **بلا** سندٍ مستقل ⇒ `VOID_WITHDRAWN`.
    4. اعتمادٌ على مسحوبٍ **مع** سندٍ مستقل ⇒ `SURVIVES_NARROWER_GROUND` (إعادةُ إسناد).
    5. كلُّ ما سبق سالماً والنصُّ الرسميُّ مطلوب ⇒ `BLOCKED_PENDING_TEXT`.

    ⚠️ القاعدةُ 2 قبل 3 عمداً: لو سبقت `VOID_WITHDRAWN` لأُسقطت `C8`/`C9`
    (`repatriation_breach_risk` و`contract_term_ceiling`) وهما مقياسان صالحان في
    سؤالِ التدفّق النقدي — والحذفُ هنا إتلافُ معرفةٍ لا تصحيحُها.
    """
    if claim.reclassified_to is not None and not claim.reclassified_to.strip():
        raise RetractionError(f"{claim.claim_id}: إعادةُ تصنيفٍ بلا هدف.")

    voided = tuple(
        w.withdrawal_id for w in withdrawals if w.voided_model in claim.depends_on
    )
    #: السندُ الباقي: إمّا سندٌ مستقلٌّ مسمّى، أو قيدٌ بديلٌ نافذ — من الحقلَين معاً.
    grounds = tuple(
        dict.fromkeys(
            [
                g
                for g in claim.independent_grounds
                if g in INDEPENDENT_GROUNDS or g in _CONSTRAINT_IDS
            ]
            + [g for g in claim.depends_on if g in _CONSTRAINT_IDS]
        )
    )

    if not claim.depends_on:
        state = ClaimState.QUOTABLE
        reason = "لا يعتمد على أيّ نموذج — لا يصل إليه سحب."
        action = "يُقتبَس كما هو."
    elif claim.reclassified_to is not None:
        state = ClaimState.RECLASSIFIED
        reason = (
            f"سندُه الأصلي ({', '.join(voided) or '—'}) مسحوب، لكنّ النموذجَ سليمٌ في "
            "سؤالٍ وخاطئٌ في السؤال الذي سُمّي به."
        )
        action = f"يُعاد تصنيفُه إلى: {claim.reclassified_to}"
    elif voided and not grounds:
        state = ClaimState.VOID_WITHDRAWN
        reason = (
            f"يعتمد على {', '.join(voided)} ولا يملك سنداً مستقلاً — "
            "الكميةُ غيرُ معرَّفة بعد السحب، لا «صغيرة»."
        )
        action = "⛔ يُسحب من أيّ وثيقةِ عرض؛ ويُستبدل بالقيد البديل إن وُجد."
    elif voided and grounds:
        state = ClaimState.SURVIVES_NARROWER_GROUND
        reason = (
            f"سندُه الأصلي ({', '.join(voided)}) مسحوب، لكنّه يستند كذلك إلى "
            f"{', '.join(grounds)} — فينجو **مضيَّقاً** لا كما كُتب."
        )
        action = "يُعاد إسنادُه كتابةً إلى السند الباقي قبل أيّ اقتباس، ويُسقَط الرقمُ المسحوب."
    elif claim.needs_official_text:
        state = ClaimState.BLOCKED_PENDING_TEXT
        reason = "سالمٌ بنيوياً، لكنّ مرجعَه نقلٌ عن مصدرٍ ثانوي (بوّابة FCM §5)."
        action = "⛔ لا يُقتبَس في عرضٍ قبل التقاط نصّ الجريدة الرسمية."
    else:
        state = ClaimState.QUOTABLE
        reason = "يعتمد على قيدٍ نافذٍ ولم يصل إليه سحب."
        action = "يُقتبَس مع ذكر قيدِه البديل."

    return ClaimVerdict(
        claim_id=claim.claim_id,
        state=state,
        voided_by=voided,
        surviving_grounds=grounds,
        reason_ar=reason,
        action_ar=action,
    )


def ledger(claims: tuple[Claim, ...] = CLAIMS) -> dict[str, object]:
    """سطحُ الاقتباس كاملاً: أحكام + عدٌّ على الحالات + نسبةُ التلوّث."""
    verdicts = [adjudicate(c).as_dict() for c in claims]
    counts: dict[str, int] = {s.value: 0 for s in ClaimState}
    for v in verdicts:
        counts[str(v["state"])] += 1
    total = len(verdicts)
    quotable = counts[ClaimState.QUOTABLE.value]
    return {
        "total": total,
        "by_state": counts,
        "items": verdicts,
        "quotable_share": (quotable / total) if total else None,
        "reading_ar": (
            f"{quotable} من {total} ادّعاءً قابلٌ للاقتباس كما هو؛ والباقي إمّا مسحوبٌ "
            "أو مضيَّقٌ أو معادُ التصنيف أو محجوبٌ حتى النصّ الرسمي. ⛔ النسبةُ "
            "وصفٌ لسطحٍ لا حكمٌ على جودة الدفعات."
        ),
    }


# ── 4) القيدُ البديل محسوباً — لا مروياً ────────────────────────────────────────


def credit_term_admissibility(
    term_days: int,
    credit_insured: bool = False,
) -> dict[str, object]:
    """قيدُ السقف (S_A) — **باقي** السحب، لأنه قيدٌ على البند لا على التوقيت.

    ⛔ لا يُنتج «أقصرُ أفضل»: الترتيبُ على الخطر النقديِّ مسألةُ أداةٍ أخرى
    (`portable_trust`) بعد إعادة تصنيفها.
    """
    if term_days < 0:
        raise RetractionError("أجلُ السداد عددُ أيامٍ غيرُ سالب (0 = دفعٌ مُقدَّم).")
    cap = CREDIT_INSURED_CAP_DAYS if credit_insured else CREDIT_CAP_DAYS
    if term_days <= CREDIT_CAP_DAYS:
        status = "ADMISSIBLE"
    elif credit_insured and term_days <= CREDIT_INSURED_CAP_DAYS:
        status = "ADMISSIBLE_INSURED_ONLY"
    elif term_days <= CREDIT_INSURED_CAP_DAYS:
        status = "NEEDS_CREDIT_INSURANCE"
    else:
        status = "PROHIBITED"
    return {
        "term_days": term_days,
        "credit_insured": credit_insured,
        "applicable_cap_days": cap,
        "status": status,
        "basis": "S_A — النظام 26-02 م2 (نقلٌ عن الجريدة ن°58)",
        "reported_as": "🟢⟨ح⟩ فحصُ بنيةٍ مقابل مرجعٍ مُسند — ⛔ ليس رأياً قانونياً",
    }


def repatriation_slack_days() -> dict[str, object]:
    """هامشُ الترحيل تحت S_B — **`None` لا صفراً** (D-212).

    هذه هي النتيجةُ المحوريةُ في الدفعة: تحت «الترحيلُ يوم الدفع» لا يوجد هامشٌ
    صغيرٌ ولا كبير — توجد **كميةٌ غيرُ معرَّفة**، لأنّ اللحظةَ التي ينشأ عندها
    الالتزام يحدّدها المشتري. ومن هنا يُولد القيدُ الجديد (T4).
    """
    return {
        "slack_days": None,
        "reason": (
            "RSM_DAY_BUDGET مسحوب (W1) — وتحت S_B ينشأ الالتزامُ لحظةَ دفع المشتري، "
            "فلا يبقى مقدارٌ يُطرح منه أجلُ السداد."
        ),
        "replaced_by": "rail_readiness_gate() — الجاهزيةُ قبل الإصدار، لا الهامشُ بعد الأجل",
    }


def buffer_days(term_days: int, cap_days: int = CREDIT_CAP_DAYS) -> int:
    """⛔ مُعطَّلة — ترفع `WithdrawnModelError` دائماً.

    مُبقاة بالاسم نفسه عمداً: أيُّ كودٍ قديمٍ أو وثيقةٍ تستدعيها تسقط فوراً بدل أن
    تُنتج رقماً مسحوباً بهدوء. هذا هو الفارض، لا التعليق.
    """
    raise WithdrawnModelError(
        f"buffer_days({term_days}, {cap_days}) محسوبةٌ على RSM_DAY_BUDGET المسحوب "
        "(W1 · FCM §2.1). الكميةُ غيرُ معرَّفة بعد S_B — استعمل "
        "repatriation_slack_days() وrail_readiness_gate()."
    )


def rail_readiness_gate(
    *,
    rail_declared_ready: bool,
    invoice_issued: bool,
    declaration_filed: bool | None = None,
) -> dict[str, object]:
    """البوّابةُ الجديدة (T4) — لا وجودَ لها في أيّ دفعةٍ سابقة على القرص.

    لماذا وُلدت؟ لأنّ S_B تجعل الالتزامَ لحظياً عند الدفع. فالفاتورةُ تُصدر **قبل**
    أن يتمكّن المشتري من الدفع، وإذا لم تكن السكّةُ جاهزةً لحظةَ وصول الحصيلة وقع
    الخرقُ بلا خطأٍ إجرائيٍّ من أحد. إذن الترتيبُ الإلزامي:

        جاهزيةُ السكّة  ←  إصدارُ الفاتورة  ←  دفعُ المشتري  ←  الترحيل (لحظي)

    ⛔ ليست رأياً قانونياً؛ هي ترتيبُ تبعيّةٍ مشتقٌّ من S_B وS_C.
    """
    breaches: list[str] = []
    if invoice_issued and not rail_declared_ready:
        breaches.append(
            "INVOICE_BEFORE_RAIL — فاتورةٌ صدرت قبل إعلان جاهزية السكّة؛ تحت S_B "
            "يقع الخرقُ لحظةَ الدفع لا لحظةَ الإجراء."
        )
    if invoice_issued and declaration_filed is False:
        breaches.append(
            "DECLARATION_MISSING — التصريحُ المنصوص عليه في م57 (S_C) بديلُ التوطين، "
            "وغيابُه يُبقي الحصيلة غير موطَّنة ⇒ S_D (تحصيلٌ بالدينار)."
        )
    return {
        "rail_declared_ready": rail_declared_ready,
        "invoice_issued": invoice_issued,
        "declaration_filed": declaration_filed,
        "ordering_ar": "جاهزيةُ السكّة ← إصدارُ الفاتورة ← دفعُ المشتري ← الترحيلُ اللحظي",
        "passes": not breaches,
        "breaches": breaches,
        "reported_as": "🟢⟨ح⟩ ترتيبُ تبعيّةٍ مشتقٌّ من S_B وS_C — ⛔ ليس رأياً قانونياً",
    }


# ── 5) المسارُ الحرج — مَن يُغلق البطاقة، لا كم تكلّف ───────────────────────────


class Executor(StrEnum):
    """مَن يملك إغلاق البطاقة — مجموعةٌ مغلقة."""

    OWNER = "OWNER"
    RESEARCHER = "RESEARCHER"
    WORLD = "WORLD"


@dataclass(frozen=True)
class Card:
    """بطاقةٌ مفتوحة على القرص: من يُغلقها، وعلى ماذا تعتمد، وأيّ مسارٍ تخدم."""

    card_id: str
    source: str
    summary_ar: str
    executor: Executor
    depends_on: tuple[str, ...] = field(default=())
    path: str = "A0"

    def __post_init__(self) -> None:
        if not self.card_id.strip():
            raise RetractionError("بطاقةٌ بلا معرّف.")
        if self.path not in PATHS:
            raise RetractionError(f"{self.card_id}: مسارٌ غير معلَن {self.path!r}")


#: المساراتُ المعلَنة — مجموعةٌ مغلقة. `A0` = الفاتورةُ الأولى (WOD) ·
#: `CH` = قنواتُ FIV · `FX` = السكّةُ التنظيمية.
PATHS: Final = frozenset({"A0", "CH", "FX"})


#: البطاقاتُ المفتوحة كما وردت في FIV (T71–T76) وWOD (T65–T70)، + بطاقتا هذه الدفعة.
#: ⚠️ التبعياتُ تُعرَّف بعد البناء لأنّ `Card` مجمَّدة — يُتحقّق منها في `__post_init__`.
_CARDS_RAW: Final = (
    ("T65", "HARD_CURRENCY_NEW_KNOWLEDGE_WOD.md:218", "النصُّ الأوّليّ لأربع خلايا مُمنوعة", Executor.RESEARCHER, (), "FX"),
    ("T66", "HARD_CURRENCY_NEW_KNOWLEDGE_WOD.md:219", "حزمةُ الجهد-5 (`msa_nda_review` + `dpa_sccs_pack`) قبل أيّ عرض", Executor.RESEARCHER, (), "A0"),
    ("T67", "HARD_CURRENCY_NEW_KNOWLEDGE_WOD.md:220", "عرضٌ بثلاث صيغِ وصف + جوابُ مشترٍ", Executor.WORLD, ("T66",), "A0"),
    ("T68", "HARD_CURRENCY_NEW_KNOWLEDGE_WOD.md:221", "سطرُ «تاريخ إنجاز الخدمة» في نموذج العقد", Executor.RESEARCHER, (), "A0"),
    ("T69", "HARD_CURRENCY_NEW_KNOWLEDGE_WOD.md:222", "سؤالُ مشترٍ فرنسي/إسباني عن الاستقطاع", Executor.WORLD, (), "FX"),
    ("T70", "HARD_CURRENCY_NEW_KNOWLEDGE_WOD.md:223", "اختبارُ A0 على مشترٍ حقيقيّ بعقدٍ قصير", Executor.WORLD, ("T66", "T68", "T78"), "A0"),
    ("T71", "HARD_CURRENCY_NEW_KNOWLEDGE_FIV.md:177", "سؤالٌ مكتوبٌ واحد إلى Prime — «التنفيذُ بيد المالك»", Executor.OWNER, (), "CH"),
    ("T72", "HARD_CURRENCY_NEW_KNOWLEDGE_FIV.md:178", "سؤالُ DataVendor — بعد إغلاق T71", Executor.OWNER, ("T71",), "CH"),
    ("T73", "HARD_CURRENCY_NEW_KNOWLEDGE_FIV.md:179", "مسودّةُ طلب مكافأة (CH2) — محجوزةٌ على ردّ T71", Executor.RESEARCHER, ("T71",), "CH"),
    ("T74", "HARD_CURRENCY_NEW_KNOWLEDGE_FIV.md:180", "إعادةُ مسحٍ مصغَّرٍ لسوق التدقيق شهرياً", Executor.RESEARCHER, (), "CH"),
    ("T75", "HARD_CURRENCY_NEW_KNOWLEDGE_FIV.md:181", "التقاطُ شارة التوظيف أو إسقاطُها", Executor.RESEARCHER, (), "CH"),
    ("T76", "HARD_CURRENCY_NEW_KNOWLEDGE_FIV.md:182", "قرارُ مالكٍ في ترخيص codebase قبل أيّ تحرّك CH5", Executor.OWNER, (), "CH"),
    ("T77", "RCL-11 (هذه الدفعة)", "التقاطُ نصّ م61 + م57 + م67 من `joradp.dz` — يُغلق S_E", Executor.RESEARCHER, (), "FX"),
    ("T78", "RCL-11 (هذه الدفعة)", "إعلانُ جاهزية السكّة + تقديمُ تصريح م57 — بوابة T4 قبل أيّ فاتورة", Executor.RESEARCHER, ("T77",), "A0"),
)

_ALL_CARDS: Final = tuple(
    Card(card_id=c, source=s, summary_ar=t, executor=e, depends_on=d, path=p)
    for c, s, t, e, d, p in _CARDS_RAW
)

CARDS: Final = _ALL_CARDS

_CARD_BY_ID: Final = {c.card_id: c for c in _ALL_CARDS}


def _validate_card_graph(cards: tuple[Card, ...]) -> None:
    """تحقّقُ ما بعد البناء: تبعياتٌ معلَنة فقط، وبلا دورة.

    لماذا بعد البناء؟ لأنّ `Card` مجمَّدة والتبعياتُ تُعرَّف داخل المجموعة نفسها —
    والتحقّقُ داخل `__post_init__` يستدعي المجموعةَ قبل وجودها. الفحصُ هنا لا هناك.
    """
    known = frozenset(c.card_id for c in cards)
    if len(known) != len(cards):
        raise RetractionError("معرّفاتُ بطاقاتٍ مكرَّرة — أيُّهما يُغلق؟")
    local = {c.card_id: c for c in cards}
    for card in cards:
        unknown = set(card.depends_on) - known
        if unknown:
            raise RetractionError(
                f"{card.card_id}: تعتمد على بطاقاتٍ غير معلَنة {sorted(unknown)}"
            )
    # كشفُ الدورة: إن لم يُغلق الترتيبُ كلَّ البطاقات فثمّة دورة.
    # ⚠️ على `local` لا على `_CARD_BY_ID` — وإلا فُحص رسمُ الوحدة لا الرسمُ المُمرَّر.
    closed: set[str] = set()
    pending = set(known)
    while pending:
        ready = {c for c in pending if set(local[c].depends_on) <= closed}
        if not ready:
            raise RetractionError(f"دورةٌ في تبعيات البطاقات: {sorted(pending)}")
        closed |= ready
        pending -= ready


_validate_card_graph(_ALL_CARDS)


def card_ledger(cards: tuple[Card, ...] = CARDS) -> dict[str, object]:
    """عدٌّ على المُنفِّذ وعلى المسار — لا على الجهد."""
    by_exec: dict[str, int] = {e.value: 0 for e in Executor}
    by_path: dict[str, int] = {}
    for c in cards:
        by_exec[c.executor.value] += 1
        by_path[c.path] = by_path.get(c.path, 0) + 1
    return {
        "total": len(cards),
        "by_executor": by_exec,
        "by_path": by_path,
        "items": [
            {
                "card_id": c.card_id,
                "executor": c.executor.value,
                "path": c.path,
                "depends_on": list(c.depends_on),
                "summary_ar": c.summary_ar,
                "source": c.source,
            }
            for c in cards
        ],
    }


def sendable_path(target: str = "T70") -> dict[str, object]:
    """أصغرُ مجموعةِ بطاقاتٍ تُغلق الهدف — محسوبةٌ على التبعيات، مع فصلٍ بحسب المُنفِّذ.

    المُخرَجُ المقصود: هل أقصرُ مسارٍ إلى أوّل عرضٍ قابلٍ للإرسال يمرّ بالمالك أم لا؟
    هذا سؤالٌ يُجاب بعدٍّ لا برأي.
    """
    if target not in _CARD_BY_ID:
        raise RetractionError(f"هدفٌ غيرُ معلَن: {target}")

    needed: list[str] = []
    seen: set[str] = set()
    stack = [target]
    while stack:
        cid = stack.pop()
        if cid in seen:
            continue
        seen.add(cid)
        needed.append(cid)
        stack.extend(_CARD_BY_ID[cid].depends_on)
    needed_set = frozenset(needed)

    # ترتيبٌ topological بسيط: التابع بعد متبوعه.
    ordered: list[str] = []
    while needed_set:
        ready = sorted(
            cid
            for cid in needed_set
            if all(d in ordered for d in _CARD_BY_ID[cid].depends_on)
        )
        if not ready:  # pragma: no cover - دورةٌ مستحيلةٌ في بياناتٍ معلَنة
            raise RetractionError("دورةٌ في تبعيات البطاقات.")
        ordered.extend(ready)
        needed_set -= frozenset(ready)

    executors = {cid: _CARD_BY_ID[cid].executor for cid in ordered}
    owner_blocking = sorted(c for c, e in executors.items() if e is Executor.OWNER)
    return {
        "target": target,
        "target_path": _CARD_BY_ID[target].path,
        "minimum_set": ordered,
        "length": len(ordered),
        "by_executor": {
            e.value: sorted(c for c, x in executors.items() if x is e) for e in Executor
        },
        "owner_blocking": owner_blocking,
        "owner_free": not owner_blocking,
        "reading_ar": (
            "المسارُ لا يمرّ بالمالك إطلاقاً — كلُّ بطاقاتِه بيد الباحث."
            if not owner_blocking
            else f"المسارُ محجوبٌ بالمالك عند: {', '.join(owner_blocking)}."
        ),
    }


def closure(card_id: str) -> frozenset[str]:
    """إغلاقُ التبعيات: البطاقةُ وكلُّ ما يجب أن يُغلق قبلها."""
    seen: set[str] = set()
    stack = [card_id]
    while stack:
        cid = stack.pop()
        if cid in seen:
            continue
        seen.add(cid)
        stack.extend(_CARD_BY_ID[cid].depends_on)
    return frozenset(seen)


def path_disjointness(path_a: str = "A0", path_b: str = "CH") -> dict[str, object]:
    """هل يتقاطع مسارُ A0 (الفاتورة الأولى) مع مسارِ القنوات (FIV)؟

    فصلان لا فصلٌ واحد — والفرقُ بينهما هو النتيجة:

    * **على البطاقات** (التسمية): هل تخدم البطاقةُ نفسُها المسارَين؟
    * **على الإغلاق** (التبعيات): هل يحتاج مسارٌ إلى بطاقةٍ من الآخر؟

    قد يكون المساران منفصلَين بالتسمية ومتشابكَين بالتبعية — وعندها يكون حجبُ
    أحدهما **معطِّلاً** للآخر رغم أنّ أحداً لا يشارك فيه.
    """
    a = frozenset(c.card_id for c in CARDS if c.path == path_a)
    b = frozenset(c.card_id for c in CARDS if c.path == path_b)
    a_closure = frozenset().union(*(closure(c) for c in a)) if a else frozenset()
    b_closure = frozenset().union(*(closure(c) for c in b)) if b else frozenset()
    shared = sorted((a_closure & b_closure) - (a & b))
    return {
        "path_a": sorted(a),
        "path_b": sorted(b),
        "cards_intersection": sorted(a & b),
        "cards_disjoint": not (a & b),
        "closure_intersection": shared,
        "closure_disjoint": not shared,
        "reading_ar": (
            f"منفصلان على البطاقات **ومتشابكان على الإغلاق** عبر: {', '.join(shared)} — "
            "فحجبُ الثاني يُعطّل الأول رغم أنّه لا يشارك في أيٍّ من بطاقاته."
            if shared and not (a & b)
            else (
                f"منفصلان تماماً — حجبُ {path_b} لا يُعطّل {path_a}."
                if not (a & b)
                else f"يتشاركان البطاقات: {sorted(a & b)}."
            )
        ),
    }


# ── 6) شروطُ القتل — مجموعةٌ مغلقة لكلّ دفعة (عرف WOD/AHW، ⛔ لا تسلسلَ عامّاً) ──


def kill_switches() -> list[dict[str, object]]:
    """K1–K5 لهذه الدفعة، ولكلٍّ برهانٌ سلبيٌّ في الاختبارات."""
    return [
        {
            "id": "K1",
            "condition_ar": "يُستخرج نصُّ م61 من الجريدة الرسمية فيُثبت **ميزانيةَ أيام**",
            "consequence_ar": "W1 باطلة، ويعود `buffer_days` كميةً معرَّفة — وتُلغى البوّابة T4",
            "observable_ar": "اقتباسٌ حرفيٌّ من `joradp.dz` (T77)",
        },
        {
            "id": "K2",
            "condition_ar": "يدفع مشترٍ واحدٌ وتصل الحصيلةُ بلا تصريح م57 وبلا خرق",
            "consequence_ar": "S_C/S_D أضعفُ من المعلن، وتُنزَل بوابةُ T4 إلى ملاحظة",
            "observable_ar": "إيصالُ تحويلٍ واحد + كشفُ حساب (T70)",
        },
        {
            "id": "K3",
            "condition_ar": "يظهر ادّعاءٌ على القرص يعتمد على مسحوبٍ ولم تلتقطه هذه الأداة",
            "consequence_ar": "سطحُ الاقتباس ناقص، ولا يُقتبَس الحكمُ «x من y قابلٌ للاقتباس»",
            "observable_ar": "بطاقةُ تدقيقٍ واحدة تُخفق في `tests/shared/test_rcl_retraction_cascade.py`",
        },
        {
            "id": "K4",
            "condition_ar": "يُثبت أنّ A0 ليست فئةَ الفاتورة الأولى (C15)",
            "consequence_ar": "المسارُ الحرج كلُّه يُعاد حسابُه على فئةٍ أخرى",
            "observable_ar": "قياسُ WOD مُعاداً بمُدخَلاتٍ محدَّثة",
        },
        {
            "id": "K5",
            "condition_ar": "تُغلق البطاقاتُ كلُّها ولا يُرسل عرضٌ واحد",
            "consequence_ar": "العائقُ ليس المعرفة ولا البطاقات — بل الفاعل (F-06)",
            "observable_ar": "سجلُّ إرسالٍ فارغ بعد إغلاق T66 وT68 وT78",
        },
    ]


# ── 7) الحمولة ──────────────────────────────────────────────────────────────────


def _inputs() -> dict[str, object]:
    """المُدخَلاتُ القانونية — وهي وحدها ما تُبصَم."""
    return {
        "as_of": AS_OF,
        "batch": BATCH,
        "withdrawals": [
            {
                "withdrawal_id": w.withdrawal_id,
                "voided_model": w.voided_model,
                "withdrawn_on": w.withdrawn_on,
                "source": w.source,
                "replaced_by": w.replaced_by,
            }
            for w in WITHDRAWALS
        ],
        "replacement_constraints": [
            {
                "constraint_id": c.constraint_id,
                "ref_status": c.ref_status,
                "source": c.source,
            }
            for c in REPLACEMENT_CONSTRAINTS
        ],
        "claims": [
            {
                "claim_id": c.claim_id,
                "batch": c.batch,
                "artifact": c.artifact,
                "depends_on": list(c.depends_on),
                "independent_grounds": list(c.independent_grounds),
                "reclassified_to": c.reclassified_to,
                "needs_official_text": c.needs_official_text,
            }
            for c in CLAIMS
        ],
        "cards": [
            {
                "card_id": c.card_id,
                "executor": c.executor.value,
                "path": c.path,
                "depends_on": list(c.depends_on),
            }
            for c in CARDS
        ],
        "credit_cap_days": CREDIT_CAP_DAYS,
        "credit_insured_cap_days": CREDIT_INSURED_CAP_DAYS,
    }


def inputs_fingerprint() -> str:
    """بصمةُ المُدخَلات — sha256 محسوبةٌ فعلاً على ترميزٍ قانونيٍّ ثابت."""
    canonical = json.dumps(_inputs(), sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def measure_all() -> dict[str, object]:
    """الحمولةُ الكاملة: أصفارٌ مُعلَنة + مُدخَلات + بصمة + نتائج — حتميةٌ تماماً."""
    surface = ledger()
    path = sendable_path("T70")
    return {
        "$schema_version": "1",
        "as_of": AS_OF,
        "batch": BATCH,
        "declared_zeros": {
            "model_runs_executed": 0,
            "client_measurements": 0,
            "invoices_issued": 0,
            "contracts_signed": 0,
            "offers_sent": 0,
            "official_texts_extracted": 0,
            "rails_declared_ready": 0,
            "revenue_claim": "NONE",
        },
        "inputs": _inputs(),
        "inputs_fingerprint": inputs_fingerprint(),
        "results": {
            "quotable_surface": surface,
            "replacement_constraints": [
                {
                    "constraint_id": c.constraint_id,
                    "statement_ar": c.statement_ar,
                    "source": c.source,
                    "ref_status": c.ref_status,
                    "design_consequence_ar": c.design_consequence_ar,
                }
                for c in REPLACEMENT_CONSTRAINTS
            ],
            "credit_term": {
                "cap_days": CREDIT_CAP_DAYS,
                "insured_cap_days": CREDIT_INSURED_CAP_DAYS,
                "rows": [credit_term_admissibility(t) for t in (0, 15, 30, 45, 60, 90, 120, 150, 180, 270, 360)],
            },
            "repatriation_slack": repatriation_slack_days(),
            "rail_readiness_gate": {
                "cases": [
                    rail_readiness_gate(rail_declared_ready=False, invoice_issued=True),
                    rail_readiness_gate(rail_declared_ready=True, invoice_issued=True, declaration_filed=False),
                    rail_readiness_gate(
                        rail_declared_ready=True, invoice_issued=True, declaration_filed=True
                    ),
                    rail_readiness_gate(rail_declared_ready=False, invoice_issued=False),
                ],
                "new_prerequisite_ar": (
                    "T4: لا تُصدر فاتورةٌ قبل إعلان جاهزية السكّة وتقديم تصريح م57 — "
                    "مشتقٌّ من S_B، ⛔ لا وجودَ له في أيّ دفعةٍ سابقة على القرص."
                ),
            },
            "card_ledger": card_ledger(),
            "sendable_path": path,
            "path_disjointness": {
                "A0_vs_CH": path_disjointness("A0", "CH"),
                "A0_vs_FX": path_disjointness("A0", "FX"),
                "reading_ar": (
                    "الفاتورةُ الأولى (A0) منفصلةٌ عن قنوات FIV (CH) انفصالاً تامّاً، "
                    "لكنّها **متشابكةٌ مع المسار التنظيمي (FX)** عبر T77 — أي أنّ "
                    "استخراجَ نصّ الجريدة الرسمية صار على المسار الحرج لأول دولار."
                ),
            },
            "withdrawal_register": [
                {
                    "withdrawal_id": w.withdrawal_id,
                    "voided_model": w.voided_model,
                    "withdrawn_on": w.withdrawn_on,
                    "source": w.source,
                    "quote": w.quote,
                    "replaced_by": w.replaced_by,
                }
                for w in WITHDRAWALS
            ],
            "kill_switches": kill_switches(),
        },
        "limits_ar": [
            "⛔ ليس رأياً قانونياً ولا ضريبياً — أحكامُ بنيةٍ مقابل مراجعَ مُسندة.",
            "⛔ النصُّ الحرفيُّ للجريدة الرسمية لم يُستخرج (S_E · T77) — وكلُّ قيدٍ تنظيميٍّ هنا مشروطٌ بنقلٍ ثانوي.",
            "⛔ لا رقمَ إيرادٍ ولا تسعير؛ `revenue_claim = NONE`.",
            "⛔ لا خطَّ عرضٍ ثامن — هذه الدفعة لا تضيف إلى `OFFER_CATALOG.json`.",
            "⛔ سطحُ الاقتباس محصورٌ في الادّعاءات المُدرجة في `CLAIMS`؛ وK3 هو شرطُ قتله.",
        ],
    }
