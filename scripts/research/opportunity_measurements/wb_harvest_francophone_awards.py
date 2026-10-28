"""Harvest World Bank contract-award notices for francophone African borrowers (official API)."""

import json
import os
import ssl
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

CTX = ssl.create_default_context(cafile=os.environ.get("SSL_CERT_FILE") or None)
COUNTRIES = [
    "Benin",
    "Burkina Faso",
    "Burundi",
    "Cameroon",
    "Central African Republic",
    "Chad",
    "Comoros",
    "Congo, Republic of",
    "Congo, Democratic Republic of",
    "Cote d'Ivoire",
    "Djibouti",
    "Gabon",
    "Guinea",
    "Madagascar",
    "Mali",
    "Mauritania",
    "Niger",
    "Senegal",
    "Togo",
    "Western and Central Africa",
    "Eastern and Southern Africa",
]
FL = "id,notice_type,noticedate,project_ctry_name,project_id,project_name,bid_description,procurement_method_name,notice_text"
OUT = Path(sys.argv[1])


def get(params):
    url = "https://search.worldbank.org/api/v2/procnotices?" + urllib.parse.urlencode(params)
    for attempt in range(5):
        try:
            with urllib.request.urlopen(
                urllib.request.Request(url, headers={"User-Agent": "research/1.0"}),
                context=CTX,
                timeout=90,
            ) as r:
                return json.load(r)
        except Exception as e:
            time.sleep(2**attempt)
            last = e
    raise last


def main():
    done = (
        {json.loads(row)["id"] for row in OUT.read_text(encoding="utf-8").splitlines()}
        if OUT.exists()
        else set()
    )
    with OUT.open("a", encoding="utf-8") as out:
        for c in COUNTRIES:
            os_ = 0
            while True:
                d = get(
                    {
                        "format": "json",
                        "rows": 200,
                        "os": os_,
                        "notice_type_exact": "Contract Award",
                        "project_ctry_name_exact": c,
                        "fl": FL,
                        "srt": "noticedate",
                        "order": "desc",
                    }
                )
                p = d.get("procnotices") or {}
                items = list(p.values()) if isinstance(p, dict) else p
                total = int(d.get("total") or 0)
                old = 0
                for v in items:
                    if v.get("id") in done:
                        continue
                    nd = v.get("noticedate") or ""
                    try:
                        y = int(nd[-4:])
                    except ValueError:
                        y = 0
                    if y and y < 2024:
                        old += 1
                        continue
                    done.add(v["id"])
                    out.write(json.dumps(v, ensure_ascii=False) + "\n")
                print(c, "os", os_, "got", len(items), "total", total, "old", old, flush=True)
                os_ += 200
                if not items or os_ >= total or old == len(items):
                    break
                time.sleep(0.3)


if __name__ == "__main__":
    main()
