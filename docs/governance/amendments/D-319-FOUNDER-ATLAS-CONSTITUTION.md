# Constitutional Amendment Record — D-319

- **Change ID:** D-319-FOUNDER-ATLAS-CONSTITUTION
- **Status:** PROPOSED_PENDING_INDEPENDENT_REVIEW
- **Reason:** On 2026-10-15 the owner ordered that two documents dated 2026-10-11 — «أطلس المؤسس العظيم» (40 pages, law «لا سحر بلا دليل») and «الصاروخ لا يُصدَّق بمنظره» (22 pages) — become strict law that cannot be bypassed. An audit of D-318 against the Rocket PDF found that D-318 is a condensed rewrite with escape hatches the owner's text does not have, that the thesis's `gate.py` existed nowhere as code, and that the D-318 CI-wiring check read to the end of `ci.yml`, so a commented-out line counted as wiring.
- **Scope:**
  - Add `docs/architecture/FOUNDER_ATLAS_CONSTITUTION.md` (D-319 / §0.31), byte-pinned by `docs/governance/D319_IMMUTABLE_TEXT.json`, its gate `scripts/fitness/check_founder_atlas_constitution.py` (wired in `guardrails`), its negative tests, a registry row, a `NEGATIVE_PROOFS.json` row, and entrypoints in CLAUDE.md, AGENTS.md and ENGINEERING_CONSTITUTION.md §1.3.
  - Void the D-318 escape hatches by precedence, quoting each verbatim; D-318's frozen bytes are not edited.
  - Tighten the D-318 gate's CI-wiring check to the `guardrails` job, ignoring comments.
  - Enforce the machine-checkable Atlas rules in their existing homes. These protected paths change:
    - `scripts/fitness/check_code_acceptance.py`: `evidence_report` computed by `shared/evidence/gate.py`, no self-declared PASS, runtime evidence paths exist.
    - `scripts/fitness/check_engineering_governance.py` and `docs/governance/ENGINEERING_GOVERNANCE_POLICY.json`: pre-modification fields gain `non_goals`, `acceptance_criteria`, `target_operating_cost`; the D-319 artifacts become protected.
    - `scripts/fitness/check_hard_currency_engine.py`: no mail-sending import in the engine.
    - `scripts/fitness/check_evidence_proportionality_constitution.py`: job-confined wiring.
    - Tests under `tests/fitness/` for each of the above, written red first.
  - The verbatim transcriptions of both documents and the PDF hashes are **not** part of this amendment: the owner has not confirmed them. They require a new amendment record.
- **Affected invariants:**
  - The owner's verbatim text wins over every summary; between the Atlas and an existing rule, the stricter wins.
  - CI blocks what we write (catalog, buyer text, acceptance packet, our claims); the ledger records what happened and a true record is never rejected.
  - The evidence level and decision are computed by deterministic code; a change that touches verifier files computes `HOLD`.
  - No new ladder, gate ledger status or status vocabulary (D-314): Atlas gates A–H are a derived view with `ATLAS_*` tokens.
  - The code never says PIVOT or STOP; a fired kill condition hands the decision to the owner.
  - Existing constitutions remain in force; D-319 is additive and only tightens.
- **Risk:** A rule that names a symbol can drift from what the symbol does; the gate proves that each named home exists, not that it is correct — the negative tests of each home carry that. Stricter acceptance checks can turn a legitimate packet red until it is completed. Voiding D-318 hatches by reference rather than by editing D-318 leaves two texts to read; the precedence rule and this record make the reading explicit.
- **Owner:** Human/admin constitutional authority
- **Independent reviewer:** Required GitHub CODEOWNER reviewer who did not author this change. The only CODEOWNER is @HOUSSAM16ai; if the owner is also the reviewer, review is not independent and the PR says so.
- **Mitigation:** Every new rule was written as a failing test before its implementation, and the red outputs are kept for the PR. The D-319 gate checks the byte pin, markers, each quoted D-318 hatch (present verbatim in D-318 and carrying a written verdict), each `file::symbol` home, the registry row, the entrypoints, job-confined CI wiring and protected-path coverage; its negative tests break each one.
- **Rollback:** Revert the D-319 commits as one reviewed change while keeping this append-only record as history. Rollback must not weaken any pre-existing constitution, test, CI requirement or protected-branch setting.
- **Verification plan:** Run `python scripts/fitness/check_founder_atlas_constitution.py` and `python scripts/fitness/check_evidence_proportionality_constitution.py`; run `pytest tests/fitness/test_founder_atlas_constitution_gate.py tests/fitness/test_evidence_proportionality_constitution_gate.py tests/fitness/test_code_acceptance_gate.py tests/fitness/test_check_value_chain.py tests/fitness/test_check_hard_currency_engine.py tests/shared tests/unit/tools`; run the engineering-governance, governance-registry, gate-negative-proof, value-chain, code-acceptance and repository-microscope gates against `origin/main`; confirm the packet's `evidence_report` computes `HOLD`; obtain independent human/CODEOWNER review before approval or merge.
- **Expiration:** 2026-11-20 if independent review has not approved, rejected, or replaced this proposal.
- **Human/admin approval required: YES**

## Declaration

This record is a proposal. The authoring agent cannot approve or merge the constitutional amendment. The repository can make normal-path bypass detectable and rejectable; only external platform controls and human/admin authority can govern changes outside that path.
