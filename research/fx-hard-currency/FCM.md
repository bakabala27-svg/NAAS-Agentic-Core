# FCM v0.1 - The sanction is not a fine, it is forced conversion

> **Status:** research result. Article-level identifiers verified against a secondary
> source that quotes the articles; the literal Journal Officiel text is **not yet**
> extracted. Nothing here is sellable before that extraction.

Companion code: `fcm_model.py` (standalone, stdlib only).

---

## 1. The three findings that overturn RSM v0.1

| # | Finding | Article |
|---|---|---|
| 1 | Repatriation is due **the day the non-resident client pays**, not within a day budget | Reg 26-02 art. 2, rewriting Reg 07-01 art. 61, final paragraph |
| 2 | Online digital services, startup services and non-trader professionals are **exempt from bank domiciliation**, replaced by a declaration (project description, unit price, online posting date) | Reg 07-01 art. 57, as amended by Reg 21-01 |
| 3 | The sanction for non-domiciled or late proceeds is **collection in DZD**, not a monetary fine | Reg 07-01 art. 67, as amended by Reg 21-01 |

Article 61 term history: 120 days (Reg 07-01, JO 31 of 2007-05-13) -> 180 (Reg 11-06,
2011-10-19) -> 360 (Reg 16-04, 2016-11-17) -> **120** (Reg 26-02, JO 58 of 2026-08-12).
The widely repeated "cut to 180 days" headline is wrong: the baseline was 360, and 180
is only the insured maximum, not the rule.

---

## 2. What this retracts from RSM v0.1 (knowledge note #001)

1. The `gap = 120 - sum(days)` model and its 24-combination table are **withdrawn**.
   Article 61 grants no day budget.
2. The "practical net-60 ceiling" is **withdrawn** as a quantitative inference.
3. The speculative penalty of 1x-2x the amount is **withdrawn**, replaced by finding 3.
4. The 48-hour domiciliation rule **does not apply** to the exporter class in question.

---

## 3. The quantified consequence

At official 151 DZD/EUR against a parallel quote of 280 DZD/EUR, mandatory conversion
destroys **46.07%** of real purchasing power (parallel premium 85.4%).

| Annual EUR revenue | EUR-equivalent lost | Kept |
|---|---|---|
| 12,000 | 5,529 | 6,471 |
| 24,000 | 11,057 | 12,943 |
| 60,000 | 27,643 | 32,357 |
| 120,000 | 55,286 | 64,714 |
| 1,800,000 | 829,286 | 970,714 |

**"100% retention" is not free use.** Instruction 06-2021 keeps the proceeds in an FX
account split 80% imports / 20% export promotion, forbids a debit balance, treats cash
withdrawal as exceptional, and converts the balance to DZD on closure. Retention is a
spending restriction, not currency freedom.

### Tranche vs full stream (EUR 120,000)

| Reserve converted | EUR lost | Ratio vs full stream |
|---|---|---|
| 10% | 5,529 | x10.0 cheaper |
| 25% | 13,821 | x4.0 cheaper |
| 100% | 55,286 | - |

### Sensitivity to the parallel rate (EUR 120,000)

| Parallel DZD/EUR | Haircut | EUR lost |
|---|---|---|
| 200 | 24.50% | 29,400 |
| 240 | 37.08% | 44,500 |
| 280 | 46.07% | 55,286 |
| 320 | 52.81% | 63,375 |

---

## 4. Commercial reading

A EUR 400 "payment-path audit" pays for itself if it avoids **3.62%** of the haircut at
EUR 24,000 exposure, **1.45%** at EUR 60,000, and **0.72%** at EUR 120,000. That is the
entire commercial claim - no certificate, no guarantee.

**Demand is untested.** Zero paid invoices. The model sizes the pain; it does not prove
anyone will pay to have it measured.

---

## 5. Blocking gate before any sale

Extract the literal text of Reg 26-02 art. 61 from Journal Officiel 58 (2026-08-12,
p. 28) via `joradp.dz`, plus Instruction 06-2021 and arts. 57/67 of Reg 07-01. Until
then every figure above is conditional on a secondary source's quotation.

---

## 6. Reproduction

```bash
python3 research/fx-hard-currency/fcm_model.py
```

The script runs an assertion self-check on every quoted figure before printing.

---

*FCM v0.1 - 15 September 2026*
