# Constitutional Amendment Record — D-321

- **Change ID:** D-321-DEMAND-FIRST-LAW
- **Status:** PROPOSED_PENDING_INDEPENDENT_REVIEW
- **Reason:** On 2026-10-20 the owner wrote: «دائما أكبر خطر كارثي هو بناء منتج بلا سوق — يجب أن يصبح اهم قانون هو التاكد من أن هناك من يتألم و يبحث عن الحل بشغف و يوجد من يدفع». The repository shows the risk is real:
  - 10 of 25 value-chain paths declared build links (probe, test, result on a third-party system) with no entity replying in the ledger;
  - the active thesis (D-300) was chosen by its legal deadline, tool and delivery cost, and D-300 itself lists «صفر محادثة مع مشترٍ» as a weakness;
  - the ledger holds 5 entities contacted, 0 quotes and 0 payments.

  The owner chose the two-stage evidence bar («مرحلتان») and paused FR e-invoicing outreach until the pain-research report returns («جمّدها حتى نتائج البحث»).
- **Scope:**
  - Add `docs/architecture/DEMAND_FIRST_CONSTITUTION.md` (CLAUDE.md §0.32), byte-pinned in `docs/governance/D321_IMMUTABLE_TEXT.json`.
  - Add one top line to CLAUDE.md before the D-300 line, so the law is read before any section. Three blank lines that sat after a `---` rule and before a heading are removed, so the 1262-line cap is not raised and no rule text is deleted.
  - `shared/research/value_chain.py`:
    - adds `DEMAND_LEGS`, `CODE_LINKS` and the frozen debt `BUILT_BEFORE_DEMAND` (10 paths);
    - `_demand_state` adds `demand_legs`, `replying_entities`, `code_licensed` and `built_before_demand` to the derived block;
    - `_demand_declaration_problems` and `_built_before_demand_problems` turn CI red for a build link declared before demand, a debt that does not shrink, or a demand leg without dated sourced evidence.
  - `scripts/fitness/check_value_chain.py` threads the frozen debt through `run`.
  - `scripts/fitness/check_code_acceptance.py` adds `validate_demand_first` and `current_added_paths`. Product code is accepted only with `change_class` `DEMAND_LICENSED` (a named path with `code_licensed: true`) or `MAINTENANCE_KEEP_CI_HONEST` (a reason, and no added product file).
  - `docs/governance/ENGINEERING_GOVERNANCE_POLICY.json`:
    - adds a `demand_first` section with `product_code_prefixes`, `non_product_prefixes` and `change_classes`;
    - makes the law, pin, gate and test protected paths.
  - New gate `scripts/fitness/check_demand_first_constitution.py`, wired in `guardrails`, with its negative tests `tests/fitness/test_demand_first_constitution_gate.py` and a `NEGATIVE_PROOFS.json` row.
  - A `CONSTITUTION_REGISTRY.json` row (§0.32), and entrypoints in AGENTS.md and ENGINEERING_CONSTITUTION.md §1.4.
  - `tests/fitness/test_check_value_chain.py` gains 8 tests, and its fixture helper re-derives with a fixture debt (`_FIXTURE_DEBT`). The fixture path declares build links without demand, which the law now makes red, so the fixture carries the same frozen debt as the ten real paths. `tests/fitness/test_code_acceptance_gate.py` gains 7 tests and `tests/shared/test_value_chain.py` gains 1.
- **Affected invariants:**
  - The three legs (pain, active search, payer) use the chain's own statuses `REACHED` and `NOT_REACHED`. No new ladder or status vocabulary is added (D-319).
  - Public evidence licenses only a buyer test. Build links 3–5 and product code need three replying entities in the ledger and an evidenced payer.
  - What was built before demand is shown, never deleted; its debt only shrinks, in both directions.
  - The law never writes PIVOT or STOP; the owner decides. D-300 is paused, not revoked. Between this law and an existing rule, the stricter wins. Every existing constitution stays in force.
- **Risk:**
  - The machine checks that sources are dated and ledger rows exist. It cannot check that a pain is real, or the "passion" the owner named; those stay human judgements and the law says so.
  - `shared/` is product code except `shared/research/` and `shared/evidence/`. That exemption is the law's own evidence machinery, and it is named in the policy with its reason.
  - The decision brief (`economic_decision`) does not yet read the FR e-invoicing pause.
- **Owner:** Human/admin constitutional authority
- **Independent reviewer:** Required GitHub CODEOWNER reviewer who did not author this change. The only CODEOWNER is @HOUSSAM16ai. If the owner is also the reviewer, review is not independent, and the PR says so.
- **Mitigation:**
  - Red first: before the implementation, 34 tests failed and the D-321 gate module did not exist. The output is kept for the PR.
  - Each new negative test breaks one guarantee on purpose: a build link after the law; a frozen path raising its link; a debt entry for a missing path or above the declared link; a licensed path left in the debt; two replying entities instead of three; a leg without dated sourced evidence or price; a leg not reached without a reason; product code with no change class; maintenance adding a file or with no reason; an unlicensed path named as licensing; a one-byte change of the law; a missing marker; a removed enforcing symbol; the law not first in CLAUDE.md; an unregistered constitution; a commented CI line; an unprotected artifact.
- **Rollback:** Revert the D-321 commits as one reviewed change, keeping this append-only record as history. Rollback must not weaken any pre-existing constitution, test, CI requirement or protected-branch setting.
- **Verification plan:**
  - Run `python scripts/fitness/check_demand_first_constitution.py`, `python scripts/fitness/check_value_chain.py`, `python scripts/research/value_chain.py --check` and `CODE_ACCEPTANCE_BASE_SHA=origin/main python scripts/fitness/check_code_acceptance.py`.
  - Run `pytest tests/fitness/test_demand_first_constitution_gate.py tests/fitness/test_check_value_chain.py tests/fitness/test_code_acceptance_gate.py tests/shared/test_value_chain.py`.
  - Run the engineering-governance, governance-registry, memory-coherence, documentation-contract and repository-microscope gates against `origin/main`.
  - Obtain independent human/CODEOWNER review before approval or merge.
- **Expiration:** 2026-11-20 if independent review has not approved, rejected, or replaced this proposal.
- **Human/admin approval required: YES**

## Declaration

This record is a proposal. The authoring agent cannot approve or merge the constitutional amendment. The repository can make normal-path bypass detectable and rejectable; only external platform controls and human/admin authority can govern changes outside that path.
