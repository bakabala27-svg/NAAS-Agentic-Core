"""اختباراتُ سجلِّ قنوات التحصيل — FIV (الدفعة العاشرة).

تُثبِت أنّ الأرقامَ محسوبةٌ لا مكتوبة: النطاقاتُ بلا مراكز، والرسمُ لا ينتقل بين
فئات الأصول، والغائبُ `None` بسببٍ منطوق، والبصمةُ حتميةٌ — وأنّ شروطَ القتل **قادرةٌ
على الإطلاق** (شرطٌ لا يُطلَق زينةٌ تُقرأ حماية).
"""

from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from shared.research.first_invoice import (
    AS_OF,
    BATCH,
    CHANNELS,
    CONFLICTS,
    FeeScheduleMissingError,
    apply_fee,
    audit_band,
    contradictions,
    fee_schedule,
    fiv_policy,
    inputs_fingerprint,
    kill_switches,
    listing_band,
    measure_all,
    net_probe,
    per_unit,
    rank_for_first_test,
    settle_summary,
)

TOOL = REPO_ROOT / "shared" / "research" / "first_invoice.py"


def test_frozen_identity() -> None:
    assert AS_OF == "2026-09-15"
    assert BATCH == "FIV-10"


def test_five_channels_with_stable_ids() -> None:
    assert [c.channel_id for c in CHANNELS] == [
        "CH1_prime_open",
        "CH2_prime_app",
        "CH3_prime_sprint",
        "CH4_datavendor_listing",
        "CH5_datavendor_codebase",
    ]


def test_every_channel_has_source_and_entry_note() -> None:
    for channel in CHANNELS:
        assert channel.sources, channel.channel_id
        assert channel.entry_note_ar.strip(), channel.channel_id
        assert channel.entry in {"OPEN", "APPROVAL", "REVIEW_5D"}, channel.channel_id


def test_per_unit_basic() -> None:
    assert per_unit(42000, 4200) == 10.0
    assert per_unit(18000, 9100) == pytest.approx(1.978021978021978)


def test_per_unit_zero_denominator_is_none() -> None:
    assert per_unit(1000, 0) is None
    assert per_unit(1000, -3) is None


def test_listing_band_counts_and_bounds() -> None:
    band = listing_band()
    assert band["count"] == 6
    assert band["price_lo_usd"] == 18000
    assert band["price_hi_usd"] == 65000
    assert band["unit_lo_usd"] == pytest.approx(1.978021978021978)
    assert band["unit_hi_usd"] == pytest.approx(15.714285714285714)


def test_listing_band_has_no_center() -> None:
    text = json.dumps(listing_band(), ensure_ascii=False).lower()
    assert "mean" not in text and "median" not in text and "average" not in text


def test_fee_schedule_codebase_only() -> None:
    schedule = fee_schedule()
    assert schedule["codebase"]["seller_share"] == 0.8
    assert schedule["taskset"]["seller_share"] is None
    assert schedule["taskset"]["reason"] == "FEE_UNSTATED_FOR_TASKSET"
    assert schedule["bounty"]["seller_share"] is None
    assert schedule["bounty"]["reason"] == "FEE_UNSTATED"


def test_apply_fee_codebase() -> None:
    assert apply_fee("codebase", 1000.0) == 800.0


def test_apply_fee_refuses_transfer_to_taskset() -> None:
    with pytest.raises(FeeScheduleMissingError):
        apply_fee("taskset", 1000.0)


def test_apply_fee_refuses_bounty() -> None:
    with pytest.raises(FeeScheduleMissingError):
        apply_fee("bounty", 1000.0)


def test_apply_fee_refuses_unknown_class() -> None:
    with pytest.raises(FeeScheduleMissingError):
        apply_fee("airdrop", 1000.0)


def test_net_probe_single_quotable() -> None:
    probes = net_probe()
    assert probes["CH5_datavendor_codebase"]["net_usd"] == 800.0
    assert probes["CH5_datavendor_codebase"]["state"] == "QUOTABLE"
    assert probes["CH1_prime_open"]["reason"] == "FEE_UNSTATED"
    assert probes["CH2_prime_app"]["reason"] == "FEE_UNSTATED"
    assert probes["CH3_prime_sprint"]["reason"] == "NON_CASH_TICKET"
    assert probes["CH4_datavendor_listing"]["reason"] == "FEE_UNSTATED_FOR_TASKSET"
    assert all(probes[c]["net_usd"] is None for c in probes if c != "CH5_datavendor_codebase")


def test_rank_for_first_test_is_declared_order() -> None:
    assert rank_for_first_test() == [
        "CH1_prime_open",
        "CH2_prime_app",
        "CH3_prime_sprint",
        "CH5_datavendor_codebase",
        "CH4_datavendor_listing",
    ]


def test_rank_is_deterministic() -> None:
    assert rank_for_first_test() == rank_for_first_test()


def test_settle_two_stated_three_unstated() -> None:
    summary = settle_summary()
    assert summary["stated"] == 2
    assert summary["unstated"] == 3
    assert summary["stated_ids"] == ["CH4_datavendor_listing", "CH5_datavendor_codebase"]


def test_audit_band_floor_and_open_ceiling() -> None:
    band = audit_band()
    assert band["anchors"] == 6
    assert band["floor_usd"] == 0
    assert band["engagement_floor_usd"] == 8000
    assert band["highest_stated_hi_usd"] == 100000
    assert band["ceiling_open"] is True


def test_contradictions_three_with_explicit_states() -> None:
    assert [c.conflict_id for c in CONFLICTS] == [
        "C1_funding_round",
        "C2_fee_transfer",
        "C3_repo_rename",
    ]
    states = {c["conflict_id"]: c["status"] for c in contradictions()}
    assert states == {
        "C1_funding_round": "OPEN",
        "C2_fee_transfer": "GUARDED",
        "C3_repo_rename": "RESOLVED_PRIMARY",
    }
    assert all(c["rule_ar"].strip() for c in contradictions())


def test_kill_switches_silent_on_declared_data() -> None:
    assert kill_switches() == []


def test_kill_switch_k1_can_fire(monkeypatch: pytest.MonkeyPatch) -> None:
    import shared.research.first_invoice as module

    monkeypatch.setattr(
        module,
        "CHANNELS",
        tuple(__import__("dataclasses").replace(channel, payout_rail=None) for channel in CHANNELS),
    )
    assert "K1_ALL_SETTLE_UNSTATED" in kill_switches()


def test_kill_switch_k5_can_fire(monkeypatch: pytest.MonkeyPatch) -> None:
    import dataclasses

    import shared.research.first_invoice as module

    first = dataclasses.replace(CHANNELS[0], sources=())
    monkeypatch.setattr(module, "CHANNELS", (first, *tuple(CHANNELS[1:])))
    assert "K5_ZERO_SOURCE_CHANNEL" in kill_switches()


def test_fingerprint_is_64_hex_and_deterministic() -> None:
    first = inputs_fingerprint()
    assert re.fullmatch(r"[0-9a-f]{64}", first)
    assert inputs_fingerprint() == first


def test_measure_all_declared_zeros() -> None:
    payload = measure_all()
    assert payload["declared_zeros"] == {
        "model_runs_executed": 0,
        "client_measurements": 0,
        "invoices_issued": 0,
        "settled_contracts": 0,
        "exploit_code_present": False,
        "revenue_claim": "NONE",
    }


def test_measure_all_result_keys_closed() -> None:
    payload = measure_all()
    assert sorted(payload["results"].keys()) == sorted(
        [
            "channels_ranked",
            "listing_band",
            "audit_band",
            "fee_schedule",
            "net_probe",
            "net_probe_summary",
            "settle",
            "spend",
            "contradictions",
            "naming",
            "source_counts",
            "single_source_channels",
            "kill_switches",
        ]
    )


def test_measure_all_no_infinity_or_nan() -> None:
    text = json.dumps(measure_all(), ensure_ascii=False)
    assert "Infinity" not in text and "NaN" not in text


def test_measure_all_deterministic_bytes() -> None:
    first = json.dumps(measure_all(), ensure_ascii=False, indent=2, sort_keys=True)
    second = json.dumps(measure_all(), ensure_ascii=False, indent=2, sort_keys=True)
    assert first == second


def test_fiv_policy_cap_values() -> None:
    policy = fiv_policy()
    assert policy["max_spend_usd"] == 0
    assert policy["max_effort_days"] == 5
    assert policy["adjustable_by"] == "owner decision only"


def test_tool_is_stdlib_only() -> None:
    allowed = set(sys.stdlib_module_names) | {"__future__"}
    tree = ast.parse(TOOL.read_text(encoding="utf-8"), filename=str(TOOL))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert alias.name.split(".")[0] in allowed, alias.name
        elif isinstance(node, ast.ImportFrom):
            assert node.level == 0
            assert (node.module or "").split(".")[0] in allowed, node.module


def test_tool_has_no_print() -> None:
    tree = ast.parse(TOOL.read_text(encoding="utf-8"), filename=str(TOOL))
    calls = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "print"
    ]
    assert calls == []
