# `docs/evidence/`

Visual evidence attached to pull requests, committed so a reviewer can see it
from the diff and so the link in a PR body does not rot.

D-270 L1 asks for the command and its output; `validate_pr_description.py`
additionally requires a screenshot on any change that touches `frontend/`,
because what a student sees should be visible in review. Files here are that
screenshot — captured from a real run, never a mock-up, and named for the change
they belong to.

| file | what it shows |
|---|---|
| `react19-frontend-2026-08-24.png` | the login screen served by `next start` after the React 18.3.1 → 19.2.8 / Next 16.3.0 → 16.3.1 / katex 0.16 → 0.18 uplift (#2291, #2292): Arabic RTL layout, theme tokens and form controls all intact. |
| `d305-hard-currency-frontier-2026-10-01.png` | the admin-only Hard-Currency Center (D-305) on the built bundle, logged in as the owner: the frontier map with the real funnel on top (1 contact · 0 replies · 0 settled payments · `GATE_C = ABSENT`), the five derived classifications for the 25 paths, and one path's eight-link chain with its next link and actor. |
| `d305-hard-currency-cbam-2026-10-01.png` | the CBAM decision tool on pinned code `2523100090`: Algerian default values, path toll, crossover threshold, the 73-of-90 banner, a plant figure of 0.6 tCO₂e/t giving 2026 as the first cheaper year, and the threshold-by-year chart with its hover tooltip. |
| `d305-hard-currency-einvoicing-2026-10-01.png` | the FR e-invoicing workbench after uploading `docs/commercial/outreach/demo/DEMO_20_FICHES.csv`: summary tiles equal to `audit_french_csv`, the anomaly table and the two downloads; the file is not stored. |
| `d305-student-menu-no-center-2026-10-01.png` | the same build logged in as a student: the header menu has no Hard-Currency Center entry. |
| `d306-decision-chamber-2026-10-02.png` | the Decision Chamber (D-306), the first tab of the admin-only center on the built bundle: the nine lines (one active thesis · highest truthful claim, link 4 of 8 · first missing proof, link 5 · why code cannot produce it · the next human act, a follow-up call to the one firm emailed · the evidence it may produce · kill condition K1 at 1/30, not yet evaluable · the most tempting forbidden shortcut · 10 days since the last ledger event). |
| `d306-decision-chamber-dark-2026-10-02.png` | the same chamber in the dark theme, from the theme button in the header. |
| `d306-outcome-preview-refused-2026-10-02.png` | the "record a confirmed outcome" door: a proposed `PAYMENT_SETTLED` row for Balagué with no earlier `QUOTE_SENT` is refused with its reason, and nothing is written (the owner commits ledger rows through git). |
