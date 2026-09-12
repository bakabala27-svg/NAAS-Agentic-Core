"""البرهان السلبي لبوّابة جولة القرار 02 — `check_decision_round02.py` · D-207/D-266 L4.

**لماذا هذا الملفّ:** بوّابةٌ لا تُحجَب حين يُخرَق قانونها زينةٌ تُقرأ حماية. فكلّ فحصٍ هنا
**يكسر مُدخلاً** ويؤكّد رمز خروج ≠ 0 على شجرةٍ مؤقتة، ثمّ يُثبت أنّ الشجرة الحقيقية تمرّ.
الأفكار الثلاث الجديدة في هذه الجولة لها برهانٌ سلبيٌّ خاص:

1. رقمٌ عن الأداة في §4 ≠ ملفّ القياس ⇒ أحمر (لا «93 مسباراً» باليد بينما الملفّ يقول 90).
2. `empty_run_cells.flips_total > 0` بلا إذن وسقف خسارة ⇒ أحمر (استشهادٌ كاذب بنموذجٍ لم يُشغَّل).
3. عبارةٌ مدحوضة بأدلّة الجولة خارج سياق منعٍ صريح ⇒ أحمر — وداخل سياق المنع ⇒ أخضر
   (وإلا صار الفحص منعاً للكلام عن المنع).

⚠️ لا تُلمَس شجرة المستودع: كلّ كسرٍ يُكتب في `tmp_path` ويُشار إليه بإبدال ثوابت الوحدة
المستورَدة، كما في `test_decision_round01_gate.py`.
"""

from __future__ import annotations

import contextlib
import csv
import io
import json
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts" / "fitness"))

import check_decision_round02 as gate

STUDY = REPO_ROOT / "studies" / "algeria-hard-currency"
GATE_SCRIPT = REPO_ROOT / "scripts" / "fitness" / "check_decision_round02.py"
ARTIFACT = REPO_ROOT / "docs" / "research" / "CND_MEASUREMENTS.json"
OFFER_DOC = REPO_ROOT / "docs" / "commercial" / "CND_EXPORTABLE_EVAL_OFFER.md"
KNOWLEDGE_DOC = REPO_ROOT / "docs" / "research" / "HARD_CURRENCY_NEW_KNOWLEDGE_CND.md"
INVENTORY_DOC = REPO_ROOT / "docs" / "research" / "AR_FR_SAFETY_BENCHMARK_INVENTORY.md"
TRUTH_DOC = REPO_ROOT / ".memory" / "cnd_null_invariance_truth.md"
CATALOG = REPO_ROOT / "docs" / "commercial" / "OFFER_CATALOG.json"


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


def _tree(tmp_path: Path) -> dict[str, object]:
    """نسخةٌ صالحة من كلّ مُدخلات البوّابة إلى `tmp_path`."""
    shutil.copy(STUDY / "decision_ledger_round02.csv", tmp_path / "decision_ledger_round02.csv")
    shutil.copy(STUDY / "evidence_round02.csv", tmp_path / "evidence_round02.csv")
    shutil.copy(STUDY / "DECISION-ROUND-02.md", tmp_path / "DECISION-ROUND-02.md")
    shutil.copy(ARTIFACT, tmp_path / "CND_MEASUREMENTS.json")
    shutil.copy(OFFER_DOC, tmp_path / "CND_EXPORTABLE_EVAL_OFFER.md")
    shutil.copy(CATALOG, tmp_path / "OFFER_CATALOG.json")
    return {
        "LEDGER": tmp_path / "decision_ledger_round02.csv",
        "EVIDENCE": tmp_path / "evidence_round02.csv",
        "ROUND": tmp_path / "DECISION-ROUND-02.md",
        "ARTIFACT": tmp_path / "CND_MEASUREMENTS.json",
        "OFFER_DOC": tmp_path / "CND_EXPORTABLE_EVAL_OFFER.md",
        "CATALOG": tmp_path / "OFFER_CATALOG.json",
        "SCANNED_DOCS": (
            tmp_path / "DECISION-ROUND-02.md",
            KNOWLEDGE_DOC,
            INVENTORY_DOC,
            tmp_path / "CND_EXPORTABLE_EVAL_OFFER.md",
            TRUTH_DOC,
        ),
    }


def _rewrite_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _patch_artifact(path: Path, mutate) -> None:
    payload = json.loads(path.read_text(encoding="utf-8"))
    mutate(payload)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _append(path: Path, text: str) -> None:
    path.write_text(path.read_text(encoding="utf-8") + text, encoding="utf-8")


# --------------------------------------------------------------------------- #
# 0) المرجع
# --------------------------------------------------------------------------- #
def test_valid_copy_passes(tmp_path: Path) -> None:
    """نسخةٌ سليمة يجب أن تُقبل — بلا هذا لا معنى لأيّ كسرٍ لاحق."""
    code, output = _run(**_tree(tmp_path))
    assert code == 0, output


def test_real_repository_tree_passes() -> None:
    """الشجرة الحقيقية — بالعملية الفرعية كما في CI، لا بإبدال ثوابت."""
    result = subprocess.run(
        [sys.executable, str(GATE_SCRIPT)],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "جولة القرار 02 متّسقة" in result.stdout


# --------------------------------------------------------------------------- #
# 1) السجلّ والأعداد المشتقّة
# --------------------------------------------------------------------------- #
def test_published_count_drift_is_blocked(tmp_path: Path) -> None:
    """⛔ عددٌ منسوخ في الجدول لا مشتقٌّ من CSV يصير ادّعاءً لا دليلاً."""
    paths = _tree(tmp_path)
    text = Path(paths["ROUND"]).read_text(encoding="utf-8")
    Path(paths["ROUND"]).write_text(
        text.replace(
            "| **3** | `gate_state` يبدأ بـ«فاشلة»", "| **9** | `gate_state` يبدأ بـ«فاشلة»", 1
        ),
        encoding="utf-8",
    )
    code, output = _run(**paths)
    assert code == 1
    assert "مقابل المعلَن في الجولة=9" in output


def test_e2_level_is_blocked_while_no_loss_ceiling_exists(tmp_path: Path) -> None:
    """⛔ ترقيةٌ إلى E2 بلا سقف خسارة ولا إذن تشغيل — الجولة كلها مصمَّمة عند E1."""
    paths = _tree(tmp_path)
    rows = _rows(Path(paths["LEDGER"]))
    rows[0]["max_level"] = "E2"
    _rewrite_csv(Path(paths["LEDGER"]), rows)
    code, output = _run(**paths)
    assert code == 1
    assert "خارج E0/E1" in output


def test_missing_ledger_row_is_blocked(tmp_path: Path) -> None:
    """⛔ حذفُ صفٍّ يجعل العدد «متّسقاً» مع سجلٍّ أنقصه المتَّهَم."""
    paths = _tree(tmp_path)
    rows = _rows(Path(paths["LEDGER"]))
    _rewrite_csv(Path(paths["LEDGER"]), rows[:-1])
    code, output = _run(**paths)
    assert code == 1
    assert "8" in output


def test_column_shift_is_blocked(tmp_path: Path) -> None:
    """⛔ انزياحُ أعمدة (قرارٌ في خانة الادّعاء) يُرفض لا يمرّ صامتاً."""
    paths = _tree(tmp_path)
    rows = _rows(Path(paths["LEDGER"]))
    rows[0]["key_claim"], rows[0]["decision"] = rows[0]["decision"], rows[0]["key_claim"]
    _rewrite_csv(Path(paths["LEDGER"]), rows)
    code, output = _run(**paths)
    assert code == 1
    assert "انزياحُ أعمدة" in output


def test_row_without_shared_dependency_is_blocked(tmp_path: Path) -> None:
    """⛔ خانةُ الاعتماد المشترك الفارغة تُقرأ «محفظة متنوّعة» وهي عُقدة واحدة."""
    paths = _tree(tmp_path)
    rows = _rows(Path(paths["LEDGER"]))
    rows[1]["shared_dependency"] = ""
    _rewrite_csv(Path(paths["LEDGER"]), rows)
    code, output = _run(**paths)
    assert code == 1
    assert "بلا اعتماد مشترك" in output


def test_e2_eligible_row_must_be_declared_as_zero(tmp_path: Path) -> None:
    """⛔ الصفرُ يجب أن يُقال: حذفُ صفّ «مؤهَّلة لـ E2» يُخفي أنّ أحداً لا يملك إذناً."""
    paths = _tree(tmp_path)
    text = Path(paths["ROUND"]).read_text(encoding="utf-8")
    lines = [line for line in text.splitlines() if not line.startswith("| **مؤهَّلة لـ E2")]
    Path(paths["ROUND"]).write_text("\n".join(lines) + "\n", encoding="utf-8")
    code, output = _run(**paths)
    assert code == 1
    assert "مفقود من §5.1" in output


# --------------------------------------------------------------------------- #
# 2) الأدلّة والادّعاءات
# --------------------------------------------------------------------------- #
def test_dangling_evidence_id_is_blocked(tmp_path: Path) -> None:
    """⛔ معرّف S## مذكور ولا وجود له في السجلّ — استشهادٌ معلّق."""
    paths = _tree(tmp_path)
    _append(Path(paths["ROUND"]), "\n\nمصدرٌ مُختلَق S99 للتجربة.\n")
    code, output = _run(**paths)
    assert code == 1
    assert "S99" in output


def test_unreferenced_evidence_is_blocked(tmp_path: Path) -> None:
    """⛔ دليلٌ في السجلّ لا تستشهد به الجولة حشوٌ يُقرأ إسناداً."""
    paths = _tree(tmp_path)
    text = Path(paths["ROUND"]).read_text(encoding="utf-8")
    Path(paths["ROUND"]).write_text(text.replace("S40", "—"), encoding="utf-8")
    code, output = _run(**paths)
    assert code == 1
    assert "لا تستشهد بها الجولة" in output


def test_evidence_without_independence_note_is_blocked(tmp_path: Path) -> None:
    """⛔ سندٌ بلا نسبةِ استقلال يُقرأ حيادياً وهو ليس كذلك."""
    paths = _tree(tmp_path)
    rows = _rows(Path(paths["EVIDENCE"]))
    rows[0]["independence_note"] = ""
    _rewrite_csv(Path(paths["EVIDENCE"]), rows)
    code, output = _run(**paths)
    assert code == 1
    assert "بلا ملاحظة استقلال" in output


def test_claim_without_a_row_is_blocked(tmp_path: Path) -> None:
    """⛔ ادّعاءٌ مُشار إليه بلا سطرٍ في جدول §6 لا حالةَ له ولا سند."""
    paths = _tree(tmp_path)
    _append(Path(paths["ROUND"]), "\n\nيعتمد هذا على C99 كذلك.\n")
    code, output = _run(**paths)
    assert code == 1
    assert "C99" in output


# --------------------------------------------------------------------------- #
# 3) أرقامُ الأداة (§4) — الصنف الجديد من الادّعاء
# --------------------------------------------------------------------------- #
def test_measurement_drift_is_blocked(tmp_path: Path) -> None:
    """⛔ «93 مسباراً» مكتوبةٌ باليد بينما الملفّ يقول 90 — هذا هو الكذب الذي تحرسه البوّابة."""
    paths = _tree(tmp_path)
    _patch_artifact(Path(paths["ARTIFACT"]), lambda payload: payload["coverage"].update(probes=90))
    code, output = _run(**paths)
    assert code == 1
    assert "`coverage.probes`" in output
    assert "90" in output


def test_measurement_row_without_a_path_in_the_artifact_is_blocked(tmp_path: Path) -> None:
    """⛔ مسارٌ مُختلَق داخل جدول §4 يُقرأ اشتقاقاً وهو لا يحلّ في شيء."""
    paths = _tree(tmp_path)
    text = Path(paths["ROUND"]).read_text(encoding="utf-8")
    anchor = "| `coverage.probes` | 93 |"
    assert anchor in text
    Path(paths["ROUND"]).write_text(
        text.replace(anchor, anchor + "\n| `coverage.invented_metric` | 7 |", 1),
        encoding="utf-8",
    )
    code, output = _run(**paths)
    assert code == 1
    assert "غير قابل للحلّ" in output


def test_measurement_filter_that_matches_nothing_is_blocked(tmp_path: Path) -> None:
    """⛔ مرشِّحٌ لا يطابق صفّاً (أو يطابق اثنين) ليس اشتقاقاً بل تخمين."""
    paths = _tree(tmp_path)
    text = Path(paths["ROUND"]).read_text(encoding="utf-8")
    Path(paths["ROUND"]).write_text(
        text.replace(
            "`maturity_gap[scope=pooled_all_families][kind=violation].pairs`",
            "`maturity_gap[scope=pooled_invented][kind=violation].pairs`",
            1,
        ),
        encoding="utf-8",
    )
    code, output = _run(**paths)
    assert code == 1
    assert "أعطى 0 نتيجة" in output


def test_thinning_the_measurement_table_is_blocked(tmp_path: Path) -> None:
    """⛔ إفراغُ §4 يُسقط الاشتقاق كلّه فيصير النصّ بلا أرقام — والبوّابة ترفض الإفراغ."""
    paths = _tree(tmp_path)
    text = Path(paths["ROUND"]).read_text(encoding="utf-8")
    start = text.index("## 4.")
    end = text.index("## 5.")
    Path(paths["ROUND"]).write_text(
        text[:start]
        + "## 4. أرقام الأداة\n\n| المفتاح | القيمة |\n|---|---|\n| `coverage.probes` | 93 |\n\n"
        + text[end:],
        encoding="utf-8",
    )
    code, output = _run(**paths)
    assert code == 1
    assert "صفّاً فقط" in output


def test_deleting_the_zero_run_guard_is_blocked(tmp_path: Path) -> None:
    """⛔ حذفُ الحارس يُسكت الشاهد بدل أن يُقنعه — أخطر من غيابه أصلاً."""
    paths = _tree(tmp_path)
    _patch_artifact(Path(paths["ARTIFACT"]), lambda payload: payload.pop("empty_run_cells"))
    code, output = _run(**paths)
    assert code == 1
    assert "حارسُ صفرِ المحاكمات مفقود" in output


def test_flips_without_authorization_are_blocked(tmp_path: Path) -> None:
    """⛔ رقمُ انقلابٍ في مستودعٍ لم يشغّل نموذجاً استشهادٌ كاذب، ولو كان الملفّ «موجوداً»."""
    paths = _tree(tmp_path)
    _patch_artifact(
        Path(paths["ARTIFACT"]),
        lambda payload: payload["empty_run_cells"].update(flips_total=5),
    )
    code, output = _run(**paths)
    assert code == 1
    assert "استشهادٌ كاذب" in output


def test_silence_about_zero_runs_is_blocked(tmp_path: Path) -> None:
    """⛔ الصمتُ عن صفر المحاكمات يُقرأ قياساً — يجب أن يُقال نصّاً."""
    paths = _tree(tmp_path)
    text = Path(paths["ROUND"]).read_text(encoding="utf-8")
    Path(paths["ROUND"]).write_text(
        text.replace("صفر محاكمات", "—").replace("صفرُ محاكمات", "—"), encoding="utf-8"
    )
    code, output = _run(**paths)
    assert code == 1
    assert "الصمتُ يُقرأ قياساً" in output


def test_missing_no_spend_statement_is_blocked(tmp_path: Path) -> None:
    """⛔ جولةٌ بلا عبارة «لا يوجد سقف خسارة معتمد» توصي بإنفاقٍ لم يُؤذَن به."""
    paths = _tree(tmp_path)
    text = Path(paths["ROUND"]).read_text(encoding="utf-8")
    Path(paths["ROUND"]).write_text(text.replace("لا يوجد سقف خسارة معتمد", "—"), encoding="utf-8")
    code, output = _run(**paths)
    assert code == 1
    assert "توصيةٌ بلا سقف خسارة" in output


# --------------------------------------------------------------------------- #
# 4) المحرّمات وخطوط العرض
# --------------------------------------------------------------------------- #
def test_refuted_claim_outside_a_prohibition_is_blocked(tmp_path: Path) -> None:
    """⛔ عبارةٌ دحضتها أدلّةُ الجولة تعود إلى النصّ بلا علامة منع — أحمر."""
    paths = _tree(tmp_path)
    _append(Path(paths["ROUND"]), "\n\nلا يوجد معيارُ سلامة عربي مفتوح بحجم كبير.\n")
    code, output = _run(**paths)
    assert code == 1
    assert "عبارةٌ مدحوضة خارج سياق منع" in output


def test_refuted_claim_inside_a_prohibition_is_allowed(tmp_path: Path) -> None:
    """الفحص ليس منعاً للكلام عن المنع: العبارة نفسها داخل سطر ⛔ تمرّ."""
    paths = _tree(tmp_path)
    _append(Path(paths["ROUND"]), "\n\n⛔ ممنوعٌ قول «لا يوجد معيارُ سلامة عربي» — S28 يدحضه.\n")
    code, output = _run(**paths)
    assert code == 0, output


def test_refuted_claim_in_the_offer_document_is_blocked(tmp_path: Path) -> None:
    """الفحصُ يمسح وثائق العرض والمعرفة والجرد والحالة، لا وثيقة القرار وحدها."""
    paths = _tree(tmp_path)
    _append(Path(paths["OFFER_DOC"]), "\n\nنحن وحدنا نقيس الثبات داخل البند.\n")
    code, output = _run(**paths)
    assert code == 1
    assert "CND_EXPORTABLE_EVAL_OFFER.md" in output


def test_phantom_offer_line_is_blocked(tmp_path: Path) -> None:
    """⛔ خطُّ عرضٍ مُسمّى في الوثيقة وغير موجود في الكتالوج يُقرأ مصرَّحاً."""
    paths = _tree(tmp_path)
    _append(Path(paths["OFFER_DOC"]), "\n\n| `cnd-invariance-audit` | أثر | `PROPOSED` |\n")
    catalog = json.loads(Path(paths["CATALOG"]).read_text(encoding="utf-8"))
    catalog["offers"].append({"id": "cnd-invariance-audit", "status": "PROPOSED"})
    Path(paths["CATALOG"]).write_text(json.dumps(catalog, ensure_ascii=False), encoding="utf-8")
    code, output = _run(**paths)
    assert code == 1
    assert "خطُّ عرضٍ ثامن" in output


def test_offer_line_cited_but_absent_from_catalog_is_blocked(tmp_path: Path) -> None:
    """⛔ الاتجاهُ الآخر: معرّفٌ في الوثيقة بلا صفٍّ في الكتالوج = خطٌّ وهمي."""
    paths = _tree(tmp_path)
    _append(Path(paths["OFFER_DOC"]), "\n\n| `ghost-line-x1` | أثر | `PROPOSED` |\n")
    code, output = _run(**paths)
    assert code == 1
    assert "خطوطاً غير موجودة في الكتالوج" in output


def test_missing_scanned_document_is_blocked(tmp_path: Path) -> None:
    """⛔ وثيقةٌ مفقودة في فحص المحرّمات لا تُقرأ نظيفة."""
    paths = _tree(tmp_path)
    (tmp_path / "CND_EXPORTABLE_EVAL_OFFER.md").unlink()
    code, output = _run(**paths)
    assert code == 1
    assert "وثيقةٌ مفقودة في فحص المحرّمات" in output
