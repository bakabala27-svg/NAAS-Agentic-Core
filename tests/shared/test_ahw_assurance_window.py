"""اختبارات AHW — نافذةُ صلاحية الضمان (الأفق · ميزانية الخصم · التقادم · الأجل).

تُثبت هذه الاختبارات أربعَ جملٍ حسابية، لا أربعَ رغبات:

1. **الأفق**: مرونةُ التعرّض تُحسب من نقطتَي إسناد، وتُرفَض المدخلاتُ التي لا تُنتج
   مرونةً موجَّهة — فلا «نموذج عالمي» مبطَّن في الدالة.
2. **ميزانية الخصم**: المنحنى يُعيد إنتاج نقطتَي الإسناد حرفياً، ⛔ لا extrapolation
   خارج السقف، والشكلُ اللوغاريتمي لا يشبع — لذلك لا يباع «رقمٌ أعلى» بميزانيةٍ أكبر.
3. **التقادم**: سرعةُ النقاط/اليوم خاصةٌ بحزمتها، والنافذةُ الصلبة هي **أصغرُ** الحدين،
   والدورةُ التقويمية تفوت الإصدارَ باحتمالٍ يُحسب لا يُروى.
4. **الأجلُ والتنابيد**: مجموعةُ آجالٍ تنجو تحت **كل** مرجعٍ مُسند مع هامشٍ أدنى معلَن،
   ودبوسُ التقرير يرفض الاقتباسَ إذا نقصَ حقلٌ أو انتهت نافذتُه.

وأخيراً: ملفُّ القياس المودَع **يطابق المحسوب** — وهو الحارسُ الذي يمنع انحراف الرقم
في الوثيقة التجارية عن الرقم في الكود (درسُ D-266: الفارضُ يضمّن عدمَ إمكان فكّ أسلاكه).
"""

from __future__ import annotations

import ast
import json
import math
import sys
from datetime import date, timedelta
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.research.measure_assurance_window import build  # noqa: E402
from shared.research.assurance_window import (  # noqa: E402
    AssurancePoint,
    AssuranceWindowError,
    ChurnRates,
    HorizonAnchor,
    MIN_TOLERANCE_POINTS,
    RepatriationRef,
    ReportPin,
    SuiteDrift,
    budget_is_stated,
    buffer_days,
    curve_family,
    detection_lag_days,
    drift_before_detection,
    drift_sample_note,
    drift_velocity,
    evaluate_pin,
    events_per_year,
    fit_assurance_curve,
    horizon_band_flags,
    horizon_exposure_multiplier,
    horizon_risk_exponent,
    legal_term_ceiling,
    release_beat_probability,
    require_horizon_band,
    robust_terms,
    robust_warranty_days,
    survival_probability,
    summarize,
    term_survives,
    warranty_days,
    warranty_table,
    warranty_window_days,
)

# ── أدواتُ اختبارٍ مشتركة ───────────────────────────────────────────────────────

LOW = HorizonAnchor(minutes=30.0, rate=0.005)
HIGH = HorizonAnchor(minutes=480.0, rate=0.1667)
TBS = SuiteDrift("Terminal-Bench-Science 0.1", 24.7, 52.6, 84)
HARVEY = SuiteDrift("Harvey Legal Agent Benchmark", 11.25, 6.67, 84)


# ── 1) HRE — أُسّ الأفق ─────────────────────────────────────────────────────────


def test_horizon_exponent_matches_hand_computation() -> None:
    eps = horizon_risk_exponent(LOW, HIGH)
    expected = math.log(0.1667 / 0.005) / math.log(480.0 / 30.0)
    assert eps == pytest.approx(expected, rel=1e-12)
    assert eps > 1.0  # فوق خطّي — هذه هي الجملةُ القابلة للدحض


def test_horizon_exponent_is_superlinear_by_construction() -> None:
    eps = horizon_risk_exponent(LOW, HIGH)
    assert horizon_exposure_multiplier(eps, 8.0) > 8.0


def test_horizon_exponent_accepts_swapped_input_order() -> None:
    assert horizon_risk_exponent(HIGH, LOW) == pytest.approx(horizon_risk_exponent(LOW, HIGH))


def test_horizon_exponent_rejects_identical_horizons() -> None:
    with pytest.raises(AssuranceWindowError):
        horizon_risk_exponent(HorizonAnchor(60.0, 0.01), HorizonAnchor(60.0, 0.2))


def test_horizon_exponent_rejects_contradictory_direction() -> None:
    # معدّلٌ أعلى عند أفقٍ أقصر ⇒ لا مرونة؛ الرفضُ لا الصفر
    with pytest.raises(AssuranceWindowError):
        horizon_risk_exponent(HorizonAnchor(480.0, 0.005), HorizonAnchor(30.0, 0.2))


@pytest.mark.parametrize("rate", [0.0, 1.0, 1.5, -0.2])
def test_horizon_anchor_rejects_rates_outside_unit_interval(rate: float) -> None:
    with pytest.raises(AssuranceWindowError):
        HorizonAnchor(minutes=60.0, rate=rate)


def test_horizon_anchor_rejects_nonpositive_horizon() -> None:
    with pytest.raises(AssuranceWindowError):
        HorizonAnchor(minutes=0.0, rate=0.01)


def test_horizon_bands_are_labelled_and_monotone() -> None:
    bands = horizon_band_flags(horizon_risk_exponent(LOW, HIGH), (2.0, 4.0, 8.0, 16.0))
    values = [bands[key] for key in ("x2", "x4", "x8", "x16")]
    assert values == sorted(values)
    assert bands["x16"] == pytest.approx(math.exp(horizon_risk_exponent(LOW, HIGH) * math.log(16)), abs=1e-3)


def test_exposure_ratio_must_be_positive() -> None:
    with pytest.raises(AssuranceWindowError):
        horizon_exposure_multiplier(1.2, 0.0)


@pytest.mark.parametrize("band", [None, "", "   "])
def test_require_horizon_band_rejects_silence(band: str | None) -> None:
    with pytest.raises(AssuranceWindowError):
        require_horizon_band(band)


def test_require_horizon_band_accepts_named_band() -> None:
    require_horizon_band("1h-8h")


# ── 2) ABAC — ميزانيةُ المهاجم ─────────────────────────────────────────────────


def test_curve_reproduces_both_anchor_points_exactly() -> None:
    curve = fit_assurance_curve(AssurancePoint(0, 0.949), AssurancePoint(4783, 0.603), b0=1.0)
    assert curve.assurance_at(0) == pytest.approx(0.949)
    assert curve.assurance_at(4783) == pytest.approx(0.603)


def test_curve_is_monotone_decreasing_over_supported_range() -> None:
    curve = fit_assurance_curve(AssurancePoint(0, 0.949), AssurancePoint(4783, 0.603), b0=1.0)
    values = [curve.assurance_at(b) for b in (0, 100, 1000, 4000, 4783)]
    floats = [float(v) for v in values if v is not None]
    assert floats == sorted(floats, reverse=True)


def test_curve_refuses_to_extrapolate_beyond_ceiling() -> None:
    curve = fit_assurance_curve(AssurancePoint(0, 0.949), AssurancePoint(4783, 0.603))
    assert curve.assurance_at(4784) is None
    assert curve.assurance_at(-1) is None


def test_attempts_per_point_equals_budget_over_measured_drop() -> None:
    curve = fit_assurance_curve(AssurancePoint(0, 0.949), AssurancePoint(4783, 0.603), b0=1.0)
    assert curve.attempts_per_point() == pytest.approx(4783.0 / 34.6, rel=1e-9)


def test_log_form_never_saturates_per_doubling() -> None:
    curve = fit_assurance_curve(AssurancePoint(0, 0.949), AssurancePoint(4783, 0.603), b0=1.0)
    asymptote = curve.points_per_doubling_asymptote() / 100.0
    measured = curve.marginal_per_doubling(400)
    assert measured is not None
    assert measured == pytest.approx(asymptote, rel=1e-2)
    # وكلُّ مضاعفةٍ تليها تكلّف المثل: لا «تشبّع» يُشترى بميزانيةٍ أكبر
    later = curve.marginal_per_doubling(800)
    assert later is not None and later >= measured - 1e-9


def test_marginal_at_zero_is_measured_from_scale_unit_not_from_zero() -> None:
    curve = fit_assurance_curve(AssurancePoint(0, 0.949), AssurancePoint(4783, 0.603), b0=10.0)
    at_zero = curve.marginal_per_doubling(0)
    assert at_zero is not None
    assert at_zero == pytest.approx((curve.assurance_at(10) or 0.0) - (curve.assurance_at(20) or 0.0))


def test_marginal_outside_supported_range_is_none_not_zero() -> None:
    curve = fit_assurance_curve(AssurancePoint(0, 0.949), AssurancePoint(4783, 0.603), b0=100.0)
    assert curve.marginal_per_doubling(4000) is None  # 8000 > سقفُ الإسناد


def test_budget_for_target_respects_ceilings_and_targets() -> None:
    curve = fit_assurance_curve(AssurancePoint(0, 0.949), AssurancePoint(4783, 0.603), b0=1.0)
    assert curve.budget_for_target(0.949) is None  # لا هبوط ⇒ لا جواب
    assert curve.budget_for_target(0.99) is None  # هدفٌ فوق الأساس
    assert curve.budget_for_target(0.1) is None  # يتطلب ميزانيةً فوق سقف الإسناد
    inside = curve.budget_for_target(0.899)
    assert inside is not None and inside <= 4783


def test_fit_rejects_non_monotone_or_non_increasing_budget() -> None:
    with pytest.raises(AssuranceWindowError):
        fit_assurance_curve(AssurancePoint(0, 0.603), AssurancePoint(4783, 0.949))
    with pytest.raises(AssuranceWindowError):
        fit_assurance_curve(AssurancePoint(100, 0.949), AssurancePoint(50, 0.603))
    with pytest.raises(AssuranceWindowError):
        fit_assurance_curve(AssurancePoint(0, 0.949), AssurancePoint(4783, 0.603), b0=0.0)


@pytest.mark.parametrize("budget,assurance", [(-5, 0.5), (0, 0.0), (0, 1.5)])
def test_assurance_point_validation_is_strict(budget: int, assurance: float) -> None:
    with pytest.raises(AssuranceWindowError):
        AssurancePoint(budget=budget, assurance=assurance)


def test_curve_family_keeps_the_measured_effect_and_varies_the_form() -> None:
    rows = curve_family(AssurancePoint(0, 0.949), AssurancePoint(4783, 0.603))
    assert len(rows) == 4
    for row in rows:
        assert row["attempts_per_point"] == pytest.approx(138.24)
    for row in rows:
        assert row["kappa_points_per_log10"] > 0
        assert row["budget_for_minus_10pts"] is None or isinstance(
            row["budget_for_minus_10pts"], int
        )


def test_missing_adversary_budget_flag_detects_unfalsifiable_numbers() -> None:
    assert budget_is_stated({"catch_rate": 0.949, "adversary_budget": 0}) is True
    assert budget_is_stated({"catch_rate": 0.949}) is False
    assert budget_is_stated({"catch_rate": 0.949, "adversary_budget": None}) is False
    assert budget_is_stated({"catch_rate": 0.949, "refinement_attempts": 4783}) is True


# ── 3) AWW — التقادمُ والمخاطرُ المتزاحمة ───────────────────────────────────────


def test_drift_velocity_uses_absolute_points_per_day() -> None:
    assert drift_velocity(TBS) == pytest.approx(27.9 / 84.0)
    assert drift_velocity(HARVEY) == pytest.approx(4.58 / 84.0)


def test_drift_direction_exposes_the_regression() -> None:
    assert TBS.direction == "up"
    assert HARVEY.direction == "down"
    assert SuiteDrift("flat", 10.0, 10.0, 30).direction == "flat"


@pytest.mark.parametrize("before,after", [(-1.0, 5.0), (5.0, 101.0)])
def test_suite_drift_rejects_out_of_band_scores(before: float, after: float) -> None:
    with pytest.raises(AssuranceWindowError):
        SuiteDrift("bad", before, after, 84)


def test_suite_drift_requires_positive_gap_and_named_suite() -> None:
    with pytest.raises(AssuranceWindowError):
        SuiteDrift("x", 1.0, 2.0, 0)
    with pytest.raises(AssuranceWindowError):
        SuiteDrift("   ", 1.0, 2.0, 30)


def test_warranty_days_closed_form_and_maturity_rules() -> None:
    v = drift_velocity(TBS)
    assert warranty_days(v, 2.0) == pytest.approx(2.0 / v)
    assert warranty_days(0.0, 5.0) is None  # ⛔ الصفرُ لا يُقرأ مهلةً لا نهائية


@pytest.mark.parametrize("tol", [0.0, 0.4, -1.0])
def test_warranty_days_rejects_silently_tiny_tolerances(tol: float) -> None:
    with pytest.raises(AssuranceWindowError):
        warranty_days(0.3, tol)


def test_minimum_tolerance_constant_is_enforced_in_code_not_prose() -> None:
    assert MIN_TOLERANCE_POINTS == 0.5
    assert warranty_days(0.3, MIN_TOLERANCE_POINTS) is not None


def test_warranty_table_reports_direction_and_all_tolerances() -> None:
    rows = warranty_table((TBS, HARVEY), tolerances=(2.0, 5.0))
    assert len(rows) == 2
    for row in rows:
        assert row["direction"] in {"up", "down", "flat"}
        assert row["warranty_days_at_2pts"] is not None
        assert row["warranty_days_at_5pts"] is not None
        assert float(row["warranty_days_at_5pts"]) > float(row["warranty_days_at_2pts"])


def test_sample_note_counts_regressions_instead_of_narrating_them() -> None:
    note = drift_sample_note((TBS, HARVEY, SuiteDrift("flat-suite", 5.0, 5.0, 84)))
    assert note["suites"] == 3
    assert note["downward_suites"] == ["Harvey Legal Agent Benchmark"]
    assert note["flat_suites"] == ["flat-suite"]
    assert note["sample_adequate"] is True


def test_sample_note_flags_undersized_evidence() -> None:
    note = drift_sample_note((TBS,))
    assert note["sample_adequate"] is False


def test_churn_from_cadence_is_exactly_the_inverse() -> None:
    churn = ChurnRates.from_cadences(release_cadence_days=84.0)
    assert churn.release_per_day == pytest.approx(1.0 / 84.0)
    assert churn.suite_change_per_day == 0.0  # مجهول ⇒ صفرٌ مسمّى، لا تخمين
    assert churn.total() == pytest.approx(1.0 / 84.0)


@pytest.mark.parametrize("cadence", [0.0, -10.0])
def test_churn_rejects_nonpositive_cadences(cadence: float) -> None:
    with pytest.raises(AssuranceWindowError):
        ChurnRates.from_cadences(release_cadence_days=cadence)


def test_warranty_window_is_theta_over_lambda() -> None:
    churn = ChurnRates.from_cadences(release_cadence_days=84.0)
    assert warranty_window_days(churn, 0.9) == pytest.approx(math.log(1 / 0.9) / (1 / 84.0))
    assert warranty_window_days(churn, 0.5) == pytest.approx(math.log(2.0) / (1 / 84.0))
    assert warranty_window_days(ChurnRates(), 0.9) is None  # لا مُدخَل ⇒ لا نافذة


@pytest.mark.parametrize("theta", [0.0, 1.0, 1.4])
def test_warranty_window_rejects_bad_theta(theta: float) -> None:
    with pytest.raises(AssuranceWindowError):
        warranty_window_days(ChurnRates(release_per_day=0.01), theta)


def test_survival_probability_at_measured_cadence() -> None:
    churn = ChurnRates.from_cadences(release_cadence_days=84.0)
    assert survival_probability(churn, 90.0) == pytest.approx(math.exp(-90.0 / 84.0))
    with pytest.raises(AssuranceWindowError):
        survival_probability(churn, -1.0)


def test_robust_warranty_takes_the_smaller_bound() -> None:
    churn = ChurnRates.from_cadences(release_cadence_days=84.0)
    velocity_bound = warranty_days(drift_velocity(TBS), 5.0)
    risk_bound = warranty_window_days(churn, 0.9)
    robust = robust_warranty_days(TBS, 5.0, churn, 0.9)
    assert velocity_bound is not None and risk_bound is not None
    assert robust == pytest.approx(min(velocity_bound, risk_bound))
    assert robust <= velocity_bound and robust <= risk_bound


def test_robust_warranty_is_none_when_no_bound_exists() -> None:
    flat = SuiteDrift("flat", 40.0, 40.0, 84)
    assert robust_warranty_days(flat, 5.0, ChurnRates(), 0.9) is None


def test_release_beat_probability_is_complement_of_survival() -> None:
    p = release_beat_probability(90.0, 84.0)
    assert p == pytest.approx(1.0 - math.exp(-90.0 / 84.0))
    assert p > 0.6  # الجملةُ التجارية: ربعُ السنة أبطأُ من دورةِ الإصدار


def test_beat_probability_is_monotone_in_cycle_and_in_cadence() -> None:
    assert release_beat_probability(30.0, 84.0) < release_beat_probability(90.0, 84.0)
    assert release_beat_probability(90.0, 180.0) < release_beat_probability(90.0, 84.0)


def test_beat_probability_rejects_bad_inputs() -> None:
    with pytest.raises(AssuranceWindowError):
        release_beat_probability(0.0, 84.0)
    with pytest.raises(AssuranceWindowError):
        release_beat_probability(90.0, 0.0)


def test_detection_lag_and_drift_before_detection() -> None:
    assert detection_lag_days(90.0) == pytest.approx(45.0)
    expected = drift_velocity(TBS) * 45.0
    assert drift_before_detection(TBS, 90.0) == pytest.approx(expected)


def test_drift_before_detection_exceeds_the_measured_regression() -> None:
    """أثرُ التأخيرِ على الحزمة الأسرع أكبرُ من الانحدارِ الذي يُفترض أن نلتقطه."""
    noise_floor = drift_before_detection(TBS, 90.0)
    signal = abs(HARVEY.points)
    assert noise_floor > signal


def test_events_per_year_from_cadence_plus_ad_hoc() -> None:
    assert events_per_year(84.0) == pytest.approx(365.0 / 84.0)
    assert events_per_year(84.0, extra_events_per_year=2.0) == pytest.approx(365.0 / 84.0 + 2.0)
    with pytest.raises(AssuranceWindowError):
        events_per_year(0.0)


# ── 4) الدبوسُ وحالاتُ الصلاحية ─────────────────────────────────────────────────


def _pin(issued: date, **overrides: object) -> ReportPin:
    base: dict[str, object] = {
        "model_id": "claude-fable-5-1",
        "harness": "terminal-bench-4.0@pin-a",
        "safeguard_config": "GA-classifiers",
        "suite_version": "0.1",
        "adversary_budget": 0,
        "suite": "Terminal-Bench-Science 0.1",
        "score_points": 52.6,
    }
    base.update(overrides)
    return ReportPin(issued_on=issued, **base)  # type: ignore[arg-type]


def test_complete_pin_at_launch_day_is_fresh_and_quotable() -> None:
    status = evaluate_pin(_pin(date(2026, 9, 1)), date(2026, 9, 1), drift=TBS)
    assert status.state == "FRESH"
    assert status.quotable is True
    assert status.window_days is not None


def test_aged_pin_is_stale_and_not_quotable() -> None:
    status = evaluate_pin(_pin(date(2026, 6, 9)), date(2026, 9, 1), drift=TBS)
    assert status.state == "STALE"
    assert status.quotable is False
    assert status.age_days == 84.0


def test_unpinned_report_is_never_quotable_even_when_young() -> None:
    status = evaluate_pin(
        _pin(date(2026, 9, 1), harness="", adversary_budget=None),
        date(2026, 9, 1),
        drift=TBS,
    )
    assert status.state == "UNPINNED"
    assert status.quotable is False
    assert set(status.missing) == {"harness", "adversary_budget"}


def test_pin_without_drift_evidence_uses_the_risk_bound_then_age_bands() -> None:
    churn = ChurnRates.from_cadences(release_cadence_days=84.0)
    fresh = evaluate_pin(_pin(date(2026, 9, 1)), date(2026, 9, 3), churn=churn)
    assert fresh.state == "FRESH"
    assert fresh.window_days == pytest.approx(warranty_window_days(churn, 0.9), abs=0.01)
    # بعد 31 يوماً تتجاوز النافذةَ المحسوبة من الدورية وحدها ⇒ STALE، لا «تقريرٌ قديمٌ مقبول»
    aged = evaluate_pin(_pin(date(2026, 8, 1)), date(2026, 9, 1), churn=churn)
    assert aged.state == "STALE" and aged.quotable is False
    # وبلا أيِّ مُدخَلِ إحلالٍ لا توجد نافذة: تبقى أعمارُ التصميم تحكم (14 → 90 يوماً)
    no_input = evaluate_pin(_pin(date(2026, 8, 1)), date(2026, 9, 1), churn=ChurnRates())
    assert no_input.state == "THROTTLED" and no_input.window_days is None
    very_old = evaluate_pin(_pin(date(2026, 5, 1)), date(2026, 9, 1), churn=ChurnRates())
    assert very_old.state == "STALE"


def test_pin_validation_refuses_time_travel() -> None:
    future = date.today() + timedelta(days=30)
    with pytest.raises(AssuranceWindowError):
        _pin(future).missing_fields()
    with pytest.raises(AssuranceWindowError):
        evaluate_pin(_pin(date(2026, 9, 1)), date(2026, 8, 1), drift=TBS)


# ── 5) الأجلُ التنظيميُّ كقيدِ تصميم ────────────────────────────────────────────

LEGACY = RepatriationRef("نظامُ 16-04", 306, 360)
NEW = RepatriationRef("تنظيمُ 2026 (مُبلَّغ)", 120, 180, status="press-reported-awaiting-official-text")


def test_legal_ceiling_is_the_binding_of_the_two_limits() -> None:
    assert legal_term_ceiling(LEGACY) == 306
    assert legal_term_ceiling(NEW) == 120


def test_term_survives_under_each_reference_independently() -> None:
    assert term_survives(90, NEW) is True
    assert term_survives(180, NEW) is False  # يتجاوز نافذةَ الترحيل
    assert term_survives(270, NEW) is False
    assert term_survives(180, LEGACY) is True


def test_buffer_days_is_the_design_number_not_the_ceiling() -> None:
    assert buffer_days(45, NEW) == 75
    assert buffer_days(120, NEW) == 0  # «مسموحٌ بلا هامش» ليس تصميماً


@pytest.mark.parametrize("term", [0, -30])
def test_term_must_be_positive(term: int) -> None:
    with pytest.raises(AssuranceWindowError):
        term_survives(term, LEGACY)


def test_robust_terms_keeps_only_ages_surviving_every_reference() -> None:
    rows = robust_terms((30, 45, 60, 90, 120, 180, 270), (LEGACY, NEW), min_buffer_days=30)
    robust = {int(row["term_days"]) for row in rows if row["robust_under_all_refs"]}
    assert robust == {30, 45, 60, 90}
    for row in rows:
        if not row["robust_under_all_refs"]:
            continue
        per_ref = row["per_ref"]
        assert isinstance(per_ref, dict)
        for ref_row in per_ref.values():
            assert isinstance(ref_row, dict)
            assert int(ref_row["buffer_days"]) >= 30


def test_robust_terms_never_averages_across_conflicting_references() -> None:
    rows = robust_terms((105,), (LEGACY, NEW), min_buffer_days=30)
    assert rows[0]["robust_under_all_refs"] is False


def test_reference_validation_demands_naming_and_positive_days() -> None:
    with pytest.raises(AssuranceWindowError):
        RepatriationRef("", 120, 180)
    with pytest.raises(AssuranceWindowError):
        RepatriationRef("bad", 0, 180)


# ── 6) الخلاصةُ وملفُّ القياس: الرقمُ واحدٌ في الكود والوثيقة ───────────────────


def test_summarize_returns_engineering_fields_only() -> None:
    churn = ChurnRates.from_cadences(release_cadence_days=84.0)
    out = summarize(
        low=LOW,
        high=HIGH,
        ratio=16.0,
        drifts=(TBS, HARVEY),
        churn=churn,
        cycle_days=90.0,
        release_cadence_days=84.0,
    )
    assert out["horizon_risk_exponent"] == pytest.approx(horizon_risk_exponent(LOW, HIGH), abs=1e-6)
    assert out["suite_count"] == 2
    assert out["eval_events_per_year"] is not None
    for forbidden in ("price", "revenue", "currency_inflow"):
        assert forbidden not in out


def test_summarize_survives_missing_cadence_without_inventing_it() -> None:
    out = summarize(
        low=LOW,
        high=HIGH,
        ratio=16.0,
        drifts=(TBS,),
        churn=ChurnRates(),
        cycle_days=90.0,
    )
    assert out["risk_warranty_days"] is None
    assert out["eval_events_per_year"] is None
    assert out["release_beat_probability_per_cycle"] is None


def test_measurements_file_matches_recomputation() -> None:
    """منعُ D-266: لا يُقَبَّل رقمٌ في الوثيقة بأن يُنسخ — يُشتقّ."""
    path = ROOT / "docs" / "research" / "AHW_MEASUREMENTS.json"
    assert path.is_file(), "أعِد توليد ملفّ القياس قبل الاختبار"
    stored = json.loads(path.read_text(encoding="utf-8"))
    rebuilt = build()
    for key in ("kind", "as_of", "inputs", "results", "boundaries"):
        assert stored[key] == rebuilt[key], f"انحرافٌ في {key}"
    assert stored["model_runs_executed"] == 0
    assert stored["client_measurements"] == 0
    assert stored["revenue_claim"].startswith("NONE")


def test_measurements_file_is_strict_json_without_nan_or_infinity() -> None:
    path = ROOT / "docs" / "research" / "AHW_MEASUREMENTS.json"
    text = path.read_text(encoding="utf-8")
    assert "NaN" not in text and "Infinity" not in text
    payload = json.loads(text, parse_constant=lambda bad: (_ for _ in ()).throw(ValueError(bad)))
    assert isinstance(payload, dict)


def test_module_is_stdlib_only_and_imports_nothing_from_app() -> None:
    for rel in ("shared/research/assurance_window.py", "scripts/research/measure_assurance_window.py"):
        tree = ast.parse((ROOT / rel).read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            names: list[str] = []
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                names = [node.module]
            for name in names:
                root_name = name.split(".")[0]
                assert root_name not in {"app", "microservices", "numpy", "pandas", "scipy"}, (
                    f"{rel} يستورد {name} — الحزمةُ stdlibٌ فقط لتُشحن لعميلٍ بلا تبعياتنا"
                )
