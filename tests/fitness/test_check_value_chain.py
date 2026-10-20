"""البرهان السلبي لبوّابة سلسلة القيمة (D-305 · D-270 L4): كلّ خرقٍ يُحمِّرها.

كلّ حالة تبني مستودعاً مصغّراً، وتكسره عمداً بطريقةٍ واحدة، وتؤكّد أنّ ``check_value_chain``
يُرجع قائمة فشلٍ غير فارغة — ثمّ أنّ النسخة السليمة تمرّ (بوّابةٌ لا تمرّ أبداً ليست بوّابة).
"""

from __future__ import annotations

import copy
import importlib.util
import json
from datetime import date
from pathlib import Path
from types import ModuleType

import pytest

from shared.research.contact_ledger import COLUMNS, parse_ledger
from shared.research.value_chain import compute_derived

REPO_ROOT = Path(__file__).resolve().parents[2]
TODAY = date(2026, 10, 1)


def _gate() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "check_value_chain", REPO_ROOT / "scripts" / "fitness" / "check_value_chain.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


check_value_chain = _gate()


def _ledger(rows: list[dict[str, str]]) -> str:
    lines = [",".join(COLUMNS)]
    lines += [",".join(row.get(column, "") for column in COLUMNS) for row in rows]
    return "\n".join(lines) + "\n"


_EMAIL = {
    "date": "2026-09-22",
    "target_ref": "TARGETS.csv#id=1",
    "entity": "Firm",
    "country": "FR",
    "channel": "email",
    "action": "EMAIL_SENT",
}


def _base_doc() -> dict[str, object]:
    links: dict[str, object] = {
        "1": {"status": "REACHED", "evidence": ["evidence/observation.md"]},
        "2": {"status": "REACHED", "evidence": ["evidence/observation.md"]},
        "3": {
            "status": "REACHED",
            "evidence": ["evidence/sample.csv"],
            "contains_user_data": False,
        },
        "4": {"status": "REACHED", "evidence": ["evidence/test_tool.py"]},
        "5": {"status": "NOT_REACHED", "reason_ar": "لا ملفّ حقيقي"},
        "6": {"status": "NOT_REACHED", "reason_ar": "تابع"},
    }
    return {
        "paths": [
            {
                "id": "P-1",
                "title_ar": "مسارٌ اختباري",
                "source": "evidence/observation.md",
                "catalog_id": "line-1",
                "ledger_routes": ["TARGETS.csv"],
                "links": links,
            }
        ]
    }


def _write_repo(
    root: Path,
    doc: dict[str, object],
    *,
    ledger_rows: list[dict[str, str]] | None = None,
    catalog_status: str = "PROPOSED",
    offer_fields: dict[str, object] | None = None,
    rederive: bool = True,
) -> Path:
    (root / "evidence").mkdir(parents=True, exist_ok=True)
    for name in ("observation.md", "sample.csv", "test_tool.py"):
        (root / "evidence" / name).write_text("x\n", encoding="utf-8")
    commercial = root / "docs" / "commercial"
    (commercial / "outreach").mkdir(parents=True, exist_ok=True)
    ledger_text = _ledger(ledger_rows if ledger_rows is not None else [_EMAIL])
    (commercial / "outreach" / "CONTACT_LEDGER.csv").write_text(ledger_text, encoding="utf-8")
    catalog = {"offers": [{"id": "line-1", "status": catalog_status, **(offer_fields or {})}]}
    (commercial / "OFFER_CATALOG.json").write_text(json.dumps(catalog), encoding="utf-8")
    if rederive:
        doc = copy.deepcopy(doc)
        rows = parse_ledger(ledger_text, today=TODAY)
        doc["derived"] = compute_derived(doc, rows, built_before_demand=_FIXTURE_DEBT)
    (commercial / "VALUE_CHAIN.json").write_text(
        json.dumps(doc, ensure_ascii=False), encoding="utf-8"
    )
    return root


#: The fixture path P-1 declares code links 3 and 4 with no demand evidence, the same state
#: as the ten real paths D-321 found built before demand. It stands in their frozen debt.
_FIXTURE_DEBT = {"P-1": 4}


def _failures(root: Path, *, built_before_demand: dict[str, int] | None = None) -> list[str]:
    debt = _FIXTURE_DEBT if built_before_demand is None else built_before_demand
    return check_value_chain.run(root, today=TODAY, built_before_demand=debt)


def test_clean_repo_passes(tmp_path: Path) -> None:
    assert _failures(_write_repo(tmp_path, _base_doc())) == []


def test_real_repository_passes() -> None:
    assert check_value_chain.run() == []


def test_empty_link_is_rejected(tmp_path: Path) -> None:
    doc = _base_doc()
    del doc["paths"][0]["links"]["3"]  # type: ignore[index]
    failures = _failures(_write_repo(tmp_path, doc))
    assert len(failures) >= 1


def test_missing_evidence_file_is_rejected(tmp_path: Path) -> None:
    doc = _base_doc()
    doc["paths"][0]["links"]["4"]["evidence"] = ["evidence/deleted.py"]  # type: ignore[index]
    failures = _failures(_write_repo(tmp_path, doc))
    assert len(failures) >= 1


def test_manual_ledger_link_is_rejected(tmp_path: Path) -> None:
    doc = _base_doc()
    doc["paths"][0]["links"]["7"] = {"status": "REACHED", "evidence": ["evidence/observation.md"]}  # type: ignore[index]
    failures = _failures(_write_repo(tmp_path, doc))
    assert len(failures) >= 1


def test_hand_written_classification_is_rejected(tmp_path: Path) -> None:
    root = _write_repo(tmp_path, _base_doc())
    path = root / "docs" / "commercial" / "VALUE_CHAIN.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    doc["derived"]["paths"][0]["classification"] = "commercial_evidence"
    path.write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")
    assert len(_failures(root)) >= 1


def test_catalog_status_above_evidence_is_rejected(tmp_path: Path) -> None:
    failures = _failures(_write_repo(tmp_path, _base_doc(), catalog_status="DISCOVERY"))
    assert len(failures) >= 1


def test_forbidden_wording_is_rejected(tmp_path: Path) -> None:
    doc = _base_doc()
    doc["paths"][0]["title_ar"] = "منتجٌ ثوري للعملة الصعبة"  # type: ignore[index]
    failures = _failures(_write_repo(tmp_path, doc))
    assert len(failures) >= 1


def test_prohibition_line_may_name_the_forbidden_word(tmp_path: Path) -> None:
    doc = _base_doc()
    doc["paths"][0]["links"]["5"]["reason_ar"] = "⛔ لا يُوصَف ثورياً قبل الدليل"  # type: ignore[index]
    assert _failures(_write_repo(tmp_path, doc)) == []


def test_unrouted_ledger_row_is_rejected(tmp_path: Path) -> None:
    stray = dict(_EMAIL, target_ref="ELSEWHERE.csv#id=9")
    failures = _failures(_write_repo(tmp_path, _base_doc(), ledger_rows=[_EMAIL, stray]))
    assert len(failures) >= 1


def test_privacy_must_be_declared_not_assumed(tmp_path: Path) -> None:
    doc = _base_doc()
    del doc["paths"][0]["links"]["3"]["contains_user_data"]  # type: ignore[index]
    failures = _failures(_write_repo(tmp_path, doc))
    assert len(failures) >= 1


def test_unreadable_input_is_reported_not_passed(tmp_path: Path) -> None:
    root = _write_repo(tmp_path, _base_doc())
    (root / "docs" / "commercial" / "VALUE_CHAIN.json").write_text("{not json", encoding="utf-8")
    assert len(_failures(root)) >= 1


@pytest.mark.parametrize("status", ["PILOT", "PAID_PROOF"])
def test_money_statuses_need_money_in_the_ledger(tmp_path: Path, status: str) -> None:
    failures = _failures(_write_repo(tmp_path, _base_doc(), catalog_status=status))
    assert len(failures) >= 1


# ── الأطلس (D-319): ما يُكتب في الكتالوج وسلسلة القيمة لا يتجاوز دليله ─────────────


def _has(failures: list[str], marker: str) -> bool:
    return any(marker in failure for failure in failures)


def test_offer_ready_needs_the_nine_offer_fields(tmp_path: Path) -> None:
    """الأطلس §5.1: عرضٌ قابلٌ للشراء يسمّي العميل والمشكلة والنتيجة والحدود والمدّة والسعر
    وشروط القبول وطريقة التسليم وطريقة التقييم — وإلّا فليس عرضاً."""
    failures = _failures(_write_repo(tmp_path, _base_doc(), catalog_status="OFFER_READY"))
    assert _has(failures, "الأطلس §5.1")


def test_offer_ready_waits_for_legal_and_rail(tmp_path: Path) -> None:
    """الأطلس §12.1 و§0.2: لا ثمن يُعرَض قبل أن يُثبَت أنّ البيع قانونيّ وأنّ المال يصل."""
    failures = _failures(_write_repo(tmp_path, _base_doc(), catalog_status="OFFER_READY"))
    assert _has(failures, "C-LEGAL") and _has(failures, "C-RAIL")


def test_repeatable_needs_a_margin_and_a_buyer_who_paid_twice(tmp_path: Path) -> None:
    """الأطلس §0.3: «قابلٌ للتكرار» يتطلّب هامشاً مُعلَناً وعميلاً دفع مرّتين."""
    failures = _failures(_write_repo(tmp_path, _base_doc(), catalog_status="REPEATABLE"))
    assert _has(failures, "gross_margin") and _has(failures, "دفع مرّتين")


def test_link_5_must_say_what_it_proves_and_what_it_does_not(tmp_path: Path) -> None:
    """الأطلس: لا تضع علامة «مثبت» لمجرّد وجود ملفٍّ أو نتيجة اختبارٍ محلية."""
    doc = _base_doc()
    doc["paths"][0]["links"]["5"] = {  # type: ignore[index]
        "status": "REACHED",
        "evidence": ["evidence/test_tool.py"],
    }
    failures = _failures(_write_repo(tmp_path, doc))
    assert _has(failures, "proves_ar") and _has(failures, "does_not_prove_ar")


def test_link_6_needs_ledger_lines_from_three_replying_entities(tmp_path: Path) -> None:
    """الأطلس §3.4: أدلّةٌ متكرّرة لدى عدّة عملاء مستقلّين — من السجلّ لا من ملفّ."""
    doc = _base_doc()
    links = doc["paths"][0]["links"]  # type: ignore[index]
    links["5"] = {  # type: ignore[index]
        "status": "REACHED",
        "evidence": ["evidence/test_tool.py"],
        "proves_ar": "نتيجةٌ على ملفٍّ لم نكتبه",
        "does_not_prove_ar": "أنّ مشترياً يدفع",
    }
    links["6"] = {"status": "REACHED", "evidence": ["evidence/observation.md"]}  # type: ignore[index]
    failures = _failures(_write_repo(tmp_path, doc))
    assert _has(failures, "LEDGER:") and _has(failures, "as_of") and _has(failures, "3 ")


# ── D-321 «الألم أولاً»: لا حلقة كودٍ قبل ألمٍ يُبحث عن حلّه ودافعٍ موجود ──────────────


def _demand(**legs: object) -> dict[str, object]:
    absent = {"status": "NOT_REACHED", "reason_ar": "لا دليل بعد"}
    return {leg: legs.get(leg, absent) for leg in ("pain", "active_search", "payer")}


def _source(n: int, **extra: str) -> dict[str, str]:
    return {"url": f"https://example.org/thread/{n}", "date": "2026-10-01", "fact": "شكوى", **extra}


_PAYER = {"status": "REACHED", "evidence": [_source(9, price="49 EUR/month")]}


def _replies(count: int) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for n in range(1, count + 1):
        sent = dict(_EMAIL, target_ref=f"TARGETS.csv#id={n}", entity=f"Firm {n}")
        rows += [sent, dict(sent, date="2026-09-23", action="REPLY_RECEIVED")]
    return rows


def test_a_code_link_declared_after_the_law_needs_demand(tmp_path: Path) -> None:
    """A path outside the frozen debt may not declare links 3-5 before buyers spoke."""
    failures = _failures(_write_repo(tmp_path, _base_doc()), built_before_demand={})
    assert _has(failures, "D-321")


def test_a_frozen_path_cannot_raise_its_code_link(tmp_path: Path) -> None:
    failures = _failures(_write_repo(tmp_path, _base_doc()), built_before_demand={"P-1": 3})
    assert _has(failures, "D-321")


def test_the_frozen_debt_shrinks_in_both_directions(tmp_path: Path) -> None:
    """A debt entry for a path that is gone, or above what the path declares, is red."""
    root = _write_repo(tmp_path, _base_doc())
    assert _has(_failures(root, built_before_demand={"P-1": 4, "P-GONE": 3}), "P-GONE")
    assert _has(_failures(root, built_before_demand={"P-1": 5}), "D-321")


def test_three_replying_entities_and_a_payer_license_code(tmp_path: Path) -> None:
    doc = _base_doc()
    doc["paths"][0]["demand"] = _demand(payer=_PAYER)  # type: ignore[index]
    root = _write_repo(tmp_path, doc, ledger_rows=_replies(3))
    assert not _has(_failures(root, built_before_demand={}), "D-321")


def test_two_replying_entities_do_not_license_code(tmp_path: Path) -> None:
    doc = _base_doc()
    doc["paths"][0]["demand"] = _demand(payer=_PAYER)  # type: ignore[index]
    root = _write_repo(tmp_path, doc, ledger_rows=_replies(2))
    assert _has(_failures(root, built_before_demand={}), "D-321")


def test_a_licensed_path_must_leave_the_frozen_debt(tmp_path: Path) -> None:
    doc = _base_doc()
    doc["paths"][0]["demand"] = _demand(payer=_PAYER)  # type: ignore[index]
    root = _write_repo(tmp_path, doc, ledger_rows=_replies(3))
    assert _has(_failures(root), "BUILT_BEFORE_DEMAND")


def test_a_reached_leg_needs_dated_sourced_evidence(tmp_path: Path) -> None:
    doc = _base_doc()
    doc["paths"][0]["demand"] = _demand(  # type: ignore[index]
        pain={"status": "REACHED", "evidence": [_source(1), _source(2)]},
        active_search={"status": "REACHED", "evidence": [{"url": "not-a-url", "fact": "x"}]},
        payer={"status": "REACHED", "evidence": [_source(3)]},
    )
    failures = _failures(_write_repo(tmp_path, doc))
    assert _has(failures, "pain") and _has(failures, "active_search") and _has(failures, "price")


def test_a_leg_not_reached_must_say_why(tmp_path: Path) -> None:
    doc = _base_doc()
    doc["paths"][0]["demand"] = _demand(pain={"status": "NOT_REACHED"})  # type: ignore[index]
    assert _has(_failures(_write_repo(tmp_path, doc)), "pain")
