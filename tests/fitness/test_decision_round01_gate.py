"""البرهان السلبي لفاصلة جولة القرار 01 — محرك الالتزام · D-207.

**لماذا هذا الملفّ:** `check_decision_round01.py` يفرض أن تكون أعداد الجولة
المنشورة في `DECISION-ROUND-01.md` **مشتقّة** من `decision_ledger_round01.csv`،
وأن لا E2 بلا تفويض مكتوب، ولا استشهاد معلّق. فاصلةٌ كهذه إن لم يشغّلها شيءٌ
في CI صارت «فارضاً بلا مرمى» (D-207) — ومن يقرأها وهي خضراء دائماً يظنّها دليلاً
وهي زينة. فكلّ فحصٍ هنا **يكسر** مُدخلاً ويؤكّد رمز خروج ≠ 0 على شجرةٍ مؤقتة،
ثمّ يُثبت أنّ الشجرة الحقيقية تمرّ (⛔ «اختبارٌ يتوقّع النجاح» ليس برهاناً سلبياً).

⚠️ لا تُلمَس شجرة المستودع: كلّ كسرٍ يُكتب في `tmp_path` ويُشار إليه بإبدال
الثوابت `LEDGER/EVIDENCE/ROUND` على الوحدة المستورَدة، كما في
`test_dual_track_alignment_gate.py`.
"""

from __future__ import annotations

import contextlib
import csv
import io
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts" / "fitness"))

import check_decision_round01 as gate

STUDY = REPO_ROOT / "studies" / "algeria-hard-currency"
GATE_SCRIPT = REPO_ROOT / "scripts" / "fitness" / "check_decision_round01.py"


def _run(**overrides) -> tuple[int, str]:
    """يشغّل `main()` تحت مسارات بديلة ويُعيد (رمز الخروج، المخرَج)."""
    saved = {name: getattr(gate, name) for name in overrides}
    for name, value in overrides.items():
        setattr(gate, name, value)
    buffer = io.StringIO()
    try:
        with contextlib.redirect_stdout(buffer):
            code = gate.main()
    finally:
        for name, value in saved.items():
            setattr(gate, name, value)
    return code, buffer.getvalue()


def _tree(tmp_path: Path, *, drop_count_line: bool = False) -> dict[str, Path]:
    """نسخةٌ صالحة من السجلات الثلاثة إلى `tmp_path`، مع سطحٍ يُبقي الفحص الذاتي حيّاً."""
    shutil.copy(STUDY / "decision_ledger_round01.csv", tmp_path / "decision_ledger_round01.csv")
    shutil.copy(STUDY / "evidence_round01.csv", tmp_path / "evidence_round01.csv")
    round_text = (STUDY / "DECISION-ROUND-01.md").read_text(encoding="utf-8")
    if drop_count_line:
        round_text = round_text.replace("**12**", "**99**", 1)
    round_path = tmp_path / "DECISION-ROUND-01.md"
    round_path.write_text(round_text, encoding="utf-8")
    return {
        "LEDGER": tmp_path / "decision_ledger_round01.csv",
        "EVIDENCE": tmp_path / "evidence_round01.csv",
        "ROUND": round_path,
    }


def _rewrite(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def test_valid_copy_passes(tmp_path: Path) -> None:
    """المرجع: نسخةٌ سليمة يجب أن تُقبل — بلا هذا لا معنى لأيِّ كسرٍ لاحق."""
    code, output = _run(**_tree(tmp_path))
    assert code == 0, output


def test_published_count_drift_is_blocked(tmp_path: Path) -> None:
    """⛔ عددٌ منسوخٌ في الجدول لا CSV — يصير ادّعاءً لا دليلاً."""
    paths = _tree(tmp_path, drop_count_line=True)
    code, output = _run(**paths)
    assert code == 1
    assert "المعلن في الجولة" in output


def test_column_shift_is_blocked(tmp_path: Path) -> None:
    """⛔ انزياح أعمدة (قرارٌ في خانة الادّعاء) يجب أن يُرفض لا أن يمرّ صامتاً."""
    paths = _tree(tmp_path)
    rows = list(csv.DictReader(paths["LEDGER"].open(encoding="utf-8")))
    for row in rows:
        if row["id"] == "H7":
            row["key_claim"] = row["decision"]
            row["decision"] = "طاقة"
    _rewrite(paths["LEDGER"], rows)
    code, output = _run(**paths)
    assert code == 1
    assert "انزياح أعمدة" in output


def test_e2_without_written_authorization_is_blocked(tmp_path: Path) -> None:
    """⛔ ترقيةٌ بلا تفويض مكتوب تُطفئ البوابة التي يفترض أن تحرسها."""
    paths = _tree(tmp_path)
    rows = list(csv.DictReader(paths["LEDGER"].open(encoding="utf-8")))
    for row in rows:
        if row["max_level"] == "E1":
            row["max_level"] = "E2"
            break
    _rewrite(paths["LEDGER"], rows)
    code, output = _run(**paths)
    assert code == 1
    assert "E2" in output


def test_missing_ledger_row_is_blocked(tmp_path: Path) -> None:
    """⛔ حذف صفٍّ يجعل العدد «متسقاً» مع سجلٍ أنقصه المتَّهَم — فيُرفض."""
    paths = _tree(tmp_path)
    rows = list(csv.DictReader(paths["LEDGER"].open(encoding="utf-8")))
    _rewrite(paths["LEDGER"], rows[:-1])
    code, output = _run(**paths)
    assert code == 1
    assert "32" in output


def test_dangling_evidence_id_is_blocked(tmp_path: Path) -> None:
    """⛔ معرّف S## مذكورٌ في الجولة ولا يوجد في سجلّ الأدلة — استشهادٌ معلّق."""
    paths = _tree(tmp_path)
    round_path = paths["ROUND"]
    round_path.write_text(
        round_path.read_text(encoding="utf-8") + "\n\nمصدرٌ مُختلَق S99 للتجربة.\n",
        encoding="utf-8",
    )
    code, output = _run(ROUND=round_path, **{k: v for k, v in paths.items() if k != "ROUND"})
    assert code == 1
    assert "S99" in output


def test_real_repository_tree_passes() -> None:
    """الشجرة الحقيقية — تُشغَّل بالعملية الفرعية كما في CI، لا بإبدال ثوابت."""
    result = subprocess.run(
        [sys.executable, str(GATE_SCRIPT)],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "متسقة مع سجلها" in result.stdout
