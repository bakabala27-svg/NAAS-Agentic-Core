# الحالة الحيّة — WOD: انحرافُ الاستقطاع والتأهيل (دفعة 8 · 2026-09-14)

> **وثيقة حالة.** لا تحمل قانوناً (D-266 · D-290 L1): القانونُ في الدساتير القائمة، والأطروحة في
> [`docs/research/HARD_CURRENCY_NEW_KNOWLEDGE_WOD.md`](../docs/research/HARD_CURRENCY_NEW_KNOWLEDGE_WOD.md)،
> والقياسُ في [`docs/research/WOD_MEASUREMENTS.json`](../docs/research/WOD_MEASUREMENTS.json)، والعرض في
> [`docs/commercial/WOD_BUYER_LAYER_OFFER.md`](../docs/commercial/WOD_BUYER_LAYER_OFFER.md).
> كلُّ سطرٍ هنا قابلٌ للتحقّق من القرص، وحالةٌ معلنةٌ بلا دليل = انتهاك.

**as-of:** 2026-09-14

---

## 1 — ما تقيسه الوحدة

`shared/research/withholding_onboarding.py` (stdlib فقط، لا استيراد من `app/`):

| الطبقة | الدوال | ما تُخرجه |
|---|---|---|
| الاستقطاع | `effective_rate` · `characterization_inversion` · `matrix` | رقمٌ أو `None` بسببٍ منطوق لكلّ (سوق × وصف عقد) |
| التأهيل | `evaluate` · `minimum_unlock_set` · `entry_frontier` · `reference_ladder` | حالةُ عبورٍ لكلّ فئة مشترين + خطةُ فتحٍ مثلى بجهدٍ مُعلن |
| الالتقاط | `net_capture` · `summarize` | صافٍ = 1 × (1 − استقطاع) إن عبَرت، وإلا صفرٌ أو `None` |
| الشروط | `kill_switches` · `inputs_fingerprint` · `module_imports` | K1–K5 + بصمةُ مُدخلات + حراسةُ النقاء |

**التحقّق الآلي:**

```bash
python3 scripts/research/measure_withholding_onboarding.py --check   # الملفُّ مطابقٌ لإعادة الحساب
python3 -m pytest tests/shared/test_wod_withholding_onboarding.py -q # 54 اختباراً
```

## 2 — الأرقامُ المحسوبة (من `WOD_MEASUREMENTS.json`)

* خلايا: **22 = 18 قابلة للاقتباس + 4 مُمنوعة** · أسس: `DOMESTIC_ZERO` 10 · `TREATY_CAP` 7 ·
  `DOMESTIC_UNSTATED` 2 · `TREATY_COVERAGE_UNSTATED` 2 · `DOMESTIC_NO_TREATY` 1.
* تعويضٌ مطلوب عند 30%: **+42.86%**؛ عند 16.67%: **+20.00%**.
* فئاتٌ عابرةٌ اليوم: **1 من 12** (A0) · خطةُ الفتح: `msa_nda_review` + `dpa_sccs_pack` = **جهد 5**
  ⇒ A3 بريطانيا · A4 ألمانيا · A10 كندا · بعد أول فاتورة: A11 (المرجع).
* `kill_switches = []` وبصمةُ المُدخلات `17cf39bbd2ac…`.

## 3 — ما ⛔ لا تدّعيه

1. ⛔ **ليست رأياً ضريبياً ولا قانونياً** ولا محاسبياً؛ تُخرج عنوانَ السؤال، لا الحسم.
2. ⛔ **لا قياسَ عميل**: صفرُ عقد، صفرُ فاتورة، صفرُ مقابلةِ مشترٍ — كلُّ مُدخلٍ مصدرٌ منشورٌ مؤرَّخ.
3. ⛔ **لا رقمَ إيراد** ولا سعر؛ الكلفةُ بوحدة جهدٍ (⚙️ = يوم) لا بمال.
4. ⛔ **لا يتعدّل نصُّ عقيدة العملة الصعبة** ([`FOREIGN_CURRENCY_DOCTRINE.md`](../docs/FOREIGN_CURRENCY_DOCTRINE.md)) بحسابٍ داخليّ.
5. ⛔ **لا خطَّ ثامنَ** في [`OFFER_CATALOG.json`](../docs/commercial/OFFER_CATALOG.json).

## 4 — محفّزات إعادة التحقّق

| المحفّز | العمل |
|---|---|
| ورود نصٍّ أوّليّ لأيّ خليةٍ `TREATY_COVERAGE_UNSTATED` (FR · ES) أو `DOMESTIC_UNSTATED` (IT · SA) | تحديث الجدول وبصمة المُدخلات، وإعادةُ `--check` |
| تغيّرُ تشريع استقطاعٍ داخليّ في الأسواق الأحد عشر | إعادةُ القياسِ كاملاً ومقارنةُ البصمة |
| أولُ فاتورةٍ مدفوعة في A0 | نقلُ الفئةِ من `PASS` المحسوب إلى دليلٍ حقيقيّ (D-273 `currency_policy_ar`) |
| أوّلُ جوابٍ مكتوبٍ من مشترٍ عن وصف العقد المقبول | تسجيلُه في بطاقات `T65–T70` بالبحث |

---

*باحث مستقل — 2026-09-14 — إضافة لا حذف · صفرُ رقمٍ مخترع.*
