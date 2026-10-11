# Constitutional Amendment Record — D-317

- **Change ID:** D-317-CODESCENE-HCE-COVERAGE-SCOPE
- **Status:** PROPOSED_PENDING_INDEPENDENT_REVIEW
- **Reason:** PR #2611 changes code under `tools/hard_currency_engine/`. The original monolith report measured `app/` only. Adding HCE to that scope did not resolve the live gate: CI run `38150400694` completed, but CodeScene reported 0.4% changed-code coverage against its unchanged 95% gate and listed the changed HCE files as uncovered (including all of `csv_safety.py`). The focused HCE suite passes locally at 85.40% package coverage. The mismatch means the combined report still is not being interpreted as expected; path layout is a candidate cause, not yet a proven root cause.
- **Scope:** Keep the existing monolith test run and artifact, but generate Cobertura from one repository-root source using `coverage.codescene.ini`. Its report filter remains limited to `app/` and `tools/hard_currency_engine/`, and the CI command uses the configured source instead of separate `--cov` roots. The CodeScene PR summary will name both measured scopes and the repository-relative path layout.

  The 73% monolith floor, the 70% HCE-only floor, the CodeScene 95% changed-code gate, all tests and deselections, and the job graph remain unchanged. No new coverage job or lower threshold is added.
- **Evidence and expected effect:** The focused HCE suite passes locally with 61 tests and 85.40% package coverage. The focused suite also produces a Cobertura report whose filenames retain repository paths such as `tools/hard_currency_engine/csv_safety.py`; the recorded per-file local rates include 98.89% for `csv_safety.py`, 96.68% for `france_validator.py`, 97.04% for `belgium_validator.py`, and 83.33% for `cli.py`. A prior local diff-specific estimate was 311/312 (99.7%) executable added HCE lines covered, but it did not predict the remote CodeScene result. These are local focused-suite results, not a CodeScene verdict. The full monolith and live CodeScene gate must still verify the combined report and unchanged thresholds.
- **Affected invariants:**
  - A coverage report must measure the code whose changes it judges (D-197); omitted source must not masquerade as zero coverage.
  - The coverage floor remains a one-way ratchet: this proposal does not lower either existing floor.
  - One existing test run and one existing artifact remain the source of truth; no duplicate coverage job or report pipeline is introduced.
  - CodeScene remains outside `required-ci` as required by D-234; this proposal does not make a third-party service a merge blocker.
- **Risk:** The root-source configuration must preserve the existing `app/` denominator while adding HCE, and the unchanged combined monolith floor must remain at least 73%. CI will test that rather than weakening the floor. The external CodeScene check may still fail if the report mapping hypothesis is wrong, changed executable lines remain uncovered, or project settings differ from the reported 95% threshold.
- **Owner:** Human/admin constitutional authority
- **Independent reviewer:** Required GitHub CODEOWNER reviewer who did not author this change
- **Mitigation:** Both source scopes are explicitly filtered in the coverage configuration; the monolith still runs once and produces one artifact; the existing HCE-specific quality gate and its 70% floor are untouched. The CodeScene check remains separate and its result is reported without being represented as a merge gate.
- **Rollback:** Revert `coverage.codescene.ini`, restore the original monolith `--cov=app` and `--cov=tools/hard_currency_engine` arguments, and remove the corresponding PR-scope wording. Keep this append-only record as the history of the proposal; do not alter the existing 73%, 70%, or 95% floors during rollback.
- **Verification plan:**
  - Run the HCE quality gate and complete monolith job on the PR head; confirm the combined line-coverage floor remains at least 73% and the HCE suite remains green.
  - Confirm Cobertura uses a repository-root source and its filenames include both `app/` and `tools/hard_currency_engine/` paths with measured hits in changed HCE files.
  - Confirm the live CodeScene check reports at least 95% changed-code coverage on the new PR head. Until that check completes, the CodeScene outcome is unverified.
  - Run workflow-hygiene and governance checks, plus `git diff --check`.
- **Expiration:** 2026-11-11 if independent review has not approved, rejected, or replaced this record.
- **Human/admin approval required: YES**

## Declaration

This is a proposal, not approval. The authoring agent may not self-approve or merge it without independent review.
