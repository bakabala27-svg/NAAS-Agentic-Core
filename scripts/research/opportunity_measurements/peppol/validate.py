"""Checksum census of the Peppol Directory participant export (read-only, offline)."""

import collections
import json
import re
import sys


def luhn(s):
    if not s.isdigit():
        return False
    total = 0
    for i, ch in enumerate(reversed(s)):
        d = int(ch)
        if i % 2 == 1:
            d *= 2
            if d > 9:
                d -= 9
        total += d
    return total % 10 == 0


def siren_ok(s):
    return len(s) == 9 and luhn(s)


def siret_ok(s):
    if len(s) != 14 or not s.isdigit():
        return False
    if s.startswith("356000000"):  # La Poste exception
        return sum(int(c) for c in s) % 5 == 0
    return luhn(s)


def be_ok(s):  # Belgian enterprise number, 10 digits
    return len(s) == 10 and s.isdigit() and s[0] in "01" and 97 - int(s[:8]) % 97 == int(s[8:])


def fr_vat_key(siren):
    return (12 + 3 * (int(siren) % 97)) % 97


def no_ok(s):
    if len(s) != 9 or not s.isdigit():
        return False
    w = [3, 2, 7, 6, 5, 4, 3, 2]
    r = (
        11 - sum(int(a) * b for a, b in zip(s, w, strict=False)) % 11
    )  # 8 weights over the first 8 digits
    r = 0 if r == 11 else r
    return r != 10 and r == int(s[8])


def abn_ok(s):
    if len(s) != 11 or not s.isdigit():
        return False
    d = [int(c) for c in s]
    d[0] -= 1
    w = [10, 1, 3, 5, 7, 9, 11, 13, 15, 17, 19]
    return sum(a * b for a, b in zip(d, w, strict=True)) % 89 == 0


def gs1_ok(s):
    if len(s) != 13 or not s.isdigit():
        return False
    body, chk = s[:12], int(s[12])
    t = sum(int(c) * (3 if i % 2 else 1) for i, c in enumerate(body))
    return (10 - t % 10) % 10 == chk


def se_ok(s):
    return len(s) == 10 and luhn(s)


FAKE = re.compile(r"^(\d)\1{6,}")  # long runs like 000000000, 1111111


REPORTED = ("0208", "9925", "0225", "0002", "0009", "9957", "0192", "0151", "0088", "0007")


class Census:
    """Running tallies of the participant export, one counter per identifier scheme."""

    def __init__(self):
        self.stats = collections.defaultdict(collections.Counter)
        self.be0208, self.be9925 = set(), set()
        self.fr0225_siren = collections.Counter()
        self.fr0225_suffix = collections.Counter()
        self.examples = collections.defaultdict(list)

    def ex(self, key, v):
        if len(self.examples[key]) < 6:
            self.examples[key].append(v)

    def checked(self, scheme, st, v, ok, fake):
        """Common tally for a scheme with one checksum: valid / invalid (+ optional fake run)."""
        if ok:
            st["valid"] += 1
        else:
            st["invalid"] += 1
            self.ex(scheme + ":invalid", v)
        if fake and FAKE.match(v):
            st["fake_run"] += 1


def _be_0208(c, st, v, low):
    c.checked("0208", st, v, be_ok(v), fake=True)
    if be_ok(v):
        c.be0208.add(v)


def _be_9925(c, st, v, low):
    if low.startswith("be") and be_ok(low[2:]):
        st["valid_be"] += 1
        c.be9925.add(low[2:])
    elif low.startswith("be"):
        st["be_bad_checksum_or_len"] += 1
        c.ex("9925:be_bad", v)
    elif low.startswith("0208") and be_ok(low[4:]):
        st["prefix_0208_instead_of_BE"] += 1
        c.ex("9925:0208", v)
    elif be_ok(low):
        st["missing_BE_prefix"] += 1
        c.ex("9925:noBE", v)
    else:
        st["other"] += 1
        c.ex("9925:other", v)


def _fr_0225(c, st, v, low):
    siren, _, suffix = v.partition("_")
    c.fr0225_siren[siren] += 1
    c.fr0225_suffix[suffix.split("_")[-1] if suffix else "(none)"] += 1
    if siren_ok(siren):
        st["siren_valid"] += 1
        if FAKE.match(siren):
            st["siren_fake_run"] += 1
            c.ex("0225:fake", v)
    else:
        st["siren_invalid"] += 1
        c.ex("0225:invalid", v)


def _fr_vat_9957(c, st, v, low):
    body = low[2:] if low.startswith("fr") else low
    ok = (
        len(body) == 11
        and body.isdigit()
        and siren_ok(body[2:])
        and int(body[:2]) == fr_vat_key(body[2:])
    )
    key = ("fr_" if low.startswith("fr") else "no_FR_prefix_") + ("valid" if ok else "invalid")
    st[key] += 1
    if not ok:
        c.ex("9957:invalid", v)


def _single_checksum(fn, fake):
    def handler(c, st, v, low, scheme):
        c.checked(scheme, st, v, fn(v), fake=fake)

    return handler


HANDLERS = {"0208": _be_0208, "9925": _be_9925, "0225": _fr_0225, "9957": _fr_vat_9957}
SINGLE = {
    "0002": _single_checksum(siren_ok, fake=True),
    "0009": _single_checksum(siret_ok, fake=True),
    "0192": _single_checksum(no_ok, fake=False),
    "0151": _single_checksum(abn_ok, fake=False),
    "0088": _single_checksum(gs1_ok, fake=False),
    "0007": _single_checksum(se_ok, fake=False),
}


def tally(c, pid):
    """Count one participant identifier into the census."""
    if not pid.startswith("iso6523-actorid-upis::"):
        return
    scheme, _, v = pid[22:].partition(":")
    st = c.stats[scheme]
    st["n"] += 1
    low = v.lower()
    if "test" in low:
        st["has_test"] += 1
        c.ex(scheme + ":test", v)
    if scheme in HANDLERS:
        HANDLERS[scheme](c, st, v, low)
    elif scheme in SINGLE:
        SINGLE[scheme](c, st, v, low, scheme)


def summary(c):
    return {
        "stats": {k: dict(v) for k, v in c.stats.items() if k in REPORTED},
        "be": {
            "0208_valid_unique": len(c.be0208),
            "9925_valid_unique": len(c.be9925),
            "both": len(c.be0208 & c.be9925),
            "only_0208": len(c.be0208 - c.be9925),
            "only_9925": len(c.be9925 - c.be0208),
        },
        "fr0225": {
            "unique_siren": len(c.fr0225_siren),
            "addresses_per_siren_top": c.fr0225_siren.most_common(10),
            "suffix_top": c.fr0225_suffix.most_common(12),
        },
        "examples": c.examples,
    }


def _write(path, text):
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


def main():
    c = Census()
    with open(sys.argv[1], encoding="latin-1") as f:
        next(f)
        for line in f:
            tally(c, line.strip().strip('"'))
    _write(sys.argv[2], json.dumps(summary(c), ensure_ascii=False, indent=1))
    _write(sys.argv[3], "\n".join(sorted(c.be0208 - c.be9925)))
    _write(sys.argv[4], "\n".join(sorted(c.be9925 - c.be0208)))
    _write(
        sys.argv[5],
        "\n".join(s for s in c.fr0225_siren if siren_ok(s) and not FAKE.match(s)),
    )


if __name__ == "__main__":
    main()
