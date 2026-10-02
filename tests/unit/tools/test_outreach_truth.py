"""D-304 — what the owner sends to a buyer is checked like code.

The wedge's first buyer reads these files word for word, under the owner's name.
Three defects were found in them before any of them had a reply:

- C12: a research file gave Balagué a valid French VAT number that belongs to
  another company (SIREN 791 349 749 instead of 501 058 812).
- C7/C8: sales sentences stated measured trends ("ont fortement augmenté", "une
  part significative des échecs") and guarantees ("garantir un routage sans
  échec"). The error rate in real files has never been measured
  (``OFFER_CATALOG.json`` — ``claims_forbidden_ar``).
- C5: three different package prices in three files (150–300 €, 290 €,
  290–390 €). The owner chose one on 2026-09-30: 290 € HT up to 200 records.

The email already sent to Balagué on 2026-09-22 is kept verbatim as the record;
a warning next to it says not to reuse its unmeasured phrase.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# The rules live in one home since D-306; the Decision Chamber asks the same questions
# of any sentence the owner types.
from tools.hard_currency_engine.buyer_claims import (
    EURO_RANGE,
    PACKAGE_PRICE,
    buyer_lines,
    findings,
    identifier_mismatches,
)

OUTREACH = REPO_ROOT / "docs/commercial/outreach"
KIT = OUTREACH / "BALAGUE_FIRST_CLIENT_KIT_2026-09-22.md"
MALT = OUTREACH / "ready_to_send/03_PROFIL_MALT.md"
CATALOG = REPO_ROOT / "docs/commercial/OFFER_CATALOG.json"
WEDGE_ID = "fr-be-einvoicing-referential-cleansing"

#: The files the owner copies into an email, a call or a profile for the active wedge.
#: ``04_SCRIPTS_EXPANSION_GLOBAL.md`` is not listed: its corridors 3→9 are frozen
#: (D-300) and its header says so.
SEND_FILES = (
    OUTREACH / "ready_to_send/00_PLAN_ENVOI.md",
    OUTREACH / "ready_to_send/01_MAILS_CABINETS_PRETS.md",
    OUTREACH / "ready_to_send/02_PARTENARIATS_PDP.md",
    MALT,
    KIT,
)

#: Verdicts that block a line from being sent. HYPOTHESIS_ONLY is not here: the email
#: already sent to Balagué on 2026-09-22 stays verbatim as the record (D-304), and the
#: rewording of trends is a human review.
_BLOCKING = frozenset({"FORBIDDEN", "UNSUPPORTED"})


def test_the_c12_line_is_caught() -> None:
    """The negative proof: the wrong line from the research file fails the rule."""
    line = "Balagué — **SIREN 501 058 812** (RCS Toulouse 501 058 812) · TVA FR 61 791 349 749"
    assert identifier_mismatches(line) == [
        "FR61791349749 carries SIREN 791349749, the line names ['501058812']"
    ]
    assert identifier_mismatches("SIREN 501 058 812 · TVA FR40501058812") == []


def test_every_outreach_vat_number_matches_its_siren() -> None:
    problems = [
        f"{path.relative_to(REPO_ROOT)}:{number}: {problem}"
        for path in sorted(OUTREACH.rglob("*.md"))
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1)
        for problem in identifier_mismatches(line)
    ]
    assert problems == []


def test_buyer_text_states_no_rate_and_no_guarantee() -> None:
    problems = [
        f"{path.relative_to(REPO_ROOT)}:{number}: {item.rule} {item.excerpt!r}"
        for path in SEND_FILES
        for number, line in buyer_lines(path.read_text(encoding="utf-8"))
        for item in findings(line)
        if item.verdict in _BLOCKING
    ]
    assert problems == []


def test_one_package_price_everywhere() -> None:
    route = next(
        offer["hard_currency_route_ar"]
        for offer in json.loads(CATALOG.read_text(encoding="utf-8"))["offers"]
        if offer["id"] == WEDGE_ID
    )
    for name, text in (
        ("kit", KIT.read_text(encoding="utf-8")),
        ("malt", MALT.read_text(encoding="utf-8")),
    ):
        assert PACKAGE_PRICE in text, name
        assert EURO_RANGE.findall(text) == [], name
    # The catalog route also cites market day rates as ranges (sources, not our price).
    assert PACKAGE_PRICE in route
    assert "290–390" not in route
