# Constitutional Amendment Record — D-319B

- **Change ID:** D-319B-FOUNDER-ATLAS-VERBATIM-TEXTS
- **Status:** PROPOSED_PENDING_INDEPENDENT_REVIEW
- **Reason:** Record D-319 left the verbatim transcriptions of the owner's two documents dated 2026-10-11 out of the constitution until the owner confirmed them, and said they need a new amendment record. On 2026-10-20 the owner confirmed both transcriptions as they are («مؤكَّد كما هو»), including the 8 doubt items sent on 2026-10-19, and asked for them in the same pull request (#2633).
- **Scope:**
  - Add `docs/architecture/FOUNDER_ATLAS_VERBATIM.md` («أطلس المؤسس العظيم», 40 pages, 87,007 bytes) and `docs/architecture/EVIDENCE_PROPORTIONALITY_VERBATIM.md` («الصاروخ لا يُصدَّق بمنظره», 22 pages, 76,179 bytes), byte-identical to the files the owner confirmed.
  - `docs/governance/D319_IMMUTABLE_TEXT.json`: a `verbatim_texts` list with each file's sha256 and byte count, and the source PDF's sha256, size, page count, title and date; `verbatim_texts_status` becomes `CONFIRMED_BY_OWNER`. The PDFs themselves are not committed.
  - `docs/architecture/FOUNDER_ATLAS_CONSTITUTION.md` §2 is reworded from pending to confirmed, so its own pin is re-hashed.
  - `scripts/fitness/check_founder_atlas_constitution.py` gains `check_verbatim_pins`, and the two texts join the artifacts it requires to be protected; `tests/fitness/test_founder_atlas_constitution_gate.py` gains 8 negative tests, written red first.
  - `docs/governance/ENGINEERING_GOVERNANCE_POLICY.json`: the two texts become protected paths.
  - CLAUDE.md §0.31, `docs/DOCUMENTATION_INDEX.md`, `docs/DOCUMENTATION_MANIFEST.json` and `.memory/decisions.md` stop saying the texts are pending.
- **Affected invariants:**
  - The owner's verbatim text wins over every summary, D-318 and CLAUDE.md included; between the Atlas and an existing rule, the stricter wins.
  - One byte changed in the law or in either verbatim text turns CI red.
  - The only intended difference from the PDFs is the by-line, replaced by «وثيقة المالك المؤرخة في 2026-10-11» so no personal name enters the public repository (D-318 precedent). The gate rejects the by-line's shape without naming anyone.
  - D-319 and every existing constitution stay in force; this record only adds the texts.
- **Risk:** The pin freezes whatever text it is given. Each page was compared by machine with the PDF's text layer, but no independent second reader checked the text against the page images; the owner's confirmation is the only human check. A transcription error found later needs its own amendment record.
- **Owner:** Human/admin constitutional authority
- **Independent reviewer:** Required GitHub CODEOWNER reviewer who did not author this change. The only CODEOWNER is @HOUSSAM16ai; if the owner is also the reviewer, review is not independent and the PR says so.
- **Mitigation:** The new tests break each guarantee on purpose: a one-byte change, a missing text, a dropped pin, a status still pending, an invalid PDF hash, a by-line, and an unprotected text. The red run before `check_verbatim_pins` existed is kept for the PR (8 failed, 10 passed). `sha256sum` of each committed text equals the hash of the file the owner confirmed.
- **Rollback:** Revert the D-319B commit as one reviewed change while keeping this append-only record as history. Rollback restores D-319's pending state and must not weaken any pre-existing constitution, test, CI requirement or protected-branch setting.
- **Verification plan:** Run `python scripts/fitness/check_founder_atlas_constitution.py`; run `pytest tests/fitness/test_founder_atlas_constitution_gate.py`; run `sha256sum docs/architecture/FOUNDER_ATLAS_VERBATIM.md docs/architecture/EVIDENCE_PROPORTIONALITY_VERBATIM.md` and compare with the pin; run the engineering-governance, documentation-contract, code-acceptance and repository-microscope gates against `origin/main`; obtain independent human/CODEOWNER review before approval or merge.
- **Expiration:** 2026-11-20 if independent review has not approved, rejected, or replaced this proposal.
- **Human/admin approval required: YES**

## Declaration

This record is a proposal. The authoring agent cannot approve or merge the constitutional amendment. The repository can make normal-path bypass detectable and rejectable; only external platform controls and human/admin authority can govern changes outside that path.
