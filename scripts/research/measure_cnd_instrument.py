#!/usr/bin/env python3
"""قياسٌ حتمي على الأداة نفسها: ماذا تستطيع ذخيرةُ CND أن تقيس اليوم، وماذا لا تستطيع؟

## لماذا هذا السكربت موجود

المعرفةُ الجديدة في `shared/research/null_invariance.py` هي **أداةُ قياس**: شهادةُ
بطلانٍ للتحويلات السطحية، وقياسٌ مزدوج داخل البند الواحد (تسريب + رفض كاذب)، وسياسةٌ
كناريةٌ بلا محتوى ضار. لكنّ أداةً لم تُقَس حدودُها تُستعمل خارجها — وهذا بالضبط ما
يمنعه الدستور (D-290 · L3: «لا تُباع قيمةٌ لم تُقَس»).

فالسؤالان اللذان يجيب عنهما هذا السكربت **قبل** أيّ تشغيلٍ على نموذج:

1. **هل الأداةُ ترفض ما يجب رفضه؟** الضابطُ السلبي (نقلُ نقطةٍ يغيّر الكلمة) مشتقٌّ
   داخل الذخيرة الحقيقية، ويجب أن يُرفَض ٨/٨ — وإن قُبل يوماً فالفلتر معطوب.
2. **هل الذخيرةُ كافيةٌ للحكم؟** لكلّ عائلةِ سطحٍ عددُ الأزواج مقابل `MIN_N_FOR_ESTIMATE`،
   وأصغرُ عددِ أزواجٍ يستبعد الصفر لكلّ أثرٍ أدنى معلن (MDE) — فتُقال الجملةُ التي
   تسبق الإنفاق: «بهذه الذخيرة لا يُحسم أيُّ أثرٍ من هذه»، بدلَ تنفيذٍ يُنتج «لا نعرف»
   ويُقرأ دحضاً (درسُ VERA على بروتوكول H1).

## ما يخرج منه ليس رأياً ولا قياسَ نموذج

الناتج `docs/research/CND_MEASUREMENTS.json` — ملفُّ قياسٍ مؤرَّخ، كلُّ رقمٍ فيه قابلٌ
لإعادة الحساب بتشغيل السكربت نفسه (`--check` يقارن ويُفشِل عند الانحراف). وهو
**حسابٌ على الأداة وذخيرتها**: ⛔ لا نموذجَ شُغِّل، ولا عميلَ قِيس، ولا سعرَ سُئل.

الوسم: 🟢⟨ح⟩ حتمي محسوب — وسمٌ مكمّل لا بديل (🟢 موثق · 🟡 أطروحة · 🔴 فرضية).

## الاستعمال

    python3 scripts/research/measure_cnd_instrument.py            # يكتب ملف القياس
    python3 scripts/research/measure_cnd_instrument.py --check    # يتحقق من المودَع

لا يُكتب في `app/` ولا يستورد منها: الحزمة `shared.research` stdlib خالصة.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:  # pragma: no cover - إقلاع المسار
    sys.path.insert(0, str(ROOT))

from shared.research.null_invariance import (
    CND_VERSION,
    MAX_LENGTH_RATIO,
    MIN_LENGTH_RATIO,
    CanaryCorpus,
    CertificationTier,
    CndEstimate,
    ProbeKind,
    SurfaceBehaviour,
    SurfaceFamily,
    break_even_cost_ratio,
    build_cells,
    corpus_coverage,
    expected_exposure_cost,
    freeze_corpus,
    load_canary_corpus,
    minimum_pairs_for_effect,
    reissue_corpus,
)
from shared.research.portable_trust import MIN_N_FOR_ESTIMATE

CORPUS = ROOT / "shared" / "research" / "corpus" / "cnd_canary_v1.json"
OUTPUT = ROOT / "docs" / "research" / "CND_MEASUREMENTS.json"

#: الآثارُ الدنيا المعلنة (MDE) التي يُسأل عنها قبل التنفيذ — لا بعدها.
#: 🟡 مُدخلاتُ تحليل لا قياسات: «لو كان التباعدُ الأساسي ٢٪ وأردنا كشف ٧٪…».
MDE_GRID: tuple[tuple[float, float], ...] = (
    (0.02, 0.07),
    (0.02, 0.10),
    (0.05, 0.15),
    (0.10, 0.20),
    (0.10, 0.30),
)

#: معدّلاتٌ إيضاحية لنسبة التعادل — 🟡 مُدخلاتُ تحليل، ⛔ ليست قياسَ عميل.
ILLUSTRATIVE_RATES: tuple[tuple[float, float], ...] = (
    (0.05, 0.05),
    (0.05, 0.20),
    (0.20, 0.05),
    (0.35, 0.10),
)

#: حجمُ العيّنة الوهمي المستعمل لجعل الخلايا الإيضاحية ناضجة (٤٠٠ زوجاً).
ILLUSTRATIVE_PAIRS: int = 400


def _mature_estimate(rate: float, pairs: int = ILLUSTRATIVE_PAIRS) -> CndEstimate | None:
    """يبني خليةً ناضجةً بمعدّلٍ مُعلن — لاستدعاء الدوال الحقيقية بلا اختصارٍ موازٍ."""
    from shared.research.null_invariance import DivergenceCell, compute_cnd

    cell = DivergenceCell(
        family=SurfaceFamily.MSA,
        tier=CertificationTier.CERTIFIED,
        kind=ProbeKind.VIOLATION,
        pairs=pairs,
        flips=round(rate * pairs),
        stable=pairs - round(rate * pairs),
        excluded=0,
        unattributable=0,
    )
    return compute_cnd(cell)


def certification_audit(corpus: CanaryCorpus) -> dict[str, object]:
    """تدقيقُ الشهادات: لكلّ عائلةٍ درجتُها وقيمُ الفحوص المُلاحظة (لا خلاصة فقط)."""
    rows: dict[str, object] = {}
    for family, probes in corpus.by_family().items():
        variants = [probe for probe in probes if not probe.is_baseline]
        if not variants:
            rows[str(family)] = {
                "role": "baseline",
                "probes": len(probes),
                "note_ar": "أساسُ القياس — لا تحويلَ ليُشهَد عليه.",
            }
            continue
        tiers = {str(probe.certificate.tier) for probe in variants}
        reasons: dict[str, int] = {}
        for probe in variants:
            for reason in probe.certificate.reasons:
                reasons[str(reason)] = reasons.get(str(reason), 0) + 1
        ratios = [probe.certificate.length_ratio for probe in variants]
        drifts = [probe.certificate.token_drift for probe in variants]
        rows[str(family)] = {
            "role": "control" if family is SurfaceFamily.AR_DOT_SHIFT_CONTROL else "surface",
            "probes": len(variants),
            "tiers": sorted(tiers),
            "rejection_reasons": dict(sorted(reasons.items())),
            "length_ratio_min": round(min(ratios), 4),
            "length_ratio_max": round(max(ratios), 4),
            "length_ratio_band": [MIN_LENGTH_RATIO, MAX_LENGTH_RATIO],
            "token_drift_max": max(drifts),
            "requires_human_review": variants[0].certificate.requires_human_review,
        }
    return dict(sorted(rows.items()))


def maturity_gap(corpus: CanaryCorpus) -> list[dict[str, object]]:
    """فجوةُ النضج: كم زوجاً لكلّ عائلةٍ ولكلّ تجميع، وكم نيّةً يلزم لبلوغ حدّ الحكم.

    الصفوفُ على مستويين لأنّ الحكمين مختلفان: **لكلّ عائلة** (أيُّ سطحٍ بعينه يقلب
    القرار) و**مُجمَّعاً لكلّ اتجاه** (هل يوجد تباعدٌ ما أياً كان سطحه). الذخيرةُ قد
    تكفي الثاني دون الأول — وهذا فرقٌ يجب أن يُقال رقماً لا أن يُخفى في متوسط.
    """
    intents = len({probe.intent_id for probe in corpus.probes})
    rows: list[dict[str, object]] = []

    def row(
        *, scope: str, kind: ProbeKind, pairs: int, pairs_per_intent: float
    ) -> dict[str, object]:
        needed = -(-MIN_N_FOR_ESTIMATE * intents // pairs) if pairs > 0 and intents > 0 else None
        return {
            "scope": scope,
            "kind": str(kind),
            "pairs": pairs,
            "min_pairs_for_index": MIN_N_FOR_ESTIMATE,
            "mature": pairs >= MIN_N_FOR_ESTIMATE,
            "pairs_per_intent": round(pairs_per_intent, 3),
            "intents_required_for_maturity": needed,
            "intents_today": intents,
        }

    for kind in (ProbeKind.VIOLATION, ProbeKind.BENIGN):
        per_family: dict[SurfaceFamily, int] = {}
        per_language: dict[str, int] = {}
        total = 0
        for _baseline, variant in corpus.pairs(kind):
            if variant.certificate.is_rejected:
                continue
            per_family[variant.family] = per_family.get(variant.family, 0) + 1
            per_language[variant.language] = per_language.get(variant.language, 0) + 1
            total += 1
        for family, pairs in sorted(per_family.items()):
            rows.append(
                row(
                    scope=str(family),
                    kind=kind,
                    pairs=pairs,
                    pairs_per_intent=pairs / intents if intents else 0.0,
                )
            )
        for language, pairs in sorted(per_language.items()):
            rows.append(
                row(
                    scope=f"pooled_language:{language}",
                    kind=kind,
                    pairs=pairs,
                    pairs_per_intent=pairs / intents if intents else 0.0,
                )
            )
        rows.append(
            row(
                scope="pooled_all_families",
                kind=kind,
                pairs=total,
                pairs_per_intent=total / intents if intents else 0.0,
            )
        )
    return rows


def power_curve() -> list[dict[str, object]]:
    """أصغرُ عددِ أزواجٍ يحسم كلّ أثرٍ أدنى معلن — أو `None` إن لم يُحسم في المدى."""
    rows: list[dict[str, object]] = []
    for baseline_rate, target_rate in MDE_GRID:
        rows.append(
            {
                "baseline_flip_rate": baseline_rate,
                "target_flip_rate": target_rate,
                "effect_pp": round((target_rate - baseline_rate) * 100, 2),
                "smallest_decisive_pairs": minimum_pairs_for_effect(baseline_rate, target_rate),
                "reported_as": "🟢⟨ح⟩ حتمي على فاصل نيوكومب — لا قياسَ نموذج",
            }
        )
    return rows


def break_even_table() -> list[dict[str, object]]:
    """نسبةُ التعادل وكلفةُ التعرّض **بوحدات معيارية** — السعرُ من المشتري لا منّا.

    ⛔ لا يورو ولا دولار هنا: الكلفتان مُدخلان رمزيان (=١) كي يظهر أنّ الأداة تُعيد
    ترتيب الأولويات بنِسَب المشتري، لا بحجّة البائع. من يريد مبلغاً يُمرّر كلفته هو.
    """
    rows: list[dict[str, object]] = []
    for leak_rate, refusal_rate in ILLUSTRATIVE_RATES:
        leak = _mature_estimate(leak_rate)
        refusal = _mature_estimate(refusal_rate)
        cost = expected_exposure_cost(
            leak,
            refusal,
            cost_per_leak=1.0,
            cost_per_false_refusal=1.0,
            volume=1_000_000,
        )
        rows.append(
            {
                "leak_rate_assumed": leak_rate,
                "refusal_rate_assumed": refusal_rate,
                "break_even_cost_ratio": break_even_cost_ratio(leak, refusal),
                "exposure_per_million_unit_costs": (
                    None
                    if cost is None
                    else {
                        "low": round(cost.total_low, 2),
                        "point": round(cost.total_point, 2),
                        "high": round(cost.total_high, 2),
                        "dominant_direction": cost.dominant_direction_at_point,
                    }
                ),
                "status": "🟡 مُدخلُ تحليلٍ معلن — ⛔ ليس قياساً على عميل ولا سعراً",
            }
        )
    return rows


def canary_survival(corpus: CanaryCorpus) -> dict[str, object]:
    """هل نجى الرمزُ الكناري من كلِّ تحويلٍ صالح؟ شرطُ تصميمٍ لا زينة.

    الرمزُ لاتينيٌّ رقميٌّ عمداً: إن تغيّر تحت تحويلٍ أبجدي، فالفرقُ المقيس بين
    الأساس والسطح لم يعد فرقَ لغةٍ بل فرقَ مُحفِّز — والقياسُ كلُّه يسقط.
    """
    usable = 0
    preserved = 0
    lost: list[str] = []
    for kind in (ProbeKind.VIOLATION, ProbeKind.BENIGN):
        for baseline, variant in corpus.pairs(kind):
            if variant.certificate.is_rejected:
                continue
            usable += 1
            in_base = baseline.canary_token in baseline.text
            in_variant = variant.canary_token in variant.text
            if in_base == in_variant:
                preserved += 1
            else:
                lost.append(variant.probe_id)
    return {
        "usable_pairs": usable,
        "canary_state_preserved": preserved,
        "canary_state_broken": lost,
        "rule_ar": "الرمزُ حاضرٌ في مسابير الخرق وغائبٌ في المباحة، بالتساوي على الطرفين.",
    }


def reissue_stability(corpus: CanaryCorpus) -> dict[str, object]:
    """إعادةُ الإصدار برموزٍ جديدة لا تُغيّر الأداة: نفسُ الدرجات ونفسُ الرفض."""
    reissued = reissue_corpus(corpus, "ENG-DEMO-0001")
    original_tiers = {probe.probe_id: str(probe.certificate.tier) for probe in corpus.probes}
    reissued_tiers = {probe.probe_id: str(probe.certificate.tier) for probe in reissued.probes}
    tokens_changed = sum(
        1
        for probe in reissued.probes
        if probe.canary_token
        != next(p.canary_token for p in corpus.probes if p.probe_id == probe.probe_id)
    )
    return {
        "probes": len(reissued.probes),
        "tokens_refreshed": tokens_changed,
        "tier_map_identical": original_tiers == reissued_tiers,
        "rejected_before": len(corpus.rejected()),
        "rejected_after": len(reissued.rejected()),
        "example_fresh_token": next(
            probe.canary_token for probe in reissued.probes if probe.intent_id == "CND-INT-01"
        ),
        "limit_ar": (
            "الجدّةُ مُنشأة لا مُثبتة: لا وسيلة لإثبات أنّ نموذجاً لم يرَ نمطَ الرمز قبلاً، "
            "لذلك يبقى القياسُ مزدوجاً داخل الاشتباك (أساس/سطح)."
        ),
    }


def build_payload(corpus: CanaryCorpus) -> dict[str, object]:
    """يبني ملفَّ القياس كاملاً — حتميٌّ إلا من طابع الزمن الذي يُستثنى في `--check`."""
    receipt = freeze_corpus(corpus)
    coverage = corpus_coverage(corpus)
    behaviours: dict[str, SurfaceBehaviour] = {}
    cells = build_cells(corpus, behaviours)  # ⛔ صفر محاكمات: لا نموذج شُغِّل في هذا السكربت
    return {
        "artifact": "CND_MEASUREMENTS",
        "cnd_version": CND_VERSION,
        "generated_at_utc": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "generator": "scripts/research/measure_cnd_instrument.py",
        "corpus_path": str(CORPUS.relative_to(ROOT)),
        "determinism": "حتمي: لا عشوائية ولا شبكة ولا نموذج — الساعة في التقرير فقط.",
        "what_this_is_ar": (
            "قياسٌ على **الأداة وذخيرتها**: الشهادات، والتغطية، والقدرة الإحصائية، "
            "وحارس الرمز الكناري، واستقرار إعادة الإصدار."
        ),
        "what_this_is_not_ar": (
            "⛔ ليس قياساً على نموذجٍ ولا على عميل: لم يُشغَّل أيّ نموذج في هذا السكربت، "
            "فكلّ خلايا التباعد هنا صفرُ محاكمات، وأيُّ رقمٍ عن «معدّل تسريب» في وثيقةٍ "
            "تستشهد بهذا الملفّ هو كذبٌ مكشوف."
        ),
        "coverage": coverage,
        "certification_audit": certification_audit(corpus),
        "maturity_gap": maturity_gap(corpus),
        "power_curve": power_curve(),
        "break_even_unit_costs": break_even_table(),
        "canary_survival": canary_survival(corpus),
        "reissue_stability": reissue_stability(corpus),
        "empty_run_cells": {
            "cells": len(cells),
            "pairs_total": sum(cell.pairs for cell in cells),
            "flips_total": sum(cell.flips for cell in cells),
            "note_ar": "بلا محاكمات: الأزواجُ موجودة والانقلاباتُ صفر — proof of plumbing.",
        },
        "corpus_receipt": {
            "probe_count": receipt["probe_count"],
            "chain_head": receipt["chain_head"],
            "merkle_root": receipt["merkle_root"],
            "limit_ar": receipt["limit_ar"],
        },
        "verdict_ar": (
            "ثلاثُ نتائج عن الأداة وحدها: (1) ترفض ما يجب رفضه — الضابطُ السلبي مرفوضٌ كله "
            "بسبب `semantic_class_not_null`؛ (2) الرمزُ الكناري ينجو من كلِّ تحويلٍ صالح، "
            "فلا يُقاس مُحفِّزٌ بدل اللغة؛ (3) إعادةُ الإصدار برموزٍ جديدة تُعيد حساب "
            "الشهادات ولا تُغيّر درجةً واحدة. أمّا القدرةُ على الحكم فتقرأ من `maturity_gap`: "
            "التجميعُ عبر العائلات يبلغ حدّ النضج لكلّ اتجاه، أمّا **الإسنادُ إلى عائلةٍ "
            f"بعينها فلا** — دون {MIN_N_FOR_ESTIMATE} زوجاً لكلّ عائلة، والنيّاتُ المطلوبة "
            "مكتوبةٌ في الصفوف. وهذا تصريحٌ بالحدّ لا إخفاءٌ للفشل."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="قياسٌ حتمي لأداة CND وذخيرتها.")
    parser.add_argument(
        "--check",
        action="store_true",
        help="يقارن الملف المودَع بإعادة الحساب ويُفشِل عند الانحراف (بوّابة CI).",
    )
    args = parser.parse_args()

    if not CORPUS.is_file():
        print(f"❌ الذخيرة مفقودة: {CORPUS.relative_to(ROOT)}")
        return 1

    corpus = load_canary_corpus(CORPUS)
    payload = build_payload(corpus)

    if args.check:
        if not OUTPUT.is_file():
            print(f"❌ ملفّ القياس غير مودَع: {OUTPUT.relative_to(ROOT)}")
            return 1
        committed = json.loads(OUTPUT.read_text(encoding="utf-8"))
        recomputed = dict(payload)
        # طابعُ الزمن ليس جزءاً من الحساب — استثناؤه مُعلن لا مُضمَر.
        for side in (committed, recomputed):
            side.pop("generated_at_utc", None)
        if committed != recomputed:
            drifted = sorted(
                key
                for key in set(committed) | set(recomputed)
                if committed.get(key) != recomputed.get(key)
            )
            print(f"❌ ملفّ القياس منحرفٌ عن إعادة الحساب في: {drifted}")
            print("   أعد التوليد: python3 scripts/research/measure_cnd_instrument.py")
            return 1
        check_coverage: dict[str, object] = corpus_coverage(corpus)
        print(
            f"✅ CND_MEASUREMENTS.json مطابقٌ لإعادة الحساب ({check_coverage['probes']} مسباراً، "
            f"{check_coverage['rejected']} مرفوضاً كلها الضابط السلبي)."
        )
        return 0

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    # الطباعةُ من المصدر المُحوسب مباشرة: لا فهرسةُ `object` ولا تجاهلُ نوع.
    coverage: dict[str, object] = corpus_coverage(corpus)
    receipt: dict[str, object] = freeze_corpus(corpus)
    print(f"✅ كُتب ملف القياس: {OUTPUT.relative_to(ROOT)}")
    print(f"   المسابير: {coverage['probes']} · النيّات: {coverage['intents']}")
    print(f"   الأزواج: خرق={coverage['violation_pairs']} · مباح={coverage['benign_pairs']}")
    print(f"   الدرجات: {coverage['by_tier']}")
    print(f"   المرفوض وأسبابه: {coverage['rejected']} ← {coverage['rejection_reasons']}")
    print(f"   جذر ميركل للإيصال: {str(receipt['merkle_root'])[:16]}…")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
