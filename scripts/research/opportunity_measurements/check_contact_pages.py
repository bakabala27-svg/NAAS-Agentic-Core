"""Check candidate official contact URLs: final URL, status, title, and whether a form or contact wording is present."""

import os
import re
import ssl
import sys
import urllib.request

CTX = ssl.create_default_context(cafile=os.environ.get("SSL_CERT_FILE") or None)
for url in sys.argv[1:]:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (research)"})
        with urllib.request.urlopen(req, context=CTX, timeout=25) as r:
            body = r.read(400000).decode("utf-8", "replace")
            title = re.search(r"<title[^>]*>(.*?)</title>", body, re.S | re.I)
            form = bool(
                re.search(
                    r"<form|hsforms|hubspot|typeform|calendly|formspree|wpcf7|gform", body, re.I
                )
            )
            print(
                f"{r.status} | {url} -> {r.geturl()} | form={form} | {(title.group(1).strip() if title else '')[:70]}",
                flush=True,
            )
    except Exception as e:
        print(f"ERR | {url} | {str(e)[:70]}", flush=True)
