"""E: Belgian entities registered under both 0208 and 9925 — do both point to the same SMP?"""

import json
import random
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # sibling helpers (net.py, validate.py)
import net
from validate import be_ok

S = sys.argv[1]
a, b = set(), set()
with open(S + "/participants.csv", encoding="latin-1") as f:
    next(f)
    for line in f:
        pid = line.strip().strip('"')
        if pid.startswith("iso6523-actorid-upis::0208:"):
            v = pid[27:]
            if be_ok(v):
                a.add(v)
        elif pid.startswith("iso6523-actorid-upis::9925:"):
            v = pid[27:].lower()
            if v.startswith("be") and be_ok(v[2:]):
                b.add(v[2:])
both = sorted(a & b)
sample = random.Random(97).sample(both, 600)


def row(num):
    return {
        "num": num,
        "smp_0208": net.naptr_host(f"0208:{num}"),
        "smp_9925": net.naptr_host(f"9925:be{num}"),
    }


with ThreadPoolExecutor(8) as ex:
    rows = list(ex.map(row, sample))
with open(S + "/out/e_be_split.jsonl", "w") as f:
    for r in rows:
        f.write(json.dumps(r) + "\n")
print("E done", len(both), flush=True)
