"""Deterministic economics for the three finalists. Every input is either a dated public
figure (source key) or an explicit assumption (ASSUMPTION). No forecast: only arithmetic."""

import json

EUR_DZD = 151.1803  # Banque d'Algérie interbank, 2026-10-21 (Maghreb Emergent)
ANAE_CAP_DZD = 5_000_000  # auto-entrepreneur annual ceiling (secondary source, D-323)
HOURS_PER_MONTH = 160  # ASSUMPTION
SALARIES_DZD = {"low": 80_000, "mid": 120_000, "high": 160_000}  # ASSUMPTION per month
TEAM = 3  # ASSUMPTION: three people
OVERHEAD_DZD = 50_000  # ASSUMPTION: tools, internet, workspace per month


def eur(dzd):
    return round(dzd / EUR_DZD, 2)


out = {"eur_dzd": EUR_DZD, "anae_cap_eur": eur(ANAE_CAP_DZD)}
out["hourly_cost_eur"] = {k: eur(v / HOURS_PER_MONTH) for k, v in SALARIES_DZD.items()}
fixed = TEAM * SALARIES_DZD["mid"] + OVERHEAD_DZD
out["team_fixed_month_eur_mid"] = eur(fixed)

# F1 — e-invoicing identifier cleansing. Price: owner's decision 2026-09-30 (290 EUR HT up to 200 records).
price_f1 = 290
minutes_per_record = {"fast": 1, "slow": 3}  # ASSUMPTION
f1 = {}
for speed, m in minutes_per_record.items():
    hours = 200 * m / 60
    for band, h_eur in out["hourly_cost_eur"].items():
        cost = round(hours * h_eur, 2)
        f1[f"{speed}/{band}"] = {
            "hours": round(hours, 1),
            "labour_eur": cost,
            "gross_margin_pct": round(100 * (price_f1 - cost) / price_f1, 1),
        }
out["f1_unit"] = f1
var_mid = round((200 * 2 / 60) * out["hourly_cost_eur"]["mid"], 2)  # 2 min/record, mid salary
out["f1_breakeven_jobs_per_month"] = round(
    out["team_fixed_month_eur_mid"] / (price_f1 - var_mid), 1
)
PME, ETI = 172_600, 7_200  # INSEE 2022 (IA101)
out["f1_fr_pme_addressable_eur"] = {f"{a}%": round(PME * a / 100 * price_f1) for a in (1, 3, 5)}
out["f1_fr_eti_count"] = ETI
out["f1_jobs_to_hit_anae_cap"] = round(out["anae_cap_eur"] / price_f1)

# F2 — Arabic AI guard testing. Published bands: AU$15k–80k (aona.ai), US$25k–150k (ud.hk).
weeks, people = 3, 3  # ASSUMPTION engagement shape
f2_cost = eur(people * SALARIES_DZD["mid"] * weeks / 4.33)
out["f2_engagement_cost_eur_mid"] = f2_cost

# F3 — accessibility (RGAA) audit. Published bands: 1,500–8,000 EUR HT; e-commerce ~5,000 (25 pages).
# Published bands 1,500 / 5,000 / 8,000 EUR HT are quoted for context; no figure below depends on them.
audit_days, auditors = 8, 1  # ASSUMPTION: ~1.5 weeks one auditor
f3_cost = eur(auditors * SALARIES_DZD["mid"] * audit_days / 21.7)
out["f3_audit_cost_eur_mid"] = f3_cost
out["f3_margin_pct"] = {p: round(100 * (p - f3_cost) / p, 1) for p in (1500, 5000, 8000)}
out["f3_audits_to_cover_team_month"] = {
    p: round(out["team_fixed_month_eur_mid"] / (p - f3_cost), 2) for p in (1500, 5000)
}
print(json.dumps(out, indent=1, ensure_ascii=False))
