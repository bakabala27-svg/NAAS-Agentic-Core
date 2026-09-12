"""اختبارات DLY — طبقةُ القرار المتأخّر (الكمون · اللاتماثل · سلامة المحضر · الخصمان).

تُثبت هذه الاختبارات جُملاً حسابية، لا رغبات:

1. **الكمون**: الفصلُ بين التقني والتنظيمي يُحسب لكلّ طرفٍ على حدة، والفجوةُ المُعلَنة
   بلا تاريخ تجعل حكمَ ذلك الطرف `UNMEASURED` — ⛔ لا يُستنتج من غياب المقطع سلامتُه.
2. **اللاتماثل**: نسبةُ الأوتار تُحسب عند نقطتَي القياس، وإسقاطُ الحجم خارج نافذة
   القياس يُرجَع `None` لا رقماً (المنعُ في الكود لا في النثر).
3. **سلامةُ المحضر**: خصمٌ محسوبٌ من معدّل انتحالٍ مُقاس، مع اتّجاهِ الحدّ حين تكون
   العيّنةُ ناقصة، وإلزامِ دليلٍ خارج النطاق عند أيّ انتحالٍ مُقاس.
4. **الزوج لا المكوّن**: دلتا الحزام ترفض اسمَ نموذجٍ بلا اسم حزام — وهو الحارسُ الذي
   يمنع «النموذج آمن» من رقمٍ قِيس على الحزام.
5. **الخصمان**: تشتّتُ حجم السوق يُقارَن **بفجوة القرار** لا بعتبةٍ مطلقة، وانحيازُ
   الأجر يُخرِج نطاقاً واتّجاهاً ⛔ لا متوسّطاً.
6. **الحجبُ الجزئي**: غلافٌ بروتوكولي ثابت ⇒ حجبُ أيّ عددٍ دون الكلّ صفرُ الأثر.

وأخيراً: ملفُّ القياس المودَع **يطابق المحسوب**، وصفرُ ثغرةٍ أُعيد إنتاجُها، وصفرُ
ادّعاءِ إيراد — وهو الحارسُ الذي يمنع انحراف الرقم في الوثيقة التجارية عن الرقم في الكود.
"""

from __future__ import annotations

import ast
import json
import sys
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.research.measure_decision_latency import build
from shared.research.decision_latency import (
    BINDING_LAYERS,
    PARTIES,
    DatedEvent,
    DecisionLatencyError,
    EscalationPolicy,
    HarnessDelta,
    HumanDecisionCycle,
    LatencySegment,
    LatencySplit,
    LossSplit,
    MachineTempo,
    MarketEstimate,
    RateAnchor,
    RewardOutcome,
    TranscriptSpoofing,
    UnmeasuredGap,
    adversary_is_self,
    assurance_requires_pair,
    blocklist_yield,
    controls_held_share,
    days_between,
    dispersion_is_decision_grade,
    failsafe_gap,
    grader_spec_divergence,
    lead_time_days,
    market_dispersion,
    projected_volume,
    rate_bias,
    tempo_ratio,
    transcript_evidence_share,
    unsolvable_concentration,
)

# ── أدواتُ اختبارٍ مشتركة ───────────────────────────────────────────────────────

SIGNAL = DatedEvent("أوّل إدخالٍ في اللوحة", date(2026, 5, 12), "DETECTION")
OBSERVED = DatedEvent("فريقٌ داخلي يرصد", date(2026, 5, 26), "DETECTION")
INCIDENT = DatedEvent("فتحُ حادثة", date(2026, 7, 5), "DECISION")
BREACH = DatedEvent("أوّل إجراءٍ في الحملة", date(2026, 7, 9), "DETECTION")
CUT = DatedEvent("قطعُ الوصول", date(2026, 7, 13), "DETECTION")

TEMPO = MachineTempo(
    actions=17_613,
    window_start=datetime(2026, 7, 9, 2, 28, tzinfo=UTC),
    window_end=datetime(2026, 7, 13, 14, 14, tzinfo=UTC),
    source="HF 2026-07-27",
)
CYCLE = HumanDecisionCycle(decisions=1, over_days=54.0, source="OpenAI 2026-08-26")
SPOOF = TranscriptSpoofing(spoof_rate=0.07, sample_complete=False, source="METR 2026-08-26")
DELTA = HarnessDelta(100.0, "production harness + system prompt", "IM1", "OpenAI 2026-08-26")


# ── 1) الأحداث والمقاطع ────────────────────────────────────────────────────────


def test_dated_event_rejects_layer_outside_closed_set() -> None:
    with pytest.raises(DecisionLatencyError, match="المجموعة المغلقة"):
        DatedEvent("حدث", date(2026, 7, 1), "INTUITION")


def test_binding_layers_is_a_closed_named_set() -> None:
    assert BINDING_LAYERS == (
        "DETECTION", "CORRELATION", "DECISION", "AUTHORITY", "UNMEASURED",
    )


def test_parties_are_exactly_operator_and_defender() -> None:
    assert PARTIES == ("OPERATOR", "DEFENDER")


def test_days_between_refuses_time_travel_instead_of_returning_negative() -> None:
    with pytest.raises(DecisionLatencyError, match="أسبقُ من"):
        days_between(date(2026, 7, 5), date(2026, 5, 12))


def test_days_between_is_exact_on_the_measured_chain() -> None:
    assert days_between(SIGNAL.on, INCIDENT.on) == 54.0
    assert days_between(OBSERVED.on, INCIDENT.on) == 40.0
    assert days_between(SIGNAL.on, OBSERVED.on) == 14.0


def test_segment_rejects_reversed_span() -> None:
    with pytest.raises(DecisionLatencyError, match="ينتهي قبل أن يبدأ"):
        LatencySegment("مقلوب", INCIDENT, SIGNAL, "DECISION", "OPERATOR", "ORGANIZATIONAL")


def test_segment_rejects_unknown_party_and_kind() -> None:
    with pytest.raises(DecisionLatencyError, match="طرفٌ خارج"):
        LatencySegment("x", SIGNAL, OBSERVED, "DETECTION", "VENDOR", "ORGANIZATIONAL")
    with pytest.raises(DecisionLatencyError, match="نوعُ مقطعٍ خارج"):
        LatencySegment("x", SIGNAL, OBSERVED, "DETECTION", "OPERATOR", "CULTURAL")


def test_unmeasured_gap_refuses_silence_and_missing_source() -> None:
    with pytest.raises(DecisionLatencyError, match="بلا قولِ المصدر"):
        UnmeasuredGap("DEFENDER", "CORRELATION", "", "HF 2026-07-27")
    with pytest.raises(DecisionLatencyError, match="بلا مصدر"):
        UnmeasuredGap("DEFENDER", "CORRELATION", "قال المصدر", "")


def test_declared_gap_forces_party_verdict_to_unmeasured() -> None:
    """الفجوةُ المُعلَنة قد تكون أكبرَ من كلِّ ما قِيس ⇒ لا حكمَ على ذلك الطرف."""
    segs = (
        LatencySegment("s1", SIGNAL, OBSERVED, "DETECTION", "OPERATOR", "TECHNICAL"),
        LatencySegment("s2", BREACH, CUT, "DECISION", "DEFENDER", "ORGANIZATIONAL"),
    )
    without_gap = LatencySplit(segs)
    assert without_gap.party_binding_layer("DEFENDER") == "DECISION"
    with_gap = LatencySplit(
        segs,
        (UnmeasuredGap("DEFENDER", "CORRELATION", "فشلَ التصعيدُ بلا تاريخ", "HF 2026-07-27"),),
    )
    assert with_gap.party_binding_layer("DEFENDER") == "UNMEASURED"
    assert with_gap.open_gaps_count == 1


def test_binding_layer_picks_the_largest_total_and_refuses_ties() -> None:
    # 14 يوماً كشف مقابل 40 يوماً قرار ⇒ القرارُ هو المُلزِم
    segs = (
        LatencySegment("det", SIGNAL, OBSERVED, "DETECTION", "OPERATOR", "TECHNICAL"),
        LatencySegment("dec", OBSERVED, INCIDENT, "DECISION", "OPERATOR", "ORGANIZATIONAL"),
    )
    assert LatencySplit(segs).binding_layer == "DECISION"
    # والمعكوس حين يرجح الكشف
    flipped = (
        LatencySegment("det", OBSERVED, INCIDENT, "DETECTION", "OPERATOR", "TECHNICAL"),
        LatencySegment("dec", BREACH, CUT, "DECISION", "OPERATOR", "ORGANIZATIONAL"),
    )
    assert LatencySplit(flipped).binding_layer == "DETECTION"
    # والتعادُلُ الصريح ⇒ UNMEASURED لا ترجيحٌ صامت
    equal = (
        LatencySegment("a", SIGNAL, OBSERVED, "DETECTION", "OPERATOR", "TECHNICAL"),
        LatencySegment("b", SIGNAL, OBSERVED, "DECISION", "DEFENDER", "ORGANIZATIONAL"),
    )
    assert LatencySplit(equal).binding_layer == "UNMEASURED"


def test_split_refuses_empty_segments() -> None:
    with pytest.raises(DecisionLatencyError, match="صفرُ مقطع"):
        LatencySplit(())


def test_ratio_is_none_when_technical_is_zero_not_infinity() -> None:
    seg = (LatencySegment("dec", OBSERVED, INCIDENT, "DECISION", "OPERATOR", "ORGANIZATIONAL"),)
    assert LatencySplit(seg).organizational_to_technical_ratio is None


def test_layer_ratio_is_none_when_detection_layer_absent_not_zero_division() -> None:
    """⛔ قسمةٌ على صفر تُقرأ `None` لا `inf` ولا استثناءً يُبتلع — قاعدة D-212."""
    seg = (LatencySegment("dec", OBSERVED, INCIDENT, "DECISION", "OPERATOR", "ORGANIZATIONAL"),)
    assert LatencySplit(seg).decision_to_detection_ratio is None


def test_the_two_ratios_are_different_quantities_not_renamings() -> None:
    """الاسمان يحسبان كمّيتين مختلفتين — وقد تتعارضان، فالتوحيدُ بينهما خطأٌ لا اختصار.

    ⛔ `days` ليست معاملاً في `LatencySegment`: هي مُشتقّة من حدثَين مؤرَّخين. فالفروقُ
    تُبنى بالتواريخ لا بالأرقام — لأنّ التاريخَ جزءٌ من الدليل لا وسيلةُ إدخالٍ مريحة.
    مقطعُ DECISION **تقنيُّ** الصنف هو ما يفصل الكمّيتَين: التنظيمي÷التقني = 2/4 = 0.5
    بينما DECISION÷DETECTION = 5/1 = 5.0، أي على طرفَي 1.0.
    """
    base = date(2026, 5, 26)

    def span(days: int, layer: str) -> tuple[DatedEvent, DatedEvent]:
        return (
            DatedEvent(f"بدءٌ +{days}", base, layer),
            DatedEvent(f"نهايةٌ +{days}", base + timedelta(days=days), layer),
        )

    a0, a1 = span(2, "DECISION")
    b0, b1 = span(1, "DETECTION")
    c0, c1 = span(3, "DECISION")
    seg = (
        LatencySegment("dec_org", a0, a1, "DECISION", "OPERATOR", "ORGANIZATIONAL"),
        LatencySegment("det_tech", b0, b1, "DETECTION", "DEFENDER", "TECHNICAL"),
        LatencySegment("dec_tech", c0, c1, "DECISION", "OPERATOR", "TECHNICAL"),
    )
    split = LatencySplit(seg)
    assert split.organizational_to_technical_ratio == pytest.approx(2.0 / 4.0, rel=1e-12)
    assert split.decision_to_detection_ratio == pytest.approx(5.0 / 1.0, rel=1e-12)
    # والكمّيتان على طرفَي 1.0 ⇒ لا يُمكن أن يكونا النسبةَ نفسها تحت أيّ إعادة تسمية.
    assert split.organizational_to_technical_ratio < 1.0 < split.decision_to_detection_ratio


def test_layer_total_validates_the_layer_name_instead_of_returning_zero() -> None:
    """طبقةٌ مكتوبةٌ خطأً تُرجع 0.0 صامتةً في أيّ تنفيذٍ بالترشيح — فالتحقّقُ صريح."""
    seg = (LatencySegment("dec", OBSERVED, INCIDENT, "DECISION", "OPERATOR", "ORGANIZATIONAL"),)
    with pytest.raises(DecisionLatencyError, match="طبقةٌ غير معروفة"):
        LatencySplit(seg).layer_total("DECISON")  # خطأٌ إملائي مقصود
    assert LatencySplit(seg).layer_total("CORRELATION") == 0.0  # صفرٌ صادق: الطبقةُ صالحةٌ وفارغة


# ── 2) الأوتار واللاتماثل ──────────────────────────────────────────────────────


def test_machine_tempo_window_matches_the_published_utc_span() -> None:
    expected = 4 + (11 + 46 / 60) / 24  # 07-09 02:28 → 07-13 14:14
    assert TEMPO.window_days == pytest.approx(expected, rel=1e-12)
    assert TEMPO.actions_per_day == pytest.approx(17_613 / expected, rel=1e-12)


def test_machine_tempo_rejects_empty_window_and_zero_actions() -> None:
    with pytest.raises(DecisionLatencyError, match="إجراءات"):
        MachineTempo(0, TEMPO.window_start, TEMPO.window_end, "x")
    with pytest.raises(DecisionLatencyError, match="قبل بدايتها"):
        MachineTempo(10, TEMPO.window_end, TEMPO.window_start, "x")
    with pytest.raises(DecisionLatencyError, match="بلا مصدر"):
        MachineTempo(10, TEMPO.window_start, TEMPO.window_end, "  ")


def test_human_cycle_refuses_zero_decisions_as_a_slow_rate() -> None:
    with pytest.raises(DecisionLatencyError, match="غيابُ قياس"):
        HumanDecisionCycle(0, 54.0, "x")


def test_tempo_ratio_is_a_ratio_of_rates_at_the_anchors() -> None:
    assert tempo_ratio(TEMPO, CYCLE) == pytest.approx(TEMPO.actions_per_day * 54.0, rel=1e-12)


def test_projected_volume_refuses_extrapolation_beyond_measurement_window() -> None:
    assert projected_volume(TEMPO, 54.0) is None
    assert projected_volume(TEMPO, 100.0) is None
    inside = projected_volume(TEMPO, 2.0)
    assert inside == pytest.approx(TEMPO.actions_per_day * 2.0, rel=1e-12)
    with pytest.raises(DecisionLatencyError, match="أفقٌ غير موجب"):
        projected_volume(TEMPO, 0.0)


# ── 3) سلامة المحضر ────────────────────────────────────────────────────────────


def test_trust_ceiling_is_one_minus_measured_spoof_rate() -> None:
    assert SPOOF.trust_ceiling == pytest.approx(0.93, rel=1e-12)


def test_incomplete_sample_labels_the_bound_direction() -> None:
    assert SPOOF.bound_direction == "UPPER_BOUND_ON_TRUST"
    complete = TranscriptSpoofing(0.07, True, "x")
    assert complete.bound_direction == "EXACT"


def test_any_measured_spoofing_requires_out_of_band_evidence() -> None:
    assert SPOOF.requires_out_of_band is True
    assert adversary_is_self(SPOOF) is True
    clean = TranscriptSpoofing(0.0, True, "x")
    assert clean.requires_out_of_band is False


def test_spoof_rate_validation_is_strict() -> None:
    for bad in (-0.01, 1.0, 7.0):
        with pytest.raises(DecisionLatencyError, match=r"\[0,1\)"):
            TranscriptSpoofing(bad, True, "x")


def test_transcript_evidence_share_carries_source_and_adversary_flag() -> None:
    share = transcript_evidence_share(SPOOF)
    assert share["adversary_is_the_monitored"] is True
    assert share["source"] == SPOOF.source
    assert share["requires_out_of_band_evidence"] is True


# ── 4) الزوج لا المكوّن + الإخفاق الآمن ───────────────────────────────────────


def test_harness_delta_refuses_a_model_name_without_a_harness_name() -> None:
    with pytest.raises(DecisionLatencyError, match="الزوج"):
        HarnessDelta(100.0, "", "IM1", "src")
    with pytest.raises(DecisionLatencyError, match="الزوج"):
        HarnessDelta(100.0, "harness", "  ", "src")


def test_harness_delta_refuses_factor_that_is_not_a_protection() -> None:
    with pytest.raises(DecisionLatencyError, match="ليس دلتا حماية"):
        HarnessDelta(1.0, "h", "m", "src")


def test_assurance_requires_pair_is_structural_not_narrative() -> None:
    assert assurance_requires_pair(DELTA) is True


def test_lead_time_is_days_not_a_story() -> None:
    assert lead_time_days(24.0) == pytest.approx(1.0)
    assert lead_time_hours_rejected()


def lead_time_hours_rejected() -> bool:
    try:
        lead_time_days(-1.0)
    except DecisionLatencyError:
        return True
    return False


def test_failsafe_is_the_direction_of_the_default_not_the_length_of_the_timer() -> None:
    pause = EscalationPolicy(30.0, "PAUSE", "OpenAI 2026-08-26")
    continue_ = EscalationPolicy(30.0, "CONTINUE", "افتراضُ جهةٍ أخرى")
    assert pause.failsafe is True
    assert continue_.failsafe is False
    assert failsafe_gap(pause)["defect"] is None
    assert "الصمتُ يُفسَّر إذناً" in str(failsafe_gap(continue_)["defect"])
    # المدّةُ نفسها مع اتجاهين مختلفَين ⇒ المنتجُ هو الاتجاه
    assert failsafe_gap(pause)["decide_within_minutes"] == failsafe_gap(continue_)["decide_within_minutes"]


def test_escalation_policy_rejects_undefined_default_and_missing_source() -> None:
    with pytest.raises(DecisionLatencyError, match="افتراضٌ غير مُعرَّف"):
        EscalationPolicy(30.0, "ESCALATE_SOMETIMES", "src")
    with pytest.raises(DecisionLatencyError, match="بلا مصدر"):
        EscalationPolicy(30.0, "PAUSE", "")


# ── 5) عملٌ بلا مكافأة + تباعدُ المُقيِّم ─────────────────────────────────────


def test_zero_gain_returns_none_not_zero_not_infinity() -> None:
    reward = RewardOutcome(17_613, 0.0, "ExploitGym score", "OpenAI 2026-08-26")
    assert reward.wasted is True
    assert reward.actions_per_unit_gain is None
    finite = RewardOutcome(100, 4.0, "score", "src")
    assert finite.actions_per_unit_gain == pytest.approx(25.0)


def test_concentration_ratio_is_chatter_share_over_unsolvable_share() -> None:
    out = unsolvable_concentration(198, 898, 0.93)
    assert out["unsolvable_share"] == pytest.approx(198 / 898, rel=1e-12)
    assert out["concentration_ratio"] == pytest.approx(0.93 / (198 / 898), rel=1e-12)
    assert out["concentration_ratio"] > 1.0  # الخطرُ تركّز في المستحيل


def test_concentration_refuses_zero_unsolvable_and_bad_shares() -> None:
    with pytest.raises(DecisionLatencyError, match="لا تركّزَ يُقاس"):
        unsolvable_concentration(0, 898, 0.93)
    with pytest.raises(DecisionLatencyError, match="متناقض"):
        unsolvable_concentration(900, 898, 0.5)
    with pytest.raises(DecisionLatencyError, match="خارج \[0,1\]"):
        unsolvable_concentration(10, 100, 1.5)


def test_grader_divergence_is_a_set_difference_not_an_opinion() -> None:
    out = grader_spec_divergence(
        frozenset({"flag_found", "intended_vulnerability_used"}), frozenset({"flag_found"})
    )
    assert out["divergent"] is True
    assert out["documented_only"] == ["intended_vulnerability_used"]
    assert out["phantom_requirements"] == 1
    same = grader_spec_divergence(frozenset({"a"}), frozenset({"a"}))
    assert same["divergent"] is False
    assert "لا تباعد" in str(same["reading"])


def test_grader_divergence_detects_the_other_direction_too() -> None:
    out = grader_spec_divergence(frozenset({"a"}), frozenset({"a", "b"}))
    assert out["deployed_only"] == ["b"]
    assert out["divergent"] is True
    assert out["phantom_requirements"] == 0


def test_grader_divergence_refuses_empty_documented_spec() -> None:
    with pytest.raises(DecisionLatencyError, match="فارغة"):
        grader_spec_divergence(frozenset(), frozenset({"a"}))


# ── 6) خصمان على أدلّة السوق ──────────────────────────────────────────────────


ESTIMATES = (
    MarketEstimate("AI Agent Security", 2025, 450e6, "MarketIntelo", date(2026, 7, 4)),
    MarketEstimate("AI Agent Security", 2025, 18.72e9, "SNS Insider", date(2026, 7, 23)),
    MarketEstimate("AI Agent Security", 2025, 35.09e9, "SNS Insider", date(2026, 7, 23)),
)


def test_dispersion_ratio_is_max_over_min_of_the_same_named_quantity() -> None:
    out = market_dispersion(ESTIMATES)
    assert out["dispersion_ratio"] == pytest.approx(35.09e9 / 450e6, rel=1e-12)
    assert out["n_estimates"] == 3


def test_dispersion_refuses_to_merge_different_markets_or_years() -> None:
    mixed = ESTIMATES + (MarketEstimate("Securing AI", 2027, 4_783e6, "Gartner", date(2026, 8, 26)),)
    with pytest.raises(DecisionLatencyError, match="أسماء/سنواتٍ مختلفة"):
        market_dispersion(mixed)
    with pytest.raises(DecisionLatencyError, match="ليس تشتّتاً"):
        market_dispersion((ESTIMATES[0],))


def test_same_source_self_contradiction_is_named_not_averaged() -> None:
    out = market_dispersion(ESTIMATES)
    contradictions = out["same_source_self_contradictions"]
    assert len(contradictions) == 1
    assert contradictions[0]["source"] == "SNS Insider"
    assert contradictions[0]["values_usd"] == [18.72e9, 35.09e9]


def test_decision_grade_is_judged_against_the_decision_gap_not_a_constant() -> None:
    dispersion = 35.09e9 / 450e6  # 77.9778 — التشتّتُ المقيس فعلاً
    assert dispersion_is_decision_grade(dispersion, 100.0) is True   # فجوةٌ أوسع من التشتّت ⇒ يُرتَّب
    assert dispersion_is_decision_grade(dispersion, 77.0) is False   # فجوةٌ أضيق ⇒ لا يُرتَّب
    assert dispersion_is_decision_grade(dispersion, 2.0) is False    # والفجوةُ المُعلَنة عندنا
    assert dispersion_is_decision_grade(2.5, 3.0) is True            # تشتّتٌ ضيّقٌ يكفي للترتيب
    with pytest.raises(DecisionLatencyError, match="مستحيل"):
        dispersion_is_decision_grade(0.5, 2.0)
    with pytest.raises(DecisionLatencyError, match="ليست فجوة"):
        dispersion_is_decision_grade(2.0, 1.0)


def test_rate_bias_reports_band_and_direction_and_never_a_mean() -> None:
    anchors = (
        RateAnchor("مُبلَّغ ذاتياً", 144.0, "SELF_REPORTED_ASKED", "contractrates.fyi", date(2026, 6, 30)),
        RateAnchor("مشتقٌّ من إعلانات", 63.92, "POSTING_DERIVED_OFFERED", "ZipRecruiter", date(2026, 7, 9)),
        RateAnchor("مشتقٌّ من إعلانات", 57.64, "POSTING_DERIVED_OFFERED", "ZipRecruiter", date(2026, 9, 10)),
    )
    out = rate_bias(anchors)
    assert out["band_usd_per_hour"] == [57.64, 144.0]
    assert out["self_report_bias_factor"] == pytest.approx(144.0 / 57.64, rel=1e-12)
    assert out["bias_direction"] == "SELF_REPORT_HIGHER"
    assert out["realized_anchor_present"] is False
    assert "يُخطَّط على الأدنى" in str(out["planning_rule"])
    assert "mean" not in out and "average" not in out


def test_rate_anchor_rejects_measurement_kind_outside_closed_set() -> None:
    with pytest.raises(DecisionLatencyError, match="نوعُ قياسٍ خارج"):
        RateAnchor("x", 100.0, "GUESSED", "src", date(2026, 1, 1))


def test_rate_bias_refuses_a_single_anchor() -> None:
    with pytest.raises(DecisionLatencyError, match="لا تُنتج انحيازاً"):
        rate_bias((RateAnchor("x", 100.0, "SELF_REPORTED_ASKED", "src", date(2026, 1, 1)),))


# ── 7) الحجبُ الجزئي وفصلُ الخسارة ─────────────────────────────────────────────


def test_partial_block_of_an_invariant_envelope_yields_exactly_zero() -> None:
    assert blocklist_yield(6, 5, True) == 0.0
    assert blocklist_yield(6, 0, True) == 0.0
    assert blocklist_yield(6, 6, True) == 1.0


def test_without_envelope_invariance_blocking_is_proportional() -> None:
    assert blocklist_yield(6, 3, False) == pytest.approx(0.5)


def test_blocklist_validation_is_strict() -> None:
    with pytest.raises(DecisionLatencyError, match="صفرُ قناة"):
        blocklist_yield(0, 0, True)
    with pytest.raises(DecisionLatencyError, match="خارج نطاق القنوات"):
        blocklist_yield(6, 7, True)


LOSSES = LossSplit(
    confirmed_damage_items=("قراءةُ قاعدةٍ داخلية",),
    response_cost_items=("إعادةُ بناء عنقود", "تدويرُ اعتمادات"),
    controls_that_held=("قائمةُ السماح ردّت SSRF", "84 عمليةً رُفضت"),
    third_party_protected_asset_affected=False,
    third_party_source="HF 2026-07-27 + OpenAI 2026-08-26",
)


def test_internal_damage_alone_does_not_make_a_loss_insurable() -> None:
    assert LOSSES.damage_confirmed is True
    assert LOSSES.insurable_loss_present is False
    assert LOSSES.sellable_unit == "RESPONSE_COST_REDUCTION"


def test_third_party_damage_flips_the_sellable_unit() -> None:
    flipped = LossSplit(
        LOSSES.confirmed_damage_items, LOSSES.response_cost_items, LOSSES.controls_that_held,
        True, LOSSES.third_party_source,
    )
    assert flipped.sellable_unit == "LOSS_INDEMNITY_OR_PREVENTION"


def test_loss_split_refuses_silence_and_unsupported_claims() -> None:
    with pytest.raises(DecisionLatencyError, match="لا ضررَ ولا كلفة"):
        LossSplit((), (), (), False, "src")
    with pytest.raises(DecisionLatencyError, match="بلا بند ضرر"):
        LossSplit((), ("كلفة",), (), True, "src")
    with pytest.raises(DecisionLatencyError, match="بلا مصدر"):
        LossSplit(("ضرر",), ("كلفة",), (), False, " ")


def test_controls_held_share_is_none_when_nothing_was_measured() -> None:
    assert controls_held_share(LOSSES) == pytest.approx(2 / 3)
    empty = LossSplit((), ("كلفة",), (), False, "src")
    assert controls_held_share(empty) is None


# ── 8) ملفُّ القياس المودَع يطابق المحسوب ─────────────────────────────────────


def test_measurements_file_matches_recomputation() -> None:
    path = ROOT / "docs" / "research" / "DLY_MEASUREMENTS.json"
    assert path.is_file(), "ملفُّ القياس غير موجود — شغّل measure_decision_latency.py"
    stored = json.loads(path.read_text(encoding="utf-8"))
    fresh = build()
    assert stored["results"] == fresh["results"]
    assert stored["inputs_digest_sha256"] is not None


def test_measurements_file_is_strict_json_without_nan_or_infinity() -> None:
    raw = (ROOT / "docs" / "research" / "DLY_MEASUREMENTS.json").read_text(encoding="utf-8")
    assert "NaN" not in raw and "Infinity" not in raw
    json.loads(raw, parse_constant=lambda c: pytest.fail(f"ثابتٌ غير منتهٍ في الملف: {c}"))


def test_measurement_declares_zero_runs_zero_clients_zero_revenue_zero_exploits() -> None:
    payload = build()
    assert payload["model_runs_executed"] == 0
    assert payload["client_measurements"] == 0
    assert payload["exploits_reproduced"] == 0
    assert payload["revenue_claim"].startswith("NONE")


def test_module_is_stdlib_only_and_imports_nothing_from_app() -> None:
    src = (ROOT / "shared" / "research" / "decision_latency.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    allowed_roots = {"__future__", "dataclasses", "datetime", "math", "shared.research"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert alias.name.split(".")[0] in {a.split(".")[0] for a in allowed_roots}, alias.name
        elif isinstance(node, ast.ImportFrom):
            assert node.module and node.module.startswith(tuple(allowed_roots)), node.module
    assert "from app" not in src and "import app" not in src


def test_measurement_script_reproduces_no_exploit_code() -> None:
    """⛔ لا شيفرةَ استغلالٍ في مسار القياس: لا sqlite3 constructor ولا Jinja exec."""
    for rel in (
        "shared/research/decision_latency.py",
        "scripts/research/measure_decision_latency.py",
    ):
        src = (ROOT / rel).read_text(encoding="utf-8")
        for banned in ("sqlite3_initialize", "ZZROOTSTART", "__builtins__.exec", "169.254.169.254"):
            assert banned not in src, f"{rel} يحمل شيفرةَ استغلال: {banned}"


def test_summary_reports_both_parties_and_the_open_gaps() -> None:
    results = build()["results"]
    assert results["binding_layer"] == "DECISION"
    assert results["operator_binding_layer"] == "DECISION"
    assert results["defender_binding_layer"] == "UNMEASURED"
    assert results["open_gaps"] == 2
    assert results["organizational_days"] > results["technical_days"]
    assert results["layer_totals_days"]["DECISION"] == max(results["layer_totals_days"].values())


def test_summary_never_projects_volume_outside_the_measurement_window() -> None:
    results = build()["results"]
    assert results["projected_volume_outside_measurement_window"] is None
    assert results["tempo_ratio_actions_per_human_decision"] > 1.0


def test_every_adjudicated_claim_in_the_input_is_blocked_as_cited() -> None:
    """الأداةُ طُبِّقت على المدخل: كلُّ ادّعاءٍ كما ورد غيرُ قابلٍ للاقتباس، عدا وقائع الحادث."""
    cases = build()["results"]["adjudication_cases"]
    accepted = [c for c in cases if c["quotable_as_cited"]]
    assert len(accepted) == 1
    assert accepted[0]["verdict"] == "ACCEPTED_WITH_ONE_CORRECTION"
    for case in cases:
        if not case["date_present_in_input"]:
            assert case["age_days_at_as_of"] is None
            assert case["within_max_report_age"] is False
            assert case["quotable_as_cited"] is False


def test_refuted_claims_never_become_quotable_by_resourcing_alone() -> None:
    cases = {c["verdict"]: c for c in build()["results"]["adjudication_cases"]}
    assert cases["REFUTED"]["quotable_when_resourced"] is False
    assert cases["REFUTED_DISPERSION"]["quotable_when_resourced"] is False
    assert cases["UNSOURCED"]["quotable_when_resourced"] is False
    assert cases["THROTTLED_AND_STALE"]["quotable_when_resourced"] is False


def test_phases_omitted_by_the_input_are_the_highest_decision_value() -> None:
    inputs = build()["inputs"]
    omitted = inputs["phases_omitted_by_input_under_review"]
    assert set(omitted) == {"c2", "evasion", "tailscale"}
    volumes = inputs["hf_phase_volumes"]
    assert inputs["input_omitted_actions_total"] == sum(volumes[p] for p in omitted)
    # الأطوارُ المسقوطة هي الوحيدة التي تُسمّي قناةَ التحكم والتسريب والتسلّل الجانبي
    assert volumes["tailscale"] > volumes["exfil"]
    assert volumes["c2"] > volumes["evasion"]
