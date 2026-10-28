"""Summaries with Wilson 95% intervals for samples A, B, D."""

import collections
import json
import math
import os
import sys
import urllib.parse
from pathlib import Path

OUT_DIR = sys.argv[1] + "/out"


def wilson(k, n, z=1.96):
    if n == 0:
        return (0, 0, 0)
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return round(100 * p, 1), round(100 * (c - h) / d, 1), round(100 * (c + h) / d, 1)


def host(u):
    return urllib.parse.urlparse(u).netloc if u and str(u).startswith("http") else str(u)


def load(n):
    return (
        [
            json.loads(row)
            for row in Path(f"{OUT_DIR}/{n}.jsonl").read_text(encoding="utf-8").splitlines()
        ]
        if os.path.exists(f"{OUT_DIR}/{n}.jsonl")
        else []
    )


res = {}
A = load("a_be_only_0208")
if A:
    n = len(A)
    in_sml = [r for r in A if r["smp_0208"] not in (None, "ERROR")]
    vat = [r for r in in_sml if r["vies_valid"] is True]
    unreach = [r for r in vat if r["sml_9925"] is None]
    res["A"] = {
        "n": n,
        "0208_in_sml": len(in_sml),
        "vat_active": len(vat),
        "vies_unknown": sum(r["vies_valid"] is None for r in in_sml),
        "vat_active_no_9925_in_sml": len(unreach),
        "share_of_vat_active": wilson(len(unreach), len(vat)),
        "share_of_sample": wilson(len(unreach), n),
        "smp_of_unreachable": collections.Counter(host(r["smp_0208"]) for r in unreach).most_common(
            10
        ),
        "no_9925_but_9925_exists": sum(r["sml_9925"] not in (None, "ERROR") for r in in_sml),
    }
B = load("b_fr0225_sirene")
if B:
    n = len(B)
    ok = [r for r in B if not r.get("err")]
    closed = [r for r in ok if r.get("etat_administratif") == "C"]
    nf = [r for r in ok if not r["found"]]
    res["B"] = {
        "n": n,
        "errors": n - len(ok),
        "closed": len(closed),
        "closed_share": wilson(len(closed), len(ok)),
        "not_found": len(nf),
        "not_found_share": wilson(len(nf), len(ok)),
        "closed_by_year": collections.Counter(
            (r.get("date_fermeture") or "?")[:4] for r in closed
        ).most_common(),
        "closed_smp": collections.Counter(host(r.get("smp")) for r in closed).most_common(10),
        "notfound_smp": collections.Counter(host(r.get("smp")) for r in nf).most_common(10),
        "categorie": collections.Counter(
            r.get("categorie_entreprise") for r in ok if r["found"]
        ).most_common(),
        "addresses_closed": sum(r["n_addresses"] for r in closed),
        "addresses_all": sum(r["n_addresses"] for r in ok),
    }
D = load("d_stale_sample")
if D:
    n = len(D)
    stale = [r for r in D if r["smp"] is None]
    res["D"] = {
        "n": n,
        "stale": len(stale),
        "stale_share": wilson(len(stale), n),
        "errors": sum(r["smp"] == "ERROR" for r in D),
        "stale_by_scheme": collections.Counter(r["id"].split(":")[0] for r in stale).most_common(
            10
        ),
        "sample_by_scheme": collections.Counter(r["id"].split(":")[0] for r in D).most_common(10),
    }
print(json.dumps(res, ensure_ascii=False, indent=1))
