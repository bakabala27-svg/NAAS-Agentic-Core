"""Supplier-country league table from World Bank award notices: presence (any status) and wins."""

import collections
import html
import json
import re
import sys
import unicodedata
from pathlib import Path

STOP = r"(?=\s(?:Bid|Final|Signed|Scores|Evaluat|Rejected|Beneficial|Price|Technical|Registry|Tel|Tél|T[ée]l|Email|E-mail|Fax|Mobile|Cell|Web|Awarded|Duration|Notice|Contract|Reason|Name|Nationality|Combined|Rank|Minimum|Consultant|Methodology|Key|Currency|Amount|\(|\d)|$)"
ALIAS = {
    "tunisie": "tunisia",
    "maroc": "morocco",
    "algerie": "algeria",
    "algrie": "algeria",
    "senegal": "senegal",
    "sngal": "senegal",
    "cote divoire": "cote d'ivoire",
    "cote d'ivoire": "cote d'ivoire",
    "ivory coast": "cote d'ivoire",
    "cte divoire": "cote d'ivoire",
    "benin": "benin",
    "bnin": "benin",
    "cameroun": "cameroon",
    "tchad": "chad",
    "egypte": "egypt",
    "egypt, arab republic of": "egypt",
    "liban": "lebanon",
    "jordanie": "jordan",
    "turquie": "turkey",
    "turkiye": "turkey",
    "trkiye": "turkey",
    "inde": "india",
    "chine": "china",
    "china, people's republic of": "china",
    "etats-unis": "united states",
    "usa": "united states",
    "united states of america": "united states",
    "royaume-uni": "united kingdom",
    "uk": "united kingdom",
    "allemagne": "germany",
    "belgique": "belgium",
    "espagne": "spain",
    "italie": "italy",
    "pays-bas": "netherlands",
    "suisse": "switzerland",
    "canada": "canada",
    "mauritanie": "mauritania",
    "niger": "niger",
    "mali": "mali",
    "burkina": "burkina faso",
    "congo, democratic republic of": "congo dr",
    "rdc": "congo dr",
    "congo, rep.": "congo rep",
    "congo, republic of": "congo rep",
    "madagascar": "madagascar",
    "kenya": "kenya",
    "nigeria": "nigeria",
    "south africa": "south africa",
    "afrique du sud": "south africa",
    "rwanda": "rwanda",
    "ethiopie": "ethiopia",
    "pakistan": "pakistan",
    "bangladesh": "bangladesh",
    "indonesie": "indonesia",
}


def norm(name):
    n = (
        unicodedata.normalize("NFKD", name)
        .encode("ascii", "ignore")
        .decode()
        .lower()
        .strip(" .,;:-'")
    )
    n = re.sub(r"\s+", " ", n)
    rules = [
        ("burkina", "burkina faso"),
        ("centrafric", "central african republic"),
        ("central african", "central african republic"),
        ("ivoire", "cote d'ivoire"),
        ("comor", "comoros"),
        ("tunis", "tunisia"),
        ("maroc", "morocco"),
        ("morocco", "morocco"),
        ("egypt", "egypt"),
        ("turk", "turkey"),
        ("liban", "lebanon"),
        ("lebanon", "lebanon"),
        ("jordan", "jordan"),
        ("mauritan", "mauritania"),
        ("senegal", "senegal"),
        ("sngal", "senegal"),
        ("cameroun", "cameroon"),
        ("tchad", "chad"),
    ]
    if "congo" in n:
        return (
            "congo dr"
            if ("democrat" in n or "dmocrat" in n or "rdc" in n or "kinshasa" in n)
            else "congo rep"
        )
    if n.startswith("alg"):
        return "algeria"
    for key, val in rules:
        if key in n:
            return val
    return ALIAS.get(n, n)


def text(v):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", v.get("notice_text") or "")))


def segments(t):
    a = re.search(
        r"Awarded (?:Bidder|Firm)\(s\):(.*?)(?:Rejected|Evaluated Bidder|Evaluated Firm|Beneficial Ownership|$)",
        t,
    )
    return (a.group(1) if a else ""), t


def countries(seg):
    return {norm(m) for m in re.findall(r"Country:\s*([A-Za-zÀ-ÿ' ,.\-]{2,45}?)" + STOP, seg)}


def _lines(path):
    with open(path, encoding="utf-8") as fh:
        yield from fh


def main(path, out):
    present = collections.Counter()
    won = collections.Counter()
    borrowers = collections.defaultdict(collections.Counter)
    n = 0
    seen = set()
    for line in _lines(path):
        v = json.loads(line)
        if v["id"] in seen:
            continue
        seen.add(v["id"])
        n += 1
        a, t = segments(text(v))
        allc, winc = countries(t), countries(a)
        for c in allc:
            present[c] += 1
        for c in winc:
            won[c] += 1
            borrowers[c][v.get("project_ctry_name") or "?"] += 1
    rows = sorted(present, key=lambda c: (-won[c], c))  # ties by name: set order is hash-seeded
    Path(out).write_text(
        json.dumps(
            {
                "notices": n,
                "rows": [
                    {
                        "country": c,
                        "present": present[c],
                        "won": won[c],
                        "top_borrowers": borrowers[c].most_common(8),
                    }
                    for c in rows
                    if present[c] >= 5
                ],
            },
            ensure_ascii=False,
            indent=1,
        ),
        encoding="utf-8",
    )
    print("notices", n)
    for c in rows[:45]:
        print(f"{c[:28]:28} present {present[c]:6} won {won[c]:6} rate {won[c] / present[c]:.0%}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
