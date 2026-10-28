"""Sample B run in parallel with A: same seed and draw order as measure.py, so the SIREN sample is identical."""

import collections
import json
import random
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # sibling helpers (net.py, validate.py)
import net

S = sys.argv[1]
OUT = S + "/out"
rng = random.Random(20261026)
be_only = Path(OUT + "/be_only_0208.txt").read_text(encoding="utf-8").split()
sirens = Path(OUT + "/fr0225_sirens.txt").read_text(encoding="utf-8").split()
rng.sample(be_only, 400)
sample_fr = set(rng.sample(sirens, 1200))
fr_ids = collections.defaultdict(list)
with open(S + "/participants.csv", encoding="latin-1") as f:
    next(f)
    for line in f:
        if line.startswith('"iso6523-actorid-upis::0225:'):
            v = line.strip().strip('"')[27:]
            s = v.partition("_")[0]
            if s in sample_fr:
                fr_ids[s].append(v)
PART = OUT + "/b_partial.jsonl"
done = {}
if Path(PART).exists():
    for line in Path(PART).read_text(encoding="utf-8").splitlines():
        r = json.loads(line)
        done[r["siren"]] = r
rows = []
with open(PART, "a", encoding="utf-8") as part:
    for siren in sorted(sample_fr):
        if siren in done and not done[siren].get("err"):
            rows.append(done[siren])
            continue
        d = net.get_json(
            f"https://recherche-entreprises.api.gouv.fr/search?q={siren}&page=1&per_page=1",
            tries=8,
            pause=2,
        )
        hit = next((x for x in d.get("results", []) if x.get("siren") == siren), None)
        rows.append(
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
        part.write(json.dumps(rows[-1], ensure_ascii=False) + "\n")
        part.flush()
        time.sleep(0.3)
for r in rows:
    if r.get("etat_administratif") == "C" or not r["found"]:
        r["smp"] = net.naptr_host(f"0225:{r['id']}") if r["id"] else None
with open(OUT + "/b_fr0225_sirene.jsonl", "w") as f:
    for r in rows:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")
print("B done", len(rows), flush=True)
