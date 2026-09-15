# المصادر — دراسة 004

**قاعدةُ الدفعة:** كلّ رقمٍ إمّا **موروثٌ ببصمة** أو **مُعلَنٌ كتقدير** أو **`None`**.
⛔ لا متوسطَ ولا استكمالَ ولا «القيمة المعقولة». الغائبُ `None` لا صفر (D-212).

**قاعدةُ الدرجة:** لا يخرج إلى `QUOTABLE` أيُّ حكمٍ يعتمد على مصدرٍ درجة **ب** وحده.

| الرمز | الدرجة | الناشر | التاريخ | ما ثُبِّت منه |
|---|---|---|---|---|
| **S1** | **أ** | European Commission, DG TAXUD | نُشر 2026-08-06 · جُلب 2026-09-15 | 69 صفاً جزائرياً (مباشر/غير مباشر/إجمالي/مسار) |
| **S2** | **أ** | European Commission, DG TAXUD | نُشر 2026-02-06 · جُلب 2026-09-15 | 56 رمزاً مرجعياً × العمودَين A وB |
| **S3** | **أ** | European Commission, DG CLIMA | 2024-02-26 | جدولُ معامل CBAM عبر الزمن (Table 8) |
| **S4** | **ب** | OPIS/McCloskey + DEHSt | 2026-01-07 | صيغةُ الالتزام وترتيبُ SEFA |
| **S5** | **أ** | European Commission, DG TAXUD | 2026-05-27 | «مسارُ الإعلان يختار العمود» + الأرضيةُ عند الصفر |
| **S6** | **أ** | EUR-Lex — IR (EU) 2026/1740 Annex I | 2026-07-31 | جدولُ العلاوة + «عمودُ الإجماليّ» + مفاتيحُ المسار (A)–(L) |
| **S7** | **أ** | المفوضية (ثلاثةُ منافذ قطاعية متزامنة) | 2026-07-06 | سعرُ الشهادة 2026Q1/Q2 |
| **S8** | **ب** | ID (EU) 2026/1862 — **منقول** | 2026-09-09 | CSCF 2026–2030 = 1.000 |
| S9 | أ | EUR-Lex | 2025-12-22 | السجلُّ الببليوغرافيّ لـ IR 2025/2621 |
| S10 | ب | Studio Ponchio (guida CBAM DAC8, EN) | 2026-09-09 | تواريخُ الالتزام + عتبةُ 50 t |
| S11 | أ | هذا المستودع | 2026-09-15 | سجلُّ السحب: الأداةُ القديمة ما تزال بحسابها |
| S12 | **ج** | هذا المستودع | 2026-09-14 | الدفعاتُ السابقة — ⛔ **عيبُ إسنادٍ مُقاس** |
| S13 | **ج** | cbamguide · senken · carboncomplete | 2026-01-15 | ⛔ **ليس سنداً** — قرينةٌ على خطأٍ سائد |

---

## S1 — القيم الافتراضية للفترة النهائية (النسخة 2)

* **الناشر:** European Commission, DG TAXUD
* **الرابط:** `https://taxation-customs.ec.europa.eu/document/download/1c05d211-80cb-4aaa-8ef0-e08005a95d7e_en?filename=DV%20correcting%20act_final%20update_06.08.xlsx`
* **السندُ القانونيّ:** IR (EU) 2025/2621 Annex I كما استُبدل بـ IR (EU) 2026/1740
* **الاقتباس:** «Version 2 | 2026-08-06 | Default values based on Annex I and II to
  Implementing Regulation (EU) 2026/1740 adopted on 20 July 2026»
* **الطريقة:** `fetch_page` يحوّل XLSX إلى جداول markdown؛ الجزائر في القطع 1–4
  (إسمنت · أسمدة · ألومنيوم · هيدروجين · حديدٌ وصلب).
* **⛔ التحفّظ:** الملفّ «لأغراض المعلومات فقط»؛ الملزمُ قانوناً هو نصُّ اللائحة.
  لا يحوي الملحقَين II (الانبعاثات غير المباشرة) وIII (الكهرباء) ⇒ **غيرُ المباشرة
  هنا منقولةٌ من عمود الملفّ نفسه لا محسوبةً من عامل شبكة**.
* **سجلُّ النسخ (يُغذّي K4):** v1 = 2026-02-04 · v2 = 2026-08-06 ⇒ **نسختان في ستة أشهر**.

## S2 — مراجعُ CBAM للفترة النهائية

* **الناشر:** European Commission, DG TAXUD
* **الرابط:** `https://taxation-customs.ec.europa.eu/document/download/9877523c-2a02-4926-a211-aefae7cf6d0d_en?filename=CBAM%20Benchmarks_20260206.xlsx`
* **السند:** IR (EU) 2025/2620, Annex point 5, Columns A and B
* **الاقتباس:** «CN code | CN Description | Column A BMg [tCO2e/t] | Column A Production
  route indicator | Column B BMg [tCO2e/t] | Column B Production route indicator»
* **⛔ التحفّظ:** **الألومنيوم لم يُستخرج** من هذا الملفّ ⇒ مراجعُه A/B غائبةٌ عمداً،
  ⛔ لا مُصفَّرة (K5). وجدولُ «Other countries» غيرُ مستخرج ⇒ سبعةُ رموزٍ جزائريةٍ بـ «-»
  تبقى `None`.

## S3 — جدولُ معامل CBAM (دليلُ منهجية التخصيص)

* **الناشر:** European Commission, DG CLIMA — `1_gd1_general_guidance_en.pdf`
* **الرابط:** `https://climate.ec.europa.eu/document/download/d5276f6c-4355-438a-a0ef-0c03a9b34a39_en?filename=1_gd1_general_guidance_en.pdf`
* **السند:** Directive 2003/87/EC art. 10a(1a) كما عُدِّلت بـ Dir. (EU) 2023/959
* **الاقتباس (Table 8):** «CBAM 1 1 0.975 0.95 0.90 0.775 0.515 0.39 0.265 0.14 0»
  · «No CBAM factor (i.e. factor=1) applies to sub-installations producing goods not
  listed in Annex I»
* **جدولُ CSCF/الخفض الخطيّ المصاحب:** 2026 = 1.000 · 2027 = 0.9570 · 2028 = 0.9130 ·
  2029 = 0.8690 · 2030 = 0.8250
* **لماذا هو حاسم:** **الاتجاه.** المعاملُ **يهبط** ⇒ إنه «ما تبقّى من التخصيص
  المجانيّ» ⇒ وهو مضروبٌ في المرجع لا في الانبعاث.

## S4 — صيغةُ الالتزام (⛔ درجة ب)

* **الناشر:** OPIS / McCloskey (2026-01-07) + DEHSt (سلطةٌ وطنية ألمانية)
* **الرابط:** `https://www.opis.com/resources/energy-market-news-from-opis/provisional-cbam-calculation-values-pass-committee-vote/`
* **الاقتباس:** «CBAM-liable Emissions = Total Embedded Emissions − Free Allocation
  Adjustment − Carbon Price Already Paid; Specific Embedded Free Allocation = CBAM
  factor × Cross-Sectoral Correction Factor × CBAM Benchmark; The CBAM factor starts at
  97.5% in 2026»
* **التقاطع:** DEHSt: «the annually decreasing CBAM factor» · أسئلةُ المفوضية: «the CBAM
  adjustment for free allocation will gradually decrease»
* **⛔ سببُ الدرجة ب:** النصُّ الحرفيّ لملحق IR 2025/2620 **لم يُستخرج** (محاولةُ جلب
  دليلِ المفوضية رقم 4 فشلت). ولهذا **K3**: أيُّ نصٍّ أوّليّ يخالف هذا يُبطل الصيغةَ
  كلَّها. مُسنَدٌ بمرسَي درجة أ (S3 · S5) فلا يقوم الحكمُ على مصدرٍ ثانويّ وحده.

## S5 — أسئلةُ المفوضية وأجوبتها (2026-05-27)

* **الناشر:** European Commission, DG TAXUD
* **الرابط:** `https://taxation-customs.ec.europa.eu/document/download/013fa763-5dce-4726-a204-69fec04d5ce2_en`
* **السند:** Reg. (EU) 2023/956 arts. 6–9 · IR (EU) 2025/2620 Annex §3/§4
* **الاقتباس (العمود):** «If default values for embedded emissions are declared, the
  adjustment should equally be based on default values for free allocation … based on the
  CBAM benchmarks defined in **Column B** of this Annex. If applicable, the same
  production route shall be used as indicated in Annex I to Implementing Regulation (EU)
  2025/2621»
* **الاقتباس (الأرضية):** «where the number of certificates is calculated to have a
  negative value, it is set to zero»
* **لماذا هو حاسم:** هذا هو **السندُ الأوّليّ** على أنّ مسارَ الإعلان يختار العمود —
  وهو العمودُ الفقريّ لرسمِ المسار. والأرضيةُ هي سندُ **السقف** (004-08).

## S6 — رأسُ الملحق I من IR (EU) 2026/1740

* **الناشر:** EUR-Lex
* **الرابط:** `https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=OJ:L_202601740`
* **الاقتباس (حرفيّ):** «the default values of the column **'total emissions'** shall be
  selected and increased as follows: For goods in the cement, iron and steel, aluminium
  and hydrogen sectors, the mark-up shall be **10 % for the year 2026, 20 % for the year
  2027 and 30 % for the year 2028 and onwards**. For goods in the fertiliser sector, the
  mark-up shall be **1 % for the year 2026 and onwards**.»
* **مفاتيحُ المسار (حرفيّة):** (A) كلِنكر/إسمنت رماديّ · (B) أبيض · (C) صلبٌ كربونيّ
  فرنُ صهر/محوّل · (D) DRI/EAF · (E) خردة/EAF · (F) سبائكٌ منخفضة فرنُ صهر/محوّل ·
  (G) سبائكٌ منخفضة DRI/EAF · (H) سبائكٌ منخفضة خردة/EAF · (J) سبائكٌ عالية EAF ·
  (K) ألومنيوم أوّليّ · (L) ألومنيوم ثانويّ
* **نفاذ:** يحلُّ محلَّ الملحقَين I وIV من IR 2025/2621، ويسري **من 1 يناير 2026**
  (رجعيّ)، ويدخل حيّزَ النفاذ في اليوم الثالث بعد النشر.
* **لماذا هو حاسم:** يُثبت أنّ العلاوةَ على **عمود الإجماليّ** — وهو ما كان **افتراضاً**
  في `markup_gradient.py` (ادّعاء 002-03 درجة ب) وصار هنا **نصّاً** درجة أ.

## S7 — سعرُ شهادة CBAM

* **الناشر:** المفوضية الأوروبية، منقولٌ متزامناً من ثلاثة منافذ قطاعية
* **الرابط:** `https://eurometal.net/european-commission-announces-q2-2026-cbam-certificate-price/`
* **القيم:** 2026Q1 = **€75.36** (نُشر 2026-04-07) · 2026Q2 = **€75.28** (نُشر 2026-07-06)
* **⛔ الغائب:** 2026Q3 و2026Q4 **غيرُ منشورَين** ⇒ `None`، ⛔ لا استمرارٌ لقيمة الربع
  الثاني. الربعُ الثالث يُنشر **2026-10-05** (CPN-T5).
* **⛔ التحفّظ:** صفحةُ المفوضية نفسها لم تُجلب (فشل TLS من البيئة) — القيمةُ من ثلاثة
  منافذَ متوافقة، والدرجةُ أ للنشر لا للوسيط.

## S8 — عاملُ التصحيح عبر القطاعات (⛔ درجة ب)

* **الناشر:** Implementing Decision (EU) 2026/1862 (2026-07-23) — **منقول**
* **الرابط:** `https://www.studioponchio.eu/guida-cbam-dac8-en/`
* **السند:** Directive 2003/87/EC art. 10a(5)
* **الاقتباس:** «Specific embedded free allocation: 2026 CBAM factor (0.975) ×
  cross-sectoral correction factor (**1.00**) × benchmark (1.370) = **1.33575** t per
  tonne» — مثالُ الهند `7208` مسار BF-BOF، SEE = 4.280
* **⛔ سببُ الدرجة ب:** **لم يُقرأ نصُّ القرار 2026/1862 نفسه.** القيمة 1.000 منقولةٌ
  عن مثالٍ محسوبٍ في مصدرٍ مهنيّ، وسابقتُها (2021–2025) كانت 100% بقرارٍ من المفوضية.
* **الأثر:** كلّ رقمٍ باليورو في الدفعة **مشروط**، و`cscf_sensitivity` تحسب الانتشارَ
  عند 0.9/0.95/1.0 (عتبةُ الإسمنت الرماديّ 2026: انتشارٌ **0.06494 t/t**). **K2**.

## S9 — السجلُّ الببليوغرافيّ لـ IR (EU) 2025/2621

* **الرابط:** `https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=OJ:L_202502621`
* **⛔ التحفّظ:** جُلب السجلُّ الببليوغرافيّ وحده — الملفُّ الكامل ~2400 صفحة ولم
  يُحلَّل (سقفُ الجلب 30 صفحة). ولهذا كلّ رقمٍ بلدِيٍّ هنا من **S1** لا من هذا السجل،
  والدرجاتُ منفصلةٌ عمداً.

## S10 — تواريخُ الالتزام (نافذةُ البيع)

* **الرابط:** `https://www.studioponchio.eu/guida-cbam-dac8-en/`
* **الاقتباس:** «first annual CBAM declaration due **30 September 2027** for imports of
  2026; de minimis **50 tonnes** per year does not apply to hydrogen and electricity»
* **جدولُ أعمال الفترة النهائية:** IR 2025/2547 (المنهجية) · IR 2025/2548 (سعرُ الشهادة) ·
  IR 2025/2620 (تعديلُ التخصيص المجانيّ) · IR 2025/2621 (القيمُ الافتراضية) ·
  IR 2026/1740 (التصحيح) · ID 2026/1862 (CSCF) · Reg 2024/3210 (السجلّ)
* **⛔ الاستعمال:** **لتحديد نافذة البيع** فقط — قرارُ «أيَّ مسارٍ نُعلن» يُتَّخذ قبل
  2027-09-30 بأشهر. ⛔ لا يُقتبَس لأيّ رقمٍ ماليّ.

## S11 — سجلُّ السحب (هذا المستودع)

* `research/fx-hard-currency/cbam_value.py` — `FACTOR = {2026: 0.025, …}` مضروباً في الفجوة
* `studies/cbam-markup-gradient-002/markup_gradient.py` — `CBAM_FACTOR = {2026: 0.975, …}`
  مضروباً في الوفر
* **التناقضُ 39×** في المعامل نفسه.
* **⛔ لم يُحرَّر أيٌّ منهما.** الحارس:
  `test_withdrawn_arithmetic_is_still_reachable_in_the_old_instruments` يسقط يوم يُحرَّر
  أحدهما ⇒ الانتشارُ فعلٌ مرئيٌّ يحتاج قراراً مكتوباً (عرف RCL).

## S12 — الدفعاتُ السابقة (⛔ درجة ج)

* `UCL` · `FCM` · دراسة 002 · `README_NEW_KNOWLEDGE.md` · `FRONTIER_CLAIM_LEDGER_2026-09.md`
* **⛔ عيبُ إسنادٍ مُقاس:** `UCL` ورثت ستّةَ أرقامٍ ببصماتٍ مُعلَنة (`SFD` · `ERD` ·
  `PTD` · `PID` · `ABR` · `CPD`)، ومسحٌ كاملٌ للمستودع يُثبت أنّ **كلَّ بصمةٍ تظهر في
  ملفَّين فحسب**: وثيقة `UCL` وأداتُه. ⛔ لا ملفَّ قياسٍ مُودَع ولا دراسةً ولا وثيقةَ
  دفعاتٍ تحملُها (مُختبَر في `test_ucl_inherited_fingerprints_are_not_on_disk`).
* **الأثر:** نطاقُ M3 اليورويّ (6,000–60,000 €/day) كان **غيرَ قابلٍ للتدقيق**. هذه
  الدفعة تشتقّ **الآلية** من مصدرٍ أوّليّ وتترك النطاقَ اليورويّ **بلا ادّعاء**.
* **⛔ لا يُستشهد ببصماتٍ مُورَّثة كـ «موروثة»**: أيُّ رقمٍ جديد هنا إمّا من S1–S11 أو
  مُعلَنٌ كتقدير.

## S13 — ⛔ ليس سنداً: القراءةُ السوقيةُ الخاطئة

* **الناشرون:** cbamguide.com · senken.io · carboncomplete.com (ثلاثةٌ متوافقة)
* **الادّعاء:** «معاملُ CBAM: **2.5% في 2026** يصعد إلى **100% في 2034**، مطبَّقٌ على
  الانبعاثات الخاضعة»
* **⛔ لماذا هو درجة ج:** يقرأ المعاملَ «حصةً خاضعة» **تصعد**، بينما النصُّ الأوّليّ
  (S3) يجعله «ما تبقّى من التخصيص المجانيّ» **يهبط** من 97.5% إلى 0. والمادةُ
  10a(1a) واحدة.
* **⛔ لماذا هو مُدرَج أصلاً:** لأنّه **قرينةٌ على أنّ الأدبيات الثانوية سائدةُ الخطأ** —
  وهذا بالضبط سببُ أنّ أداةً بدبوسٍ أوّليّ لها سعر. ⛔ لا يُقتبَس منها رقم.
* **أثرُه على المستودع:** `markup_gradient.py` استعمل 0.975 **بالاتجاه الصحيح** لكن
  **في الموضع الخطأ** (مضروباً في الوفر)؛ و`cbam_value.py` استعمل 0.025 **في الموضع
  الصحيح** لكن **باتجاهٍ مُستعارٍ من S13**. كلاهما ⛔ لا يُقتبَس.

---

## ما لم يُجلب (⛔ مُعلَن، لا منسيّ)

| الغائب | السبب | الأثر | البطاقة |
|---|---|---|---|
| مراجعُ الألومنيوم A/B | لم يُستخرج من S2 | 6 رموزٍ جزائريةٍ **غيرُ قابلةٍ للترتيب** (`None` لا صفر) — **K5** | CPN-T1 |
| جدولُ «Other countries and territories» | قطعةٌ متأخرةٌ من S1 لم تُجلب | 7 رموزٍ بـ «-» تبقى `None` (حديدُ السبائك `7202`) | CPN-T2 |
| نصُّ ID (EU) 2026/1862 | لم يُجلب | CSCF درجة ب ⇒ **كلُّ رقمٍ يورويّ `CONDITIONAL`** — **K2** | CPN-T3 |
| ملحقُ IR (EU) 2025/2620 الحرفيّ | محاولةُ جلبِ دليلِ المفوضية رقم 4 فشلت | صيغةُ SEFA درجة ب (مُسنَدةٌ بمرسَي درجة أ) — **K3** | CPN-T4 |
| سعرُ شهادة 2026Q3/Q4 | ⛔ **غيرُ منشورٍ بعد** (2026-10-05) | كلّ الأرقام باليورو على سعر **2026Q2** | CPN-T5 |
| انبعاثٌ فعليٌّ لأيّ منشأة جزائرية | ⛔ غيرُ متاحٍ ولا يُدّعى | العتباتُ مُدبَّسة والقرارُ للمشتري — ⛔ **لا رقمَ إيراد** | ⛔ ليست بطاقة |
| `25070080` · `25233000` · `7202`* · `7208` · `7209` · `7210` · `7213` · `7214 20 00` · `7216` · `7218` · `7219` | لا مرجعَ مستخرجاً | 17 رمزاً `BENCHMARKS_NOT_EXTRACTED` | CPN-T1/T2 |

**مجموعُ الغياب:** 26 رمزاً من 69 غيرُ قابلةٍ للترتيب، بأربعةِ أسبابٍ **منطوقة** ومُعدَّدة
في `pin_inventory` — ⛔ لا سببٌ واحدٌ مُجمَّع.
