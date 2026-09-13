"""اختباراتُ FXR — سكّةُ العملة الصعبة (الدفعة السادسة).

كلُّ اختبارٍ يثبّت **رقماً مُحوسباً من نصٍّ مُسند**، لا رأياً:
F1 (100% احتفاظ) · F3 (120/180 يوم) · F4 (سقف 5م دج) · F5 (حظر الأصل الخارجي).
"""

from __future__ import annotations

import math

import pytest

from shared.research.fx_rail import (
    AE_CEILING_DZD_SERVICES,
    FX_SNAPSHOT_2026_09,
    REPATRIATION_CAP_DAYS,
    ae_ceiling,
    ceiling_headroom,
    entity_ladder,
    fx_cost_base_rule,
    fx_retention,
    measure_all,
    purchasing_power_multiple,
    repatriation_compliance,
    repatriation_feasible_terms,
    score_rails,
    spread_penalty,
)

# ---------------------------------------------------------------------------
# 1) سقفُ الكيان (F4 × F9)
# ---------------------------------------------------------------------------


def test_ae_ceiling_is_a_function_of_the_rate_not_a_constant():
    """السقفُ الدولاري مشتقٌّ من السعر المُسند — لا رقمٌ مكتوبٌ يدوياً."""
    cap = ae_ceiling()
    expected_low = AE_CEILING_DZD_SERVICES / FX_SNAPSHOT_2026_09.official_usd_dzd_high
    expected_high = AE_CEILING_DZD_SERVICES / FX_SNAPSHOT_2026_09.official_usd_dzd_low
    assert cap.usd_per_year_at_official_low == pytest.approx(round(expected_low, 2))
    assert cap.usd_per_year_at_official_high == pytest.approx(round(expected_high, 2))
    # الأسوأُ هو الأقلّ دولارات — وهذا هو رقمُ التخطيط.
    assert cap.usd_per_year_at_official_low < cap.usd_per_year_at_official_high


def test_ae_ceiling_lands_near_37_5k_usd_per_year():
    """الرقمُ الذي يُبنى عليه كلُّ تسعير: ≈37,5 ألف دولار/سنة."""
    cap = ae_ceiling()
    assert 37_000 < cap.usd_per_year_at_official_low < 38_000
    assert 37_000 < cap.usd_per_year_at_official_high < 38_000
    assert 32_000 < cap.eur_per_year < 33_000
    assert 3_000 < cap.usd_per_month_worst < 3_200


def test_board_high_target_breaches_the_entity_ceiling():
    """النتيجةُ المركزية: هدف 8000$/شهر يتجاوز سقفَ ANAE بمضاعف >2."""
    fit = ceiling_headroom(8_000.0)
    assert fit["fits"] is False
    assert fit["ratio"] > 2.0
    assert "يتجاوز السقف" in fit["verdict"]


def test_board_low_target_fits_with_less_than_five_percent_headroom():
    """وهدف 3000$/شهر «ينجح» بهامشٍ أقلّ من 5% — أي إنه عملياً عند الحدّ."""
    fit = ceiling_headroom(3_000.0)
    assert fit["fits"] is True
    assert 0.90 < fit["ratio"] < 1.0
    assert (1.0 - fit["ratio"]) < 0.05


# ---------------------------------------------------------------------------
# 2) سُلَّمُ الكيانات
# ---------------------------------------------------------------------------


def test_entity_ladder_migrates_at_the_trigger_not_at_the_ceiling():
    """الانتقالُ عند 70% من السقف، لا بعد كسره."""
    stage1 = entity_ladder(20_000.0)
    stage2 = entity_ladder(50_000.0)
    assert stage1[0]["applies"] is True
    assert stage1[1]["applies"] is False
    assert stage2[0]["applies"] is False
    assert stage2[1]["applies"] is True
    # العتبةُ مُشتقّة، لا مكتوبة.
    assert stage1[0]["trigger_usd_per_year"] == pytest.approx(
        round(stage1[0]["ceiling_usd_per_year"] * 0.70, 2)
    )


def test_thirty_thousand_dollars_already_trips_the_migration_trigger():
    """نتيجةٌ غيرُ متوقَّعة: 30 ألف$/سنة — 80% من السقف فقط — تُوجب الانتقال.

    لأنّ العتبةَ 70%: 0,70 × 37.464$ ≈ 26.225$. فمن يخطّط «سنةً واحدة» على
    30 ألف$ يكون قد كسر عتبةَ الترحيل دون أن يكسر السقف.
    """
    row = entity_ladder(30_000.0)
    assert row[0]["applies"] is False
    assert row[1]["applies"] is True
    assert row[0]["breaches_ceiling"] is False  # لم يكسر السقف — كسر العتبة فقط
    assert row[0]["trigger_usd_per_year"] < 30_000.0


def test_migration_trigger_sits_below_the_ceiling():
    ladder = entity_ladder(1.0)
    assert ladder[0]["trigger_usd_per_year"] < ladder[0]["ceiling_usd_per_year"]


def test_entity_ladder_flags_ceiling_breach_in_dzd():
    """50 ألف دولار × أعلى سعرٍ رسمي ⇒ رقمُ أعمالٍ يكسر السقفَ بالدينار."""
    row = entity_ladder(50_000.0)[0]
    assert row["breaches_ceiling"] is True
    assert row["ca_dzd_at_official_high"] > AE_CEILING_DZD_SERVICES


# ---------------------------------------------------------------------------
# 3) الاحتفاظُ بالعملة (F1)
# ---------------------------------------------------------------------------


def test_retention_is_one_hundred_percent_and_splits_80_20():
    ret = fx_retention(10_000.0)
    assert ret["retained_in_fx_account_pct"] == 100.0
    imports = ret["earmarked_imports_of_goods_and_services_usd"]
    promo = ret["earmarked_export_promotion_usd"]
    assert imports == pytest.approx(8_000.0)
    assert promo == pytest.approx(2_000.0)
    assert imports + promo == pytest.approx(10_000.0)
    assert ret["free_use_for_electronic_payments_and_transfers"] is True


# ---------------------------------------------------------------------------
# 4) الفجوة: كلفةُ التحويل (F9)
# ---------------------------------------------------------------------------


def test_round_trip_loses_roughly_forty_four_percent():
    pen = spread_penalty()
    assert pen["purchasing_power_lost_pct"] == pytest.approx(44.0, abs=0.5)
    assert pen["usd_recovered_per_usd_after_round_trip"] < 0.6
    # رقمان لفجوةٍ واحدة، ولا يُكتب أحدهما فوق الآخر (عرف D-282).
    assert pen["gap_pct_as_published_exdz"] < pen["gap_pct_worst_case"]
    assert pen["gap_pct_as_published_exdz"] == pytest.approx(76.84, abs=0.05)


def test_paying_from_the_fx_account_is_worth_more_than_one_point_seven():
    assert purchasing_power_multiple() > 1.7


def test_fx_cost_base_rule_respects_the_80_percent_earmark():
    """6 آلاف$ كلفة على 10 آلاف$ إيراد ⇒ داخل قاعدة الـ80%، ومُحصَّن بالكامل."""
    rule = fx_cost_base_rule(10_000.0, 6_000.0)
    assert rule["within_80pct_rule"] is True
    assert rule["shielded_from_spread_usd"] == pytest.approx(6_000.0)
    assert rule["fx_cost_share_of_revenue"] == pytest.approx(0.6)


def test_fx_cost_base_rule_rejects_overspend_beyond_the_earmark():
    rule = fx_cost_base_rule(10_000.0, 9_000.0)
    assert rule["within_80pct_rule"] is False
    assert rule["shielded_from_spread_usd"] == pytest.approx(8_000.0)


def test_fx_cost_base_rule_returns_none_on_zero_revenue():
    """عدمُ النضج لا يُقرأ صفراً (D-212): قسمةٌ على صفر تُرجع None."""
    rule = fx_cost_base_rule(0.0, 100.0)
    assert rule["fx_cost_share_of_revenue"] is None
    assert rule["within_80pct_rule"] is None


# ---------------------------------------------------------------------------
# 5) الساعةُ التنظيمية (F3)
# ---------------------------------------------------------------------------


def test_terms_up_to_120_are_compliant_and_beyond_need_insurance():
    terms = {t["payment_term_days"]: t for t in repatriation_feasible_terms()}
    assert terms[0]["status"] == "COMPLIANT"
    assert terms[90]["status"] == "COMPLIANT"
    assert terms[120]["status"] == "COMPLIANT"
    assert terms[150]["status"] == "INSURED_ONLY"
    assert terms[180]["status"] == "INSURED_ONLY"
    assert terms[270]["status"] == "PROHIBITED"
    assert terms[360]["status"] == "PROHIBITED"


def test_only_terms_with_a_real_margin_survive():
    """120 يوماً «مسموحة» بهامشٍ صفري — فلا تُسمّى تصميماً."""
    terms = {t["payment_term_days"]: t for t in repatriation_feasible_terms()}
    assert terms[120]["margin_days_to_120"] == 0
    assert terms[120]["survives_with_margin"] is False
    assert terms[90]["survives_with_margin"] is True
    assert terms[60]["survives_with_margin"] is True


def test_insured_only_terms_name_the_instrument():
    terms = {t["payment_term_days"]: t for t in repatriation_feasible_terms()}
    assert "تأمين" in terms[150]["requirement"]
    assert "⛔" in terms[270]["requirement"]


def test_repatriation_case_clean_has_no_breaches():
    case = repatriation_compliance(
        service_realized_day=30,
        client_paid_day=90,
        funds_in_algerian_account_day=90,
        payment_term_in_contract_days=90,
    )
    assert case["compliant"] is True
    assert case["breaches"] == []


def test_repatriation_case_bad_names_all_three_breaches():
    """ثلاثةُ خروقٍ مُسمّاة: بلا أجلٍ في العقد، دفعٌ متأخر، ترحيلٌ بعد الدفع."""
    case = repatriation_compliance(
        service_realized_day=30,
        client_paid_day=200,
        funds_in_algerian_account_day=205,
        payment_term_in_contract_days=None,
    )
    assert case["compliant"] is False
    codes = {b.split(" — ")[0] for b in case["breaches"]}
    assert codes == {
        "CONTRACT_TERM_MISSING",
        "PAID_AFTER_120",
        "NOT_REPATRIATED_ON_PAYMENT_DAY",
    }


def test_repatriation_deadline_is_anchored_to_service_realization():
    """العدُّ يبدأ من **إنجاز الخدمة** لا من الفوترة ولا من التعاقد."""
    on_the_line = repatriation_compliance(
        service_realized_day=30,
        client_paid_day=150,
        funds_in_algerian_account_day=150,
        payment_term_in_contract_days=120,
    )
    assert on_the_line["deadline_day"] == 30 + REPATRIATION_CAP_DAYS
    # الدفعُ في يوم الحدّ نفسه داخل الأجل — الحدُّ مُضمَّن لا مستثنى.
    assert on_the_line["compliant"] is True

    one_day_late = repatriation_compliance(
        service_realized_day=30,
        client_paid_day=151,
        funds_in_algerian_account_day=151,
        payment_term_in_contract_days=120,
    )
    assert one_day_late["compliant"] is False
    assert any(b.startswith("PAID_AFTER_120") for b in one_day_late["breaches"])


def test_insured_term_between_121_and_180_is_flagged_not_silently_allowed():
    case = repatriation_compliance(
        service_realized_day=0,
        client_paid_day=150,
        funds_in_algerian_account_day=150,
        payment_term_in_contract_days=150,
    )
    assert case["compliant"] is False
    assert any(b.startswith("TERM_NEEDS_CREDIT_INSURANCE") for b in case["breaches"])


# ---------------------------------------------------------------------------
# 6) السكك (F5 — الحظر)
# ---------------------------------------------------------------------------


def test_the_diy_foreign_entity_rail_is_ranked_last_and_flagged_criminal():
    rails = {r["rail_id"]: r for r in score_rails()}
    ranked_ids = [r["rail_id"] for r in score_rails()]
    assert ranked_ids[-1] == "X1"
    assert rails["X1"]["legally_sourced"] is False
    assert rails["X1"]["criminal_exposure"] is not None
    assert "م126" in rails["X1"]["legal_basis"]
    assert rails["X1"]["score"] < rails["R1"]["score"]


def test_all_legal_rails_keep_fx_and_have_a_blocking_step():
    rails = [r for r in score_rails() if r["rail_id"] != "X1"]
    assert len(rails) == 4
    for rail in rails:
        assert rail["keeps_fx"] is True
        assert rail["legally_sourced"] is True
        assert rail["criminal_exposure"] is None
        assert rail["blocking_step_ar"].strip()


def test_r1_ceiling_is_the_computed_ae_ceiling():
    rails = {r["rail_id"]: r for r in score_rails()}
    assert rails["R1"]["ceiling_usd_per_year"] == pytest.approx(
        ae_ceiling().usd_per_year_at_official_low
    )


# ---------------------------------------------------------------------------
# 7) المُحصِّلة
# ---------------------------------------------------------------------------


def test_measure_all_is_deterministic():
    assert measure_all() == measure_all()


def test_measure_all_declares_its_limits():
    m = measure_all()
    assert "ليست رأياً قانونياً" in m["legal_disclaimer_ar"]
    assert len(m["kill_conditions_ar"]) >= 4
    # لم يُقرأ نصُّ الجريدة الرسمية بعد ⇒ الحدُّ مُعلَن في المُحصِّلة نفسها.
    assert any("الجريدة الرسمية" in k for k in m["kill_conditions_ar"])


def test_measure_all_carries_the_procurement_evidence():
    m = measure_all()
    channels = {c["channel_id"]: c for c in m["results"]["demand_channels_outside_sales"]}
    assert channels["C1"]["verified_awards"][0]["total_value_gbp"] == 5_000_000
    assert channels["C1"]["verified_awards"][0]["awardee_is_sme"] is True
    assert channels["C2"]["algeria_eligible"] is True
    assert channels["C2"]["eligible_wilayas_count"] == 14


def test_snapshot_correction_against_the_board_is_recorded():
    """أرقامُ الصرف في اللوحة (151/280/73%) مُصحَّحة صراحةً في المُحصِّلة."""
    m = measure_all()
    assert "151" in m["fx_snapshot"]["correction_ar"]
    assert m["fx_snapshot"]["gap_pct_as_published_exdz"] == pytest.approx(76.84, abs=0.05)
    assert not math.isnan(m["fx_snapshot"]["gap_pct_worst_case"])
