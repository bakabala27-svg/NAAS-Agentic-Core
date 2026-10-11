# Constitutional Amendment Record — D-317

- **Change ID:** D-317-CODESCENE-HCE-COVERAGE-SCOPE
- **Status:** PROPOSED_PENDING_INDEPENDENT_REVIEW
- **Reason:** PR #2611 changes code under `tools/hard_currency_engine/`, but `test-monolith` currently emits CodeScene's `coverage.xml` with `--cov=app` only. The PR's HCE tests pass while CodeScene reports 0.4% changed-code coverage against its unchanged 95% gate; the engine source is absent from the report, so that result does not measure the changed engine code. The HCE-specific workflow already measures this package, but its separate report is not the artifact consumed by CodeScene.
- **Scope:** One additional source argument in `.github/workflows/ci.yml`'s existing monolith test command: `--cov=tools/hard_currency_engine`, alongside the existing `--cov=app`. The existing CodeScene job summary is updated to state both measured scopes.

  The 73% monolith floor, the 70% HCE-only floor, the CodeScene 95% changed-code gate, all tests and deselections, and the job graph remain unchanged. No new coverage job or report pipeline is added.
- **Evidence and expected effect:** The focused HCE suite passes locally with 58 tests. With HCE source measured against that suite, the package reports 85% total coverage and 311/312 (99.7%) executable added lines in the changed HCE source are covered; the remaining uncovered statement is a defensive UTF-8 replacement fallback that follows a `latin1` decoder, which accepts every byte sequence. These are local focused-suite results, not a CodeScene verdict. The full monolith and the live CodeScene gate must still verify the combined report and its unchanged thresholds.
- **Affected invariants:**
  - A coverage report must measure the code whose changes it judges (D-197); omitted source must not masquerade as zero coverage.
  - The coverage floor remains a one-way ratchet: this proposal does not lower either existing floor.
  - One existing test run and one existing artifact remain the source of truth; no duplicate CI truth layer is introduced.
  - CodeScene remains outside `required-ci` as required by D-234; this proposal does not make a third-party service a merge blocker.
- **Risk:** Adding HCE source may lower the combined monolith percentage below 73%, in which case the existing test job will fail. That is a visible measurement result; the floor must not be weakened to obtain green. The CodeScene check may still fail if any changed executable lines are uncovered or its project settings differ from the reported 95% threshold.
- **Owner:** Human/admin constitutional authority
- **Independent reviewer:** Required GitHub CODEOWNER reviewer who did not author this change
- **Mitigation:** The HCE source is measured by the existing monolith run; the existing HCE-specific quality gate and its 70% floor are untouched. The summary names the measured and deliberately unmeasured scopes so a zero-coverage artifact cannot be misread as a verdict on unmeasured code.
- **Rollback:** Revert the extra `--cov=tools/hard_currency_engine` argument and the corresponding scope-summary wording. Keep this append-only record as the history of the proposal; do not alter the existing 73%, 70%, or 95% floors during rollback.
- **Verification plan:**
  - Run the HCE quality gate and the complete monolith test job on the PR head; confirm the combined line-coverage floor remains at least 73% and the HCE suite remains green.
  - Confirm the uploaded Cobertura report contains both `app/` and `tools/hard_currency_engine/` sources.
  - Confirm the live CodeScene check reports at least 95% changed-code coverage on the new PR head. Until that check completes, the CodeScene outcome is unverified.
  - Run workflow-hygiene and governance checks, plus `git diff --check`.
- **Expiration:** 2026-11-11 if independent review has not approved, rejected, or replaced this record.
- **Human/admin approval required: YES**

## Declaration

This is a proposal, not approval. The authoring agent may not self-approve or merge it without independent review.
