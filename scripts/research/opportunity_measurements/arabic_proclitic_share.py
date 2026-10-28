"""Share of Arabic word tokens carrying a fused definite/proclitic prefix, measured on a local
corpus (tracked .md files of this repository). Lower-bound estimate: only prefix classes
ال · [وفبك]ال · لل are counted; attached pronoun suffixes are NOT counted (no morphological
analyser). Function words that are lexically ال-initial are excluded."""

import re
import subprocess
from collections import Counter
from pathlib import Path

files = subprocess.run(
    ["git", "-c", "core.quotepath=false", "ls-files", "-z", "*.md"],
    capture_output=True,
    text=True,
    check=True,
).stdout.split("\0")
token_re = re.compile(r"[ء-غف-ي]+")  # Arabic letters, tatweel/harakat excluded
strip_marks = re.compile(r"[ـً-ْ]")  # tatweel + harakat
EXCLUDE = {
    "الذي",
    "التي",
    "الذين",
    "اللذان",
    "اللتان",
    "اللاتي",
    "اللواتي",
    "الآن",
    "الله",
    "اللهم",
    "إلا",
    "الا",
}
prefix_re = re.compile(r"^(?:[وفبك]?ال|لل)")

total = prefixed = 0
per_file = Counter()
for f in files:
    try:
        text = Path(f).read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        continue
    for tok in token_re.findall(strip_marks.sub("", text)):
        if len(tok) < 2 or tok in EXCLUDE:
            continue
        total += 1
        if prefix_re.match(tok) and len(tok) >= 4:
            prefixed += 1
print(f"files={len(files)} arabic_tokens={total} prefixed={prefixed} share={prefixed / total:.4f}")
