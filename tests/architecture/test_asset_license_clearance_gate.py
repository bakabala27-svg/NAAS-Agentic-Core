"""ADR-017 — براهينُ سلبية مُثبَتة لبوّابة براءة الحقوق.

**بوّابةٌ لم تُرَ حمراء ليست بوّابةً (D-270 L4).** كلُّ حالةٍ هنا تُفسد بنداً واحداً من
عقد `check_asset_license_clearance` على **نموذجٍ صغيرٍ مستقلٍّ** للشجرة، وتُثبت أن
البوّابة تُرجِع 1 وأنّ رسالتها تُسمّي البند المكسور — لأنّ برهاناً لا يفحص النصَّ كان
يمرّر «فشيلاً لسببٍ آخر» ويقرأ نجاحاً.

النموذجُ صغيرٌ عمداً: نسخةٌ كاملة من الشجرة (ولو بالروابط الرمزية) تجعل الاختبار
يتعلّق بملفاتٍ لا يقيسها، وهو العطبُ الذي موّهه سابقاً «النسخةُ الجزئية تُبلّغ عن
اثني عشر ملفاً لم يمسّها الاختبار» في `test_revenue_doctrine_gate.py`.

لا شيء هنا يلمس الشبكة: الرخصُ مُدخلاتٌ ثابتة، والاختبارُ يقيس **المنطق الحارس** لا
عالمَ الأطراف الثالثة.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
GATE = REPO_ROOT / "scripts" / "fitness" / "check_asset_license_clearance.py"
RELATIVE = "scripts/fitness/check_asset_license_clearance.py"

#: تاريخٌ ثابتٌ كي لا يتقادم الاختبارُ مع ساعة الآلة: نافذةُ المراجعة 365 يوماً.
_REVIEWED = "2026-09-16"


def _fixture_register() -> dict[str, Any]:
    """نموذجٌ صحيحٌ بأصغرِ حجم: مصدرٌ حزمةٌ ملفٌّ ثنائيٌّ عرضٌ بطاقةٌ واحدة."""
    return {
        "$schema_version": "1",
        "decision": "ADR-017",
        "generated_on": _REVIEWED,
        "vocabulary": {
            "commercial_use": [
                "ALLOWED",
                "ALLOWED_WITH_ATTRIBUTION",
                "REFERENCE_LINK_ONLY",
                "BLOCKED_FOR_DERIVATIVES",
                "DANGLING_MUST_RELOCATE",
            ],
            "method": [
                "github-api-license",
                "upstream-license-file-read",
                "github-api-404",
                "git-tree-inspection",
            ],
            "on_premise_distribution": [
                "OK_BOTH",
                "FILE_LEVEL_NOTICE",
                "SOURCE_OBLIGATION_ON_PREMISE",
                "BLOCK_ON_PREMISE",
                "UNRESOLVED_DO_NOT_SHIP",
            ],
            "offer_clearance": ["CLEARED", "BLOCKED_BY_UPSTREAM_LICENSE"],
            "finding_kind": ["offer_blocked", "tracked_binary", "dangling_citation"],
            "finding_severity": ["BLOCKING", "HIGH", "MEDIUM"],
        },
        "policy": {
            "promotion_blocked_at": ["OFFER_READY", "PILOT", "PAID_PROOF", "REPEATABLE"],
            "promotable_commercial_use": ["ALLOWED", "ALLOWED_WITH_ATTRIBUTION"],
            "review_window_days": 365,
        },
        "upstream_sources": [
            {
                "recorded_repo": "acme/permissive-lib",
                "upstream_repo": "acme/permissive-lib",
                "recorded_url": "https://github.com/acme/permissive-lib",
                "matrix_status": "MANDATORY_REFERENCE",
                "upstream_license": "MIT",
                "commercial_use": "ALLOWED",
                "method": "github-api-license",
                "attribution_required": False,
                "reason_ar": "رخصةٌ مبيحة.",
                "reviewed_on": _REVIEWED,
            }
        ],
        "production_dependencies": [
            {
                "package": "fastapi",
                "pinned_version": "0.109.2",
                "license": "MIT",
                "license_evidence": "https://pypi.org/pypi/fastapi/json",
                "saas_ok": True,
                "on_premise_distribution": "OK_BOTH",
                "note_ar": "رخصةٌ مبيحةٌ للاتجاهين.",
                "reviewed_on": _REVIEWED,
            }
        ],
        "tracked_binary_artifacts": [
            {
                "path": "docs/evidence/shot.png",
                "kind": "own_work_image",
                "size_bytes": 12,
                "distribution": "OWN_WORK_MIT",
                "finding_ar": "أصلٌ محليّ.",
                "remediation_ar": "",
                "reviewed_on": _REVIEWED,
            }
        ],
        "offer_clearance": [
            {
                "offer_id": "demo-offer",
                "offer_status": "PROPOSED",
                "backbone_refs": ["permissive-lib"],
                "clearance": "CLEARED",
                "blockers": [],
                "reviewed_on": _REVIEWED,
            }
        ],
        "findings_ar": [
            {
                "id": "F-IP-99",
                "kind": "offer_blocked",
                "severity": "MEDIUM",
                "title_ar": "لا حجابَ في النموذج",
                "finding_ar": "بطاقةٌ مُعلَنةٌ لغياب الحجاب، لأنّ الخانةَ الفارغة تُقرأ نجاحاً.",
                "covers": [],
                "action_ar": "لا شيء.",
                "owner_ar": "test-fixture",
                "verified_on": _REVIEWED,
            }
        ],
    }


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _build_fixture(root: Path, register: dict[str, Any] | None = None) -> Path:
    """يشيّد شجرةً مصغّرةً قابلةً للفحص، ويُجهّز فهرسَ git بلا التزام."""
    root.mkdir(parents=True, exist_ok=True)
    (root / "docs/governance").mkdir(parents=True, exist_ok=True)
    (root / "docs/commercial").mkdir(parents=True, exist_ok=True)
    (root / "docs/evidence").mkdir(parents=True, exist_ok=True)
    (root / "docs/evidence/shot.png").write_bytes(b"\x89PNG\r\n\x1a\n12")
    _write(
        root / "docs/governance/SOURCE_ADOPTION_MATRIX.json",
        {
            "sources": [
                {
                    "source_id": "permissive-lib",
                    "url": "https://github.com/acme/permissive-lib",
                    "status": "MANDATORY_REFERENCE",
                }
            ]
        },
    )
    _write(
        root / "docs/commercial/OFFER_CATALOG.json",
        {"offers": [{"id": "demo-offer", "status": "PROPOSED"}]},
    )
    (root / "requirements-prod.txt").write_text("fastapi==0.109.2  # تعليق\n", encoding="utf-8")
    _write(root / "docs/governance/ASSET_LICENSE_CLEARANCE.json", register or _fixture_register())
    for args in (["init", "-q"], ["add", "-A"]):
        subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, text=True)
    return root


def _run_gate(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(  # قائمةُ وسائط ثابتة: لا قشرةٌ ولا تدخلُ مستخدم (D-189)
        [sys.executable, str(GATE), "--root", str(root)],
        capture_output=True,
        text=True,
        check=False,
        cwd=REPO_ROOT,
    )


def _break(root: Path, mutate: Any) -> subprocess.CompletedProcess[str]:
    """يُعيد كتابةَ السجلّ بعد إفسادهِ، ثم يشغّل البوّابةَ على الشجرة المكسورة."""
    path = root / "docs/governance/ASSET_LICENSE_CLEARANCE.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    mutate(payload)
    _write(path, payload)
    return _run_gate(root)


@pytest.mark.parametrize(
    ("mutate", "expected_text"),
    [
        pytest.param(
            lambda p: p["upstream_sources"][0].__setitem__("commercial_use", "PERMISSIVE_MAYBE"),
            "خارج القاموس",
            id="قيمةٌ خارج القاموس المُعلَن",
        ),
        pytest.param(
            lambda p: p["upstream_sources"].append(
                {
                    "recorded_repo": "acme/ghost-lib",
                    "upstream_repo": "acme/ghost-lib",
                    "upstream_license": "MIT",
                    "commercial_use": "ALLOWED",
                    "method": "github-api-license",
                    "attribution_required": False,
                    "reviewed_on": _REVIEWED,
                }
            ),
            "لمصدرٍ ليس في المصفوفة",
            id="سجلٌّ لمصدرٍ غير موجود في مصفوفة المصادر",
        ),
        pytest.param(
            lambda p: p["upstream_sources"][0].update({"upstream_license": None}),
            "لا ملفّ ترخيص في المصدر",
            id="براءةٌ معلَنةٌ لمصدرٍ بلا رخصة",
        ),
        pytest.param(
            lambda p: p["offer_clearance"][0].update(
                {"offer_status": "PILOT", "blockers": [{"ref": "x", "why_ar": "حجابٌ مسجَّل"}]}
            ),
            "لا يُباع أصلٌ لا يملكه البائع",
            id="عرضٌ مرقّى إلى PILOT مع حجابٍ مرخّص",
        ),
        pytest.param(
            lambda p: p["offer_clearance"][0].update({"clearance": "BLOCKED_BY_UPSTREAM_LICENSE"}),
            "لا تُطابق",
            id="حالةُ العرض لا تُطابق سجلَّ حُجوبه (كذبٌ على النفس)",
        ),
        pytest.param(
            lambda p: p["production_dependencies"].clear(),
            "بلا سجلّ ترخيص",
            id="تبعيةُ إنتاجٍ بلا سجلّ (انحرافٌ عن `requirements-prod.txt`)",
        ),
        pytest.param(
            lambda p: p["production_dependencies"][0].update({"license": "AGPL-3.0"}),
            "عنقود عميل",
            id="رخصةٌ قويةُ الاشتقاق مُعلَنةٌ مقبولةً على عنقود العميل",
        ),
        pytest.param(
            lambda p: p["upstream_sources"][0].update({"reviewed_on": "2019-01-01"}),
            "أقدمُ من نافذة المراجعة",
            id="ادّعاءٌ مؤرَّخٌ منقضٍ يمرّ أخضر",
        ),
        pytest.param(
            lambda p: p["upstream_sources"][0].update({"reviewed_on": "العامُ القادم"}),
            "بلا `reviewed_on`",
            id="تاريخٌ ليس بصيغةٍ قابلة للتحقّق",
        ),
        pytest.param(
            lambda p: p["upstream_sources"][0].pop("commercial_use"),
            "خارج القاموس",
            id="خانةٌ فارغةٌ تُقرأ نجاحاً",
        ),
    ],
)
def test_gate_blocks_each_broken_contracts(tmp_path: Path, mutate: Any, expected_text: str) -> None:
    root = _build_fixture(tmp_path / "repo")
    result = _break(root, mutate)
    assert result.returncode == 1, f"البوّابة مرّت على عقدٍ مكسور:\n{result.stdout}\n{result.stderr}"
    assert expected_text in result.stdout, f"الرسالة لا تُسمّي البند المكسور:\n{result.stdout}"


def test_gate_blocks_untracked_binary(tmp_path: Path) -> None:
    """ملفٌّ ثنائيٌّ يُضاف إلى الشجرة بلا سجلّ توزيع ⇒ أحمر (الاتجاه الذي لا تحرسه بوّابة)."""
    root = _build_fixture(tmp_path / "repo")
    (root / "docs/evidence/contract.pdf").write_bytes(b"%PDF-1.7")
    subprocess.run(["git", "add", "-A"], cwd=root, check=True, capture_output=True, text=True)
    result = _run_gate(root)
    assert result.returncode == 1
    assert "بلا سجلّ توزيع" in result.stdout


def test_gate_blocks_blocked_binary_without_remediation(tmp_path: Path) -> None:
    root = _build_fixture(tmp_path / "repo")

    def mutate(payload: dict[str, Any]) -> None:
        payload["tracked_binary_artifacts"][0].update(
            {"distribution": "NOT_CLEARED_FOR_REDISTRIBUTION"}
        )

    result = _break(root, mutate)
    assert result.returncode == 1
    assert "remediation_ar" in result.stdout


def test_gate_blocks_missing_register(tmp_path: Path) -> None:
    """غيابُ السجلّ ليس نظافة: بوّابةٌ فقدت مصدرَها تُبرّئ شجرةً لم تفحصها (D-208 §6)."""
    root = _build_fixture(tmp_path / "repo")
    (root / "docs/governance/ASSET_LICENSE_CLEARANCE.json").unlink()
    result = _run_gate(root)
    assert result.returncode == 1
    assert "ملفٌّ مفقود" in result.stdout


def test_gate_blocks_unreadable_register(tmp_path: Path) -> None:
    root = _build_fixture(tmp_path / "repo")
    (root / "docs/governance/ASSET_LICENSE_CLEARANCE.json").write_text(
        "{not json", encoding="utf-8"
    )
    result = _run_gate(root)
    assert result.returncode == 1
    assert "لا يمكن تحليل" in result.stdout


def test_fixture_of_a_clean_tree_passes(tmp_path: Path) -> None:
    """النموذجُ الصحيح يمرّ — والبرهانُ السلبي على عقدٍ صحيحٍ بلا معنى."""
    result = _run_gate(_build_fixture(tmp_path / "repo"))
    assert result.returncode == 0, result.stdout


def test_real_register_passes_the_gate() -> None:
    result = _run_gate(REPO_ROOT)
    assert result.returncode == 0, f"سجلُّ البراءة المودَع لا يجيز بوّابتَه:\n{result.stdout}"


def test_register_ships_evidence_method_per_row() -> None:
    """لا «بُراءةٌ بالحدس»: كلُّ سجلٍّ يسمّي وسيلةَ قراءة رخصته وتاريخَها."""
    register = json.loads(
        (REPO_ROOT / "docs/governance/ASSET_LICENSE_CLEARANCE.json").read_text(encoding="utf-8")
    )
    methods = {str(row.get("method") or "") for row in register["upstream_sources"]}
    assert methods <= {"github-api-license", "upstream-license-file-read", "github-api-404"}
    assert all(row.get("reviewed_on") for row in register["upstream_sources"])


def test_gate_is_wired_into_required_ci() -> None:
    """فارضٌ لا يشغّله أحدٌ شعارٌ لا حراسة (D-207): البوّابة خطوةٌ في `guardrails`."""
    workflow = (REPO_ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    assert RELATIVE in workflow, "البوّابة ليست مربوطةً بـ`guardrails` ⇒ لا تُشغَّل في required-ci"
