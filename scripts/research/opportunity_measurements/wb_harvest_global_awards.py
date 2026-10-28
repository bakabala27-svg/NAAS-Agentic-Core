"""Harvest the most recent 100,000 World Bank contract-award notices worldwide (API offset cap), resumable."""

import json
import os
import ssl
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

CTX = ssl.create_default_context(cafile=os.environ.get("SSL_CERT_FILE") or None)
FL = "id,notice_type,noticedate,project_ctry_name,project_id,procurement_method_name,bid_description,notice_text"
OUT = Path(sys.argv[1])
STATE = OUT.with_suffix(".offset")


def get(params):
    url = "https://search.worldbank.org/api/v2/procnotices?" + urllib.parse.urlencode(params)
    last = None
    for attempt in range(6):
        try:
            with urllib.request.urlopen(
                urllib.request.Request(url, headers={"User-Agent": "research/1.0"}),
                context=CTX,
                timeout=120,
            ) as r:
                return json.load(r)
        except Exception as e:
            last = e
            time.sleep(2**attempt)
    raise last


def main():
    os_ = int(STATE.read_text()) if STATE.exists() else 0
    with OUT.open("a", encoding="utf-8") as out:
        while os_ < 100000:
            d = get(
                {
                    "format": "json",
                    "rows": 500,
                    "os": os_,
                    "notice_type_exact": "Contract Award",
                    "fl": FL,
                    "srt": "noticedate",
                    "order": "desc",
                }
            )
            p = d.get("procnotices") or {}
            items = list(p.values()) if isinstance(p, dict) else p
            if not items:
                print("empty at", os_, flush=True)
                break
            for v in items:
                out.write(json.dumps(v, ensure_ascii=False) + "\n")
            out.flush()
            os_ += 500
            STATE.write_text(str(os_))
            if os_ % 5000 == 0:
                print("offset", os_, "last date", items[-1].get("noticedate"), flush=True)
            time.sleep(0.2)


if __name__ == "__main__":
    main()
