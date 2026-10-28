"""Three live measurements on random samples; writes JSON lines. Seed fixed for reproducibility."""

import collections
import json
import random
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # sibling helpers (net.py, validate.py)
import net
from validate import FAKE, be_ok, siren_ok

S = sys.argv[1]
OUT = S + "/out"
rng = random.Random(20261026)

# ---- index full IDs we need -------------------------------------------------
be_only = Path(OUT + "/be_only_0208.txt").read_text(encoding="utf-8").split()
sirens = Path(OUT + "/fr0225_sirens.txt").read_text(encoding="utf-8").split()
sample_be = rng.sample(be_only, 400)
sample_fr = set(rng.sample(sirens, 1200))
fr_ids = collections.defaultdict(list)
invalid = []  # (scheme, value)
with open(S + "/participants.csv", encoding="latin-1") as f:
    next(f)
    for line in f:
        pid = line.strip().strip('"')
        if not pid.startswith("iso6523-actorid-upis::"):
            continue
        scheme, _, v = pid[22:].partition(":")
        if scheme == "0225":
            siren = v.partition("_")[0]
            if siren in sample_fr:
                fr_ids[siren].append(v)
            if not siren_ok(siren) or FAKE.match(siren):
                invalid.append((scheme, v))
        elif scheme == "0208" and not be_ok(v):
            invalid.append((scheme, v))
        elif scheme == "9925":
            low = v.lower()
            if not (low.startswith("be") and be_ok(low[2:])):
                invalid.append((scheme, v))
print("indexed", len(fr_ids), "fr sirens;", len(invalid), "invalid ids", flush=True)


def dump(name, rows):
    with open(f"{OUT}/{name}.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


# ---- C: attribute every malformed identifier to its SMP ---------------------
def smp_of(item):
    scheme, v = item
    return {"scheme": scheme, "value": v, "smp": net.naptr_host(f"{scheme}:{v}")}


with ThreadPoolExecutor(8) as ex:
    rows_c = list(ex.map(smp_of, invalid))
dump("c_invalid_smp", rows_c)
print("C done", flush=True)


# ---- A: Belgian entities in the directory under 0208 only -------------------
def be_row(num):
    return {
        "num": num,
        "smp_0208": net.naptr_host(f"0208:{num}"),
        "sml_9925": net.naptr_host(f"9925:be{num}"),
    }


with ThreadPoolExecutor(6) as ex:
    rows_a = list(ex.map(be_row, sample_be))
for r in rows_a:
    d = net.get_json(
        f"https://ec.europa.eu/taxation_customs/vies/rest-api/ms/BE/vat/{r['num']}",
        tries=5,
        pause=3,
    )
    r["vies_valid"] = d.get("isValid")
    r["vies_user_error"] = d.get("userError")
    r["vies_err"] = d.get("_error")
    time.sleep(0.8)
dump("a_be_only_0208", rows_a)
print("A done", flush=True)

# ---- B: French 0225 SIRENs vs SIRENE status ----------------------------------
rows_b = []
for siren in sorted(sample_fr):
    d = net.get_json(
        f"https://recherche-entreprises.api.gouv.fr/search?q={siren}&page=1&per_page=1",
        tries=8,
        pause=2,
    )
    hit = next((x for x in d.get("results", []) if x.get("siren") == siren), None)
    rows_b.append(
        {
            "siren": siren,
            "n_addresses": len(fr_ids[siren]),
            "id": fr_ids[siren][0] if fr_ids[siren] else None,
            "found": hit is not None,
            "err": d.get("_error"),
            **(
                {
                    k: hit.get(k)
                    for k in (
                        "etat_administratif",
                        "date_creation",
                        "date_fermeture",
                        "categorie_entreprise",
                        "nature_juridique",
                        "tranche_effectif_salarie",
                    )
                }
                if hit
                else {}
            ),
        }
    )
    time.sleep(0.35)
for r in rows_b:
    if r.get("etat_administratif") == "C" or not r["found"]:
        r["smp"] = net.naptr_host(f"0225:{r['id']}") if r["id"] else None
dump("b_fr0225_sirene", rows_b)
print("B done", flush=True)
