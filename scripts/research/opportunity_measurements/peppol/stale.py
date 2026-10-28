"""D: share of directory entries absent from the live SML, on a uniform random sample (reservoir)."""

import json
import random
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # sibling helpers (net.py, validate.py)
import net

S = sys.argv[1]
rng = random.Random(4242)
k = 1500
res = []
n = 0
with open(S + "/participants.csv", encoding="latin-1") as f:
    next(f)
    for line in f:
        pid = line.strip().strip('"')
        if not pid.startswith("iso6523-actorid-upis::"):
            continue
        n += 1
        if len(res) < k:
            res.append(pid[22:])
        else:
            j = rng.randrange(n)
            if j < k:
                res[j] = pid[22:]


def row(v):
    return {"id": v, "smp": net.naptr_host(v)}


with ThreadPoolExecutor(8) as ex:
    rows = list(ex.map(row, res))
with open(S + "/out/d_stale_sample.jsonl", "w") as f:
    for r in rows:
        f.write(json.dumps(r) + "\n")
print("D done", n, flush=True)
