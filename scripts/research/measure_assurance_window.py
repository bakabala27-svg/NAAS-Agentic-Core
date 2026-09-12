#!/usr/bin/env python3
"""قياسٌ حتمي على المعرفة الرابعة (AHW): كم يعيشُ رقمُ الاطمئنان، وبأيّ أفقٍ يُقاس؟

## لماذا هذا السكربت موجود

الدفعة الرابعة (AHW) تدّعي ثلاث جمل قابلة للدحض:

1. أنّ التعرّض ينمو **فوق خطّيّ** مع طول المهمة (نقطتا METR المنشورتان).
2. أنّ رقمَ الاطمئنان **يتقادم** بسرعةٍ تُقاس بالنقاط/اليوم بين إصدارَين، وباتّجاهَين
   لا باتجاهٍ واحد (فيهبوطٍ مقيس على مهمة قانونية مستقلة).
3. أنّ **دورةً تقويمية** (ربعَ سنة) لا تلتقي الانحدارات: يحلُّ إصدارٌ قبلها باحتمالٍ
   يُحسب، فتكون وحدةُ البيع حدثَ الإصدار لا السنة.

كلُّ جملةٍ منها تُحسب هنا على القرص، حتمياً، من **مدخلاتٍ مُسندةٍ بتاريخٍ ومصدر**،
وتُودَع في `docs/research/AHW_MEASUREMENTS.json`. و`--check` يُعيد الحساب ويُفشِل عند
أيّ انحرافٍ بين المودَع والمحسوب.

## ما ليس في هذا الملف

⛔ لم يُشغَّل أيُّ نموذجٍ لغوي. ⛔ لا قياسَ عميل. ⛔ لا سعرَ مُختلَق ولا رقمُ إيراد.
الأرقامُ إمّا (أ) مشتقّةٌ حتمياً من مُدخلات منشورة مُسندة، أو (ب) حدودُ تصميمٍ هندسية.
الوسم: 🟢⟨ح⟩ حتمي محسوب — مكمِّلٌ لـ(🟢 موثق · 🟡 أطروحة · 🔴 فرضية) لا بديلٌ عنها.

## الاستعمال

    python3 scripts/research/measure_assurance_window.py            # يكتب ملفّ القياس
    python3 scripts/research/measure_assurance_window.py --check    # يتحقّق من المودَع

لا يُكتب في `app/` ولا يستورد منها: الحزمة `shared.research` stdlib خالصة.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import UTC, date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from shared.research.assurance_window import (
    AssurancePoint,
    ChurnRates,
    HorizonAnchor,
    RepatriationRef,
    ReportPin,
    SuiteDrift,
    acceptance_corridor,
    adjudicate,
    curve_family,
    drift_sample_note,
    evaluate_pin,
    fit_assurance_curve,
    horizon_risk_exponent,
    pin_is_quotable,
    release_beat_probability,
    robust_terms,
    robust_warranty_days,
    summarize,
    survival_probability,
    warranty_table,
    warranty_window_days,
)

OUT = ROOT / "docs" / "research" / "AHW_MEASUREMENTS.json"

# ── مُدخلاتٌ مُسندة (كلُّ سطرٍ منها له مصدرٌ مؤرَّخ في سجلّ الادعاءات) ──────────

#: نقطتا METR (Frontier Risk Report، 2026-05-19) لمعدّل السلوك المعرِّض مقابل الأفق.
METR_LOW = HorizonAnchor(minutes=30.0, rate=0.005, label="≤30 دقيقة · ≈0.5% غشّ")
METR_HIGH = HorizonAnchor(minutes=480.0, rate=0.1667, label=">8 ساعات · >1 من 6")

#: خطُّ Anthropic Fable: 2026-06-09 → 2026-09-01 = 84 يوماً، درجاتٌ من جدول الإطلاق
#: نفسه + قياسٌ مستقلٌّ واحد (Vals AI، 2026-09-04) يوثّق **اتجاهاً هابطاً**.
CADENCE_DAYS = 84
DRIFTS: tuple[SuiteDrift, ...] = (
    SuiteDrift("Terminal-Bench-Science 0.1", 24.7, 52.6, CADENCE_DAYS),
    SuiteDrift("Terminal-Bench 4.0", 42.0, 55.8, CADENCE_DAYS),
    SuiteDrift("AutomationBench", 17.1, 31.4, CADENCE_DAYS),
    SuiteDrift("OSWorld 2.0 (partial)", 72.9, 77.9, CADENCE_DAYS),
    SuiteDrift("Humanity's Last Exam (no tools)", 57.8, 60.9, CADENCE_DAYS),
    SuiteDrift("CursorBench 3.2.0", 70.5, 73.4, CADENCE_DAYS),
    SuiteDrift("Harvey Legal Agent Benchmark (مستقل)", 11.25, 6.67, CADENCE_DAYS),
)

#: MonitoringBench (arXiv 2605.09684، مايو 2026): معدّل التقاطٍ عند ميزانيتَي مهاجم.
BASE_ATTACK = AssurancePoint(budget=0, assurance=0.949, label="هجماتٌ مُستدعاةٌ من النموذج")
REFINED_ATTACK = AssurancePoint(budget=4783, assurance=0.603, label="أفضل الهجمات المُصقولة")

#: الدورةُ التقويمية المُفتَرَضة اليوم في أدبيات «تقرير الجاهزية» (90 يوماً).
CAL_CYCLE_DAYS = 90.0
TOLERANCE_POINTS = 5.0
THETA = 0.9

#: مرجعا الترحيل — **لا يُحسم** أيُّهما؛ يُبنى قيدُ العقد على بقائه تحت الاثنين معاً.
FX_REFS: tuple[RepatriationRef, ...] = (
    RepatriationRef(
        name="نظامُ 16-04 م61 (المرجع المُعتمَد في العقيدة)",
        repatriation_days=306,
        credit_ceiling_days=360,
        status="documented-official",
    ),
    RepatriationRef(
        name="تنظيمُ بنك الجزائر المُبلَّغ صحفياً 2026-08-20",
        repatriation_days=120,
        credit_ceiling_days=180,
        status="press-reported-awaiting-official-text",
    ),
)
FX_TERMS: tuple[int, ...] = (30, 45, 60, 90, 120, 180, 270)

#: ── حدثُ 2026-09-08 (Navier–Stokes) مُسندٌ بتاريخٍ لا بتذكُّر ────────────────────
#: الإعلانُ يومَ الثلاثاء 2026-09-08؛ الوصولُ إلى النتيجة 2026-09-05 بعد ≈88 ساعةٍ من
#: انطلاقِ الجهد (2026-09-01)؛ formalization + تحققٌ في Lean خلال 17 ساعةً إضافية عبر
#: GPT-6 Astra؛ اكتمالُ المشروعِ والتحقّق 2026-09-06؛ عبارةُ المسألة صيغت بتكييفٍ من
#: مستودع Formal Conjectures (Google DeepMind)؛ سلسلةُ الأدوات `lean 4.34.0-rc2`؛
#: ولا قائمةَ مُدقِّقين مستقلّين منشورة، والمنفذُ ليس مجلةً محكَّمة.
NS_ANNOUNCED_ON = date(2026, 9, 8)
NS_SOLVED_ON = date(2026, 9, 5)
NS_LEAN_HOURS = 17
NS_SOLVE_HOURS = 88
NS_TOOLCHAIN = "lean 4.34.0-rc2"
NS_QUALIFYING_OUTLET = False  # مدوَّنة + PDF + مستودع Lean — لا منفذٌ مؤهَّل عند كلاي

#: تاريخُ مصدرِ S48 الذي بنى عليه سجلُّنا عبارةَ «⛔ لا مسائل الألفية»، وتاريخُ كتابة
#: السجلّ — الفارقُ بينهما هو ما دحضَ سجلَّنا **قبل** أن يُكتب.
LEDGER_SOURCE_ON = date(2026, 8, 1)
LEDGER_WRITTEN_ON = date(2026, 9, 12)


def _shelf_window_days(churn: ChurnRates) -> float:
    """أفقُ صلاحية **ادّعاءٍ وثائقي** = أفقُ بقاءِ الرقم تحت زحزحةِ التكوين (بلا v مُختلَقة)."""
    window = warranty_window_days(churn, THETA)
    if window is None:
        raise AssertionError("لا نافذةَ بمخاطر صفرية — راجع ChurnRates")
    return window


def _adjudication_cases() -> list[dict[str, object]]:
    """الحالتان اللتان تُعلِّمانا أكثرَ من غيرهما: رقمٌ طازجٌ لا يُقتبس، وادّعاءٌ قديمٌ دحضه حدثٌ أنكره."""
    churn = ChurnRates.from_cadences(release_cadence_days=float(CADENCE_DAYS))
    window = _shelf_window_days(churn)

    # (أ) الإعلانُ نفسه كما كان سيُدرَج في عرضٍ بيعي بعد أربعة أيام
    announcement = ReportPin(
        model_id="openai-internal-post-astra",
        harness="navier-stokes-lean@f9e8bc5",
        safeguard_config="vendor-monitored",
        suite_version="clay-C-and-D(forced)",
        adversary_budget=0,
        issued_on=NS_ANNOUNCED_ON,
        suite="Millennium-NS/Lean",
        notes=("⛔ لم نُشغِّل المُدقِّق؛ لم نقرأ الـ165 صفحة",),
    )
    ann_status = evaluate_pin(announcement, LEDGER_WRITTEN_ON, churn=churn, theta=THETA)
    ann_adjud = adjudicate(
        "VENDOR_ONLY",
        "CONTESTED_PRIORITY",
        scope_source="THIRD_PARTY",
        toolchain=NS_TOOLCHAIN,
        verified_by=(),
    )

    # (ب) صفُّ A3 من سجلِّنا، مُدبَّساً بمصدره ومؤرَّخاً بيوم كتابته
    self_claim = ReportPin(
        model_id="claim:A3",
        harness="FRONTIER_CLAIM_LEDGER_2026-09.md",
        safeguard_config="single-source-no-sweep",
        suite_version="S48@2026-08-01",
        adversary_budget=0,
        issued_on=LEDGER_SOURCE_ON,
        suite="literature-claim",
        notes=("الحكمُ المنسوبُ للمصدر: «⛔ لا مسائل الألفية»",),
    )
    self_status = evaluate_pin(self_claim, LEDGER_WRITTEN_ON, churn=churn, theta=THETA)
    self_adjud = adjudicate("UNSTATED", scope_source="SELF", toolchain="")

    rows: list[dict[str, object]] = []
    for label, status, adjud, extra in (
        (
            "إعلانُ 2026-09-08 بعد 4 أيام — القِدَمُ يسمح، الاستقلالُ يمنع",
            ann_status,
            ann_adjud,
            {
                "lean_hours_after_solve": NS_LEAN_HOURS,
                "solve_hours": NS_SOLVE_HOURS,
                "solved_on": NS_SOLVED_ON.isoformat(),
                "announced_on": NS_ANNOUNCED_ON.isoformat(),
                "scope_source": "THIRD_PARTY",
                "toolchain": NS_TOOLCHAIN,
            },
        ),
        (
            "صفُّ A3 من سجلِّنا عند كتابته — المصدرُ أسبقُ 42 يوماً والحادثُ الداحضُ أسبقُ 4",
            self_status,
            self_adjud,
            {
                "source_age_days_at_write": (LEDGER_WRITTEN_ON - LEDGER_SOURCE_ON).days,
                "refuting_event_predated_write_days": (LEDGER_WRITTEN_ON - NS_ANNOUNCED_ON).days,
                "scope_source": "SELF",
            },
        ),
    ):
        rows.append(
            {
                "case": label,
                "age_state": status.state,
                "age_state_label": status.label,
                "age_days": status.age_days,
                "shelf_window_days": round(window, 2),
                "ceiling": adjud.ceiling,
                "quotable_by_age": status.quotable,
                "quotable_final": pin_is_quotable(status, adjud),
                "reasons": list(adjud.reasons),
                "notes": list(adjud.notes),
                **extra,
            }
        )
    return rows


def _corridor_block() -> dict[str, object]:
    """كم يوماً يبقى البرهانُ «غيرَ قابلٍ للشراء»؟ حسابٌ من نصِّ قواعد كلاي، لا تنبّؤ."""
    as_filed = acceptance_corridor(
        NS_ANNOUNCED_ON, LEDGER_WRITTEN_ON, qualifying_outlet=NS_QUALIFYING_OUTLET
    )
    as_if_published = acceptance_corridor(
        NS_ANNOUNCED_ON, LEDGER_WRITTEN_ON, qualifying_outlet=True
    )
    return {
        "clock_started_as_filed": as_filed.clock_started,
        "earliest_eligible_if_published_on_announcement_day": (
            None
            if as_if_published.earliest_eligible_on is None
            else as_if_published.earliest_eligible_on.isoformat()
        ),
        "corridor_days_if_published": as_if_published.corridor_days,
        "elapsed_days": as_if_published.elapsed_days,
        "remaining_days": as_if_published.remaining_days,
        "fraction_elapsed": as_if_published.fraction_elapsed,
        "reading": "الممرُّ 731 يوماً من «برهانٍ موجودٍ ولا يُشترى»، **و** العدُّ لم يبدأ لأنّ النشرَ لم "
        "يكن في منفذٍ مؤهَّل. القيمةُ التي تُباع ليست البرهانَ بل **ما يحدث داخل الممرّ**: قياسٌ "
        "مُفعَّلٌ بالحدث يُبقي ادّعاءَ العميل صحيحاً أثناء انتظار القبول",
    }


def build() -> dict[str, object]:
    """يبني ملفَّ القياس كلَّه — دالٌّ صافٍ: لا قراءةَ وقتٍ ولا شبكةَ ولا نموذج."""
    churn = ChurnRates.from_cadences(release_cadence_days=float(CADENCE_DAYS))
    summary = summarize(
        low=METR_LOW,
        high=METR_HIGH,
        ratio=16.0,
        drifts=DRIFTS,
        churn=churn,
        cycle_days=CAL_CYCLE_DAYS,
        release_cadence_days=float(CADENCE_DAYS),
        tolerance_points=TOLERANCE_POINTS,
        theta=THETA,
    )
    eps = horizon_risk_exponent(METR_LOW, METR_HIGH)
    table = warranty_table(DRIFTS, tolerances=(2.0, 5.0, 10.0))
    tbs = next(row for row in table if row["suite"] == "Terminal-Bench-Science 0.1")
    harvey = next(row for row in table if row["suite"].startswith("Harvey"))
    robust_tbs = robust_warranty_days(
        SuiteDrift(
            "Terminal-Bench-Science 0.1",
            24.7,
            52.6,
            CADENCE_DAYS,
        ),
        TOLERANCE_POINTS,
        churn,
        THETA,
    )
    family = curve_family(BASE_ATTACK, REFINED_ATTACK)
    curve = fit_assurance_curve(BASE_ATTACK, REFINED_ATTACK, b0=1.0)
    beat = release_beat_probability(CAL_CYCLE_DAYS, float(CADENCE_DAYS))
    pins = _pin_cases()
    return {
        "kind": "assurance-horizon-warranty-measurement",
        "as_of": "2026-09-12",
        "method": "حتميٌّ بالكامل (stdlib) — لا نموذج، لا شبِكة، لا قياسَ عميل",
        "model_runs_executed": 0,
        "client_measurements": 0,
        "revenue_claim": "NONE — لا إيرادَ ولا عميلَ ولا دفعة",
        "inputs": {
            "horizon_anchors": [
                {
                    "minutes": a.minutes,
                    "rate": a.rate,
                    "label": a.label,
                    "source": "METR Frontier Risk Report، 2026-05-19 (عبر وصفٍ ثانوي "
                    "مؤرَّخ — يُعاد التحقق من النصّ الأصلي قبل أيّ استعمالٍ في عرضٍ بيعي)",
                }
                for a in (METR_LOW, METR_HIGH)
            ],
            "drift_pairs": [
                {
                    "suite": d.suite,
                    "before": d.before,
                    "after": d.after,
                    "days": d.days,
                    "source": "جدولُ إطلاق Claude Fable 5.1 (2026-09-01) وما قابله من "
                    "Claude Fable 5 (2026-06-09)؛ القياسُ المستقلُّ من Vals AI (2026-09-04)",
                }
                for d in DRIFTS
            ],
            "adversary_budget_points": [
                {
                    "budget": p.budget,
                    "assurance": p.assurance,
                    "label": p.label,
                    "source": "MonitoringBench (arXiv:2605.09684، مايو 2026) — 4,783 محاولة "
                    "تصعيد، و83.78% من المحاولات نجحت في مهمةٍ جانبية بعد التصعيد",
                }
                for p in (BASE_ATTACK, REFINED_ATTACK)
            ],
            "frontier_event": [
                {
                    "event": "إعلانُ OpenAI عن حلِّ مسألة Navier–Stokes existence and smoothness",
                    "announced_on": NS_ANNOUNCED_ON.isoformat(),
                    "provenance": "منشورُ الصانع + PDF + مستودع Lean عامّ؛ بيانُ أسبقيةٍ مضادٍّ قبل 12 ساعة",
                    "source": "openai.com/index/navier-stokes-solution/ · "
                    "github.com/openai/NavierStokesAndEuler · "
                    "en.wikipedia.org/wiki/Navier%E2%80%93Stokes_priority_controversy",
                },
                {
                    "event": "قواعدُ جائزة الألفية: منفذٌ مؤهَّل + عامّان + قبولٌ عامّ، ولا استلامَ مشاركةٍ مباشرة",
                    "source": "claymath.org/millennium-problems/rules/ (قواعدُ 2018-09-26) و"
                    "claymath.org/millennium/navier-stokes-equation/ (الحالة: Active)",
                },
            ],
            "ledger_self_audit_dates": {
                "ledger_source_on": LEDGER_SOURCE_ON.isoformat(),
                "ledger_written_on": LEDGER_WRITTEN_ON.isoformat(),
                "note": "الفارقُ بين تاريخِ المصدر وتاريخِ الكتابة هو عمرُ الادّعاء عند النشر؛ "
                "الفارقُ بين الحادثِ الداحض وتاريخِ الكتابة هو كم كان المسحُ متأخّراً",
            },
            "regulatory_references": [
                {
                    "name": ref.name,
                    "repatriation_days": ref.repatriation_days,
                    "credit_ceiling_days": ref.credit_ceiling_days,
                    "status": ref.status,
                }
                for ref in FX_REFS
            ],
        },
        "results": {
            "horizon": {
                "risk_exponent": round(eps, 6),
                "reading": "ε > 1 ⇒ التعرّضُ ينمو فوق خطّيٍّ مع الأفق؛ لا يُقال «المرونة "
                "العالمية»، بل «ما تُنتجه نقطتاُ الإسناد هاتان»",
                "exposure_bands": summary["horizon_bands"],
            },
            "depreciation": {
                "suite_count": len(table),
                "warranty_table": table,
                "sample_note": drift_sample_note(DRIFTS),
                "shortest_warranty_days_at_2pts": tbs["warranty_days_at_2pts"],
                "harvey_warranty_days_at_2pts": harvey["warranty_days_at_2pts"],
                "robust_warranty_days_most_volatile_at_5pts": (
                    None if robust_tbs is None else round(robust_tbs, 2)
                ),
                "survival_of_quarterly_report_pct": round(
                    _survival(churn, CAL_CYCLE_DAYS) * 100.0, 2
                ),
            },
            "adversary_budget": {
                "forms_note": "نقطتان لا تحدّدان المنحنى؛ B₀ مُدخَلٌ تصميميٌّ معلن، "
                "والثابتُ بينهما هو الأثرُ عند الميزانية المقيسة",
                "attempts_per_point_b0_1": round(curve.attempts_per_point(), 2),
                "points_per_doubling_b0_1": round(curve.points_per_doubling_asymptote(), 4),
                "budget_for_minus_10pts_b0_1": curve.budget_for_target(curve.a0 - 0.10),
                "reading_curve": "الشكلُ اللوغاريتمي لا يشبع: كلُّ مضاعفةٍ لميزانية الخصم "
                "تكلّف ≈2.83 نقطة التقاط (عند B₀=1). لذلك ⛔ لا يُباع «رقمٌ مضمون» بميزانيةٍ "
                "أكبر — يُباع (A,B) معاً ويُعاد القياسُ عند تغيّر B المتاح للخصم",
                "family": family,
            },
            "billing_unit": {
                "release_beat_probability_per_quarter": round(beat, 4),
                "reading": "⛔ تقريرٌ ربعُ سنوي يفوته إصدارٌ جديد في ≈"
                f"{round(beat * 100.0, 1)}% من الأرباع — الفوترةُ على حدث الإصدار، لا على السنة",
                "eval_events_per_year_at_measured_cadence": summary["eval_events_per_year"],
                "detection_lag_days": summary["detection_lag_days"],
                "drift_before_detection_points": summary["drift_before_detection"],
            },
            "contract_terms": {
                "min_buffer_days": 30,
                "rows": robust_terms(FX_TERMS, FX_REFS, min_buffer_days=30),
                "reading": "مجموعةُ الآجال التي تنجو تحت **كل** مرجع مُسند مع هامش "
                "تأخير ≥30 يوماً؛ ⛔ لا يُحسم أيُّ نصٍّ تنظيمي هنا — الحسمُ للجريدة الرسمية",
            },
            "pin_status_cases": pins,
            "adjudication_cases": _adjudication_cases(),
            "acceptance_corridor": _corridor_block(),
        },
        "boundaries": {
            "not_claimed": [
                "لا قياسَ عميلٍ ولا تشغيلَ نموذج — المدخلاتُ منشورةٌ لا مقيسةٌ عندنا",
                "لا سعرَ ولا إيرادَ ولا «ضمان» — ⛔ عبارةُ الضمان ممنوعةٌ دستورياً (L3)",
                "سرعةُ التقادم خاصةٌ بالحزمة بين إصدارَين محدّدَين؛ نقلُها إلى حزمةٍ أخرى غيرُ مبرَّر",
                "ε محسوبةٌ من نقطتَين؛ لا تُستعمل تنبّؤاً خارج [30 دقيقة، 8 ساعات]",
                "مرجعُ الترحيل الأقصر **مُبلَّغٌ صحفياً** ولم يُحسم من الجريدة الرسمية؛ العقيدة لم تُعدَّل",
            ],
            "reverification_triggers": [
                "إصدارُ نموذجٍ جديد على الخطِّ المفحوص (يلغي n-warranty المقيس)",
                "تغيّرُ إصدار الحزمة المعيارية أو تكليفُها (churn حزمٍ لا churn نماذج)",
                "نشرُ JORADP نصَّ تنظيمِ الترحيل 2026 (يُغلِق D-282 أو يُثبِّت التعارض)",
                "أيُّ عرضٍ بيعيٍّ يقتبس رقماً من هذا الملف بلا دبوسٍ من `pin_status_cases`",
                "انتهاءُ الممرِّ الرسميِّ (2028-09-08 إن بدأ العدُّ) أو صدورُ بيانٍ من Clay عن الحالة",
                "أيُّ بيانٍ مُوقَّعٍ من مُدقِّقٍ مستقلٍّ خارج الصانع يُغيّر `ceiling` من THROTTLE",
                "كلُّ مسحٍ أدبيٍّ يُكتب في سجلِّ الادعاءات: إن تجاوز عمرُهُ `shelf_window_days` "
                "عند الكتابة فالحكمُ يُكتب `STALE` لا `🟢`",
            ],
        },
    }


def _survival(churn: ChurnRates, days: float) -> float:
    """`exp(−λt)` — احتماءُ بقاء الرقم المقتبس داخل السعة."""
    return survival_probability(churn, days)


def _pin_cases() -> list[dict[str, object]]:
    """ثلاثُ حالات دبوسٍ قياسية — تُستعمل في الاختبارات وفي نصّ العرض معاً."""
    cases: list[dict[str, object]] = []
    tbs = SuiteDrift("Terminal-Bench-Science 0.1", 24.7, 52.6, CADENCE_DAYS)
    churn = ChurnRates.from_cadences(release_cadence_days=float(CADENCE_DAYS))
    fresh = ReportPin(
        model_id="claude-fable-5-1",
        harness="terminal-bench-4.0@pin-a",
        safeguard_config="GA-classifiers",
        suite_version="0.1",
        adversary_budget=0,
        issued_on=date(2026, 9, 1),
        suite="Terminal-Bench-Science 0.1",
        score_points=52.6,
    )
    aged = ReportPin(
        model_id="claude-fable-5",
        harness="terminal-bench-4.0@pin-a",
        safeguard_config="GA-classifiers",
        suite_version="0.1",
        adversary_budget=0,
        issued_on=date(2026, 6, 9),
        suite="Terminal-Bench-Science 0.1",
        score_points=24.7,
    )
    unpinned = ReportPin(
        model_id="some-model",
        harness="",
        safeguard_config="",
        suite_version="",
        adversary_budget=None,
        issued_on=date(2026, 9, 1),
    )
    for label, pin, as_of in (
        ("تقريرٌ صدر يومَ الإطلاق، قُوبل في اليوم نفسه", fresh, date(2026, 9, 1)),
        ("تقريرٌ على Fable 5 قُدّم بعد 84 يوماً (دورةٌ ربعُ سنوية)", aged, date(2026, 9, 1)),
        ("تقريرٌ بلا مِصْمَلٍ ولا ميزانية مهاجم", unpinned, date(2026, 9, 1)),
    ):
        status = evaluate_pin(
            pin,
            as_of,
            drift=tbs,
            tolerance_points=TOLERANCE_POINTS,
            churn=churn,
            theta=THETA,
        )
        cases.append(
            {
                "case": label,
                "state": status.state,
                "state_label": status.label,
                "quotable": status.quotable,
                "age_days": status.age_days,
                "warranty_days": status.window_days,
                "missing_fields": list(status.missing),
            }
        )
    return cases


def _canonical_digest(payload: dict[str, object]) -> str:
    """بصمةُ المدخلات (تُعلَّق في أيّ عرضٍ يقتبس رقماً من هنا)."""
    encoded = json.dumps(payload["inputs"], ensure_ascii=False, sort_keys=True).encode()
    return hashlib.sha256(encoded).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__ or "")
    parser.add_argument(
        "--check", action="store_true", help="يقارن المودَع بالمحسوب ويفشل عند الانحراف"
    )
    args = parser.parse_args()

    payload = build()
    payload["generated_at"] = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    payload["inputs_digest_sha256"] = _canonical_digest(payload)

    if args.check:
        if not OUT.is_file():
            print("❌ measure_assurance_window: ملفُ القياس غير موجود", file=sys.stderr)
            return 1
        stored = json.loads(OUT.read_text(encoding="utf-8"))
        for key in ("kind", "as_of", "inputs_digest_sha256"):
            if stored.get(key) != payload.get(key):
                print(
                    f"❌ انحراف في {key}: {stored.get(key)!r} ≠ {payload.get(key)!r}",
                    file=sys.stderr,
                )
                return 1
        if stored.get("results") != payload["results"]:
            print(
                "❌ انحرافٌ في الأرقام المحسوبة — أُعيد توليدُ الملفّ أو صحّح المدخلات", file=sys.stderr
            )
            return 1
        print("measure_assurance_window --check: PASS")
        return 0

    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"measure_assurance_window: كُتب {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
