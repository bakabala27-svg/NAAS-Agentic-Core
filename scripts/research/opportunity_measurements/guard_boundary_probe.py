"""Replicates LLM Guard BanSubstrings matching (MatchType.STR / MatchType.WORD, case_sensitive=False)
on neutral canary words, Arabic vs French. stdlib only, no network, no third-party code executed.

Matching logic copied from protectai/llm-guard llm_guard/input_scanners/ban_substrings.py (read 2026-10-26):
  STR : substring in text
  WORD: re.search(r"\\b" + re.escape(substring) + r"\\b", text) is not None
  case_sensitive False -> substring.lower(), text.lower(); no Unicode normalization.
"""

import json
import re
import sys


def match(kind: str, banned: str, text: str) -> bool:
    banned, text = banned.lower(), text.lower()
    if kind == "STR":
        return banned in text
    return re.search(r"\b" + re.escape(banned) + r"\b", text) is not None


# Neutral canary terms only (no harmful words). Each surface form is a regular,
# everyday spelling of the SAME word in context.
CASES = {
    "ar": {
        "banned": "كتاب",
        "forms": {
            "bare": "هذا كتاب جديد",
            "def_article ال": "قرأت الكتاب أمس",
            "conj+article وال": "والكتاب على الطاولة",
            "prep+article بال": "أمسكته بالكتاب",
            "prep لل": "عدت للكتاب",
            "conj ف+ال": "فالكتاب مفيد",
            "enclitic كتابك": "أين كتابك",
            "enclitic كتابنا": "هذا كتابنا",
            "tatweel كـتـاب": "هذا كـتـاب",
            "diacritics كِتَاب": "هذا كِتَابٌ",
            "presentation forms": "هذا ﻛﺘﺎﺏ",
        },
    },
    "ar_tamarbuta": {
        "banned": "رسالة",
        "forms": {
            "bare": "وصلت رسالة",
            "def_article ال": "قرأت الرسالة",
            "enclitic (ة→ت) رسالتك": "وصلت رسالتك",
            "ha-for-ta spelling رساله": "وصلت رساله",
        },
    },
    "ar_alef_ya": {
        "banned": "مستشفى",
        "forms": {
            "bare": "ذهبت إلى مستشفى",
            "def_article ال": "ذهبت إلى المستشفى",
            "ya-for-alif-maqsura مستشفي": "ذهبت إلى مستشفي",
        },
    },
    "fr": {
        "banned": "ami",
        "forms": {
            "bare": "un ami fidèle",
            "capitalised": "Ami fidèle",
            "upper": "AMI FIDÈLE",
            "elided article l'": "l'ami est venu",
            "elided preposition d'": "le chien d'ami",
            "plural amis": "des amis fidèles",
        },
    },
    "fr_accent": {
        "banned": "élève",
        "forms": {
            "bare": "un élève sérieux",
            "elided article l'": "l'élève est là",
            "capitalised": "Élève sérieux",
            "upper": "ÉLÈVE SÉRIEUX",
            "accents dropped (informal)": "un eleve serieux",
        },
    },
}

rows = []
for lang, spec in CASES.items():
    for form, text in spec["forms"].items():
        rows.append(
            {
                "lang": lang,
                "banned": spec["banned"],
                "form": form,
                "STR": match("STR", spec["banned"], text),
                "WORD": match("WORD", spec["banned"], text),
            }
        )


def rate(lang_prefix: str, kind: str) -> str:
    sel = [r for r in rows if r["lang"].startswith(lang_prefix)]
    hit = sum(r[kind] for r in sel)
    return f"{hit}/{len(sel)}"


for r in rows:
    print(f"{r['lang']:13s} {r['form']:28s} STR={r['STR']!s:5s} WORD={r['WORD']}")
print(
    "summary  ar STR",
    rate("ar", "STR"),
    " ar WORD",
    rate("ar", "WORD"),
    "| fr STR",
    rate("fr", "STR"),
    " fr WORD",
    rate("fr", "WORD"),
)
print("python", sys.version.split()[0])
with open(sys.argv[1], "w", encoding="utf-8") as fh:
    json.dump(rows, fh, ensure_ascii=False, indent=1)
