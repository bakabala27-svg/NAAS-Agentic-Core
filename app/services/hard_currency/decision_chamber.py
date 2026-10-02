"""غرفة القرار (D-306) — الطبقة الرقيقة بين مصادر المركز وآلة الحقيقة الاقتصادية.

الحساب كلّه في ``shared/research/economic_truth`` و``economic_decision``؛ هنا القراءة من
المصادر المحقونة، وحقن مُدقِّق نصّ المشتري (``tools`` — ``shared`` لا يستورده)، والامتناع.

**الغرفة تمتنع ولا تتجاوز:** إن رفض المُدقِّق جملةً واحدة من جملها هي، لا تُعرَض الشاشة —
503 بالسبب. شاشةٌ تقول ما لا يسنده دليلٌ أسوأ من شاشةٍ لا تقول شيئاً.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import date

from app.services.hard_currency.sources import (
    HardCurrencySources,
    InputRejectedError,
    SourceUnavailableError,
)
from shared.research.contact_ledger import LEDGER_REL, SCORECARD_REL
from shared.research.economic_decision import (
    QUESTIONS,
    build_brief,
    cross_examine,
    preview_outcome,
    render_sentences,
    sentence_problems,
)
from shared.research.economic_truth import build_snapshot
from shared.research.value_chain import CATALOG_REL, VALUE_CHAIN_REL
from tools.hard_currency_engine.buyer_claims import classify, findings

#: نصّ المشتري المعروض للاستجواب — جملٌ لا وثائق.
MAX_BUYER_TEXT_CHARS = 2000


def _wording(text: str) -> list[tuple[str, str, str]]:
    return [(item.rule, item.verdict, item.excerpt) for item in findings(text)]


def _classify(text: str) -> tuple[str, str, list[tuple[str, str]]]:
    verdict = classify(text)
    return verdict.verdict, verdict.reason_ar, [(f.rule, f.excerpt) for f in verdict.findings]


@dataclass(frozen=True)
class _Inputs:
    chain_doc: dict[str, object]
    ledger_text: str
    catalog: dict[str, object]
    scorecard: dict[str, object]


def _inputs(sources: HardCurrencySources) -> _Inputs:
    return _Inputs(
        chain_doc=sources.read_json(VALUE_CHAIN_REL),
        ledger_text=sources.read_text(LEDGER_REL),
        catalog=sources.read_json(CATALOG_REL),
        scorecard=sources.read_json(SCORECARD_REL),
    )


def _snapshot(sources: HardCurrencySources, today: date | None) -> dict[str, object]:
    inputs = _inputs(sources)
    return build_snapshot(
        chain_doc=inputs.chain_doc,
        ledger_text=inputs.ledger_text,
        catalog=inputs.catalog,
        scorecard=inputs.scorecard,
        root=sources.root,
        today=today or date.today(),
        wording=_wording,
    )


def _guard(sentences: Sequence[Mapping[str, object]], snapshot: Mapping[str, object]) -> None:
    evidence = snapshot.get("evidence")
    problems = sentence_problems(sentences, evidence if isinstance(evidence, list) else [])
    if problems:
        raise SourceUnavailableError(
            "الغرفة امتنعت: جملٌ تتجاوز دليلها — " + " · ".join(problems[:3])
        )


def chamber(sources: HardCurrencySources, *, today: date | None = None) -> dict[str, object]:
    """الشاشة الأولى: الحقيقة، والموجز، والجمل — أو امتناعٌ بسببه."""
    snapshot = _snapshot(sources, today)
    brief = build_brief(snapshot)
    sentences = render_sentences(snapshot, brief)
    _guard(sentences, snapshot)
    return {
        "snapshot": snapshot,
        "brief": brief,
        "sentences": sentences,
        "questions": list(QUESTIONS),
    }


def examine(
    sources: HardCurrencySources,
    question: str,
    text: str | None,
    *,
    today: date | None = None,
) -> dict[str, object]:
    if question not in QUESTIONS:
        raise InputRejectedError(422, f"سؤالٌ خارج المجموعة المغلقة: {question}")
    if question == "say_to_buyer" and not (text or "").strip():
        raise InputRejectedError(422, "say_to_buyer يتطلّب نصّاً")
    if text is not None and len(text) > MAX_BUYER_TEXT_CHARS:
        raise InputRejectedError(413, f"النصّ أطول من {MAX_BUYER_TEXT_CHARS} حرفاً")
    snapshot = _snapshot(sources, today)
    answer = cross_examine(
        question, snapshot, build_brief(snapshot), text=text, classify_text=_classify
    )
    sentences = answer.get("sentences")
    _guard(sentences if isinstance(sentences, list) else [], snapshot)
    return {"verdict": None, "findings": None, **answer}


def preview(
    sources: HardCurrencySources, row: Mapping[str, str], *, today: date | None = None
) -> dict[str, object]:
    """⛔ لا كتابة: السطر والفرق و``written: false`` — المالك يلتزم عبر git."""
    inputs = _inputs(sources)
    return preview_outcome(
        row=row,
        chain_doc=inputs.chain_doc,
        ledger_text=inputs.ledger_text,
        catalog=inputs.catalog,
        scorecard=inputs.scorecard,
        root=sources.root,
        today=today or date.today(),
        wording=_wording,
    )
