"""Why Tunisian firms win: participation, win rate, sectors, consortia and scoring weights (WB award notices)."""

import collections
import html
import json
import re
import statistics as st

PAT = {
    "TN": r"Country:\s*(Tunisia|Tunisie)",
    "MA": r"Country:\s*(Morocco|Maroc)",
    "DZ": r"Country:\s*(Algeria|Alg[ée]?rie)",
}
SECT = [
    (
        "ingénierie/supervision",
        r"contr[ôo]le et surveillance|supervision|maîtrise d.?œuvre|ma[îi]trise d.?oeuvre|APS|APD|[ée]tude|etude|feasib|faisabilit",
    ),
    ("audit/finance", r"audit|comptab|financ|fiduciaire|commissaire"),
    (
        "SI/données",
        r"donn[ée]?es|syst[èe]?me d.?information|num[ée]?ris|digital|logiciel|informatique|plateforme|registre|data",
    ),
    ("formation", r"formation|renforcement des capacit|training"),
    ("travaux/fournitures", r"travaux|fourniture|acquisition|construction|r[ée]habilitation"),
]


def text(v):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", v.get("notice_text") or "")))


def awarded(t):
    m = re.search(
        r"Awarded (?:Bidder|Firm)\(s\):(.*?)(?:Rejected|Evaluated Bidder|Evaluated Firm|Beneficial Ownership|$)",
        t,
    )
    return m.group(1) if m else ""


part = collections.Counter()
win = collections.Counter()
sect = {c: collections.Counter() for c in PAT}


def _lines(path):
    with open(path, encoding="utf-8") as fh:
        yield from fh


consort = collections.Counter()
method = {c: collections.Counter() for c in PAT}
weights = []
n = 0
for line in _lines("dl/awards.jsonl"):
    v = json.loads(line)
    n += 1
    t = text(v)
    a = awarded(t)
    for c, p in PAT.items():
        if re.search(p, t):
            part[c] += 1
            if re.search(p, a):
                win[c] += 1
                desc = v.get("bid_description") or ""
                s = next((name for name, rx in SECT if re.search(rx, desc, re.I)), "أخرى")
                sect[c][s] += 1
                method[c][v.get("procurement_method_name") or "?"] += 1
                countries = re.findall(
                    r"Country:\s*([A-Za-zéèô' ,\.]+?)(?=\s(?:[A-Z]|Bid|Final|Scores|Price|Signed|Evaluat|Benef|$))",
                    a,
                )
                if len({x.strip() for x in countries}) > 1:
                    consort[c] += 1
                if c == "TN":
                    m = re.search(
                        r"Consultant Specific Experience:\s*(\d+).*?Methodology:\s*(\d+).*?Key Personnel:\s*(\d+)",
                        t,
                    )
                    if m:
                        weights.append(tuple(int(x) for x in m.groups()))
print("notices", n)
for c in PAT:
    print(
        f"{c}: appears in {part[c]} notices (bidder of any status), wins {win[c]} -> win share {win[c] / part[c]:.0%}"
        if part[c]
        else c
    )
    print("   sectors:", dict(sect[c].most_common()))
    print(
        "   consortium with another country:",
        consort[c],
        f"({consort[c] / win[c]:.0%})" if win[c] else "",
    )
    print("   methods:", dict(method[c].most_common(5)))
if weights:
    print(
        "TN QCBS score breakdown (experience, methodology, key personnel) over",
        len(weights),
        "notices: medians",
        st.median(w[0] for w in weights),
        st.median(w[1] for w in weights),
        st.median(w[2] for w in weights),
    )
