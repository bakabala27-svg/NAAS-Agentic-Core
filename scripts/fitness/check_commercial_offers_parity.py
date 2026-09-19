#!/usr/bin/env python3
"""بوّابة مطابقة وثائق العروض مع الكتالوج — لا سُلَّمٌ ثانٍ للحقيقة التجارية (W-13 → ADR-017).

**لماذا هذه البوّابة موجودة:**

`docs/commercial/SOVEREIGN_KNOWLEDGE_REVENUE_MAP.md` §5.3 شخّص العطب وسمّى شرطَ إغلاقه
نصّاً: «تفعيل بوابة `check_commercial_offers_parity.py` تفرض مطابقة وثائق العروض مع
الكتالوج». البوّابة **لم تُكتب قطّ**، فبقي التشخيصُ يقرأ حراسةً وهو ليس حراسةً — صنف
ISS-186/149 الذي حارَسَه هذا المستودع في كل مكانٍ آخر (قانونٌ يُسمّي فارضاً محذوفاً).

والعطبُ الموصوف حقيقيٌّ وقابلٌ للقياس: خمسةُ ملفات `*_OFFER.md` في `docs/commercial/`
تصف عروضاً مُسعَّرةً قابلةً للبيع، و`OFFER_CATALOG.json` يصف خطّاتٍ تجاريةً أُخرى
بحالاتِ نضجٍ من `readiness_states`. لا رابطَ بين السطحين: لا يعرف أيُّهما عن الآخر،
فلا يعرف قارئٌ خارجي (مشتَرٍ، شريك، وكيلُ مبيعات) أيَّ السجِلَّين يُصدِّق. وحين تُكتب
حالةُ نضجٍ في نثرِ وثيقةٍ لا في الكتالوج، يصبح لكلّ عرضٍ سلَّمان — وهو بالضبط ما
أنتج ISS-139 وD-186 في طبقةٍ أخرى من هذا المستودع.

**ما تفرضه (ولا تخترع قاعدةً جديدة):**

1. **صلةٌ مُعلَنة لكلّ وثيقة عرض:** كلُّ `docs/commercial/*_OFFER.md` يحمل علامةً واحدة
   `<!-- catalog-relationship: … -->` تُصَرِّح صلتَه بالكتالوج الكنسي: إمّا
   `line:<offer-id>` أو `OUTSIDE_CATALOG` **مع سببٍ منطوق**. الصلةُ الصامتة
   تُقرأ «خارج الكتالوج» لدى قارئٍ و«داخله» لدى قارئٍ آخر — فالحالتان تُكتبان.
2. **المرجعُ موجود:** كلُّ `line:<id>` يجب أن يكون سطراً في `OFFER_CATALOG.json`.
   خريطةُ سلطةٍ تكذب أسوأ من غيابها (ISS-149).
3. **سُلَّمٌ واحد:** لا تُعلَن حالةُ نضجٍ في فقرةٍ تسمّي عرضاً من الكتالوج إلا بمساواة
   حالةِ الكتالوج. الحالةُ تعيش في `status` وتُشار إليها الوثيقة، لا تنسخها.
4. **العلامةُ وحيدةٌ لا مكرَّرة:** علامتان لوثيقةٍ واحدة = حالتان، والبوابة ترفض
   الاختيار نيابةً عن الكاتب.

⛔ **ما لا تفعله:** لا تُحصي عددَ أسطر الكتالوج ولا تُثبِّت قائمة العروض — الكتالوج
مفتوحُ العضوية (D-296 ألغت حصرَ السبعة: الشرطُ الوحيد سوقيّ)، والعددُ والقائمة
يعيشان في `OFFER_CATALOG.json` وحده. ولا تُلزم كلَّ وثيقةٍ في
`docs/commercial/` بأن تكون عرضاً: معيارُ الوثيقةِ-العرض هو اسمُها `*_OFFER.md`، وهو
اختيارٌ صريحٌ لا استنتاجٌ بالذكاء.

تُشغَّل ضمن وظيفة `guardrails` في `.github/workflows/ci.yml`.
Exit 0 = نظيف · 1 = انتهاك.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

COMMERCIAL_DIR = "docs/commercial"
CATALOG_REL = "docs/commercial/OFFER_CATALOG.json"
OFFER_DOC_GLOB = "*_OFFER.md"

#: `line:<id>` أو `OUTSIDE_CATALOG` مع سببٍ منطوق — لا صلةً صامتة.
_MARKER = re.compile(
    r"<!--\s*catalog-relationship:\s*(?P<kind>[A-Za-z_:-]+)\s*(?:\|\s*reason:\s*(?P<reason>[^>]*))?-->"
)
_OUTSIDE = "OUTSIDE_CATALOG"
_READINESS = re.compile(r"\b(PROPOSED|DISCOVERY|OFFER_READY|PILOT|PAID_PROOF|REPEATABLE)\b")

_FAILURES: list[str] = []


def fail(message: str) -> None:
    _FAILURES.append(message)
    print(f"❌ {message}")


def passed(message: str) -> None:
    print(f"✅ {message}")


def _load_catalog(root: Path) -> dict[str, dict]:
    path = root / CATALOG_REL
    if not path.is_file():
        fail(f"الكتالوج مفقود: {CATALOG_REL}")
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError, OSError) as exc:
        fail(f"لا يمكن تحليل {CATALOG_REL}: {exc}")
        return {}
    offers = payload.get("offers") if isinstance(payload, dict) else None
    if not isinstance(offers, list) or not offers:
        fail("`offers` مفقودٌ أو فارغ في الكتالوج — مطابقةٌ بلا طرفٍ ثانٍ")
        return {}
    return {
        str(row.get("id")): str(row.get("status") or "")
        for row in offers
        if isinstance(row, dict) and row.get("id")
    }


def _parse_markers(rel: str, text: str) -> list[tuple[str, str]]:
    found = [(m.group("kind"), (m.group("reason") or "").strip()) for m in _MARKER.finditer(text)]
    if not found:
        fail(
            f"{rel}: لا صلةَ مُعلَنة بالكتالوج — أضيف علامةً واحدة "
            "`<!-- catalog-relationship: line:<id> | reason: … -->` أو "
            f"`{_OUTSIDE}` بسببٍ منطوق"
        )
        return []
    if len(found) > 1:
        fail(f"{rel}: {len(found)} علاماتِ صلةٍ لوثيقةٍ واحدة — حالةٌ واحدة لا اثنتان")
        return []
    kind, reason = found[0]
    if not reason:
        fail(
            f"{rel}: صلةٌ بالكتالوج بلا سببٍ منطوق (`| reason: …`) — الخانةُ الفارغة "
            "تُقرأ نجاحاً (D-206 L11)"
        )
    return [(kind, reason)]


def _check_status_paraphrases(rel: str, text: str, catalog: dict[str, str]) -> None:
    for paragraph in text.split("\n\n"):
        named = [offer_id for offer_id in catalog if offer_id in paragraph]
        if not named:
            continue
        declared = set(_READINESS.findall(paragraph))
        expected = {catalog[offer_id] for offer_id in named}
        for state in sorted(declared - expected):
            fail(
                f"{rel}: فقرةٌ تسمّي {sorted(named)} وتعلن الحالة `{state}` بينما "
                f"الكتالوج يقول `{sorted(expected)[0]}` — انسخ الحالة إلى الكتالوج بقرار، "
                "لا في نثر الوثيقة"
            )


def _check_one_doc(path: Path, root: Path, catalog: dict[str, str]) -> None:
    rel = str(path.relative_to(root))
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError) as exc:
        fail(f"{rel}: لا تُقرأ الوثيقة ({exc}) — فحصٌ لم يقع لا يُشهَد له بالنظافة (D-208 §6)")
        return
    markers = _parse_markers(rel, text)
    for kind, _reason in markers:
        if kind == _OUTSIDE:
            continue
        offer_id = kind.removeprefix("line:")
        if not kind.startswith("line:") or offer_id not in catalog:
            fail(
                f"{rel}: الصلة المعلَنة `{kind}` لا تُطابق سطراً في الكتالوج — "
                "خريطةُ سلطةٍ تكذب أسوأ من غيابها"
            )
    _check_status_paraphrases(rel, text, catalog)


def main(argv: list[str] | None = None) -> int:
    """نقطةُ الدخول؛ `--root` ثقبُ اختبارٍ يقيس نسخةً من الشجرة بلا مسّها."""
    args = list(sys.argv[1:] if argv is None else argv)
    root = REPO_ROOT
    if "--root" in args:
        index = args.index("--root")
        if index + 1 >= len(args):
            fail("`--root` يحتاج مساراً")
            return 1
        root = Path(args[index + 1]).resolve()
    catalog = _load_catalog(root)
    if not catalog:
        return 1
    docs = sorted((root / COMMERCIAL_DIR).glob(OFFER_DOC_GLOB))
    if not docs:
        fail(f"لا وثائق عروض تحت `{COMMERCIAL_DIR}/{OFFER_DOC_GLOB}` — لا معنى لمطابقةٍ بلا وثائق")
        return 1
    for path in docs:
        _check_one_doc(path, root, catalog)
    if _FAILURES:
        print(
            f"\n❌ مطابقة العروض (W-13): {len(_FAILURES)} انتهاكاً — سطران للحقيقة التجارية سطران يكذبان."
        )
        return 1
    passed(
        f"صلةٌ مُعلَنة وحالةٌ واحدة لكلّ وثيقة عرض ({len(docs)} وثائق · {len(catalog)} سطراً في الكتالوج)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
