"""Fetch candidate official homepages; report status, title, functional mailto addresses and contact links."""

import html
import json
import os
import re
import ssl
import sys
import urllib.request

CTX = ssl.create_default_context(cafile=os.environ.get("SSL_CERT_FILE") or None)
FUNCTIONAL = re.compile(
    r"^(contact|info|commercial|sales|business|bd|partenariat|partners|partnership|hello|bonjour|marketing|direction|rh|recrutement|careers|admin|office|secretariat|communication|devis)[\w.\-]*@",
    re.I,
)


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (research)"})
    with urllib.request.urlopen(req, context=CTX, timeout=25) as r:
        return r.geturl(), r.status, r.read(600000).decode("utf-8", "replace")


def main():
    out = {}
    for url in sys.argv[1:]:
        try:
            final, st, body = fetch(url)
        except Exception as e:
            out[url] = {"error": str(e)[:120]}
            print(url, "ERR", str(e)[:80], flush=True)
            continue
        title = re.search(r"<title[^>]*>(.*?)</title>", body, re.S | re.I)
        mails = sorted(
            {
                m.lower()
                for m in re.findall(r"[\w.+\-]+@[\w\-]+\.[\w.\-]+", html.unescape(body))
                if not m.lower().endswith((".png", ".jpg", ".svg", ".webp", ".gif"))
            }
        )
        contacts = sorted(
            {
                h
                for h in re.findall(r'href="([^"]+)"', body)
                if re.search(r"contact|nous-joindre|joindre|partenaire|partner", h, re.I)
            }
        )[:6]
        out[url] = {
            "final": final,
            "status": st,
            "title": (title.group(1).strip()[:90] if title else ""),
            "functional": [m for m in mails if FUNCTIONAL.match(m)],
            "other_mails": len([m for m in mails if not FUNCTIONAL.match(m)]),
            "contact_links": contacts,
        }
        print(
            url,
            st,
            "|",
            out[url]["title"][:60],
            "|",
            out[url]["functional"][:4],
            "|",
            contacts[:3],
            flush=True,
        )
    with open("dl/sites.json", "a", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False)


if __name__ == "__main__":
    main()
