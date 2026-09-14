# -*- coding: utf-8 -*-
"""
Repatriation Slack Model (RSM v0.1)

Algeria Reglement 26-02 (23 Jul 2026, JO 58 of 12 Aug 2026)
  x SaaS / merchant-of-record settlement rails.

Regulatory clock
----------------
  D0            = date of service completion
  Legal ceiling = 120 calendar days
  Extension     = 180 days, only with PRIOR export-credit insurance covering a
                  contractual payment term exceeding 120 days

Settlement clock
----------------
  D0 -> client pays (contractual payment terms)
     -> intermediary / merchant-of-record hold
     -> wait for the next periodic payout batch
     -> banking transit (SWIFT + correspondent)
     -> credit to the Algerian FX account = repatriation event

  slack = 120 - total elapsed days
  slack < 0  =>  structural breach, independent of exporter diligence

Run
---
  python3 model.py

No third-party dependencies. Writes rows.json next to this file.
See CLAIMS.md for the claim-scope ledger and SOURCES.md for provenance.
"""

import json
import os

CEILING_STD = 120
CEILING_EXT = 180


def batch_wait(cadence_days: int) -> int:
    """Worst-case extra wait to reach a periodic payout batch after the hold ends.

    A semi-monthly batch (cadence 15) can add up to 14 days; a daily or rolling
    payout adds nothing.
    """
    return 0 if cadence_days <= 1 else cadence_days - 1


RAILS = [
    dict(id="R1", name="SWIFT wire, net-30",
         terms=30, hold=0, cadence=1, transit=7,
         note="Direct resident invoice. The only rail with no third-party custody."),
    dict(id="R2", name="SWIFT wire, net-60",
         terms=60, hold=0, cadence=1, transit=7,
         note="Common enterprise procurement term in the EU and the Gulf."),
    dict(id="R3", name="SWIFT wire, net-90",
         terms=90, hold=0, cadence=1, transit=10,
         note="Large-account term. Exposed to correspondent compliance holds."),
    dict(id="R4", name="MoR semi-monthly (Lemon Squeezy pattern)",
         terms=0, hold=13, cadence=15, transit=5,
         note="13-day hold, payouts twice monthly, 1-5 days to bank."),
    dict(id="R5", name="MoR monthly net-30 (Paddle pattern)",
         terms=0, hold=30, cadence=30, transit=5,
         note="Monthly settlement cycle on prior-month net revenue."),
    dict(id="R6", name="PSP rolling payout",
         terms=0, hold=2, cadence=1, transit=5,
         note="Requires a PSP-supported entity; Algeria is not a supported jurisdiction."),
]

RESERVES = [
    dict(id="RS0", name="no reserve", pct=0.00, window=0),
    dict(id="RS1", name="25% / 30-day rolling", pct=0.25, window=30),
    dict(id="RS2", name="25% / 90-day rolling", pct=0.25, window=90),
    dict(id="RS3", name="10% / 180-day rolling", pct=0.10, window=180),
]

# Two admissible readings of D0 for a 12-month prepaid subscription.
INTERPRETATIONS = [
    dict(id="I-A", name="D0 = invoice / access granted (day 0)", offset=0),
    dict(id="I-B", name="D0 = end of subscription period (day 365)", offset=365),
]


def elapsed(rail: dict, reserve_window: int = 0) -> int:
    """Calendar days from D0 until the funds are credited in hard currency."""
    hold = max(rail["hold"], reserve_window)
    return rail["terms"] + hold + batch_wait(rail["cadence"]) + rail["transit"]


def verdict(slack) -> str:
    if slack is None:
        return "-"
    if slack < 0:
        return "BREACH"
    if slack <= 15:
        return "FRAGILE"
    if slack <= 45:
        return "TIGHT"
    return "SAFE"


def build_rows() -> list:
    rows = []
    for rail in RAILS:
        for rs in RESERVES:
            main_days = elapsed(rail, 0)
            res_days = elapsed(rail, rs["window"]) if rs["pct"] > 0 else None
            rows.append(dict(
                rail_id=rail["id"],
                rail=rail["name"],
                reserve_id=rs["id"],
                reserve=rs["name"],
                reserve_pct=rs["pct"],
                days_main=main_days,
                slack_main=CEILING_STD - main_days,
                days_reserved=res_days,
                slack_reserved=(CEILING_STD - res_days) if res_days is not None else None,
            ))
    return rows


def exposed_share(row: dict) -> float:
    """Fraction of annual revenue sitting in structural breach."""
    if row["reserve_pct"] == 0:
        return 1.0 if row["slack_main"] < 0 else 0.0
    return (
        (1 - row["reserve_pct"]) * (1 if row["slack_main"] < 0 else 0)
        + row["reserve_pct"] * (1 if row["slack_reserved"] < 0 else 0)
    )


def main() -> None:
    rows = build_rows()
    line = "=" * 104

    print(line)
    print("RSM v0.1 | ceiling = %d days | reading I-A (D0 = day 0)" % CEILING_STD)
    print(line)
    print(f"{'rail':<40}{'reserve':<24}{'main d':>8}{'slack':>8}{'res d':>8}{'slack':>8}{'verdict':>10}")
    print("-" * 104)
    for r in rows:
        v_main = verdict(r["slack_main"])
        v_res = verdict(r["slack_reserved"])
        worst = v_res if (r["slack_reserved"] is not None
                          and r["slack_reserved"] < r["slack_main"]) else v_main
        print(f"{r['rail']:<40}{r['reserve']:<24}{r['days_main']:>8}{r['slack_main']:>8}"
              f"{(r['days_reserved'] if r['days_reserved'] is not None else '-'):>8}"
              f"{(r['slack_reserved'] if r['slack_reserved'] is not None else '-'):>8}{worst:>10}")

    print()
    print(line)
    print("EXPOSURE: share of ARR that is structurally late")
    print(line)
    for r in rows:
        share = exposed_share(r)
        if share > 0:
            print(f"  {r['rail']:<40}{r['reserve']:<24}{share * 100:>6.1f}% of revenue late")

    print()
    print(line)
    print("PENALTY SIZING (illustrative; see CLAIMS.md item J-04)")
    print(line)
    for arr in (120_000, 500_000, 1_800_000):
        at_risk = arr * 0.10
        print(f"  ARR ${arr:>9,} | 10%/180d reserve on an MoR rail -> ${at_risk:>9,.0f} exposed; "
              f"statutory exposure ${at_risk:>9,.0f} (1x) to ${at_risk * 2:>10,.0f} (2x)")

    print()
    print(line)
    print("INTERPRETATION RISK: 12-month prepaid contract on the MoR semi-monthly rail")
    print(line)
    rail = RAILS[3]
    cash_day = elapsed(rail, 0)
    for itp in INTERPRETATIONS:
        deadline = itp["offset"] + CEILING_STD
        slack = deadline - cash_day
        print(f"  {itp['name']:<46} cash in at day {cash_day:>4} | deadline day {deadline:>4} "
              f"| slack {slack:>5} d -> {verdict(slack)}")

    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rows.json")
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(rows, fh, indent=1, ensure_ascii=False)
    print(f"\nwrote {out_path}")


if __name__ == "__main__":
    main()
