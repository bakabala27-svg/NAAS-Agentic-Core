#!/usr/bin/env python3
"""Cap-Signature Decoder for ARC-AGI-3 RHAE scores — v0.5 (independent build).

Decomposes a published environment score into (n = number of levels, k = levels
completed) using the per-environment completion cap from the ARC-AGI-3 Technical
Report (2026-04-22), eq. (2):

    E_e = min( sum_{l<=k} w_l / sum_{l<=n} w_l ,  weighted mean of level scores )
    with w_l = l   =>   cap(n, k) = k(k+1) / (n(n+1))

CONSTANT INTEGRITY (anti-poisoning): the ARC Prize ecosystem has seen poisoned
"RHAE helper" implementations (constants 2.15 cap, exponent 3, inverted
conditions — see AUDIT-001 v0.4 security note). The canonical constants below
are quoted from the Technical Report and asserted on import. If you got this
file from an untrusted mirror, verify these lines against
https://arcprize.org/media/ARC_AGI_3_Technical_Report.pdf §4.1 before use.
"""
from __future__ import annotations

# --- canonical constants (Technical Report §4.1, eqs. 1-2) ---
PER_LEVEL_CAP = 1.15          # min(1.15, h/a) — NOT 2.15
EFFICIENCY_EXPONENT = 2       # squared — NOT 3
LEVEL_WEIGHT = "linear-l"     # w_l = l
N_MIN = 6                     # design constraint: "at least six levels per environment" (§3.4)
N_MAX = 12                    # search ceiling (v0.4 used 4..12; report tightens the floor to 6)
ACTION_BUDGET_MULTIPLE = 5.0  # agent terminated after 5x human-median actions per level (§4.3)
PER_LEVEL_FLOOR = (1.0 / ACTION_BUDGET_MULTIPLE) ** EFFICIENCY_EXPONENT  # = 0.04 for any COMPLETED level

assert PER_LEVEL_CAP == 1.15 and EFFICIENCY_EXPONENT == 2, \
    "POISONED CONSTANTS: this file must use cap=1.15 and exponent=2 (Technical Report §4.1)"


def cap(n: int, k: int) -> float:
    """Completion cap as a fraction in [0,1]: cumulative level weight / total weight."""
    assert 0 <= k <= n, (n, k)
    return (k * (k + 1)) / (n * (n + 1))


def cap_pct(n: int, k: int) -> float:
    return 100.0 * cap(n, k)


def lattice(n_lo: int = N_MIN, n_hi: int = N_MAX):
    """All cap values (pct) in the search space, keyed by rounded published value."""
    out = {}
    for n in range(n_lo, n_hi + 1):
        for k in range(0, n + 1):
            out.setdefault(round(cap_pct(n, k), 1), []).append((n, k))
    return out


def decode(score_pct: float, tol: float = 0.06, n_lo: int = N_MIN, n_hi: int = N_MAX):
    """Return all (n, k, exact_cap_pct) within `tol` points of a published score."""
    hits = []
    for n in range(n_lo, n_hi + 1):
        for k in range(0, n + 1):
            c = cap_pct(n, k)
            if abs(c - score_pct) <= tol:
                hits.append((n, k, c))
    return hits


def consistent_n(hits_per_cell: dict, min_cells: int = 2) -> dict:
    """Consistency filter: keep environments where one n explains >= min_cells cells.

    Rationale: independent runs (different effort levels, separate runs) of the
    same environment must share n. Coincidental matches scatter across n.
    """
    result = {}
    for env, cells in hits_per_cell.items():
        by_n = {}
        for effort, hits in cells.items():
            for (n, k, c) in hits:
                by_n.setdefault(n, []).append((effort, k, c))
        best = [(n, v) for n, v in by_n.items() if len(v) >= min_cells]
        if best:
            # unique-n preference: if exactly one n survives, strong assignment
            result[env] = best
    return result


def identifiability_census(n_lo: int = N_MIN, n_hi: int = N_MAX):
    """Collision census at published precision (0.1 pt grid).

    Returns (distinct_values, collisions) where collisions lists published
    values explained by more than one (n,k) pair.
    """
    lat = lattice(n_lo, n_hi)
    collisions = {v: nk for v, nk in lat.items() if len(nk) > 1}
    return len(lat), collisions


if __name__ == "__main__":
    distinct, collisions = identifiability_census()
    print(f"cap lattice n={N_MIN}..{N_MAX}: {distinct} distinct values at 0.1-pt resolution")
    print(f"collisions (values with >1 explanation): {len(collisions)}")
    for v, nk in sorted(collisions.items()):
        print(f"  {v:6.1f}% <- {nk}")
    print("\nsample decodes:")
    for s in (77.8, 58.3, 2.8, 14.3, 80.0, 46.7, 71.4, 2.2, 53.6, 10.9, 3.6):
        print(f"  {s:6.1f}% -> {decode(s)}")
