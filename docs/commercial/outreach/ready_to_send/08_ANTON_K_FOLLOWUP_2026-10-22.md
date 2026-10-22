# 08 — متابعة Anton K (Green and Fair) — 2026-10-22

**الجهة:** `ANTON_K_TARGET_2026-09-23.csv#id=1` · **القناة:** بريدٌ مباشر في الخيط القائم · **المرسل:** المالك بيده.
**حالة الخيط:** آخر رسالةٍ منه 2026-10-15: «We have successfully passed the process and just waiting for the official certificate.» آخر رسالةٍ منّا في اليوم نفسه تسأل عن الاعتماد والقطاعات. **لا ردّ بعدها، ولا صفٌّ في السجلّ بعد 2026-10-15.**
**لماذا الآن:** سبعة أيام بلا فعل، والمحادثة هي الوحيدة التي ردّت من خمس جهات. الشهادة قد تكون صدرت؛ والسؤال المعلّق (الملفّ المهني المطلوب) هو ما يوقف الخطوة التالية.

**قاعدة هذه الرسالة:** طلبٌ واحد ظاهر + معلومةٌ واحدة مطلوبة + عيّنةٌ مكتبية بلا بيانات مصنع. **لا سعر، لا وعد، لا تسمية الجهة لأيّ مصنّع، لا ادّعاء وفرٍ قبل قراءة رمز CN.**

---

## النصّ الإنجليزي (يُرسَل كما هو، بعد ملء الاسم)

**Subject:** Re: CBAM local support in Algeria — certificate scope and one desk note

Dear Anton,

Thank you for the update of 15 October — good to hear the process is complete on your side.

Two small practical points:

1. When the certificate is issued, would you send me the activity groups it actually covers? I will only mention your firm to a manufacturer once I can state the scope accurately — I would rather say nothing than say it wrong.
2. You mentioned that the Delegated Regulation requires environmental education and experience for the local auditor. What evidence would you accept for that — a degree, EU ETS or verification experience, or a training record? I would rather prepare the right profile than send a CV that misses the requirement.

In the meantime I can prepare a one-page desk note for one CN code of your choice: the published default value against a plausible actual range, and what that difference means for the certificate cost. No plant data, no NDA, no charge — it is the format I would use with a manufacturer, and you can tell me whether it is useful to your team.

Best regards,
[الاسم]

---

## ما تفعله كلّ فقرة (لمراجعة المالك قبل الإرسال)

| الفقرة | الوظيفة | ما لا تقوله |
|---|---|---|
| 1 | تسأل عن **نطاق الشهادة** بلغةٍ محايدة | لا تؤكّد أنّها صدرت؛ ولا تسمّي الجهة لأحد |
| 2 | تحوّل اعتراضه («يجب مؤهّل بيئي») إلى **سؤالٍ عن المعيار** | لا تدّعي مؤهّلاً لا نملكه، ولا تقدّم سيرةً ناقصة |
| 3 | تقدّم **عيّنةً مكتبية** ممكنةً اليوم بلا بيانات مصنع | لا تعِد بوفرٍ؛ المقارنة قد تكون سلبية لبعض الرموز |
| الخاتمة | تترك القرار له | لا سعر، ولا نسبة، ولا طلب اجتماع |

**حدّ العيّنة:** تُصنَع مرّةً واحدة، لرمزٍ واحد، ولا تُكرَّر لأكثر من جهةٍ قبل أن يردّ أحد. إن طلب رمزاً، اقرأ قيمته الافتراضية من ملحق IR 2025/2620 قبل أيّ حساب، ولا تُخرج رقماً بلا مصدر.

---

## بعد الإرسال — الصفّ الوحيد المسموح

لا يُضاف صفٌّ قبل الإرسال الفعلي. بعد الإرسال، أضِف إلى `docs/commercial/outreach/CONTACT_LEDGER.csv` صفاً واحداً بهذا الشكل (املأ التاريخ الحقيقي):

```csv
YYYY-MM-DD,ANTON_K_TARGET_2026-09-23.csv#id=1,Anton K,EU,email,EMAIL_SENT,,docs/commercial/outreach/ready_to_send/08_ANTON_K_FOLLOWUP_2026-10-22.md,"Follow-up sent by the owner after the 2026-10-15 reply. Asks (1) the activity groups the certificate covers, (2) what evidence of environmental education/experience the Delegated Regulation requires for a local auditor, (3) offers one desk note on published default values for one CN code, no plant data, no charge. No price, no claim."
```

ثم أعد توليد اللوحة بالأمر المعتاد في المستودع (اللوحة مشتقّةٌ من السجلّ، ولا تُحرَّر بيد).

**شرط الإيقاف:** لا ردّ خلال 14 يوماً ⇒ لا رسالةٌ ثانية إلا بعد ظهور الشهادة في قائمةٍ عامة. وإن لم تظهر خلال 60 يوماً ⇒ يُستبدَل الخيط بمحقّقٍ معتمد من قائمة المفوضية عند نشرها (شرط النقض 10 في `../CBAM_FIRST_CLIENT_KIT_2026-10-22/README.md` §10).
