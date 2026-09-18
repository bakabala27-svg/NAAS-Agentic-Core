# الحالة الحيّة — SSI: مؤشرُ البنية البيعية (دفعة SSI · 2026-09-18)

> **وثيقة حالة.** لا تحمل قانوناً (D-266): الأطروحةُ في
> [`docs/research/HARD_CURRENCY_NEW_KNOWLEDGE_SSI.md`](../docs/research/HARD_CURRENCY_NEW_KNOWLEDGE_SSI.md)،
> والقياسُ في [`docs/research/SSI_MEASUREMENTS.json`](../docs/research/SSI_MEASUREMENTS.json)،
> والأداةُ في [`shared/research/offer_sellability.py`](../shared/research/offer_sellability.py).
> كلُّ سطرٍ هنا قابلٌ للتحقّق من القرص، وحالةٌ معلَنةٌ بلا دليل = انتهاك.
> **الترقيمُ الدستوري محجوزٌ للمالك — لا D-Number هنا.**

**as-of:** 2026-09-18

---

## 1) البوابة التجارية

| البند | الحالة | الدليل على القرص |
|---|---|---|
| GATE_C — عملة صعبة مسوّاة | `ABSENT` | لا عقد · لا فاتورة · لا دفعة |
| خطوط الكتالوج المستفيدة (1 · 2 · 6) | `PROPOSED` | [`OFFER_CATALOG.json`](../docs/commercial/OFFER_CATALOG.json) — سبعةٌ مصرَّحٌ بها، ⛔ لا ثامن (تحرسه `check_agent_reliability_constitution.py`) |
| مقابلاتُ اكتشاف لهذا الخطّ | **صفر** | ⛔ لا محضرَ مؤرَّخ |
| تشغيلُ نموذجٍ لغوي لأجل هذا الخطّ | **صفر** | `model_runs_executed = 0` في [`SSI_MEASUREMENTS.json`](../docs/research/SSI_MEASUREMENTS.json) |
| قياسٌ على workload عميل | **صفر** | `client_measurements = 0` — كلُّ المدخلات من صفحاتِ بائعين منشورة |
| سقفُ خسارةٍ معتمد | **لا يوجد** | ⛔ لا إنفاق (الاختباراتُ T-MF01/02/03 أسئلةٌ مكتوبة بيد المالك) |

---

## 2) حالةُ القياس (مشتقةٌ من الأداة — تُعاد بـ`--emit`)

| البند | الحالة | الدليل |
|---|---|---|
| الفحوصاتُ الذاتية | **23/23 خضراء** | `python3 shared/research/offer_sellability.py --check` |
| تطابقُ الملفِّ مع الإصدار الحيّ | **MATCH** | أُصدِر الملفّ من الأداة نفسها بتاريخ 2026-09-18 |
| بصمةُ المدخلات | `13cfebcb14e0bf3e…` (كاملةٌ في الملفّ) | `sha256_inputs` في [`SSI_MEASUREMENTS.json`](../docs/research/SSI_MEASUREMENTS.json) |
| اتفاقُ المرمِّزين | **غيرُ مقاس** | مرمِّزٌ واحد (v1) — البروتوكولُ في ورقة SSI (κ ≥ 0.7) |
| فرضياتٌ ببروتوكولِ دحض | **3** (H-SSI01/02/03) | مربوطةٌ بـT-MF01/02/03 في [MF-01](../studies/market-first-sales-reality/ROUND-01-SALES-REALITY-MAP.md) |

---

## 3) ما الذي يُغيِّر هذه الحالة (ولا شيء سواه)

- `PROPOSED` → `DISCOVERY`: محضرُ مقابلةٍ مؤرَّخٌ واحد على الأقلّ.
- أيُّ ترقيةٍ فوق ذلك: عقدٌ/فاتورةٌ/دفعةٌ موثقة (عقدُ الجاهزية في
  [`FOREIGN_CURRENCY_OPERATING_SYSTEM.md`](../docs/commercial/FOREIGN_CURRENCY_OPERATING_SYSTEM.md)).
- أيُّ تعديلٍ في الترميز: نسخةُ أداةٍ جديدة + إعادةُ إصدارٍ + بصمةٌ جديدة — في نفس التغيير.
