"""Small polite HTTP helpers (stdlib only) for public registries."""

import base64
import hashlib
import json
import os
import ssl
import time
import urllib.parse
import urllib.request

CTX = ssl.create_default_context(cafile=os.environ.get("SSL_CERT_FILE") or None)
SML_ZONE = "iso6523-actorid-upis.participant.sml.prod.tech.peppol.org"


def get_json(url, tries=6, pause=1.5, timeout=25):
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "independent-research/0.1", "Accept": "application/json"},
            )
            with urllib.request.urlopen(req, context=CTX, timeout=timeout) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            last = e
            if e.code in (404,):
                return {"_http": 404}
            time.sleep(pause * (i + 1))
        except Exception as e:
            last = e
            time.sleep(pause * (i + 1))
    return {"_error": repr(last)}


def naptr_host(value):
    """value like '0208:0400000977' -> SMP URL, or None if not registered in the SML."""
    h = (
        base64.b32encode(hashlib.sha256(value.lower().encode()).digest())
        .decode()
        .rstrip("=")
        .lower()
    )
    d = get_json(
        "https://dns.google/resolve?name=" + urllib.parse.quote(f"{h}.{SML_ZONE}") + "&type=NAPTR"
    )
    if "_error" in d:
        return "ERROR"
    if d.get("Status") == 3:
        return None
    for a in d.get("Answer", []):
        data = a.get("data", "")
        if "!" in data:
            return data.split("!")[2]
    return "NO_NAPTR"
