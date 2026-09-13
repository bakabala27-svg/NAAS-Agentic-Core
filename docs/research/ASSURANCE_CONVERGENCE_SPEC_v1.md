# Assurance Convergence Specification v1

**Status:** documentation only. No new CI gate, no new decision round, no measured claim.
**Base commit:** `7117a0d1c28e950ddabe0a863b763fbc029c5316` (`chore(acceptance): refresh git_change_snapshot against origin/main`, 2026-09-13).
**Scope:** reconcile the external commercial board (Notion) with the repository's measured artifacts, then state four derived instruments precisely enough to be refuted.
**Evidence discipline:** every number below is either (a) quoted from a named repo artifact, (b) quoted from a dated external source, or (c) marked `(F)` for forecast / `UNSOURCED`. Nothing here is a new measurement.

---

## 0. Why this document exists

The repository now carries six research batches (CDKC · VEP · CND · AHW · DLY · FXR) and five decision rounds, while the commercial board lives outside the repo. Divergence between the two is not a cosmetic problem: the board is the authority that authorises or forbids work, and a board that quotes superseded numbers authorises the wrong work.

This document does three things and nothing else:

1. records the divergences found by matching the board against HEAD (§1);
2. fixes one canonical value per contested fact (§2);
3. states four instruments that follow from the repository's own measurements plus the 2026 literature, each with a falsification test (§3).

**Authority order.** Board kill-list > this document > any prompt or plan. Where this document appears to authorise work the board forbids, the board wins.

---

## 1. Coherence ledger (repo vs. board)

| # | Divergence | Evidence | Resolution |
|---|---|---|---|
| C1 | Board builds `ك-03` (hard-currency channel) on a "50% of export proceeds" retention rule | `FXR` batch, commit `a6333e2`: instruction 06-2021 art. 4 + Bank of Algeria communiqué 2021-07-18 state **100%**, services and startups explicitly covered — recorded as **REFUTED** | The `ك-03` premise is withdrawn. The blocker is *account opening and repatriation timing*, not a retention haircut |
| C2 | Board targets **$8,000/mo** solo practice | `FXR`: ANAE services ceiling 5,000,000 DZD/yr ≈ **$3,122/mo** worst case | The $8,000/mo target is **2.56× the legal ceiling of the structure the board itself recommends**. Canonical target: **$3,000/mo** under ANAE, with a migration trigger at 70% of ceiling (≈$26,225/yr) |
| C3 | Board doctrine: repatriation "< 360 days", "day 306" | `FXR`: règlement 26-02 (JO n°58, 2026-08-12) → **120 days**, 180 only with prior export-credit insurance, >180 prohibited | Doctrine §01 and K4 are **superseded**, patched additively per D-290 L10 (primary JO text unfetchable — limit declared, not hidden) |
| C4 | Headline accuracy quoted as 99.9% / 99.95% / 99.99% / 98.6% across board pages | `studies/claim-scope-audit-001/` v0.5 re-extraction, `cells_public_v05.csv` | One audited value: **99.95%**. 99.9% may appear only as "market shorthand", never as the audited figure. Embargo 98.6% and live 99.99% are *series members*, not alternatives |
| C5 | Pricing appears as five incompatible ranges ($500–1,500 · $800–2,000 · $1,500–4,000 · $2,000–6,000 · $4,000–12,000) | board pages; `س-07` | One ladder: **$750 → $2,500 → $7,500**, each rung unlocked only by a named reference. All other ranges struck |
| C6 | SCR-12 control #12 is simultaneously "pending", "second person re-tests", and "closed for aggregate+public layers" | `docs(studies)` commit `eb2d798` closes it for aggregate+public only | Split into **#12a** (independent second-assessor replication — OPEN, cannot be self-closed) and **#12b** (layer-classified replication — PARTIAL). Independent items, never reported as one |
| C7 | Board EU AI Act dates differ across three pages | — | One line, quoted verbatim everywhere: GPAI and Commission powers **2026-08-02**; Annex III high-risk **2027-12-02**; product-embedded **2028-08-02** |

**Consequence of C1+C2 together.** The board's revenue target was set against a legal structure that cannot hold it, while the barrier it feared most does not exist as stated. Both errors point the same way: the constraint is *entity and collection mechanics*, not market size and not currency retention.

---

## 2. Canonical facts

Use these exact values; do not paraphrase, round, or re-derive.

| Fact | Canonical value | Producer |
|---|---|---|
| Harness inversion | 62.7% at $26,098 vs 99.95% at $18,817 | audit #001 v0.5 |
| Reasoning disabled | 96.7% | audit #001 v0.5 |
| Cost per environment | $18,817 / 55 envs = **$342/env** | derived, v0.5 |
| Withdrawn figure | $112.68/pair — **do not quote** | v0.5 correction |
| Dial concentration | top-10 environments = 85.2% of variance | v0.5, Fig. set |
| Chance model | p = 3.3e-34 (fixed-sample; see §3.2) | v0.5 |
| Identifiability | 58 distinct cap-lattices, 0/100 collisions | v0.5 |
| Envelope scaling | **E = √RHAE** — linear-on-quadratic arithmetic is prohibited repo-wide | eqs. (1)–(3) |
| Validity ceiling | 8.85 days; 731-day corridor | D-293 |
| Entity ceiling | 5,000,000 DZD/yr ≈ $3,122/mo | FXR |
| Round-trip loss | convert-then-rebuy = −44.0%; paying costs from the FX account is worth 1.786× | FXR |

---

## 3. Four instruments

Each instrument is stated as: definition → why it is not already in the repo → falsification test. None introduces a new CI gate; each extends an existing module in `shared/research/`.

### 3.1 CRL — Claimable Resolution Limit

**Definition.** A benchmark comparison has a resolution floor. With per-item sampling variance σ²_s and verdict-instability variance σ²_v (the latter arising from threshold-boundary flips, not from item sampling), the smallest defensible gap between two systems is

```
Δ_min = z_{1-α/2} · sqrt( 2·σ²_s + 2·σ²_v )
```

Any published gap below Δ_min is **unclaimable**: it is an artefact of measurement apparatus, exactly as two stars closer than the Rayleigh criterion are one blur regardless of exposure time.

**Why it is new here.** The repository already measures threshold density and verdict flipping (`assurance_window.py`), and the 2026 literature supplies the sampling half (error bars on evals, arXiv:2411.00640) and the reliability half (*Measurement Without Validity: The Compounding Reliability Problem in Agentic AI Evaluation*, arXiv:2608.00794). Neither side composes the two into a single publishable floor. The commercial consequence is direct: **CRL converts "the vendor's number is misleading" into "the vendor's number is below the resolution of its own apparatus"** — a statement about instruments, not about intent, and therefore not defamatory (addresses `ت-12`).

**Supporting result.** Threshold-Density: with verdict threshold τ, noise scale σ, and boundary density f(τ),

```
E[unstable items] = κ · σ · f(τ) · N,   κ = 2/√π ≈ 1.128
```

and verdict stability S requires `n ≥ ln(0.05)/ln(S)` → **29 / 59 / 299** runs for S = 0.90 / 0.95 / 0.99. Only boundary-band items need resampling, which is where the cost saving lives.

**Anti-gaming requirement.** CRL is trivially gamed by understating f(τ). Any CRL figure must ship with a disclosure of τ, σ, the density-estimation bandwidth *and its selection rule*, f(τ), and the density profile over [τ−5σ, τ+5σ] at ≥41 points. A CRL without that disclosure is void.

**Falsification.** Take any two systems whose published gap is below their CRL. Re-run both at n ≥ 59 on the boundary band. If the ranking is stable across ≥95% of resamples, CRL is over-conservative and the formula is wrong.

### 3.2 AVCL — Anytime-Valid Claim Ledger

**Definition.** A claim's evidence is not a p-value but a **wealth process**. For each claim, maintain an e-process E_t; the claim is quotable iff `sup_t E_t ≥ 1/α`, and Ville's inequality gives `P(sup_t E_t ≥ 1/α) ≤ α` *at every stopping time*, including stopping times chosen after looking.

**Why it matters to this repository specifically.** `p = 3.3e-34` was computed under fixed-sample assumptions while the analysis was in fact monitored continuously and extended when interesting. That is optional stopping, and it inflates Type-I error by an amount that is not bounded by the reported p. The 2026 literature has settled the fix: safe anytime-valid inference and e-processes (Ramdas, Grünwald, Vovk & Shafer, *Statistical Science* 38(4):576–601; Ramdas & Wang, *Foundations and Trends in Statistics*, 2025), with LLM-specific instantiations in SERPANT (ICML 2026, e-processes for online model ranking with family-wise control at any monitoring time) and CITE (arXiv:2605.05873, anytime-valid certification of self-consistency, explicitly handling the *unseen-category* problem when the answer set grows during sampling).

**Restatement required.** Recompute the chance model as an e-process with Bonferroni over the full comparison family (69 × 5 = 345). Report `sup_t E_t` and the stopping rule. If the conclusion inverts, **the inversion is the deliverable** — do not retune.

**Second correction, same family.** The identifiability claim "0/100 collisions" is a rule-of-three situation: 0 of 100 supports only **≤0.03 collision rate (95% CI, Clopper–Pearson)**. Reaching ≤0.003 needs ~1,000 trials. Restate accordingly.

**Third correction.** 32 of the 300 cells are constraint-solved or saturation-inferred, i.e. partially derived from the model being tested. Recompute leave-out on the 268 direct cells and publish both numbers side by side; a conclusion that survives only on 300 is a conclusion about the inference procedure.

**Falsification.** If the e-process crosses 1/α at a *smaller* sample than the fixed-sample test required, the fixed-sample analysis was merely inefficient, not invalid, and this section overstates the problem.

### 3.3 The determinism cell — D0…D3 × 7-axis pin vector

**Definition.** Reproducibility is not a scalar. Fix the pin vector

```
a1 weights + version        a5 hardware + kernel
a2 decoding params + seed   a6 toolchain / GEMM library
a3 batch composition        a7 input context + memory + tool state
a4 tensor / pipeline parallel degree
```

Classes: **D0** asserted · **D1** trace-fixed · **D2** distributionally stable · **D3** bitwise identical.

Two facts make this a **partial order, not a scale**: a system can be D2 on {a1…a3} and D0 on {a4, a5}, and such pairs are *incomparable*. A `dominates()` predicate must therefore be able to return "incomparable"; any total ordering is a defect. **A class label quoted without its axis set is semantically undefined and must be rejected, not warned about.**

**Orthogonal layer lattice:** `aggregate ⊒ public ⊒ per-run ⊒ per-token`. The certified object is a **cell** (class × axis set × layer), never a class alone.

**Grounding in the 2026 state of the art.** Batch-invariant kernels (Thinking Machines, 2025) remove batch-size dependence — axis a3 — and nothing more. The follow-up work is explicit: "the technique is currently limited to variations related only to the batch dimension … but not to other forms of nondeterminism like changing the TP sizes or GPU types" (arXiv:2506.09501v2, NeurIPS 2025). LLM-42 (arXiv:2601.17768, Microsoft Research / UW / IISc) attacks the same problem through verified speculation. Token-probability analysis (arXiv:2601.06118) shows nondeterminism persists at the probability layer even where text output looks stable — which is precisely why `per-token` sits at the bottom of the lattice.

**Repository's measured position:** **D2 at {aggregate, public}**. That is the exact content of "SCR-12 #12 closed for aggregate+public layers" and the reason #12 must split into #12a/#12b (C6).

**Required-class rule.** Irreversible actions require D2 at S ≥ 0.95 (n ≥ 59). Everything else requires D1. **D3 is never claimed on shared inference infrastructure**, because floating-point non-associativity under dynamic batching and variable reduction order makes bitwise identity unavailable in principle, not merely unimplemented.

**Falsification.** Exhibit a real deployment where a single scalar reproducibility grade predicts verdict stability as well as the cell does. The partial order then buys nothing.

### 3.4 AXR — Assurance Exchange Rate

**Definition.** Determinism is bought, not declared. AXR is the marginal cost of raising one pin axis by one class, in dollars per environment:

```
AXR(a_i : D_k → D_{k+1}) = Δcost / n_envs
```

**Anchor.** The repository's own measurement gives the denominator and the baseline: $18,817 / 55 environments = **$342/env**. Every determinism upgrade can therefore be quoted in multiples of a number the buyer already understands.

**Why this is the commercially load-bearing instrument.** The board's diagnosis is "the product is a document, not a machine" (`ك-02`). AXR is the smallest object that turns assurance into a line item: a buyer does not purchase "rigour", they purchase *this axis, at this class, at this layer, for this many dollars per environment*. It also prices the refusal: if AXR for a4 (parallelism) is unbounded on a vendor's hosted endpoint, that is a measured procurement fact, not an opinion.

**Pairs with pin decay.** Certificates expire without vendor cooperation. Detection is a two-sided CUSUM on log σ with a calibrated and *reported* ARL₀; a certificate then carries a measured half-life, bounded above by the repository's existing 8.85-day validity ceiling (D-293). Expiry is mechanical, not negotiated.

**Falsification.** Measure AXR for one axis on two vendors. If the figures differ by less than the CRL of the cost measurement itself, AXR is not discriminative and should be dropped.

---

## 4. Where this sits in the assurance literature

Three independent 2026 movements converge on the same gap, and none of them closes it:

- **Validity.** Construct-validity work (Zhou et al., *Nature*, 2026; *Measurement to Meaning*, arXiv:2505.10573; *Science of AI Evaluation Requires Item-level Benchmark Data*, arXiv:2604.03244) establishes that a benchmark number does not license a capability claim. It does not say **which numbers are unclaimable** — §3.1 does.
- **Statistics.** SAVI and e-values give valid inference under monitoring. They are not wired into any published audit ledger — §3.2 does that.
- **Attestation.** Audit-as-code (Frontiers in AI, 2026) and cryptographic binding with reproducibility verification (arXiv:2603.14332, incl. a DV-SNARK path ~690× cheaper by proving the *verification metric* rather than the forward pass) make assurance machine-checkable. They assume a reproducibility grade exists — §3.3 supplies its correct algebra, §3.4 its price.

The unoccupied position is therefore not "more governance". It is: **the measurement of what cannot be measured, priced per environment, with an expiry date.** Negative results are the product.

---

## 5. Non-goals

- No `DECISION-ROUND-06`. The board forbids a sixth round before a paid invoice.
- No expansion of proof coverage as an end in itself.
- No instrument beyond §3.1–§3.4.
- No additions to `CLAUDE.md` (173,035 B) or `spec.md` (45,881 B).
- No platform, dashboard, or frontend work.
- No price outside the $750 / $2,500 / $7,500 ladder.
- No D3 claim. No stability claim without its cell. No invented citation — unverifiable claims are marked `UNSOURCED`.
- Nothing here is legal, financial, or investment advice.

---

## 6. Open items this document does not close

1. **`.env.docker` is tracked (909 B) with no `.example` counterpart.** Untracking it is cheap; rotating whatever it contains is owner-only and cannot be delegated.
2. **Root hygiene.** `SYNC_TEST_MARKER.txt` (29 B), `pr_description_test.md` / `pr_description_test2.md` (3,240 B each, byte-identical), `fix.py` (400 B), `test_validate.py`, `test_visual_pedagogy_ui.py`, `uv.lock` (52 B — empty), `.magic_urls` (61 B), `live_db_restructure.py` at root, and `Introduction to Agents.pdf` (9,473,606 B) tracked as a blob rather than a release asset.
3. **Independence.** Most commits are authored by an agent and committed under a different identity. Until a trusted-party count is declared per axis, `#12a` cannot be closed by anyone inside this repository — including the agent writing this file.
4. **Owner-only actions.** Entity registration, professional account opening, key rotation, buyer interviews, and the first collected invoice. These are listed, never simulated.
