"""H: full census — every SIREN behind a French 0225 Peppol address vs the SIRENE legal-unit stock (2026-10-01)."""

import collections
import csv
import io
import json
import random
import sys
import zipfile
from pathlib import Path

S = sys.argv[1]
OUT = S + "/out"
sirens = set(Path(OUT + "/fr0225_sirens.txt").read_text(encoding="utf-8").split())
print("peppol 0225 sirens", len(sirens), flush=True)
z = zipfile.ZipFile(S + "/sirene_ul.zip")
name = z.namelist()[0]
f = io.TextIOWrapper(z.open(name), encoding="utf-8", newline="")
r = csv.reader(f)
head = next(r)
ix = {h: i for i, h in enumerate(head)}
print(
    "columns",
    [
        h
        for h in head
        if h
        in (
            "siren",
            "etatAdministratifUniteLegale",
            "dateDebut",
            "statutDiffusionUniteLegale",
            "categorieJuridiqueUniteLegale",
            "categorieEntreprise",
            "dateCreationUniteLegale",
        )
    ],
    flush=True,
)
found = {}
total = 0
closed_all = 0
for row in r:
    total += 1
    s = row[ix["siren"]]
    if row[ix["etatAdministratifUniteLegale"]] == "C":
        closed_all += 1
    if s in sirens:
        found[s] = (
            row[ix["etatAdministratifUniteLegale"]],
            row[ix["dateDebut"]],
            row[ix["statutDiffusionUniteLegale"]],
            row[ix["categorieJuridiqueUniteLegale"]],
            row[ix.get("categorieEntreprise", ix["siren"])],
        )
closed = {s: v for s, v in found.items() if v[0] == "C"}
missing = sirens - set(found)
by_year = collections.Counter((v[1] or "?")[:4] for v in closed.values())
by_cj = collections.Counter(v[3][:2] for v in closed.values())
res = {
    "sirene_rows": total,
    "sirene_closed_rows": closed_all,
    "peppol_sirens": len(sirens),
    "found": len(found),
    "missing_from_sirene": len(missing),
    "closed": len(closed),
    "closed_by_year_of_closure_period": dict(sorted(by_year.items())),
    "closed_by_legal_form_prefix": by_cj.most_common(12),
    "statut_diffusion_found": collections.Counter(v[2] for v in found.values()).most_common(),
}
Path(OUT + "/h_sirene_census.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
rng = random.Random(2610)
Path(OUT + "/h_closed_sample.txt").write_text(
    "\n".join(rng.sample(sorted(closed), min(300, len(closed))))
)
Path(OUT + "/h_missing_sample.txt").write_text(
    "\n".join(rng.sample(sorted(missing), min(100, len(missing))))
)
print("H done", json.dumps(res)[:600], flush=True)
