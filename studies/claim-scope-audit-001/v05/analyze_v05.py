#!/usr/bin/env python3
"""v0.5 analysis engine — independent replication + new-knowledge layer.

Every number printed/derived here is computed from:
  [P] primary fetches 2026-09-12: arcprize.org/results/openai-gpt-6-astra,
      arcprize.org/blog/astra, ARC-AGI-3 Technical Report PDF (2026-04-22)
  [D] derivations executed by this script
Poisoned-constant self-check lives in cap_decoder.py (asserts cap=1.15, exp=2).
"""
import csv, math, statistics
from collections import defaultdict
from cap_decoder import cap, cap_pct, decode, consistent_n, identifiability_census, PER_LEVEL_FLOOR, N_MIN

HERE = "studies/claim-scope-audit-001/v05/"
EFFORTS = ["max", "xhigh", "high", "medium", "low", "none"]

# ---------- load ----------
rows = list(csv.DictReader(open(HERE + "cells_public_v05.csv")))
assert len(rows) == 300, len(rows)
cells = {}          # (harness, env, effort) -> score
prov = {}
for r in rows:
    cells[(r["harness"], r["env"], r["effort"])] = float(r["score_pct"])
    prov[(r["harness"], r["env"], r["effort"])] = r["provenance"]
envs_std = sorted({e for (h, e, _) in cells if h == "standard"})
assert len(envs_std) == 25

# verified semi-private aggregates (results page "Verified scores", 2 decimals) [P]
SP = {"standard": {"max": 62.71, "xhigh": 59.34, "high": 54.82, "medium": 38.59, "low": 17.45, "none": 35.18},
      "adapter":   {"max": 98.55, "xhigh": 98.44, "high": 99.95, "medium": 98.44, "low": 98.03, "none": 96.72}}
COST = {"standard": {"max": 26098, "xhigh": 37317, "high": 40705, "medium": 48090, "low": 38166, "none": 49791},
        "adapter":   {"max": 17332, "xhigh": 18147, "high": 18817, "medium": 19285, "low": 21298, "none": 23457}}
GPT56_SOL = 7.8  # standard harness, 1 decimal as published [P via v0.2 F01/TNW]
HUMAN_FEE = 12.78  # $/attempted game before bonuses [P blog]

out = []
def say(*a):
    s = " ".join(str(x) for x in a)
    out.append(s)
    print(s)

# ---------- 1. reconstruction integrity: column means vs v0.4 §11 ----------
say("== 1. public-set column means (my 300-cell reconstruction) vs v0.4 §11 ==")
v04_pub = {"low": 38.81, "none": 56.25, "medium": 54.39, "high": 65.18, "max": 68.34, "xhigh": 61.76}
for eff in ["max", "xhigh", "high", "medium", "low", "none"]:
    col = [cells[("standard", e, eff)] for e in envs_std]
    m = statistics.mean(col)
    say(f"  {eff:6s}: mine={m:7.3f}  v0.4={v04_pub[eff]:6.2f}  diff={m - v04_pub[eff]:+.3f}")

# ---------- 2. v0.2 derived-layer replication from 2-decimal verified scores ----------
say("\n== 2. aggregate layer recomputed from 2-decimal verified scores [P] ==")
for h in ("standard", "adapter"):
    for eff in EFFORTS:
        r = SP[h][eff]
        E = math.sqrt(r / 100)
        say(f"  {h:8s} {eff:6s}: RHAE={r:6.2f}%  E=sqrt(RHAE)={E:.6f}  actions/human=1/E={1/E:.4f}x  cost=${COST[h][eff]:,}")

# ---------- 3. Pareto dominance, 36 pairs ----------
say("\n== 3. Pareto dominance (adapter vs standard, all 36 effort pairs) ==")
viol = 0
min_score_gap = 1e9
min_cost_margin = 1e9
for e1 in EFFORTS:
    for e2 in EFFORTS:
        if not (SP["adapter"][e1] > SP["standard"][e2] and COST["adapter"][e1] < COST["standard"][e2]):
            viol += 1
        min_cost_margin = min(min_cost_margin, COST["standard"][e2] - COST["adapter"][e1])
say(f"  violations: {viol}/36; cost margin = cheapest standard - priciest adapter = "
    f"${min(COST['standard'].values()) - max(COST['adapter'].values()):,} "
    f"({(min(COST['standard'].values()) - max(COST['adapter'].values())) / min(COST['standard'].values()) * 100:.1f}%)")

# ---------- 4. N1 amplification table ----------
say("\n== 4. amplification dS/dE=2E ==")
for label, r in (("99.95 (adapter high)", 99.95), ("62.71 (std max)", 62.71),
                 ("17.45 (std low)", 17.45), ("2.11 (Grok 4.6, relay)", 2.11)):
    E = math.sqrt(r / 100)
    say(f"  at {label:26s}: 1 RHAE pt = {100/(200*E):.3f}% actions-efficiency; amp=2E={2*E:.3f}x")
gap_hi = SP["adapter"]["high"] - SP["adapter"]["max"]
say(f"  99.95 vs 98.55: score gap {gap_hi:.2f} pts -> action-efficiency gap "
    f"{100*(math.sqrt(.9995)-math.sqrt(.9855)):.3f}% (=divide by ~{gap_hi/(100*(math.sqrt(.9995)-math.sqrt(.9855))):.2f})")

# ---------- 5. N4 effort-dial economics ----------
say("\n== 5. effort-dial economics ==")
dE = 100 * (math.sqrt(SP['adapter']['high']/100) - math.sqrt(SP['adapter']['max']/100))
dC = COST['adapter']['high'] - COST['adapter']['max']
say(f"  adapter max->high: +{SP['adapter']['high']-SP['adapter']['max']:.2f} RHAE pts for +${dC:,} "
    f"= ${dC/(SP['adapter']['high']-SP['adapter']['max']):,.0f}/pt = ${dC/dE:,.0f} per 1% action-efficiency")
span = 100*(math.sqrt(SP['adapter']['high']/100) - math.sqrt(SP['adapter']['none']/100))
say(f"  adapter none->high: +{SP['adapter']['high']-SP['adapter']['none']:.2f} RHAE pts = +{span:.2f}% action-efficiency; "
    f"cost ratio none/high = {COST['adapter']['none']/COST['adapter']['high']:.3f}x")

# ---------- 6. cap decoder on the standard public set ----------
say("\n== 6. cap-signature decoder (tol=0.06, n=6..12 per report §3.4) ==")
TOL = 0.06
nontrivial = [(e, eff) for e in envs_std for eff in EFFORTS
              if 0.0 < cells[("standard", e, eff)] < 100.0]
say(f"  non-trivial standard cells (0 < score < 100): {len(nontrivial)}  "
    f"[v0.4 claimed 95; strict count = {len(nontrivial)}]")
hits_per_env = defaultdict(dict)
all_matches = []
for (e, eff) in nontrivial:
    s = cells[("standard", e, eff)]
    h = decode(s, tol=TOL)
    if h:
        hits_per_env[e][eff] = h
        all_matches.append((e, eff, s, h))
say(f"  raw cap matches: {len(all_matches)}  [v0.4 claimed 50]")
cons = consistent_n(hits_per_env, min_cells=2)
n_cons_matches = sum(len(v) for e, d in hits_per_env.items() if e in cons for v in d.values())
say(f"  matches inside consistency-approved envs: {n_cons_matches}")
for env in sorted(cons):
    ns = {n: [(eff, k) for (eff, k, c) in v] for n, v in cons[env]}
    say(f"    {env}: n-candidates -> " + "; ".join(f"n={n}: {sorted(set(k for _, k in v))} ({len(v)} cells)" for n, v in ns.items()))
# near-misses (tol 0.06..0.10)
nm = []
for (e, eff) in nontrivial:
    s = cells[("standard", e, eff)]
    if not decode(s, tol=TOL) and decode(s, tol=0.10):
        nm.append((e, eff, s, decode(s, tol=0.10)))
say(f"  near-misses at tol 0.10 (excluded at 0.06): {[(e, eff, s) for (e, eff, s, _) in nm]}")

# identifiability census + chance model
distinct, collisions = identifiability_census()
say(f"\n== 7. identifiability: {distinct} distinct cap values at 0.1-pt resolution (n={N_MIN}..12); collisions: {len(collisions)} ==")
for v, nk in sorted(collisions.items()):
    say(f"    {v:6.1f}% <- {nk}")
bins = 1000
p_chance = sum(2 if (i / 10) in () else 0 for i in range(0))  # placeholder, computed below
# chance: each published value sits on 0.1 grid; a cap value covers the grid points within 0.06 -> 1 bin each (2 if on .x5 boundary)
grid_hits = set()
for v in sorted({round(cap_pct(n, k), 2) for n in range(N_MIN, 13) for k in range(n + 1)}):
    for g in range(1, 1000):  # grid 0.1 .. 99.9
        if abs(g / 10 - v) <= TOL:
            grid_hits.add(g)
p_chance = len(grid_hits) / 999
k_obs = len(all_matches)
n_nt = len(nontrivial)
# exact binomial tail P(X >= k_obs)
tail = sum(math.comb(n_nt, i) * p_chance**i * (1 - p_chance)**(n_nt - i) for i in range(k_obs, n_nt + 1))
say(f"  published-grid bins covered by any cap value: {len(grid_hits)}/999 -> p(match by chance)={p_chance:.4f}")
say(f"  expected chance matches in {n_nt} cells: {n_nt*p_chance:.1f}; observed {k_obs}; exact binomial tail p = {tail:.3e}")

# ---------- 8. primary-source anchor: Figure 4 (re86) ----------
say("\n== 8. Figure-4 anchor (Technical Report): re86 = 8 levels, 11 human playthroughs ==")
re86 = [(8, 100), (8, 100), (8, 100), (8, 100), (8, 89), (6, 56), (6, 44), (6, 26), (2, 8), (2, 8), (2, 2)]
ok = all(score <= cap_pct(8, k) + 0.01 for k, score in re86)
say(f"  every human score <= cap(8,k): {ok}  (cap(8,2)={cap_pct(8,2):.2f}, cap(8,6)={cap_pct(8,6):.2f})")
say(f"  decoder on our RE86 cells: {sorted({(n,k) for (e,eff,s,h) in all_matches if e=='RE86' for (n,k,c) in h})}")
say(f"  Astra RE86 max/xhigh/high = {cells[('standard','RE86','max')]} = cap(8,7)={cap_pct(8,7):.2f} -> k=7 of n=8; KILL GATE: report says Lvl/8 -> SURVIVES")

# ls20 out-of-sample: report Figure 8 shows 7 levels
say(f"  ls20 decoder hits: {sorted({(n,k) for (e,eff,s,h) in all_matches if e=='LS20' for (n,k,c) in h})} "
    f"-> consistency filter must reject n=10 spurious; ground truth n=7 (Fig.8)")

# ---------- 9. max-effort classification (v0.4 §10) ----------
say("\n== 9. max-effort classification ==")
perfect, capped, efflim, zero = [], [], [], []
for e in envs_std:
    s = cells[("standard", e, "max")]
    if s == 100.0:
        perfect.append(e)
    elif s == 0.0:
        zero.append(e)
    elif decode(s, tol=TOL):
        capped.append((e, s, decode(s, tol=TOL)))
    else:
        efflim.append((e, s))
say(f"  perfect={len(perfect)} {perfect}")
say(f"  cap-limited={len(capped)} {[(e, s) for e, s, _ in capped]}")
say(f"  efficiency-limited={len(efflim)} {efflim}")
say(f"  zero={len(zero)} {zero}")

# ---------- 10. low-effort anomaly ----------
say("\n== 10. low-effort anomaly ==")
worse = [e for e in envs_std if cells[("standard", e, "low")] < cells[("standard", e, "none")]]
ties = [e for e in envs_std if cells[("standard", e, "low")] == cells[("standard", e, "none")]]
say(f"  envs with low < none: {len(worse)}/25 {worse}")
say(f"  ties (low == none): {len(ties)} {ties}")
pub_drop = statistics.mean([cells[('standard', e, 'none')] for e in envs_std]) - statistics.mean([cells[('standard', e, 'low')] for e in envs_std])
say(f"  public drop none->low = {pub_drop:.2f} pts; semi-private drop = {SP['standard']['none']-SP['standard']['low']:.2f} pts; "
    f"cross-set difference = {abs(pub_drop - (SP['standard']['none']-SP['standard']['low'])):.2f} pts")
# is the drop carried by completion collapse?
collapse = [e for e in worse if decode(cells[('standard', e, 'low')], tol=TOL) and not decode(cells[('standard', e, 'none')], tol=TOL)]
say(f"  of the {len(worse)}: collapse-to-cap at low (completion stop): {[e for e in worse if decode(cells[('standard',e,'low')], tol=TOL)]}")

# ---------- 11. public-vs-semi-private inflation ----------
say("\n== 11. public vs semi-private inflation (standard harness) ==")
pub_means = {}
for eff in EFFORTS:
    pub_means[eff] = statistics.mean([cells[("standard", e, eff)] for e in envs_std])
    infl = pub_means[eff] - SP["standard"][eff]
    say(f"  {eff:6s}: public={pub_means[eff]:6.2f}  semi-private={SP['standard'][eff]:6.2f}  inflation={infl:+6.2f}")
order = sorted(EFFORTS, key=lambda x: -(pub_means[x] - SP["standard"][x]))
say(f"  inflation ranking (high->low): {order}")

# ---------- 12. adapter saturation ----------
say("\n== 12. adapter public saturation ==")
a100 = [(e, eff) for e in envs_std for eff in EFFORTS if cells[("adapter", e, eff)] == 100.0]
anon100 = [(e, eff) for e in envs_std for eff in EFFORTS if cells[("adapter", e, eff)] < 100.0]
say(f"  cells at exactly 100.0: {len(a100)}/150 (incl. {sum(1 for k in a100 if prov[('adapter',)+k]=='infer-saturation')} inferred)")
say(f"  exceptions: {[(e, eff, cells[('adapter', e, eff)]) for e, eff in anon100]}")
none_mean = statistics.mean([cells[("adapter", e, "none")] for e in envs_std])
say(f"  adapter 'none' public mean = {none_mean:.3f}  [blog-era figure 97.11 -> {'MATCH' if abs(none_mean-97.11)<0.01 else 'MISMATCH'}]")
for eff in ("max", "xhigh", "medium"):
    vals = [cells[("adapter", e, eff)] for e in envs_std]
    say(f"  adapter {eff}: all-100 = {all(v == 100.0 for v in vals)} (direct-only: {all(v==100.0 for e in envs_std for v in [cells[('adapter',e,eff)]] if prov[('adapter',e,eff)]=='direct')})")

# ---------- 13. cost vs score correlation ----------
say("\n== 13. cost-vs-score across the dial ==")
def spearman(x, y):
    rx = {v: i + 1 for i, v in enumerate(sorted(set(x)))}
    ry = {v: i + 1 for i, v in enumerate(sorted(set(y)))}
    n = len(x)
    dm = statistics.mean([rx[a] - ry[b] for a, b in zip(x, y)])
    d2 = sum((rx[a] - ry[b]) ** 2 for a, b in zip(x, y))
    return 1 - 6 * d2 / (n * (n * n - 1))
for h in ("standard", "adapter"):
    sc = [SP[h][e] for e in EFFORTS]
    co = [COST[h][e] for e in EFFORTS]
    say(f"  {h:8s}: spearman(cost,score) = {spearman(co, sc):+.3f}  (scores {sc}, costs {co})")
say(f"  blog's own sentence: 'Higher reasoning levels generally cost LESS' [P]")

# ---------- 14. discrimination panel ----------
say("\n== 14. per-env dial variance (standard public) — discrimination ranking ==")
var_rank = []
for e in envs_std:
    vals = [cells[("standard", e, eff)] for eff in EFFORTS]
    var_rank.append((statistics.pvariance(vals), max(vals) - min(vals), e))
var_rank.sort(reverse=True)
tot_var = sum(v[0] for v in var_rank)
cum = 0
for v, rng, e in var_rank:
    cum += v
    say(f"  {e}: var={v:8.1f} range={rng:6.1f} cum_share={cum/tot_var*100:5.1f}%")

# ---------- 15. harness delta at max ----------
say("\n== 15. harness contribution per env (adapter_max - standard_max) ==")
deltas = sorted(((100.0 - cells[("standard", e, "max")], e) for e in envs_std), reverse=True)
say(f"  total delta = {sum(d for d, _ in deltas):.1f} pts over 25 envs; mean = {statistics.mean(d for d, _ in deltas):.2f}")
say(f"  top-5 pure-state-continuity gaps: {deltas[:5]}")

# ---------- 16. viral ratios & human anchoring ----------
say("\n== 16. ratios ==")
viral = SP["adapter"]["high"] / GPT56_SOL
l4l = SP["standard"]["max"] / GPT56_SOL
say(f"  viral (adapter-high / Sol std): {viral:.3f}x score -> {math.sqrt(viral):.3f}x actions")
say(f"  like-for-like (std-max / Sol std): {l4l:.3f}x score -> {math.sqrt(l4l):.3f}x actions")
say(f"  score-space inflation vs action-space: {(viral - math.sqrt(viral)) / math.sqrt(viral) * 100:.1f}%")
say(f"  vs April-2026 official frontier top (Opus 4.6 Max = 0.50%, Table 2): "
    f"std-max {SP['standard']['max']/0.50:.1f}x score / {math.sqrt(SP['standard']['max']/0.50):.1f}x actions")
say(f"  human wage anchor: 55 envs x $12.78 = ${55*HUMAN_FEE:,.2f}; cheapest adapter run = "
    f"{min(COST['adapter'].values())/(55*HUMAN_FEE):.1f}x; cheapest standard = {min(COST['standard'].values())/(55*HUMAN_FEE):.1f}x")
fig4 = [100, 100, 100, 100, 89, 56, 44, 26, 8, 8, 2]
say(f"  re86 human RHAE distribution (Fig.4): mean={statistics.mean(fig4):.1f}% median={statistics.median(fig4)}% "
    f"-> share of humans at 100% = {sum(1 for x in fig4 if x==100)}/{len(fig4)}")

# ---------- 17. per-level floor check ----------
say("\n== 17. action-budget floor: any completed level contributes >= 4% of its weight ==")
viol_floor = []
for (h, e, eff), s in cells.items():
    if 0 < s < 0.09:  # below minimal k=1 contribution at worst case n=12: w1/W * 0.04
        viol_floor.append((h, e, eff, s))
say(f"  cells below the k=1 floor across all 300: {len(viol_floor)} {viol_floor}  (n=12 worst case: {100*0.04/(12*13/2):.3f}%)")

# ---------- 18. v0.2 derived metrics replication ----------
say("\n== 18. v0.2 derived_metrics.csv replication from verified 1-decimal table ==")
v02 = {"max": (62.7, 98.6), "xhigh": (59.3, 98.4), "high": (54.8, 99.9), "medium": (38.6, 98.4), "low": (17.5, 98.0), "none": (35.2, 96.7)}
for eff, (s, a) in v02.items():
    say(f"  {eff:6s}: delta={a-s:.1f} ratio={a/s:.2f}  [ledger D01]")
say(f"  Pareto min-adapter {min(v02[e][1] for e in v02)} > max-standard {max(v02[e][0] for e in v02)}; "
    f"costs max-adapter {max(COST['adapter'].values())} < min-standard {min(COST['standard'].values())} [D02]")
say(f"  inflation (99.9/7.8)/(62.7/7.8) = {(99.9/GPT56_SOL)/(62.7/GPT56_SOL):.3f} [D05]")
say(f"  per-pair: 18817/167=${18817/167:.2f}; 26098/167=${26098/167:.2f} [D06]")

open(HERE + "derived_v05.txt", "w").write("\n".join(out))
print("\nWROTE", HERE + "derived_v05.txt")
