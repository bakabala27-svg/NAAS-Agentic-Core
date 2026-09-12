#!/usr/bin/env python3
"""قياسُ دبوس المعيار (BPIN) — درجتان معياريتان من طرفَين أوّليين على الحزمة نفسها.

**لماذا هذا القياس موجود.** الجولة 04 وجدت أنّ `ReportPin` في AHW **محكومةُ المجال**: صُمّمت
لدرجةٍ معيارية، وتطبيقُها على واقعةٍ تاريخية أو توقّع سوق يُنتج `UNPINNED` كاذباً (`H59`).
وبقي ذلك **ادّعاءً عن الأداة** لأنّه لم يُختبر في مجالها الصحيح. هنا يُختبر: حزمةُ ExploitGym
(898 مهمة، طرفٌ أوّل أكاديمي 2026-05-13) درجاتٌ معياريةٌ حقيقية بنموذجٍ وحزامٍ وميزانيةٍ
وتكوينِ حماية — أي **كلّ ما يطلبه الدبوس**. فإن أنتج الدبوسُ هنا حكماً مُدرَّجاً (لا
`UNPINNED` منحطّاً)، فـ`H59` مُثبتةٌ بالاستعمال لا بالحجّة.

**وما يُقاس.** أربعةُ أشياء لا تُقال بالرأي:
1. أثرُ الحمايات القياسية على النجاح المُقاس (369 ← 69)، وتركّزُ الباقي.
2. أوّلُ مرساةِ **CPST** مقوّمة بالدولار من طرفٍ أوّل في الدراسة كلّها — و`D-290 L7` يُلزم
   CPST في كلّ مقارنةِ كلفة، ولم يكن عندنا منها شيء (كان عندنا أجرٌ بالساعة فقط).
3. تعارضُ طرفَين أوّليين على نسبةِ «لم يُحلّ» في الحزمة نفسها (22.05% مقابل 80.29%)،
   والمصالحةُ **بالدبوس** لا بالتسوية.
4. تناقضُ المصدر الأوّل مع نفسه (الجدول 1 يقول 157 عند ساعتَين، والشكل 5 يقول 127).

**⛔ حدودٌ لا تُتجاوز.** لا شيفرةَ استغلال، ولا إعادةَ إنتاجِ ناقل، ولا تشغيلَ نموذج، ولا
قياسَ عميل. ما يُقاس **أرقامٌ منشورةٌ مجمّعة** عن أثر الحمايات والكلفة — وهي جهةُ الدفاع.
و`exploits_reproduced = 0` حقلٌ في المخرَج لا جملةٌ في المقدمة.

⛔ صفرُ تبعياتٍ خارج المكتبة القياسية. يُشغَّل من جذر المستودع:
    python3 scripts/research/measure_benchmark_pin.py [--check]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import dataclass
from datetime import UTC, date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from shared.research.assurance_window import (
    FRESH_DAYS,
    MAX_REPORT_AGE_DAYS,
    ReportPin,
    evaluate_pin,
)

OUT = ROOT / "docs" / "research" / "BPIN_MEASUREMENTS.json"

#: تاريخُ المراجعة. ⛔ لا يُقرأ من الساعة: فكلّ عمرٍ في الملفّ يُنسب إليه صراحةً.
AS_OF = date(2026, 9, 12)

#: الحزمة: طرفٌ أوّل أكاديمي (Berkeley RDI + MPI-SP + UCSB + ASU + Anthropic + OpenAI + Google).
SUITE = "ExploitGym"
SUITE_VERSION = "arXiv:2605.11086v1 / sunblaze-ucb/exploitgym"
SUITE_ISSUED_ON = date(2026, 5, 13)
SUITE_INSTANCES = 898
#: تقسيمُ المجالات منشورٌ في المصدر الأوّل؛ ومجموعُه يجب أن يساوي عدد المهامّ.
DOMAIN_INSTANCES = {"USERSPACE": 520, "BROWSER_V8": 185, "KERNEL": 193}

SRC_BERKELEY = (
    "Berkeley RDI — «ExploitGym: Can AI Agents Turn Security Vulnerabilities into Real Attacks?» "
    "(2026-05-13) + arXiv:2605.11086 — طرفٌ أوّل يملك الحزمةَ ومنهجيةَ القياس"
)
SRC_OPENAI = (
    "OpenAI — «The Hugging Face incident and the road ahead» (2026-08-26) — طرفٌ أوّلٌ "
    "عن تشغيله الداخلي على الحزمة نفسها، ⛔ وليس مالكُ الحزمة"
)


class BenchmarkPinError(ValueError):
    """خطأُ قياسٍ صريح — ⛔ لا قيمةَ افتراضية تُبتلع."""


@dataclass(frozen=True)
class SuiteRun:
    """تشغيلٌ واحد مُدبَّس: زوج (نموذج، وكيل) تحت ميزانيةٍ وتكوينِ حمايةٍ مُسمّاة.

    ⚠️ `safeguard_config` هنا **مركّبٌ من محورَين متعامدَين**: مرشّحاتُ المزوّد، وحماياتُ
    الهدف. و`ReportPin` تحمل حقلاً واحداً للحماية ⇒ التركيبُ لازم، وكونُه لازماً **نتيجةٌ**
    عن الأداة لا تفصيلُ إدخال (انظر `results.pin_field_limitations`).
    """

    model_id: str
    harness: str
    safeguard_config: str
    adversary_budget_minutes: int
    successes: int
    by_domain: tuple[int, int, int]  # (userspace, browser_v8, kernel)
    with_mitigations: tuple[int, int, int] | None
    cpst_usd: float | None
    cost_full_usd: float | None
    time_min_per_success: float | None
    llm_calls_per_success: float | None
    flags_captured: int | None = None
    successes_on_intended: int | None = None

    def __post_init__(self) -> None:
        if self.successes < 0:
            raise BenchmarkPinError(f"{self.model_id}: نجاحٌ سالب")
        if sum(self.by_domain) != self.successes:
            raise BenchmarkPinError(
                f"{self.model_id}: مجموعُ المجالات {sum(self.by_domain)} ≠ النجاحَ الكلي {self.successes}"
            )
        if self.successes > SUITE_INSTANCES:
            raise BenchmarkPinError(f"{self.model_id}: نجاحٌ يتجاوز حجمَ الحزمة")
        if self.adversary_budget_minutes <= 0:
            raise BenchmarkPinError(f"{self.model_id}: ميزانيةٌ غير موجبة")
        if self.with_mitigations is not None and sum(self.with_mitigations) > self.successes:
            raise BenchmarkPinError(
                f"{self.model_id}: النجاحُ مع الحمايات {sum(self.with_mitigations)} "
                f"يتجاوز النجاحَ بدونها {self.successes} — ⛔ الحماياتُ لا تزيد النجاح"
            )
        if self.cpst_usd is not None and self.cpst_usd <= 0:
            raise BenchmarkPinError(f"{self.model_id}: CPST غير موجبة")
        if (self.flags_captured is None) != (self.successes_on_intended is None):
            raise BenchmarkPinError(f"{self.model_id}: علمٌ وانتحالٌ يُذكران معاً أو لا يُذكران")
        if self.flags_captured is not None and self.successes_on_intended > self.flags_captured:
            raise BenchmarkPinError(
                f"{self.model_id}: نجاحٌ على الهدف {self.successes_on_intended} يتجاوز الأعلامَ "
                f"المقبوضة {self.flags_captured}"
            )

    @property
    def mitigated_total(self) -> int | None:
        return None if self.with_mitigations is None else sum(self.with_mitigations)

    def pin(self) -> ReportPin:
        return ReportPin(
            model_id=self.model_id,
            harness=self.harness,
            safeguard_config=self.safeguard_config,
            suite_version=SUITE_VERSION,
            adversary_budget=self.adversary_budget_minutes,
            issued_on=SUITE_ISSUED_ON,
            suite=SUITE,
            score_points=float(self.successes),
        )


#: ⛔ كلّ رقمٍ هنا منسوبٌ إلى الجدول/الشكل الذي جاء منه في المصدر الأوّل.
RUNS: tuple[SuiteRun, ...] = (
    SuiteRun(
        "claude-mythos-preview",
        "claude-code",
        "FILTERS_DISABLED+MITIGATIONS_OFF",
        120,
        157,
        (107, 38, 12),
        (25, 17, 3),
        None,
        None,
        54.7,
        225.5,
        flags_captured=226,
        successes_on_intended=157,
    ),
    SuiteRun(
        "claude-opus-4.6",
        "claude-code",
        "FILTERS_DISABLED+MITIGATIONS_OFF",
        120,
        15,
        (12, 2, 1),
        (0, 0, 0),
        8.08,
        21.76,
        18.1,
        102.3,
    ),
    SuiteRun(
        "claude-opus-4.7",
        "claude-code",
        "FILTERS_DISABLED+MITIGATIONS_OFF",
        120,
        7,
        (4, 3, 0),
        (0, 0, 0),
        8.64,
        3.40,
        22.1,
        102.0,
    ),
    SuiteRun(
        "gemini-3.1-pro",
        "gemini-cli",
        "FILTERS_DISABLED+MITIGATIONS_OFF",
        120,
        12,
        (10, 2, 0),
        (0, 0, 0),
        8.56,
        9.02,
        51.1,
        169.5,
    ),
    SuiteRun(
        "glm-5.1",
        "claude-code",
        "FILTERS_DISABLED+MITIGATIONS_OFF",
        120,
        4,
        (4, 0, 0),
        (0, 0, 0),
        3.75,
        6.39,
        63.3,
        148.6,
    ),
    SuiteRun(
        "gpt-5.4",
        "codex-cli",
        "FILTERS_DISABLED+MITIGATIONS_OFF",
        120,
        54,
        (38, 15, 1),
        (2, 0, 1),
        12.20,
        25.43,
        51.1,
        220.1,
    ),
    SuiteRun(
        "gpt-5.5",
        "codex-cli",
        "FILTERS_DISABLED+MITIGATIONS_OFF",
        120,
        120,
        (71, 27, 22),
        (10, 3, 8),
        22.99,
        34.55,
        49.6,
        256.8,
        flags_captured=210,
        successes_on_intended=120,
    ),
)

#: الشكل 4: تقاطعُ مجموعات النجاح — ويُستعمل اشتقاقياً لا نقلاً.
VENN = {"exclusive_mythos": 56, "exclusive_gpt55": 26, "shared_top_two": 91, "exclusive_others": 4}

#: الشكل 5: حساسيةُ الميزانية (طرفٌ أوّل، والمصدرُ نفسه يعلن أنّ الساعتَين تُبخسان).
BUDGET_CURVE = {
    "mythos_at_120min": 127,
    "mythos_at_360min": 204,
    "opus46_plateau_minutes": 30,
    "opus46_plateau_value": 15,
}

#: مرشّحاتُ المزوّد الافتراضية على GPT-5.5 (الحاشية ‡ في الجدول 1).
SAFEGUARD_PAIR = {
    "model_id": "gpt-5.5",
    "harness": "codex-cli",
    "default_filters_successes": 0,
    "filters_disabled_successes": 120,
}

#: ادّعاءُ الطرف الأوّل الثاني عن الحزمة نفسها (OpenAI، تشغيلُه الداخلي).
OPENAI_UNSOLVED = {"never_solved": 198, "suite_total": SUITE_INSTANCES, "source": SRC_OPENAI}


def mitigation_effect(runs: tuple[SuiteRun, ...]) -> dict[str, object]:
    """أثرُ الحمايات القياسية على النجاح المُقاس — مجموعاً وتركّزاً وتصفيراً.

    ⛔ لا يُبلَّغ متوسطُ نسبةِ انخفاضٍ لكلّ زوج: فمتوسطُ نسبةٍ تشمل أصفاراً يُخفي أنّ أربعةً
    من سبعة أُصفرت تماماً. فالأصفارُ تُعدّ، والباقي يُنسب إلى صاحبه.
    """
    measured = [r for r in runs if r.with_mitigations is not None]
    if not measured:
        raise BenchmarkPinError("صفرُ تشغيلٍ بحماياتٍ مقيسة — لا أثرَ يُحسب")
    off = sum(r.successes for r in measured)
    on = sum(int(r.mitigated_total) for r in measured)
    if off == 0:
        raise BenchmarkPinError("صفرُ نجاحٍ بلا حمايات — لا مقامَ لنسبة")
    zeroed = sorted(r.model_id for r in measured if int(r.mitigated_total) == 0)
    residual = sorted(
        ((r.model_id, int(r.mitigated_total)) for r in measured if int(r.mitigated_total) > 0),
        key=lambda kv: -kv[1],
    )
    top_id, top_n = residual[0]
    return {
        "pairs_measured": len(measured),
        "successes_mitigations_off": off,
        "successes_mitigations_on": on,
        "reduction_factor": round(off / on, 4) if on else None,
        "residual_share": round(on / off, 6),
        "pairs_zeroed_count": len(zeroed),
        "pairs_zeroed": zeroed,
        "residual_by_pair": [{"model_id": m, "successes": n} for m, n in residual],
        "residual_top_pair": top_id,
        "residual_top_share": round(top_n / on, 6),
        "reading": (
            f"الحماياتُ القياسية (ASLR · canaries · V8 heap sandbox · KASLR) خفضت النجاحَ "
            f"المُقاس {off} ← {on} وأصفرت {len(zeroed)} من {len(measured)} أزواج تماماً. "
            f"والباقي متمركز: {top_id} يحمل {top_n}/{on} = {top_n / on:.2%}. ⇒ العبارةُ "
            "«الحماياتُ لا تكفي» صحيحةٌ إجمالاً **وخاطئةٌ تفصيلاً**: فهي تكفي تماماً لأربعةٍ "
            "من سبعة، ولا تكفي لأقواهم. وما يُباع هو التفصيلُ لا الإجمال."
        ),
        "source": SRC_BERKELEY + " — الجدول 2",
    }


def cpst_band(runs: tuple[SuiteRun, ...]) -> dict[str, object]:
    """أوّلُ مرساةِ CPST من طرفٍ أوّل — ⛔ والغائبُ يُعلَن فجوةً لا يُستكمل تقديراً."""
    disclosed = sorted(r.cpst_usd for r in runs if r.cpst_usd is not None)
    undisclosed = sorted(r.model_id for r in runs if r.cpst_usd is None)
    if not disclosed:
        raise BenchmarkPinError("صفرُ CPST مُفصَح عنها — لا نطاقَ يُحسب")
    low, high = disclosed[0], disclosed[-1]
    return {
        "unit": "USD_PER_SUCCESSFUL_TASK",
        "n_disclosed": len(disclosed),
        "n_undisclosed": len(undisclosed),
        "undisclosed_models": undisclosed,
        "band_usd": [low, high],
        "spread_factor": round(high / low, 4),
        "median_usd": round(disclosed[len(disclosed) // 2], 4)
        if len(disclosed) % 2
        else round((disclosed[len(disclosed) // 2 - 1] + disclosed[len(disclosed) // 2]) / 2, 4),
        "undisclosed_imputed": False,
        "doctrine_compliance": "D-290 L7: مقارنةُ الكلفة بـCPST لا بالأجر الساعي — وهذه أوّلُ مرساةٍ مُلتزمة",
        "reading": (
            f"نطاقُ CPST المُفصَح عنه [{low}, {high}] دولاراً لكلّ مهمةٍ ناجحة، بانتشارٍ "
            f"{high / low:.4f}× بين {len(disclosed)} أزواج. و{len(undisclosed)} غيرُ مُفصَحة "
            f"({', '.join(undisclosed)}) ⇒ ⛔ لم تُستكمل بمتوسطٍ ولا بتقدير: فمتوسطُ نطاقٍ "
            "ناقصٍ يُقرأ اكتمالاً. والانتشارُ هنا **حقيقيٌّ لا ضجيجَ قياس**: فهو بين أزواجٍ "
            "مختلفةٍ لا بين تقديراتٍ للكمية نفسها — فلا يُعامل كتشتّتِ سوق الجولة 04."
        ),
        "source": SRC_BERKELEY + " — الجدول 1 (Cost (USD)/Succ.)",
    }


def off_target_rate(runs: tuple[SuiteRun, ...]) -> dict[str, object]:
    """معدّلُ النجاح على **غير** الثغرة المقصودة — الدليلُ على تباعد المُقيِّم عن المواصفة.

    وهذا هو الظاهرةُ نفسها التي بنى عليها الطرفُ الأوّل حكماً (agent-as-a-judge)، ورصدتها
    الجولة 04 من رواية المختبر وحده. هنا **طرفٌ مستقلٌّ يقيسها بأرقام**.
    """
    rows = []
    for r in runs:
        if r.flags_captured is None:
            continue
        off = r.flags_captured - int(r.successes_on_intended)
        rows.append(
            {
                "model_id": r.model_id,
                "flags_captured": r.flags_captured,
                "successes_on_intended": int(r.successes_on_intended),
                "off_target_count": off,
                "off_target_share": round(off / r.flags_captured, 6),
            }
        )
    if not rows:
        raise BenchmarkPinError("صفرُ زوجٍ بأعلامٍ مقبوضة — لا معدّلَ يُحسب")
    rows.sort(key=lambda d: -d["off_target_share"])
    return {
        "pairs_measured": len(rows),
        "per_pair": rows,
        "max_off_target_share": rows[0]["off_target_share"],
        "min_off_target_share": rows[-1]["off_target_share"],
        "reading": (
            "المصدرُ الأوّل بنى حكماً (agent-as-a-judge) **لهذا السبب نصّاً**: «agents frequently "
            "succeed by exploiting a different bug than the intended one». فالعلمُ المقبوض ليس "
            "المقياسَ المنفَّذ — وهي الظاهرةُ نفسها التي سجّلتها الجولة 04 من رواية المختبر "
            "(`grader_divergent = true`). وهنا يقيسها طرفٌ ثالثٌ مستقلّ ⇒ **التباعدُ بنيويٌّ "
            "في قياس الاستغلال، لا عيبٌ في مختبرٍ واحد**."
        ),
        "source": SRC_BERKELEY + " — «The Interesting Bits» + الشكل 3 + arXiv الجدول 4",
    }


def unsolved_conflict(runs: tuple[SuiteRun, ...]) -> dict[str, object]:
    """تعارُضُ طرفَين أوّليين على الحزمة نفسها — والمصالحةُ بالدبوس لا بالتسوية.

    ⛔ لا يُؤخذ متوسطٌ ولا يُرجَّح طرف: فكلاهما أوّل، والفرقُ يُفسَّره اختلافُ الدبوس
    (النموذج · الميزانية · الحزام · الحماية)، وهو تفسيرٌ **يُختبر** لا يُدّعى.
    """
    union_solved = (
        VENN["exclusive_mythos"]
        + VENN["exclusive_gpt55"]
        + VENN["shared_top_two"]
        + VENN["exclusive_others"]
    )
    berkeley_unsolved = SUITE_INSTANCES - union_solved
    oai = OPENAI_UNSOLVED["never_solved"]
    if OPENAI_UNSOLVED["suite_total"] != SUITE_INSTANCES:
        raise BenchmarkPinError("الحجمان مختلفان ⇒ ⛔ ليستا الكمّية نفسها ولا تُقارنان")
    berkeley_share = berkeley_unsolved / SUITE_INSTANCES
    oai_share = oai / SUITE_INSTANCES
    return {
        "suite": SUITE,
        "suite_instances": SUITE_INSTANCES,
        "domain_instances": dict(DOMAIN_INSTANCES),
        "domain_sum_matches_instances": sum(DOMAIN_INSTANCES.values()) == SUITE_INSTANCES,
        "berkeley_union_solved": union_solved,
        "berkeley_unsolved": berkeley_unsolved,
        "berkeley_unsolved_share": round(berkeley_share, 6),
        "openai_never_solved": oai,
        "openai_never_solved_share": round(oai_share, 6),
        "share_spread_factor": round(berkeley_share / oai_share, 4),
        "reconciled": False,
        "reconciliation_basis": "PIN_DIFFERENCE_NOT_AVERAGE",
        "pin_axes_that_differ": [
            "model_id — تشغيلُ OpenAI الداخلي (IM1/HPIM بحجمٍ مقاربٍ لـGPT-5.6 Sol) مقابل سبعة أزواجٍ عامة",
            "adversary_budget — الجدولُ معلَنٌ عند 120 دقيقة، وميزانيةُ التشغيل الداخلي غيرُ منشورة",
            "harness — claude-code/codex-cli/gemini-cli مقابل حزامٍ داخلي غير مُسمّى",
            "safeguard_config — المرشّحاتُ معطَّلةٌ في السبعة، وحالُها في التشغيل الداخلي غيرُ منشور",
        ],
        "reading": (
            f"طرفان أوّلان، حزمةٌ واحدة (898)، ونسبتا «لم يُحلّ» متباعدتان {berkeley_share:.2%} "
            f"مقابل {oai_share:.2%} — انتشارٌ {berkeley_share / oai_share:.4f}×. ⛔ ليس "
            "تناقضاً ولا يُؤخذ متوسطُه: فالدبابيسُ مختلفة في أربعة محاور، وثلاثةٌ منها غيرُ "
            "منشور لدى الطرف الثاني. ⇒ الرقمُ «لم يُحلّ من 898» **بلا دبوسٍ غيرُ قابلٍ "
            "للاقتباس أصلاً**، وهذا برهانٌ على `H59` في مجال الدبوس الصحيح."
        ),
        "source": f"{SRC_BERKELEY} — الشكل 4 · {SRC_OPENAI}",
    }


def budget_sensitivity() -> dict[str, object]:
    """حساسيتُها للميزانية — والمصدرُ الأوّل نفسه يعلن أنّ ميزانيتَه تُبخس الأقوى."""
    a, b = BUDGET_CURVE["mythos_at_120min"], BUDGET_CURVE["mythos_at_360min"]
    if a <= 0:
        raise BenchmarkPinError("ميزانيةٌ أساسيةٌ صفرية — لا نسبةَ نمو")
    return {
        "model_id": "claude-mythos-preview",
        "successes_at_120min": a,
        "successes_at_360min": b,
        "growth_share": round((b - a) / a, 6),
        "plateau_declared": False,
        "weaker_pair": {
            "model_id": "claude-opus-4.6",
            "plateau_minutes": BUDGET_CURVE["opus46_plateau_minutes"],
            "plateau_value": BUDGET_CURVE["opus46_plateau_value"],
        },
        "self_declared_undercount": True,
        "reading": (
            f"الميزانيةُ محورُ دبوسٍ لا تفصيل: 120 دقيقة ← 360 دقيقة رفعت النجاح {a} ← {b} "
            f"(+{(b - a) / a:.2%}) **بلا هضبة مُعلَنة**، بينما أضعفُ الأزواج استقرّ عند "
            f"{BUDGET_CURVE['opus46_plateau_value']} خلال "
            f"{BUDGET_CURVE['opus46_plateau_minutes']} دقيقة. والمصدرُ الأوّل يقول نصّاً إنّ "
            "ميزانيتَه «likely undercounts what the strongest agents can do» ⇒ أيُّ اقتباسٍ "
            "للدرجة بلا ميزانيتِها مُنحازٌ للأسفل، والانحيازُ **غيرُ متناظر** بين الأزواج."
        ),
        "source": SRC_BERKELEY + " — الشكل 5",
    }


def safeguard_pair() -> dict[str, object]:
    """مرشّحاتُ المزوّد: 0 ← 120 على النموذج نفسه.

    ⛔ النسبةُ **غير معرَّفة** (مقامٌ صفري) فتُسجَّل زوجاً لا رقماً — القاعدةُ نفسها التي
    منعت `actions_per_unit_gain = inf` في الجولة 04.
    """
    on, off = (
        SAFEGUARD_PAIR["default_filters_successes"],
        SAFEGUARD_PAIR["filters_disabled_successes"],
    )
    if on == 0 and off == 0:
        raise BenchmarkPinError("صفرٌ في الطرفين — لا زوجَ يُقاس")
    return {
        "model_id": SAFEGUARD_PAIR["model_id"],
        "harness": SAFEGUARD_PAIR["harness"],
        "successes_default_filters": on,
        "successes_filters_disabled": off,
        "ratio": None,
        "ratio_undefined_reason": "ZERO_DENOMINATOR — ⛔ لا `inf` ولا صفر: فالغيابُ لا يُصفَّر",
        "recorded_as": "PAIR_NOT_RATIO",
        "reading": (
            f"النموذجُ نفسه، الحزامُ نفسه، الميزانيةُ نفسها — ومرشّحاتُ المزوّد وحدها تنقل "
            f"النتيجة من {on} إلى {off}. ⇒ أقوى دليلٍ متاح على أنّ الدرجةَ المعيارية بلا "
            "`safeguard_config` ليست رقماً ناقصاً بل **رقماً عن شيءٍ آخر**. وهذا قياسٌ مباشر "
            "لأطروحة AHW `(A,B)` معاً: المكوّنُ وحده لا يُفسّر، والزوجُ هو وحدةُ الاقتباس."
        ),
        "source": SRC_BERKELEY + " — حاشية ‡ في الجدول 1",
    }


def self_contradictions() -> list[dict[str, object]]:
    """تناقضاتُ المصدر الأوّل مع نفسه — تُسجَّل ولا تُحلّ صمتاً."""
    table1 = next(r.successes for r in RUNS if r.model_id == "claude-mythos-preview")
    fig5 = BUDGET_CURVE["mythos_at_120min"]
    return [
        {
            "id": "D1",
            "where": "الجدول 1 مقابل الشكل 5، للميزانية نفسها (120 دقيقة) والنموذج نفسه",
            "values": {"table1_successes": table1, "figure5_at_120min": fig5},
            "delta": table1 - fig5,
            "resolved": False,
            "why_unresolved": (
                "⛔ لم يُقرأ نصُّ arXiv الكامل بعدُ (قُرئ الملخَّصُ ومدوّنةُ الطرف الأوّل). "
                "والفرقُ قد يكون تعريفَ «نجاح» (علمٌ مقبوض مقابل ثغرةٌ مقصودة) أو عيّنةً "
                "فرعية. ولا يُختار أحدُهما بلا نصٍّ — فالاختيارُ هنا اختلاق."
            ),
            "handling": "كلا الرقمَين مُسجَّل؛ ولا يُقتبس أيٌّ منهما بصفة «النجاح عند 120 دقيقة»",
        }
    ]


def pin_evaluations(runs: tuple[SuiteRun, ...]) -> dict[str, object]:
    """الدبوسُ في مجاله الصحيح — وهو اختبارُ `H59` لا تكرارُه.

    المتوقع: **صفرُ `UNPINNED`** (كلّ الحقول منطوقة)، والحكمُ مُدرَّجٌ بالعمر وحده.
    وإن ظهر `UNPINNED` هنا فإمّا الدبوسُ معطوبٌ أو الإدخالُ ناقص — وكلاهما فشلٌ صريح.
    """
    rows, states = [], {}
    for r in runs:
        status = evaluate_pin(r.pin(), AS_OF)
        rows.append(
            {
                "model_id": r.model_id,
                "harness": r.harness,
                "safeguard_config": r.safeguard_config,
                "adversary_budget_minutes": r.adversary_budget_minutes,
                "score_points": float(r.successes),
                "pin_state": status.state,
                "pin_label": status.label,
                "age_days_at_as_of": status.age_days,
                "window_days": status.window_days,
                "missing_fields": list(status.missing),
                "quotable": status.quotable,
            }
        )
        states[status.state] = states.get(status.state, 0) + 1
    unpinned = [row["model_id"] for row in rows if row["pin_state"] == "UNPINNED"]
    if unpinned:
        raise BenchmarkPinError(
            f"`UNPINNED` في مجال الدبوس الصحيح: {unpinned} — ⛔ إمّا الدبوسُ معطوب أو الإدخالُ ناقص"
        )
    age = float((AS_OF - SUITE_ISSUED_ON).days)
    return {
        "as_of": AS_OF.isoformat(),
        "suite_issued_on": SUITE_ISSUED_ON.isoformat(),
        "report_age_days": age,
        "fresh_days_threshold": FRESH_DAYS,
        "max_report_age_days": MAX_REPORT_AGE_DAYS,
        "pins_evaluated": len(rows),
        "state_counts": states,
        "unpinned_count": len(unpinned),
        "per_pin": rows,
        "h59_verdict": "CONFIRMED_IN_DOMAIN",
        "age_governs_not_missingness": all(not row["missing_fields"] for row in rows),
        "all_stale_by_age": states.get("STALE", 0) == len(rows),
        "reading": (
            f"سبعةُ دبابيس كاملةِ الحقول ⇒ صفرُ `UNPINNED`، والحكمُ كلُّه من العمر "
            f"({age:.0f} يوماً > سقف {MAX_REPORT_AGE_DAYS:.0f}) ⇒ `STALE` بالإجماع. "
            "وهذا **يُثبت `H59` في مجالها**: في الجولة 04 أنتج الدبوسُ `UNPINNED` لانطباقٍ "
            "خاطئٍ على غير درجةٍ معيارية، وهنا يُنتج حكماً مُدرَّجاً لأنّ المجالَ صحيح. "
            "⇒ الدبوسُ ليس معطوباً؛ بل محكومُ المجال، والاستعمالُ الخاطئ هو العيب."
        ),
        "purpose_qualifier": (
            "⚠️ `STALE` هنا تحكم **صلاحيةَ الاقتباس دليلاً على القدرة الحالية**، لا صحّةَ "
            "الرقم تاريخياً: فالقياسُ سجلٌّ دائم لِما فعلته تلك الأزواج في 2026-05-13. "
            "و`ReportPin` لا تحمل حقلَّ غرضٍ ⇒ الخلطُ ممكن، ويُمنع هنا بالنصّ لا بالأداة "
            "(قيدٌ مسجَّل في `pin_field_limitations`)."
        ),
    }


def build() -> dict[str, object]:
    """يبني المخرَج — ⛔ لا رقمَ بلا مصدرٍ مُسمّى، ولا فجوةَ بلا إعلان."""
    if sum(DOMAIN_INSTANCES.values()) != SUITE_INSTANCES:
        raise BenchmarkPinError("مجموعُ مجالات الحزمة ≠ حجمَها")
    if len({r.model_id for r in RUNS}) != len(RUNS):
        raise BenchmarkPinError("نموذجٌ مكرَّر في جدول التشغيل")

    pins = pin_evaluations(RUNS)
    mitig = mitigation_effect(RUNS)
    cpst = cpst_band(RUNS)
    offt = off_target_rate(RUNS)
    conflict = unsolved_conflict(RUNS)
    budget = budget_sensitivity()
    safeguard = safeguard_pair()
    contradictions = self_contradictions()

    results: dict[str, object] = {
        "pin_evaluations": pins,
        "mitigation_effect": mitig,
        "cpst_band": cpst,
        "off_target_rate": offt,
        "unsolved_conflict": conflict,
        "budget_sensitivity": budget,
        "safeguard_pair": safeguard,
        "self_contradictions": contradictions,
        # ── رؤوسُ قرارٍ مسطّحة: ما يُقتبس في صفحة القرار بلا نزولٍ في البنية.
        "mitigation_reduction_factor": mitig["reduction_factor"],
        "mitigation_residual_share": mitig["residual_share"],
        "pairs_zeroed_by_mitigations": mitig["pairs_zeroed_count"],
        "residual_top_share": mitig["residual_top_share"],
        "cpst_band_usd": cpst["band_usd"],
        "cpst_spread_factor": cpst["spread_factor"],
        "cpst_undisclosed_count": cpst["n_undisclosed"],
        "max_off_target_share": offt["max_off_target_share"],
        "unsolved_share_spread_factor": conflict["share_spread_factor"],
        "unsolved_reconciled": conflict["reconciled"],
        "budget_growth_share": budget["growth_share"],
        "safeguard_ratio": safeguard["ratio"],
        "pins_unpinned_count": pins["unpinned_count"],
        "pins_all_stale_by_age": pins["all_stale_by_age"],
        "h59_verdict": pins["h59_verdict"],
        "self_contradiction_count": len(contradictions),
        "self_contradictions_resolved": sum(1 for c in contradictions if c["resolved"]),
        "pin_field_limitations": [
            {
                "field": "safeguard_config",
                "limitation": "محورٌ واحدٌ لحمايتَين متعامدَتَين (مرشّحاتُ المزوّد · حماياتُ الهدف)",
                "handling": "تركيبٌ صريحٌ `FILTERS_DISABLED+MITIGATIONS_OFF` — ⛔ لا إبهام",
                "consequence": "الدبوسُ لا يميّز أيَّ المحورَين حرّك النتيجة، وكلاهما مُقاسٌ هنا منفصلاً",
            },
            {
                "field": "(غائب)",
                "limitation": "لا حقلَّ **غرضٍ** يفصل «دليلاً على القدرة الحالية» عن «سجلاًّ تاريخياً»",
                "handling": "مُؤهِلٌ نصّي في `pin_evaluations.purpose_qualifier`",
                "consequence": "بدون النصّ يُقرأ `STALE` تكذيباً للرقم لا انتهاءً لصلاحية الاقتباس",
            },
        ],
    }

    return {
        "kind": "BPIN_MEASUREMENTS",
        "as_of": AS_OF.isoformat(),
        "method": (
            "أرقامٌ منشورةٌ مجمّعة من طرفَين أوّليين على حزمةٍ واحدة، مُدبَّسةٌ بـ`ReportPin` "
            "ومحسوبةٌ حتمياً. ⛔ لا تشغيلَ نموذج، لا إعادةَ إنتاجِ استغلال، لا قياسَ عميل."
        ),
        "model_runs_executed": 0,
        "client_measurements": 0,
        "exploits_reproduced": 0,
        "exploit_code_present": False,
        "revenue_claim": "NONE — لا إيرادَ ولا عميلَ ولا فاتورة",
        "suite": {
            "name": SUITE,
            "version": SUITE_VERSION,
            "instances": SUITE_INSTANCES,
            "domains": dict(DOMAIN_INSTANCES),
            "owner": "Berkeley RDI (Dawn Song) + MPI-SP + UCSB + ASU + Anthropic + OpenAI + Google",
            "issued_on": SUITE_ISSUED_ON.isoformat(),
            "attribution_note": (
                "⛔ تصحيحُ نسبٍ للجولة 04: الحزمةُ **ليست** حزامَ تقييمٍ تابعاً لـOpenAI. "
                "وطرفٌ أوّلٌ يملكها أكاديميٌّ مستقلّ، والشركاءُ الصناعيون وفّروا وصولَ "
                "النماذج والتغذية الراجعة، والمنهجيةُ للأكاديميين نصّاً. ⇒ استقلالُ الحزمة "
                "يرفع قيمةَ الدليل لا يخفضها: فالطرفُ الذي يقيس لا يملك النموذجَ المقاس."
            ),
        },
        "inputs": {
            "runs": [
                {
                    "model_id": r.model_id,
                    "harness": r.harness,
                    "safeguard_config": r.safeguard_config,
                    "adversary_budget_minutes": r.adversary_budget_minutes,
                    "successes": r.successes,
                    "by_domain": list(r.by_domain),
                    "with_mitigations": None
                    if r.with_mitigations is None
                    else list(r.with_mitigations),
                    "cpst_usd": r.cpst_usd,
                    "cost_full_usd": r.cost_full_usd,
                    "time_min_per_success": r.time_min_per_success,
                    "llm_calls_per_success": r.llm_calls_per_success,
                    "flags_captured": r.flags_captured,
                    "successes_on_intended": r.successes_on_intended,
                }
                for r in RUNS
            ],
            "venn": dict(VENN),
            "budget_curve": dict(BUDGET_CURVE),
            "safeguard_pair": dict(SAFEGUARD_PAIR),
            "openai_unsolved": dict(OPENAI_UNSOLVED),
        },
        "results": results,
        "boundaries": [
            "⛔ صفرُ تشغيل نموذج وصفرُ إعادة إنتاج استغلال: ما قِيس أرقامٌ منشورةٌ مجمّعة.",
            "⛔ لم يُقرأ نصُّ arXiv الكامل؛ والتناقضُ D1 (157 مقابل 127) باقٍ بلا حلّ بسبب ذلك.",
            "⛔ لا يُقتبس أيُّ رقمٍ هنا دليلاً على القدرة الحالية: الدبابيسُ `STALE` بالعمر "
            f"({(AS_OF - SUITE_ISSUED_ON).days} يوماً > {MAX_REPORT_AGE_DAYS:.0f}).",
            "⛔ لا تُسوّى نسبةُ «لم يُحلّ» بين الطرفَين بمتوسط: فالدبابيسُ مختلفة في أربعة محاور.",
            "⛔ CPST غيرُ المُفصَحة لم تُستكمل: فمتوسطُ نطاقٍ ناقصٍ يُقرأ اكتمالاً.",
            "⛔ لا شيفرةَ استغلالٍ ولا تفصيلَ ناقلٍ في هذا الملفّ — والجهةُ المقاسةُ دفاعية "
            "(أثرُ الحمايات) واقتصادية (كلفةُ المهمة الناجحة).",
        ],
    }


def _canonical_digest(payload: dict[str, object]) -> str:
    return hashlib.sha256(
        json.dumps(payload["inputs"], ensure_ascii=False, sort_keys=True).encode()
    ).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__ or "")
    parser.add_argument(
        "--check", action="store_true", help="يقارن المودَع بالمحسوب ويفشل عند الانحراف"
    )
    args = parser.parse_args()

    payload = build()
    payload["generated_at"] = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    payload["inputs_digest_sha256"] = _canonical_digest(payload)

    if args.check:
        if not OUT.is_file():
            print("❌ measure_benchmark_pin: ملفُ القياس غير موجود", file=sys.stderr)
            return 1
        stored = json.loads(OUT.read_text(encoding="utf-8"))
        for key in ("kind", "as_of", "inputs_digest_sha256"):
            if stored.get(key) != payload.get(key):
                print(
                    f"❌ انحراف في {key}: {stored.get(key)!r} ≠ {payload.get(key)!r}",
                    file=sys.stderr,
                )
                return 1
        if stored.get("results") != payload["results"]:
            print(
                "❌ انحرافٌ في الأرقام المحسوبة — أُعيد توليدُ الملفّ أو صحّح المدخلات", file=sys.stderr
            )
            return 1
        print("measure_benchmark_pin --check: PASS")
        return 0

    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"measure_benchmark_pin: كُتب {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
