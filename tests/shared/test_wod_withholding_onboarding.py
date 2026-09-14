"""اختباراتُ الدفعة الثامنة (WOD) — انحرافُ الاستقطاع والتأهيل.

ثلاثةُ أصنافٍ من الاختبارات، وهي مقصودةٌ لا حشو:

1. **حراسةُ القاعدة**: صفرٌ داخليٌّ لا يحتاج معاهدة، ونصٌّ ناقصٌ يُنشئ `None` لا صفراً —
   أي أنّ «مجهول» و«معفى» لا يُخفق بينهما.
2. **البرهانُ السلبيّ**: نُفسِد المُدخَل عمداً ونتوقّع أن تُصرخ البوّابة (شروطُ القتل)،
   وأن يمتنع المخطِّطُ عن القدرات المحظورة بعقيدة (K1/K5).
3. **مطابقةُ المودَع**: الملفُّ المقيس في `docs/research/WOD_MEASUREMENTS.json` يُعاد
   حسابه هنا، فيفشل الاختبارُ إن انحرف القرصُ عن الشيفرة.
"""

from __future__ import annotations

import json
from dataclasses import replace
from itertools import combinations
from pathlib import Path

import pytest

from shared.research.withholding_onboarding import (
    AS_OF,
    BP_SCALE,
    DEFAULT_HELD,
    DEFAULT_RAIL_CONFLICTS,
    DEFAULT_UNLOCK_BUDGET,
    STDLIB_ONLY,
    AbStatus,
    Archetype,
    Capability,
    Catalog,
    Characterization,
    Doctrine,
    InversionState,
    Jurisdiction,
    KillSwitch,
    RateBasis,
    Requirement,
    RequirementKind,
    TreatyState,
    algeria_markets,
    characterization_inversion,
    effective_rate,
    entry_frontier,
    evaluate,
    held_capabilities,
    inputs_fingerprint,
    kill_switches,
    measure_all,
    minimum_unlock_set,
    module_imports,
    net_capture,
    reference_ladder,
    summarize,
    wod_archetypes,
    wod_catalog,
)

ROOT = Path(__file__).resolve().parents[2]
MEASUREMENT = ROOT / "docs" / "research" / "WOD_MEASUREMENTS.json"
MODULE = ROOT / "shared" / "research" / "withholding_onboarding.py"


@pytest.fixture(scope="module")
def markets() -> tuple[Jurisdiction, ...]:
    return algeria_markets()


@pytest.fixture(scope="module")
def catalog() -> Catalog:
    return wod_catalog()


@pytest.fixture(scope="module")
def archetypes() -> tuple[Archetype, ...]:
    return wod_archetypes()


@pytest.fixture(scope="module")
def held(catalog: Catalog) -> frozenset[str]:
    return held_capabilities(catalog, held=DEFAULT_HELD)


def _by_code(markets: tuple[Jurisdiction, ...], code: str) -> Jurisdiction:
    return next(item for item in markets if item.code == code)


# ══════════════════════════════════════════════════════════════════════════════
# 1) طبقةُ الاستقطاع
# ══════════════════════════════════════════════════════════════════════════════


def test_us_service_is_quotable_zero(markets: tuple[Jurisdiction, ...]) -> None:
    verdict = effective_rate(_by_code(markets, "US"), Characterization.SERVICE)
    assert verdict.basis is RateBasis.DOMESTIC_ZERO
    assert verdict.is_quotable
    assert verdict.rate_bp_hi == 0
    assert verdict.net_multiplier_lo() == 1.0


def test_us_royalty_is_30_percent_without_treaty(markets: tuple[Jurisdiction, ...]) -> None:
    verdict = effective_rate(_by_code(markets, "US"), Characterization.ROYALTY)
    assert verdict.basis is RateBasis.DOMESTIC_NO_TREATY
    assert verdict.rate_bp_hi == BP_SCALE * 30 // 100
    assert verdict.net_multiplier_lo() == 0.7


def test_us_royalty_uplift_is_the_documented_42_86_percent(
    markets: tuple[Jurisdiction, ...],
) -> None:
    verdict = effective_rate(_by_code(markets, "US"), Characterization.ROYALTY)
    assert verdict.uplift_required() == 0.428571


def test_france_service_is_blocked_not_guessed(markets: tuple[Jurisdiction, ...]) -> None:
    verdict = effective_rate(_by_code(markets, "FR"), Characterization.SERVICE)
    assert verdict.basis is RateBasis.TREATY_COVERAGE_UNSTATED
    assert not verdict.is_quotable
    assert verdict.rate_bp_lo is None and verdict.rate_bp_hi is None
    assert "TREATY" not in verdict.reason_ar  # السببُ عربيٌّ منطوق لا رمزٌ فقط
    assert "33.33%" in verdict.reason_ar


def test_italy_and_saudi_service_are_unstated_not_zero(
    markets: tuple[Jurisdiction, ...],
) -> None:
    for code in ("IT", "SA"):
        verdict = effective_rate(_by_code(markets, code), Characterization.SERVICE)
        assert verdict.basis is RateBasis.DOMESTIC_UNSTATED
        assert verdict.rate_bp_lo is None


def test_domestic_zero_does_not_require_treaty_text(
    markets: tuple[Jurisdiction, ...],
) -> None:
    """القاعدة الحاكمة: الصفرُ الداخلي قابلٌ للاقتباس ولو كانت حالةُ المعاهدة متعارضة."""

    netherlands = _by_code(markets, "NL")
    assert netherlands.treaty is TreatyState.UNSTATED
    for characterization in (Characterization.SERVICE, Characterization.ROYALTY):
        verdict = effective_rate(netherlands, characterization)
        assert verdict.is_quotable and verdict.basis is RateBasis.DOMESTIC_ZERO


def test_treaty_cap_can_be_a_band_not_a_number(markets: tuple[Jurisdiction, ...]) -> None:
    france = effective_rate(_by_code(markets, "FR"), Characterization.ROYALTY)
    assert france.basis is RateBasis.TREATY_CAP
    assert (france.rate_bp_lo, france.rate_bp_hi) == (500, 1000)
    spain = effective_rate(_by_code(markets, "ES"), Characterization.ROYALTY)
    assert (spain.rate_bp_lo, spain.rate_bp_hi) == (700, 1400)


def test_germany_royalty_is_soli_adjusted(markets: tuple[Jurisdiction, ...]) -> None:
    verdict = effective_rate(_by_code(markets, "DE"), Characterization.ROYALTY)
    assert verdict.rate_bp_lo == 1000  # سقف المعاهدة
    assert verdict.net_multiplier_lo() == 0.9


def test_canada_service_is_zero_only_because_work_is_abroad(
    markets: tuple[Jurisdiction, ...],
) -> None:
    verdict = effective_rate(_by_code(markets, "CA"), Characterization.SERVICE)
    assert verdict.is_quotable and verdict.rate_bp_hi == 0
    assert "خارج" in verdict.reason_ar or "كند" in verdict.reason_ar


def test_every_cell_has_a_reason_and_none_contains_nan(
    markets: tuple[Jurisdiction, ...],
) -> None:
    for jurisdiction in markets:
        for characterization in (Characterization.SERVICE, Characterization.ROYALTY):
            verdict = effective_rate(jurisdiction, characterization)
            assert verdict.reason_ar.strip()
            for value in (verdict.rate_pct_lo, verdict.rate_pct_hi):
                assert value is None or 0 <= value < 100


def test_only_booleans_are_used_for_quotability(markets: tuple[Jurisdiction, ...]) -> None:
    verdict = effective_rate(_by_code(markets, "FR"), Characterization.SERVICE)
    assert verdict.is_quotable is False
    assert verdict.net_multiplier_lo() is None
    assert verdict.uplift_required() is None


def test_jurisdiction_rejects_out_of_range_rates(markets: tuple[Jurisdiction, ...]) -> None:
    with pytest.raises(ValueError):
        replace(_by_code(markets, "US"), royalty_domestic_bp=BP_SCALE)


def test_jurisdiction_rejects_inverted_royalty_band(
    markets: tuple[Jurisdiction, ...],
) -> None:
    with pytest.raises(ValueError):
        replace(_by_code(markets, "FR"), royalty_treaty_bp=1500, royalty_treaty_alt_bp=500)


# ══════════════════════════════════════════════════════════════════════════════
# 2) وجهُ التعرّض — الانقلابُ المعبّر عنه بالأرقام
# ══════════════════════════════════════════════════════════════════════════════


def test_license_is_worse_where_services_are_exempt(
    markets: tuple[Jurisdiction, ...],
) -> None:
    for code in ("US", "UK", "DE", "CA"):
        assert (
            characterization_inversion(_by_code(markets, code), use_domestic=True)
            is InversionState.ROYALTY_WORSE
        )


def test_services_are_exposed_where_no_domestic_exemption_exists(
    markets: tuple[Jurisdiction, ...],
) -> None:
    for code in ("FR", "ES"):
        assert (
            characterization_inversion(_by_code(markets, code), use_domestic=True)
            is InversionState.BOTH_EXPOSED
        )


def test_zero_markets_are_labelled_as_such(markets: tuple[Jurisdiction, ...]) -> None:
    for code in ("NL", "CH", "AE"):
        assert (
            characterization_inversion(_by_code(markets, code), use_domestic=True)
            is InversionState.BOTH_ZERO
        )


def test_unstated_markets_never_become_tied(markets: tuple[Jurisdiction, ...]) -> None:
    for code in ("IT", "SA"):
        assert (
            characterization_inversion(_by_code(markets, code), use_domestic=True)
            is InversionState.UNSTATED
        )


def test_effective_inversion_uses_quotable_cells_only(
    markets: tuple[Jurisdiction, ...],
) -> None:
    assert characterization_inversion(_by_code(markets, "US")) is InversionState.ROYALTY_WORSE
    assert (characterization_inversion(_by_code(markets, "FR")) is InversionState.UNSTATED) or (
        characterization_inversion(_by_code(markets, "FR")) is InversionState.BOTH_ZERO
    )


# ══════════════════════════════════════════════════════════════════════════════
# 3) طبقةُ التأهيل — الحالاتُ والمنعُ المسند
# ══════════════════════════════════════════════════════════════════════════════


def test_entry_frontier_is_exactly_the_unreferenced_direct_buyer(
    archetypes: tuple[Archetype, ...], catalog: Catalog, held: frozenset[str]
) -> None:
    frontier = entry_frontier(archetypes, catalog, held)
    assert [item.archetype for item in frontier] == ["A0_us_startup_pilot"]


def test_marketplace_archetype_is_blocked_by_doctrine_not_by_price(
    archetypes: tuple[Archetype, ...], catalog: Catalog, held: frozenset[str]
) -> None:
    verdict = next(
        item
        for item in (evaluate(a, catalog, held) for a in archetypes)
        if item.archetype == "A9_marketplace_mor"
    )
    assert verdict.status is AbStatus.BLOCKED_DOCTRINE
    assert "psp_jurisdiction_support" in verdict.missing
    assert "K5" in verdict.reason_ar or "محظورة" in verdict.reason_ar


def test_reference_demanding_archetypes_cannot_be_first(
    archetypes: tuple[Archetype, ...], catalog: Catalog, held: frozenset[str]
) -> None:
    verdicts = {item.archetype: item for item in (evaluate(a, catalog, held) for a in archetypes)}
    for code in ("A2_us_enterprise_sec", "A6_eu_public_body", "A11_nl_reference_buyer"):
        assert verdicts[code].status is AbStatus.AFTER_FIRST_INVOICE
    assert "commercial_reference" in verdicts["A11_nl_reference_buyer"].missing


def test_french_archetype_pays_for_written_clearance(
    archetypes: tuple[Archetype, ...], catalog: Catalog, held: frozenset[str]
) -> None:
    france = next(item for item in archetypes if item.id == "A5_fr_enterprise")
    verdict = evaluate(france, catalog, held)
    assert verdict.status is AbStatus.UNLOCKABLE
    assert "tax_clearance" in verdict.missing
    assert verdict.effort_units == 2 + 3 + 6  # مراجعةُ عقد + حزمةُ بيانات + تحقّقٌ كتابي


def test_unlockable_effort_is_the_cheapest_allowed_route(
    archetypes: tuple[Archetype, ...], catalog: Catalog, held: frozenset[str]
) -> None:
    lab = next(item for item in archetypes if item.id == "A1_us_lab_eval")
    verdict = evaluate(lab, catalog, held)
    assert verdict.status is AbStatus.UNLOCKABLE
    assert verdict.effort_units == 2 + 4


def test_evaluate_reason_lists_every_missing_requirement(
    archetypes: tuple[Archetype, ...], catalog: Catalog, held: frozenset[str]
) -> None:
    lab = next(item for item in archetypes if item.id == "A1_us_lab_eval")
    verdict = evaluate(lab, catalog, held)
    for requirement_id in verdict.missing:
        assert requirement_id in verdict.reason_ar


def test_held_capabilities_appends_references_only_on_request(
    catalog: Catalog,
) -> None:
    base = held_capabilities(catalog, held=("form_filling", "reference_1"))
    assert base == frozenset({"form_filling"})
    extended = held_capabilities(
        catalog, held=("form_filling", "reference_1"), allow_after_first_invoice=True
    )
    assert extended == frozenset({"form_filling", "reference_1"})


def test_unknown_capability_in_stack_is_an_error(catalog: Catalog) -> None:
    with pytest.raises(KeyError):
        held_capabilities(catalog, held=("not_a_capability",))


def test_catalog_rejects_capability_pointing_at_unknown_requirement() -> None:
    requirements = {"r1": Requirement("r1", "متطلَّب", RequirementKind.LEGAL, ("c1",))}
    capabilities = {"c1": Capability("c1", "قدرة", 1, ("r2",))}
    with pytest.raises(ValueError):
        Catalog(requirements=requirements, capabilities=capabilities)


def test_catalog_rejects_unsatisfiable_requirement() -> None:
    requirements = {"r1": Requirement("r1", "متطلَّب", RequirementKind.LEGAL, ())}
    with pytest.raises(ValueError):
        Catalog(requirements=requirements, capabilities={})


def test_after_first_invoice_capability_cannot_carry_planned_effort() -> None:
    with pytest.raises(ValueError):
        Capability("ref", "مرجع", 3, ("commercial_reference",), after_first_invoice=True)


def test_archetype_without_requirements_is_rejected() -> None:
    with pytest.raises(ValueError):
        Archetype("A", "US", "فئةٌ فارغة", ())


# ══════════════════════════════════════════════════════════════════════════════
# 4) خطةُ الفتح — البحثُ الشامل وحراسةُ العقيدة
# ══════════════════════════════════════════════════════════════════════════════


def test_plan_matches_exhaustive_bruteforce(
    archetypes: tuple[Archetype, ...], catalog: Catalog, held: frozenset[str]
) -> None:
    """الأمثلُ يُتحقَّق منه بحسابٍ مستقلّ داخل الاختبار لا بالثقة في الدالّة."""

    budget = DEFAULT_UNLOCK_BUDGET
    candidates = [
        cap
        for cap in catalog.capabilities.values()
        if cap.id not in held and cap.doctrine is Doctrine.ALLOWED and not cap.after_first_invoice
    ]
    baseline = {
        archetype.id
        for archetype in archetypes
        if evaluate(archetype, catalog, held).status is AbStatus.PASS
    }
    best_key: tuple[int, int, tuple[str, ...]] | None = None
    for size in range(len(candidates) + 1):
        for subset in combinations(candidates, size):
            effort = sum(cap.effort_units for cap in subset)
            if effort > budget:
                continue
            stack = frozenset(held | {cap.id for cap in subset})
            opened = tuple(
                sorted(
                    archetype.id
                    for archetype in archetypes
                    if archetype.id not in baseline
                    and evaluate(archetype, catalog, stack).status is AbStatus.PASS
                )
            )
            key = (-len(opened), effort, tuple(sorted(cap.id for cap in subset)))
            if best_key is None or key < best_key:
                best_key = key
    plan = minimum_unlock_set(archetypes, catalog, held, budget_units=budget)
    assert best_key is not None
    assert (-len(plan.opened), plan.effort_units, tuple(sorted(plan.chosen))) == best_key


def test_plan_opens_three_markets_with_two_capabilities(
    archetypes: tuple[Archetype, ...], catalog: Catalog, held: frozenset[str]
) -> None:
    plan = minimum_unlock_set(archetypes, catalog, held, budget_units=DEFAULT_UNLOCK_BUDGET)
    assert plan.chosen == ("dpa_sccs_pack", "msa_nda_review")
    assert plan.opened == ("A10_ca_private", "A3_uk_private", "A4_de_private")
    assert plan.effort_units == 5


def test_plan_never_chooses_a_doctrine_forbidden_capability(
    archetypes: tuple[Archetype, ...], catalog: Catalog, held: frozenset[str]
) -> None:
    forbidden = {
        cap.id for cap in catalog.capabilities.values() if cap.doctrine is not Doctrine.ALLOWED
    }
    for budget in range(0, 12):
        plan = minimum_unlock_set(archetypes, catalog, held, budget_units=budget)
        assert not set(plan.chosen) & forbidden


def test_plan_budget_zero_opens_nothing(
    archetypes: tuple[Archetype, ...], catalog: Catalog, held: frozenset[str]
) -> None:
    plan = minimum_unlock_set(archetypes, catalog, held, budget_units=0)
    assert plan.chosen == () and plan.opened == () and plan.effort_units == 0


def test_plan_rejects_negative_budget(
    archetypes: tuple[Archetype, ...], catalog: Catalog, held: frozenset[str]
) -> None:
    with pytest.raises(ValueError):
        minimum_unlock_set(archetypes, catalog, held, budget_units=-1)


def test_reference_ladder_opens_exactly_the_reference_only_buyer(
    archetypes: tuple[Archetype, ...], catalog: Catalog, held: frozenset[str]
) -> None:
    plan = minimum_unlock_set(archetypes, catalog, held, budget_units=DEFAULT_UNLOCK_BUDGET)
    stack = frozenset(held | set(plan.chosen))
    first_round, second_round = reference_ladder(archetypes, catalog, stack)
    assert set(first_round) == {
        "A0_us_startup_pilot",
        "A3_uk_private",
        "A4_de_private",
        "A10_ca_private",
    }
    newly = {
        verdict.archetype for verdict in second_round if verdict.status is AbStatus.PASS
    } - set(first_round)
    assert newly == {"A11_nl_reference_buyer"}


# ══════════════════════════════════════════════════════════════════════════════
# 5) الالتقاطُ الصافي — لا رقمَ على خليةٍ مجهولة ولا على سكّةٍ مخرومة
# ══════════════════════════════════════════════════════════════════════════════


def test_net_capture_multiplies_passability_by_net_rate(
    archetypes: tuple[Archetype, ...],
    catalog: Catalog,
    held: frozenset[str],
    markets: tuple[Jurisdiction, ...],
) -> None:
    archetype = next(item for item in archetypes if item.id == "A0_us_startup_pilot")
    verdict = evaluate(archetype, catalog, held)
    capture = net_capture(
        archetype,
        verdict,
        {item.code: item for item in markets},
        characterization=Characterization.SERVICE,
    )
    assert capture.net_capture == 1.0


def test_net_capture_is_none_on_unstated_cell(
    archetypes: tuple[Archetype, ...],
    catalog: Catalog,
    held: frozenset[str],
    markets: tuple[Jurisdiction, ...],
) -> None:
    archetype = next(item for item in archetypes if item.id == "A0_us_startup_pilot")
    verdict = evaluate(archetype, catalog, held)
    france_like = replace(archetype, id="A0_like_fr", market="FR")
    capture = net_capture(
        france_like,
        verdict,
        {item.code: item for item in markets},
        characterization=Characterization.SERVICE,
    )
    assert capture.net_capture is None
    assert "لا صافٍ" in capture.reason_ar


def test_net_capture_is_none_on_structurally_breaching_rail(
    archetypes: tuple[Archetype, ...],
    catalog: Catalog,
    held: frozenset[str],
    markets: tuple[Jurisdiction, ...],
) -> None:
    """القناةُ التي تُنتج خرقاً نظاميّاً لا تُنتج رقماً — البرهانُ السلبيّ للسكّة."""

    archetype = next(item for item in archetypes if item.id == "A0_us_startup_pilot")
    verdict = evaluate(archetype, catalog, held)
    capture = net_capture(
        archetype,
        verdict,
        {item.code: item for item in markets},
        characterization=Characterization.SERVICE,
        rail_conflict=DEFAULT_RAIL_CONFLICTS["A9_marketplace_mor"],
    )
    assert capture.net_capture is None
    assert "خرق" in capture.reason_ar


def test_net_capture_is_zero_when_archetype_is_not_passable(
    archetypes: tuple[Archetype, ...],
    catalog: Catalog,
    held: frozenset[str],
    markets: tuple[Jurisdiction, ...],
) -> None:
    lab = next(item for item in archetypes if item.id == "A1_us_lab_eval")
    verdict = evaluate(lab, catalog, held)
    capture = net_capture(
        lab,
        verdict,
        {item.code: item for item in markets},
        characterization=Characterization.SERVICE,
    )
    assert capture.passable is False and capture.net_capture == 0.0
    assert "بالعبور" in capture.reason_ar


def test_net_capture_on_unknown_market_is_none(
    archetypes: tuple[Archetype, ...],
    catalog: Catalog,
    held: frozenset[str],
    markets: tuple[Jurisdiction, ...],
) -> None:
    archetype = next(item for item in archetypes if item.id == "A0_us_startup_pilot")
    unknown = replace(archetype, market="ZZ")
    capture = net_capture(
        unknown,
        evaluate(archetype, catalog, held),
        {item.code: item for item in markets},
        characterization=Characterization.SERVICE,
    )
    assert capture.net_capture is None and capture.passable is False


# ══════════════════════════════════════════════════════════════════════════════
# 6) شروطُ القتل — براهينُ سلبية
# ══════════════════════════════════════════════════════════════════════════════


def test_no_kill_switch_fires_on_the_declared_data(
    archetypes: tuple[Archetype, ...],
    catalog: Catalog,
    held: frozenset[str],
    markets: tuple[Jurisdiction, ...],
) -> None:
    assert (
        kill_switches(markets, archetypes, catalog, held, budget_units=DEFAULT_UNLOCK_BUDGET) == ()
    )


def test_k4_fires_when_budget_forbids_every_unlock(
    archetypes: tuple[Archetype, ...],
    catalog: Catalog,
    held: frozenset[str],
    markets: tuple[Jurisdiction, ...],
) -> None:
    fired = kill_switches(markets, archetypes, catalog, held, budget_units=0)
    assert KillSwitch.K4_NO_UNLOCK_WITHIN_BUDGET in fired


def test_k5_fires_when_every_rate_is_unstated(
    archetypes: tuple[Archetype, ...],
    catalog: Catalog,
    held: frozenset[str],
    markets: tuple[Jurisdiction, ...],
) -> None:
    blanked = tuple(
        replace(
            item,
            service_domestic_bp=None,
            service_treaty_bp=None,
            royalty_domestic_bp=None,
            royalty_treaty_bp=None,
            royalty_treaty_alt_bp=None,
        )
        for item in markets
    )
    fired = kill_switches(blanked, archetypes, catalog, held, budget_units=DEFAULT_UNLOCK_BUDGET)
    assert KillSwitch.K5_ALL_RATES_UNSTATED in fired


def test_k1_fires_when_characterization_stops_mattering(
    archetypes: tuple[Archetype, ...],
    catalog: Catalog,
    held: frozenset[str],
    markets: tuple[Jurisdiction, ...],
) -> None:
    flat = tuple(
        replace(
            item,
            service_domestic_bp=1000,
            service_treaty_bp=None,
            royalty_domestic_bp=1000,
            royalty_treaty_bp=None,
            royalty_treaty_alt_bp=None,
            treaty=TreatyState.NONE,
        )
        for item in markets
    )
    fired = kill_switches(flat, archetypes, catalog, held, budget_units=DEFAULT_UNLOCK_BUDGET)
    assert KillSwitch.K1_NO_CHARACTERIZATION_EFFECT in fired


def test_k2_fires_when_no_market_exposes_services(
    archetypes: tuple[Archetype, ...],
    catalog: Catalog,
    held: frozenset[str],
    markets: tuple[Jurisdiction, ...],
) -> None:
    """لو عُفيَ مقابلُ الخدمة في كلّ سوق لسقطت أطروحةُ «الوصفةُ الافتراضية غير آمنة»."""

    safe = tuple(
        replace(
            item,
            service_domestic_bp=0,
            service_treaty_bp=None,
            royalty_domestic_bp=max(1, item.royalty_domestic_bp or 1),
        )
        for item in markets
    )
    fired = kill_switches(safe, archetypes, catalog, held, budget_units=DEFAULT_UNLOCK_BUDGET)
    assert KillSwitch.K2_NO_INVERSION_ANYWHERE in fired


def test_k3_fires_when_everything_passes(catalog: Catalog) -> None:
    easy = (
        Archetype("E1", "US", "فئةٌ تطلب الحدَّ الأدنى", ("legal_capacity",)),
        Archetype("E2", "DE", "فئةٌ تطلب الحدَّ الأدنى", ("sanctions_screen",)),
    )
    held = held_capabilities(catalog, held=DEFAULT_HELD)
    fired = kill_switches(
        algeria_markets(), easy, catalog, held, budget_units=DEFAULT_UNLOCK_BUDGET
    )
    assert KillSwitch.K3_EVERYTHING_PASSES in fired


# ══════════════════════════════════════════════════════════════════════════════
# 7) نزاهةُ الحزمة والمودَع
# ══════════════════════════════════════════════════════════════════════════════


def test_module_imports_are_stdlib_only() -> None:
    imports = set(module_imports(MODULE))
    assert imports <= STDLIB_ONLY, f"استيراداتٌ خارج المسموح: {sorted(imports - STDLIB_ONLY)}"
    assert not imports & {"app", "microservices", "shared"}


def test_measurement_file_matches_recomputation() -> None:
    committed = json.loads(MEASUREMENT.read_text(encoding="utf-8"))
    computed = measure_all()
    for key in ("batch", "as_of", "declared_zeros", "inputs_fingerprint", "results"):
        assert json.dumps(committed[key], ensure_ascii=False, sort_keys=True) == json.dumps(
            computed[key], ensure_ascii=False, sort_keys=True
        ), f"انحرافٌ في الحقل {key}"


def test_measurement_declares_zeros_and_no_revenue() -> None:
    committed = json.loads(MEASUREMENT.read_text(encoding="utf-8"))
    zeros = committed["declared_zeros"]
    assert zeros["revenue_claim"] == "NONE"
    assert zeros["model_runs_executed"] == 0
    assert zeros["client_measurements"] == 0
    assert committed["as_of"] == AS_OF.isoformat()
    assert committed["batch"] == "WOD-8"


def test_summary_counters_add_up(
    archetypes: tuple[Archetype, ...],
    catalog: Catalog,
    held: frozenset[str],
    markets: tuple[Jurisdiction, ...],
) -> None:
    results = summarize(
        markets,
        archetypes,
        catalog,
        held,
        budget_units=DEFAULT_UNLOCK_BUDGET,
        rail_conflicts=DEFAULT_RAIL_CONFLICTS,
    )
    cells = results["cells"]
    assert cells["quotable"] + cells["blocked"] == cells["total"]
    assert cells["total"] == 2 * len(markets)
    assert sum(cells["basis_counts"].values()) == cells["total"]
    statuses = results["archetypes"]["status_counts"]
    assert sum(statuses.values()) == results["archetypes"]["total"] == len(archetypes)
    assert len(results["captures"]) == 2 * len(archetypes)


def test_measurement_is_deterministic() -> None:
    assert json.dumps(measure_all(), ensure_ascii=False, sort_keys=True) == json.dumps(
        measure_all(), ensure_ascii=False, sort_keys=True
    )


def test_fingerprint_changes_when_a_rate_changes(markets: tuple[Jurisdiction, ...]) -> None:
    from shared.research.withholding_onboarding import jurisdiction_view

    base = {"jurisdictions": [jurisdiction_view(item) for item in markets]}
    mutated = {
        "jurisdictions": [
            jurisdiction_view(
                replace(item, royalty_domestic_bp=2500) if item.code == "US" else item
            )
            for item in markets
        ]
    }
    assert inputs_fingerprint(base) != inputs_fingerprint(mutated)


def test_no_float_artifacts_in_serialized_measurement() -> None:
    text = MEASUREMENT.read_text(encoding="utf-8")
    assert "NaN" not in text and "Infinity" not in text
