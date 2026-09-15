"""fcm_model.py - Forced Conversion Model (FCM v0.1).

What this file computes
-----------------------
The cost of the Algerian FX repatriation regime for a resident exporter of
digital services, expressed as the *haircut* imposed by mandatory conversion of
export proceeds at the official rate while the exporter's real purchasing power
is set by the parallel rate.

Legal basis (article-level identifiers; literal text extraction still pending)
-----------------------------------------------------------------------------
  - Regulation 26-02 (signed 2026-07-23, Journal Officiel 58 of 2026-08-12),
    article 2 rewrites article 61 of Regulation 07-01 (2007-02-03):
    120 days from shipment/completion, extendable to a 180-day maximum only
    with prior export-credit insurance, and - decisively - "in all cases the
    export proceeds must be repatriated on the day they are paid by the
    non-resident client".
  - Regulation 07-01 article 67 (as amended by Regulation 21-01, 2021-03-28):
    non-domiciled or late-repatriated proceeds are *collected in DZD*. The
    sanction is not a fine; it is forced conversion.
  - Regulation 07-01 article 57 (as amended by Regulation 21-01): exports of
    online digital services, startup services, and service exports by
    non-trader professionals are exempt from bank domiciliation, replaced by a
    declaration (project description, unit price, online posting date).
  - Instruction 06-2021 (2021-06-29): FX account retention (80% imports /
    20% export-promotion account), no debit balance, closure balance converted
    to DZD.

What FCM v0.1 retracts from RSM v0.1
------------------------------------
  1. The "gap = 120 - sum(days)" day-budget model and its 24-combination table:
     withdrawn. Article 61 grants no day budget, because repatriation is due on
     the day the client pays.
  2. The "practical net-60 ceiling": withdrawn as a quantitative inference.
  3. The speculative 1x-2x penalty: withdrawn, replaced by article 67 forced
     DZD collection.
  4. The 48-hour domiciliation rule: does not apply to online digital services
     or non-trader professionals (article 57).

Declared, falsifiable inputs
----------------------------
The official rate is observable; the parallel rate is a market quote that moves.
Every number below is a function of those two inputs only - no hidden constants.

Standalone: no third-party or repository imports. Run `python3 fcm_model.py`.
"""

OFFICIAL = 151.0  # DZD per EUR, official reference
PARALLEL = 280.0  # DZD per EUR, parallel market quote

# Annual hard-currency service-export revenue scenarios, in EUR.
EXPOSURES = (12_000, 24_000, 60_000, 120_000, 1_800_000)

# Share of the stream that would be exposed if only a tranche were repatriated.
TRANCHES = (0.10, 0.25, 1.00)

AUDIT_PRICE = 400.0  # EUR, price of one "payment-path audit"
SENSITIVITY = (200.0, 240.0, 280.0, 320.0)


def haircut(official: float = OFFICIAL, parallel: float = PARALLEL) -> float:
    """Fraction of real value destroyed by conversion at the official rate."""
    return 1.0 - official / parallel


def premium(official: float = OFFICIAL, parallel: float = PARALLEL) -> float:
    """Parallel-market premium over the official rate."""
    return parallel / official - 1.0


def loss(amount_eur: float, official: float = OFFICIAL, parallel: float = PARALLEL) -> float:
    """Real value lost, in EUR-equivalent purchasing power."""
    return amount_eur * haircut(official, parallel)


def breakeven_share(amount_eur: float, price: float = AUDIT_PRICE) -> float:
    """Share of the haircut an audit must avoid to pay for itself."""
    return price / loss(amount_eur)


def main() -> None:
    h, p = haircut(), premium()
    print(f"official {OFFICIAL:.0f} DZD/EUR | parallel {PARALLEL:.0f} DZD/EUR")
    print(f"haircut {h:.2%} | parallel premium {p:.1%}\n")

    print(f"{'annual EUR':>12}{'EUR lost':>12}{'kept':>10}")
    for amount in EXPOSURES:
        print(f"{amount:12,}{loss(amount):12,.0f}{amount - loss(amount):10,.0f}")

    print("\nTranche-only vs full-stream conversion (EUR 120,000 stream):")
    base = 120_000
    full = loss(base)
    for share in TRANCHES:
        value = loss(base * share)
        ratio = full / value if value else float("inf")
        print(f"  reserve {share:5.0%} -> lost {value:9,.0f}  (x{ratio:.1f} cheaper than full)")

    print(f"\nBreak-even for a EUR {AUDIT_PRICE:.0f} payment-path audit:")
    for amount in (24_000, 60_000, 120_000):
        print(f"  exposure {amount:8,} -> must avoid {breakeven_share(amount):6.2%} of the haircut")

    print("\nSensitivity to the parallel rate (EUR 120,000 stream):")
    for rate in SENSITIVITY:
        hh = haircut(parallel=rate)
        print(f"  parallel {rate:6.0f} -> haircut {hh:6.2%} -> lost {base * hh:9,.0f}")

    print("\nOpen, blocking: literal text of Reg 26-02 art. 61 from joradp.dz")
    print("(JO 58, 2026-08-12, p.28) is not yet extracted. No sale before it is.")


def _self_check() -> None:
    """Deterministic regression guard - values quoted in FCM.md."""
    assert abs(haircut() - 0.460714) < 1e-5, haircut()
    assert abs(premium() - 0.854305) < 1e-5, premium()
    assert round(loss(60_000)) == 27_643, loss(60_000)
    assert round(loss(120_000)) == 55_286, loss(120_000)
    assert round(loss(1_800_000)) == 829_286, loss(1_800_000)
    assert abs(breakeven_share(60_000) - 0.014470) < 1e-5, breakeven_share(60_000)
    assert abs(haircut(parallel=200.0) - 0.245) < 1e-9
    assert abs(haircut(parallel=320.0) - 0.528125) < 1e-9


if __name__ == "__main__":
    _self_check()
    main()
    print("\nself-check: OK")
