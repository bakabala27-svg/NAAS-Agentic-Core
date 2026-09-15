"""cbam_value.py - size the euro value at stake in A*, from verified public data.

Verified inputs (sources in research/fx-hard-currency/README.md):
  - CBAM definitive regime from 2026-01-01
  - CBAM certificate price Q2-2026 = EUR 75.28 / tCO2e (EC, 6 Jul 2026)
  - Default values per country+CN code, Reg (EU) 2025/2621 corr. 2026/1740
  - Default mark-up: +10% 2026, +20% 2027, +30% from 2028 (fertilisers exempt, +1%/yr)
  - Verification cost EUR 5k-50k per installation
  - First 2026 declaration + surrender due 2027-09-30

Assumed (declared, not verified - these are the falsifiable parts):
  - CBAM factor (share of embedded emissions actually charged) by year
  - Emission intensity gap between default value and plausible actual value
  - Algerian export tonnage to the EU by sector

Standalone: no third-party or repository imports. Run with `python3 cbam_value.py`.
"""

CERT = 75.28  # EUR / tCO2e
MARKUP = {2026: 0.10, 2027: 0.20, 2028: 0.30, 2029: 0.30, 2030: 0.30}
# CBAM factor = 1 - free allocation share. EU ETS free allowance phase-out path.
FACTOR = {2026: 0.025, 2027: 0.05, 2028: 0.10, 2029: 0.225, 2030: 0.485}

# sector: (EU-bound tonnes/yr, default intensity tCO2/t, plausible actual tCO2/t)
SECTORS = {
    "Fertilisers (urea/ammonia)": (1_800_000, 2.30, 1.65),
    "Iron & steel (DRI/EAF)": (1_200_000, 2.10, 1.05),
    "Cement (clinker/grey)": (900_000, 0.90, 0.72),
}
FERT = "Fertilisers (urea/ammonia)"


def main():
    print(f"{'sector':28}{'t/yr':>11}{'gap tCO2/t':>12}" + "".join(f"{y:>12}" for y in FACTOR))
    totals = dict.fromkeys(FACTOR, 0.0)
    for name, (tonnes, dflt, actual) in SECTORS.items():
        row = ""
        for y, price in FACTOR.items():
            markup = 0.01 * (y - 2025) if name == FERT else MARKUP[y]
            gap = dflt * (1 + markup) - actual
            value = tonnes * gap * price * CERT / 1e6  # EUR millions
            totals[y] += value
            row += f"{value:12.1f}"
        print(f"{name:28}{tonnes:11,}{dflt - actual:12.2f}{row}")
    print(
        f"{'TOTAL EUR millions/yr':28}{'':11}{'':12}"
        + "".join(f"{totals[y]:12.1f}" for y in FACTOR)
    )

    print("\nCapture test for one independent researcher:")
    for y in (2026, 2028, 2030):
        pool = totals[y] * 1e6
        for share in (0.0005, 0.002, 0.01):
            print(f"  {y}  capture {share:.2%} of saving -> EUR {pool * share:,.0f}")
        print()
    print("Reference: accredited verification costs EUR 5,000-50,000 per installation.")
    print("A* is NOT verification (EU accreditation required). A* is the monitoring")
    print("dataset the operator must hand the verifier - upstream of that fee.")


if __name__ == "__main__":
    main()
