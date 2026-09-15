"""دبوسُ القيم الافتراضية — CPN (الدفعة الثانية عشرة).

CBAM Pin: ما الذي يدفعه المستوردُ فعلاً — لا ما تقولُه الفجوة.

**المشكلةُ التي تقيسها هذه الأداة.**

المستودعُ بنى أطروحةً تجاريةً على جملةٍ واحدة: «القيمةُ الافتراضية عقابية؛ فبائعُ
البيانات الفعلية يوفّر للمستورد الفرق». ثلاثةُ ملفاتٍ حسبت هذا الفرق
(`cbam_value.py` · `markup_gradient.py` · حوضا `CPD`) — واثنان منها استعملا
**معاملَ CBAM في مكانين متناقضين** (0.025 مضروباً في الفجوة مقابل 0.975 مضروباً
في الوفر)، فانتشر الفرقُ بينهما 39× بلا أدنى إشارةٍ إلى التناقض. ولا واحدٌ منها
حسب **تعديلَ التخصيص المجانيّ** (SEFA)، لأنه لم يكن يملك مراجعَ CBAM.

هذه الأداة تُدبِّس الأرقامَ من المصدر الأوّلي وتُخرج الكميةَ التي كانت ناقصة.

**المعرفةُ الجديدة (القانونُ CPN-1: رسمُ المسار).**

الانتقالُ من القيمة الافتراضية إلى البيانات الفعلية **ليس وفراً**؛ إنه مقايضةٌ
بطرفين:

    ما تكسبه = إعفاءُ العلاوة      = SEE_default × mark-up
    ما تدفعه = **رسمُ المسار**     = CBAM_factor × CSCF × (BM_B − BM_A)

`BM_B` هو مرجعُ CBAM المستعمل **حين تُعلَن القيم الافتراضية**، و`BM_A` هو المرجعُ
المستعمل **حين تُعلَن البيانات الفعلية** (ملحق IR 2025/2620، العمودان A وB).
العمودان **ليسا متساويين**: للأسمدة الجزائرية المرجعُ B أكبرُ من A بـ 17×
(اليوريا 0.902 مقابل 0.053) و40× (نترات الأمونيوم 0.767 مقابل 0.019)، وللإسمنت
البورتلاندي الرماديّ B = 0.666 مقابل **A = 0.000**.

⇒ **من يشتري بياناتٍ فعلية يتخلّى عن اعتمادِ تخصيصٍ مجانيٍّ أكبرَ بكثيرٍ مما يكسب
من حذف العلاوة.** الوفرُ الصافي موجبٌ فقط إذا كانت المنشأةُ أنظفَ من
«صافي الرسم المطلوب» = رسمُ المسار − إعفاءُ العلاوة.

**ما تقيسه — وما لا تقيسه.**

تقيس، لكلّ رمز CN مدبوسٍ ولكلّ سنة:

1. **عتبةُ العبور** (`crossover_see`): أعلى انبعاثٍ فعليّ يبقى معه إعلانُ البيانات
   الفعلية أرخصَ من الافتراضية. كلّ مدخلاتها من المصدر الأوّلي ⇒ **بلا أيّ افتراضٍ
   عن المنشأة**. هذا هو المُنتَج: المشتري يقارن رقمَه الخاصّ بعتبتنا.
2. **رسمُ المسار** (`path_toll`) بـ tCO₂e/t وباليورو للطنّ.
3. **أوّلُ سنةٍ قابلةٍ للبيع** (`first_sellable_year`): متى تنقلب العتبةُ فوق
   انبعاثٍ مرشَّح مُعلَن — لأنّ العلاوة تصعد ومعاملَ CBAM يهبط، فالعتبةُ **تتّسع
   كلّ سنة**، والمنتجُ غيرُ القابل للبيع في 2026 قابلٌ له في سنةٍ محسوبة.

⛔ لا تقيس: انبعاثَ أيّ منشأة (لم نُشغّل نموذجاً، ولم ندخل موقعاً) · احتمالَ
القبول · التسعير · أيَّ رقم إيراد (`revenue_claim = NONE`) · الألومنيوم (مرجعاه
A وB **لم يُستخرجا** ⇒ كلُّ رموزه `UNRANKABLE`، والفراغُ `None` لا صفر).

**القوانين الحاكمة داخل هذا الملفّ.**

1. **الافتراضي `None` لا صفر**: رمزٌ بلا مرجعٍ مستخرج ليس «وفراً صفرياً» — إنه
   **غيرُ قابلٍ للترتيب**، وطلبُ حسابِه يرفع `UnpinnedError` لا يُرجِع صفراً.
2. **الدبوسُ يُقتبَس بحرفه**: كلّ قيمةٍ في `ALGERIA_DEFAULTS` و`BENCHMARKS` منقولةٌ
   كما طُبعت (فاصلةٌ عشريةٌ أوروبية ← نقطة)، ومصدرُها واسمُ الملفّ وتاريخُ الوصول
   في `SOURCES`. `_self_check()` يفرض أن يكون `direct + indirect == total` لكلّ صفّ
   مغلق، وأن يبقى `N/A` و`-` **نصّين** لا أصفاراً.
3. **الدرجةُ partٌ من الرقم**: كلّ مصدرٍ موسومٌ `أ` (أوّلِيّ) أو `ب` (ثانويّ/مشروط)
   أو `ج` (مانع). وأيُّ حكمٍ يتوقّف على مصدرٍ من الدرجة `ب` وحده يُوسَم
   `CONDITIONAL` ولا يخرج `QUOTABLE`.
4. **معاملُ CBAM مضروبٌ في المرجع لا في الانبعاث**: هذه هي المفاضلةُ التي تُبطل
   قراءتين في المستودع؛ وبرهانُها السالبة في الاختبارات (K3).

القانون: stdlib فقط، لا استيراد من app/ ولا microservices/ — تُشحَن إلى عميلٍ لا
يملك تبعياتنا. المكتبةُ تُرجِع بياناتٍ ولا تطبع (D-281).
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import StrEnum
from typing import Final

__all__ = [
    "ALGERIA_CARBON_STEEL_ROUTE",
    "ALGERIA_DEFAULTS",
    "AS_OF",
    "BATCH",
    "BENCHMARKS",
    "CANDIDATE_SEE",
    "CBAM_FACTOR",
    "CERT_PRICE_EUR",
    "CSCF",
    "CSCF_SENSITIVITY",
    "DEFAULT_QUARTER",
    "HORIZON",
    "MARKUP",
    "SOURCES",
    "DefaultRow",
    "PinError",
    "UnpinnedError",
    "Verdict",
    "benchmark_resolution",
    "certificates_actual",
    "certificates_default",
    "closure_audit",
    "column_asymmetry",
    "crossover_see",
    "cscf_sensitivity",
    "default_route",
    "error_identity",
    "first_sellable_year",
    "inputs_fingerprint",
    "kill_switches",
    "markup_relief",
    "measure_all",
    "net_required_reduction",
    "overstatement",
    "path_toll",
    "pinned_codes",
    "saving",
    "sefa",
    "self_check",
    "unconditional_year",
    "unpaired_benchmark_cns",
]

BATCH: Final = "CPN-12"
AS_OF: Final = "2026-09-15"

#: أفقُ الحساب. لا يُمدّ إلى ما بعد 2034: من 2034 «لا ينطبق معامل CBAM»
#: (المصدر S3)، فالصيغةُ نفسها تتغيّر ولا تُستنتَج بالاستمرار.
HORIZON: Final = tuple(range(2026, 2035))


class PinError(Exception):
    """خطأٌ في الدبوس: طلبُ كميةٍ على مُدخَلٍ غير مُدبوس أو غير مُعرَّف."""


class UnpinnedError(PinError):
    """الفراغُ `None` لا صفر — الرمزُ غيرُ مدبوس، وطلبُه في كودٍ بيعيٍّ خطأ."""


class Verdict(StrEnum):
    """حكمٌ من مجموعةٍ مغلقة — لا حكمَ خامساً ولا «ربما»."""

    ACTUAL_CHEAPER = "ACTUAL_CHEAPER"
    DEFAULT_CHEAPER = "DEFAULT_CHEAPER"
    EXACTLY_AT_CROSSOVER = "EXACTLY_AT_CROSSOVER"
    UNRANKABLE = "UNRANKABLE"


# ── المصادر: كلُّ رقمٍ في هذا الملفّ ينتهي إلى سطرٍ هنا ──────────────────────────

SOURCES: Final = {
    "S1": {
        "id": "S1",
        "title_ar": "القيم الافتراضية للفترة النهائية — ملف Excel الرسميّ (النسخة 2)",
        "publisher": "European Commission, DG TAXUD",
        "url": (
            "https://taxation-customs.ec.europa.eu/document/download/"
            "1c05d211-80cb-4aaa-8ef0-e08005a95d7e_en"
            "?filename=DV%20correcting%20act_final%20update_06.08.xlsx"
        ),
        "published_on": "2026-08-10",
        "accessed_on": AS_OF,
        "grade": "أ",
        "legal_basis": "IR (EU) 2025/2621 Annex I as replaced by IR (EU) 2026/1740",
        "quote": (
            "Version 2 | 2026-08-06 | Default values based on Annex I and II to "
            "Implementing Regulation (EU) 2026/1740 adopted on 20 July 2026"
        ),
        "caveat_ar": (
            "الملفّ «لأغراض المعلومات فقط»؛ الملزمُ قانوناً هو نصّ اللائحة. "
            "لا يحوي ملاحق II (غير المباشرة) وIII (الكهرباء)."
        ),
    },
    "S2": {
        "id": "S2",
        "title_ar": "مراجع CBAM للفترة النهائية — ملف Excel الرسميّ (النسخة 1)",
        "publisher": "European Commission, DG TAXUD",
        "url": (
            "https://taxation-customs.ec.europa.eu/document/download/"
            "9877523c-2a02-4926-a211-aefae7cf6d0d_en"
            "?filename=CBAM%20Benchmarks_20260206.xlsx"
        ),
        "published_on": "2026-02-13",
        "accessed_on": AS_OF,
        "grade": "أ",
        "legal_basis": "IR (EU) 2025/2620, Annex point 5, Columns A and B",
        "quote": (
            "CN code | CN Description | Column A BMg [tCO2e/t] | Column A Production "
            "route indicator | Column B BMg [tCO2e/t] | Column B Production route indicator"
        ),
        "caveat_ar": (
            "⛔ الألومنيوم لم يُستخرج من هذا الملفّ — مراجعُه A/B غائبةٌ عمداً، "
            "لا مُصفَّرة."
        ),
    },
    "S3": {
        "id": "S3",
        "title_ar": "جدولُ معامل CBAM عبر الزمن (دليلُ منهجية التخصيص)",
        "publisher": "European Commission, DG CLIMA",
        "url": (
            "https://climate.ec.europa.eu/document/download/"
            "d5276f6c-4355-438a-a0ef-0c03a9b34a39_en?filename=1_gd1_general_guidance_en.pdf"
        ),
        "published_on": "2024-02-26",
        "accessed_on": AS_OF,
        "grade": "أ",
        "legal_basis": "Directive 2003/87/EC art. 10a(1a), as amended by Dir. (EU) 2023/959",
        "quote": "CBAM 1 1 0.975 0.95 0.90 0.775 0.515 0.39 0.265 0.14 0",
        "caveat_ar": (
            "الاتجاهُ حاسم: المعاملُ **يهبط** من 0.975 إلى 0 — أي إنه «ما تبقّى من "
            "التخصيص المجانيّ»، وهو مضروبٌ في المرجع لا في الانبعاث."
        ),
    },
    "S4": {
        "id": "S4",
        "title_ar": "صيغةُ الالتزام وحسابُ تعديل التخصيص المجانيّ",
        "publisher": "OPIS / McCloskey (نقلٌ عن أعمال التنفيذ) + DEHSt (سلطةٌ وطنية)",
        "url": "https://www.opis.com/resources/energy-market-news-from-opis/provisional-cbam-calculation-values-pass-committee-vote/",
        "published_on": "2026-01-07",
        "accessed_on": AS_OF,
        "grade": "ب",
        "legal_basis": "Reg. (EU) 2023/956 Annex II; IR (EU) 2025/2620",
        "quote": (
            "CBAM-liable Emissions = Total Embedded Emissions - Free Allocation "
            "Adjustment - Carbon Price Already Paid; Free Allocation Adjustment = "
            "Specific Embedded Free Allocation x Mass; Specific Embedded Free "
            "Allocation = CBAM factor x Cross-Sectoral Correction Factor x CBAM "
            "Benchmark; The CBAM factor starts at 97.5% in 2026"
        ),
        "caveat_ar": (
            "ثانويّ، لكنه يتقاطع مع مصدرَين مستقلَّين: DEHSt («the annually "
            "decreasing CBAM factor») وأسئلة المفوضية («the CBAM adjustment for free "
            "allocation will gradually decrease»). النصُّ الحرفيّ لملحق 2025/2620 "
            "**لم يُستخرج** ⇒ الدرجة ب."
        ),
    },
    "S5": {
        "id": "S5",
        "title_ar": "أسئلةُ المفوضية وأجوبتها عن CBAM — ترتيبُ العمليات في الصيغة",
        "publisher": "European Commission, DG TAXUD",
        "url": "https://taxation-customs.ec.europa.eu/document/download/013fa763-5dce-4726-a204-69fec04d5ce2_en",
        "published_on": "2026-05-27",
        "accessed_on": AS_OF,
        "grade": "أ",
        "legal_basis": "Reg. (EU) 2023/956 arts. 6-9; IR (EU) 2025/2620 Annex §3/§4",
        "quote": (
            "the number of CBAM certificates to be surrendered ... is determined by the "
            "amount of this imported CBAM good and the specific embedded emissions, "
            "reduced by the specific embedded free allocation ... If default values for "
            "embedded emissions are declared, the adjustment should equally be based on "
            "default values for free allocation ... based on the CBAM benchmarks defined "
            "in Column B of this Annex. If applicable, the same production route shall be "
            "used as indicated in Annex I to Implementing Regulation (EU) 2025/2621"
        ),
        "caveat_ar": "هذا هو السندُ الأوّليّ على أنّ مسارَ الإعلان يختار العمود.",
    },
    "S6": {
        "id": "S6",
        "title_ar": "جدولُ العلاوة ونطاقُ تطبيقها (نصُّ رأس الملحق I)",
        "publisher": "EUR-Lex — IR (EU) 2026/1740, Annex I",
        "url": "https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=OJ:L_202601740",
        "published_on": "2026-07-31",
        "accessed_on": AS_OF,
        "grade": "أ",
        "legal_basis": "IR (EU) 2026/1740 Annex I, opening paragraphs",
        "quote": (
            "the default values of the column 'total emissions' shall be selected and "
            "increased as follows: For goods in the cement, iron and steel, aluminium and "
            "hydrogen sectors, the mark-up shall be 10 % for the year 2026, 20 % for the "
            "year 2027 and 30 % for the year 2028 and onwards. For goods in the fertiliser "
            "sector, the mark-up shall be 1 % for the year 2026 and onwards."
        ),
        "caveat_ar": (
            "يُثبت أيضاً أنّ «العلاوة على عمود الإجمالي» لا على المباشر وحده — وهو ما "
            "كان افتراضاً في `markup_gradient.py`."
        ),
    },
    "S7": {
        "id": "S7",
        "title_ar": "سعرُ شهادة CBAM — الربعان الأوّل والثاني 2026",
        "publisher": "European Commission (نقلٌ متزامنٌ من ثلاثة منافذ قطاعية)",
        "url": "https://eurometal.net/european-commission-announces-q2-2026-cbam-certificate-price/",
        "published_on": "2026-07-06",
        "accessed_on": AS_OF,
        "grade": "ب",
        "legal_basis": "IR (EU) 2025/2548",
        "quote": "Q1 2026 | 7 April 2026 | EUR 75.36/t || Q2 2026 | 6 July 2026 | EUR 75.28/t",
        "caveat_ar": (
            "الربعُ الثالث يُنشر 2026-10-05 ⇒ `None` حتى ذلك التاريخ، ⛔ لا يُستمرأ "
            "بقيمة الربع الثاني. صفحةُ المفوضية نفسها لم تُجلب."
        ),
    },
    "S8": {
        "id": "S8",
        "title_ar": "عاملُ التصحيح عبر القطاعات 2026-2030 = 1",
        "publisher": "Implementing Decision (EU) 2026/1862 (23 يوليو 2026) — منقول",
        "url": "https://www.studioponchio.eu/guida-cbam-dac8-en/",
        "published_on": "2026-09-09",
        "accessed_on": AS_OF,
        "grade": "ب",
        "legal_basis": "Directive 2003/87/EC art. 10a(5); ID (EU) 2026/1862",
        "quote": (
            "Specific embedded free allocation: 2026 CBAM factor (0.975) x cross-sectoral "
            "correction factor (1.00) x benchmark (1.370) = 1.33575 t per tonne"
        ),
        "caveat_ar": (
            "⛔ **لم يُقرأ نصُّ القرار 2026/1862 نفسه**. القيمة 1.000 منقولةٌ عن مثالٍ "
            "محسوبٍ في مصدرٍ مهنيّ، وسابقتُها (2021-2025) كانت 100% بقرارٍ من المفوضية. "
            "لهذا `CSCF` حساسيةٌ معلنةٌ في K2، ولا يخرج أيُّ حكمٍ يعتمد عليها وحدها "
            "`QUOTABLE`."
        ),
    },
    "S9": {
        "id": "S9",
        "title_ar": "السجلُّ التشريعيّ للائحة التنفيذ 2025/2621 (الأصلُ الذي صُحِّح)",
        "publisher": "EUR-Lex",
        "url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=OJ:L_202502621",
        "published_on": "2025-12-22",
        "accessed_on": AS_OF,
        "grade": "أ",
        "legal_basis": "IR (EU) 2025/2621",
        "quote": "Commission Implementing Regulation (EU) 2025/2621 ... laying down rules for the application of Regulation (EU) 2023/956 ... as regards default values",
        "caveat_ar": (
            "⛔ جُلب السجلُّ الببليوغرافيّ وحده؛ ملفُّ PDF الكامل ~2400 صفحة ولم يُحلَّل "
            "(سقفُ الجلب 30 صفحة). ولهذا كلّ رقمٍ بلدِيٍّ هنا من **ملفّ المفوضية** (S1) "
            "لا من هذا السجل، والدرجاتُ منفصلةٌ عمداً."
        ),
    },
    "S10": {
        "id": "S10",
        "title_ar": "جدولُ أعمال الفترة النهائية وتواريخُ الالتزام",
        "publisher": "Studio Ponchio — guida CBAM DAC8 (EN)",
        "url": "https://www.studioponchio.eu/guida-cbam-dac8-en/",
        "published_on": "2026-09-09",
        "accessed_on": AS_OF,
        "grade": "ب",
        "legal_basis": "IR 2025/2547 · IR 2025/2548 · IR 2025/2620 · IR 2025/2621 · IR 2026/1740 · ID 2026/1862 · Reg 2024/3210",
        "quote": "first annual CBAM declaration due 30 September 2027 for imports of 2026; de minimis 50 tonnes per year does not apply to hydrogen and electricity",
        "caveat_ar": (
            "يستعمل **لتحديد نافذة البيع** لا لحسابٍ: أوّلُ إقرارٍ سنويّ 30 سبتمبر 2027 "
            "عن واردات 2026 ⇒ قرارُ «أيُّ مسارٍ نعلن» يُتَّخذ قبل ذلك التاريخ بأشهر، "
            "لا بعده. ⛔ لا يُقتبَس لأيّ رقمٍ ماليّ."
        ),
    },
    "S11": {
        "id": "S11",
        "title_ar": "سجلُّ السحب: الأداتان السابقتان ما تزالان على القرص بحسابهما القديم",
        "publisher": "هذا المستودع — `research/fx-hard-currency/cbam_value.py` و`studies/cbam-markup-gradient-002/markup_gradient.py`",
        "url": "file://research/fx-hard-currency/cbam_value.py",
        "published_on": AS_OF,
        "accessed_on": AS_OF,
        "grade": "أ",
        "legal_basis": "عرف RCL: السحبُ يُسجَّل في سجلِّه ولا يُنشَر إلى مصادر الأرقام",
        "quote": (
            "cbam_value.py: FACTOR = {2026: 0.025, ...} مطبوعٌ في الفجوة · "
            "markup_gradient.py: CBAM_FACTOR = {2026: 0.975, ...} مطبوعٌ في الوفر"
        ),
        "caveat_ar": (
            "الأداتان تتناقضان بنسبة 39× في المعامل نفسه. هذا التناقضُ هو **سببُ وجود "
            "الدفعة**، لا نتيجةٌ لها. ⛔ لم يُحرَّر أيٌّ منهما: الاختبار "
            "`test_withdrawn_arithmetic_is_still_reachable_in_the_old_instruments` يثبت "
            "أنّ الانتشارَ يحتاج قراراً مكتوباً."
        ),
    },
    "S12": {
        "id": "S12",
        "title_ar": "الدفعاتُ السابقة المُحالة إليها: UCL · FCM · دراسة 002",
        "publisher": "هذا المستودع — `docs/research/` و`research/fx-hard-currency/`",
        "url": "file://docs/research/HARD_CURRENCY_NEW_KNOWLEDGE_UCL.md",
        "published_on": "2026-09-14",
        "accessed_on": AS_OF,
        "grade": "ج",
        "legal_basis": "لا سندَ قانونيّ — إسنادٌ داخليّ",
        "quote": "UCL M3 `cbam_pin.py` = 11,000 €/day (band 6,000-60,000)",
        "caveat_ar": (
            "⛔ **عيبُ إسنادٍ مُقاس**: UCL ورثت ستّةَ أرقامٍ (SFD · ERD · PTD · PID · "
            "ABR · CPD) ببصماتٍ مُعلَنة، ولا وثيقةَ ولا ملفَّ قياسٍ لأيٍّ منها على القرص "
            "(مُختبَر في `test_ucl_inherited_fingerprints_are_not_on_disk`). فنطاقُ M3 "
            "اليورويّ كان غيرَ قابلٍ للتدقيق. هذه الدفعة تشتقّ الآليةَ من مصدرٍ أوّليّ "
            "وتترك النطاقَ اليورويّ **بلا ادّعاء** (`revenue_claim = NONE`)."
        ),
    },
    "S13": {
        "id": "S13",
        "title_ar": "⛔ ليس سنداً: القراءةُ السوقيةُ الخاطئة لمعامل CBAM",
        "publisher": "cbamguide.com · senken.io · carboncomplete.com (ثلاثةٌ متوافقة)",
        "url": "https://www.cbamguide.com/",
        "published_on": "2026-01-15",
        "accessed_on": AS_OF,
        "grade": "ج",
        "legal_basis": "لا شيء — هذه **قرينةٌ على وجود الخطأ في السوق**، لا سلطة",
        "quote": "the CBAM factor: 2.5% in 2026 rising to 100% in 2034, applied to the chargeable emissions",
        "caveat_ar": (
            "تقرأ المعاملَ «حصةً خاضعة» تصعد من 2.5% إلى 100%، بينما النصُّ الأوّليّ "
            "(S3) يجعله «ما تبقّى من التخصيص المجانيّ» يهبط من 97.5% إلى 0 — والقانونُ "
            "يصفُ الحالتين بمعاملٍ واحدٍ في المادة 10a(1a). **تُذكَر هنا لتسجيل أنّ "
            "الأدبيات الثانوية سائدةُ الخطأ**، وهذا بالضبط سببُ أنّ أداةً بدبوسٍ "
            "أوّليّ لها سعر. ⛔ لا يُقتبَس منها رقم."
        ),
    },
}


# ── الجدولةُ التنظيمية (كلُّها من S3 وS6) ───────────────────────────────────────

#: معامل CBAM = **ما تبقّى** من التخصيص المجانيّ. يهبط، ⛔ لا يصعد (S3).
CBAM_FACTOR: Final = {
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

#: العلاوة على عمود «الإجمالي» (S6). الأسمدة 1% من 2026 فصاعداً — ⛔ ليست متصاعدة.
MARKUP: Final = {
    "cement": {2026: 0.10, 2027: 0.20, 2028: 0.30},
    "iron_steel": {2026: 0.10, 2027: 0.20, 2028: 0.30},
    "aluminium": {2026: 0.10, 2027: 0.20, 2028: 0.30},
    "hydrogen": {2026: 0.10, 2027: 0.20, 2028: 0.30},
    "fertilisers": {2026: 0.01, 2027: 0.01, 2028: 0.01},
}
#: من 2028 فصاعداً العلاوةُ ثابتة (نصّ S6: «30 % for the year 2028 and onwards»).
for _sector in ("cement", "iron_steel", "aluminium", "hydrogen"):
    for _year in range(2029, 2035):
        MARKUP[_sector][_year] = 0.30
for _year in range(2029, 2035):
    MARKUP["fertilisers"][_year] = 0.01

#: عاملُ التصحيح عبر القطاعات — درجة ب (S8)، بحساسيةٍ معلنة.
CSCF: Final = {year: 1.000 for year in HORIZON}
CSCF_SENSITIVITY: Final = (0.900, 0.950, 1.000)

#: سعرُ الشهادة باليورو/طنّ CO₂e. `None` = لم يُنشر بعد (⛔ لا استمرار).
CERT_PRICE_EUR: Final = {"2026Q1": 75.36, "2026Q2": 75.28, "2026Q3": None, "2026Q4": None}
DEFAULT_QUARTER: Final = "2026Q2"


# ── الدبابيس: القيم الافتراضية الجزائرية (S1) ───────────────────────────────────
#
# البنية: cn -> DefaultRow(sector, direct, indirect, total, route)
#   direct/indirect/total : float أو None حين طبعت الخلية "-" أو "N/A"
#   route                 : مؤشر مسار الإنتاج الذي يحدّد مرجع CBAM، أو None
#
# ⛔ "-" و"N/A" **ليسا صفراً**: الأولى تعني «لا قيمةَ بلدِيّة ⇒ يُستخدم جدول
# "Other countries and territories"» (نصّ S6)، والثانية «القطاعُ لا يُسعّر غير
# المباشر». الخلطُ بينهما هو الذي أنتج أرقامَ `cbam_value.py` القديمة.


@dataclass(frozen=True)
class DefaultRow:
    """صفٌّ واحد من الملحق I كما طُبع — لا كما فُسِّر."""

    cn: str
    sector: str
    description: str
    direct: float | None
    indirect: float | None
    total: float | None
    route: str | None

    def __post_init__(self) -> None:
        if not self.cn.strip():
            raise PinError("CN code is required")
        if self.sector not in MARKUP:
            raise PinError(f"unknown sector: {self.sector}")

    @property
    def closure_gap(self) -> float | None:
        """`total − (direct + indirect)` — ⛔ ليس صفراً بحكم البناء.

        النتيجةُ المقاسة في `closure_audit()`: الملفُّ الرسميّ نفسه يحوي صفوفاً لا
        تُغلق، لأنّ كلّ عمودٍ مُقرَّبٌ إلى ثلاث خاناتٍ على حدة. والقانونُ (S6) يقول
        «يُختار عمود الإجمالي» ⇒ **الإجماليّ كميةٌ أولية، لا مجموع**.
        """
        if None in (self.direct, self.indirect, self.total):
            return None
        return round(self.total - (self.direct + self.indirect), 5)


def _row(
    cn: str,
    sector: str,
    description: str,
    direct: float | None,
    indirect: float | None,
    total: float | None,
    route: str | None = None,
) -> DefaultRow:
    return DefaultRow(
        cn=cn,
        sector=sector,
        description=description,
        direct=direct,
        indirect=indirect,
        total=total,
        route=route,
    )


#: القيم الافتراضية الجزائرية — **كلُّ صفٍّ منقولٌ حرفياً من S1** (Annex I كما
#: استُبدل بـ IR 2026/1740، نسخة الملفّ 2 بتاريخ 2026-08-06).
ALGERIA_DEFAULTS: Final = {
    # ── الإسمنت ────────────────────────────────────────────────────────────────
    "2507008080": _row("2507008080", "cement", "Calcined clay", None, None, None, None),
    "2523100010": _row("2523100010", "cement", "White clinker", 1.290, 0.060, 1.340, "(B)"),
    "2523100090": _row("2523100090", "cement", "Other clinker including grey clinker", 1.240, 0.040, 1.280, "(A)"),
    "25232100": _row("25232100", "cement", "White Portland cement", 1.230, 0.140, 1.370, None),
    "25232900": _row("25232900", "cement", "Grey Portland cement", 1.230, 0.060, 1.300, None),
    "25233000": _row("25233000", "cement", "Aluminous cement", None, None, None, None),
    "2523900010": _row("2523900010", "cement", "White hydraulic cement", 1.280, 0.170, 1.440, "(B)"),
    "2523900090": _row("2523900090", "cement", "Other hydraulic cements incl. grey", 1.170, 0.070, 1.240, "(A)"),
    # ── الأسمدة ────────────────────────────────────────────────────────────────
    "28080000": _row("28080000", "fertilisers", "Nitric acid; sulphonitric acids", 2.490, 0.040, 2.530, None),
    "28141000": _row("28141000", "fertilisers", "Anhydrous ammonia", 1.960, 0.120, 2.080, None),
    "28142000": _row("28142000", "fertilisers", "Ammonia in aqueous solution", 0.590, 0.040, 0.620, None),
    "28342100": _row("28342100", "fertilisers", "Nitrate of potassium", 2.000, 0.060, 2.060, None),
    "31021012": _row("31021012", "fertilisers", "Urea aq. >45%N, 31.8-33.2% urea", 0.440, 0.030, 0.470, None),
    "31021015": _row("31021015", "fertilisers", "Urea aq. >45%N, >33.2-55% urea", 0.720, 0.030, 0.760, None),
    "31021019": _row("31021019", "fertilisers", "Urea, >45%N", 1.320, 0.100, 1.410, None),
    "31021090": _row("31021090", "fertilisers", "Urea, <=45%N", 1.290, 0.090, 1.380, None),
    "31022100": _row("31022100", "fertilisers", "Ammonium sulphate", 0.560, 0.070, 0.630, None),
    "31022900": _row("31022900", "fertilisers", "Double salts AS + AN", 1.270, 0.080, 1.360, None),
    "31023010": _row("31023010", "fertilisers", "Ammonium nitrate in aqueous solution", 1.510, 0.060, 1.570, None),
    "31023090": _row("31023090", "fertilisers", "Ammonium nitrate", 2.330, 0.090, 2.420, None),
    "31024010": _row("31024010", "fertilisers", "AN + calcium carbonate, <=28%N", 1.980, 0.090, 2.070, None),
    "31024090": _row("31024090", "fertilisers", "AN + calcium carbonate, >28%N", 1.980, 0.090, 2.070, None),
    "31025000": _row("31025000", "fertilisers", "Sodium nitrate", 3.880, 0.060, 3.940, None),
    "31026000": _row("31026000", "fertilisers", "Double salts CN + AN", 1.950, 0.080, 2.030, None),
    "31028000": _row("31028000", "fertilisers", "UAN mixtures", 1.460, 0.080, 1.530, None),
    "31029000": _row("31029000", "fertilisers", "Other mineral/chemical N fertilisers", 1.490, 0.090, 1.580, None),
    "31051000": _row("31051000", "fertilisers", "Animal/vegetable origin, <=10 kg", 0.730, 0.080, 0.810, None),
    "31052010": _row("31052010", "fertilisers", "PK with N >10%", 0.970, 0.090, 1.060, None),
    "31052090": _row("31052090", "fertilisers", "NPK with N <=10%", 0.660, 0.070, 0.720, None),
    "31053000": _row("31053000", "fertilisers", "Diammonium phosphate (DAP)", 0.460, 0.050, 0.510, None),
    "31054000": _row("31054000", "fertilisers", "Monoammonium phosphate (MAP)", 0.290, 0.040, 0.340, None),
    "31055100": _row("31055100", "fertilisers", "N+P incl. nitrates and phosphates", 1.330, 0.110, 1.440, None),
    "31055900": _row("31055900", "fertilisers", "N+P excl. nitrates and phosphates", 0.520, 0.090, 0.610, None),
    "31059020": _row("31059020", "fertilisers", "N+K, >10% N", 1.310, 0.070, 1.380, None),
    "31059080": _row("31059080", "fertilisers", "N+K, <=10% N", 0.670, 0.050, 0.720, None),
    # ── الألومنيوم (المسار L = ثانويّ في كلِّ صفّ) ─────────────────────────────
    "7601": _row("7601", "aluminium", "Unwrought aluminium", 0.360, None, 0.360, "(L)"),
    "7603": _row("7603", "aluminium", "Aluminium powders and flakes", 0.920, None, 0.920, "(L)"),
    "76041010": _row("76041010", "aluminium", "Bars and rods", 1.140, None, 1.140, "(L)"),
    "76041090": _row("76041090", "aluminium", "Profiles", 1.160, None, 1.160, "(L)"),
    "76042100": _row("76042100", "aluminium", "Hollow profiles", 1.160, None, 1.160, "(L)"),
    "7605": _row("7605", "aluminium", "Aluminium wire", 1.140, None, 1.140, "(L)"),
    "7606": _row("7606", "aluminium", "Plates, sheets, strip >0.2 mm", 1.600, None, 1.600, "(L)"),
    "7608": _row("7608", "aluminium", "Aluminium tubes and pipes", 1.160, None, 1.160, "(L)"),
    "7614": _row("7614", "aluminium", "Stranded wire, cables, plaited bands", 1.140, None, 1.140, "(L)"),
    # ── الهيدروجين ─────────────────────────────────────────────────────────────
    "28041000": _row("28041000", "hydrogen", "Hydrogen", 10.820, None, 10.820, None),
    # ── الحديد والصلب ──────────────────────────────────────────────────────────
    "26011200": _row("26011200", "iron_steel", "Agglomerated iron ores and concentrates", 0.180, 0.030, 0.210, None),
    "7201": _row("7201", "iron_steel", "Pig iron and spiegeleisen", 2.870, None, 2.870, None),
    "720211": _row("720211", "iron_steel", "Ferro-manganese >2% C", None, None, None, None),
    "720219": _row("720219", "iron_steel", "Ferro-manganese <=2% C", None, None, None, None),
    "720241": _row("720241", "iron_steel", "Ferro-chromium >4% C", None, None, None, None),
    "720249": _row("720249", "iron_steel", "Ferro-chromium <=4% C", None, None, None, None),
    "72026000": _row("72026000", "iron_steel", "Ferro-nickel", None, None, None, None),
    "7203": _row("7203", "iron_steel", "DRI and other spongy ferrous products", 0.810, None, 0.810, None),
    "7205": _row("7205", "iron_steel", "Granules and powders", 2.890, None, 2.890, "(C)/(F)"),
    "72061000": _row("72061000", "iron_steel", "Ingots of iron and non-alloy steel", 3.000, None, 3.000, "(C)"),
    "72069000": _row("72069000", "iron_steel", "Puddled bars / other primary forms", 3.000, None, 3.000, "(C)"),
    "72071114": _row("72071114", "iron_steel", "Semi-finished, <0.25% C, w<2t, <=130 mm", 3.000, None, 3.000, "(C)"),
    "72071116": _row("72071116", "iron_steel", "Semi-finished, <0.25% C, w<2t, >130 mm", 3.000, None, 3.000, "(C)"),
    "72071190": _row("72071190", "iron_steel", "Semi-finished, <0.25% C, forged", 3.000, None, 3.000, "(C)"),
    "72071210": _row("72071210", "iron_steel", "Semi-finished, <0.25% C, w>=2t, rolled", 3.000, None, 3.000, "(C)"),
    "72072015": _row("72072015", "iron_steel", "Semi-finished, 0.25-0.6% C, rolled", 3.000, None, 3.000, "(C)"),
    "7208": _row("7208", "iron_steel", "Flat-rolled HR, width >=600 mm", 3.000, None, 3.000, "(C)"),
    "7209": _row("7209", "iron_steel", "Flat-rolled CR, width >=600 mm", 3.000, None, 3.000, "(C)"),
    "7210": _row("7210", "iron_steel", "Flat-rolled clad/plated/coated, >=600 mm", 3.000, None, 3.000, "(C)"),
    "7213": _row("7213", "iron_steel", "Bars and rods, hot-rolled, in coils", 3.000, None, 3.000, "(C)"),
    "72142000": _row("72142000", "iron_steel", "Reinforcing bars and rods (rebar)", 3.000, None, 3.000, "(C)"),
    "7216": _row("7216", "iron_steel", "Angles, shapes and sections", 3.000, None, 3.000, "(C)"),
    "72181000": _row("72181000", "iron_steel", "Stainless ingots and primary forms", 3.300, None, 3.300, None),
    "72191100": _row("72191100", "iron_steel", "Stainless flat-rolled HR >=600 mm >10 mm", 3.300, None, 3.300, None),
}

#: الرمزُ الوطنيّ الجزائريّ لصلب الكربون من 7206 إلى 7217 **كلُّه** 3.000 بمسار (C)
#: — وهذا وحده نتيجة، لا مُدخَل: الجزائر لا تملك مسار BF/BOF بحجمٍ يُصدَّر،
#: ومع ذلك القيمةُ البلدِيّة مُدبَّسة على ذلك المسار.
ALGERIA_CARBON_STEEL_ROUTE: Final = "(C)"


# ── الدبابيس: مراجع CBAM، العمودان A وB (S2) ────────────────────────────────────
#
# cn -> {"A": {route: BMg}, "B": {route: BMg}}
#   العمود A = المرجع المستعمل حين تُعلَن **بياناتٌ فعلية** (S5, ملحق 2025/2620 §3)
#   العمود B = المرجع المستعمل حين تُعلَن **قيمٌ افتراضية** (S5, ملحق 2025/2620 §4)
#   "" كمفتاح مسار = المرجع لا يتعلّق بمسار الإنتاج.
#
# ⛔ الألومنيوم **غائب** من هذا الجدول عمداً: لم يُستخرج. انظر S2.caveat_ar وK5.

BENCHMARKS: Final = {
    # ── الإسمنت ────────────────────────────────────────────────────────────────
    "25070080": {"A": {"": 0.666}, "B": {"": 0.666}},
    "25231000": {"A": {"(A)": 0.666, "(B)": 0.859}, "B": {"(A)": 0.666, "(B)": 0.859}},
    "25232100": {"A": {"": 0.000}, "B": {"": 0.859}},
    "25232900": {"A": {"": 0.000}, "B": {"": 0.666}},
    "25233000": {"A": {"(1)": 0.717, "(2)": 0.686}, "B": {"(1)": 0.717, "(2)": 0.686}},
    "25239000": {"A": {"(A)": 0.000, "(B)": 0.000}, "B": {"(A)": 0.666, "(B)": 0.847}},
    # ── الهيدروجين ─────────────────────────────────────────────────────────────
    "28041000": {"A": {"": 5.089}, "B": {"": 5.089}},
    # ── الأسمدة ────────────────────────────────────────────────────────────────
    "28080000": {"A": {"": 0.151}, "B": {"": 0.582}},
    "28141000": {"A": {"": 1.522}, "B": {"": 1.522}},
    "28142000": {"A": {"": 0.457}, "B": {"": 0.457}},
    "28342100": {"A": {"": 0.019}, "B": {"": 0.626}},
    "31021012": {"A": {"": 0.018}, "B": {"": 0.304}},
    "31021015": {"A": {"": 0.029}, "B": {"": 0.503}},
    "31021019": {"A": {"": 0.053}, "B": {"": 0.902}},
    "31021090": {"A": {"": 0.051}, "B": {"": 0.882}},
    "31022100": {"A": {"": 0.022}, "B": {"": 0.414}},
    "31022900": {"A": {"": 0.019}, "B": {"": 0.566}},
    "31023010": {"A": {"": 0.000}, "B": {"": 0.508}},
    "31023090": {"A": {"": 0.019}, "B": {"": 0.767}},
    "31024010": {"A": {"": 0.019}, "B": {"": 0.688}},
    "31024090": {"A": {"": 0.019}, "B": {"": 0.688}},
    "31025000": {"A": {"(1)": 0.270, "(2)": 0.254}, "B": {"(1)": 0.701, "(2)": 0.685}},
    "31026000": {"A": {"": 0.042}, "B": {"": 0.633}},
    "31028000": {"A": {"": 0.000}, "B": {"": 0.625}},
    "31029000": {"A": {"": 0.053}, "B": {"": 0.847}},
    "31051000": {"A": {"": 0.019}, "B": {"": 0.376}},
    "31052010": {"A": {"": 0.090}, "B": {"": 0.434}},
    "31052090": {"A": {"": 0.090}, "B": {"": 0.319}},
    "31053000": {"A": {"": 0.006}, "B": {"": 0.339}},
    "31054000": {"A": {"": 0.006}, "B": {"": 0.173}},
    "31055100": {"A": {"": 0.090}, "B": {"": 0.548}},
    "31055900": {"A": {"": 0.006}, "B": {"": 0.391}},
    "31059020": {"A": {"": 0.019}, "B": {"": 0.476}},
    "31059080": {"A": {"": 0.019}, "B": {"": 0.248}},
    # ── الحديد والصلب ──────────────────────────────────────────────────────────
    "26011200": {"A": {"": 0.086}, "B": {"": 0.086}},
    "72011011": {"A": {"": 1.089}, "B": {"": 1.210}},
    "72021120": {"A": {"(1)": 1.361, "(2)": 1.277}, "B": {"(1)": 1.361, "(2)": 1.277}},
    "72024110": {"A": {"(1)": 1.142, "(2)": 1.106}, "B": {"(1)": 1.142, "(2)": 1.106}},
    "72026000": {"A": {"(1)": 2.390, "(2)": 2.295}, "B": {"(1)": 2.390, "(2)": 2.295}},
    "72031000": {"A": {"": 0.295}, "B": {"": 0.397}},
    "72039000": {"A": {"": 0.295}, "B": {"": 0.397}},
    "72051000": {"A": {"": 0.000}, "B": {"(C)": 1.288, "(D)": 0.424, "(E)": 0.027}},
    "72061000": {
        "A": {"(C)": 0.150, "(D)": 0.027, "(E)": 0.027},
        "B": {"(C)": 1.288, "(D)": 0.424, "(E)": 0.027},
    },
    "72069000": {
        "A": {"(C)": 0.150, "(D)": 0.027, "(E)": 0.027},
        "B": {"(C)": 1.288, "(D)": 0.424, "(E)": 0.027},
    },
    "72071111": {
        "A": {"(C)": 0.188, "(D)": 0.065, "(E)": 0.065},
        "B": {"(C)": 1.364, "(D)": 0.475, "(E)": 0.066},
    },
    "72071114": {
        "A": {"(C)": 0.188, "(D)": 0.065, "(E)": 0.065},
        "B": {"(C)": 1.364, "(D)": 0.475, "(E)": 0.066},
    },
    "72071116": {
        "A": {"(C)": 0.188, "(D)": 0.065, "(E)": 0.065},
        "B": {"(C)": 1.364, "(D)": 0.475, "(E)": 0.066},
    },
    "72071190": {
        "A": {"(C)": 0.453, "(D)": 0.330, "(E)": 0.330},
        "B": {"(C)": 1.629, "(D)": 0.740, "(E)": 0.331},
    },
    "72071210": {
        "A": {"(C)": 0.188, "(D)": 0.065, "(E)": 0.065},
        "B": {"(C)": 1.364, "(D)": 0.475, "(E)": 0.066},
    },
    "72071290": {
        "A": {"(C)": 0.453, "(D)": 0.330, "(E)": 0.330},
        "B": {"(C)": 1.629, "(D)": 0.740, "(E)": 0.331},
    },
    "72071912": {
        "A": {"(C)": 0.188, "(D)": 0.065, "(E)": 0.065},
        "B": {"(C)": 1.364, "(D)": 0.475, "(E)": 0.066},
    },
    "72071919": {
        "A": {"(C)": 0.453, "(D)": 0.330, "(E)": 0.330},
        "B": {"(C)": 1.629, "(D)": 0.740, "(E)": 0.331},
    },
    "72071980": {
        "A": {"(C)": 0.188, "(D)": 0.065, "(E)": 0.065},
        "B": {"(C)": 1.364, "(D)": 0.475, "(E)": 0.066},
    },
    "72072011": {
        "A": {"(C)": 0.188, "(D)": 0.065, "(E)": 0.065},
        "B": {"(C)": 1.364, "(D)": 0.475, "(E)": 0.066},
    },
    "72072015": {
        "A": {"(C)": 0.188, "(D)": 0.065, "(E)": 0.065},
        "B": {"(C)": 1.364, "(D)": 0.475, "(E)": 0.066},
    },
    "72072017": {
        "A": {"(C)": 0.188, "(D)": 0.065, "(E)": 0.065},
        "B": {"(C)": 1.364, "(D)": 0.475, "(E)": 0.066},
    },
}


def _norm(cn: str) -> str:
    """يطبع الرمز كما يُدبَّس: بلا مسافات. ⛔ لا يُخمِّن طولاً ولا يُصفّر."""
    key = "".join(cn.split())
    if not key:
        raise PinError("empty CN code")
    return key


def benchmark_resolution(cn: str) -> dict[str, object]:
    """كيف يرتبط رمزُ القيم الافتراضية برمزِ المراجع — **بإجراءٍ معلَن لا بتخمين**.

    المراجعُ مُفهرسةٌ بـ CN8، والملحقُ I يستعمل أحياناً 4 أو 6 خاناتٍ أو TARIC10.
    الإجراءُ: تطابقٌ تامٌّ عند 8، ثم قطعُ الخانات الزائدة والبحثُ عن **كلّ** المرشّحين
    الذين يبدأون بالمقطع. وحين يكون المرشّحون أكثرَ من واحد:

    * إن كانت جداولُهم **متطابقةَ القيم** ⇒ الحلُّ سليم، ويُسجَّل أنّ التطابقَ عدديٌّ
      لا اسميّ (وهذا ما وقع فعلاً في `7203`: `72031000` و`72039000` كلاهما A=0.295 /
      B=0.397 — فالغموضُ في الترقيم لا في الرقم).
    * إن اختلفت ⇒ `None` مع سببٍ منطوق. ⛔ لا يُختار «الأوّل» ولا «المتوسط».

    هذه هي النقطةُ التي ينفصل فيها البحثُ المليمتريّ عن التقدير: الفرقُ بين
    «غيرُ قابلٍ للترتيب» و«قابلٌ للترتيب بقرارٍ معلَن» هنا هو **فحصُ المرشّحين كلّهم**.
    """
    key = _norm(cn)
    if key in BENCHMARKS:
        return {
            "cn": key,
            "resolved": key,
            "candidates": [key],
            "resolution": "EXACT_CN8",
            "reason": None,
        }
    for width in (8, 6, 4):
        if len(key) < width:
            continue
        prefix = key[:width]
        candidates = sorted(b for b in BENCHMARKS if b.startswith(prefix))
        if not candidates:
            continue
        if len(candidates) == 1:
            return {
                "cn": key,
                "resolved": candidates[0],
                "candidates": candidates,
                "resolution": "PREFIX_UNIQUE",
                "reason": None,
            }
        tables = {json.dumps(BENCHMARKS[c], sort_keys=True) for c in candidates}
        if len(tables) == 1:
            return {
                "cn": key,
                "resolved": candidates[0],
                "candidates": candidates,
                "resolution": "PREFIX_VALUE_IDENTICAL",
                "reason": None,
                "note_ar": (
                    f"المرشّحون {candidates} متطابقو القيم ⇒ الغموضُ في الترقيم لا في "
                    "الرقم، فالحلُّ سليمٌ ومسجَّل."
                ),
            }
        return {
            "cn": key,
            "resolved": None,
            "candidates": candidates,
            "resolution": "PREFIX_AMBIGUOUS_VALUES_DIFFER",
            "reason": "BENCHMARK_PREFIX_AMBIGUOUS_VALUES_DIFFER",
        }
    return {
        "cn": key,
        "resolved": None,
        "candidates": [],
        "resolution": "NOT_FOUND",
        "reason": "BENCHMARKS_NOT_EXTRACTED",
    }


def _benchmark_cn(cn: str) -> str | None:
    """المرجعُ المحلول — ⛔ `None` حين لا إجراءَ سليم يقرّره (انظر `benchmark_resolution`)."""
    resolved = benchmark_resolution(cn)["resolved"]
    return str(resolved) if resolved is not None else None


def _resolve(cn: str, column: str, route: str | None) -> float | None:
    """المرجعُ إن كان قابلاً للحلّ من مسار البلد، وإلا `None` — ⛔ لا افتراض.

    حالةٌ واقعةٌ في الدبابيس نفسها: `31025000` (نترات الصوديوم) مرجعاه مقسومان على
    مؤشرَين `(1)/(2)` بينما الصفُّ الجزائريّ **لا يحمل مؤشراً** ⇒ الرمزُ غيرُ قابلٍ
    للترتيب، وسببُه منطوق. التخمينُ هنا هو بالضبط ما أنتج أرقامَ الدفعات السابقة.
    """
    try:
        return _bm(cn, column, route)
    except UnpinnedError:
        return None


def pinned_codes() -> dict[str, dict[str, object]]:
    """جردُ ما هو مدبوسٌ فعلاً: صفٌّ بلدِيٌّ **و** مرجعٌ A **و** مرجعٌ B **قابلان للحلّ**."""
    out: dict[str, dict[str, object]] = {}
    for cn, row in ALGERIA_DEFAULTS.items():
        resolution = benchmark_resolution(cn)
        bm_cn = resolution["resolved"]
        if row.total is None:
            reason = "NO_COUNTRY_VALUE_USE_OTHER_COUNTRIES_TABLE"
        elif bm_cn is None:
            reason = "BENCHMARKS_NOT_EXTRACTED"
        elif _resolve(cn, "B", row.route) is None or _resolve(cn, "A", row.route) is None:
            table = BENCHMARKS[_benchmark_cn(cn)]
            reason = (
                "BENCHMARK_ROUTE_KEYS_UNPAIRED"
                if not (set(table["A"]) & set(table["B"]))
                else "BENCHMARK_ROUTE_AMBIGUOUS_COUNTRY_ROW_HAS_NO_INDICATOR"
            )
        else:
            reason = None
        out[cn] = {
            "sector": row.sector,
            "benchmark_cn": bm_cn,
            "benchmark_candidates": resolution["candidates"],
            "benchmark_resolution": resolution["resolution"],
            "route_pinned": row.route,
            "rankable": reason is None,
            "absent_reason": reason,
        }
    return out


def column_asymmetry() -> dict[str, object]:
    """**نتيجةٌ لا مُدخَل**: هل العمودُ B أكبرُ من A دائماً؟

    الجوابُ المفيدُ أدقُّ من «نعم» ومن «لا»: **B ≥ A في كلّ زوجٍ مدبوس، بلا استثناءٍ
    واحدٍ معاكس، لكن في 17 زوجاً من 90 يتساوى العمودان تماماً** — وهناك الرسمُ صفر.
    الإبلاغُ عن «B أكبرُ دائماً» كان تعميماً يسقط عند أول رمزٍ متساوٍ؛ والإبلاغُ عن
    التوزيع يجعل الحكمَ قابلاً للدفاع: **الانتقالُ من العمود B إلى A لا يربح اعتماداً
    قطّ، ويخسره في 81.1% من الأزواج**.
    """
    b_larger: list[str] = []
    a_larger: list[str] = []
    equal: list[str] = []
    for cn, table in sorted(BENCHMARKS.items()):
        for route in sorted(set(table["A"]) & set(table["B"])):
            a, b = table["A"][route], table["B"][route]
            key = f"{cn}{route}"
            if b - a > 5e-4:
                b_larger.append(key)
            elif a - b > 5e-4:
                a_larger.append(key)
            else:
                equal.append(key)
    total = len(b_larger) + len(a_larger) + len(equal)
    return {
        "route_pairs_pinned": total,
        "unpaired_benchmark_cns": unpaired_benchmark_cns(),
        "column_b_larger": len(b_larger),
        "column_a_larger": len(a_larger),
        "columns_equal": len(equal),
        "max_gap_t": round(max((_gap(c) for c in BENCHMARKS), default=0.0), 5),
        "share_where_switching_forfeits_credit": (
            round(len(b_larger) / total, 4) if total else None
        ),
        "unpaired_benchmark_cns": unpaired_benchmark_cns(),
        "column_a_larger_pairs": a_larger,
        "tied_pairs": equal,
        "asymmetry_is_universal_ar": (
            "لا زوجَ واحداً فيه A > B ⇒ التخلّي عن الاعتماد لا يُعوَّض أبداً. "
            "لكنّ التعادلَ موجودٌ في 17 زوجاً (الرمزُ الكاملُ في `tied_pairs`) وهناك "
            "رسمُ المسار صفر، فالانتقالُ فيها **لا يُكلِّف** شيئاً على جانب الاعتماد."
        ),
    }


def _gap(cn: str) -> float:
    table = BENCHMARKS[cn]
    shared = set(table["A"]) & set(table["B"])
    if not shared:  # مرجعٌ من عمودٍ واحد ⇒ لا زوجَ يُقارَن
        return 0.0
    return max(table["B"][r] - table["A"][r] for r in shared)


def unpaired_benchmark_cns() -> list[str]:
    """رموزٌ مرجعيّةٌ **مفاتيحُ مسارَيها غير متطابقة** ⇒ ⛔ لا زوجَ يُقارَن.

    مثالٌ واقعيّ: `72051000` عمودُه A مُفهرَسٌ بمفتاحٍ فارغٍ (لا مؤشرَ مسار) بينما
    عمودُه B مُفهرَسٌ بـ `(C)/(D)/(E)`. الملفُّ الرسميّ لا يقرنهما، ونحن لا نخمّن
    القرين: الرمزُ يُخرَج من الجدول ويُعلَن بالاسم.
    """
    return sorted(cn for cn, t in BENCHMARKS.items() if not (set(t["A"]) & set(t["B"])))


def closure_audit() -> dict[str, object]:
    """**نتيجةٌ لا مُدخَل**: هل تُغلق أعمدةُ الملفّ الرسميّ نفسه؟

    يفحص كلّ صفٍّ بلدِيٍّ مُدبَّس بثلاثة أعمدةٍ مغلقة ويقيس
    `total − (direct + indirect)`. الصفوفُ التي لا تُغلق ليست خطأً في النقل — بل
    **خاصيةٌ في المنشور**: كلّ عمودٍ مُقرَّبٌ إلى ثلاث خاناتٍ على حدة، ونصُّ
    الملحق (S6) يأمر باختيار **عمود الإجمالي**.

    الأثرُ القابلُ للبيع: لا يجوز لأحدٍ أن يعيد بناء الإجمالي من مكوّناته، ولا أن
    يستعمل «غير المباشر المنشور» مع «مباشرٍ محسوب» ثم يقارن الناتج بالقيمة
    البلدِيّة. من يفعل ذلك في سلعةٍ مركَّبة يحصل على رقمٍ يختلف عن الرقم الملزم
    بمقدارٍ **محسوبٍ هنا**.
    """
    open_rows: list[dict[str, object]] = []
    gaps: list[float] = []
    closed_rows = 0
    partial_rows = 0
    for cn, row in sorted(ALGERIA_DEFAULTS.items()):
        gap = row.closure_gap
        if gap is None:
            partial_rows += 1
            continue
        if abs(gap) < 5e-4:
            closed_rows += 1
            continue
        open_rows.append(
            {
                "cn": cn,
                "sector": row.sector,
                "description": row.description,
                "direct": row.direct,
                "indirect": row.indirect,
                "total": row.total,
                "gap_t": gap,
                "gap_eur_per_t_2026Q2": round(gap * _price(), 2),
                "operative_column": "total",
                "rule_source": "S6",
            }
        )
        gaps.append(abs(gap))
    return {
        "rows_pinned": len(ALGERIA_DEFAULTS),
        "rows_with_three_columns": closed_rows + len(open_rows),
        "rows_closed": closed_rows,
        "rows_open": len(open_rows),
        "rows_partial_absent": partial_rows,
        "open_rows": open_rows,
        "max_abs_gap_t": round(max(gaps), 5) if gaps else 0.0,
        "all_gaps_are_rounding_scale": bool(gaps) and max(gaps) <= 0.010 + 1e-9,
        "law_ar": (
            "الإجماليّ كميةٌ أولية لا مجموع: «the default values of the column "
            "'total emissions' shall be selected» (S6). ⛔ لا يُعاد بناؤه من مكوّناته."
        ),
    }


# ── الصيغة ──────────────────────────────────────────────────────────────────────
#
# لكلّ طنّ:
#   NC_default = SEE_d × (1 + mark-up) − f × CSCF × BM_B(route_d)
#   NC_actual  = SEE_a              − f × CSCF × BM_A(route_a)
#   cost       = NC × certificate_price      (سالبٌ ⇒ صفر: «تُصفَّر ولا تُستردّ» — S5)
#
# ⇒ الوفرُ من إعلان البيانات الفعلية:
#   saving = [SEE_d × mark-up] − f × CSCF × (BM_B − BM_A) − (SEE_a − SEE_d)
#            └─ إعفاءُ العلاوة ─┘   └──── رسمُ المسار ────┘   └─ تحسينُ المنشأة ─┘


def _check_year(year: int) -> None:
    """⛔ لا استمرار: من 2035 «لا ينطبق معامل CBAM» (S3) فالصيغةُ تتغيّر."""
    if year not in HORIZON:
        raise PinError(
            f"year {year} is outside the pinned horizon {HORIZON[0]}-{HORIZON[-1]}: "
            "the CBAM factor is 0 from 2034 and the formula changes thereafter"
        )


def _f(mapping: dict[str, object], key: str) -> float:
    """قارئٌ مُعنوَن — `dict[str, object]` هو عرفُ الحزمة، والحسابُ يحتاج `float`.

    ⛔ ليس `float(str(...))` التفافياً (وهو ما نُقِد في D-294): يفشل بصوتٍ عالٍ إن
    كان الحقلُ غيرَ عدديّ، فلا يُبتلع خطأُ نوعٍ في رقمٍ ماليّ.
    """
    value = mapping[key]
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise PinError(f"{key}: expected a number, got {type(value).__name__}")
    return float(value)


def _flag(mapping: dict[str, object], key: str) -> bool:
    """قارئٌ مُعنوَن للرايات — ⛔ لا `bool(object)` صامتة."""
    value = mapping[key]
    if not isinstance(value, bool):
        raise PinError(f"{key}: expected a bool, got {type(value).__name__}")
    return value


def _price(quarter: str = DEFAULT_QUARTER) -> float:
    value = CERT_PRICE_EUR.get(quarter, None)
    if value is None:
        raise UnpinnedError(
            f"certificate price for {quarter} is not published yet - absent is None, not Q2"
        )
    return value


def _bm(cn: str, column: str, route: str | None) -> float:
    bm_cn = _benchmark_cn(cn)
    if bm_cn is None:
        raise UnpinnedError(f"{cn}: CBAM benchmarks (columns A and B) were not extracted")
    table = BENCHMARKS[bm_cn][column]
    key = route or ""
    if key in table:
        return table[key]
    if "" in table:
        return table[""]
    raise UnpinnedError(
        f"{cn}: no column-{column} benchmark for route {route!r} (have {sorted(table)})"
    )


def default_route(cn: str) -> str | None:
    """مسارُ الإنتاج المُدبَّس للبلد — هو الذي يختار عمودَ B (S5: «the same
    production route shall be used as indicated in Annex I»)."""
    row = ALGERIA_DEFAULTS.get(_norm(cn))
    if row is None:
        raise PinError(f"{cn}: no Algerian default row pinned")
    return row.route


def sefa(cn: str, year: int, column: str, route: str | None, cscf: float | None = None) -> float:
    """التخصيصُ المجانيّ النوعيّ (tCO₂e/t) = f × CSCF × BM."""
    if year not in CBAM_FACTOR:
        raise PinError(f"year {year} outside the pinned horizon {HORIZON[0]}-{HORIZON[-1]}")
    factor = CBAM_FACTOR[year]
    correction = CSCF[year] if cscf is None else cscf
    return factor * correction * _bm(cn, column, route)


def certificates_default(cn: str, year: int, quarter: str = DEFAULT_QUARTER) -> dict[str, object]:
    """كلفةُ الطنّ باليورو حين يُعلَن بالقيمة الافتراضية (مسارُ «لا تفعل شيئاً»)."""
    _check_year(year)
    row = ALGERIA_DEFAULTS.get(_norm(cn))
    if row is None:
        raise PinError(f"{cn}: no Algerian default row pinned")
    if row.total is None:
        raise UnpinnedError(
            f"{cn}: Algeria has no country value - "
            "the 'Other countries and territories' table applies"
        )
    markup = MARKUP[row.sector][year]
    gross = row.total * (1.0 + markup)
    deduction = sefa(cn, year, "B", row.route)
    net = max(0.0, gross - deduction)
    return {
        "cn": row.cn,
        "sector": row.sector,
        "year": year,
        "quarter": quarter,
        "see_default_t": row.total,
        "markup": markup,
        "marked_up_see_t": round(gross, 5),
        "sefa_t": round(deduction, 5),
        "net_certificates_t": round(net, 5),
        "eur_per_t": round(net * _price(quarter), 2),
    }


def certificates_actual(
    cn: str,
    year: int,
    see_actual: float,
    route: str | None = None,
    quarter: str = DEFAULT_QUARTER,
) -> dict[str, object]:
    """كلفةُ الطنّ باليورو حين تُعلَن بياناتٌ فعلية مُتحقَّق منها بمسارٍ مُثبَت."""
    _check_year(year)
    if see_actual < 0:
        raise PinError("negative specific embedded emissions are not a measurement")
    route = default_route(cn) if route is None else route
    deduction = sefa(cn, year, "A", route)
    unfloored = see_actual - deduction
    net = max(0.0, unfloored)
    return {
        "cn": _norm(cn),
        "year": year,
        "quarter": quarter,
        "see_actual_t": see_actual,
        "route": route,
        "sefa_t": round(deduction, 5),
        "unfloored_t": round(unfloored, 5),
        "net_certificates_t": round(net, 5),
        "eur_per_t": round(net * _price(quarter), 2),
        #: الأرضيةُ مُلزِمة: منشأةٌ أنظفُ من مرجع العمود A لا تستردّ شيئاً (S5).
        "floor_binding": unfloored < 0,
    }


def path_toll(cn: str, year: int, route_actual: str | None = None) -> dict[str, object]:
    """**رسمُ المسار** (CPN-1): ما تُسلِّمه من اعتمادٍ مجانيّ حين تنتقل إلى الفعليّ.

    = f × CSCF × (BM_B(route_default) − BM_A(route_actual))

    موجبٌ ⇒ الانتقالُ يُكلِّف. صفرٌ ⇒ العمودان متطابقان ولا رسم. سالبٌ ⇒ الانتقالُ
    يمنح اعتماداً أكبر (لم يُرصد في أيّ رمزٍ مدبوس — وK1 هو شرطُ قتله).
    """
    _check_year(year)
    route_default = default_route(cn)
    route_actual = route_default if route_actual is None else route_actual
    bm_b = _bm(cn, "B", route_default)
    bm_a = _bm(cn, "A", route_actual)
    factor = CBAM_FACTOR[year] * CSCF[year]
    return {
        "cn": _norm(cn),
        "year": year,
        "route_default": route_default,
        "route_actual": route_actual,
        "bm_b_t": bm_b,
        "bm_a_t": bm_a,
        "benchmark_gap_t": round(bm_b - bm_a, 5),
        "toll_t": round(factor * (bm_b - bm_a), 5),
        "toll_eur_per_t": round(factor * (bm_b - bm_a) * _price(), 2),
    }


def markup_relief(cn: str, year: int) -> dict[str, object]:
    """**إعفاءُ العلاوة**: ما تكسبه من حذف العلاوة حين تنتقل إلى الفعليّ."""
    _check_year(year)
    row = ALGERIA_DEFAULTS[_norm(cn)]
    if row.total is None:
        raise UnpinnedError(f"{cn}: no country value pinned")
    markup = MARKUP[row.sector][year]
    return {
        "cn": row.cn,
        "year": year,
        "markup": markup,
        "relief_t": round(row.total * markup, 5),
        "relief_eur_per_t": round(row.total * markup * _price(), 2),
    }


def net_required_reduction(
    cn: str, year: int, route_actual: str | None = None
) -> dict[str, object]:
    """**صافي الرسم المطلوب**: كم يجب أن تكون المنشأةُ أنظفَ من قيمتها البلدِيّة
    كي يكون الانتقالُ إلى البيانات الفعلية مربحاً — بصرف النظر عن أيّ رقمٍ فعليّ.

    = رسمُ المسار − إعفاءُ العلاوة   (tCO₂e/t)

    هذه هي الكميةُ القابلةُ للبيع: كلُّ مدخلاتها من المصدر الأوّلي، ⛔ ولا واحدٌ
    منها افتراضٌ عن المنشأة.
    """
    _check_year(year)
    toll = path_toll(cn, year, route_actual)
    relief = markup_relief(cn, year)
    required = _f(toll, "toll_t") - _f(relief, "relief_t")
    return {
        "cn": toll["cn"],
        "year": year,
        "toll_t": toll["toll_t"],
        "relief_t": relief["relief_t"],
        "required_reduction_t": round(required, 5),
        "required_reduction_eur_per_t": round(required * _price(), 2),
        "route_default": toll["route_default"],
        "route_actual": toll["route_actual"],
    }


def crossover_see(cn: str, year: int, route_actual: str | None = None) -> dict[str, object]:
    """**عتبةُ العبور**: أعلى SEE فعليّ يبقى معه إعلانُ البيانات الفعلية أرخص.

    SEE_a < SEE_d × (1+m) − f × CSCF × BM_B + f × CSCF × BM_A

    ⛔ ليست رأياً ولا تقديراً: كلّ طرفٍ فيها مدبوس. ومقارنتُها برقمِ المنشأة هي
    القرار — ونحن لا نملك رقمَ المنشأة ولا ندّعيه.
    """
    _check_year(year)
    row = ALGERIA_DEFAULTS[_norm(cn)]
    if row.total is None:
        raise UnpinnedError(
            f"{cn}: no country value pinned - 'Other countries' table applies"
        )
    route_default = row.route
    route_actual = route_default if route_actual is None else route_actual
    markup = MARKUP[row.sector][year]
    gross = row.total * (1.0 + markup)
    credit = sefa(cn, year, "B", route_default) - sefa(cn, year, "A", route_actual)
    return {
        "cn": row.cn,
        "sector": row.sector,
        "year": year,
        "route_default": route_default,
        "route_actual": route_actual,
        "marked_up_see_t": round(gross, 5),
        "sefa_credit_t": round(credit, 5),
        "crossover_see_t": round(gross - credit, 5),
    }


def saving(
    cn: str,
    year: int,
    see_actual: float,
    route_actual: str | None = None,
    quarter: str = DEFAULT_QUARTER,
) -> dict[str, object]:
    """الوفرُ الصافي باليورو/طنّ من إعلان بياناتٍ فعلية بدل الافتراضية."""
    base = certificates_default(cn, year, quarter)
    alt = certificates_actual(cn, year, see_actual, route_actual, quarter)
    delta_t = _f(base, "net_certificates_t") - _f(alt, "net_certificates_t")
    verdict = (
        Verdict.EXACTLY_AT_CROSSOVER
        if abs(delta_t) < 5e-5
        else (Verdict.ACTUAL_CHEAPER if delta_t > 0 else Verdict.DEFAULT_CHEAPER)
    )
    naive = round(max(0.0, _f(base, "marked_up_see_t") - see_actual) * _price(quarter), 2)
    ceiling = _f(base, "eur_per_t")
    return {
        "cn": base["cn"],
        "year": year,
        "quarter": quarter,
        "see_actual_t": see_actual,
        "default_eur_per_t": ceiling,
        "actual_eur_per_t": _f(alt, "eur_per_t"),
        "saving_eur_per_t": round(delta_t * _price(quarter), 2),
        "naive_gap_eur_per_t": naive,
        #: **السقف**: أقصى ما يمكن أن تبلغه قيمةُ البيانات الفعلية هو الفاتورةُ كلّها،
        #: لأنّ كلفة المسار الفعليّ لا تنزل تحت الصفر (أرضية S5). ⛔ لا استرداد.
        "ceiling_eur_per_t": ceiling,
        #: **دحضٌ بلا بيانات**: إذا تجاوزت «الفجوةُ الساذجة» السقفَ فالادّعاءُ مستحيلٌ
        #: حسابياً — لا يحتاج انبعاثَ منشأةٍ ليُرفَض.
        "naive_exceeds_ceiling": naive > ceiling + 1e-9,
        "ceiling_excess_eur_per_t": round(naive - ceiling, 2) if naive > ceiling else 0.0,
        "verdict": verdict,
    }


def unconditional_year(
    cn: str, route_actual: str | None = None
) -> dict[str, object]:
    """أوّلُ سنةٍ يصير فيها الانتقالُ مربحاً **ولو لم تُخفِّض المنشأةُ شيئاً**.

    الشرط: `required_reduction ≤ 0`، أي أنّ رسمَ المسار صار أصغرَ من إعفاء العلاوة.
    هذه أطهرُ نتيجةٍ في الدفعة لأنها **لا تحتاج أيّ رقمٍ عن المنشأة**: كلّ طرفيها
    مدبوس. وتُجيب السؤال التجاريّ الوحيد الذي يهمّ المشتري: «متى يصير شراءُ
    البيانات إلزامياً اقتصادياً بلا شرط؟» — بتاريخ، لا برجاء.
    """
    hit: int | None = None
    trajectory: list[dict[str, object]] = []
    for year in HORIZON:
        required = _f(net_required_reduction(cn, year, route_actual), "required_reduction_t")
        trajectory.append({"year": year, "required_reduction_t": required})
        if hit is None and required <= 0.0:
            hit = year
    return {
        "cn": _norm(cn),
        "route_actual": route_actual if route_actual is not None else default_route(cn),
        "unconditional_year": hit,
        "trajectory": trajectory,
        "never_within_horizon": hit is None,
    }


def overstatement(
    cn: str, year: int, see_actual: float, route_actual: str | None = None
) -> dict[str, object]:
    """حجمُ الخطأ في الأطروحة القديمة: «الفجوةُ هي الوفر».

    `naive_gap / saving` — وحين يكون الوفرُ الصافي ≤ 0 فالنسبةُ **ليست رقماً كبيراً**
    بل `None` بسببٍ منطوق: الإشارةُ انقلبت، والقسمةُ على ما دون الصفر تُنتج وهماً
    ثانياً. الفراغُ `None` لا صفر (D-212).
    """
    result = saving(cn, year, see_actual, route_actual)
    naive = _f(result, "naive_gap_eur_per_t")
    real = _f(result, "saving_eur_per_t")
    ceiling = _f(result, "ceiling_eur_per_t")
    exceeds = _flag(result, "naive_exceeds_ceiling")
    if real <= 0:
        return {
            "cn": result["cn"],
            "year": year,
            "see_actual_t": see_actual,
            "naive_gap_eur_per_t": naive,
            "saving_eur_per_t": real,
            "ceiling_eur_per_t": ceiling,
            "ceiling_excess_eur_per_t": round(naive - ceiling, 2) if exceeds else 0.0,
            "naive_exceeds_ceiling": exceeds,
            "ratio": None,
            "reason": "SIGN_FLIP: the actual-data path costs more than the default path",
            "verdict": result["verdict"],
        }
    # هنا `real > 0` بحكم الفرع ⇒ القسمةُ معرَّفة، ⛔ ولا `if real else None` زائدة (SIM)
    return {
        "cn": result["cn"],
        "year": year,
        "see_actual_t": see_actual,
        "naive_gap_eur_per_t": naive,
        "saving_eur_per_t": real,
        "ceiling_eur_per_t": ceiling,
        "ceiling_excess_eur_per_t": round(naive - ceiling, 2) if exceeds else 0.0,
        "naive_exceeds_ceiling": exceeds,
        "ratio": round(naive / real, 4),
        "reason": None,
        "verdict": result["verdict"],
    }


def error_identity(
    cn: str, year: int, route_actual: str | None = None
) -> dict[str, object]:
    """**برهانٌ مغلقٌ لا يحتاج انبعاثَ منشأة**: حجمُ الخطأ في الأطروحة القديمة ثابت.

    لتكن `SEEₘ` = القيمة البلدِيّة × (1+العلاوة)، و`SEFA_B`/`SEFA_A` اعتمادا
    العمودين. الخطأُ = «الفجوةُ الساذجة» − «الوفرُ الحقيقيّ»:

    * إن كان `SEFA_A ≤ SEE ≤ SEEₘ`  ⇒  الخطأ = `SEFA_B − SEFA_A` = **رسمُ المسار
      بالضبط**، وثابتٌ بالنسبة إلى `SEE`. أي أنّ كلّ ادّعاءٍ «وفّرنا الفجوة» يُبالغ
      بمقدارٍ **محسوبٍ سلفاً بلا أيّ بياناتٍ عن المنشأة**.
    * إن كان `SEE < SEFA_A`  ⇒  الخطأ = `SEFA_B − SEE`، **يكبر كلّما نظُفت المنشأة**،
      لأنّ أرضية الصفر (S5) تمنع الاسترداد بينما الفجوةُ الساذجة تستمرّ في الاتّساع.
    * إن كان `SEE > SEEₘ`  ⇒  الفجوةُ الساذجة تُصفَّر (لا يُدّعى وفرٌ سالب) بينما
      الوفرُ الحقيقيّ يزداد سالبية ⇒ الخطأُ غيرُ محدود.

    هاتان الحالتان تُختبَران على شبكةٍ من القيم، والحالةُ الأولى تُثبَت جبرياً:
    `(SEEₘ−SEE) − [(SEEₘ−SEFA_B) − (SEE−SEFA_A)] = SEFA_B − SEFA_A`.
    """
    route = default_route(cn) if route_actual is None else route_actual
    sefa_b = sefa(cn, year, "B", default_route(cn))
    sefa_a = sefa(cn, year, "A", route)
    marked = _f(certificates_default(cn, year), "marked_up_see_t")
    toll = round((sefa_b - sefa_a) * _price(), 2)

    #: التسامحُ سنتيمان: كلّ طرفٍ في `saving()` مُقرَّبٌ على حدة، فالمقارنةُ
    #: الحرفيّة تقيس التقريبَ لا الهوية.
    TOL = 0.02
    above: list[bool] = []
    below: list[bool] = []
    beyond: list[float] = []
    step = 0.05

    value = sefa_a
    while value <= marked + 1e-9:
        out = saving(cn, year, value, route_actual)
        error = _f(out, "naive_gap_eur_per_t") - _f(out, "saving_eur_per_t")
        above.append(abs(error - toll) <= TOL)
        value = round(value + step, 5)

    value = 0.0
    while value < sefa_a - 1e-9:
        out = saving(cn, year, value, route_actual)
        error = _f(out, "naive_gap_eur_per_t") - _f(out, "saving_eur_per_t")
        below.append(abs(error - (sefa_b - value) * _price()) <= TOL)
        value = round(value + step, 5)

    value = round(marked + step, 5)
    while value <= marked + 2.0:
        out = saving(cn, year, value, route_actual)
        assert _f(out, "naive_gap_eur_per_t") == 0.0
        beyond.append(_f(out, "saving_eur_per_t"))
        value = round(value + step, 5)

    return {
        "cn": _norm(cn),
        "year": year,
        "route": route,
        "toll_eur_per_t": toll,
        "marked_up_default_t": marked,
        "regime_above_column_a_error_is_constant": bool(above) and all(above),
        "grid_points_above": len(above),
        "regime_below_column_a_error_grows": (not below) or all(below),
        "grid_points_below": len(below),
        "regime_beyond_default_naive_clips_to_zero": (not beyond)
        or all(beyond[i] >= beyond[i + 1] for i in range(len(beyond) - 1)),
        "saturation_point_see_t": round(sefa_a, 5),
        "max_real_saving_eur_per_t": round(max(0.0, marked - sefa_b) * _price(), 2),
        "error_at_zero_emissions_eur_per_t": round(sefa_b * _price(), 2),
        "tolerance_eur": TOL,
        "claim_ar": (
            "الخطأُ في «الفجوةُ هي الوفر» = رسمُ المسار بالضبط، ثابتٌ لكلّ انبعاثٍ بين "
            "مرجع العمود A والقيمة البلدِيّة المُعلاة — فيُحسَب **قبل** أن تُقاس أيُّ "
            "منشأة. وتحت مرجع العمود A يكبر الخطأ مع النظافة لأنّ الأرضيةَ تمنع "
            "الاسترداد، وفوق القيمة المُعلاة تُصفَّر الفجوةُ الساذجة بينما يستمرّ الوفرُ "
            "الحقيقيّ في السالبية."
        ),
    }


def first_sellable_year(
    cn: str, see_actual: float, route_actual: str | None = None
) -> dict[str, object]:
    """أوّلُ سنةٍ يصير فيها منتَجُ البيانات الفعلية **أرخصَ** للمشتري.

    العتبةُ تتّسع كلّ سنة (العلاوةُ تصعد، ومعاملُ CBAM يهبط) ⇒ الإجابةُ ليست
    «نعم/لا» بل **تاريخ**. والتاريخُ هو ما يُسعَّد به عقدٌ لا يُسعَّد بوعظ.
    `None` ⇒ لا تنقلب داخل الأفق، ⛔ ولا يُقرأ «أبداً».
    """
    flipped: int | None = None
    trajectory: list[dict[str, object]] = []
    for year in HORIZON:
        cross = _f(crossover_see(cn, year, route_actual), "crossover_see_t")
        trajectory.append({"year": year, "crossover_see_t": cross})
        if flipped is None and see_actual < cross:
            flipped = year
    return {
        "cn": _norm(cn),
        "see_actual_t": see_actual,
        "first_sellable_year": flipped,
        "trajectory": trajectory,
        "never_within_horizon": flipped is None,
    }


# ── شروطُ القتل ─────────────────────────────────────────────────────────────────


def kill_switches() -> dict[str, object]:
    """خمسةُ شروطٍ تُبطل الدفعة — لكلٍّ حالةٌ محسوبةٌ من القرص، ⛔ لا من النية."""
    gaps = [_max_gap(c) for c in BENCHMARKS]
    positive_tolls = [g for g in gaps if g is not None and g > 0]
    return {
        "K1": {
            "statement_ar": (
                "نُشر ملحقٌ يجعل العمودَ A مساوياً للعمود B لكلّ رمزٍ مدبوس ⇒ يسقط "
                "رسمُ المسار كلّه وتعود الأطروحةُ القديمة (الفجوةُ = الوفر) صحيحة."
            ),
            "fired": len(positive_tolls) == 0,
            "evidence": {"codes_with_positive_benchmark_gap": len(positive_tolls), "codes_examined": len(BENCHMARKS)},
        },
        "K2": {
            "statement_ar": (
                "نُشر القرار 2026/1862 بقيمة CSCF ≠ 1 ⇒ تُعاد كلُّ العتبات؛ والحساسيةُ "
                "معلنةٌ في `cscf_sensitivity`."
            ),
            "fired": any(abs(v - 1.000) > 1e-9 for v in CSCF.values()),
            "evidence": {"cscf_pinned": CSCF[2026], "grade_of_source": SOURCES["S8"]["grade"]},
        },
        "K3": {
            "statement_ar": (
                "صدر نصٌّ أوّليّ يجعل معاملَ CBAM مضروباً في **الانبعاث** لا في المرجع "
                "(قراءة cbamguide: 2.5% في 2026) ⇒ تُبطل الصيغةُ كلَّ قياسٍ هنا."
            ),
            "fired": CBAM_FACTOR[2026] != 0.975,
            "evidence": {
                "cbam_factor_2026": CBAM_FACTOR[2026],
                "independent_anchors": ["S3", "S4", "S5"],
                "contradicted_reading": "net = gross x 2.5% (secondary, single-source)",
            },
        },
        "K4": {
            "statement_ar": (
                "صُحِّح الملحقُ مرّةً ثالثة (سجلُّ النسخ في S1 يُظهر v1→v2 في ستة أشهر) "
                "⇒ كلُّ دبوسٍ هنا قابلٌ للتقادم، وإعادةُ الاستخراج إلزاميةٌ قبل أيّ عرض."
            ),
            "fired": SOURCES["S1"]["quote"].split("|")[0].strip() != "Version 2",
            "evidence": {"version_history": SOURCES["S1"]["quote"], "act": "IR (EU) 2026/1740"},
        },
        "K5": {
            "statement_ar": (
                "استُخرجت مراجعُ الألومنيوم A/B ⇒ الرموزُ `UNRANKABLE` تصير قابلةً "
                "للترتيب ويجب إعادةُ الحساب، لا توسيعُ الجدول القديم."
            ),
            "fired": any(cn.startswith("76") for cn in BENCHMARKS),
            "evidence": {"aluminium_benchmarks_extracted": 0, "aluminium_default_rows_pinned": _aluminium_rows()},
        },
    }


def _max_gap(bm_cn: str) -> float | None:
    """أكبرُ فرقٍ بين العمودين لرمزٍ واحد؛ `None` حين لا يُقارَن مسارٌ بمسار."""
    table = BENCHMARKS[bm_cn]
    a, b = table["A"], table["B"]
    keys = set(a) & set(b)
    if not keys:
        return None
    return max(b[k] - a[k] for k in keys)


def _aluminium_rows() -> int:
    return sum(1 for row in ALGERIA_DEFAULTS.values() if row.sector == "aluminium")


def cscf_sensitivity(
    cn: str, year: int, route_actual: str | None = None
) -> dict[str, object]:
    """كم تتحرّك العتبةُ لو كان CSCF ≠ 1 — لأنّ درجته **ب** لا أ (S8 · K2).

    ⛔ لا تُستعمل لتبرير الثقة: تُستعمل لإعلان أنّ كلّ رقمٍ باليورو في هذه الدفعة
    **مشروط**، وأنّ شرطَه رقمٌ لم يُقرأ نصُّه الأوّليّ.
    """
    _check_year(year)
    key = _norm(cn)
    row = ALGERIA_DEFAULTS[key]
    if row.total is None:
        raise UnpinnedError(f"{cn}: no country value pinned")
    base = _f(crossover_see(cn, year, route_actual), "crossover_see_t")
    markup = MARKUP[row.sector][year]
    gross = row.total * (1.0 + markup)
    route_default = row.route
    route_a = route_default if route_actual is None else route_actual
    gap = _bm(cn, "B", route_default) - _bm(cn, "A", route_a)

    variants: dict[str, float] = {}
    for value in CSCF_SENSITIVITY:
        factor = CBAM_FACTOR[year] * value
        variants[str(value)] = round(gross - factor * gap, 5)
    spread = max(variants.values()) - min(variants.values())
    return {
        "cn": key,
        "year": year,
        "base_cscf_1.000": base,
        "variants": variants,
        "spread_t": round(spread, 5),
        "base_agrees_with_variant_1.000": abs(base - variants["1.0"]) < 1e-9,
    }


# ── الحمولة ─────────────────────────────────────────────────────────────────────


def _inputs() -> dict[str, object]:
    return {
        "as_of": AS_OF,
        "batch": BATCH,
        "horizon": list(HORIZON),
        "cbam_factor": CBAM_FACTOR,
        "cscf": CSCF,
        "markup": MARKUP,
        "cert_price_eur": CERT_PRICE_EUR,
        "candidate_see": CANDIDATE_SEE,
        "algeria_defaults": {
            cn: [row.sector, row.direct, row.indirect, row.total, row.route]
            for cn, row in sorted(ALGERIA_DEFAULTS.items())
        },
        "benchmarks": {cn: BENCHMARKS[cn] for cn in sorted(BENCHMARKS)},
        "sources": {sid: SOURCES[sid] for sid in sorted(SOURCES)},
    }


def inputs_fingerprint() -> str:
    """بصمةُ المُدخَلات — sha256 محسوبةٌ فعلاً على ترميزٍ قانونيٍّ ثابت."""
    canonical = json.dumps(_inputs(), sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def self_check() -> None:
    """حارسٌ حتميٌّ على الدبابيس نفسها — يسقط لو حُرِّف رقمٌ منقول."""
    # القيمةُ البلدِيّة لصلب الكربون الجزائريّ موحّدةٌ على المسار (C) — وهذه نتيجة
    carbon = [
        row for row in ALGERIA_DEFAULTS.values()
        if row.sector == "iron_steel" and row.route == ALGERIA_CARBON_STEEL_ROUTE
    ]
    assert carbon and {row.total for row in carbon} == {3.000}, {row.total for row in carbon}
    # دبابيسُ اسميةٌ مُقتبسةٌ حرفياً من S1/S2 — أيُّ تحريكٍ لها يُسقط البصمة وهذا الحارس
    assert ALGERIA_DEFAULTS["25232900"].total == 1.300
    assert ALGERIA_DEFAULTS["31021019"].total == 1.410
    assert ALGERIA_DEFAULTS["31023090"].total == 2.420
    assert ALGERIA_DEFAULTS["72071114"].total == 3.000
    assert BENCHMARKS["25232900"]["A"] == {"": 0.000}
    assert BENCHMARKS["25232900"]["B"] == {"": 0.666}
    assert BENCHMARKS["31021019"] == {"A": {"": 0.053}, "B": {"": 0.902}}
    assert BENCHMARKS["31023090"] == {"A": {"": 0.019}, "B": {"": 0.767}}
    assert BENCHMARKS["72071114"]["A"]["(C)"] == 0.188
    assert BENCHMARKS["72071114"]["B"]["(C)"] == 1.364
    # ⛔ الألومنيوم غيرُ مُستخرج — هذا التأكيد يسقط يوم يُستخرج، وهو السقوط المطلوب
    assert not any(cn.startswith("76") for cn in BENCHMARKS)
    # اتجاهُ معامل CBAM: يهبط رتيباً (S3)
    factors = [CBAM_FACTOR[y] for y in HORIZON]
    assert factors == sorted(factors, reverse=True), factors
    assert CBAM_FACTOR[2026] == 0.975 and CBAM_FACTOR[2034] == 0.000
    # العلاوة: الأسمدة 1% في الأفق كلّه، والباقي 10/20/30 ثم ثابت
    assert {MARKUP["fertilisers"][y] for y in HORIZON} == {0.01}
    assert MARKUP["cement"][2026] == 0.10 and MARKUP["cement"][2028] == 0.30
    assert MARKUP["cement"][2034] == 0.30
    # الإغلاق: الملفُّ الرسميّ يحوي صفوفاً لا تُغلق — وهذا **قياس** لا تحقّقُ صحةِ نقل.
    # أيُّ تغييرٍ في العدد يُسقط الحارس ⇒ يُقرأ تحريفاً في الدبوس حتى يُثبت العكس.
    # الجدولُ المغلق: 43 رمزاً قابلاً للترتيب من 69، وأربعةُ أصنافِ غيابٍ منطوقة
    inventory = pinned_codes()
    assert sum(1 for v in inventory.values() if v["rankable"]) == 43, inventory
    assert benchmark_resolution("7203")["resolution"] == "PREFIX_VALUE_IDENTICAL"
    assert benchmark_resolution("7205")["resolved"] == "72051000"
    assert benchmark_resolution("7601")["resolved"] is None

    audit = closure_audit()
    assert audit["rows_open"] == 10, audit["rows_open"]
    open_cns = {
        cn for cn in ALGERIA_DEFAULTS if (gap := ALGERIA_DEFAULTS[cn].closure_gap) is not None
        and abs(gap) >= 5e-4
    }
    assert open_cns == {
        "2523100010",
        "25232900",
        "2523900010",
        "28142000",
        "31021015",
        "31021019",
        "31022900",
        "31028000",
        "31052090",
        "31054000",
    }
    assert audit["max_abs_gap_t"] == 0.010
    assert audit["all_gaps_are_rounding_scale"] is True


#: انبعاثاتٌ فعليةٌ **مرشَّحة** — درجة [A] افتراض، ⛔ لا قياس. معلَنةٌ هنا لأنها
#: المُدخَل الوحيد في الدفعة كلِّها الذي ليس من مصدرٍ أوّليّ؛ وكلُّ نتيجةٍ تعتمد
#: عليها موسومةٌ `ASSUMED_SEE`. العتباتُ (`crossover_see`) و`unconditional_year`
#: ⛔ لا تستعملها إطلاقاً — ولهذا هي المُنتَج.
CANDIDATE_SEE: Final = {
    "25232900": 0.850,   # إسمنت بورتلاندي رماديّ
    "31021019": 0.800,   # يوريا >45% N (مسار غازيّ SMR)
    "31023090": 1.200,   # نترات الأمونيوم
    "72071114": 2.000,   # بلاطة صلب كربونيّ، المسار المُدبَّس (C)
}


def _year_or_none(payload: dict[str, object]) -> int | None:
    """سنةٌ أو `None` — ⛔ لا `int(object)` ولا `cast` صامت."""
    value = payload["unconditional_year"]
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int):
        raise PinError(f"unconditional_year: expected int|None, got {type(value).__name__}")
    return value


def measure_all() -> dict[str, object]:
    """الحمولةُ الكاملة: أصفارٌ مُعلَنة + مُدخَلات + بصمة + نتائج — حتميةٌ تماماً."""
    self_check()
    inventory: dict[str, dict[str, object]] = pinned_codes()
    rankable: list[str] = sorted(cn for cn, info in inventory.items() if info["rankable"])
    headline: list[dict[str, object]] = [
        {
            "cn": cn,
            "sector": ALGERIA_DEFAULTS[cn].sector,
            "description": ALGERIA_DEFAULTS[cn].description,
            "years": {
                str(year): {
                    "default_eur_per_t": certificates_default(cn, year)["eur_per_t"],
                    "toll_eur_per_t": path_toll(cn, year)["toll_eur_per_t"],
                    "relief_eur_per_t": markup_relief(cn, year)["relief_eur_per_t"],
                    "required_reduction_t": net_required_reduction(cn, year)["required_reduction_t"],
                    "crossover_see_t": crossover_see(cn, year)["crossover_see_t"],
                }
                for year in HORIZON
            },
        }
        for cn in rankable
    ]
    reversals: list[dict[str, object]] = []
    impossible: list[dict[str, object]] = []
    for cn, see in sorted(CANDIDATE_SEE.items()):
        over = overstatement(cn, 2026, see)
        reversals.append(
            {
                "cn": cn,
                "sector": ALGERIA_DEFAULTS[cn].sector,
                "description": ALGERIA_DEFAULTS[cn].description,
                "see_actual_t": see,
                "see_status": "ASSUMED_SEE (grade [A], not a measurement)",
                "overstatement_2026": over,
                "first_sellable_year": first_sellable_year(cn, see)["first_sellable_year"],
                "unconditional_year": unconditional_year(cn)["unconditional_year"],
            }
        )
        if _flag(over, "naive_exceeds_ceiling"):
            impossible.append(
                {
                    "cn": cn,
                    "see_actual_t": see,
                    "see_status": "ASSUMED_SEE (grade [A], not a measurement)",
                    "naive_gap_eur_per_t": over["naive_gap_eur_per_t"],
                    "ceiling_eur_per_t": over["ceiling_eur_per_t"],
                    "ceiling_excess_eur_per_t": over["ceiling_excess_eur_per_t"],
                    "impossible_without_any_plant_data": True,
                }
            )
    identities: list[dict[str, object]] = [
        error_identity(cn, 2026) for cn in ("25232900", "31021019", "31023090", "72071114")
    ]
    identity_holds: bool = all(
        _flag(error_identity(cn, year), "regime_above_column_a_error_is_constant")
        for cn in rankable
        for year in (2026, 2030, 2034)
    )
    unconditional_years: dict[str, int | None] = {
        cn: _year_or_none(unconditional_year(cn)) for cn in rankable
    }
    return {
        "$schema_version": "1",
        "as_of": AS_OF,
        "batch": BATCH,
        "declared_zeros": {
            "installations_measured": 0,
            "verified_actual_emissions_obtained": 0,
            "aluminium_benchmarks_extracted": 0,
            "cn7208_column_a_extracted": 0,
            "official_annex_text_extracted": 0,
            "client_measurements": 0,
            "offers_sent": 0,
            "invoices_issued": 0,
            "contracts_signed": 0,
            "revenue_claim": "NONE",
        },
        "inputs": _inputs(),
        "inputs_fingerprint": inputs_fingerprint(),
        "results": {
            "mechanism": {
                "formula_ar": (
                    "NC = SEE × (1 + mark-up) − f × CSCF × BM — وf يهبط من 0.975 إلى 0"
                ),
                "cbam_factor_2026": CBAM_FACTOR[2026],
                "cbam_factor_is_a_multiplier_on": "BENCHMARK",
                "withdrawn_reading": "net = gross x (1 - free_allocation_remaining)",
                "anchors": ["S3", "S4", "S5"],
            },
            "pin_inventory": inventory,
            "closure_audit": closure_audit(),
            "column_asymmetry": column_asymmetry(),
            "unconditional_years": unconditional_years,
            "error_identities": identities,
            "error_identity_holds_for_every_rankable_code": identity_holds,
            "naive_impossible_cases": impossible,
            "decision_reversals": reversals,
            "rankable_codes": rankable,
            "rankable_count": len(rankable),
            "unrankable_count": len(ALGERIA_DEFAULTS) - len(rankable),
            "headline": headline,
            "kill_switches": kill_switches(),
            "quotability": {
                "QUOTABLE": [
                    "default_total_values_for_pinned_algerian_cn_codes",
                    "column_a_and_column_b_benchmarks_for_pinned_cn_codes",
                    "markup_schedule_and_its_application_to_the_total_column",
                    "cbam_factor_direction_and_values",
                    "path_toll_and_crossover_see_for_pinned_codes",
                    "non_closure_of_the_three_published_columns (10 of 34 rows)",
                ],
                "CONDITIONAL": [
                    "every_euro_figure (depends on CSCF, grade ب - S8)",
                    "formula_operation_order (depends on S4, grade ب)",
                ],
                "NOT_FOUND": [
                    "aluminium_benchmarks_columns_a_and_b",
                    "cn_7208_column_a_benchmark",
                    "certificate_price_2026Q3_and_2026Q4",
                    "any_algerian_installation_actual_emissions",
                    "the_other_countries_and_territories_fallback_rows",
                    "a_route_indicator_for_cn_31025000_in_the_algerian_row",
                ],
            },
        },
        "limits_ar": [
            "⛔ ليس رأياً قانونياً ولا ضريبياً — صيغةٌ محسوبةٌ مقابل مراجعَ مُسندة.",
            "⛔ لا انبعاثَ فعليّاً لأيّ منشأة: العتباتُ مُدبَّسة والأرقامُ الفعلية مُدخَلاتُ المشتري.",
            "⛔ لا رقمَ إيرادٍ ولا تسعير؛ `revenue_claim = NONE`.",
            "⛔ لا خطَّ عرضٍ ثامن — الكتالوج يبقى سبعة؛ هذه الدفعة تقيس ما يجوز أن يدخل عرضاً.",
            "⛔ الألومنيوم و`Other countries` غيرُ مستخرَجَين: غائبٌ `None` لا صفر.",
            "⛔ كلُّ رقمٍ باليورو مشروطٌ بـ CSCF من الدرجة ب (S8) — والحساسية محسوبة.",
            "⛔ `CANDIDATE_SEE` افتراضٌ من الدرجة [A] لا قياس: لا يُقتبَس كانبعاثِ منشأة، "
            "والعتباتُ و`unconditional_year` لا تستعمله إطلاقاً.",
        ],
    }


if __name__ == "__main__":  # pragma: no cover - واجهةُ قراءة، لا منطق
    #: ⛔ لا يُحفَر في `dict[str, object]`: تُستدعى الواجهةُ العامّة نفسها، فيبقى
    #: المسارُ مُعنوَناً ولا يصير الطبعُ مصدراً ثانياً للحقيقة.
    inventory = pinned_codes()
    rankable = sorted(cn for cn, info in inventory.items() if info["rankable"])
    print(f"{BATCH} · {AS_OF} · بصمة {inputs_fingerprint()[:16]}")
    print(f"رموزٌ قابلةٌ للترتيب: {len(rankable)} من {len(ALGERIA_DEFAULTS)}")
    for cn in rankable:
        default = certificates_default(cn, 2026)
        toll = path_toll(cn, 2026)
        cross = crossover_see(cn, 2026)
        unconditional = unconditional_year(cn)["unconditional_year"]
        print(
            f"  {cn:<12}{ALGERIA_DEFAULTS[cn].sector:<12}"
            f"افتراضيّ {_f(default, 'eur_per_t'):>8.2f} €/t · "
            f"رسمُ المسار {_f(toll, 'toll_eur_per_t'):>7.2f} €/t · "
            f"العتبة {_f(cross, 'crossover_see_t'):>7.4f} t/t · "
            f"غيرُ مشروطٍ من {unconditional}"
        )
