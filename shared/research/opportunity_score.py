"""The one merged opportunity-score model (D-319 · Founder Atlas §1.4).

The owner asked to merge the three scoring models (Atlas §1.4, the hard-currency v1
weights, the sovereign-atlas 18 criteria) and keep the strongest by reputable study.
The result is lexicographic, not a weighted sum:

1. **EXCLUDED** when an existing DCE §9 gate is ``FAIL`` with an evidence id, or an
   existing exclusion list applies (sovereign kill-criteria, D-273 §04, the D-300 freeze).
   The Atlas's three fatal flaws are the purchase, legality-and-collection and
   economics-and-liquidity gates; a high total never buys them back.
2. ``F`` — fatal gates not ``PASS``; ``S`` — six criteria scored 0–5 with unit weights;
   ``O`` — the other order gates not ``PASS``; ``Z`` — criteria at level 0.
   Order: ascending ``(F, -S, O, Z)``.

Only evidence is credited: an unknown counts 0, desk research caps a criterion at 2,
levels 3–5 need the contact ledger or an independent result, each entity counts once,
a row older than 183 days counts one level lower, a conflict credits the lower level.
No multiplier, probability or decimal enters the score.

The Atlas weights 20/20/15/15/10/10/5/5 are a fixed sensitivity scenario: if they (or
any scenario) change the top three, the answer is «عدم الحسم», never a pick.

The model ranks candidates to explore. It never chooses the action (that stays with
``economic_decision``), never raises commitment, never moves a catalog state or
``GATE_C``, and never switches the D-300 thesis. Pure stdlib; integers only in scores.
"""

from __future__ import annotations

import math
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import date
from itertools import pairwise
from statistics import median

from shared.research.economic_truth import HOLDING, NOT_YET_EVALUABLE

__all__ = [
    "ATLAS_WEIGHTS",
    "CONFIGURATION_OUTBOUND",
    "CRITERIA",
    "DECIDE_EXCLUDE",
    "DECIDE_POSTPONE",
    "DECIDE_TEST",
    "DECIDE_UNDECIDED",
    "FAIL",
    "FATAL_GATES",
    "GATES",
    "ORDER_GATES",
    "PASS",
    "STALE_AFTER_DAYS",
    "SUSPENDED",
    "TOP_K",
    "UNCHECKED",
    "UNVALIDATED_AFTER",
    "Candidate",
    "Gate",
    "OwnerParameters",
    "Ranking",
    "Row",
    "Score",
    "kendall_tau_b",
    "non_discriminating_criteria",
    "rank",
    "refutation_status",
    "score",
]

# DCE §5 gate states (مجتازة / معلقة / فاشلة / غير مفحوصة).
PASS, SUSPENDED, FAIL, UNCHECKED = "PASS", "SUSPENDED", "FAIL", "UNCHECKED"
GATE_STATES = (PASS, SUSPENDED, FAIL, UNCHECKED)

# The seven existing DCE §9 gates — no new gate (D-314).
FATAL_GATES = ("purchase", "legality_collection", "economics_liquidity")
ORDER_GATES = ("switching", "acceptance", "execution_delivery")
ADDITIONALITY = "additionality"  # may stay open at E0/E1 (DCE:210); never a rank key.
GATES = FATAL_GATES + ORDER_GATES + (ADDITIONALITY,)

# DCE §5 decision words.
DECIDE_EXCLUDE = "استبعاد"
DECIDE_TEST = "اختبار"
DECIDE_POSTPONE = "تأجيل"
DECIDE_UNDECIDED = "عدم الحسم"

CRITERIA = ("C1", "C2", "C3", "C4", "C5", "C6")
CRITERIA_AR = {
    "C1": "ألمٌ عند مشترين مسمَّين: شدّته وتكراره",
    "C2": "إنفاقٌ أو استعدادٌ للدفع باليورو/الدولار",
    "C3": "مشترون قابلون للعدّ والوصول",
    "C4": "تفوّقٌ على بديل المشتري الحالي",
    "C5": "قابلية التسليم منفرداً وتكراره",
    "C6": "هامش الوحدة وزمن أول نقدٍ بالعملة الصعبة",
}

DESK, REPO, LEDGER, INDEPENDENT = "desk", "repo", "ledger", "independent"
SOURCES = (DESK, REPO, LEDGER, INDEPENDENT)

#: Which evidence classes may support each level of each criterion (the anchors of the
#: merged model). A stronger class may support a lower level; desk research never
#: exceeds level 2, and our own data never exceeds value-chain link 4.
ALLOWED: dict[str, dict[int, frozenset[str]]] = {
    "C1": {
        1: frozenset({DESK, LEDGER, INDEPENDENT}),
        2: frozenset({DESK, LEDGER, INDEPENDENT}),
        3: frozenset({LEDGER, INDEPENDENT}),
        4: frozenset({LEDGER, INDEPENDENT}),
        5: frozenset({INDEPENDENT}),
    },
    "C2": {
        1: frozenset({DESK, LEDGER}),
        2: frozenset({DESK, LEDGER}),
        3: frozenset({LEDGER}),
        4: frozenset({LEDGER}),
        5: frozenset({LEDGER}),
    },
    "C3": {
        1: frozenset({DESK, REPO, LEDGER}),
        2: frozenset({REPO, LEDGER}),
        3: frozenset({LEDGER}),
        4: frozenset({LEDGER}),
        5: frozenset({LEDGER}),
    },
    "C4": {
        1: frozenset({DESK, REPO, LEDGER, INDEPENDENT}),
        2: frozenset({DESK, REPO, LEDGER, INDEPENDENT}),
        3: frozenset({LEDGER, INDEPENDENT}),
        4: frozenset({INDEPENDENT}),
        5: frozenset({LEDGER}),
    },
    "C5": {
        1: frozenset({REPO, LEDGER, INDEPENDENT}),
        2: frozenset({REPO, LEDGER, INDEPENDENT}),
        3: frozenset({REPO, LEDGER, INDEPENDENT}),
        4: frozenset({LEDGER, INDEPENDENT}),
        5: frozenset({LEDGER}),
    },
    "C6": {
        1: frozenset({DESK, REPO, LEDGER}),
        2: frozenset({DESK, REPO, LEDGER}),
        3: frozenset({LEDGER}),
        4: frozenset({LEDGER}),
        5: frozenset({LEDGER}),
    },
}

#: Distinct entities (organisations, or publishers for desk rows) a level needs.
MIN_ENTITIES: dict[str, dict[int, int]] = {
    "C1": {2: 2, 4: 2, 5: 2},
    "C2": {2: 2},
    "C3": {2: 20, 3: 20, 4: 3, 5: 2},
    "C4": {},
    "C5": {5: 2},
    "C6": {},
}

STALE_AFTER_DAYS = 183
#: The pre-registered purchase kill (Atlas card): 20 outbound messages in one configuration,
#: then 0 replies within 30 days, means purchase FAIL. The same number caps one CRM draft
#: batch (Atlas §0.3 · D-319): no broad marketing before knowing who buys and why.
CONFIGURATION_OUTBOUND = 20
TOP_K = 3
ROBUST_GAP = 2
#: Owner table mapped onto the six criteria: solvability 15 + scalability 5 → C5 20.
#: Human/social impact (5) is shown, never scored.
ATLAS_WEIGHTS: dict[str, int] = {"C1": 20, "C2": 20, "C3": 15, "C4": 10, "C5": 20, "C6": 10}
#: The refutation clock: no evaluation round by this date ⇒ UNVALIDATED.
UNVALIDATED_AFTER = date(2027, 4, 16)

_STANCES = ("supports", "contradicts", "refutes")


@dataclass(frozen=True)
class Gate:
    state: str
    evidence_id: str = ""


@dataclass(frozen=True)
class Row:
    """One evidence row. ``level`` is the anchor level the row claims to satisfy."""

    id: str
    criterion: str
    level: int
    source: str
    as_of: date
    entities: tuple[str, ...] = ()
    stance: str = "supports"


@dataclass(frozen=True)
class Candidate:
    id: str
    gates: Mapping[str, Gate]
    rows: tuple[Row, ...] = ()
    exclusions: tuple[str, ...] = ()


@dataclass(frozen=True)
class OwnerParameters:
    """Owner-declared economics inputs; until both exist economics cannot PASS."""

    hourly_floor_eur: int | None = None
    loss_limit_eur: int | None = None

    @property
    def declared(self) -> bool:
        return bool(self.hourly_floor_eur) and self.loss_limit_eur is not None


@dataclass(frozen=True)
class Score:
    id: str
    excluded: bool
    reasons: tuple[str, ...]
    F: int
    S: int
    O: int  # noqa: E741 — the model's own name for the other-gates key
    Z: int
    levels: dict[str, int]
    high: dict[str, int]
    gate_states: dict[str, str]
    problems: tuple[str, ...] = ()

    @property
    def key(self) -> tuple[int, int, int, int]:
        return (self.F, -self.S, self.O, self.Z)

    @property
    def s_high(self) -> int:
        return sum(self.high.values())


@dataclass(frozen=True)
class Ranking:
    ordered: tuple[Score, ...]
    excluded: tuple[Score, ...]
    decisions: dict[str, str]
    undecided: bool
    scenario_top: dict[str, tuple[str, ...]] = field(default_factory=dict)
    dominated: tuple[str, ...] = ()


def _effective_gates(
    candidate: Candidate, params: OwnerParameters
) -> tuple[dict[str, str], list[str]]:
    states: dict[str, str] = {}
    problems: list[str] = []
    for name in GATES:
        gate = candidate.gates.get(name, Gate(UNCHECKED))
        state = gate.state if gate.state in GATE_STATES else UNCHECKED
        if gate.state not in GATE_STATES:
            problems.append(f"{name}: unknown gate state {gate.state!r} read as UNCHECKED")
        if state in (PASS, FAIL) and not gate.evidence_id.strip():
            problems.append(f"{name}: {state} without an evidence id is UNCHECKED")
            state = UNCHECKED
        if name == "economics_liquidity" and state == PASS and not params.declared:
            problems.append(
                "economics_liquidity: PASS needs the owner's hourly floor H and loss limit"
            )
            state = SUSPENDED
        states[name] = state
    return states, problems


def _row_level(row: Row, today: date) -> int:
    allowed = ALLOWED[row.criterion]
    level = 0
    for candidate_level in range(min(row.level, 5), 0, -1):
        if row.source in allowed[candidate_level]:
            level = candidate_level
            break
    if level and (today - row.as_of).days > STALE_AFTER_DAYS:
        level -= 1
    return level


def _credited(rows: Sequence[Row], criterion: str, today: date) -> tuple[int, int]:
    supporting = [r for r in rows if r.stance == "supports"]
    effective = [(r, _row_level(r, today)) for r in supporting]
    credited = 0
    for level in range(5, 0, -1):
        holders = [r for r, lvl in effective if lvl >= level]
        entities = {e for r in holders for e in r.entities} or ({"_"} if holders else set())
        if holders and len(entities) >= MIN_ENTITIES[criterion].get(level, 1):
            credited = level
            break
    high = 5
    for row in rows:
        if row.stance == "contradicts":
            credited = min(credited, max(0, min(row.level, 5)))
            high = credited
        elif row.stance == "refutes":
            high = credited
    return credited, max(high, credited)


def score(
    candidate: Candidate,
    today: date,
    params: OwnerParameters,
    resolves: Callable[[str], bool] = lambda _id: True,
) -> Score:
    """Score one candidate. ``resolves`` says whether an evidence id exists."""
    states, problems = _effective_gates(candidate, params)
    usable: list[Row] = []
    for row in candidate.rows:
        if row.criterion not in CRITERIA or row.source not in SOURCES or row.stance not in _STANCES:
            problems.append(f"{row.id}: unknown criterion, source or stance — ignored")
        elif row.as_of > today:
            problems.append(f"{row.id}: dated after the scoring date — ignored")
        elif not resolves(row.id):
            problems.append(f"{row.id}: evidence id does not resolve — counts 0")
        else:
            usable.append(row)
    levels: dict[str, int] = {}
    high: dict[str, int] = {}
    for criterion in CRITERIA:
        levels[criterion], high[criterion] = _credited(
            [r for r in usable if r.criterion == criterion], criterion, today
        )
    reasons = [
        f"{name}: FAIL ({candidate.gates[name].evidence_id})"
        for name in GATES
        if states[name] == FAIL
    ]
    reasons += [f"exclusion list: {item}" for item in candidate.exclusions if item.strip()]
    return Score(
        id=candidate.id,
        excluded=bool(reasons),
        reasons=tuple(reasons),
        F=sum(1 for g in FATAL_GATES if states[g] != PASS),
        S=sum(levels.values()),
        O=sum(1 for g in ORDER_GATES if states[g] != PASS),
        Z=sum(1 for v in levels.values() if v == 0),
        levels=levels,
        high=high,
        gate_states=states,
        problems=tuple(problems),
    )


def _sum_reciprocal(swing_rank: Sequence[str]) -> dict[str, int]:
    """Integer sum-reciprocal weights from an owner swing ranking (lcm(1..6) = 60)."""
    return {c: 60 // (swing_rank.index(c) + 1) if c in swing_rank else 0 for c in CRITERIA}


def _scenarios(swing_rank: Sequence[str] | None) -> dict[str, dict[str, int]]:
    scenarios = {"unit": dict.fromkeys(CRITERIA, 1), "atlas": dict(ATLAS_WEIGHTS)}
    if swing_rank:
        scenarios["owner_swing"] = _sum_reciprocal(swing_rank)
    for left_out in CRITERIA:
        scenarios[f"without_{left_out}"] = {c: int(c != left_out) for c in CRITERIA}
    return scenarios


def _order(scores: Sequence[Score], weights: Mapping[str, int]) -> list[Score]:
    return sorted(
        scores,
        key=lambda s: (s.F, -sum(weights[c] * s.levels[c] for c in CRITERIA), s.O, s.Z, s.id),
    )


def _robustly_above(a: Score, b: Score, orders: Mapping[str, list[Score]]) -> bool:
    if a.F < b.F:
        return True
    if a.F > b.F or a.S - b.S < ROBUST_GAP:
        return False
    return all(
        [s.id for s in order].index(a.id) < [s.id for s in order].index(b.id)
        for order in orders.values()
    )


def rank(
    candidates: Sequence[Candidate],
    today: date,
    params: OwnerParameters,
    resolves: Callable[[str], bool] = lambda _id: True,
    swing_rank: Sequence[str] | None = None,
) -> Ranking:
    """Order candidates and give each a DCE decision word. Re-run from scratch per new row."""
    scores = [score(c, today, params, resolves) for c in candidates]
    excluded = tuple(sorted((s for s in scores if s.excluded), key=lambda s: s.id))
    live = [s for s in scores if not s.excluded]
    ordered = tuple(sorted(live, key=lambda s: (*s.key, s.id)))
    orders = {name: _order(live, w) for name, w in _scenarios(swing_rank).items()}
    top_sets = {name: tuple(s.id for s in order[:TOP_K]) for name, order in orders.items()}
    primary_top = ordered[:TOP_K]
    undecided = len({frozenset(t) for t in top_sets.values()}) > 1
    if len(ordered) > TOP_K:
        fourth = ordered[TOP_K]
        undecided = undecided or not all(_robustly_above(s, fourth, orders) for s in primary_top)
    keys = [s.key for s in primary_top]
    undecided = undecided or len(set(keys)) < len(keys)
    decisions = {s.id: DECIDE_EXCLUDE for s in excluded}
    contested = {cid for top in top_sets.values() for cid in top}
    for s in ordered:
        if undecided and s.id in contested:
            decisions[s.id] = DECIDE_UNDECIDED
        elif not undecided and s in primary_top:
            decisions[s.id] = DECIDE_TEST
        else:
            decisions[s.id] = DECIDE_POSTPONE
    dominated: tuple[str, ...] = ()
    if len(ordered) > TOP_K:
        third = ordered[TOP_K - 1]
        dominated = tuple(s.id for s in ordered[TOP_K:] if s.F >= third.F and s.s_high < third.S)
    return Ranking(
        ordered=ordered,
        excluded=excluded,
        decisions=decisions,
        undecided=undecided,
        scenario_top=top_sets,
        dominated=dominated,
    )


def kendall_tau_b(x: Sequence[float], y: Sequence[float]) -> float:
    """Kendall's tau-b between two paired sequences (ties allowed)."""
    if len(x) != len(y):
        raise ValueError("sequences must have the same length")
    concordant = discordant = ties_x = ties_y = 0
    n = len(x)
    for i in range(n):
        for j in range(i + 1, n):
            dx, dy = x[i] - x[j], y[i] - y[j]
            if dx == 0 and dy == 0:
                continue
            if dx == 0:
                ties_x += 1
            elif dy == 0:
                ties_y += 1
            elif (dx > 0) == (dy > 0):
                concordant += 1
            else:
                discordant += 1
    denominator = math.sqrt((concordant + discordant + ties_x) * (concordant + discordant + ties_y))
    return 0.0 if denominator == 0 else (concordant - discordant) / denominator


def _round_fails(round_: Mapping[str, Mapping[str, int]]) -> bool:
    model, gut, outcome = round_["model_rank"], round_["gut_rank"], round_["outcome"]
    ids = sorted(outcome)
    outcomes = [outcome[i] for i in ids]
    tau_model = kendall_tau_b([-model[i] for i in ids], outcomes)
    tau_gut = kendall_tau_b([-gut[i] for i in ids], outcomes)
    by_rank = sorted(ids, key=lambda i: model[i])
    bottom_half = by_rank[len(by_rank) - len(by_rank) // 2 :]
    paid_from_bottom = any(outcome[i] >= 3 for i in bottom_half)
    top_reached_sample = any(outcome[i] >= 2 for i in by_rank[:TOP_K])
    return tau_model <= 0 or tau_model < tau_gut or (paid_from_bottom and not top_reached_sample)


def refutation_status(rounds: Sequence[Mapping[str, Mapping[str, int]]], today: date) -> str:
    """REFUTED after two consecutive failing rounds; UNVALIDATED past the deadline."""
    if not rounds:
        return "UNVALIDATED" if today > UNVALIDATED_AFTER else NOT_YET_EVALUABLE
    fails = [_round_fails(r) for r in rounds]
    if any(a and b for a, b in pairwise(fails)):
        return "REFUTED"
    return HOLDING


def non_discriminating_criteria(
    frozen_levels: Mapping[str, Mapping[str, int]], outcome: Mapping[str, int]
) -> tuple[str, ...]:
    """Criteria whose median frozen level is not higher where the ledger moved (O≥1)."""
    moved = [frozen_levels[i] for i in outcome if outcome[i] >= 1 and i in frozen_levels]
    still = [frozen_levels[i] for i in outcome if outcome[i] == 0 and i in frozen_levels]
    if not moved or not still:
        return ()
    return tuple(c for c in CRITERIA if median(m[c] for m in moved) <= median(s[c] for s in still))
