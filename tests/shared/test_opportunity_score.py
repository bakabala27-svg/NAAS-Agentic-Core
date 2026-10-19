"""Invariants of the one merged opportunity-score model (D-319, Atlas §1.4).

Ranking is lexicographic over existing DCE §9 gates and six evidence-graded criteria.
No estimate enters, nothing is multiplied, and the Atlas weights act only as a check
on certainty: when they move the top 3, the answer is «عدم الحسم».
"""

from __future__ import annotations

from datetime import date

import pytest

from shared.research.opportunity_score import (
    ATLAS_WEIGHTS,
    CRITERIA,
    DECIDE_EXCLUDE,
    DECIDE_POSTPONE,
    DECIDE_TEST,
    DECIDE_UNDECIDED,
    FAIL,
    PASS,
    SUSPENDED,
    UNCHECKED,
    Candidate,
    Gate,
    OwnerParameters,
    Row,
    kendall_tau_b,
    rank,
    refutation_status,
    score,
)

TODAY = date(2026, 10, 19)
PARAMS = OwnerParameters(hourly_floor_eur=25, loss_limit_eur=100)


def _gates(**overrides: Gate) -> dict[str, Gate]:
    base = {
        "purchase": Gate(PASS, "LEDGER:1"),
        "legality_collection": Gate(PASS, "EV:legal"),
        "economics_liquidity": Gate(PASS, "EV:econ"),
        "switching": Gate(PASS, "EV:switch"),
        "acceptance": Gate(PASS, "EV:accept"),
        "execution_delivery": Gate(PASS, "EV:exec"),
        "additionality": Gate(UNCHECKED),
    }
    base.update(overrides)
    return base


def _rows(levels: dict[str, int], source: str = "ledger") -> tuple[Row, ...]:
    return tuple(
        Row(
            f"R-{c}-{n}",
            c,
            n,
            source,
            TODAY,
            entities=("a", "b", "c", *(f"e{i}" for i in range(20))),
        )
        for c, n in levels.items()
        if n
    )


def _cand(cid: str, levels: dict[str, int], **gates: Gate) -> Candidate:
    return Candidate(cid, _gates(**gates), _rows(levels))


def test_atlas_weights_are_the_owner_table_mapped_onto_six_criteria() -> None:
    assert CRITERIA == ("C1", "C2", "C3", "C4", "C5", "C6")
    # 20 pain, 20 spend, 15 access, 10 advantage, 15 solvability + 5 scalability, 10 economics.
    assert ATLAS_WEIGHTS == {"C1": 20, "C2": 20, "C3": 15, "C4": 10, "C5": 20, "C6": 10}


def test_same_inputs_give_the_same_output() -> None:
    cands = [_cand("a", {"C1": 3, "C2": 2}), _cand("b", {"C1": 1})]
    assert rank(cands, TODAY, PARAMS) == rank(cands, TODAY, PARAMS)


def test_adding_a_candidate_never_changes_another_candidates_keys() -> None:
    a, b = _cand("a", {"C1": 3, "C2": 2}), _cand("b", {"C1": 1, "C5": 3})
    alone = score(a, TODAY, PARAMS)
    ranked = {s.id: s for s in rank([a, b, _cand("c", {"C4": 4})], TODAY, PARAMS).ordered}
    assert (ranked["a"].F, ranked["a"].S, ranked["a"].O, ranked["a"].Z) == (
        alone.F,
        alone.S,
        alone.O,
        alone.Z,
    )


def test_desk_research_alone_caps_every_criterion_at_two() -> None:
    rows = tuple(Row(f"D-{c}", c, 5, "desk", TODAY, entities=("p1", "p2")) for c in CRITERIA)
    s = score(Candidate("desk", _gates(), rows), TODAY, PARAMS)
    assert all(level <= 2 for level in s.levels.values())
    assert s.S <= 12


def test_an_unknown_or_unresolved_row_scores_zero_not_a_midpoint() -> None:
    row = Row("missing", "C1", 3, "ledger", TODAY, entities=("x",))
    s = score(Candidate("u", _gates(), (row,)), TODAY, PARAMS, resolves=lambda _id: False)
    assert s.levels["C1"] == 0
    assert s.Z == 6


def test_a_fail_needs_an_evidence_id_or_it_is_unchecked() -> None:
    s = score(_cand("x", {"C1": 2}, purchase=Gate(FAIL)), TODAY, PARAMS)
    assert not s.excluded
    assert s.gate_states["purchase"] == UNCHECKED
    assert any("purchase" in p for p in s.problems)


def test_an_evidenced_fail_on_any_dce_gate_excludes() -> None:
    s = score(_cand("x", {"C1": 5}, switching=Gate(FAIL, "LEDGER:9")), TODAY, PARAMS)
    assert s.excluded
    assert "switching" in " ".join(s.reasons)


def test_an_exclusion_list_hit_excludes() -> None:
    cand = Candidate("k8", _gates(), _rows({"C1": 5}), exclusions=("D-273 §04 item 3",))
    assert score(cand, TODAY, PARAMS).excluded


def test_economics_cannot_pass_before_the_owner_declares_h_and_the_loss_limit() -> None:
    s = score(_cand("e", {"C1": 2}), TODAY, OwnerParameters())
    assert s.gate_states["economics_liquidity"] == SUSPENDED
    assert s.F == 1


def test_scores_are_integers_only() -> None:
    s = score(_cand("i", {"C1": 3, "C6": 2}), TODAY, PARAMS)
    assert all(type(v) is int for v in (s.F, s.S, s.O, s.Z))
    assert all(type(v) is int for v in s.levels.values())


def test_fatal_gates_outrank_points() -> None:
    strong = _cand("strong", {"C1": 5, "C2": 5, "C3": 5}, legality_collection=Gate(SUSPENDED))
    weak = _cand("weak", {"C1": 1})
    order = [s.id for s in rank([strong, weak], TODAY, PARAMS).ordered]
    assert order == ["weak", "strong"]


def test_a_stale_row_counts_one_level_lower() -> None:
    old = Row("old", "C1", 3, "ledger", date(2026, 1, 1), entities=("a", "b"))
    assert score(Candidate("s", _gates(), (old,)), TODAY, PARAMS).levels["C1"] == 2


def test_a_conflict_credits_the_lower_level_never_an_average() -> None:
    rows = (
        Row("up", "C2", 4, "ledger", TODAY, entities=("a",)),
        Row("down", "C2", 1, "ledger", TODAY, entities=("b",), stance="contradicts"),
    )
    s = score(Candidate("c", _gates(), rows), TODAY, PARAMS)
    assert s.levels["C2"] == 1
    assert s.high["C2"] == 1


def test_distinct_entities_are_counted_once() -> None:
    rows = (
        Row("r1", "C1", 4, "ledger", TODAY, entities=("same",)),
        Row("r2", "C1", 4, "ledger", TODAY, entities=("same",)),
    )
    # Level 4 of C1 needs two distinct entities; one entity twice is still one.
    assert score(Candidate("d", _gates(), rows), TODAY, PARAMS).levels["C1"] == 3


def test_atlas_weights_that_move_the_top_three_give_undecided() -> None:
    # Unit weights put "breadth" in the top 3; the Atlas weights (C1/C2 weigh 20) swap
    # it for "pain" — the set changes, so the model refuses to choose.
    cands = [
        _cand("spread", {"C3": 3, "C4": 3, "C5": 3, "C6": 3}),
        _cand("heavy", {"C1": 5, "C2": 5}),
        _cand("breadth", {"C3": 3, "C4": 3, "C6": 3}),
        _cand("pain", {"C1": 4, "C2": 4}),
    ]
    result = rank(cands, TODAY, PARAMS)
    assert result.undecided
    assert result.decisions["breadth"] == DECIDE_UNDECIDED
    assert result.decisions["pain"] == DECIDE_UNDECIDED


def test_a_robust_top_three_is_tested_and_the_rest_postponed() -> None:
    cands = [
        _cand("a", dict.fromkeys(CRITERIA, 5)),
        _cand("b", dict.fromkeys(CRITERIA, 4)),
        _cand("c", dict.fromkeys(CRITERIA, 3)),
        _cand("d", {"C1": 1}),
        _cand("x", {"C1": 5}, purchase=Gate(FAIL, "LEDGER:4")),
    ]
    result = rank(cands, TODAY, PARAMS)
    assert not result.undecided
    assert [result.decisions[k] for k in ("a", "b", "c")] == [DECIDE_TEST] * 3
    assert result.decisions["d"] == DECIDE_POSTPONE
    assert result.decisions["x"] == DECIDE_EXCLUDE


def test_kendall_tau_b_signs() -> None:
    assert kendall_tau_b([1, 2, 3], [1, 2, 3]) == pytest.approx(1.0)
    assert kendall_tau_b([1, 2, 3], [3, 2, 1]) == pytest.approx(-1.0)


def _round(model_good: bool) -> dict:
    ids = ["a", "b", "c", "d", "e", "f"]
    model = {k: i + 1 for i, k in enumerate(ids)}
    gut = {k: i + 1 for i, k in enumerate(reversed(ids))}
    outcome = {"a": 3, "b": 2, "c": 1, "d": 0, "e": 0, "f": 0}
    if not model_good:
        outcome = {"a": 0, "b": 0, "c": 0, "d": 1, "e": 2, "f": 3}
    return {"model_rank": model, "gut_rank": gut, "outcome": outcome}


def test_refutation_needs_two_consecutive_failing_rounds() -> None:
    assert refutation_status([_round(False)], TODAY) == "HOLDING"
    assert refutation_status([_round(False), _round(False)], TODAY) == "REFUTED"
    assert refutation_status([_round(False), _round(True), _round(False)], TODAY) == "HOLDING"


def test_no_round_by_the_deadline_means_unvalidated() -> None:
    assert refutation_status([], TODAY) == "NOT_YET_EVALUABLE"
    assert refutation_status([], date(2027, 4, 17)) == "UNVALIDATED"
