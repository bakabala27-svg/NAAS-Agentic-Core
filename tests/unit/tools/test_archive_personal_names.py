"""الأرشيف التجاري لا يحمل أسماء أشخاص — يُفحَص كالكود.

**لماذا هذا الاختبار موجود.** قال المالك في 2026-10-27: «احفظ كلّ شيء في المستودع ما عدا
الأسماء فقط لأنها شخصية». الأرشيف في ``docs/archive/commercial/`` يحفظ ما يخصّ الفريق شخصياً
(التأشيرة والتمويل والسيارة)، فاسمٌ واحد يُنسخ من محادثةٍ يكشف صاحبه لكلّ من يقرأ المستودع.

والاختبار لا يكتب الأسماء التي يمنعها: يحفظ بصماتها (SHA-256 بملحٍ ثابت) ويقارن بها كلّ
كلمةٍ وكلّ كلمتين وكلّ ثلاث كلمات في الأرشيف بعد توحيد الكتابة. فلا يصير الاختبار نفسه
تسريباً. وإضافة اسمٍ جديد تعني إضافة بصمته فقط.

التوحيد: حروفٌ صغيرة، وحذف التشكيل والتطويل، والهمزات إلى ألف، والتاء المربوطة إلى هاء،
والألف المقصورة إلى ياء. فلا يفلت اسمٌ لأنّه كُتب بهمزةٍ أو بلا تشكيل.

الحالات السلبية تزرع اسماً تجريبياً لا يخصّ أحداً وتُبرهن أنّ الكاشف يحمرّ.

**التشغيل:** ``pytest tests/unit/tools/test_archive_personal_names.py -q``
"""

from __future__ import annotations

import hashlib
import re
from collections.abc import Iterable
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
ARCHIVE = REPO_ROOT / "docs/archive/commercial"
SCANNED_SUFFIXES = (".md", ".json", ".csv", ".html")
SALT = "archive-names-v1|"
WINDOW = 3

#: بصمات الأسماء الممنوعة (كلمة أو كلمتان أو ثلاث، بعد التوحيد). لا يُكتب الاسم هنا أبداً.
FORBIDDEN = frozenset(
    {
        "b9d4e8eb9ed9491a36e9bac3fde62dc6a28e2046b65626a462659761bc7e82fd",
        "86ffc79f79e2f6e4d1d2d0c3f89bc6d19a6eb7afd91145b5361360cf061fb259",
        "4a9273fdaa4492bc1cde589fb172f3be983ce703ae457e78ba5dd551efd64173",
        "1f0706a868d89232af95ff57c825955fc9187f332c461f94f964b9ace566a56a",
        "863f2fb73f9942226e99bd005316dbd44ffbb2d007ed74c2f056a75c76f9fc40",
        "3a3b1f95e1cb2bfd1c77ab8ed28c85cebfa218fe996a40938f56b91d91c5ba40",
        "aa1d67aeef4a55edd0df53336164075817c4e5ba39ecf5b0e7b93c015fcd9c3b",
        "130a57da869ba8e314d348cbb330903181b39b96ddc6b4768623b3f695e53291",
        "83b92d84e233fa607743d6ba699eba43ddd1735aa55b8e3bdd6c25e3a7ff8169",
        "940f0be7f3a7c21c2ee110ad1bfc9fc396a33ba1821b22d9c66b54ac9092121f",
        "57b337935747ed3578070c513fdb2e25fa68912064de163cc1381213d6c860ad",
        "aa72d123dc3d5ac9364a64cef3a591e07c38d066695d8227b39506bf43772042",
    }
)

_MARKS = re.compile("[ً-ْٰـ]")
_ALEFS = re.compile("[أإآٱ]")
_WORD = re.compile(r"\w+")


def _normalise(text: str) -> str:
    text = _ALEFS.sub("ا", _MARKS.sub("", text.lower()))
    return text.replace("ة", "ه").replace("ى", "ي")


def _fingerprint(phrase: str) -> str:
    return hashlib.sha256((SALT + phrase).encode("utf-8")).hexdigest()


def _windows(tokens: list[str]) -> Iterable[str]:
    for size in range(1, WINDOW + 1):
        for start in range(len(tokens) - size + 1):
            yield " ".join(tokens[start : start + size])


def _leaks(text: str, forbidden: frozenset[str]) -> list[int]:
    """أرقام الأسطر التي يطابق فيها مقطعٌ بصمةً ممنوعة (لا يُعاد الاسم نفسه)."""
    lines: list[int] = []
    for number, line in enumerate(text.splitlines(), start=1):
        tokens = _WORD.findall(_normalise(line))
        if any(_fingerprint(phrase) in forbidden for phrase in _windows(tokens)):
            lines.append(number)
    return lines


def _archive_files() -> list[Path]:
    return sorted(
        p for p in ARCHIVE.rglob("*") if p.is_file() and p.suffix.lower() in SCANNED_SUFFIXES
    )


def test_the_archive_carries_no_personal_name() -> None:
    problems = []
    for path in _archive_files():
        lines = _leaks(path.read_text(encoding="utf-8"), FORBIDDEN)
        if lines:
            problems.append(f"{path.relative_to(REPO_ROOT)}: اسمٌ شخصي في الأسطر {lines}")
    assert not problems, "\n".join(problems)


def test_the_guard_scans_every_archive_file() -> None:
    names = {p.name for p in _archive_files()}
    assert "OWNER_ROUTES_2026-10-27_AR.md" in names
    assert "IDEA_REGISTER.json" in names
    assert any(p.parent.name == "data" for p in _archive_files())
    assert all(re.fullmatch(r"[0-9a-f]{64}", h) for h in FORBIDDEN)


def test_a_planted_name_is_red() -> None:
    planted = _fingerprint("zzqa testperson")
    assert _leaks("سطرٌ أوّل\nالشريك هو ZZQA TestPerson من الفريق", frozenset({planted})) == [2]


def test_a_planted_name_with_hamza_or_diacritics_is_red() -> None:
    planted = _fingerprint(_normalise("أحمدزززتجربة"))
    assert _leaks("كتب محمدزززتجربة", frozenset({planted})) == []
    assert _leaks("كتب إحمدزززتجربة", frozenset({planted})) == [1]
    assert _leaks("كتب أَحمدزززتجربة", frozenset({planted})) == [1]
    assert _leaks("كتب آحمدزززتجربة", frozenset({planted})) == [1]


def test_a_planted_three_word_name_is_red_only_as_a_whole() -> None:
    planted = _fingerprint("زيد عمرو بكر")
    assert _leaks("زيد وحده لا يكفي\nعمرو بكر أيضاً", frozenset({planted})) == []
    assert _leaks("قال زيد عمرو بكر", frozenset({planted})) == [1]
