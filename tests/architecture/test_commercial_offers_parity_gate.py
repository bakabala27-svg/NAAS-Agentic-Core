"""W-13 → ADR-017 — براهينُ سلبية لبوّابة مطابقة وثائق العروض مع الكتالوج.

البوابةُ وُلدت من وعدٍ في وثيقة: «تفعيلُ بوابة `check_commercial_offers_parity.py`»
(`docs/commercial/SOVEREIGN_KNOWLEDGE_REVENUE_MAP.md` §5.3) — ووعدٌ بحراسةٍ لم تُبنَ هو
صنف ISS-186. فالحاجةُ هنا ليست بوّابةً تُشغَّل فحسب، بل بوّابةٌ **تَحجب** حين تُخرَق.

كلُّ حالةٍ تكسر بنداً واحداً من العقد على نموذجٍ مصغَّر، وتؤكّد الرمز 1 ورسالةً تُسمّي
البند. أمّا الشجرةُ الحقيقية فيُثبت اختبارٌ أخيرٌ أنها تمرّ — والاثنان معاً هما البرهان:
الحارسُ awakeٌ والقانونُ مُرضٍ عنه.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
GATE = REPO_ROOT / "scripts" / "fitness" / "check_commercial_offers_parity.py"
RELATIVE = "scripts/fitness/check_commercial_offers_parity.py"

_MARKER = "<!-- catalog-relationship: {kind} | reason: {reason} -->"
_CATALOG = {
    "offers": [
        {"id": "ai-red-teaming-multilingual", "status": "PROPOSED"},
        {"id": "niche-rlhf-data", "status": "PROPOSED"},
    ]
}


def _build(
    root: Path, *, docs: dict[str, str] | None = None, catalog: dict[str, Any] | None = None
) -> Path:
    """شجرةٌ مصغَّرة: كتالوجٌ ووثيقةُ عرضٍ واحدةٌ مُعلَنةُ الصلة."""
    root.mkdir(parents=True, exist_ok=True)
    commercial = root / "docs/commercial"
    commercial.mkdir(parents=True, exist_ok=True)
    (commercial / "OFFER_CATALOG.json").write_text(
        json.dumps(catalog or _CATALOG, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    payload = docs or {
        "DEMO_OFFER.md": (
            "# عرضٌ تجريبي\n\n"
            "> **الصلةُ بالكتالوج:** "
            + _MARKER.format(kind="line:ai-red-teaming-multilingual", reason="سطرٌ كنسيٌّ واحد")
            + "\n"
        )
    }
    for name, text in payload.items():
        (commercial / name).write_text(text, encoding="utf-8")
    return root


def _run(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(  # قائمةُ وسائط ثابتة: لا قشرة (D-189)
        [sys.executable, str(GATE), "--root", str(root)],
        capture_output=True,
        text=True,
        check=False,
        cwd=REPO_ROOT,
    )


def test_clean_declaration_passes(tmp_path: Path) -> None:
    result = _run(_build(tmp_path / "repo"))
    assert result.returncode == 0, result.stdout


@pytest.mark.parametrize(
    ("docs", "expected_text"),
    [
        pytest.param(
            {"DEMO_OFFER.md": "# عرضٌ بلا صلةٍ مُعلَنة\n\nنصٌّ يبيع ولا يقول أين هو من الكتالوج.\n"},
            "لا صلةَ مُعلَنة",
            id="وثيقةُ عرضٍ بلا علامة صلة",
        ),
        pytest.param(
            {
                "DEMO_OFFER.md": "# عرض\n\n> "
                + _MARKER.format(kind="OUTSIDE_CANONICAL_SEVEN", reason="سبب")
                + "\n> "
                + _MARKER.format(kind="line:niche-rlhf-data", reason="سبب ثانٍ")
                + "\n"
            },
            "لوثيقةٍ واحدة",
            id="علامةٌ مكرَّرة لوثيقةٍ واحدة",
        ),
        pytest.param(
            {
                "DEMO_OFFER.md": "> "
                + _MARKER.format(kind="line:invented-offer", reason="لا وجود له")
                + "\n"
            },
            "لا تُطابق سطراً في الكتالوج",
            id="صلةٌ بسطرٍ غير موجود في الكتالوج",
        ),
        pytest.param(
            {
                "DEMO_OFFER.md": "> "
                + _MARKER.format(kind="OUTSIDE_CANONICAL_SEVEN", reason="")
                + "\n"
            },
            "بلا سببٍ منطوق",
            id="خارج الكتالوج بلا سببٍ مكتوب",
        ),
        pytest.param(
            {
                "DEMO_OFFER.md": "> **الحالة:** "
                + _MARKER.format(kind="line:ai-red-teaming-multilingual", reason="سطرٌ واحد")
                + " — والكتالوجُ اليوم `PAID_PROOF` لسطر `ai-red-teaming-multilingual`.\n"
            },
            "بينما",
            id="نثرُ الوثيقة يسبقُ حالةَ الكتالوج (سُلَّمٌ ثانٍ)",
        ),
    ],
)
def test_gate_blocks_each_broken_parity(
    tmp_path: Path, docs: dict[str, str], expected_text: str
) -> None:
    result = _run(_build(tmp_path / "repo", docs=docs))
    assert result.returncode == 1, f"البوّابة مرّت على عقدٍ مكسور:\n{result.stdout}"
    assert expected_text in result.stdout, f"الرسالة لا تُسمّي البند:\n{result.stdout}"


def test_gate_blocks_missing_catalog(tmp_path: Path) -> None:
    """كتالوجٌ مفقودٌ لا يعني «لا شيء لمطابقته»: الفحصُ لم يقع، فلا يُشهَد بالنظافة."""
    root = _build(tmp_path / "repo")
    (root / "docs/commercial/OFFER_CATALOG.json").unlink()
    result = _run(root)
    assert result.returncode == 1
    assert "الكتالوج مفقود" in result.stdout


def test_gate_blocks_unreadable_catalog(tmp_path: Path) -> None:
    root = _build(tmp_path / "repo")
    (root / "docs/commercial/OFFER_CATALOG.json").write_text("{oops", encoding="utf-8")
    result = _run(root)
    assert result.returncode == 1
    assert "لا يمكن تحليل" in result.stdout


def test_gate_blocks_offer_docs_without_a_catalog(tmp_path: Path) -> None:
    """`offers` فارغةٌ في الكتالوج = مطابقةٌ بلا طرفٍ ثانٍ، لا نجاحٌ صامت."""
    root = _build(tmp_path / "repo", catalog={"offers": []})
    result = _run(root)
    assert result.returncode == 1
    assert "مطابقةٌ بلا طرفٍ ثانٍ" in result.stdout


def test_offer_docs_in_the_tree_declare_their_relation() -> None:
    """الوثائقُ الخمس المُودَعة مُعلِنةُ الصلة — لا استثناءٌ مُجمَّدٌ بلا سببٍ يُنسى."""
    for path in sorted((REPO_ROOT / "docs/commercial").glob("*_OFFER.md")):
        assert "catalog-relationship:" in path.read_text(encoding="utf-8"), path.name


def test_gate_is_wired_into_required_ci() -> None:
    workflow = (REPO_ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    assert RELATIVE in workflow, "البوّابة ليست في `guardrails` ⇒ لا تُشغَّل في required-ci"
