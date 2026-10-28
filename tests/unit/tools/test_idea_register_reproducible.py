"""السجلّ الموحّد يُعاد إنتاجه من سكربتاته المحفوظة في المستودع — يُفحَص كالكود.

**لماذا هذا الاختبار موجود.** ``IDEA_REGISTER.json`` وقراءته ``IDEA_REGISTER_AR.md`` مولَّدان،
وكان مولِّدهما يعيش خارج المستودع في مساحةٍ مؤقّتة تُمحى بانتهاء الجلسة. فلو ضاع لصار السجلّ
نصّاً يُحرَّر يدوياً، وتتفرّق نسخته عن قواعده دون أن يلاحظ أحد. قال المالك في 2026-10-28:
«أرسل كلّ شيء تناولناه في المحادثة للمستودع»، فصار المولِّد في
``scripts/research/idea_register/``، وهذا الاختبار يُثبت أنّ ما يولّده هو بالضبط ما هو محفوظ.

الاختبار لا يكتب على القرص ولا يقرأ الشبكة: يبني السجلّ في الذاكرة ويقارنه بالملفّين.
والحالتان السلبيتان تُبرهنان أنّ أيّ تحريرٍ يدوي للملفّين، أو أيّ تغييرٍ في البيانات لم يُعَد
توليده، يحمرّ.

**التشغيل:** ``pytest tests/unit/tools/test_idea_register_reproducible.py -q``
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from types import ModuleType

REPO_ROOT = Path(__file__).resolve().parents[3]
BUILDER = REPO_ROOT / "scripts/research/idea_register/build_register.py"
ARCHIVE = REPO_ROOT / "docs/archive/commercial"


def _builder() -> ModuleType:
    spec = importlib.util.spec_from_file_location("idea_register_builder", BUILDER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _rendered() -> tuple[str, str]:
    builder = _builder()
    register = builder.build()
    as_json = json.dumps(register, ensure_ascii=False, indent=1) + "\n"
    return as_json, builder.md(register)


def _drift(rendered: tuple[str, str], committed: tuple[str, str]) -> list[str]:
    names = ("IDEA_REGISTER.json", "IDEA_REGISTER_AR.md")
    return [name for name, new, old in zip(names, rendered, committed, strict=True) if new != old]


def _committed() -> tuple[str, str]:
    return (
        (ARCHIVE / "IDEA_REGISTER.json").read_text(encoding="utf-8"),
        (ARCHIVE / "IDEA_REGISTER_AR.md").read_text(encoding="utf-8"),
    )


def test_the_committed_register_is_exactly_what_the_scripts_build() -> None:
    drift = _drift(_rendered(), _committed())
    assert not drift, (
        f"السجلّ المحفوظ يختلف عمّا يولّده المولِّد: {drift} — "
        "شغّل python3 -I scripts/research/idea_register/build_register.py ولا تحرّر الملفّين يدوياً"
    )


def test_a_hand_edit_of_the_reading_view_is_red() -> None:
    as_json, as_md = _committed()
    edited = as_md.replace("## 1.", "## 1 (محرَّر يدوياً).", 1)
    assert _drift(_rendered(), (as_json, edited)) == ["IDEA_REGISTER_AR.md"]


def test_a_data_change_without_regeneration_is_red() -> None:
    as_json, as_md = _committed()
    register = json.loads(as_json)
    register["records"][0]["option"]["trigger_ar"] += " (تغييرٌ لم يُعَد توليده)"
    stale = json.dumps(register, ensure_ascii=False, indent=1) + "\n"
    assert _drift(_rendered(), (stale, as_md)) == ["IDEA_REGISTER.json"]
