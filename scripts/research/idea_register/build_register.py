"""Build the idea register (JSON) and its Arabic reading view (Markdown) from the archives + curated screening data.

Run from the repository root:  python3 -I scripts/research/idea_register/build_register.py
Writes docs/archive/commercial/IDEA_REGISTER.json and docs/archive/commercial/IDEA_REGISTER_AR.md.
"""

from __future__ import annotations

import collections
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import audit_a1 as a1

REPO = Path(__file__).resolve().parents[3]
ARCH = REPO / "docs/archive/commercial"
VC = json.loads((REPO / "docs/commercial/VALUE_CHAIN.json").read_text(encoding="utf-8"))
REVIEWED = "2026-10-26"  # last full pass over every record
REVIEWED_ON = "2026-10-28"  # date of this register edition
# Records touched after the full pass carry their own review date.
LAST_REVIEWED = dict.fromkeys(
    (
        "B01",
        "B20",
        "B23",
        "B36",
        "B37",
        "B46",
        "B49",
        "B50",
        "B51",
        "B52",
        "B53",
        "B54",
        "B55",
        "J13",
        "J14",
    ),
    "2026-10-27",
)
LAST_REVIEWED.update(
    dict.fromkeys(
        ("B03", "B53", "B56", "B57", "B58", "B59", "B60", "B61", "B62", "B63", "B64", "B65"),
        "2026-10-28",
    )
)

# ---------------------------------------------------------------- vocabularies
VOCAB = {
    "kind": {"idea": "فكرة", "job": "وظيفة أو مهمّة", "value_chain_path": "مسار في سلسلة القيمة"},
    "stage": {
        "included": "متأهّلة — اجتازت البوّابات الخمس",
        "conditional": "مشروطة — شرطٌ واحد معلوم يفتحها",
        "excluded": "مستبعدة — بوّابةٌ مسمّاة وسببٌ مكتوب",
        "personal_income": "دخلٌ فردي — خارج غربال الشركة",
        "governed_elsewhere": "حالتها في سلسلة القيمة لا هنا",
    },
    "option_state": {
        "active_test": "اختبار مشترٍ جاهز للإرسال",
        "awaiting_owner": "ينتظر قرار المالك",
        "held_option": "خيارٌ محفوظ بشرط إعادة فتح",
        "parked": "مركونة — لا مُحرِّك قريب",
        "closed_by_fact": "أغلقتها واقعةٌ خارجية",
        "frozen": "مجمّدة بقرارٍ قائم",
        "see_value_chain": "تُدار في سلسلة القيمة",
    },
    "evidence_level": {
        "D0": "ادّعاء بلا مصدر خارجي",
        "D1": "مصدر خارجي يثبت المشكلة أو سعر بائع، بلا مشترٍ ملزم",
        "D2": "مشترٍ مسمّى (فئةً أو جهة) + التزام قانوني أو ميزانية منشورة",
        "D3": "محادثة موثّقة مع مشترٍ",
        "D4": "عرض موقّع أو عيّنة مسلّمة أو عربون",
        "D5": "دفعة مسوّاة في كشف بنكي",
        "na": "لا ينطبق",
    },
    "gate_verdict": {"pass": "✓", "partial": "~", "fail": "✗", "na": "—"},
    "domain": {
        "development_finance": "التمويل التنموي والمناقصات الدولية",
        "einvoicing": "الفوترة الإلكترونية وبيانات الضريبة",
        "ai_assurance": "اختبار الذكاء الاصطناعي وضمانه",
        "accessibility": "الإتاحة الرقمية",
        "climate": "الامتثال المناخي والبيئي",
        "industry": "التشغيل الصناعي والصيانة",
        "trade_dz": "التجارة والمدفوعات عبر الجزائر",
        "education": "التعليم",
        "health": "الصحّة والدواء",
        "legal_hr": "القانون والعمل والأجور",
        "public_services": "الخدمات العامة والجالية",
        "infrastructure": "البنية التحتية والمياه",
        "cybersecurity": "الأمن السيبراني",
        "language_data": "بيانات اللغة",
        "channel": "قنوات البيع",
        "finance_reg": "التنظيم المالي",
        "translation": "الترجمة والتكييف اللغوي",
        "tourism": "السياحة والنقل عبر الحدود",
    },
    "currency": {
        "EUR": "يورو",
        "USD": "دولار",
        "USD_PEGGED": "عملة مربوطة بالدولار",
        "EUR_PEGGED": "عملة مربوطة باليورو (فرنك CFA)",
        "DZD": "دينار",
        "CAD": "دولار كندي",
        "TND": "دينار تونسي",
        "MIXED": "مختلطة",
        "unknown": "غير معروفة",
    },
    "delivery": {
        "remote_service": "خدمة عن بُعد",
        "remote_data": "عمل بيانات عن بُعد",
        "field": "عمل ميداني أو أجهزة",
        "software": "برمجية",
        "channel": "قناة",
        "employment": "توظيف",
    },
    "constraint": {
        "none": "لا عائق حاسم",
        "owner_decision": "قرار المالك (تجميد D-300)",
        "competence": "كفاءة تُتعلَّم ولا تُرخَّص",
        "licensed_profession": "مهنة مرخّصة",
        "gdpr_transfer": "نقل معطيات شخصية أوروبية",
        "health_data": "معطيات صحّية",
        "ethics": "مانع أخلاقي",
        "expertise": "اختصاص غير متوفّر",
        "capital_field": "رأس مال أو حضور ميداني",
        "slot_taken": "الدور أُسند لغيرنا",
        "dzd_only": "الدفع بالدينار وحده",
        "no_named_payer": "لا دافع مسمّى",
        "stale_evidence": "دليل قديم",
        "diplomatic": "مانع دبلوماسي",
        "policy_flux": "سياسة متحرّكة",
        "data_law_dz": "قانون المعطيات الجزائري 25-11",
        "verifier_pending": "شهادة جهة التحقّق",
        "frozen_by_decision": "مجمّدة بقرار",
        "channel": "قناة لا فرصة",
        "payer_unproven": "الدافع مسمّى ودفعه غير مُثبَت",
        "not_a_defect": "الإرشاد الرسمي لا يعدّه عيباً",
        "references_needed": "مراجع سابقة وأهلية غير مُتحقَّقة",
        "tax_withholding": "اقتطاعٌ ضريبي وإقامةٌ مطلوبة",
        "client_account_access": "دخولٌ إلى حساب العميل لدى الجهة الرسمية",
        "no_margin": "لا هامش عبر الطريق القانوني",
    },
}
GATES = {
    "G1": "دافعٌ بالعملة الصعبة بدليلٍ منشور",
    "G2": "جواز التسليم من الجزائر",
    "G3": "قدرة الفريق على التسليم خلال 90 يوماً",
    "G4": "ألمٌ موثَّق عمره 12 شهراً أو أقلّ",
    "G5": "عشرون مشترياً مسمّى يمكن الوصول إليهم",
}
P, M, F = "pass", "partial", "fail"


def g(*v):  # gate verdict tuple -> dict
    return dict(zip(GATES, v, strict=True))


GROUPS = {
    "F1": {
        "title_ar": "تنظيف معرّفات الفوترة الإلكترونية وبيانات العملاء (فرنسا وبلجيكا ثمّ الإمارات والسعودية)",
        "stage": "included",
        "option_state": "awaiting_owner",
        "next_test_ar": "20 رسالة لموزّعي برامج المحاسبة والمنصّات ومزوّدي Peppol، بعد قرار المالك في D-300",
        "kill_ar": "صفر ردود خلال 30 يوماً من الرسالة العشرين",
    },
    "F2": {
        "title_ar": "اختبار حواجز الذكاء الاصطناعي بالعربية والدارجة",
        "stage": "included",
        "option_state": "active_test",
        "next_test_ar": "إرسال قائمة D-320 (20 جهة) كما هي",
        "kill_ar": "صفر ردود خلال 30 يوماً من الرسالة العشرين",
    },
    "F3": {
        "title_ar": "تدقيق الإتاحة الرقمية لمواقع التجارة الفرنسية ثمّ إصلاحها",
        "stage": "included",
        "option_state": "active_test",
        "next_test_ar": "إرسال قائمة D-322 (20 استمارة) كما هي",
        "kill_ar": "صفر ردود خلال 30 يوماً من الرسالة العشرين",
    },
    "C1": {
        "title_ar": "بيانات اللغات الجزائرية",
        "stage": "conditional",
        "option_state": "held_option",
        "next_test_ar": "رأي محامٍ جزائري مكتوب في نقل التسجيلات (القانون 25-11) + سعر ساعة من شركة بيانات",
        "kill_ar": "رأيٌ يمنع النقل، أو لا سعر فوق كلفة الساعة",
    },
    "C2": {
        "title_ar": "بيانات CBAM للمصانع المصدّرة",
        "stage": "conditional",
        "option_state": "held_option",
        "next_test_ar": "صدور شهادة جهة التحقّق الأوروبية ونطاقها",
        "kill_ar": "رفض الاعتماد أو نطاقٌ لا يشمل الجزائر",
    },
    "C3": {
        "title_ar": "جاهزية الاستيراد والمدفوعات المحتجزة",
        "stage": "conditional",
        "option_state": "held_option",
        "next_test_ar": "مصدّرٌ أوروبيّ غير فرنسي يقول إنّ شحنته أو دفعته عالقة",
        "kill_ar": "صفر مصدّر مسمّى بعد 20 رسالة",
    },
    "C5": {
        "title_ar": "جاهزية Peppol في الإمارات لمزوّدي الخدمة المعتمدين",
        "stage": "conditional",
        "option_state": "held_option",
        "next_test_ar": "رسالة لـ20 مزوّداً معتمداً أو مضيفاً مسمّى بأرقامه وحده: هل تتابعون غياب قدرة الاستقبال قبل يناير؟",
        "kill_ar": "أقلّ من ردّين خلال 14 يوماً",
    },
    "C6": {
        "title_ar": "بيانات المالية العامّة في إفريقيا الفرنكوفونية",
        "stage": "conditional",
        "option_state": "held_option",
        "next_test_ar": "10 فائزين تونسيين ومغاربة بعقود البنك الدولي + 24 مُدمِجاً إيفوارياً: هل تحتاجون فريق بياناتٍ فرنكوفونياً من الباطن؟",
        "kill_ar": "لا اتفاق شراكة خلال 6 أشهر، أو أقلّ من 3 تأكيدات إيفوارية خلال 3 أسابيع",
    },
    "C7": {
        "title_ar": "تجهيز تسجيل الأجهزة الطبية في EUDAMED",
        "stage": "conditional",
        "option_state": "held_option",
        "next_test_ar": "20 ممثّلاً أوروبياً مسمّى: هل تدفعون سعراً ثابتاً لكلّ جهاز مقابل ملفّات رفعٍ جاهزة خلال 5 أيام؟",
        "kill_ar": "أقلّ من اثنين يطلبان سعراً خلال 14 يوماً",
    },
    "C4": {
        "title_ar": "أطبّاء PADHUE",
        "stage": "conditional",
        "option_state": "held_option",
        "next_test_ar": "نصّ القانون الذي يعوّض المباراة",
        "kill_ar": "نصٌّ يلغي الحاجة إلى الملفّ",
    },
    "C8": {
        "title_ar": "مكتب التحقّق من الشركات الجزائرية لبائعي المعلومات التجارية ومؤمّني الائتمان",
        "stage": "conditional",
        "option_state": "held_option",
        "next_test_ar": "20 بائع تقارير ومؤمّن ائتمان (عشرة مسمّون): من ينجز تقاريركم عن الشركات الجزائرية، وفي كم يوم، وبكم؟",
        "kill_ar": "أقلّ من 3 شركاتٍ جزائرية مرسلة للفحص التجريبي بحلول 2026-12-11",
    },
    "C9": {
        "title_ar": "الترجمة العربية-الفرنسية لمكاتب الأمم المتحدة الإقليمية",
        "stage": "conditional",
        "option_state": "held_option",
        "next_test_ar": "20 وحدة مشتريات إقليمية: هل لديكم اتفاقٌ طويل الأمد للترجمة العربية-الفرنسية، ومتى يُعاد طرحه؟",
        "kill_ar": "أقلّ من 3 تؤكّد إعادة طرحٍ قبل 2027-06 بحلول 2026-12-15",
    },
    "C10": {
        "title_ar": "إعلانات مطابقة التغليف (PPWR) وملفّاتها التقنية قبل الغرامات الألمانية في 2027-02-12",
        "stage": "conditional",
        "option_state": "held_option",
        "next_test_ar": "13 مصنّعاً فرنسياً مسمّى و11 مكتب امتثال: هل لديكم تراكم إعلاناتٍ تُعدّ أو يُعاد إصدارها، وهل تدفعون للإعلان؟",
        "kill_ar": "أقلّ من 3 من 20 يذكرون حجماً بحلول 2026-12-15",
    },
}

# ------------------------------------------------- curated screening, per idea
# id: (domain, markets, payer_currency, delivery, evidence, evidence_basis, gates|None, stage, constraint,
#      option_state, trigger, group, related)
IDEAS = {
    "B01": (
        "einvoicing",
        ["FR", "BE"],
        "EUR",
        "remote_service",
        "D2",
        "إلزامٌ قانوني في فرنسا وبلجيكا + بيانات رسمية عن الرفض؛ 4 مكاتب راسلناها بلا ردّ",
        g(P, P, P, P, P),
        "included",
        "owner_decision",
        "awaiting_owner",
        "قرار المالك في D-300",
        "F1",
        ["OPP-01", "OPP-02", "B30"],
    ),
    "B02": (
        "education",
        ["DZ"],
        "DZD",
        "software",
        "D0",
        "أصلٌ قائم بلا طلبٍ مدفوع",
        g(F, P, M, M, M),
        "excluded",
        "frozen_by_decision",
        "frozen",
        "قرار المالك برفع تجميد المنصّة (D-300)",
        None,
        ["OPP-19"],
    ),
    "B03": (
        "climate",
        ["EU", "DZ"],
        "EUR",
        "remote_service",
        "D3",
        "محادثة مع جهة تحقّق أوروبية، غير مُتحقَّق منها استقلالياً",
        g(M, P, M, M, P),
        "conditional",
        "verifier_pending",
        "held_option",
        "صدور شهادة جهة التحقّق ونطاقها",
        "C2",
        ["OPP-11"],
    ),
    "B04": (
        "industry",
        ["DZ", "EU"],
        "MIXED",
        "software",
        "D0",
        "فرضية توسّع بلا مصدر طلب",
        g(F, P, F, M, M),
        "excluded",
        "no_named_payer",
        "parked",
        "مستوردٌ أوروبي مسمّى يطلب ملفّ منتج",
        None,
        ["B03"],
    ),
    "B05": (
        "industry",
        ["DZ"],
        "DZD",
        "remote_service",
        "D0",
        "سياق سوق لا طلب",
        g(F, P, M, M, M),
        "excluded",
        "dzd_only",
        "parked",
        "مشترٍ يدفع بالعملة الصعبة",
        None,
        [],
    ),
    "B06": (
        "industry",
        ["DZ"],
        "DZD",
        "field",
        "D0",
        "فرضية بلا مصدر طلب",
        g(M, M, F, M, M),
        "excluded",
        "capital_field",
        "parked",
        "شريك عمليات + مصنع يدفع",
        None,
        [],
    ),
    "B07": (
        "industry",
        ["GLOBAL"],
        "EUR",
        "field",
        "D1",
        "حالة منشورة من بائع (Siemens)",
        g(M, M, F, M, M),
        "excluded",
        "capital_field",
        "parked",
        "شريك OEM يطلب طبقة تحليل",
        None,
        [],
    ),
    "B08": (
        "industry",
        ["DZ"],
        "MIXED",
        "field",
        "D1",
        "أمثلة بائعين",
        g(M, M, F, M, M),
        "excluded",
        "capital_field",
        "parked",
        "شريك تصنيع + طلب مسمّى",
        None,
        [],
    ),
    "B09": (
        "climate",
        ["DZ", "EU"],
        "EUR",
        "field",
        "D2",
        "اشتراطات استيراد أوروبية + برنامج Eni/Sonatrach المعلن",
        g(M, M, F, M, M),
        "excluded",
        "capital_field",
        "held_option",
        "طلب توثيق مسمّى من مشغّل تحت إشراف مختصّ",
        None,
        [],
    ),
    "B10": (
        "trade_dz",
        ["DZ", "EU"],
        "EUR",
        "remote_service",
        "D1",
        "تحذيرات رسمية + بائعون منافسون، بلا مصدّر مسمّى",
        g(M, P, M, P, M),
        "conditional",
        "no_named_payer",
        "held_option",
        "مصدّرٌ أوروبي يقول إنّ شحنته أو دفعته عالقة",
        "C3",
        ["B24"],
    ),
    "B11": (
        "ai_assurance",
        ["GLOBAL"],
        "USD",
        "remote_service",
        "D1",
        "إشارة طلب على منصّة عمل حرّ لم تُتحقَّق",
        g(M, P, F, F, M),
        "excluded",
        "stale_evidence",
        "parked",
        "طلبٌ مسمّى حديث لاختبار واجهة عربية",
        None,
        ["J09", "OPP-18"],
    ),
    "B12": (
        "ai_assurance",
        ["EU", "GLOBAL"],
        "EUR",
        "remote_service",
        "D1",
        "حالة بائع (BPCE/Giskard)",
        g(P, P, P, P, P),
        "included",
        "none",
        "active_test",
        "قائمة D-320",
        "F2",
        ["OPP-04", "OFF-CND"],
    ),
    "B13": (
        "industry",
        ["DZ"],
        "MIXED",
        "field",
        "D1",
        "منتج بائع (Sensitech)",
        g(M, M, F, M, M),
        "excluded",
        "capital_field",
        "parked",
        "ناقل بمسار شحن محدّد يطلب التدخّل",
        None,
        [],
    ),
    "B14": (
        "trade_dz",
        ["DZ", "EU"],
        "EUR",
        "field",
        "D1",
        "توثيق CBI؛ البرنامج مغلق",
        g(F, P, F, M, M),
        "excluded",
        "no_named_payer",
        "parked",
        "مستورد أوروبي مسمّى يطلب التتبّع",
        None,
        [],
    ),
    "B15": (
        "infrastructure",
        ["KE"],
        "MIXED",
        "field",
        "D2",
        "تأهيلٌ منشور (Naivasha) أُغلق في يونيو 2025",
        g(M, M, F, M, M),
        "excluded",
        "capital_field",
        "closed_by_fact",
        "مناقصة أداء جديدة مفتوحة مع مقاول شريك",
        None,
        [],
    ),
    "B16": (
        "legal_hr",
        ["GLOBAL"],
        "USD",
        "software",
        "D1",
        "حالات بائعين + صفقة استحواذ منشورة",
        g(M, P, F, F, M),
        "excluded",
        "expertise",
        "held_option",
        "خبير عقود شريك + مقاول مسمّى",
        None,
        [],
    ),
    "B17": (
        "cybersecurity",
        ["GLOBAL"],
        "USD",
        "remote_service",
        "D2",
        "إعلان شراء AfDB أُغلق في 2026-10-05",
        g(M, P, F, F, M),
        "excluded",
        "expertise",
        "closed_by_fact",
        "مناقصة مفتوحة مع شريك أمني مؤهّل",
        None,
        [],
    ),
    "B18": (
        "channel",
        ["GLOBAL"],
        "MIXED",
        "channel",
        "na",
        "قناة بيع لا فرصة",
        dict.fromkeys(GATES, "na"),
        "excluded",
        "channel",
        "held_option",
        "تُستعمل داخل أيّ متأهّل",
        None,
        [],
    ),
    "B19": (
        "language_data",
        ["DZ", "GLOBAL"],
        "USD",
        "remote_data",
        "D2",
        "شركات بيانات تنشر مهامّ مدفوعة للجزائر",
        g(P, M, P, P, M),
        "conditional",
        "data_law_dz",
        "held_option",
        "رأي محامٍ في القانون 25-11 + سعر ساعة",
        "C1",
        ["OPP-05", "J10", "J11"],
    ),
    "B20": (
        "finance_reg",
        ["FR"],
        "EUR",
        "remote_service",
        "D1",
        "سياق مهنة وأسعار منشورة + قرارا النقض الجنائي 2022-10-04 و2026-01-21 (احتكار المهنة يشمل المقاولة من الباطن والإعارة)",
        g(M, F, M, P, P),
        "excluded",
        "licensed_profession",
        "parked",
        "تعديل احتكار الأمر 45-2138، أو أن يكون الفريق أُجراء مكتبٍ مسجّل (توظيفٌ لا شركة)",
        None,
        ["OPP-17"],
    ),
    "B21": (
        "finance_reg",
        ["EU"],
        "EUR",
        "remote_service",
        "D1",
        "أرقام 2024 فقط",
        g(M, M, M, F, M),
        "excluded",
        "stale_evidence",
        "parked",
        "دليل ألم مؤرَّخ بعد 2025",
        None,
        [],
    ),
    "B22": (
        "einvoicing",
        ["AE"],
        "USD_PEGGED",
        "remote_service",
        "D2",
        "إلزامٌ إماراتي + وظيفة منشورة لصيانة بيانات العملاء",
        g(P, P, P, P, P),
        "included",
        "owner_decision",
        "awaiting_owner",
        "قرار المالك في D-300",
        "F1",
        ["B30", "J12"],
    ),
    "B23": (
        "climate",
        ["EU"],
        "EUR",
        "remote_service",
        "D1",
        "نصّ تنظيمي بلا ألم مُبلَغ",
        g(F, P, M, F, M),
        "excluded",
        "no_named_payer",
        "parked",
        "شكوى مستورد مسمّاة بعد 2026-12-30",
        None,
        [],
    ),
    "B24": (
        "trade_dz",
        ["DZ", "EU"],
        "MIXED",
        "remote_service",
        "D1",
        "نظام رسمي + أدلّة للمصدّرين",
        g(M, P, M, P, M),
        "conditional",
        "no_named_payer",
        "held_option",
        "مصدّرٌ أوروبي مسمّى",
        "C3",
        ["B10"],
    ),
    "B25": (
        "trade_dz",
        ["DZ"],
        "DZD",
        "remote_service",
        "D1",
        "نظام بنك الجزائر 26-02",
        g(F, P, M, P, M),
        "excluded",
        "dzd_only",
        "parked",
        "مصدّر يدفع بالعملة الصعبة",
        None,
        [],
    ),
    "B26": (
        "einvoicing",
        ["DZ"],
        "DZD",
        "remote_service",
        "D1",
        "إلزام جبائي جزائري",
        g(F, P, M, P, M),
        "excluded",
        "dzd_only",
        "parked",
        "دافع بالعملة الصعبة",
        None,
        [],
    ),
    "B27": (
        "trade_dz",
        ["DZ"],
        "DZD",
        "software",
        "D1",
        "مصادر بائعين",
        g(F, P, M, M, M),
        "excluded",
        "dzd_only",
        "parked",
        "دافع بالعملة الصعبة",
        None,
        [],
    ),
    "B28": (
        "education",
        ["DZ"],
        "DZD",
        "remote_service",
        "D1",
        "مصدر قديم (يناير 2025)",
        g(F, P, M, F, M),
        "excluded",
        "dzd_only",
        "parked",
        "رفع تجميد المنصّة + دافع",
        None,
        ["B02", "OPP-19"],
    ),
    "B29": (
        "trade_dz",
        ["DZ"],
        "DZD",
        "remote_service",
        "D1",
        "إجراء رسمي بأجلٍ في 31 أكتوبر",
        g(F, P, P, F, M),
        "excluded",
        "dzd_only",
        "parked",
        "دورة FSPE القادمة بدفعٍ بالعملة الصعبة",
        None,
        [],
    ),
    "B30": (
        "einvoicing",
        ["FR", "BE", "AE", "SA"],
        "MIXED",
        "remote_service",
        "D2",
        "إلزامات متتالية + شكاوى منشورة في فرنسا",
        g(P, P, P, P, P),
        "included",
        "owner_decision",
        "awaiting_owner",
        "قرار المالك في D-300",
        "F1",
        ["B01", "B22", "B31", "OPP-01", "OPP-02"],
    ),
    "B31": (
        "einvoicing",
        ["SA"],
        "USD_PEGGED",
        "remote_service",
        "D1",
        "إعلان الموجة 25؛ الدافع عند D1",
        g(P, P, P, P, P),
        "included",
        "owner_decision",
        "awaiting_owner",
        "قرار المالك في D-300",
        "F1",
        ["B30", "OPP-12"],
    ),
    "B32": (
        "einvoicing",
        ["OM"],
        "USD_PEGGED",
        "remote_service",
        "D1",
        "مرحلة رسمية بلا ألم مُبلَغ",
        g(F, P, M, F, M),
        "excluded",
        "no_named_payer",
        "parked",
        "شكوى مسمّاة من مكلّف عُماني",
        None,
        ["B30"],
    ),
    "B33": (
        "einvoicing",
        ["MA"],
        "MIXED",
        "remote_service",
        "D1",
        "إلزام قادم",
        g(M, F, P, M, M),
        "excluded",
        "diplomatic",
        "parked",
        "تغيّر العلاقات الجزائرية المغربية",
        None,
        ["B30"],
    ),
    "B34": (
        "public_services",
        ["FR", "DZ"],
        "EUR",
        "field",
        "D2",
        "ديوان المحاسبة + نيّة الصندوق المعلنة؛ الدور أُسند لمصرف",
        g(P, F, P, P, F),
        "excluded",
        "slot_taken",
        "closed_by_fact",
        "مناقصة جديدة يقبل فيها غيرُ المصارف",
        None,
        [],
    ),
    "B35": (
        "public_services",
        ["DZ", "FR"],
        "EUR",
        "remote_service",
        "D1",
        "صحافة",
        g(F, P, P, P, F),
        "excluded",
        "no_named_payer",
        "parked",
        "دافع مسمّى وسعر موجود",
        None,
        [],
    ),
    "B36": (
        "legal_hr",
        ["EU"],
        "EUR",
        "software",
        "D1",
        "توجيه أوروبي + أسعار برمجيات",
        g(M, M, M, P, M),
        "excluded",
        "no_named_payer",
        "parked",
        "شكوى مسمّاة من شركةٍ متعدّدة الجنسيات + الشروط الأربعة لـG2 (بنود نموذجية، وتقييم أثر النقل، ورأي محامٍ جزائري، ولا فئات خاصّة)",
        None,
        [],
    ),
    "B37": (
        "health",
        ["FR"],
        "EUR",
        "remote_service",
        "D1",
        "نقص موثّق غير مؤرَّخ",
        g(P, F, F, M, M),
        "excluded",
        "health_data",
        "parked",
        "إطار قانوني يسمح بالترميز من الخارج",
        None,
        [],
    ),
    "B38": (
        "health",
        ["FR"],
        "EUR",
        "remote_service",
        "D1",
        "محامون وجمعيات؛ سياسة متحرّكة",
        g(M, P, M, P, M),
        "conditional",
        "policy_flux",
        "held_option",
        "نصّ القانون الذي يعوّض المباراة",
        "C4",
        [],
    ),
    "B39": (
        "health",
        ["CA", "EU", "DZ"],
        "CAD",
        "employment",
        "D2",
        "برامج توظيف مدفوعة؛ كيبك أغلقت إفريقيا",
        g(P, F, M, F, M),
        "excluded",
        "ethics",
        "closed_by_fact",
        "لا يُعاد فتحه بلا مراجعة أخلاقية مكتوبة",
        None,
        [],
    ),
    "B40": (
        "legal_hr",
        ["US"],
        "USD",
        "remote_service",
        "D1",
        "قرارات قضائية منشورة",
        g(P, P, F, P, F),
        "excluded",
        "expertise",
        "parked",
        "شريك قانوني أمريكي",
        None,
        [],
    ),
    "B41": (
        "infrastructure",
        ["FR"],
        "EUR",
        "field",
        "D1",
        "منع تأجير متدرّج",
        g(P, P, F, P, M),
        "excluded",
        "capital_field",
        "parked",
        "شريك ميداني في فرنسا",
        None,
        [],
    ),
    "B42": (
        "health",
        ["DZ"],
        "MIXED",
        "remote_service",
        "D2",
        "مرسوم جزائري يُلزم الممثّل المحلّي للمموّل الأجنبي",
        g(P, M, F, P, M),
        "excluded",
        "expertise",
        "held_option",
        "شريك مؤهّل في GCP",
        None,
        ["B43"],
    ),
    "B44": (
        "einvoicing",
        ["BE", "FR"],
        "EUR",
        "remote_service",
        "D1",
        "قياسٌ أصلي (§13): نحو 175,800 شركة بلجيكية بلا رقم الضريبة، لكنّ الإرشاد الرسمي يجعله اختيارياً",
        g(F, M, P, F, P),
        "excluded",
        "not_a_defect",
        "parked",
        "دليلٌ مؤرَّخ على ارتداد فواتير مرسلة إلى رقم الضريبة + مزوّدٌ يقول إنه سيدفع",
        None,
        ["OPP-02", "B30", "B45"],
    ),
    "B45": (
        "einvoicing",
        ["AE"],
        "USD_PEGGED",
        "remote_service",
        "D2",
        "إحصاءٌ كامل (§14): 1,119 معرّفاً إماراتياً عند أربعة مزوّدين بلا قدرة الاستقبال الإماراتية قبل إطلاق 2027-01-01؛ ثلاثة منهم معتمدون",
        g(M, M, P, P, P),
        "conditional",
        "payer_unproven",
        "held_option",
        "إعادة القياس في 2027-01-05: إن بقيت المعرّفات بلا قدرة الاستقبال بعد الإطلاق صار العيب مكلفاً ومؤرَّخاً",
        "C5",
        ["B22", "B44", "B30"],
    ),
    "B46": (
        "development_finance",
        ["NE", "SN", "CI", "CG", "BI"],
        "EUR_PEGGED",
        "remote_service",
        "D2",
        "عقود البنك الدولي المُرساة: تونس 95 ومغرب 30 والجزائر 3 منذ 2024؛ النيجر 110.67 مليون فرنك",
        g(P, M, M, P, P),
        "conditional",
        "references_needed",
        "held_option",
        "فائزان تونسيان أو مغربيان يؤكّدان المقاولة من الباطن بمهمّةٍ قادمة مسمّاة بحلول 2026-11-30",
        "C6",
        ["B47", "B01"],
    ),
    "B47": (
        "einvoicing",
        ["CI"],
        "EUR_PEGGED",
        "remote_service",
        "D2",
        "قرار الضرائب الإيفواري 2026-09-14 بمهلة 45 يوماً + 24 مُدمِجاً مسمّى",
        g(M, M, P, P, P),
        "conditional",
        "tax_withholding",
        "held_option",
        "3 مُدمِجين يؤكّدون رفض تدفّقات عملائهم ويقبلون الدفع من الخارج",
        "C6",
        ["B46", "B30"],
    ),
    "B48": (
        "health",
        ["EU"],
        "EUR",
        "remote_service",
        "D2",
        "44.5% من مصنّعي الأجهزة الطبية النشطين بلا جهازٍ في EUDAMED قبل 2026-11-28 + ممثّلون مسمّون + أسعار بائعين",
        g(P, M, M, P, P),
        "conditional",
        "client_account_access",
        "held_option",
        "تأكيد أنّ واجهة EUDAMED تُظهر الأجهزة القديمة، ثمّ ممثّلان أوروبيان يطلبان سعراً لتنظيف التسجيل المتأخّر",
        "C7",
        [],
    ),
    "B43": (
        "health",
        ["DZ"],
        "MIXED",
        "remote_service",
        "D2",
        "شروط ANPP الجديدة",
        g(M, P, F, P, M),
        "excluded",
        "expertise",
        "held_option",
        "شريك مختصّ في الوبائيات",
        None,
        ["B42"],
    ),
    "B49": (
        "trade_dz",
        ["DZ", "ES", "IT", "GB", "EU"],
        "MIXED",
        "remote_service",
        "D1",
        "قياسٌ أصلي (§16، Comext): صادرات فرنسا إلى الجزائر −26% وإسبانيا +222% (يناير–أغسطس 2026 مقابل 2024) + تقرير جزائري يُباع بـ100–188 جنيهاً + يوما غرفة فالنسيا",
        g(M, M, P, P, M),
        "conditional",
        "payer_unproven",
        "held_option",
        "3 شركاتٍ جزائرية يرسلها بائعو التقارير أو المؤمّنون للفحص التجريبي بحلول 2026-12-11",
        "C8",
        ["B10", "B24"],
    ),
    "B50": (
        "translation",
        ["SA", "LB", "GLOBAL"],
        "USD",
        "remote_service",
        "D2",
        "قياسٌ أصلي (§16، UNGM): الجزائر 0 عقد مقابل تونس 228 والأردن 159 منذ 2024 + أربعة إعلانات ترجمة مفتوحة بمواعيد",
        g(M, P, M, P, P),
        "conditional",
        "references_needed",
        "held_option",
        "3 وحدات مشتريات تؤكّد إعادة طرح اتفاقٍ طويل الأمد قبل 2027-06 بحلول 2026-12-15",
        "C9",
        ["B46"],
    ),
    "B51": (
        "translation",
        ["CA"],
        "CAD",
        "remote_service",
        "D1",
        "قياسٌ أصلي (§16): 41.5% من 106 متاجر .ca بلا فرنسية و43 من 44 خارج كيبك + 11,125 شكوى في 2025-26",
        g(M, P, M, P, M),
        "conditional",
        "competence",
        "held_option",
        "وكالتان كنديتان تقبلان اختبار تحريرٍ بفرنسية كيبك بحلول 2026-12-15",
        None,
        ["B50"],
    ),
    "B52": (
        "climate",
        ["FR", "DE", "EU"],
        "EUR",
        "remote_service",
        "D2",
        "التزام PPWR منذ 2026-08-12 + كلّ إعلانات الشهر الأول أُعيدت (Packaging Europe 2026-09-24) + غرامات ألمانية من 2027-02-12 + قياسٌ أصلي: 1,072 مصنّع تغليف فرنسي بعشرة موظفين فأكثر",
        g(M, P, M, P, P),
        "conditional",
        "payer_unproven",
        "held_option",
        "3 من 20 مصنّعاً أو مكتب امتثال يذكرون حجم تراكمٍ ويقبلون سعراً للإعلان بحلول 2026-12-15",
        "C10",
        ["B23", "B03", "B48"],
    ),
    "B53": (
        "trade_dz",
        ["DZ", "TN"],
        "TND",
        "field",
        "D1",
        "قياسٌ أصلي (§19): 22 طرازاً وسعة، الفارق بالسعر الرسمي بين −26% و+13% والوسيط نحو −1%، وكلّ طرازٍ يخسر 36–98% بعد الرسوم القانونية وهامش البائع؛ و«الربح» يظهر بسعر الصرف الموازي وحده، وهو غير قانوني",
        g(F, M, M, F, F),
        "excluded",
        "no_margin",
        "closed_by_fact",
        "فارقٌ موجب يتجاوز 25% بالسعر الرسمي بعد الشحن والرسوم وهامش البائع لشهرين متتاليين، عبر تصديرٍ مسجّل يُدفع بالعملة الصعبة",
        None,
        ["B49"],
    ),
    "B54": (
        "development_finance",
        ["DZ"],
        "EUR",
        "remote_service",
        "D2",
        "إعلانان مسبقان لمندوبية الاتحاد في الجزائر (2026-09-16 و2026-10-27) + المادة 28 من NDICI + قياسٌ أصلي (FTS 2023–2025): الجهات المقيمة في الجزائر نالت 1% من 58.23 مليون € فائدتها كلّها للجزائر، ولا شركة جزائرية بين 63 قائداً لعقود الاستشارة",
        g(M, P, M, P, M),
        "conditional",
        "references_needed",
        "held_option",
        "شركتان قائدتان تقبلان شريكاً جزائرياً في عرض EU-Algeria 4 Business أو MASSALEK قبل نشر الإعلان الكامل",
        None,
        ["B46", "B49"],
    ),
    "B55": (
        "trade_dz",
        ["DZ", "FR", "BE"],
        "EUR",
        "field",
        "D1",
        "قانون المالية 2023 المادة 66 (تخفيض 50% للبنزين حتى 1800 سم³ و80% للكهربائية) + المرسوم 23-74 + منع البيع 36 شهراً؛ كلفة Sandero أو Picanto من 2024 نحو 2.4–2.7 مليون دينار مكافئ منها 13,000–13,500 € عملةٌ صعبة مشروعة؛ لا مشترٍ مسمّى",
        g(M, M, M, M, F),
        "excluded",
        "no_named_payer",
        "parked",
        "20 عائلة مسمّاة أو وكيلٌ جمركي جزائري مرخّص يطلب شريك بحثٍ في أوروبا يُدفع له باليورو بحلول 2027-01-31",
        None,
        ["B53", "B49"],
    ),
    "B56": (
        "education",
        ["DZ"],
        "DZD",
        "remote_service",
        "D1",
        "876,000 مترشّح للبكالوريا 2026 و1,232 بتقدير ممتاز (TSA 2026-07-12)؛ منصّات مدفوعة بـ500–1,200 دينار وتطبيقٌ مجاني بالذكاء الاصطناعي؛ 20 جهةً مسمّاة قُرئت قنوات 10 منها",
        g(F, M, M, M, M),
        "excluded",
        "dzd_only",
        "awaiting_owner",
        "قرار المالك بفتح مسار الدينار لإثبات الجرّ أمام ASF، ثمّ 50 تسجيلاً مسبقاً بلا دفع خلال 21 يوماً بعد بطاقة ANAE",
        None,
        ["B02"],
    ),
    "B57": (
        "industry",
        ["DZ"],
        "DZD",
        "software",
        "D1",
        "قياسٌ أصلي (§21): 152 مناقصة عجلات من 123 جهة عمومية بين 2025-10 و2026-08، من 11 شهرياً إلى 25؛ ولا مناقصة تطلب برنامجاً",
        g(F, M, M, P, M),
        "excluded",
        "dzd_only",
        "awaiting_owner",
        "قرار المالك بمسار الدينار، ثمّ جهتان من 20 أسطولاً مسمّى تقبلان سعراً لكلّ مركبة في السنة",
        None,
        ["B55"],
    ),
    "B58": (
        "trade_dz",
        ["DZ"],
        "DZD",
        "remote_service",
        "D1",
        "مجلس المحاسبة: 3% فقط من اعتمادات صندوق دعم الصادرات لسنة 2020 استُعملت (نقلاً عن الوكيل)؛ 25 مصدّراً مسمّى؛ المصدّر لا يدفع لمقيمٍ بالعملة الصعبة (التعليمة 06-2021 المادة 7.2)",
        g(F, M, M, M, M),
        "excluded",
        "dzd_only",
        "awaiting_owner",
        "قرار المالك بمسار الدينار، ثمّ 3 ردود من 20 مصدّراً على سؤال: أيّ بندٍ من الصندوق لم تطالبوا به ولماذا؟",
        None,
        ["B59", "B49"],
    ),
    "B59": (
        "trade_dz",
        ["DZ", "FR", "EU"],
        "EUR",
        "remote_service",
        "D1",
        "صادرات الجزائر غير الطاقوية إلى الاتحاد الأوروبي 1,843.7 مليون € في 2025 مقابل 12,986.5 لتونس (Comext، مُعاد حسابه)؛ تصدير الخدمة لغير مقيم يُحتفظ بعائده كاملاً (التعليمة 06-2021 المادة 4)؛ لا مشترٍ أجنبي مسمّى",
        g(M, P, M, F, F),
        "excluded",
        "no_named_payer",
        "held_option",
        "قائمة 20 مستورداً فرنسياً للأغذية أو المواد الجزائرية بقنواتٍ عامّة، ويقول اثنان منهم نعم لوكيل مصادر يُدفع له باليورو",
        None,
        ["B58", "B49", "B03"],
    ),
    "B60": (
        "public_services",
        ["DZ"],
        "DZD",
        "remote_service",
        "D1",
        "القانون 23-12 المادة 58: حجزٌ إلزامي للمؤسسات الناشئة الحاملة للعلامة حتى 20% من الطلب العمومي؛ 25 جهةً عمومية مسمّاة؛ ولا مناقصة رقمية حيّة في الولايات الخمس",
        g(F, M, M, M, M),
        "excluded",
        "dzd_only",
        "awaiting_owner",
        "قرار المالك بمسار الدينار وبتأسيس شركةٍ تحمل العلامة، ثمّ 3 استشاراتٍ في نطاقنا بميزانيةٍ معلنة خلال 60 يوماً",
        None,
        ["B56"],
    ),
    "B61": (
        "tourism",
        ["DZ", "TN"],
        "DZD",
        "field",
        "D1",
        "حافلة تونس–عنابة منذ 2026-03-13 والقطار منذ 2026-10-21، و2,660,358 مسافراً عبر ملّولة في 2025؛ لا نظام وكلاء معروف",
        g(F, M, M, M, F),
        "excluded",
        "dzd_only",
        "parked",
        "مشغّلٌ يعلن نظام وكلاء في الطارف بعمولةٍ لا تقلّ عن 5%",
        None,
        ["B64"],
    ),
    "B62": (
        "finance_reg",
        ["DZ"],
        "DZD",
        "field",
        "D1",
        "النظام 23-01 (رأسمال 1–5 ملايين دينار)؛ وزير المالية: «لم نتلقَّ أيّ طلب» والأورو 260 في السوق مقابل 150 رسمياً؛ منحة السياحة بالبطاقة وحدها منذ 2026-07-19",
        g(F, M, M, M, F),
        "excluded",
        "no_named_payer",
        "closed_by_fact",
        "انحسار الفارق بين السعرين الرسمي والموازي إلى أقلّ من 10% لثلاثة أشهر متتالية",
        None,
        ["B53"],
    ),
    "B63": (
        "industry",
        ["DZ", "FR", "EU"],
        "EUR",
        "channel",
        "D0",
        "مصانع العجلات الجديدة وIris ضاعف طاقته؛ لكنّ التصدير في عزّ النقص المحلّي هشٌّ سياسياً، ولـIris شريكٌ إسباني بحسب الوكيل",
        g(M, M, F, M, F),
        "excluded",
        "policy_flux",
        "parked",
        "انتهاء النقص المحلّي المعلن رسمياً بعد تشغيل المصانع الأربعة في 2027، ومصنّعٌ يطلب وكيلاً أوروبياً",
        None,
        ["B57"],
    ),
    "B64": (
        "tourism",
        ["DZ", "TN"],
        "DZD",
        "field",
        "D1",
        "نحو 60 وكالة جزائرية استكشفت طبرقة في ربيع 2026؛ والوكالات مذكورة في حملة 2026 على تحويل منحة السياحة",
        g(F, M, M, M, F),
        "excluded",
        "dzd_only",
        "parked",
        "قرار المالك بمسار الدينار وقراءة رخصة الوكالة وضمانها",
        None,
        ["B61"],
    ),
    "B65": (
        "tourism",
        ["DZ", "TN", "EU"],
        "EUR",
        "field",
        "D0",
        "لا دليل على طلبٍ سياحي وافد إلى حظيرة القالة أو عنابة؛ قواعد التأشيرة والرخصة لم تُقرأ",
        g(F, M, M, F, F),
        "excluded",
        "no_named_payer",
        "parked",
        "منظّم رحلاتٍ تونسي أو أوروبي مسمّى يطلب خدماتٍ ميدانية في الطارف ويدفع باليورو",
        None,
        ["B61"],
    ),
}

JOB_CCY = {
    "J01": "USD",
    "J02": "USD",
    "J03": "unknown",
    "J04": "USD",
    "J05": "USD",
    "J06": "unknown",
    "J07": "unknown",
    "J08": "unknown",
    "J09": "USD",
    "J10": "unknown",
    "J11": "unknown",
    "J12": "USD_PEGGED",
    "J13": "USD",
    "J14": "unknown",
}
JOB_REL = {
    "J01": ["OPP-03"],
    "J03": ["OPP-03", "B19"],
    "J09": ["B11"],
    "J10": ["B19"],
    "J11": ["B19"],
    "J12": ["B22"],
    "J13": ["B46"],
    "J14": ["B50"],
}

PATH_GROUP = {"OPP-01": "F1", "OPP-02": "F1", "OPP-04": "F2", "OPP-13": "F3"}
PATH_REL = {
    "OPP-01": ["B01", "B30"],
    "OPP-02": ["B01", "B30"],
    "OPP-04": ["B12"],
    "OPP-05": ["B19"],
    "OPP-11": ["B03"],
    "OPP-12": ["B31"],
    "OPP-18": ["B11"],
    "OPP-19": ["B02"],
    "OPP-03": ["J01", "J03"],
    "OPP-17": ["B20"],
    "OFF-CND": ["OPP-04", "B12"],
}
# Only OPP-04 and OPP-13 were screened as candidates in S02; OPP-01/02 join F1 by membership, not by a separate screen.
PATH_GATES = {"OPP-04": g(P, P, P, P, P), "OPP-13": g(P, P, M, P, P)}

STUDIES = [
    {
        "id": "S11",
        "date": "2026-10-28",
        "title_ar": "الموجة السادسة: كيف نستفيد نحن من مشاكل الجزائر",
        "where": "OPPORTUNITIES_PAIN_RESEARCH_2026-10-26_AR.md §21",
        "feeds": [
            "B56",
            "B57",
            "B58",
            "B59",
            "B60",
            "B61",
            "B62",
            "B63",
            "B64",
            "B65",
            "B03",
            "B53",
        ],
        "finding_ar": "لا طريق قانونياً إلى العملة الصعبة داخل هذه المشاكل خلال 90 يوماً: كلّ دافعٍ وُجد يدفع بالدينار؛ رصيد الخزينة −91.7% والاحتياطي 68.9→51.0 مليار $؛ المادة 58 تحجز الصفقات للمؤسسات الناشئة؛ المصدّر لا يدفع لمقيمٍ بالعملة الصعبة؛ 152 مناقصة عجلات من 123 جهة؛ ومكاتب الصرف بلا طلبٍ واحد",
    },
    {
        "id": "S10",
        "date": "2026-10-27",
        "title_ar": "الموجة الخامسة: لماذا يكسب الجيران العملة الصعبة أكثر، والتحويلات، والسيارات",
        "where": "OPPORTUNITIES_PAIN_RESEARCH_2026-10-26_AR.md §20",
        "feeds": ["B53", "B55", "B46", "B54"],
        "finding_ar": "صادرات خدمات المعلوماتية 2025: المغرب 2,804.5 مليون $ ومصر 2,061.4 وتونس 526.5 والجزائر 77.6 وحدها تتراجع؛ الاحتفاظ بعائد التصدير 100% في الجزائر منذ 2021 فليس هو العائق، والفارق حرّية رأس المال التونسية والمستثمرون؛ التحويلات الرسمية 2025: الجزائر 1.69 مليار $ (0.6% من الناتج) بأكبر جاليةٍ في فرنسا، ومصر صعدت من 19.53 إلى 41.52 بعد توحيد السعر؛ ما في D-323 عن Stripe صحيح والوكيل أخطأ",
    },
    {
        "id": "S09",
        "date": "2026-10-27",
        "title_ar": "أسطول الوكلاء، الموجة الرابعة: العالم كلّه بعد تونس، والهواتف، والمموّلون الآخرون",
        "where": "OPPORTUNITIES_PAIN_RESEARCH_2026-10-26_AR.md §19",
        "feeds": ["B46", "B49", "B50", "B53", "B54", "J13", "J14"],
        "finding_ar": "في 99,967 إشعاراً للبنك الدولي تفوز تونس 520 مرّة (282 خارجها) والجزائر 6 (صفر داخلها، لأنها لا تقترض: صفر ترسية في كلّ تاريخ الواجهة)؛ الهواتف بلا هامشٍ قانوني في 22 طرازاً؛ البنك الإفريقي بيانات محجوبة وعقدا بيانات من 100؛ الاتحاد الأوروبي يفتح المشاركة للجزائريين وهم 1% من 58.23 مليون €؛ والأمم المتحدة تشتري من الجزائر 23.2 مليون $ مقابل 91.3 لتونس في 2025",
    },
    {
        "id": "S01",
        "date": "2026-10-26",
        "title_ar": "تغطية مكوّنات حراسة الذكاء الاصطناعي للعربية واللهجات المغاربية",
        "where": "OPPORTUNITIES_PAIN_RESEARCH_2026-10-26_AR.md §3 (ملحق OPP-04)",
        "feeds": ["OPP-04", "B12"],
        "finding_ar": "من 11 مكوّناً، واحدٌ يعلن العربية وصفرٌ يسمّي الدارجة الجزائرية؛ المطابقة بحدود الكلمات تلتقط 3/18 صيغة عربية مقابل 9/11 فرنسية",
    },
    {
        "id": "S02",
        "date": "2026-10-26",
        "title_ar": "الغربال الموحّد بخمس بوّابات على كلّ المرشّحين",
        "where": "OPPORTUNITIES_PAIN_RESEARCH_2026-10-26_AR.md §12",
        "feeds": ["F1", "F2", "F3", "C1", "C2", "C3", "C4"],
        "finding_ar": "33 مستبعدة بسببٍ مسمّى، 5 مشروطة، 7 متأهّلة في ثلاثة عروض؛ B34 أُغلقت بواقعة",
    },
    {
        "id": "S03",
        "date": "2026-10-26",
        "title_ar": "تعداد عيوب المعرّفات في دليل Peppol وسجلّه الحيّ (بلجيكا وفرنسا)",
        "where": "OPPORTUNITIES_PAIN_RESEARCH_2026-10-26_AR.md §13",
        "feeds": ["OPP-01", "OPP-02", "B30", "B44"],
        "finding_ar": "عيوب رقم التحقّق أقلّ من 0.12%؛ نحو 175,800 شركة بلجيكية بلا رقم الضريبة الاختياري (فاستُبعدت B44)؛ و28,427 شركة فرنسية مغلقة تحمل 28,920 عنواناً، 44% منها عند Qonto مقابل حصّة 6.4%",
    },
    {
        "id": "S05",
        "date": "2026-10-26",
        "title_ar": "أسطول الوكلاء، الموجة الثانية: ملفّاتٌ جراحية ونقدٌ ثانٍ",
        "where": "OPPORTUNITIES_PAIN_RESEARCH_2026-10-26_AR.md §15",
        "feeds": ["B03", "B45", "B46", "B48", "B30"],
        "finding_ar": "الإحالة والإعداد لا يجتمعان قانونياً في CBAM؛ لا مناقصة مفتوحة للبنك الدولي في التنظيف والطريق مقاولةٌ من الباطن؛ الخيوط الأربعة الجديدة جريحة لا ميتة، ولكلٍّ اختبارٌ رخيص يحسمها",
    },
    {
        "id": "S08",
        "date": "2026-10-27",
        "title_ar": "لماذا يفوز التونسيون: المشاركة والفوز في 36,496 ترسية للبنك الدولي، وقائمة الفائزين بعقود البيانات",
        "where": "OPPORTUNITIES_PAIN_RESEARCH_2026-10-26_AR.md §18 · WB_DATA_WINNERS_FRANCOPHONE_AFRICA_2026-10-27.csv",
        "feeds": ["B46", "B01", "B30", "B12", "OPP-04"],
        "finding_ar": "التونسيون حاضرون في 728 إشعاراً ويفوزون في 307 (42%)، والجزائريون في 35 ويفوزون في 9: الفارق في المشاركة أوّلاً؛ والخبراء الرئيسيون نصف التقييم الفنّي؛ و24 فائزاً بعقود بيانات وسجلّات مسمّون، 19 منهم بقناةٍ عامّة؛ وتنظيف الفوترة الفرنسية بلا دافع الآن",
    },
    {
        "id": "S07",
        "date": "2026-10-27",
        "title_ar": "التدقيق الصارم A1: كلّ ✓ بسندٍ مقروء ومن نوعٍ مسموح، والبوّابات غير تعويضية",
        "where": "OPPORTUNITIES_PAIN_RESEARCH_2026-10-26_AR.md §17 · IDEA_REGISTER.json (audit_standard · claims)",
        "feeds": [
            "B01",
            "B03",
            "B10",
            "B12",
            "B19",
            "B22",
            "B24",
            "B30",
            "B31",
            "B38",
            "B45",
            "B46",
            "B47",
            "B48",
            "B49",
            "B50",
            "B51",
            "B52",
            "OPP-04",
            "OPP-13",
        ],
        "finding_ar": "لا فكرة تجتاز البوّابات الخمس: G1 مسنودة بترسيةٍ فعلية في B46 وحدها (البنك الدولي، النيجر، 2026-01-08، 168,715 €)؛ المتأهّلة صفر، وB31 مستبعدة، والدليل D2→D1 في B19 وB47؛ وD-320 غير جاهزة (16 من 20 قناة مجهولة)",
    },
    {
        "id": "S06",
        "date": "2026-10-27",
        "title_ar": "أسطول الوكلاء، الموجة الثالثة: أرضٌ جديدة ودروسٌ صارت اختبارات",
        "where": "OPPORTUNITIES_PAIN_RESEARCH_2026-10-26_AR.md §16",
        "feeds": ["B01", "B20", "B23", "B36", "B37", "B49", "B50", "B51", "B52"],
        "finding_ar": "G2 نقلٌ مشروط لا ممنوع (بنود نموذجية وتقييم أثر ورأي محامٍ جزائري)؛ التحقّق قلب ادّعاء الإنتاج المحاسبي (قرارا النقض يؤيّدان الاحتكار)؛ أربع أفكار مشروطة أقواها PPWR: 1,072 مصنّعاً فرنسياً، وكلّ إعلانات الشهر الأول أُعيدت، والغرامات الألمانية من 2027-02-12",
    },
    {
        "id": "S04",
        "date": "2026-10-26",
        "title_ar": "أسطول الوكلاء، الموجة الأولى: سبعة باحثين ونقدٌ مستقلّ مع تحقّقٍ من المصادر",
        "where": "OPPORTUNITIES_PAIN_RESEARCH_2026-10-26_AR.md §14",
        "feeds": ["B45", "B46", "B47", "B48", "B03", "OPP-01", "OPP-04", "OPP-13"],
        "finding_ar": "الإمارات: 1,119 معرّفاً بلا قدرة استقبال عند مزوّدين معتمدين؛ البنك الدولي: الجزائر 3 عقود مقابل تونس 95؛ EUDAMED: 44.5% بلا جهاز؛ والنقد جرح F1 وF2 وF3 ووضع سعراً منافساً لـF1",
    },
]

HISTORY = {
    "B53": [
        {
            "date": "2026-10-27",
            "event_ar": "الموجة الرابعة: سُجّلت مستبعدة من أوّل يوم — أسعار المتاجر متعادلة بالسعر الرسمي، والطريق القانوني يضيف 14% على الأقلّ، والتهريب جريمة في البلدين",
        },
        {
            "date": "2026-10-27",
            "event_ar": "الموجة الخامسة، الاتجاه المعاكس: التونسيون يشترون في الطارف وعنابة للسببين نفسيهما (السعر الموازي والدعم) بدنانير من السوق الموازية — لا يدخل البنوكَ يورو، فلا يغيّر الحكم",
        },
        {
            "date": "2026-10-28",
            "event_ar": "الموجة السادسة: ممرّ الطارف نحو تونس قائمٌ لشاحنات الأجهزة والتغليف، لكنّ الدافع التونسي يدفع بالدينار التونسي، فلا يغيّر الحكم",
        },
    ],
    "B54": [
        {
            "date": "2026-10-27",
            "event_ar": "الموجة الرابعة: الأهلية مقروءة في المادة 28 من NDICI، والإعلانان المسبقان مؤكَّدا التاريخ في بيانات البوّابة الخام؛ الأداة المالية غير مسمّاة في البيانات الوصفية",
        }
    ],
    "B50": [
        {
            "date": "2026-10-27",
            "event_ar": "الموجة الرابعة: الأمم المتحدة اشترت من الجزائر 23.2 مليون $ في 2025 مقابل 91.3 لتونس، وأغلب ذلك شراءٌ محلّي (94% من الترسيات التونسية داخل تونس)؛ وثلاثة إعلانات ترجمة للشركات مفتوحة حتى 2026-11-19",
        }
    ],
    "B49": [
        {
            "date": "2026-10-27",
            "event_ar": "الموجة الرابعة: B53 (الهواتف) سُجّلت مستبعدة بجوارها في التجارة عبر الجزائر — لا تمسّ شرط B49",
        }
    ],
    "B45": [
        {
            "date": "2026-10-26",
            "event_ar": "الملفّ الجراحي: إعادة فحصٍ حيّ لـ1,293 معرّفاً: 1,003 بلا القدرة (BDO 376، Suntech 350، Casim 222، VATit 55)؛ المضيف المجهول هو Suntech المعتمد رقم 56؛ والعقوبة على المورّد",
        },
        {
            "date": "2026-10-26",
            "event_ar": "النقد الثاني: لا قاعدة تُلزم بإعلان القدرة قبل الإطلاق، والمزوّد يصلحها بنفسه؛ مبكّرة حتى إعادة القياس بعد 2027-01-01",
        },
    ],
    "B46": [
        {
            "date": "2026-10-26",
            "event_ar": "الملفّ الجراحي: لا مناقصة مفتوحة اليوم في تنظيف السجلّات؛ القواعد لا تستبعد الجزائريين والحاجز المراجع؛ الطريق مقاولةٌ من الباطن لـ15 فائزاً مسمّى",
        },
        {
            "date": "2026-10-27",
            "event_ar": "قائمة 24 فائزاً بعقود بيانات وسجلّات (19 بقناةٍ عامّة)؛ وWEVIOO في عقدَين: تنظيف محفظة مكلّفي النيجر والسجلّ الاجتماعي الموحّد في بوروندي (OP00444744)",
        },
        {
            "date": "2026-10-27",
            "event_ar": "الموجة الرابعة: الجذر المقيس — الجزائر لا تقترض من البنك الدولي (8 إشعارات وصفر ترسية في كلّ تاريخ الواجهة مقابل 937 لتونس)، فلا مرجع أوّل يُكسَب في البيت؛ والبنك الإفريقي الآلية نفسها بخطٍّ أرقّ (عقدا بيانات من آخر 100 ترسية، والبيانات محجوبة)",
        },
    ],
    "B48": [
        {
            "date": "2026-10-26",
            "event_ar": "النقد الثاني: الموعد بعد 33 يوماً، وممثّلٌ كبير طوّر أداته (MedNet، 2026-03-10)، وجزءٌ من الصفر قد يكون إعفاءً؛ وظهور الأجهزة القديمة في الواجهة لم يُحسم",
        }
    ],
    "B01": [
        {
            "date": "2026-10-26",
            "event_ar": "النقد المستقلّ: Siretly يبيع التنظيف الآلي بـ0.29–0.40 € للسطر مقابل 1.45 € لسعر المالك؛ وعقودٌ فرنسية مُرساة للفوترة بوسيط 137,648 € تفتح طريق المقاول من الباطن",
        },
        {
            "date": "2026-10-27",
            "event_ar": "تصحيح G2 (§16): ملفّات الأطراف تحمل أسماء المقاولين الأفراد وأرقامهم، فالعرض تحت الشروط الأربعة للنقل (بنود نموذجية، وتقييم أثر يغطّي القانون 09-04، ورأي محامٍ جزائري، ولا فئات خاصّة)؛ G2 تبقى ✓ لاختبار المشتري وتصير شرطاً قبل أوّل عقد",
        },
    ],
    "B30": [
        {
            "date": "2026-10-26",
            "event_ar": "قياس Peppol: لا عيوب شكلية تُذكر؛ الألم الحيّ في معرّفاتٍ مغلقة أو غائبة عند مزوّدين مسمّين (Qonto في فرنسا)",
        },
        {
            "date": "2026-10-26",
            "event_ar": "النقد الثاني: العنوان المتبقّي لشركةٍ مغلقة قد لا يستقبل شيئاً إن كان الدليل المركزي يستبعدها، ولا عقوبة معروفة؛ معرفةٌ صحيحة بلا دافع حتى الآن",
        },
    ],
    "B12": [
        {
            "date": "2026-10-26",
            "event_ar": "معيار ArabicDialectSafety (EMNLP 2026) يغطّي الجزائرية؛ الفجوة باقية في المصنِّفات المغاربية",
        },
        {
            "date": "2026-10-27",
            "event_ar": "مُلئت 12 قناة رسمية في قائمة D-320 (تحقّقٌ حيّ)؛ بقيت 4 مجهولة من 20، فG5 تبقى جزئية",
        },
    ],
    "B03": [
        {
            "date": "2026-10-26",
            "event_ar": "حساب كلفة القيم الافتراضية لآلية الكربون: نحو 250 مليون €/سنة على صادرات الجزائر، و132 مليوناً قابلة للتوفير بالقيم الفعلية (افتراضات معلنة)",
        },
        {
            "date": "2026-10-26",
            "event_ar": "الموجة الثانية: اللائحة 2025/2551 تمنع اجتماع عمولة الإحالة مع إعداد بيانات المنشأة نفسها؛ وFertial أُسندت لمركز CRE عنابة؛ والدافع بالعملة الصعبة غائب (جريحة في G1)",
        },
        {
            "date": "2026-10-28",
            "event_ar": "الموجة السادسة: فصلا الأسمدة والحديد (31 و72) نحو 47% من صادرات الجزائر غير الطاقوية إلى الاتحاد الأوروبي في 2025 (حدٌّ أعلى على مستوى الفصل)؛ والمصدّر لا يدفع لمقيمٍ بالعملة الصعبة إلا برأي بنك الجزائر",
        },
    ],
    "OPP-13": [
        {
            "date": "2026-10-26",
            "event_ar": "محكمة ليل 2026-05-05 طبّقت سقف 250 مليون €؛ وتدقيقٌ آلي يُباع بـ190 €؛ ومشترون عموميون بوسيط سقفٍ 165,000 €",
        }
    ],
    "OPP-04": [
        {
            "date": "2026-10-26",
            "event_ar": "الجزائرية غائبة عن Belebele وFLEURS وFLORES+؛ والعمل الفردي يصل بالدينار فلا يجتاز G1",
        }
    ],
    "B20": [
        {
            "date": "2026-10-27",
            "event_ar": "الموجة الثالثة: وكيلٌ قرأ قرار النقض 21-85.594 (2022-10-04) على أنه يبيح المقاولة من الباطن تحت الإشراف؛ التحقّق أثبت العكس: القرار أيّد الإدانة، وقرار 24-81.008 (2026-01-21) مدّ الاحتكار إلى الإعارة. تبقى مستبعدة، والسبب صار مُتحقَّقاً؛ وشرط إعادة الفتح صار محدّداً (كان: إطار قانوني يسمح بالإسناد من خارج الاتحاد)",
        }
    ],
    "B23": [
        {
            "date": "2026-10-27",
            "event_ar": "الموجة الثالثة: الموعد 2026-12-30 للكبار و2027-06-30 للصغار (اللائحة 2025/2650 بحسب مصادر ثانوية) وتقدير بائع 8–25 ألف € للمستورد؛ تبقى مستبعدة (تقديمٌ مؤتمت جزئياً، وجمعٌ ميداني، ومعطياتٌ شخصية للمزارعين)",
        }
    ],
    "B36": [
        {
            "date": "2026-10-27",
            "event_ar": "تصحيح G2 (§16): نقل المعطيات الأوروبية إلى الجزائر مشروطٌ لا ممنوع، فصارت G2 جزئية (كانت ساقطة)، والعائق الحاسم صار غياب الدافع المسمّى (كان: نقل معطيات شخصية أوروبية؛ وشرط إعادة الفتح كان: قرار كفاية أو معطيات مجهولة)",
        }
    ],
    "B37": [
        {
            "date": "2026-10-27",
            "event_ar": "تصحيح G2 (§16) لا يشملها: المعطيات الصحّية تشترط استضافةً معتمدة داخل المنطقة الاقتصادية الأوروبية",
        }
    ],
    "B34": [
        {"date": "2026-10-26", "event_ar": "رادار الألم: 14 من 18 (ضمن الثلاث الأولى)"},
        {
            "date": "2026-10-26",
            "event_ar": "الغربال الموحّد: مستبعدة في G2 وG5 — Agirc-Arrco أسند المراقبة لمصرف بمناقصة (2025-10-26)",
        },
    ],
}


def _no_duplicate_keys():
    """A repeated key in HISTORY or I silently overwrites the earlier entry — a hidden deletion."""
    src = Path(__file__).read_text(encoding="utf-8")
    for name in ("HISTORY = {", "IDEAS = {"):
        start = src.index(name)
        block = src[start : src.index("\n}\n", start)]
        keys = re.findall(r'^ {1,4}"([A-Z]+-?\d+)": ', block, re.M)
        dups = sorted({k for k in keys if keys.count(k) > 1})
        if dups:
            raise SystemExit(f"duplicate keys in {name[:-4]}: {dups}")


def archive_index():
    """id -> (defining file, first date, [files holding an addendum])."""
    defined, addenda = {}, collections.defaultdict(list)
    for f in sorted(ARCH.glob("OPPORTUNITIES_*_AR.md")):
        date = re.search(r"(\d{4}-\d{2}-\d{2})", f.name).group(1)
        for line in f.read_text(encoding="utf-8").splitlines():
            m = re.match(r"^### (B\d{2}|OPP-\d{2})\b(.*)$", line)
            if m:
                if "ملحق" in m.group(2):
                    if f.name not in addenda[m.group(1)]:
                        addenda[m.group(1)].append(f.name)
                else:
                    defined.setdefault(m.group(1), (f.name, date, m.group(2).strip(" —-").strip()))
            m = re.match(r"^\| (J\d{2}) \| ([^|]+)\|", line)
            if m:
                defined.setdefault(m.group(1), (f.name, date, m.group(2).strip()))
    return defined, addenda


SYM = {"pass": "✓", "partial": "~", "fail": "✗", "na": "—"}


def apply_audit(rid, rec):
    """Apply the A1 verdict to a record; every change becomes a dated history line with its old value."""
    a = a1.AUDIT.get(rid)
    if not a:
        return rec
    sc, op, ev = rec["screening"], rec["option"], rec["evidence"]
    stage_label = {k: v.split(" — ")[0] for k, v in VOCAB["stage"].items()}
    changes = []
    for k in GATES:
        if sc["gates"][k] != a["gates"][k]:
            changes.append(f"{k} {SYM[sc['gates'][k]]}→{SYM[a['gates'][k]]}")
    new_stage = a.get("stage", sc["stage"])
    if new_stage != sc["stage"]:
        changes.append(f"المرحلة {stage_label[sc['stage']]}→{stage_label[new_stage]}")
    if "evidence" in a and a["evidence"] != ev["level"]:
        changes.append(f"الدليل {ev['level']}→{a['evidence']}")
    if "constraint" in a and a["constraint"] != sc["binding_constraint"]:
        changes.append(
            f"العائق «{VOCAB['constraint'][sc['binding_constraint']]}»→«{VOCAB['constraint'][a['constraint']]}»"
        )
    if "option" in a and a["option"] != op["state"]:
        changes.append(
            f"الخيار «{VOCAB['option_state'][op['state']]}»→«{VOCAB['option_state'][a['option']]}»"
        )
    if "basis" in a and a["basis"] != ev["basis_ar"]:
        changes.append(f"الأساس كان: «{ev['basis_ar']}»")
    if "trigger" in a and a["trigger"] != op["trigger_ar"]:
        changes.append(f"الشرط كان: «{op['trigger_ar']}»")
    rec["screening"] = {
        "stage": new_stage,
        "gates": a["gates"],
        "binding_constraint": a.get("constraint", sc["binding_constraint"]),
    }
    rec["option"] = {
        "state": a.get("option", op["state"]),
        "trigger_ar": a.get("trigger", op["trigger_ar"]),
    }
    rec["evidence"] = {
        "level": a.get("evidence", ev["level"]),
        "basis_ar": a.get("basis", ev["basis_ar"]),
    }
    event = f"تدقيق {a1.AUDIT_ID} الصارم: " + (
        " · ".join(changes) if changes else "لا تغيير — كلّ ✓ مسنودة بمصدرٍ مقروء"
    )
    rec["history"] = [*rec["history"], {"date": a1.AUDIT_DATE, "event_ar": event}]
    rec["audit"] = {"standard": a1.AUDIT_ID, "date": a1.AUDIT_DATE, "support": a["support"]}
    rec["last_reviewed"] = a1.AUDIT_DATE
    return rec


def build():
    defined, addenda = archive_index()
    records = []
    for rid in sorted(k for k in defined if k.startswith("B")):
        f, date, title = defined[rid]
        (dom, mk, ccy, dlv, ev, basis, gates, stage, cons, opt, trig, grp, rel) = IDEAS[rid]
        records.append(
            {
                "id": rid,
                "kind": "idea",
                "title_ar": title,
                "first_recorded": date,
                "archive": f,
                "addenda": addenda.get(rid, []),
                "facets": {"domain": dom, "markets": mk, "currency": ccy, "delivery": dlv},
                "evidence": {"level": ev, "basis_ar": basis},
                "screening": {"stage": stage, "gates": gates, "binding_constraint": cons},
                "option": {"state": opt, "trigger_ar": trig},
                "group": grp,
                "related": rel,
                "history": HISTORY.get(rid, []),
                "last_reviewed": LAST_REVIEWED.get(rid, REVIEWED),
            }
        )
        apply_audit(rid, records[-1])
    for rid in sorted(k for k in defined if k.startswith("J")):
        f, date, title = defined[rid]
        records.append(
            {
                "id": rid,
                "kind": "job",
                "title_ar": title,
                "first_recorded": date,
                "archive": f,
                "addenda": [],
                "facets": {
                    "domain": "employment",
                    "markets": ["DZ", "GLOBAL"],
                    "currency": JOB_CCY[rid],
                    "delivery": "employment",
                },
                "evidence": {"level": "na", "basis_ar": "إعلانٌ قُرئ أثناء البحث؛ ليس عرضاً للمؤسس"},
                "screening": {
                    "stage": "personal_income",
                    "gates": dict.fromkeys(GATES, "na"),
                    "binding_constraint": "none",
                },
                "option": {
                    "state": "held_option",
                    "trigger_ar": "إعادة التحقّق من الإعلان قبل التقديم",
                },
                "group": None,
                "related": JOB_REL.get(rid, []),
                "history": [],
                "last_reviewed": LAST_REVIEWED.get(rid, REVIEWED),
            }
        )
    for p in VC["paths"]:
        pid = p["id"]
        in_study = pid in PATH_GATES
        grp = PATH_GROUP.get(pid)
        records.append(
            {
                "id": pid,
                "kind": "value_chain_path",
                "title_ar": p.get("title_ar"),
                "first_recorded": None,
                "archive": "docs/commercial/VALUE_CHAIN.json",
                "addenda": addenda.get(pid, []),
                "facets": None,
                "evidence": {"level": "na", "basis_ar": "الحالة الحاكمة في VALUE_CHAIN.json"},
                "screening": {
                    "stage": "included" if in_study else "governed_elsewhere",
                    "gates": PATH_GATES.get(pid, dict.fromkeys(GATES, "na")),
                    "binding_constraint": "none",
                },
                "option": {
                    "state": GROUPS[grp]["option_state"] if grp else "see_value_chain",
                    "trigger_ar": GROUPS[grp]["next_test_ar"] if grp else "انظر VALUE_CHAIN.json",
                },
                "group": PATH_GROUP.get(pid),
                "related": PATH_REL.get(pid, []),
                "history": HISTORY.get(pid, []),
                "last_reviewed": REVIEWED,
            }
        )
        apply_audit(pid, records[-1])
    groups = {}
    for k, v in GROUPS.items():
        gr = {**v, "members": [r["id"] for r in records if r["group"] == k]}
        if k in a1.GROUP_STAGE and a1.GROUP_STAGE[k] != v["stage"]:
            gr["stage"] = a1.GROUP_STAGE[k]
            gr["audit_note_ar"] = (
                f"تدقيق {a1.AUDIT_ID} ({a1.AUDIT_DATE}): كانت «{VOCAB['stage'][v['stage']].split(' — ')[0]}»، "
                "ولم يبقَ عضوٌ يجتاز البوّابات الخمس بسندٍ مقروء"
            )
        groups[k] = gr
    flow = flow_counts(records)
    return {
        "$schema_version": 1,
        "title_ar": "سجلّ الأفكار الموحّد",
        "reviewed_on": REVIEWED_ON,
        "reading_view": "IDEA_REGISTER_AR.md",
        "gates": GATES,
        "vocabularies": VOCAB,
        "groups": groups,
        "studies": STUDIES,
        "flow": flow,
        "audit_standard": {
            "id": a1.AUDIT_ID,
            "date": a1.AUDIT_DATE,
            "source": a1.AUDIT_SOURCE,
            "tiers": a1.TIERS,
            "kinds": a1.KINDS,
            "gate_kinds": a1.GATE_KINDS,
            "rules_ar": a1.RULES_AR,
        },
        "claims": a1.CLAIMS,
        "records": records,
    }


def flow_counts(records):
    ideas = [r for r in records if r["kind"] == "idea"]
    paths_screened = [
        r
        for r in records
        if r["kind"] == "value_chain_path" and r["screening"]["stage"] != "governed_elsewhere"
    ]
    screened = ideas + paths_screened
    c = collections.Counter(r["screening"]["stage"] for r in screened)
    return {
        "identified_ideas": len(ideas),
        "identified_jobs": sum(r["kind"] == "job" for r in records),
        "identified_value_chain_paths": sum(r["kind"] == "value_chain_path" for r in records),
        "screened": len(screened),
        "included": c["included"],
        "conditional": c["conditional"],
        "excluded": c["excluded"],
    }


def _md_history_and_audit(reg, gates):
    """§9 belief history and §10 strict audit of the reading view."""
    voc = reg["vocabularies"]
    recs = reg["records"]
    lines = []
    lines += ["", "## 9. أثر تحديث الاعتقاد", "", "| المعرّف | التاريخ | ما تغيّر |", "|---|---|---|"]
    for r in recs:
        for h in r["history"]:
            lines.append(f"| {r['id']} | {h['date']} | {h['event_ar']} |")
    std = reg["audit_standard"]
    lines += [
        "",
        f"## 10. التدقيق الصارم {std['id']} ({std['date']})",
        "",
        f"**المعيار:** [`{std['source']}`](../../commercial/DECISION_COMMITMENT_ENGINE.md) — بوّاباتٌ غير تعويضية، ولا ترقية للاهتمام إلى ميزانية ولا للسعر إلى شراء، وما لم يُقرأ «مجهول» لا تحقّق.",
        "",
    ]
    lines += [f"{i}. {r}" for i, r in enumerate(std["rules_ar"], 1)]
    lines += [
        "",
        "**درجات السند:** " + " · ".join(f"**{k}** {v}" for k, v in std["tiers"].items()),
        "",
        "**الأنواع المسموح بها لكلّ ✓:** "
        + " · ".join(f"{k}: {', '.join(v)}" for k, v in std["gate_kinds"].items()),
        "",
        "### 10.1 الحكم لكلّ فكرةٍ حيّة",
        "",
        "| المعرّف | G1→G5 | المرحلة | سندات ✓ | سندات ~ و✗ |",
        "|---|---|---|---|---|",
    ]
    for r in recs:
        a = r.get("audit")
        if not a:
            continue
        ok = [
            f"{k}: {' '.join(a['support'].get(k, []))}"
            for k in GATES
            if r["screening"]["gates"][k] == "pass"
        ]
        nok = [
            f"{k}: {' '.join(a['support'].get(k, [])) or 'لا سند'}"
            for k in GATES
            if r["screening"]["gates"][k] != "pass"
        ]
        lines.append(
            f"| {r['id']} | {gates(r)} | {voc['stage'][r['screening']['stage']].split(' — ')[0]} | {' · '.join(ok) or '—'} | {' · '.join(nok)} |"
        )
    lines += [
        "",
        "### 10.2 سجلّ السندات",
        "",
        "| السند | يخصّ | البوّابة | النوع | الدرجة | التاريخ | ما يقوله | المصدر |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for c in reg["claims"]:
        url = c["url"]
        link = (
            f"[{c['source']}]({url})"
            if url.startswith("https://")
            else f"{c['source']} (`{url.removeprefix('repo:')}`)"
        )
        lines.append(
            f"| {c['id']} | {' · '.join(c['records'])} | {' · '.join(c['gates'])} | {std['kinds'][c['kind']]} | {c['tier']} | {c['event_date']} | {c['text_ar']} | {link} |"
        )
    return lines


def md(reg):
    voc = reg["vocabularies"]
    recs = reg["records"]
    fl = reg["flow"]
    inc_groups = [k for k, gr in reg["groups"].items() if gr["stage"] == "included"]
    cond_groups = [k for k, gr in reg["groups"].items() if gr["stage"] == "conditional"]

    def ev(r):
        return r["evidence"]["level"]

    def gates(r):
        return " ".join(voc["gate_verdict"][r["screening"]["gates"][k]] for k in GATES)

    lines = []
    lines += [
        "# سجلّ الأفكار الموحّد — كلّ فكرةٍ محفوظة ومصنَّفة",
        "",
        f"**آخر مراجعة:** {reg['reviewed_on']} · **المصدر الآلي:** [`IDEA_REGISTER.json`](IDEA_REGISTER.json) · "
        "**الأصول:** [أرشيف 2026-10-22](OPPORTUNITIES_AND_JOBS_CONVERSATION_2026-10-22_AR.md) · "
        "[أرشيف 2026-10-26](OPPORTUNITIES_PAIN_RESEARCH_2026-10-26_AR.md) · [سلسلة القيمة](../../commercial/VALUE_CHAIN.json)",
        "",
        "**الحالة:** فهرسٌ منظِّم لا خطّة تشغيل. لا يرفع أيّ فكرةٍ إلى دليل شراء، ولا يرخّص بناءً (D-321)، "
        "ولا يغيّر قرار المالك. الأرشيفان يبقيان الأصل، وهذا السجلّ يرتّبهما ولا يحلّ محلّهما.",
        "",
        "## 1. لماذا هذا السجلّ، وما قاعدته الأولى",
        "",
        "طلب المالك في 2026-10-26 تنظيم كلّ الأفكار تنظيماً علمياً **دون حذف أيّ شيء**. القاعدة الأولى إذن: "
        "**الاستبعاد ليس حذفاً**. كلّ فكرةٍ لم تُختر تبقى بسجلّها كاملاً: سببُ استبعادها، والبوّابة التي أسقطتها، "
        "والشرطُ الذي يعيد فتحها. واختبارٌ آلي (`tests/unit/tools/test_idea_register.py`) يُحمّر أيّ تغييرٍ يُسقط "
        "فكرةً من السجلّ أو يترك مستبعدةً بلا سبب.",
        "",
        "## 2. المنهج: ستّة أطرٍ منشورة، ولكلٍّ حقلٌ في السجلّ",
        "",
        "| الإطار | المصدر | ما يفرضه هنا | الحقل |",
        "|---|---|---|---|",
        "| تقرير المراجعات المنهجية PRISMA 2020 | Page وآخرون، *BMJ* 2021;372:n71 | مسار مرئي من «المُحدَّد» إلى «المُدرَج»، ولكلّ مستبعَد سببٌ مكتوب | `screening.stage` · `binding_constraint` |",
        "| مبادئ FAIR للبيانات | Wilkinson وآخرون، *Scientific Data* 3:160018، 2016 | معرّفٌ دائم لا يُعاد استعماله، وبيانات وصفية مقروءة آلياً، ومصدرٌ لكلّ سجلّ | `id` · `archive` · JSON |",
        "| المقاربة العلمية لريادة الأعمال | Camuffo وآخرون، *Management Science* 66(2)، 2020؛ وإعادة إنتاجها على 759 شركة في أربع تجارب عشوائية، *Strategic Management Journal* 45(6):1209–1237، 2024 | كلّ فكرة فرضية لها اختبار وشرط إيقاف مكتوبان مسبقاً؛ والدراسة وجدت أنّ المقاربة تزيد إنهاء الأفكار الضعيفة | `groups.*.next_test_ar` · `kill_ar` |",
        "| ريادة الأعمال البايزية | Agrawal وCamuffo وGambardella وGans وScott وStern (محرّرون)، MIT Press، 2026 | الاعتقاد يُحدَّث بالدليل، ويُحفظ أثر التحديث | `history` |",
        "| الخيارات الحقيقية | McGrath، *Academy of Management Review* 24(1):13–30، 1999 | الفكرة غير المختارة خيارٌ رخيص الحفظ، يُمارَس حين يتحقّق شرطه | `option.state` · `trigger_ar` |",
        "| المراجعة المنهجية الحيّة + تقدير اليقين | Elliott وآخرون، *J Clin Epidemiol* 91:23–30، 2017؛ Guyatt وآخرون (GRADE)، *BMJ* 336:924، 2008 | السجلّ يُراجَع باستمرار بتاريخ، وقوّة الدليل تُقدَّر بسلّمٍ صريح | `last_reviewed` · `evidence.level` |",
        "",
        "**التصنيف بالأوجه** (منهج Ranganathan): لكلّ فكرةٍ خمسة أوجهٍ مستقلّة — المجال، والسوق، والعملة، "
        "وطريقة التسليم، والعائق الحاسم — فتُقرأ القائمة من أيّ زاوية دون نسخها.",
        "",
        "**سلّم الدليل** (سلّم المستودع D0–D5، المقابل لتقدير اليقين في GRADE):",
        "",
    ]
    lines += [f"- **{k}** — {v}" for k, v in voc["evidence_level"].items() if k != "na"]
    lines += ["", "**البوّابات الخمس** (الغربال S02):", ""]
    lines += [f"- **{k}** — {v}" for k, v in reg["gates"].items()]
    lines += [
        "",
        "## 3. مسار الغربلة (على نمط PRISMA)",
        "",
        "```text",
        f"المُحدَّد:  {fl['identified_ideas']} فكرة (B01–B{fl['identified_ideas']:02d}) + {fl['identified_value_chain_paths']} مساراً في سلسلة القيمة + {fl['identified_jobs']} وظيفة",
        f"المُغربَل: {fl['screened']} (كلّ الأفكار + المسارات التي شملها الغربال)",
        f"   ├── متأهّلة:  {fl['included']}  → {len(inc_groups)} عروض: {' · '.join(inc_groups)}",
        f"   ├── مشروطة:  {fl['conditional']}  → {len(cond_groups)} مجموعات: {' · '.join(cond_groups)}، وما خارجها بشرطه",
        f"   └── مستبعدة: {fl['excluded']}  → محفوظة بسببٍ وشرط إعادة فتح",
        "الوظائف: مسار دخلٍ فردي منفصل، لا تمرّ بغربال الشركة",
        "```",
        "",
        "## 4. المجموعات: ما يُختبر الآن وما ينتظر شرطه",
        "",
        "| المجموعة | العنوان | الأعضاء | حالة الخيار | الاختبار التالي | شرط الإيقاف |",
        "|---|---|---|---|---|---|",
    ]
    for k, gr in reg["groups"].items():
        lines.append(
            f"| {k} | {gr['title_ar']} | {' · '.join(gr['members'])} | {voc['option_state'][gr['option_state']]} | {gr['next_test_ar']} | {gr['kill_ar']} |"
        )
    lines += [
        "",
        "## 5. السجلّ الكامل للأفكار، مصنّفاً بالمجال",
        "",
        "الأعمدة: الدليل (D0–D5) · البوّابات G1→G5 (✓ مستوفاة · ~ جزئياً · ✗ غير مستوفاة) · المرحلة · حالة الخيار · العائق الحاسم · شرط إعادة الفتح أو الاختبار التالي.",
        "",
    ]
    by_dom = collections.defaultdict(list)
    for r in recs:
        if r["kind"] == "idea":
            by_dom[r["facets"]["domain"]].append(r)
    for dom in voc["domain"]:
        if dom not in by_dom:
            continue
        lines += [
            f"### {voc['domain'][dom]}",
            "",
            "| المعرّف | الفكرة | السوق | العملة | الدليل | G1→G5 | المرحلة | الخيار | العائق | الشرط |",
            "|---|---|---|---|---|---|---|---|---|---|",
        ]
        for r in by_dom[dom]:
            lines.append(
                f"| {r['id']} | {r['title_ar']} | {' · '.join(r['facets']['markets'])} | {voc['currency'][r['facets']['currency']]} | "
                f"{ev(r)} | {gates(r)} | {voc['stage'][r['screening']['stage']].split(' — ')[0]} | "
                f"{voc['option_state'][r['option']['state']]} | {voc['constraint'][r['screening']['binding_constraint']]} | {r['option']['trigger_ar']} |"
            )
        lines.append("")
    lines += [
        "## 6. مسارات سلسلة القيمة",
        "",
        "حالتها الحاكمة في [`VALUE_CHAIN.json`](../../commercial/VALUE_CHAIN.json) ولا تُنسخ هنا كي لا تتقادم نسخةٌ ثانية (D-188). "
        "يُسجَّل هنا ارتباطها بالأفكار وبالمجموعات فقط.",
        "",
        "| المسار | العنوان | المجموعة | يرتبط بـ |",
        "|---|---|---|---|",
    ]
    for r in recs:
        if r["kind"] == "value_chain_path":
            lines.append(
                f"| {r['id']} | {r['title_ar']} | {r['group'] or '—'} | {' · '.join(r['related']) or '—'} |"
            )
    lines += [
        "",
        "## 7. الوظائف والمهام (مسار دخلٍ فردي)",
        "",
        "| الرقم | الجهة أو الدور | العملة | يرتبط بـ | الحالة |",
        "|---|---|---|---|---|",
    ]
    for r in recs:
        if r["kind"] == "job":
            lines.append(
                f"| {r['id']} | {r['title_ar']} | {voc['currency'][r['facets']['currency']]} | {' · '.join(r['related']) or '—'} | {r['option']['trigger_ar']} |"
            )
    lines += [
        "",
        "## 8. الدراسات الأصلية التي غذّت السجلّ",
        "",
        "| الدراسة | التاريخ | العنوان | الموضع | تغذّي | الخلاصة |",
        "|---|---|---|---|---|---|",
    ]
    for s in reg["studies"]:
        lines.append(
            f"| {s['id']} | {s['date']} | {s['title_ar']} | {s['where']} | {' · '.join(s['feeds'])} | {s['finding_ar']} |"
        )
    lines += _md_history_and_audit(reg, gates)
    lines += [
        "",
        "## 11. قواعد الإضافة (السجلّ يُضاف إليه ولا يُحذف منه)",
        "",
        "1. فكرةٌ جديدة تُعرَّف أولاً في أرشيفٍ مؤرَّخ بمصدرٍ وتاريخ، ثمّ تُضاف إلى `IDEA_REGISTER.json` بالرقم التالي. لا رقم يُعاد استعماله.",
        "2. تغيّر الحالة لا يمحو الحالة السابقة: يُضاف سطرٌ إلى `history` بالتاريخ والسبب.",
        "3. الاستبعاد يحمل دائماً بوّابةً وعائقاً وشرط إعادة فتح.",
        "4. حالة مسارات سلسلة القيمة تُقرأ من `VALUE_CHAIN.json` وحده.",
        "5. هذه القراءة العربية تُولَّد من JSON؛ والاختبار يتحقّق من أنّ كلّ معرّفٍ فيه حاضرٌ هنا وأنّ أرقام المسار مطابقة.",
        "6. كلّ فكرةٍ حيّة (متأهّلة أو مشروطة) تحمل تدقيقاً صارماً، ولا ✓ إلا بسندٍ مقروء من نوعٍ مسموح؛ يفرضه `tests/unit/tools/test_idea_register_audit.py`.",
        "",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    _no_duplicate_keys()
    reg = build()
    (ARCH / "IDEA_REGISTER.json").write_text(
        json.dumps(reg, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
    (ARCH / "IDEA_REGISTER_AR.md").write_text(md(reg), encoding="utf-8")
    print(json.dumps(reg["flow"], ensure_ascii=False))
