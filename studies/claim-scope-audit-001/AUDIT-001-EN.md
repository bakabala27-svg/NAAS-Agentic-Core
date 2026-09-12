# Claim-Scope Audit #001 — Harness Attribution Re-Audit (v0.2)

> **Claim under audit:** “GPT-6 Astra scores 99.9% on ARC-AGI-3” — OpenAI launch materials, 3 September 2026.
>
> **Auditor:** independent. No compensation from any party named. **Method:** public primary sources only; no systems accessed; no party contacted.
>
> **Date:** 2026-09-12 · **Version:** 0.2 (supersedes v0.1 of the same date). SCR-12 control #12 (independent reproduction) remains **pending**; until reproduced this is a working assessment, not a finding.
>
> **Provenance convention:** `[F]` = fact from a primary/relay source (URL in ledger) · `[D]` = derivation — arithmetic or logic *computed by this audit* from `[F]` rows, independently falsifiable · `[A]` = assumption/reading, never asserted as fact. `direct` = fetched and read by this auditor; `relay` = reported by a secondary outlet, not re-fetched.

---

## 0. Executive summary — what changed between v0.1 and v0.2

v0.1 *verified* the claim. v0.2 *measures* it. The difference is the product.

1. **The 37-point gap is now a number with a curve, not a slogan.** Matched by reasoning effort, the harness is worth **35.9 points at max reasoning and 80.5 points at low reasoning** (`[D]`, §2.1). The widely quoted “37 points” is itself a cross-effort comparison (adapter-**high** vs standard-**max**). Memory and reasoning are *substitutes*, and the substitution ratio is computable from the authors’ own table.
2. **The adapter Pareto-dominates the standard harness.** Every one of 6 adapter cells beats *every one* of 6 standard cells on **both** score and cost (`[D]`, §2.2). No standard configuration wins on any axis. That is not “the better number was also cheaper” — it is structural.
3. **Score is invariant to the reasoning dial inside the adapter** (SD ≈ 0.94 points across 6 levels) and dominant without it (range 45.2 points) (`[D]`, §2.3). “99.9%” is a property of the scaffolding’s memory, almost independent of how hard the model thinks.
4. **The post-launch “revision” has a mechanical, table-visible explanation.** The embargo draft (98.6%) is numerically identical to ARC’s adapter-**max** cell; the live post (99.9%±) corresponds to the adapter-**high** cell (`[D]`, §3). Under the adapter, max *effort* ≠ max *score*, and the two drafts picked different “top” cells. No published cell reads “99.99%.”
5. **“99.9%” is not a solve rate.** RHAE (Relative Human Action Efficiency) is a per-level `(human_actions / AI_actions)²` efficiency ratio against an upper-median first-time human baseline, capped near unity, aggregated per game (`[F]`, §1.2). “Solved 99.9% of the 167 pairs” is a mistranslation the market ran with — and v0.1’s §1 silently imported it.
6. **The generation gap was inflated ~59% by harness mixing** (`[D]`, §2.4). The viral 99.9%-vs-7.8% is a cross-harness comparison; the like-for-like is 62.7%-vs-7.8%. (99.9/7.8) ÷ (62.7/7.8) = **1.59**.
7. **The “cheaper” run is only cheaper than the other AI run.** ~$113 per pair vs ~$12.78 per game for the paid human baseline — and ~5 orders of magnitude above the authors’ own “brain-energy” floor (`[D]`, §2.5). The efficiency the benchmark rewards (actions) is not the efficiency buyers pay for (tokens).

**Verdict (v0.2):** *True-in-scope, harness-dependent-in-substance, misread-as-solve-rate-in-reception.* The claim describes a real, near-complete, human-or-better efficiency result — **under one of the two harnesses the benchmark itself defines**. It was received as a model property and as a solve fraction. It is neither. The distance between those three things is what this product prices.

---

## 1. What was actually measured (corrected)

### 1.1 The full primary table — ARC Prize’s own numbers (`[F]`, direct: arcprize.org/blog/astra)

| Reasoning effort | Standard harness (provider-neutral) | Provider Adapter (OpenAI memory/compaction) |
| --- | --- | --- |
| max | 62.7% · $26,098 | 98.6% · $17,332 |
| xhigh | 59.3% · $37,317 | 98.4% · $18,147 |
| high | 54.8% · $40,705 | **99.9% · $18,817** |
| medium | 38.6% · $48,090 | 98.4% · $19,285 |
| low | 17.5% · $38,166 | 98.0% · $21,298 |
| none | 35.2% · $49,791 | 96.7% · $23,457 |

- Both headline numbers were published **by the benchmark’s own authors** on launch day (`[F]`).
- Both harnesses solved **167 game-reasoning pairs**; adapter runs used **49% fewer tokens** and were **~3.66× faster** (`[F]`).
- **Standard harness:** max effort = max score (62.7% at max). **Adapter:** max effort (98.6%) ≠ max score (**99.9% at high**). This asymmetry is the root of §3.
- The “bombshell row” from v0.1 stands, corrected: adapter-**none** (96.7%, $23,457) beats standard-**max** (62.7%, $26,098) by 34.0 points **and** costs ~$2.6K less (`[D]`).

### 1.2 What “99.9%” *is* — RHAE (`[F]`, direct: ARC-AGI-3 technical report / scoring docs)

- ARC-AGI-3’s score is **RHAE** — Relative Human Action Efficiency. Per completed level: `min(1.15, human_actions / AI_actions)²`, aggregated per level → per game (weights increasing with level), averaged over games, with a completion cap (`[F]`).
- The human baseline is the **upper-median (2nd-best) first-time player of 10** per environment (`[F]`).
- **Consequence the market dropped:** “99.9%” is an *efficiency-weighted aggregate*, **not** “solved 99.9% of the 167 pairs.” 99.9% × 167 = 166.83 is arithmetic that has no referent here. The correct translation is roughly: *“completed the semi-private set at ≈ human-or-better action efficiency — while reusing its own memory between turns.”*
- “Astra beat the human baseline on 96% of levels” means it used fewer *actions* than the 2nd-best of 10 first-timers on 96% of levels — an action-count comparison against an upper-median baseline, not a head-to-head solve race (`[F]`/`[D]`).

### 1.3 The category error (this is the deep finding v0.1 missed)

v0.1 treated “99.9%” as a solve rate throughout — its §1 table, its “167 pairs” arithmetic, and its reception analysis all inherit that. Under RHAE, **the same number means something stronger and something weaker at once**:

- **Stronger:** near-total completion of the semi-private set at human-or-better action economy, under the adapter. The capability is real.
- **Weaker:** it is not a property of the model alone — it is the product of the model × the memory scaffold, and it is *not* a fraction of tasks solved. The “AGI” reading requires both mistranslations at once.

The public reception committed both. The vendor’s fine print contradicts neither, which is exactly why a claim-scope audit is the right instrument.

---

## 2. The derived layer — numbers nobody else computed

All of §2 is `[D]`-grade: arithmetic on ARC’s own 6×2 table (ledger: `derived_metrics.csv`). Every cell is re-derivable by a hostile reader in minutes; that is the point.

### 2.1 Harness contribution, matched by reasoning effort

| Effort | Adapter − Standard (points) |
| --- | --- |
| max | 98.6 − 62.7 = **35.9** |
| xhigh | 98.4 − 59.3 = **39.1** |
| high | 99.9 − 54.8 = **45.1** |
| medium | 98.4 − 38.6 = **59.8** |
| low | 98.0 − 17.5 = **80.5** |
| none | 96.7 − 35.2 = **61.5** |

- The quoted “37-point gap” = adapter-**high** (99.9) − standard-**max** (62.7) = 37.2 — a **cross-effort** comparison. Matched-effort, the harness is worth **35.9 to 80.5 points**.
- **The harness’s contribution *grows* as reasoning falls.** Score ratio (adapter/standard): max 1.57× → low **5.60×** (§2.4, ledger). Memory is a *substitute* for reasoning, not a complement.

### 2.2 Strict Pareto dominance

Every adapter cell beats every standard cell on score (min 96.7% vs max 62.7%) **and** on cost (max $23,457 vs min $26,098). No standard-harness configuration wins on either axis. For a buyer this is a decision rule, not a nuance: **under the benchmark’s own numbers, the adapter is the dominating strategy for this model on this set.**

### 2.3 Effort-invariance vs effort-dominance

| | Standard | Adapter |
| --- | --- | --- |
| Score range across 6 effort levels | 17.5 → 62.7 = **45.2 pts** | 96.7 → 99.9 = **3.2 pts** |
| Score SD | ≈ **15.9** | ≈ **0.94** |
| Reasoning dial effect (none→best) | +27.5 pts (35.2→62.7) | +3.2 pts (96.7→99.9) |

The reasoning dial moves **27.5 points** without the adapter and **3.2** with it — the adapter has pre-empted ~88% of what the dial would buy. “99.9% at high” is, operationally, “96.7% at none, plus rounding.” `[D]`

### 2.4 The generation-gap inflation is now a number

- Viral: 99.9 / 7.8 = **12.81×**. Like-for-like: 62.7 / 7.8 = **8.04×**. Inflation from harness mixing = 12.81 / 8.04 = **1.59× (~59%)**.
- The like-for-like jump remains enormous (8×); the audit does not need the gap to be fake to price the mispricing.

### 2.5 Cost, re-anchored to the human it “surpassed”

| Per-unit | Value | Source |
| --- | --- | --- |
| Adapter-high per pair | $18,817 / 167 = **$112.68** | `[D]` |
| Standard-max per pair | $26,098 / 167 = **$156.28** | `[D]` |
| Human participant fee | **~$12.78 / game** (before bonuses) | `[F]` (ARC blog) |
| Human “brain energy” floor | **~0.067¢ / game** | `[F]` (ARC footnote, authors’ own device) |

The “cheaper” adapter run is **~8.8× the paid human fee per game** and **~168,000× the authors’ energy floor**. The benchmark rewards *action* efficiency; the buyer pays *token* efficiency. These two efficiencies are now observably different currencies.

### 2.6 What “saturated” actually means — set-conditional

“ARC-AGI-3 is saturated” is only true **conditional on three dropped clauses**: (i) the **semi-private** set (Nvidia’s AVO harness already hit **100.00 RHAE on the 25 public demo environments** with Opus 5 in Aug 2026 — “public-set scores are not competition results”); (ii) the **Provider Adapter** (standard = 62.7%, unsaturated); (iii) a ≤~100%-capped aggregate. Drop any clause and the word “saturated” breaks. `[F]`/`[D]`

---

## 3. The revision mechanism — from “numbers moved” to “which cell”

v0.1 reported the drift as an opaque event. It has a mechanical reading:

- ARC’s adapter table has **two candidate “top” cells**: max-effort = **98.6%** ($17,332) and best-score = **99.9%** ($18,817, at *high*).
- The pre-publication draft sent to media read **98.6%** — numerically identical to the adapter-**max** cell (`[F]`, relay: TNW/aiwiki; `[D]` identity).
- The live post reads **99.9%–99.99%** — corresponding to the adapter-**high** cell (`[D]`). **No published ARC cell reads 99.99%**; ARC prints at most one decimal. The fourth significant figure is untraceable to any primary table and is likely a rounding typo of 99.9 (`[D]`/`[A]`).
- Under the adapter, max *effort* ≠ max *score* — so “the best result” is ambiguous, and the two drafts resolved the ambiguity differently.

**Two readings, both priced:** (a) benign — a defensible choice to report the best-score cell, plus pre-launch noise, plus a rounding slip; (b) non-benign — post-hoc selection of the highest cell without a change log, exactly the failure mode the Snorkel/Stanford change-log norm (§4.5) exists to prevent. This audit records both and assumes neither (`[A]`). OpenAI’s “noise of a few percentage points” defense (via Fortune) is *testable* against this table: the move from 98.6 to 99.9 is precisely the move from the max cell to the high cell, a deliberate-looking step between published rows, not 0.1% of noise around a fixed cell.

---

## 4. What the claim does NOT establish (kept from v0.1, corrected)

1. **AGI.** Rejected explicitly by the benchmark’s authors: “not claiming that it is AGI”; co-founder Mike Knoop: “we lack evidence to call this AGI yet” (`[F]`, relay).
2. **A solve rate.** It establishes an efficiency-weighted aggregate under one harness (§1.2–1.3).
3. **Your-harness performance.** A buyer on a standard stack anchors to **~62.7%**, not 99.9% — a 37-point expectation gap between procurement deck and production (`[D]`).
4. **Independent replication of the headline.** Artificial Analysis’ own testing: Intelligence Index **61** (level with the model Astra replaces, behind Fable 5.1 and Meta’s Muse Spark 1.3), Coding Agent Index **67** (level with Opus 5/Fable 5), at **$10/M in / $50/M out ≈ 2.5× Sol’s price**; gains real but narrow (knowledge hallucination 92% → 51%, with regressions on banking support, scientific Python, long-context reasoning). **Caveat this audit adds:** those AA figures are from the *pre-rebuild* index; AA’s v4.2 rebuild (Sept 5, harder tasks + more private sets) moved Astra **up** to #2. A careful audit dates every AA citation to index version, or the vendor’s rebuttal kills it (`[F]`, relay).
5. **Methodological transparency.** Stanford’s Anka Reuel and Mike Hardy: the system card contains “barely any details” on the internal hallucination benchmark — “doesn’t even include the number of test items” — and named the practice **benchmaxxing** (`[F]`, relay).
6. **Commercial availability of every quoted configuration.** Sol’s ExploitBench figure (5.5% → 11.5% post-launch) reflects a reasoning level Sol does not sell commercially; OpenAI told Fortune it is investigating reverting it (`[F]`, relay).
7. **That “saturation” is harness-independent** (§2.6).

---

## 5. Buyer checklist — v2 (answerable from this case’s own table)

1. **Which harness, and which memory regime?** For this benchmark, memory is worth 35.9–80.5 points (§2.1). If the vendor’s number didn’t specify the harness, you do not have a number.
2. **Which reasoning-effort *cell*?** Here, adapter-**high** (99.9) beats adapter-**max** (98.6). Demand the cell, not “our best result” — the two drafts of this very launch picked different cells (§3).
3. **Is the metric a solve rate or an efficiency aggregate?** RHAE is the latter. Translate before you compare across vendors or generations.
4. **Cost per solved pair, always** — $112.68 vs $156.28 here (§2.5). “Cheaper” without the denominator is decoration.
5. **Change log since launch?** Demand the Snorkel norm: every revised figure gets a dated delta and a reason. Here, five-to-six metrics moved post-launch (hallucination 4.2→2→4.2; Fable 5.1 FrontierMath 87.8→78→83; Sol ExploitBench 5.5→11.5; ARC-AGI-3 98.6→99.9; two Anthropic HealthBench scores **up**) and the post was pulled and republished (`[F]`, relay). Note: two moves favored a *competitor* — the honest story is “mostly one way,” not “all one way.”
6. **Public, semi-private, or private set — and who holds the key?** “Saturated” is set-conditional (§2.6).
7. **Can a third party re-run it, at what cost, under whose harness?** If the answer is “our harness, unannounced price,” budget the 37-point haircut.

---

## 6. Evidence ledger (resolved)

Full machine-readable ledger: `evidence_ledger.csv`. Highlights:

| # | Statement | Grade | Provenance |
| --- | --- | --- | --- |
| 1 | Full 6×2 table (both harnesses, all effort levels) | [F] | **direct** — arcprize.org/blog/astra |
| 2 | 167 pairs; 49% fewer tokens; ~3.66× faster | [F] | **direct** (ARC blog) + relay |
| 3 | RHAE formula `min(1.15, h/a)²`; upper-median baseline | [F] | **direct** — ARC-AGI-3 technical report / docs |
| 4 | ARC Prize “not claiming AGI”; Knoop quote | [F] | relay — TNW (**direct-fetched**), aiwiki |
| 5 | Five/six metrics revised post-launch; specifics | [F] | relay — Fortune via TNW (**direct-fetched**) |
| 6 | Embargo 98.6% vs live 99.9%/99.99% | [F] | relay — TNW/aiwiki; relay figures differ on 99.9 vs 99.99 |
| 7 | Chollet 66% vs table 62.7% | [F] | relay — TNW, Superpower Daily |
| 8 | Artificial Analysis figures + v4.2 rebuild timing | [F] | relay — TNW, yellow, biggo |
| 9 | “Benchmaxxing”; system-card gaps | [F] | relay — TNW (**direct-fetched**), ctaio |
| 10 | All of §2 (Pareto, effort-invariance, leverage, inflation, cost re-anchor) | [D] | computed from row 1 by this audit |
| 11 | Cell-provenance of the 98.6→99.9 revision | [D] | identity of embargo figure with adapter-max cell |
| 12 | Intent behind the revisions | [A] | not assumed; both readings priced |

**Relay-integrity note:** relay sources disagree on whether the live post read 99.9% or 99.99%. This audit treats “99.99%” as unestablished (`[D]`/`[A]`) and does not build any argument on the fourth significant figure.

---

## 7. Verdict (v0.2)

**True-in-scope, harness-dependent-in-substance, misread-as-solve-rate-in-reception.**

- The claim is an *assembled-system* measurement (model × provider memory scaffold) that was received publicly as a *model* property **and** as a *solve fraction*. It is neither.
- The capability is genuine: near-complete semi-private completion at human-or-better action economy under the adapter. The attribution is not: the same weights score 62.7% without the adapter, and the score is near-invariant to how hard the model reasons (§2.3).
- The vendor documented the mechanics; the benchmark’s authors published both numbers; the market still traded the single largest figure, inflated ~59% against the like-for-like generation gap (§2.4).
- **The distance between what was measured, what was attributed, and what was bought is precisely the risk this product prices.**

---

## 8. Falsifiability — what kills each headline finding

- **§2.1/§2.2 die** if any single standard-harness cell beats any adapter cell on score *or* cost in a corrected table.
- **§2.3 dies** if adapter scores spread beyond a few points across effort levels in a rerun.
- **§3 dies** if OpenAI publishes a change log with a benign explanation for all revisions **and** shows the live 99.9% did not originate from the adapter-high cell.
- **§2.4 dies** if Sol’s 7.8% is shown to have come from the adapter too (then the viral comparison was like-for-like).
- **Verdict softens** if ARC Prize’s new side-by-side harness policy shows the standard/adapter gap closing in future models; **hardens** if the gap persists across providers.
- **Reproduction gate (SCR-12 #12):** until a second assessor re-derives §2 from the primary table, this document is v0.2, not a finding.

**Limitations:** public sources only; no systems accessed; no party contacted. AA and Fortune details are relay-grade and should be re-fetched at the archive URLs in the ledger before a v1.0.

---

## 9. Product note — what is actually sellable here (reprice)

The claim is public; the **derived layer (§2) and the buyer-side mapping (§5) are not.** Nobody else has computed the matched-effort harness curve, the Pareto result, the 1.59× inflation, or the $112.68-vs-$12.78 re-anchor. That is the moat, and it is the only part that survives a hostile re-read.

**Pricing model v2 (replaces the flat $800–$2,000/claim):**

- **Public bait:** the v0.2 executive summary (this document, §0–§2) — reputation bait, free.
- **Paid product:** the derived layer *mapped to a specific buyer’s contract* — e.g., “your vendor quoted an ARC-AGI-3 number on your harness; here is the corrected expectation and the price-per-pair delta you should negotiate.” Priced on the decision, not the page: **$2,000–$6,000 per mapped procurement**, or a **Scope Watch** retainer ($150–$400/mo) that re-runs the leverage table on every frontier launch and every buyer’s harness.
- **Rule:** never sell a fact; sell a *falsifiable number the client cannot get anywhere else* and the *decision it changes*.
