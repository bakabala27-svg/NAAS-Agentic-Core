# Constitutional Amendment Record — D-318

- **Change ID:** D-318-EVIDENCE-PROPORTIONALITY-CONSTITUTION
- **Status:** PROPOSED_PENDING_INDEPENDENT_REVIEW
- **Reason:** The owner directed on 2026-10-11 that the thesis «الصاروخ لا يُصدَّق بمنظره: من إنتاج الكود إلى هندسة الثقة» become a project constitution that cannot be bypassed. The thesis identifies a recurring failure class: generated code, visual completeness, fluent explanations, or a green check can be mistaken for justified confidence. The governing rule is that evidence strength must be proportional to the cost of error.
- **Scope:** Add the canonical Evidence Proportionality & Trust Engineering Constitution, register it as D-318 / §0.30, expose it from all agent entry points and the documentation index, protect its law/gate/negative tests, and execute a deterministic fail-closed gate in the required `guardrails` CI path. The amendment adopts the thesis as enforceable law through the E0–E7 ladder, risk zones, L1–L12, NF-1–NF-5, independence and HOLD rules; it does not claim that a textual gate proves production correctness.
- **Affected invariants:**
  - Evidence strength is proportional to severity, irreversibility, blast radius, and detection delay.
  - A file, diff, trace, passing test, representative runtime, production measurement, and user value are distinct claims (E0–E7).
  - The change generator cannot be the sole judge of its own success or weaken its evaluator.
  - Unknown external side effects must be reconciled before retry; irreversible agent actions require deterministic policy and explicit approval.
  - The constitution, its enforcer, and its negative tests remain protected and changes remain subject to independent review.
  - Existing constitutions remain in force; D-318 is additive and cannot weaken an existing gate.
- **Risk:** A broad governance rule can become ceremonial or impose verification cost disproportionate to low-risk experiments. The law therefore declares three risk zones, makes controls falsifiable, requires thresholds before results, and states that controls proven not to reduce risk should be reviewed through the amendment process. Static checks can prove wiring and contract shape only, not runtime correctness.
- **Owner:** Human/admin constitutional authority
- **Independent reviewer:** Required GitHub CODEOWNER reviewer who did not author this change
- **Mitigation:** The gate checks the frozen SHA-256 and byte count before canonical markers, complete E0–E7/L1–L12/NF-1–NF-5 sets, registry and entrypoint links, CI wiring, and protected-artifact coverage. Negative tests prove that changing one byte, deleting E4 or L6, removing protection, omitting the registry enforcer, or disconnecting CI fails. The law states its external-admin limitation explicitly.
- **Rollback:** Revert the D-318 implementation files and references as one reviewed change while retaining this append-only amendment record as history. Rollback must not weaken any pre-existing constitution, test, CI requirement, or protected-branch setting.
- **Verification plan:** Run `python scripts/fitness/check_evidence_proportionality_constitution.py`; run `python -m pytest -q tests/fitness/test_evidence_proportionality_constitution_gate.py`; run governance, engineering-governance, documentation-contract, constitution-reality, and code-acceptance gates; run `git diff --check`; inspect that the CI invocation remains under `guardrails` with `set -euo pipefail`; obtain independent human/CODEOWNER review before approval or merge.
- **Expiration:** 2026-11-11 if independent review has not approved, rejected, or replaced this proposal.
- **Human/admin approval required: YES**

## Declaration

This record is a proposal, not self-approval. The authoring agent cannot approve or merge the constitutional amendment. The repository can make normal-path bypass detectable and rejectable; only external platform controls and human/admin authority can govern changes outside that path.
