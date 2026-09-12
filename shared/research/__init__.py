"""حزمة البحث المستقل — معرفة جديدة قابلة للتصدير بالعملة الصعبة.

تولّد هذه الحزمة ثلاثَ معارفَ جديدة كليّاً، كلٌّ منها قابلة للتدقيق والتوريّد:

1. **CDKC** (`durable_knowledge.py`, `exportable_eval.py`) — معامل المعرفة الدائمة
   القابل للتصدير، ويجمع:
   - BKT للإتقان الدائم
   - FSRS لقابلية الاسترجاع
   - التحقق الرمزي لصحة المحتوى
   - فجوة الوهم للمعايرة
   - التبديل اللغوي العربي/الفرنسي/الدارجة

2. **VEP** (`verifiable_evidence.py`, `portable_trust.py`) — بروتوكول البرهان
   القابل للحمل، ويحوّل «تقييم اعتمادية الوكلاء» من **سلعة ثقة** إلى **سلعة فحص**
   عبر إيصالٍ حتميٍّ قابل لإعادة التشغيل داخل بيئة المشتري نفسه، مع قياسِ كلفة
   التحقّق وقرارِ قبولٍ منطوق وأجلِ ترحيلٍ بوصفه قيدَ تصميمِ عقد.

3. **CND** (`null_invariance.py`) — التباعدُ عند البطلان المُصدَّق
   (Certified-Null Divergence) ومؤشّرُ الطاعة المزدوج (LID):
   - شهادةُ بطلانٍ **محسوبة** لكلّ تحويلة سطح (تشكيل/تماثلٌ بصري/Arabizi/نسخٌ صوتي/
     اختزالٌ إملائي/دارجة/تبديلٌ لغوي) بثلاث درجات: certified · partial · rejected
   - ذخيرةٌ كنارية بلا محتوى ضارّ: سياسةٌ معلنة + رمزٌ كناري يُعاد إصداره لكلّ اشتباك
   - قياسٌ **مزدوج الاتّجاه**: تسريبُ الرمز (خرقٌ ظهر بعد تحوّلٍ باطل) والرفضُ الكاذب
     (بندٌ مباحٌ رُفض بعد التحوّل) — والثاني هو ما يدفع المشتري ثمنه اليوم
   - ضابطٌ سلبي داخل الذخيرة نفسها (نقلُ نقطة: ط→ظ) تُرفض شهادته، فيُثبت أنّ الفلتر يرفض
   - كلفةُ التعرّض ونقطةُ التعادل بوحدات المشتري (لا أرقامَ مالٍ مُخترعة)

   ⚠️ حدودٌ مُعلنة: القياسُ **آليةٌ** لا معدّلَ اختراق، والأزواجُ لكلّ عائلةٍ دون حدّ
   النضج ⇒ الإسنادُ إلى عائلةٍ بعينها `None` لا صفراً (K1/K2 في وثيقة القتل).
   المعرفةُ تخدم الخطوطَ التجارية القائمة (1 · 2 · 6) — ⛔ لا خطَّ ثامناً (D-290 L8).

القانون: stdlib فقط، لا استيراد من app/ ولا microservices/ — قابلة للتوريّد والتدقيق،
وتُشحن إلى عميلٍ لا يملك تبعياتنا.
"""

from __future__ import annotations

from .durable_knowledge import (
    CdkcError,
    CdkcInput,
    CdkcResult,
    LanguageSwitchCost,
    SymbolicWeight,
    compute_cdkc,
    compute_language_switch_cost,
    compute_symbolic_weight,
)
from .exportable_eval import (
    EvalTask,
    EvalTaskKind,
    ExportableEvalBundle,
    build_eval_bundle,
)
from .null_invariance import (
    CanaryCorpus,
    CanaryProbe,
    CertificationTier,
    CndEstimate,
    DivergenceCell,
    ExposureCost,
    LidResult,
    NullityCertificate,
    NullityReason,
    NullOperator,
    OperatorKind,
    PairVerdict,
    PerturbationClass,
    ProbeKind,
    SurfaceBehaviour,
    SurfaceFamily,
    TrialOutcome,
    aggregate_trials,
    break_even_cost_ratio,
    build_cells,
    build_operator_registry,
    certify_null_transformation,
    compute_cnd,
    compute_lid,
    corpus_coverage,
    expected_exposure_cost,
    freeze_corpus,
    fresh_canary_token,
    load_canary_corpus,
    minimum_pairs_for_effect,
    pair_verdict,
    reissue_corpus,
    replace_probe_text,
)
from .portable_trust import (
    AcceptDecision,
    BreachVerdict,
    EscapeDelta,
    Interval,
    PrvResult,
    RepatriationRisk,
    acceptance_decision,
    compute_prv,
    compute_ptc,
    contract_term_ceiling,
    estimate_escape_delta,
    newcombe_difference,
    presence_substitution_index,
    repatriation_breach_risk,
    wilson_interval,
)
from .verifiable_evidence import (
    Commitment,
    EvaluationReceipt,
    FailureClass,
    MerkleStep,
    ReceiptVerification,
    RunOutcome,
    RunRecord,
    VepError,
    build_chain,
    build_receipt,
    canonical_json,
    commit_failure_classes,
    commit_value,
    deterministic_probe_stream,
    digest_payload,
    env_fingerprint,
    merkle_proof,
    merkle_root,
    public_summary,
    replay_digest,
    sha256_hex,
    verify_commitment,
    verify_merkle_proof,
    verify_receipt,
)

__all__ = [
    # CDKC — المعرفة الدائمة القابلة للتصدير
    # CND  — التباعد عند البطلان المُصدَّق ومؤشّر الطاعة المزدوج
    # VEP — البرهان القابل للحمل: الاقتصاد والقرار
    # VEP — البرهان القابل للحمل: الإيصال
    "AcceptDecision",
    "BreachVerdict",
    "CanaryCorpus",
    "CanaryProbe",
    "CdkcError",
    "CdkcInput",
    "CdkcResult",
    "CertificationTier",
    "CndEstimate",
    "Commitment",
    "DivergenceCell",
    "EscapeDelta",
    "EvalTask",
    "EvalTaskKind",
    "EvaluationReceipt",
    "ExportableEvalBundle",
    "ExposureCost",
    "FailureClass",
    "Interval",
    "LanguageSwitchCost",
    "LidResult",
    "MerkleStep",
    "NullOperator",
    "NullityCertificate",
    "NullityReason",
    "OperatorKind",
    "PairVerdict",
    "PerturbationClass",
    "ProbeKind",
    "PrvResult",
    "ReceiptVerification",
    "RepatriationRisk",
    "RunOutcome",
    "RunRecord",
    "SurfaceBehaviour",
    "SurfaceFamily",
    "SymbolicWeight",
    "TrialOutcome",
    "VepError",
    "acceptance_decision",
    "aggregate_trials",
    "break_even_cost_ratio",
    "build_cells",
    "build_chain",
    "build_eval_bundle",
    "build_operator_registry",
    "build_receipt",
    "canonical_json",
    "certify_null_transformation",
    "commit_failure_classes",
    "commit_value",
    "compute_cdkc",
    "compute_cnd",
    "compute_language_switch_cost",
    "compute_lid",
    "compute_prv",
    "compute_ptc",
    "compute_symbolic_weight",
    "contract_term_ceiling",
    "corpus_coverage",
    "deterministic_probe_stream",
    "digest_payload",
    "env_fingerprint",
    "estimate_escape_delta",
    "expected_exposure_cost",
    "freeze_corpus",
    "fresh_canary_token",
    "load_canary_corpus",
    "merkle_proof",
    "merkle_root",
    "minimum_pairs_for_effect",
    "newcombe_difference",
    "pair_verdict",
    "presence_substitution_index",
    "public_summary",
    "reissue_corpus",
    "repatriation_breach_risk",
    "replace_probe_text",
    "replay_digest",
    "sha256_hex",
    "verify_commitment",
    "verify_merkle_proof",
    "verify_receipt",
    "wilson_interval",
]
