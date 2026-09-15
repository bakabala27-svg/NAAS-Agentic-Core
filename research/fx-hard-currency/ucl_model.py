"""ucl_model.py - UCL v0.1: the unified conversion ledger for the whole repository.

What this adds that no previous batch had: the repository has been measured six
times in six vocabularies (SFD, ERD, PTD, PID, ABR, CPD) and each measurement
ended in its own recommendation. This file puts every candidate move on ONE
ledger with ONE ordering rule - euro per effort-day - and refuses to rank a move
whose euro band is unmeasured. Absent is None, never zero.

Inherited, already-audited inputs (fingerprints in docs/research):
  SFD 6a1028752c3c0824 - UCW: bank credit transfer 1-2 d, card 127-134 d;
                         reversal amplification 1.4607 (RAO, +46.07%)
  ERD 7d893aeaf37c37b7 - 15.38% of routers unreachable behind the edge
  PTD de0af52eea68be1f - WS protocol debt 2.50 constraints/hop vs HTTP 0.00
  PID 2ea31466c54e784f - 4 measured pair-defects, 400 days of detection debt,
                         0 of 98 CI gates inspect a relation between two artifacts
  ABR 20ec8bd4b363d6bf - 3 of 7 revenue lines are artifact-backed (0.50),
                         measurement coverage 0%, evidence coverage 0%
  CPD 9b46b6569dbaef83 - CBAM pool A EUR 5,582,765 (2026) is not capturable;
                         pool B EUR 6,000-60,000/yr is; capturability 1.07%

Standalone: stdlib only, no repository imports. Run with `python3 ucl_model.py`.
"""

# Candidate moves. Fields:
#   effort_days   - declared estimate, not measured
#   eur_low/high  - None when unmeasured. None is not zero.
#   cash_days     - days from delivery to euro on a bank account (SFD UCW), None if unknown
#   produces      - which ABR axis the move fills
#   line          - existing D-273 revenue line, or the slot it would occupy
MOVES = {
    "M1 discovery x5 (EU AI Act)": {
        "effort_days": 0.19,
        "eur_low": None,
        "eur_high": None,
        "cash_days": None,
        "produces": "E",
        "line": "6 eu-ai-act-compliance",
    },
    "M2 Arabic guard boundary (97 probes)": {
        "effort_days": 1.0,
        "eur_low": None,
        "eur_high": None,
        "cash_days": None,
        "produces": "M+E",
        "line": "1 ai-red-teaming-multilingual",
    },
    "M3 cbam_pin.py + layer-A outreach": {
        "effort_days": 3.0,
        "eur_low": 6000.0,
        "eur_high": 60000.0,
        "cash_days": 2,
        "produces": "M+E",
        "line": "swap an ABR-0.00 line",
    },
    "M4 technical freelance (SFD R4)": {
        "effort_days": 2.0,
        "eur_low": None,
        "eur_high": None,
        "cash_days": 2,
        "produces": "none",
        "line": "outside the catalog",
    },
    "M5 repo hygiene / make main green": {
        "effort_days": 5.0,
        "eur_low": 0.0,
        "eur_high": 0.0,
        "cash_days": None,
        "produces": "none",
        "line": "none",
    },
}

# Pair-defects carried from PID: every one of them sits between two healthy artifacts.
PAIR_DEBT_DAYS_BEFORE = 400.0
PAIR_DEBT_DAYS_AFTER = 0.0625
GATES_TOTAL = 98
GATES_PAIRWISE = 0

# Settlement rails carried from SFD (unsettled-capital window, days).
RAILS = {
    "SEPA credit transfer": (1, 2),
    "SWIFT credit transfer": (2, 5),
    "card": (127, 134),
    "card + rolling reserve": (157, 224),
}
REVERSAL_AMPLIFICATION = 1.4607


def midpoint(low, high):
    """Mean of a band, or None when either bound is unmeasured."""
    if low is None or high is None:
        return None
    return (low + high) / 2


def eur_per_effort_day(move):
    """Ordering statistic. None means unrankable - it does not mean last."""
    mid = midpoint(move["eur_low"], move["eur_high"])
    if mid is None:
        return None
    return mid / move["effort_days"]


def fmt(value, width=12, digits=2):
    """Right-aligned number, or an explicit `n/m` when the value is unmeasured."""
    return f"{'n/m':>{width}}" if value is None else f"{value:>{width},.{digits}f}"


def main():
    print("=" * 86)
    print("UCL v0.1 - one ledger, one ordering rule: euro per effort-day")
    print("=" * 86)
    print(f"{'move':38}{'days':>6}{'EUR/day':>12}{'cash (d)':>10}{'fills':>7}  line")
    print("-" * 86)

    rankable = []
    unrankable = []
    for name, move in MOVES.items():
        rate = eur_per_effort_day(move)
        (rankable if rate is not None else unrankable).append((name, rate))
        cash = "n/m" if move["cash_days"] is None else str(move["cash_days"])
        print(
            f"{name:38}{move['effort_days']:>6.2f}{fmt(rate)}"
            f"{cash:>10}{move['produces']:>7}  {move['line']}"
        )

    rankable.sort(key=lambda item: -item[1])
    print("-" * 86)
    print(f"rankable moves   : {len(rankable)} of {len(MOVES)}")
    print(f"unrankable (n/m) : {len(unrankable)} of {len(MOVES)} -> {[n for n, _ in unrankable]}")
    if rankable:
        best, best_rate = rankable[0]
        print(f"highest measured : {best} at EUR {best_rate:,.2f} per effort-day")
    zero = [n for n, m in MOVES.items() if m["eur_high"] == 0.0]
    print(f"measured zero    : {zero}")

    print()
    print("Pair-defect ledger (PID): the defect never lives inside one artifact.")
    collapse = 1 - PAIR_DEBT_DAYS_AFTER / PAIR_DEBT_DAYS_BEFORE
    print(f"  detection debt before pair gates : {PAIR_DEBT_DAYS_BEFORE:>10,.4f} days")
    print(f"  detection debt after  pair gates : {PAIR_DEBT_DAYS_AFTER:>10,.4f} days")
    print(f"  collapse                         : {collapse * 100:>10.4f} %")
    print(f"  CI gates inspecting a relation   : {GATES_PAIRWISE} of {GATES_TOTAL}")

    print()
    print("Settlement rails (SFD): unsettled-capital window before the euro is final.")
    for rail, (low, high) in RAILS.items():
        print(f"  {rail:24}{low:>5} - {high:<5} days")
    print(f"  every reversed EUR costs EUR {REVERSAL_AMPLIFICATION:.4f} to earn back")

    print()
    print("Reading rule: a move with an unmeasured euro band is not a bad move; it is")
    print("an unmeasured one. It may be executed for the evidence it produces (M/E),")
    print("never because it looked cheap. A measured zero outranks nothing.")


if __name__ == "__main__":
    main()
