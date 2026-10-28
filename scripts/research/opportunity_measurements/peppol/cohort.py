"""Stream business cards; keep participant IDs registered in 2026-09/2026-10 for schemes 0208, 9925, 0225, 0235."""

import csv
import io
import sys

csv.field_size_limit(10**9)
r = csv.reader(
    io.TextIOWrapper(sys.stdin.buffer, encoding="latin-1", newline=""), delimiter=";", quotechar='"'
)
next(r)
keep = ("0208", "9925", "0225", "0235")
n = 0
with open(sys.argv[1], "w") as out:
    for row in r:
        if len(row) < 13 or not row[0].startswith("iso6523-actorid-upis::"):
            continue
        scheme = row[0][22:].partition(":")[0]
        if scheme in keep and row[12][:7] in ("2026-09", "2026-10"):
            out.write(f"{row[12][:10]}\t{row[0][22:]}\n")
            n += 1
print("cohort done", n, flush=True)
