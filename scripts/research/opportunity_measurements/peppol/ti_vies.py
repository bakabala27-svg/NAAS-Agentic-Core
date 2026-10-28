"""G: VAT status (VIES) of October-2026 0208 registrations that have no 9925 in the SML (cohort sample F)."""

import json
import sys
import time
import urllib.parse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # sibling helpers (net.py, validate.py)
import net

S = sys.argv[1]
rows = [
    json.loads(row)
    for row in Path(S + "/out/f_cohort_smp.jsonl").read_text(encoding="utf-8").splitlines()
]
pick = [
    r
    for r in rows
    if r["scheme"] == "0208"
    and r["month"] == "2026-10"
    and r["smp"] not in (None, "ERROR")
    and r.get("sml_9925") is None
]
out = []
for r in pick[:80]:
    num = r["id"].split(":", 1)[1]
    d = net.get_json(
        f"https://ec.europa.eu/taxation_customs/vies/rest-api/ms/BE/vat/{num}", tries=4, pause=3
    )
    out.append(
        {
            "num": num,
            "smp": urllib.parse.urlparse(r["smp"]).netloc,
            "vies_valid": d.get("isValid"),
            "err": d.get("_error"),
        }
    )
    time.sleep(0.6)
with open(S + "/out/g_oct_no9925_vies.jsonl", "w") as f:
    for r in out:
        f.write(json.dumps(r) + "\n")
print("G done", len(out), flush=True)
