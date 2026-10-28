"""Extract awarded firms + countries + price from WB award notices; keep Maghreb winners."""

import collections
import html
import json
import re
import sys
from pathlib import Path

MAGHREB = {
    "Tunisia": "TN",
    "Tunisie": "TN",
    "Morocco": "MA",
    "Maroc": "MA",
    "Algeria": "DZ",
    "Algrie": "DZ",
    "Algérie": "DZ",
}
DATA_IT = re.compile(
    r"donn[ée]?es|data|base de|syst[èe]?me d.?information|\bSI\b|SIG\b|num[ée]?ris|digital|logiciel|software|informatique|application|plateforme|platform|fiabilis|assainissement|registre|recensement|enqu[êe]?te|survey|cartograph|d[ée]?mat[ée]?rialis|archiv|e-?gov|interop|web|portail|ERP|SIGFIP|identit",
    re.I,
)
CFA_PER_EUR = 655.957


def text(v):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", v.get("notice_text") or "")))


def awarded_segment(t):
    m = re.search(
        r"Awarded (?:Bidder|Firm)\(s\):(.*?)(?:Rejected|Evaluated Bidder|Evaluated Firm|$)", t
    )
    return m.group(1) if m else ""


def firms(seg):
    parts = re.split(r"Country:\s*", seg)
    out = []
    for i in range(1, len(parts)):
        names = re.findall(r"([A-Z0-9][A-Za-z0-9&'.,\-/ ]{1,140}?)\s*\((\d{3,9})\)", parts[i - 1])
        country = next((v for k, v in MAGHREB.items() if parts[i].startswith(k)), None)
        cname = parts[i].split(" ")[0]
        if names:
            out.append((names[-1][0].strip(" ,"), names[-1][1], country, cname))
    return out


def price(t):
    m = re.search(
        r"Signed Contract [Pp]rice:?\s*(?:Price:\s*Currency:\s*Amount:\s*)?([A-Z]{3})\s*([\d,.]+)",
        t,
    )
    if not m:
        m = re.search(r"Signed Contract [Pp]rice\s*([A-Z]{3})\s*([\d,.]+)", t)
    if not m:
        return None, None
    try:
        return m.group(1), float(m.group(2).replace(",", ""))
    except ValueError:
        return m.group(1), None


def main(src, dst):
    rows = [json.loads(row) for row in Path(src).read_text(encoding="utf-8").splitlines()]
    hits = []
    for v in rows:
        t = text(v)
        fs = firms(awarded_segment(t))
        mag = [f for f in fs if f[2]]
        if not mag:
            continue
        cur, amt = price(t)
        eur = (
            round(amt / CFA_PER_EUR)
            if cur in ("XOF", "XAF") and amt
            else (round(amt) if cur == "EUR" and amt else None)
        )
        hits.append(
            {
                "id": v["id"],
                "date": v.get("noticedate"),
                "borrower": v.get("project_ctry_name"),
                "project": v.get("project_name"),
                "method": v.get("procurement_method_name"),
                "scope": (v.get("bid_description") or "")[:240],
                "data_it": bool(DATA_IT.search(v.get("bid_description") or "")),
                "currency": cur,
                "amount": amt,
                "eur": eur,
                "maghreb_firms": [{"name": f[0], "wb_id": f[1], "cc": f[2]} for f in mag],
                "partners": [{"name": f[0], "country": f[3]} for f in fs if not f[2]],
            }
        )
    with open(dst, "w", encoding="utf-8") as fh:
        json.dump(hits, fh, ensure_ascii=False, indent=1)
    print(
        "notices",
        len(rows),
        "with Maghreb winner",
        len(hits),
        "data/IT",
        sum(h["data_it"] for h in hits),
    )
    by = collections.Counter(f["cc"] for h in hits for f in h["maghreb_firms"])
    print("firm-awards by cc", dict(by))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
