"""H2: addresses held by closed SIRENs + provider of a random 300 closed SIRENs (one address each)."""

import collections
import csv
import io
import json
import sys
import urllib.parse
import zipfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # sibling helpers (net.py, validate.py)
import net

S = sys.argv[1]
OUT_DIR = S + "/out"
sample = Path(OUT_DIR + "/h_closed_sample.txt").read_text(encoding="utf-8").split()
missing = Path(OUT_DIR + "/h_missing_sample.txt").read_text(encoding="utf-8").split()
closed_all = set()
z = zipfile.ZipFile(S + "/sirene_ul.zip")
f = io.TextIOWrapper(z.open(z.namelist()[0]), encoding="utf-8", newline="")
r = csv.reader(f)
h = next(r)
ix = {k: i for i, k in enumerate(h)}
fr = set(Path(OUT_DIR + "/fr0225_sirens.txt").read_text(encoding="utf-8").split())
for row in r:
    if row[ix["etatAdministratifUniteLegale"]] == "C" and row[ix["siren"]] in fr:
        closed_all.add(row[ix["siren"]])
addr_closed = 0
first = {}
want = set(sample) | set(missing)
with open(S + "/participants.csv", encoding="latin-1") as fh:
    next(fh)
    for line in fh:
        if line.startswith('"iso6523-actorid-upis::0225:'):
            v = line.strip().strip('"')[27:]
            s = v.partition("_")[0]
            if s in closed_all:
                addr_closed += 1
            if s in want and s not in first:
                first[s] = v


def smp(s):
    return {
        "siren": s,
        "id": first.get(s),
        "smp": net.naptr_host("0225:" + first[s]) if s in first else None,
    }


with ThreadPoolExecutor(8) as ex:
    rc = list(ex.map(smp, sample))
    rm = list(ex.map(smp, missing))


def host(u):
    return urllib.parse.urlparse(u).netloc if u and str(u).startswith("http") else str(u)


res = {
    "closed_sirens": len(closed_all),
    "addresses_of_closed": addr_closed,
    "closed_sample_providers": collections.Counter(host(x["smp"]) for x in rc).most_common(12),
    "missing_sample_providers": collections.Counter(host(x["smp"]) for x in rm).most_common(8),
}
Path(OUT_DIR + "/h2_closed_attr.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
print("H2 done", json.dumps(res)[:900], flush=True)
