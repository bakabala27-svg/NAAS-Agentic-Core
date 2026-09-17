#!/usr/bin/env python3
"""بوّابة براءة الحقوق — لا يُبنى عرضٌ مُباعٌ على أصلٍ لا يجوز بيعُه (ADR-017).

**لماذا هذه البوّابة موجودة:**

قياسٌ على الشجرة في 2026-09-16: `docs/commercial/OFFER_CATALOG.json` يحمل سبعةَ عروضٍ
بالعملة الصعبة، وسبعةَ `backbone_refs` لكلّ عرض، ولا **حقلَ ترخيصٍ واحداً** في
`docs/governance/SOURCE_ADOPTION_MATRIX.json` (خمسةٌ وسبعون مصدراً) ولا في كتالوج
العروض. العمود الفقري المرجعي يصف الغرض والتطبيق والفارض — ولا يسأل سؤالاً واحداً:
**هل يملك هذا الطرفُ الثالث حقَّ ما سنبيعه نحن؟**

والجوابُ عند القراءة من المصدر الأصلي ليس ما توقّعه أحد:

* `ByteByteGoHq/system-design-101` مُرخَّص **CC BY-NC-ND**: لا تجارةَ ولا اشتقاق.
* `nilbuild/developer-roadmap` ينصّ ملفّ `license` فيه على الاستخدام **الشخصي** فقط
  ويمنع النشر صراحةً — وهو مرجعٌ مُسمّى في عرضٍ تجاريّ.
* `jwasham/coding-interview-university` **CC BY-SA**: كلُّ مشتَقٍّ يُرخَّص بمثله، وهو
  يتضارب مع نصٍّ مملوكٍ مُباع.
* تسعةُ مصادر بلا ملفّ ترخيص إطلاقاً ⇒ الحقوق محفوظة ضمناً بحكم الافتتاح القانوني،
  و«موجودٌ على GitHub» ليس إذناً.
* مصدرٌ واحد يستضيف كتاباً تجارياً مقرصناً، واثنان لا يُحلّان على GitHub أصلاً.
* منشورٌ تجاريٌّ بحجمه الكامل (`Introduction to Agents.pdf`) مُودَعٌ في شجرة MIT بلا
  إذنٍ مكتوب، ويُذكر في المصفوفة واقعةً لمصدرَين غير مصنَّفَين.

هذا صنفُ العطب الذي حارسُوه غائبون: لا يُرى إلا حين يقرأه طرفٌ خارجي — أي **يومَ
التفاوض على أول عقد**. والمستودع الذي بنى كلَّ حراسته على جملة «قاعدةٌ بلا بوّابة
تنحرف بصمت» (D-188/D-207) كان سيترك بابَ البيع مفتوحاً على ملكيةٍ لا يملكها.

**ما تفرضه (لا غيرُه):**

1. **البراءة مُسجَّلةٌ لكلّ مصدر**: سجلٌّ واحدٌ لكلّ مسار في مصفوفة المصادر، بالاتجاهين
   (لا مصدرٌ بلا سجل، ولا سجلٌّ لمصدرٍ لا وجود له في المصفوفة).
2. **القاموس مُعلَنٌ في السجلّ نفسه**: القيم القانونية تعيش في `vocabulary` داخل
   الملفّ المُدقَّق، فلا تتفرّق لائحتان لمفهومٍ واحد (D-192).
3. **الادّعاء مؤرَّخٌ بمصدر قراءته**: لا `ALLOWED` بلا `method` يسمّي كيف قُرئت الرخصة،
   ولا تاريخٌ في المستقبل، ولا ادّعاءٌ بعد انقضاء `policy.review_window_days`.
4. **لا براءةٍ بقراءةٍ ناقصة**: رخصةٌ لا يُصنّفها GitHub (`NOASSERTION`) أو بلا ملفّ
   ترخيص لا تُعلَن `ALLOWED`؛ والإسنادُ إن لزم يُعلَن بحقلٍ لا بنثرٍ في الوثائق، ولا
   تُترك الخانةُ فارغةً تُقرأ نجاحاً.
5. **الترقيةُ ممنوعةٌ على محجوب**: أيّ عرضٍ في حالةٍ من `policy.promotion_blocked_at`
   وسجلُّه يحمل حجوباً ⇒ CI أحمر. والاتجاه الآخر أيضاً: سجلٌّ بلا حجوب وبنتيجته
   `BLOCKED_BY_UPSTREAM_LICENSE` = سجلٌّ يكذب على نفسه.
6. **تبعياتُ الإنتاج مُبرَّأةٌ بالاسم**: قائمةُ الحزم في السجلّ = قائمةُ التثبيت في
   `requirements-prod.txt` حرفيّاً، والاتجاهان محروسان؛ ورخصةٌ قويةُ الاشتقاق لا
   تُعلَن مقبولةً على عنقود عميل.
7. **الثنائيّ المُودَع مُصرَّحٌ عنه**: كلّ ملفٍّ ثنائيٍّ مُتتبَّع في الشجرة له سجلُّ
   توزيع، وكلُّ سجلٍّ يشير إلى ملفٍّ موجود؛ وما ليس عملَ المشروع يحمل `remediation_ar`.
8. **الفجوة تُعلَن ولا تُترَك فارغة**: كلّ حِجابٍ (عرضٌ أو ملفٌّ ثنائيٌّ أو استشهادٌ
   معلَّق) مغطًّى ببطاقةِ رصدٍ باسم صاحبه وإجراءٍ منطوق — الخانةُ الفارغة تُقرأ نجاحاً
   (`.memory/aesthetics_of_absence.md`).

⛔ **ما لا تدّعيه:** لا تثبت أن نصّاً كُتب في هذا المستودع أصليٌّ — لا تعرف ذلك ولا
تُدَّعى. ولا تفحص رخصَ تبعيات التطوير والاختبار (لا تُوزَّع)، ولا تعيد قياسَ الرخص
بنفسها: القياسُ إجراءٌ موثَّقٌ في `policy.refresh_ar` ينفّذه انسانٌ أو وكيلٌ بصلاحية
شبكة، والبوّابةُ ترفضُ الأقدمَ من نافذة المراجعة.

تُشغَّل ضمن وظيفة `guardrails` في `.github/workflows/ci.yml`.
Exit 0 = نظيف · 1 = انتهاك.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

REGISTER_REL = "docs/governance/ASSET_LICENSE_CLEARANCE.json"
MATRIX_REL = "docs/governance/SOURCE_ADOPTION_MATRIX.json"
OFFERS_REL = "docs/commercial/OFFER_CATALOG.json"
PROD_REQUIREMENTS_REL = "requirements-prod.txt"

#: الحقولُ التي يجب أن يُعلن السجلّ قاموسَها له (لا لائحةٌ ثانية داخل البوّابة).
#: الكتلُ المقيسة — عدّاداتُها تُشتَقّ وقت التشغيل ولا تُخبَّأ في السجلّ (D-192).
REGISTER_BLOCKS = (
    "upstream_sources",
    "production_dependencies",
    "tracked_binary_artifacts",
    "offer_clearance",
    "findings_ar",
)

REQUIRED_VOCABULARY = (
    "commercial_use",
    "method",
    "on_premise_distribution",
    "offer_clearance",
    "finding_kind",
    "finding_severity",
)

#: وسائلُ القراءة التي تُبرّر إعلانَ براءة (ما عداها استنتاجٌ لا دليلَ عليه).
PROOF_METHODS = frozenset({"github-api-license", "upstream-license-file-read"})
CLEARED_USES = frozenset({"ALLOWED", "ALLOWED_WITH_ATTRIBUTION"})
STRONG_COPYLEFT = frozenset(
    {"AGPL-3.0", "AGPL-3.0-only", "GPL-3.0", "GPL-3.0-only", "GPL-2.0-only"}
)
WEAK_COPYLEFT = frozenset({"LGPL-2.1-or-later", "LGPL-3.0-or-later", "LGPL-2.1-only"})

#: الرخصُ التي لا تُقرأ أبداً `NOASSERTION` (الملفّ موجودٌ لكنّ GitHub لا يصنّفه).
_UNCLASSIFIED_LICENSES = frozenset({"CUSTOM", "UNKNOWN", "UNRESOLVED"})

_SLUG = re.compile(r"github\.com/([^/]+)/([^/#?\s]+)")
_ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_BINARY_SUFFIX = re.compile(
    r"\.(pdf|epub|mobi|azw3|docx|pptx|xlsx|zip|tar|gz|tgz|bz2|7z|rar|whl|jar|exe|dll|so|dylib|"
    r"mp4|mov|avi|mkv|webm|mp3|wav|ogg|flac|png|jpe?g|webp|gif|bmp|ico|tiff|svgz|woff2?|ttf|otf)$",
    re.IGNORECASE,
)

_FAILURES: list[str] = []


def fail(message: str) -> None:
    """يسجّل الفشلَ ويطبعه — والطباعةُ وحدَها ليست تسجيلاً (D-208 §6)."""
    _FAILURES.append(message)
    print(f"❌ {message}")


def passed(message: str) -> None:
    print(f"✅ {message}")


def load_json(relative: str, root: Path) -> dict | None:
    """يقرأ JSON أو يُسجّل فشلاً — ⛔ ملفٌّ مفقودٌ أو غير قابل للتحليل ليس «نظيفاً»."""
    path = root / relative
    if not path.is_file():
        fail(f"ملفٌّ مفقود: {relative} — بوّابةٌ فقدت مصدرها تُبرّئ شجرةً لم تفحصها")
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError, OSError) as exc:
        fail(f"لا يمكن تحليل {relative}: {exc}")
        return None
    if not isinstance(payload, dict):
        fail(f"{relative} جذرُه يجب أن يكون كائناً JSON")
        return None
    return payload


def recorded_slug(url: str) -> str:
    """`owner/name` من رابط GitHub، بحروفٍ صغيرة، بلا `.git` ولا ممراً."""
    match = _SLUG.search(url or "")
    if not match:
        return ""
    return f"{match.group(1)}/{match.group(2).removesuffix('.git')}".lower()


def iso_day(value: object) -> date | None:
    """`date` من `YYYY-MM-DD`، أو `None` حين لا يكون التاريخُ بصيغةٍ قابلة للتحقّق."""
    text = str(value or "")
    if not _ISO_DATE.fullmatch(text):
        return None
    try:
        year, month, day = (int(part) for part in text.split("-"))
        return date(year, month, day)
    except ValueError:
        return None


def rows_of(register: dict, key: str) -> list[dict]:
    rows = register.get(key)
    if not isinstance(rows, list) or not rows:
        fail(f"`{key}` مفقودٌ أو فارغ في السجلّ — الغيابُ يُعلَن ولا يُصمت عنه (D-206 L11)")
        return []
    return [row for row in rows if isinstance(row, dict)]


# ─────────────────────────────────────────────────────────────────────────────
# 1 · القاموس
# ─────────────────────────────────────────────────────────────────────────────


def check_vocabulary(register: dict) -> None:
    vocabulary = register.get("vocabulary")
    if not isinstance(vocabulary, dict):
        fail("`vocabulary` مفقود — القيم القانونية تُعلَن في السجلّ نفسه، لا في البوّابة")
        return
    for field in REQUIRED_VOCABULARY:
        allowed = vocabulary.get(field)
        if not isinstance(allowed, list) or not allowed:
            fail(f"`vocabulary.{field}` مفقودٌ أو فارغ")
    if _FAILURES:
        return
    _check_row_values(register, vocabulary)


def _row_fields() -> tuple[tuple[str, str, str], ...]:
    return (
        ("upstream_sources", "commercial_use", "commercial_use"),
        ("upstream_sources", "method", "method"),
        ("production_dependencies", "on_premise_distribution", "on_premise_distribution"),
        ("offer_clearance", "clearance", "offer_clearance"),
        ("findings_ar", "kind", "finding_kind"),
        ("findings_ar", "severity", "finding_severity"),
    )


def _check_row_values(register: dict, vocabulary: dict) -> None:
    offenders: list[str] = []
    for block, field, vocab_key in _row_fields():
        allowed = {str(item) for item in vocabulary.get(vocab_key, [])}
        for row in rows_of(register, block):
            value = str(row.get(field) or "")
            if not value or value not in allowed:
                offenders.append(f"{block}.{field}={value!r}")
    if offenders:
        fail(f"قيمٌ خارج القاموس المُعلَن ({len(offenders)}): {sorted(offenders)[:6]}")
        return
    passed("قاموسُ البراءة مفروضٌ على كل سجلّ — وقيمةٌ فارغةٌ قيمةٌ خارج القاموس")


# ─────────────────────────────────────────────────────────────────────────────
# 2 · الادّعاء المؤرَّخ
# ─────────────────────────────────────────────────────────────────────────────


def _check_row_dates(label: str, rows: list[dict], today: date, window: int) -> None:
    stale: list[str] = []
    undated: list[str] = []
    future: list[str] = []
    for row in rows:
        day = iso_day(row.get("reviewed_on") or row.get("verified_on"))
        if day is None:
            undated.append(
                str(row.get("upstream_repo") or row.get("package") or row.get("path") or "?")
            )
            continue
        if day > today:
            future.append(str(row.get("upstream_repo") or row.get("package") or "?"))
        elif (today - day).days > window:
            stale.append(str(row.get("upstream_repo") or row.get("package") or "?"))
    if undated:
        fail(f"{label}: سجلٌّ بلا `reviewed_on` صالح ⇒ ادّعاءٌ بلا تاريخ قراءة: {undated[:6]}")
    if future:
        fail(f"{label}: تاريخٌ في المستقبل لا يجوز أن يكون دليلاً: {future[:6]}")
    if stale:
        fail(
            f"{label}: قياسٌ أقدمُ من نافذة المراجعة ({window} يوماً): {stale[:6]} — "
            "أعِد القياسَ بـ`policy.refresh_ar` وحدّث التواريخ، ولا تُبقِ ادّعاءً قديماً أخضر"
        )


def _review_window(register: dict) -> int:
    """نافذةُ المراجعة من `policy`؛ القيمةُ الخارجةُ عن المدى تُسجَّل ولا تُبتَلَع."""
    policy = register.get("policy")
    raw = policy.get("review_window_days") if isinstance(policy, dict) else None
    if not isinstance(raw, int) or isinstance(raw, bool) or not 0 < raw <= 730:
        fail(
            f"`policy.review_window_days` يجب أن يكون عدداً صحيحاً بين 1 و730، والمقروء "
            f"{raw!r} — ادّعاءٌ مؤرَّخٌ بلا نافذةٍ معروفة لا يُقرأ أخضر"
        )
        return 365
    return raw


def check_dates(register: dict, today: date) -> None:
    window = _review_window(register)
    for label, key in (
        ("المصادر الخارجية", "upstream_sources"),
        ("تبعيات الإنتاج", "production_dependencies"),
        ("براءة العروض", "offer_clearance"),
    ):
        _check_row_dates(label, rows_of(register, key), today, window)
    if not _FAILURES:
        passed(f"كلُّ ادّعاءِ براءةٍ مُؤرَّخٌ داخل نافذة المراجعة ({window} يوماً) وبوسيلةٍ مسجَّلة")


# ─────────────────────────────────────────────────────────────────────────────
# 3 · التغطية بالاتجاهين مع مصفوفة المصادر
# ─────────────────────────────────────────────────────────────────────────────


def _matrix_slugs(matrix: dict) -> set[str]:
    sources = matrix.get("sources")
    if not isinstance(sources, list) or not sources:
        fail("`sources` مفقودٌ أو فارغ في `SOURCE_ADOPTION_MATRIX.json`")
        return set()
    return {
        slug
        for row in sources
        if isinstance(row, dict) and (slug := recorded_slug(str(row.get("url") or "")))
    }


def check_matrix_coverage(register: dict, matrix: dict) -> None:
    expected = _matrix_slugs(matrix)
    recorded = {
        str(row.get("recorded_repo") or "").lower() for row in rows_of(register, "upstream_sources")
    }
    if missing := sorted(expected - recorded):
        fail(f"مصادرُ في المصفوفة بلا سجلّ براءة ({len(missing)}): {missing[:6]}")
    if ghosts := sorted(recorded - expected - {""}):
        fail(f"سجلاتُ براءةٍ لمصدرٍ ليس في المصفوفة ({len(ghosts)}): {ghosts[:6]}")
    if not _FAILURES:
        passed(f"براءةٌ مسجَّلةٌ لكلّ مصدرٍ في المصفوفة بالاتجاهين ({len(expected)} مساراً)")


# ─────────────────────────────────────────────────────────────────────────────
# 4 · لا براءةَ بقراءةٍ ناقصة
# ─────────────────────────────────────────────────────────────────────────────


def _reject_uncleared(row: dict, problems: list[str]) -> None:
    license_name = str(row.get("upstream_license") or "")
    use = str(row.get("commercial_use") or "")
    repo = str(row.get("upstream_repo") or "?")
    if use in CLEARED_USES and str(row.get("method") or "") not in PROOF_METHODS:
        problems.append(f"{repo}: براءةٌ معلَنةٌ بلا قراءة رخصة (`method={row.get('method')!r}`)")
    if not license_name and use in CLEARED_USES:
        problems.append(f"{repo}: لا ملفّ ترخيص في المصدر ⇒ لا يجوز إعلانُ `ALLOWED`")
    if license_name.upper() in _UNCLASSIFIED_LICENSES and use in CLEARED_USES:
        problems.append(f"{repo}: رخصةٌ غير مصنَّفة ({license_name}) لا تُعلَن مُبرَّأة")
    if use == "ALLOWED_WITH_ATTRIBUTION" and row.get("attribution_required") is not True:
        problems.append(f"{repo}: إسنادٌ لازمٌ في النثر وحده — الحقلُ `attribution_required` مطلوب")


def check_license_honesty(register: dict) -> None:
    problems: list[str] = []
    for row in rows_of(register, "upstream_sources"):
        _reject_uncleared(row, problems)
    if problems:
        fail(
            f"براءةٌ مبنيةٌ على قراءةٍ ناقصة ({len(problems)}):\n   - " + "\n   - ".join(problems[:8])
        )
        return
    passed("كلُّ براءةٍ مُعلَنةٍ مبنيةٌ على قراءة رخصةٍ مصنَّفة، والإسنادُ معلنٌ بحقلٍ لا بنثر")


# ─────────────────────────────────────────────────────────────────────────────
# 5 · الترقية ممنوعةٌ على محجوب
# ─────────────────────────────────────────────────────────────────────────────


def _offer_rows(register: dict) -> dict[str, dict]:
    rows = rows_of(register, "offer_clearance")
    by_id: dict[str, dict] = {}
    for row in rows:
        offer_id = str(row.get("offer_id") or "")
        if offer_id in by_id:
            fail(f"سجلّان لبراءة العرض نفسه: {offer_id} — حالةٌ واحدة لا اثنتان")
        by_id[offer_id] = row
    return by_id


def _catalog_ids(offers: dict) -> set[str]:
    catalog = offers.get("offers")
    if not isinstance(catalog, list) or not catalog:
        fail("`offers` مفقودٌ أو فارغ في `OFFER_CATALOG.json`")
        return set()
    return {str(row.get("id")) for row in catalog if isinstance(row, dict)}


def _promotion_states(register: dict) -> set[str]:
    policy = register.get("policy")
    states = policy.get("promotion_blocked_at") if isinstance(policy, dict) else None
    if not isinstance(states, list) or not states:
        fail("`policy.promotion_blocked_at` مفقودٌ أو فارغ — قاعدةُ الترقية بلا مرمى")
        return set()
    return {str(state) for state in states}


def check_offer_promotion(register: dict, offers: dict, catalog_ids: set[str]) -> None:
    by_id = _offer_rows(register)
    if missing := sorted(catalog_ids - set(by_id)):
        fail(f"عروضٌ في الكتالوج بلا سجلّ براءة ({len(missing)}): {missing}")
    if ghosts := sorted(set(by_id) - catalog_ids - {""}):
        fail(f"سجلّاتُ براءةٍ لعرضٍ ليس في الكتالوج ({len(ghosts)}): {ghosts}")
    blocked_states = _promotion_states(register)
    violations: list[str] = []
    for offer_id, row in sorted(by_id.items()):
        blockers = row.get("blockers")
        clearance = str(row.get("clearance") or "")
        if not isinstance(blockers, list):
            violations.append(f"{offer_id}: `blockers` يجب أن يكون قائمة")
            continue
        honest = (not blockers and clearance == "CLEARED") or (blockers and clearance != "CLEARED")
        if not honest:
            violations.append(
                f"{offer_id}: الحالة `{clearance}` لا تُطابق {len(blockers)} حِجاباً مسجَّلاً"
            )
        if row.get("offer_status") in blocked_states and blockers:
            violations.append(
                f"{offer_id}: مرقّى إلى `{row.get('offer_status')}` مع حجوبٍ مرخّص — "
                "لا يُباع أصلٌ لا يملكه البائع"
            )
    if violations:
        fail("براءةُ العروض: " + " · ".join(violations[:6]))
        return
    if not _FAILURES:
        blocked = sum(1 for row in by_id.values() if row.get("blockers"))
        passed(
            f"ترقيةُ العروض محروسَةٌ بالبراءة ({len(by_id)} عرضاً، {blocked} محجوبٌ بترخيصٍ ومُعلَنٌ كذلك)"
        )


# ─────────────────────────────────────────────────────────────────────────────
# 6 · تبعيات الإنتاج
# ─────────────────────────────────────────────────────────────────────────────


def _pinned_production(root: Path) -> set[str]:
    path = root / PROD_REQUIREMENTS_REL
    if not path.is_file():
        fail(f"ملفّ تبعيات الإنتاج مفقود: {PROD_REQUIREMENTS_REL}")
        return set()
    pinned: set[str] = set()
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.split("#", 1)[0].strip()
        match = re.match(r"^([A-Za-z0-9_.-]+)\s*(?:==|>=|~=)", line)
        if match:
            pinned.add(match.group(1).lower())
    return pinned


def _dependency_row_issues(row: dict) -> list[str]:
    issues: list[str] = []
    license_name = str(row.get("license") or "")
    distribution = str(row.get("on_premise_distribution") or "")
    name = str(row.get("package") or "?")
    if license_name in STRONG_COPYLEFT and distribution != "BLOCK_ON_PREMISE":
        issues.append(f"{name}: `{license_name}` لا تُعلَن `{distribution}` على عنقود عميل")
    if license_name in WEAK_COPYLEFT and distribution == "OK_BOTH":
        issues.append(f"{name}: `{license_name}` تُلزم إخطاراً/مصدراً عند التوزيع، فلا `OK_BOTH`")
    if distribution == "UNRESOLVED_DO_NOT_SHIP" and row.get("saas_ok") is not False:
        issues.append(f"{name}: رخصةٌ لم تُقرأ ⇒ `saas_ok` يجب أن تكون `false` لا صمتاً")
    if license_name in _UNCLASSIFIED_LICENSES and distribution == "OK_BOTH":
        issues.append(f"{name}: رخصةٌ غير مقروءةٍ لا تُبرَّأ للتوزيع")
    return issues


def check_dependencies(register: dict, root: Path) -> None:
    rows = rows_of(register, "production_dependencies")
    recorded = {str(row.get("package") or "").lower() for row in rows}
    expected = _pinned_production(root)
    if missing := sorted(expected - recorded):
        fail(f"تبعياتُ إنتاجٍ بلا سجلّ ترخيص ({len(missing)}): {missing[:8]}")
    if ghosts := sorted(recorded - expected - {""}):
        fail(f"سجلاتُ تبعياتٍ لا تُثبَّت في الإنتاج ({len(ghosts)}): {ghosts[:8]} — احذفها")
    issues = [issue for row in rows for issue in _dependency_row_issues(row)]
    if issues:
        fail("تبريرُ تبعياتٍ لا يُحتمل عند التوزيع:\n   - " + "\n   - ".join(issues[:8]))
        return
    if not _FAILURES:
        passed(f"ترخيصُ تبعيات الإنتاج مُبرَّأٌ بالاسم وباتّجاهَي التسليم ({len(expected)} حزمة)")


# ─────────────────────────────────────────────────────────────────────────────
# 7 · الموادّ الثنائية في الشجرة
# ─────────────────────────────────────────────────────────────────────────────


def _tracked_binaries(root: Path) -> set[str] | None:
    # قائمةُ وسائط ثابتةٌ بلا قشرةٍ ولا تدخلَ مستخدم (D-189 · `check_no_shell_true`).
    completed = subprocess.run(
        ["git", "-C", str(root), "ls-files"],
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        fail(f"لا يمكن سردُ الملفات المتتبَّعة (`git ls-files`): {completed.stderr.strip()[:120]}")
        return None
    return {
        path
        for path in completed.stdout.splitlines()
        if path.strip() and _BINARY_SUFFIX.search(path.strip())
    }


def check_tracked_binaries(register: dict, root: Path) -> None:
    rows = rows_of(register, "tracked_binary_artifacts")
    recorded = {str(row.get("path") or "") for row in rows}
    tracked = _tracked_binaries(root)
    if tracked is None:
        return
    if missing := sorted(tracked - recorded):
        fail(f"ملفاتٌ ثنائيةٌ متتبَّعةٌ بلا سجلّ توزيع ({len(missing)}): {missing[:6]}")
    if ghosts := sorted(recorded - tracked):
        fail(f"سجلاتُ توزيعٍ لملفاتٍ لم تعد في الشجرة ({len(ghosts)}): {ghosts[:6]} — احذفها")
    for row in rows:
        distribution = str(row.get("distribution") or "")
        if (
            distribution
            and distribution != "OWN_WORK_MIT"
            and not str(row.get("remediation_ar") or "").strip()
        ):
            fail(
                f"`{row.get('path')}`: توزيعٌ غيرُ مُبرَّأٍ بلا `remediation_ar` — الفجوةُ تُعلَن إجراءً لا صمتاً"
            )
    if not _FAILURES:
        passed(f"كلُّ ملفٍّ ثنائيٍّ في الشجرة له سجلُّ توزيع ({len(tracked)} أصلاً)")


# ─────────────────────────────────────────────────────────────────────────────
# 8 · الفجوة تُعلَن ولا تُترَك فارغة
# ─────────────────────────────────────────────────────────────────────────────


def _covered_ids(findings: list[dict], kind: str) -> set[str]:
    covered: set[str] = set()
    for row in findings:
        if str(row.get("kind") or "") != kind:
            continue
        covers = row.get("covers")
        if isinstance(covers, list):
            covered.update(str(item) for item in covers)
    return covered


def _finding_shape_issues(findings: list[dict]) -> list[str]:
    issues: list[str] = []
    seen: set[str] = set()
    for row in findings:
        finding_id = str(row.get("id") or "")
        if not finding_id:
            issues.append("بطاقةُ رصدٍ بلا `id`")
        elif finding_id in seen:
            issues.append(f"بطاقتان للرصد نفسه: {finding_id}")
        seen.add(finding_id)
        for field in ("title_ar", "finding_ar", "action_ar", "owner_ar", "kind", "severity"):
            if not str(row.get(field) or "").strip():
                issues.append(f"{finding_id or '?'}: خانةُ `{field}` فارغة")
        if iso_day(row.get("verified_on")) is None:
            issues.append(f"{finding_id or '?'}: `verified_on` ليس تاريخاً بصيغة YYYY-MM-DD")
    return issues


def _uncovered_target_issues(register: dict, findings: list[dict]) -> list[str]:
    issues: list[str] = []
    blocked_offers = {
        str(row.get("offer_id"))
        for row in rows_of(register, "offer_clearance")
        if row.get("blockers")
    }
    if uncovered_offers := sorted(blocked_offers - _covered_ids(findings, "offer_blocked")):
        issues.append(f"عروضٌ محجوبةٌ بلا بطاقة رصد (`offer_blocked`): {uncovered_offers}")
    blocked_files = {
        str(row.get("path"))
        for row in rows_of(register, "tracked_binary_artifacts")
        if str(row.get("distribution") or "") != "OWN_WORK_MIT"
    }
    if uncovered_files := sorted(blocked_files - _covered_ids(findings, "tracked_binary")):
        issues.append(f"ملفاتٌ غيرُ مُبرَّأةٍ بلا بطاقة رصد (`tracked_binary`): {uncovered_files}")
    dangling = {
        str(row.get("upstream_repo"))
        for row in rows_of(register, "upstream_sources")
        if str(row.get("commercial_use") or "") == "DANGLING_MUST_RELOCATE"
    }
    if dangling and not _covered_ids(findings, "dangling_citation"):
        issues.append(f"استشهاداتٌ معلَّقةٌ بلا بطاقة رصد (`dangling_citation`): {sorted(dangling)}")
    return issues


def check_findings(register: dict) -> None:
    findings = rows_of(register, "findings_ar")
    issues = _finding_shape_issues(findings)
    issues.extend(_uncovered_target_issues(register, findings))
    if issues:
        fail(f"سجلُّ الرصد غير مكتمل ({len(issues)}):\n   - " + "\n   - ".join(issues[:8]))
        return
    passed(f"كلُّ حجابٍ مغطًّى ببطاقةِ رصدٍ باسم صاحبها وإجراءٍ منطوق ({len(findings)} بطاقات)")


# ─────────────────────────────────────────────────────────────────────────────


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
    register = load_json(REGISTER_REL, root)
    matrix = load_json(MATRIX_REL, root)
    offers = load_json(OFFERS_REL, root)
    if register is None or matrix is None or offers is None:
        return 1
    today = date.today()
    check_vocabulary(register)
    check_dates(register, today)
    check_matrix_coverage(register, matrix)
    check_license_honesty(register)
    check_offer_promotion(register, offers, _catalog_ids(offers))
    check_dependencies(register, root)
    check_tracked_binaries(register, root)
    check_findings(register)
    if _FAILURES:
        print(
            f"\n❌ براءةُ الحقوق (ADR-017): {len(_FAILURES)} انتهاكاً — لا يُباع ما لا يملكُه البائع."
        )
        return 1
    counts = " · ".join(f"{block}={len(register.get(block) or [])}" for block in REGISTER_BLOCKS)
    passed(f"براءةُ الحقوق مفروضةٌ بعداداتٍ مشتقّةٍ وقت التشغيل: {counts}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
