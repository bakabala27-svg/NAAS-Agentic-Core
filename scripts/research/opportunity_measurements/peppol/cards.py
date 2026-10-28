"""Stream the business-card CSV from stdin; keep scheme, country, registration month for all rows (no names kept)."""

import collections
import csv
import io
import json
import sys
from pathlib import Path

csv.field_size_limit(10**9)
r = csv.reader(
    io.TextIOWrapper(sys.stdin.buffer, encoding="latin-1", newline=""), delimiter=";", quotechar='"'
)
next(r)
months = collections.defaultdict(collections.Counter)
country = collections.defaultdict(collections.Counter)
n = 0
for row in r:
    if len(row) < 13:
        continue
    pid = row[0]
    scheme = pid[22:].partition(":")[0] if pid.startswith("iso6523-actorid-upis::") else "?"
    months[scheme][row[12][:7]] += 1
    country[scheme][row[2]] += 1
    n += 1
Path(sys.argv[1]).write_text(
    json.dumps(
        {
            "rows": n,
            "months": {k: dict(v) for k, v in months.items()},
            "country": {k: dict(v) for k, v in country.items()},
        },
    ),
    encoding="utf-8",
)
print("cards done", n, flush=True)
