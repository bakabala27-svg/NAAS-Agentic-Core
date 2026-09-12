"""اختباراتُ قياس دبوس المعيار (BPIN) — `scripts/research/measure_benchmark_pin.py`.

**لماذا هذا الملفّ:** القياسُ يُنتج أوّلَ مرساةِ CPST من طرفٍ أوّل في الدراسة، ويحسم `H59`
(دبوسُ AHW محكومُ المجال) **بالاستعمال لا بالحجّة**. وكلا الرقمين يُقتبس في صفحة قرار، فكلٌّ
منهما يحتاج حارساً يمنعه من الانزلاق:

1. **الدبوسُ في مجاله يجب ألّا يُنتج `UNPINNED`** — وإن أنتجه فالدبوسُ معطوبٌ أو الإدخالُ
   ناقص، وكلاهما فشلٌ صريح لا نتيجة.
2. **المقامُ الصفري يُسجَّل زوجاً لا نسبة** — فـ«0 ← 120» ليست `inf` ولا `0`.
3. **الغائبُ لا يُستكمل** — وCPST غيرُ المُفصَحة تبقى فجوةً معلَنة، ⛔ لا متوسطاً.
4. **تعارضُ الطرفَين الأوّليين لا يُسوَّى** — فلا متوسطَ بين 22.05% و80.29%.

⛔ لا شبكةَ ولا نموذجاً ولا شيفرةَ استغلال في أيٍّ من هذه الاختبارات.
"""

from __future__ import annotations

import ast
import json
import re
import sys
from datetime import date
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.research.measure_benchmark_pin import (  # noqa: E402
    AS_OF,
    DOMAIN_INSTANCES,
    OPENAI_UNSOLVED,
    RUNS,
    SUITE_INSTANCES,
    SUITE_ISSUED_ON,
    BenchmarkPinError,
    SuiteRun,
    budget_sensitivity,
    build,
    cpst_band,
    mitigation_effect,
    off_target_rate,
    pin_evaluations,
    safeguard_pair,
    self_contradictions,
    unsolved_conflict,
)
from shared.research.assurance_window import MAX_REPORT_AGE_DAYS, ReportPin, evaluate_pin  # noqa: E402

ARTIFACT = ROOT / "docs" / "research" / "BPIN_MEASUREMENTS.json"
SCRIPT = ROOT / "scripts" / "research" / "measure_benchmark_pin.py"


# ── 0) الملفُّ المودَع يطابق إعادة الحساب ─────────────────────────────────────
def test_stored_artifact_matches_recomputation() -> None:
    """⛔ لا رقمَ في صفحة قرارٍ بلا ملفٍّ حتميٍّ وراءه — والمودَعُ يجب أن يُعاد بناؤه."""
    assert ARTIFACT.is_file(), "ملفُ BPIN_MEASUREMENTS.json غير موجود"
    stored = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    fresh = build()
    assert stored["results"] == fresh["results"]
    assert stored["kind"] == "BPIN_MEASUREMENTS"
    assert stored["as_of"] == fresh["as_of"] == AS_OF.isoformat()


def test_artifact_is_strict_json_without_nan_or_infinity() -> None:
    """`NaN`/`Infinity` ليسا JSON صالحاً — وقارئٌ متسامحٌ يُخفي قسمةً على صفر."""
    text = ARTIFACT.read_text(encoding="utf-8")
    json.loads(text, parse_constant=lambda c: pytest.fail(f"ثابتٌ غير JSON: {c}"))
    for token in ("NaN", "Infinity", "-Infinity"):
        assert token not in text, token


def test_inputs_digest_is_stable_across_rebuilds() -> None:
    """البصمةُ على المدخلات فقط — ⛔ لا على طابع الزمن وإلا تغيّرت كلّ ثانية."""
    import hashlib

    a, b = build(), build()
    for payload in (a, b):
        payload["inputs_digest_sha256"] = hashlib.sha256(
            json.dumps(payload["inputs"], ensure_ascii=False, sort_keys=True).encode()
        ).hexdigest()
    assert a["inputs_digest_sha256"] == b["inputs_digest_sha256"]
    stored = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert stored["inputs_digest_sha256"] == a["inputs_digest_sha256"]


# ── 1) الأصفارُ المعلَنة: صفرُ تشغيل · صفرُ عميل · صفرُ استغلال ───────────────
def test_measurement_declares_zero_runs_zero_clients_zero_exploits() -> None:
    """L9: ⛔ لا استعارةَ دليلِ الغير دليلاً على قدرتنا."""
    payload = build()
    assert payload["model_runs_executed"] == 0
    assert payload["client_measurements"] == 0
    assert payload["exploits_reproduced"] == 0
    assert payload["exploit_code_present"] is False
    assert str(payload["revenue_claim"]).startswith("NONE")


def test_no_exploit_code_or_vector_detail_in_the_measurement_path() -> None:
    """الجولةُ تقيس أثرَ الحمايات وكلفةَ المهمة — ⛔ لا الناقلَ ولا شيفرتَه."""
    for path in (SCRIPT, ARTIFACT):
        text = path.read_text(encoding="utf-8")
        for banned in (
            "169.254.169.254", "modprobe_path", "SROP", "signal-return-oriented",
            "catflag", "heap groom", "fake string", "OOB heap read",
            "reverse_shell", "__reduce__", "h5py.File(", "os.system(",
        ):
            assert banned not in text, f"{path.name}: {banned}"


def test_boundaries_declare_the_limits_before_the_numbers() -> None:
    payload = build()
    joined = " ".join(payload["boundaries"])
    for needed in ("صفرُ تشغيل نموذج", "arXiv", "STALE", "متوسط", "CPST"):
        assert needed in joined, needed


# ── 2) H59: الدبوسُ في مجاله الصحيح ──────────────────────────────────────────
def test_every_pin_is_complete_so_none_degenerates_to_unpinned() -> None:
    """جوهرُ الجولة: في مجال الدبوس الصحيح لا يظهر `UNPINNED` — فالحكمُ مُدرَّجٌ بالعمر."""
    pins = pin_evaluations(RUNS)
    assert pins["pins_evaluated"] == len(RUNS) == 7
    assert pins["unpinned_count"] == 0
    assert pins["age_governs_not_missingness"] is True
    assert all(not row["missing_fields"] for row in pins["per_pin"])
    assert pins["h59_verdict"] == "CONFIRMED_IN_DOMAIN"


def test_pins_are_stale_by_age_and_that_is_a_quotation_limit_not_a_falsification() -> None:
    """العمرُ 122 يوماً > سقف 90 ⇒ `STALE`؛ والمُؤهِلُ النصّي يمنع قراءتَه تكذيباً."""
    pins = pin_evaluations(RUNS)
    assert pins["report_age_days"] == float((AS_OF - SUITE_ISSUED_ON).days)
    assert pins["report_age_days"] > MAX_REPORT_AGE_DAYS
    assert pins["all_stale_by_age"] is True
    assert pins["state_counts"] == {"STALE": len(RUNS)}
    assert "purpose_qualifier" in pins and "تاريخياً" in pins["purpose_qualifier"]


def test_pin_evaluations_raises_if_an_unpinned_state_appears_in_domain() -> None:
    """⛔ `UNPINNED` هنا يعني دبوساً معطوباً أو إدخالاً ناقصاً — فيُرفع لا يُبلَّغ نتيجة."""
    broken = (
        SuiteRun("m", "", "FILTERS_DISABLED+MITIGATIONS_OFF", 120, 1, (1, 0, 0), (0, 0, 0),
                 None, None, None, None),
    )
    with pytest.raises(BenchmarkPinError, match="UNPINNED"):
        pin_evaluations(broken)


def test_the_same_pin_is_unpinned_outside_its_domain_in_round04() -> None:
    """المقارنةُ التي تجعل `H59` قياساً لا رأياً: دبوسٌ بلا درجةٍ معيارية يبقى كاملاً هنا.

    ⛔ والدليلُ أنّ الحقولَ منطوقة: فالحكمُ `STALE` (عمر) لا `UNPINNED` (نقص)، بينما حالاتُ
    الجولة 04 كانت `UNPINNED` لأنّ الدبوسَ طُبِّق على غير درجةٍ معيارية أصلاً.
    """
    pin = RUNS[0].pin()
    assert isinstance(pin, ReportPin)
    assert pin.missing_fields() == ()
    status = evaluate_pin(pin, AS_OF)
    assert status.state == "STALE"
    assert status.quotable is False
    assert pin.score_points == float(RUNS[0].successes)


# ── 3) SuiteRun: التحقّقُ يرفض المستحيل ──────────────────────────────────────
def _run(**over) -> SuiteRun:
    base = dict(model_id="m", harness="h", safeguard_config="FILTERS_DISABLED+MITIGATIONS_OFF",
                adversary_budget_minutes=120, successes=10, by_domain=(6, 3, 1),
                with_mitigations=(2, 1, 0), cpst_usd=5.0, cost_full_usd=9.0,
                time_min_per_success=20.0, llm_calls_per_success=100.0)
    base.update(over)
    return SuiteRun(**base)


def test_domain_split_must_sum_to_the_total() -> None:
    with pytest.raises(BenchmarkPinError, match="مجموعُ المجالات"):
        _run(by_domain=(6, 3, 2))


def test_mitigated_success_cannot_exceed_unmitigated() -> None:
    """⛔ الحماياتُ لا تزيد النجاح — ومخالفتُه تعني خطأً في الإدخال لا ظاهرة."""
    with pytest.raises(BenchmarkPinError, match="يتجاوز النجاحَ بدونها"):
        _run(successes=10, by_domain=(6, 3, 1), with_mitigations=(9, 2, 0))


def test_flags_and_intended_successes_are_paired_or_both_absent() -> None:
    with pytest.raises(BenchmarkPinError, match="معاً أو لا يُذكران"):
        _run(flags_captured=20)
    with pytest.raises(BenchmarkPinError, match="معاً أو لا يُذكران"):
        _run(successes_on_intended=5)


def test_intended_success_cannot_exceed_flags_captured() -> None:
    with pytest.raises(BenchmarkPinError, match="يتجاوز الأعلامَ المقبوضة"):
        _run(flags_captured=10, successes_on_intended=11)


def test_negative_success_and_nonpositive_budget_and_cpst_are_refused() -> None:
    with pytest.raises(BenchmarkPinError, match="نجاحٌ سالب"):
        _run(successes=-1, by_domain=(-1, 0, 0))
    with pytest.raises(BenchmarkPinError, match="ميزانيةٌ غير موجبة"):
        _run(adversary_budget_minutes=0)
    with pytest.raises(BenchmarkPinError, match="CPST غير موجبة"):
        _run(cpst_usd=0.0)


def test_success_cannot_exceed_suite_size() -> None:
    with pytest.raises(BenchmarkPinError, match="يتجاوز حجمَ الحزمة"):
        _run(successes=SUITE_INSTANCES + 1, by_domain=(SUITE_INSTANCES + 1, 0, 0))


def test_published_table_is_internally_consistent_for_all_seven_pairs() -> None:
    """⛔ النقلُ من المصدر الأوّل يُتحقّق منه حسابياً: المجموعُ = U + B + K لكلّ زوج."""
    for r in RUNS:
        assert sum(r.by_domain) == r.successes, r.model_id
        assert r.mitigated_total is not None and r.mitigated_total <= r.successes, r.model_id
    assert sum(DOMAIN_INSTANCES.values()) == SUITE_INSTANCES


# ── 4) أثرُ الحمايات ─────────────────────────────────────────────────────────
def test_mitigation_effect_reproduces_the_published_tables() -> None:
    m = mitigation_effect(RUNS)
    assert m["successes_mitigations_off"] == 369
    assert m["successes_mitigations_on"] == 69
    # ⚠️ القياسُ يُقرِّب عن قصدٍ لاستقرار البصمة (round 4/6) ⇒ المُقارنةُ بالحرف لا بـapprox:
    #    وتثبيتُ القيمة المُقرَّبة عقدٌ أقوى، فهو يُثبّت ما على القرص لا ما يقصده الكاتب.
    assert m["reduction_factor"] == 5.3478          # round(369/69, 4)
    assert m["residual_share"] == 0.186992          # round(69/369, 6)
    assert m["pairs_measured"] == 7
    assert m["pairs_zeroed_count"] == 4
    assert m["residual_top_pair"] == "claude-mythos-preview"
    assert m["residual_top_share"] == 0.652174      # round(45/69, 6)


def test_zeroed_pairs_are_counted_not_averaged_away() -> None:
    """⛔ متوسطُ نسبةِ انخفاضٍ تشمل أصفاراً يُخفي أنّ أربعةً من سبعة أُصفرت تماماً."""
    m = mitigation_effect(RUNS)
    assert sorted(m["pairs_zeroed"]) == [
        "claude-opus-4.6", "claude-opus-4.7", "gemini-3.1-pro", "glm-5.1",
    ]
    assert len(m["residual_by_pair"]) == 3
    assert sum(d["successes"] for d in m["residual_by_pair"]) == 69


def test_mitigation_effect_refuses_empty_and_zero_denominators() -> None:
    with pytest.raises(BenchmarkPinError, match="صفرُ تشغيلٍ بحمايات"):
        mitigation_effect((_run(with_mitigations=None),))
    with pytest.raises(BenchmarkPinError, match="لا مقامَ لنسبة"):
        mitigation_effect((_run(successes=0, by_domain=(0, 0, 0), with_mitigations=(0, 0, 0)),))


# ── 5) CPST: أوّلُ مرساةٍ من طرفٍ أوّل ───────────────────────────────────────
def test_cpst_band_is_primary_sourced_and_in_usd() -> None:
    c = cpst_band(RUNS)
    assert c["unit"] == "USD_PER_SUCCESSFUL_TASK"
    assert c["band_usd"] == [3.75, 22.99]
    assert c["spread_factor"] == 6.1307             # round(22.99/3.75, 4)
    assert c["median_usd"] == 8.6                   # (8.56 + 8.64) / 2
    assert c["n_disclosed"] == 6
    assert c["n_undisclosed"] == 1
    assert c["undisclosed_models"] == ["claude-mythos-preview"]
    assert "L7" in c["doctrine_compliance"]


def test_undisclosed_cpst_is_declared_as_a_gap_and_never_imputed() -> None:
    """⛔ الغائبُ فجوةٌ معلَنة: فمتوسطُ نطاقٍ ناقصٍ يُقرأ اكتمالاً."""
    c = cpst_band(RUNS)
    assert c["undisclosed_imputed"] is False
    assert "لم تُستكمل" in c["reading"]
    # والنطاقُ المحسوب يستثني الغائب فعلياً — لا يدخله صفرٌ ولا تقدير.
    disclosed = sorted(r.cpst_usd for r in RUNS if r.cpst_usd is not None)
    assert c["band_usd"] == [disclosed[0], disclosed[-1]]
    assert len(disclosed) == c["n_disclosed"]


def test_cpst_spread_is_real_variation_not_measurement_dispersion() -> None:
    """⛔ لا يُعامل كانتشارِ سوق الجولة 04: فهنا أزواجٌ مختلفة لا تقديراتٌ لكميةٍ واحدة."""
    c = cpst_band(RUNS)
    assert "حقيقيٌّ لا ضجيجَ قياس" in c["reading"]
    assert "تشتّتِ سوق" in c["reading"]


def test_cpst_band_refuses_zero_disclosure() -> None:
    with pytest.raises(BenchmarkPinError, match="صفرُ CPST"):
        cpst_band((_run(cpst_usd=None),))


# ── 6) التباعدُ عن الهدف ────────────────────────────────────────────────────
def test_off_target_rate_reproduces_the_published_pairs() -> None:
    o = off_target_rate(RUNS)
    assert o["pairs_measured"] == 2
    top = o["per_pair"][0]
    assert top["model_id"] == "gpt-5.5"
    assert top["flags_captured"] == 210 and top["successes_on_intended"] == 120
    assert top["off_target_count"] == 90
    assert top["off_target_share"] == 0.428571      # round(90/210, 6)
    second = o["per_pair"][1]
    assert second["model_id"] == "claude-mythos-preview"
    assert second["off_target_share"] == 0.30531     # round(69/226, 6)
    assert o["max_off_target_share"] == 0.428571
    assert o["min_off_target_share"] == 0.30531


def test_off_target_reading_names_the_independent_corroboration() -> None:
    """الظاهرةُ نفسها التي روتها الجولة 04 عن المختبر — وهنا يقيسها طرفٌ ثالث."""
    o = off_target_rate(RUNS)
    assert "agent-as-a-judge" in o["reading"]
    assert "grader_divergent" in o["reading"]
    assert "بنيوي" in o["reading"]


def test_off_target_refuses_when_no_flags_are_measured() -> None:
    with pytest.raises(BenchmarkPinError, match="صفرُ زوجٍ بأعلام"):
        off_target_rate((_run(flags_captured=None, successes_on_intended=None),))


# ── 7) تعارُضُ الطرفَين الأوّليين ────────────────────────────────────────────
def test_unsolved_conflict_keeps_both_primaries_and_refuses_to_average() -> None:
    c = unsolved_conflict(RUNS)
    assert c["suite_instances"] == 898
    assert c["berkeley_union_solved"] == 177
    assert c["berkeley_unsolved"] == 721
    assert c["berkeley_unsolved_share"] == 0.802895  # round(721/898, 6)
    assert c["openai_never_solved"] == 198
    assert c["openai_never_solved_share"] == 0.22049  # round(198/898, 6)
    assert c["share_spread_factor"] == 3.6414         # round(721/198, 4)
    assert c["reconciled"] is False
    assert c["reconciliation_basis"] == "PIN_DIFFERENCE_NOT_AVERAGE"


def test_conflict_names_the_four_pin_axes_that_differ() -> None:
    c = unsolved_conflict(RUNS)
    assert len(c["pin_axes_that_differ"]) == 4
    joined = " ".join(c["pin_axes_that_differ"])
    for axis in ("model_id", "adversary_budget", "harness", "safeguard_config"):
        assert axis in joined, axis


def test_conflict_refuses_to_compare_different_suite_sizes() -> None:
    """⛔ كمّيتان مختلفتان لا تُقارنان — القاعدةُ نفسها التي استبعدت تقديراتِ السوق."""
    import scripts.research.measure_benchmark_pin as mod

    saved = mod.OPENAI_UNSOLVED
    try:
        mod.OPENAI_UNSOLVED = dict(saved, suite_total=1000)
        with pytest.raises(BenchmarkPinError, match="ليستا الكمّية نفسها"):
            mod.unsolved_conflict(RUNS)
    finally:
        mod.OPENAI_UNSOLVED = saved


def test_suite_attribution_correction_is_recorded() -> None:
    """⛔ تصحيحُ نسبٍ للجولة 04: الحزمةُ أكاديميةٌ مستقلة، لا حزامُ تقييمٍ تابعٌ للمختبر."""
    payload = build()
    note = payload["suite"]["attribution_note"]
    assert "ليست" in note and "OpenAI" in note
    assert "Berkeley RDI" in payload["suite"]["owner"]
    assert payload["suite"]["instances"] == 898


# ── 8) الميزانيةُ ومرشّحاتُ المزوّد ─────────────────────────────────────────
def test_budget_sensitivity_reproduces_the_published_curve() -> None:
    b = budget_sensitivity()
    assert b["successes_at_120min"] == 127
    assert b["successes_at_360min"] == 204
    assert b["growth_share"] == 0.606299             # round(77/127, 6)
    assert b["plateau_declared"] is False
    assert b["self_declared_undercount"] is True
    assert b["weaker_pair"]["plateau_value"] == 15


def test_budget_growth_is_declared_asymmetric_between_pairs() -> None:
    b = budget_sensitivity()
    assert "غيرُ متناظر" in b["reading"]
    assert "undercounts" in b["reading"]


def test_safeguard_pair_records_a_pair_not_a_ratio_when_the_denominator_is_zero() -> None:
    """⛔ «0 ← 120» ليست `inf` ولا `0` — فالغيابُ لا يُصفَّر (قاعدة D-212)."""
    s = safeguard_pair()
    assert s["successes_default_filters"] == 0
    assert s["successes_filters_disabled"] == 120
    assert s["ratio"] is None
    assert s["recorded_as"] == "PAIR_NOT_RATIO"
    assert "ZERO_DENOMINATOR" in s["ratio_undefined_reason"]


def test_safeguard_pair_refuses_when_both_sides_are_zero() -> None:
    import scripts.research.measure_benchmark_pin as mod

    saved = mod.SAFEGUARD_PAIR
    try:
        mod.SAFEGUARD_PAIR = dict(saved, default_filters_successes=0, filters_disabled_successes=0)
        with pytest.raises(BenchmarkPinError, match="صفرٌ في الطرفين"):
            mod.safeguard_pair()
    finally:
        mod.SAFEGUARD_PAIR = saved


def test_safeguard_reading_ties_the_result_to_the_ab_pair_thesis() -> None:
    s = safeguard_pair()
    assert "safeguard_config" in s["reading"]
    assert "(A,B)" in s["reading"]


# ── 9) التناقضُ الداخلي يُسجَّل ولا يُحلّ صمتاً ──────────────────────────────
def test_self_contradiction_d1_is_recorded_unresolved_with_a_reason() -> None:
    c = self_contradictions()
    assert len(c) == 1
    d1 = c[0]
    assert d1["id"] == "D1"
    assert d1["values"] == {"table1_successes": 157, "figure5_at_120min": 127}
    assert d1["delta"] == 30
    assert d1["resolved"] is False
    assert "اختلاق" in d1["why_unresolved"]
    assert "لا يُقتبس" in d1["handling"]


def test_build_refuses_a_domain_split_that_does_not_sum_to_the_suite() -> None:
    import scripts.research.measure_benchmark_pin as mod

    saved = dict(mod.DOMAIN_INSTANCES)
    try:
        mod.DOMAIN_INSTANCES["KERNEL"] = 999
        with pytest.raises(BenchmarkPinError, match="مجموعُ مجالات الحزمة"):
            mod.build()
    finally:
        mod.DOMAIN_INSTANCES.clear()
        mod.DOMAIN_INSTANCES.update(saved)


def test_build_refuses_a_duplicated_model_row() -> None:
    import scripts.research.measure_benchmark_pin as mod

    saved = mod.RUNS
    try:
        mod.RUNS = (RUNS[0], RUNS[0])
        with pytest.raises(BenchmarkPinError, match="نموذجٌ مكرَّر"):
            mod.build()
    finally:
        mod.RUNS = saved


# ── 10) حدودُ الدبوس المعلَنة ────────────────────────────────────────────────
def test_pin_field_limitations_are_declared_not_hidden() -> None:
    """قيدان في `ReportPin` نفسيهما — يُعلَنان لأنّ إخفاءَهما يُقرأ كمالاً."""
    limits = build()["results"]["pin_field_limitations"]
    assert len(limits) == 2
    fields = {lim["field"] for lim in limits}
    assert "safeguard_config" in fields
    assert any("غرض" in lim["limitation"] for lim in limits)
    for lim in limits:
        assert lim["handling"] and lim["consequence"]


def test_every_result_block_carries_its_own_source() -> None:
    """⛔ لا كتلةَ نتيجةٍ بلا مصدر — فالرقمُ بلا نسبٍ يُقرأ قياساً لنا."""
    results = build()["results"]
    for key in ("mitigation_effect", "cpst_band", "off_target_rate",
                "unsolved_conflict", "budget_sensitivity", "safeguard_pair"):
        assert results[key]["source"], key
        assert "2026-05-13" in results[key]["source"] or "2026-08-26" in results[key]["source"], key


def test_flat_decision_heads_match_their_nested_blocks() -> None:
    """الرؤوسُ المسطّحة تُشتقّ من الكتل — ⛔ لا نسخَ يدوياً ينفصل عن مصدره."""
    r = build()["results"]
    assert r["mitigation_reduction_factor"] == r["mitigation_effect"]["reduction_factor"]
    assert r["mitigation_residual_share"] == r["mitigation_effect"]["residual_share"]
    assert r["pairs_zeroed_by_mitigations"] == r["mitigation_effect"]["pairs_zeroed_count"]
    assert r["residual_top_share"] == r["mitigation_effect"]["residual_top_share"]
    assert r["cpst_band_usd"] == r["cpst_band"]["band_usd"]
    assert r["cpst_spread_factor"] == r["cpst_band"]["spread_factor"]
    assert r["cpst_undisclosed_count"] == r["cpst_band"]["n_undisclosed"]
    assert r["max_off_target_share"] == r["off_target_rate"]["max_off_target_share"]
    assert r["unsolved_share_spread_factor"] == r["unsolved_conflict"]["share_spread_factor"]
    assert r["unsolved_reconciled"] == r["unsolved_conflict"]["reconciled"]
    assert r["budget_growth_share"] == r["budget_sensitivity"]["growth_share"]
    assert r["safeguard_ratio"] == r["safeguard_pair"]["ratio"]
    assert r["pins_unpinned_count"] == r["pin_evaluations"]["unpinned_count"]
    assert r["h59_verdict"] == r["pin_evaluations"]["h59_verdict"]


# ── 11) حراسُ الوحدة ─────────────────────────────────────────────────────────
def test_module_is_stdlib_only() -> None:
    """⛔ صفرُ تبعياتٍ خارجية — فالقياسُ يجب أن يُعاد في أيّ بيئةٍ بلا تثبيت."""
    tree = ast.parse(SCRIPT.read_text(encoding="utf-8"))
    allowed = {"__future__", "argparse", "hashlib", "json", "sys", "dataclasses",
               "datetime", "pathlib", "shared.research.assurance_window", "shared"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert alias.name.split(".")[0] in allowed, alias.name
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            assert mod.split(".")[0] in allowed or mod in allowed, mod


def test_module_has_no_network_or_shell_escape() -> None:
    tree = ast.parse(SCRIPT.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            assert (node.module or "").split(".")[0] not in {"urllib", "requests", "socket", "http", "subprocess"}
        elif isinstance(node, ast.Import):
            for alias in node.names:
                assert alias.name.split(".")[0] not in {"urllib", "requests", "socket", "http", "subprocess", "os"}


def test_as_of_is_not_read_from_the_clock() -> None:
    """⛔ `AS_OF` ثابتٌ منطوق: فكلّ عمرٍ في الملفّ يُنسب إليه، وقراءتُه من الساعة تُفقد
    إعادةَ البناء حرفيتها."""
    assert isinstance(AS_OF, date)
    assert AS_OF == date(2026, 9, 12)
    text = SCRIPT.read_text(encoding="utf-8")
    assert re.search(r"AS_OF = date\(2026, 9, 12\)", text)


def test_openai_claim_is_attributed_to_the_suite_not_owned_by_it() -> None:
    assert OPENAI_UNSOLVED["suite_total"] == SUITE_INSTANCES
    assert "⛔ وليس مالكُ الحزمة" in OPENAI_UNSOLVED["source"]
