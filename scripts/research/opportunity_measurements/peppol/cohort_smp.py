"""F: who registered the Sept–Oct 2026 cohort? Random 300 per (scheme, month) -> SMP host; BE 0208 also checks 9925."""

import collections
import json
import random
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # sibling helpers (net.py, validate.py)
import net

S = sys.argv[1]
groups = collections.defaultdict(list)
for line in Path(S + "/out/cohort_2026_09_10.tsv").read_text(encoding="utf-8").splitlines():
    date, pid = line.rstrip("\n").split("\t")
    scheme = pid.split(":")[0]
    groups[(scheme, date[:7])].append(pid)
rng = random.Random(7)
jobs = []
for key in sorted(groups):
    for pid in rng.sample(groups[key], min(300, len(groups[key]))):
        jobs.append((key, pid))


def row(job):
    (scheme, month), pid = job
    r = {"scheme": scheme, "month": month, "id": pid, "smp": net.naptr_host(pid)}
    if scheme == "0208":
        r["sml_9925"] = net.naptr_host("9925:be" + pid.split(":", 1)[1])
    return r


with ThreadPoolExecutor(8) as ex:
    rows = list(ex.map(row, jobs))
with open(S + "/out/f_cohort_smp.jsonl", "w") as f:
    for r in rows:
        f.write(json.dumps(r) + "\n")
print("F done", {f"{k[0]}/{k[1]}": len(v) for k, v in groups.items()}, flush=True)
