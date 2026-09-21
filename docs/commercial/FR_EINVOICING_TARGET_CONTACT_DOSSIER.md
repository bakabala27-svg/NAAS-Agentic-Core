# ملف الاتصال الجراحي — الفوترة الإلكترونية الفرنسية
### قائمة أهداف مُسمّاة + بروتوكول تواصل قابل للتنفيذ (الجزائر → فرنسا)

**تاريخ التحقق من كل بيانات هذا الملف:** 21 سبتمبر 2026
**الاشتقاق:** يبني هذا الملف على `FRENCH_EINVOICING_PROSPECTS.md` (القائمة الأولى: 18 هدفاً)
و`FR_EINVOICING_PROSPECT_INTELLIGENCE.md` (الاستخبارات لكل مرشح) و`FR_EINVOICING_FEASIBILITY_DEEP_DIVE.md` (الجدوى).
هو **لا يكرّرها**: يضيف ما لم يكن فيها — هوية قانونية (SIREN)، قناة اتصال عامة مُتحقَّق منها،
الدور الذي تطلبه، سطر الافتتاح بالفرنسية، وتسلسل التنفيذ بالساعة.

> ### ⚠️ إعلان صريح — اقرأه قبل أي شيء
> **لم يُرسل أي اتصال. صفر عملاء. صفر دفعات.**
> كل هدف هنا موسوم **فرضية مؤهَّلة (hypothèse qualifiée)** لا «عميل». الوسم مبني على إشارة عامة
> (صفحة خدمة، مقال، إعلان توظيف، قائمة رسمية)، **لا على شراء مُثبَت**.
> كل بريد/هاتف هنا **منشور علناً من الجهة نفسها أو من سجل عام**. لا أرقام هواتف شخصية، ولا عناوين
> بريد شخصية في هذا الملف (القاعدة مُعلنة في §1).
> أي بند قانوني موسوم «يحتاج تحققاً» **ليس رأياً قانونياً**.

---

## 0) ما هذا الملف وما ليس هو

| هو | ليس هو |
|---|---|
| قائمة **30 جهة مُسمّاة** في 6 طبقات + 4 جهات مُستبعَدة بسبب علم اعتراض | ليس وعداً بأن أياً منها سيدفع |
| بروتوكول اتصال مضبوط بالساعة والقناة والنسخة الجاهزة | ليس حملة إرسال جماعي |
| طريقة بناء 150 هدفاً إضافياً بنفسك من مصادر رسمية | ليس ملف بيانات شخصية لأشخاص |
| معيار توقف رقمي مُعلَن مسبقاً | ليس تبريراً للاستمرار بعد الفشل |

**حدود الخدمة المُباعة (لا تُخرَق في أي رسالة):** فياليزاسيون المرجع بيانات العملاء والمورّدين
(SIREN/SIRET عبر SIRENE، رقم TVA، جهات اتصال الفوترة، حذف المكررات، معرّفات التوجيه) وتسليم ملف
قابل للاستيراد + تقرير فجوات.
**ممنوع في العرض:** أي مسك حسابات، أي إدخال قيود أو ترميز، أي تصريح ضريبي أو اجتماعي، أي
`paramétrage` داخل منصة العميل، أي استشارة قانونية أو ضريبية (قيد `ordonnance 45-2138` — انظر التقرير §11).

---

## 1) ست قواعد إلزامية قبل أول رسالة (هذه هي «الدقة الجراحية» الحقيقية)

### القاعدة 1 — فحص «علم الاعتراض» قبل كل هدف (إلزامي)
في فرنسا يمكن لأي شركة أن تُسجّل **رفضاً لاستخدام بياناتها في التسويق المباشر** (حقل
`diffusionCommerciale` في السجل الوطني للمؤسسات التابع لـ INPI). هذا الفحص هو الفرق بين باحث محترف
ومُرسِل مزعج.

**كيف تفحص (٣٠ ثانية للهدف):**
1. `https://annuaire-entreprises.data.gouv.fr/entreprise/<slug>` أو ابحث بالـ SIREN.
2. `https://www.pappers.fr/entreprise/<slug>` — ابحث عن العبارة الحرفية:
   «**Cette entreprise s'est opposée à l'utilisation de ses données à des fins de prospection**».
3. أو من السجل الأولي: `data.inpi.fr` → بطاقة الشركة → «diffusion commerciale».

**الحُكم:** إن ظهر العلم ⇒ **يُحذف من قائمة الاتصال البارد نهائياً** (يبقى مؤهلاً فقط لمسار
الطلب الوارد: نموذج اتصال يملؤه هو، أو توصية من طرف ثالث).
**مطبّق الآن على:** FQM Conseil · FITECO · Esker · Yooz (انظر §4).

### القاعدة 2 — ما يُخزَّن وما لا يُخزَّن
يُخزَّن: اسم الشركة، SIREN، المدينة، هاتف/بريد **مهني عام**، الدور (Associé / Responsable de production)،
رابط المصدر، تاريخ التحقق، العلم القانوني.
لا يُخزَّن ولا يُنشر: هاتف شخصي، بريد شخصي، تاريخ ميلاد، معطيات مالية شخصية.
إن نشر الموقع **رقماً مباشراً لشخص** ⇒ يُذكر رابط الصفحة التي نُشر فيها، ويُتصل منه — لا يُنسخ الرقم.

### القاعدة 3 — البريد: نظام Opt-out للـB2B (مسموح، لكن بشروط)
- العنوان العام (`contact@…`) يُسوَّق إليه بدون موافقة مسبقة، **بشرط** رابط إلغاء اشتراك فعّال.
- العنوان المهني المُسمّى يستلزم أن يكون **الموضوع مرتبطاً بمهنته**.
- كل رسالة أولى تُعرّف بك، **وتذكر من أين عُرف عنوانه** (المادة 14 RGPD)، وتتضمن
  «**Répondez STOP**» أو رابط إلغاء.
- مدة الاحتفاظ: **3 سنوات** من آخر تفاعل. من لم يرد ⇒ يُحذف.
- الأساس القانوني: المصلحة المشروعة (6.1.f) — وليس «موافقة» لأن لا موافقة مطلوبة في B2B.

### القاعدة 4 — الهاتف: B2B ما زال مسموحاً بعد إصلاح 11 أغسطس 2026
القانون الجديد (27/07/2026 DGCCRF + مرسوم 2026-662) **يخصّ المستهلك**: موافقة مسبقة إلزامية، وإلغاء
`Bloctel`. **الاتصال المهني B2B لم يُمَسّ** (المادة L.34-5 CPCE): مسموح، بشرط أن يكون الموضوع مرتبطاً
بنشاط المتصل، تعريف واضح بالمتصل، ورفض فوري محترم يُسجَّل.
**نافذة الاتصال (بالساعات الفرنسية، والجزائر = فرنسا − 1 ساعة في سبتمبر-أكتوبر):**
الثلاثاء–الخميس، **10:30–12:00** و**14:00–15:30**. تجنّب الاثنين (اجتماعات الإنتاج)، الجمعة بعد 15:00،
12:00–14:00 (غداء)، وموسم البيلان (يناير–مايو).
⛔ بلغ `Non merci` واحداً ⇒ إيقاف الهدف فوراً وتسجيله.

### القاعدة 5 — LinkedIn: السقوف الرقمية الحقيقية
**20–25 دعوة/يوم كحد آمن، 100–150/أسبوع، ومعدل قبول > 30%** وإلا الحساب يُقيَّد
(الحد الرسمي 200/أسبوع لكنه يتقلّص مع كثرة الرفض). ابدأ بنصف السقف أول أسبوعين.
لا إثبات = لا إرسال جماعي من نفس القالب.

### القاعدة 6 — الصدق التجاري (وهو أصل التفاوض)
لا تدّعي صفة خبير محاسبي، ولا وضعاً قانونياً فرنسياً، ولا «شراكة رسمية» مع منصة.
التوقيع يكون: `[الاسم] — prestataire indépendant, ANAE n° [___], NIF [___] — Alger, Algérie`.
الأرقام الحقيقية (SIREN عماني؟ لا) — أي رقم لا تملكه لا يُكتب. هذا ليس مثالياً: هذا **دفاع ضد إلغاء
العقد** (loi 11/08/2026 تُبطل العقود في حال التضليل في B2C، والقضاء يُلغي العقود بالتضليل المادي في B2B).

---

## 2) جدول الملخص — 30 هدفاً في 6 طبقات

**مفتاح القراءة:** 🔥 = نفّذ هذا الأسبوع · 🎯 = قناة (تشتري بقعة عمل لا مشروعاً) · 🏛️ = مؤسسة (تفتح مئات)
· 🏭 = مشترٍ نهائي مباشر · ⛔ = مُستبعَد.

| # | الجهة | الطبقة | المدينة | القناة الأولى | الأولوية |
|---:|---|---|---|---|---|
| 1 | **GROUPE T2F** (T2F-BEA) | مكتب محاسبة | Toulouse | mail + هاتف | 🔥 |
| 2 | **ARCOEX (AR COMPTA EXPERT)** | مكتب محاسبة | Quint-Fonsegrives (31) | هاتف ثم mail | 🔥 |
| 3 | **Cabinet Archipel** | مكتب محاسبة 100% Pennylane | Lyon | mail | 🔥 |
| 4 | **Cabinet Finot & Associés** | مكتب محاسبة | Brignais (69) | mail | 🔥 |
| 5 | **RYDGE Conseil** | شبكة محاسبة (Montpellier) | Montpellier | هاتف + LinkedIn | 🔥 |
| 6 | **JF Occitanie** (Cabinet Richer) | مكتب محاسبة | Nîmes / Sommières / Montpellier | mail | 🔥 |
| 7 | **Balagué Expertise** | مكتب محاسبة | Castelginest (31) | هاتف | 🔥 |
| 8 | **Exco Fiduciaire du Sud-Ouest** (Exco Toulouse-Feuillants) | مجموعة إقليمية | Toulouse | mail + LinkedIn | 🔥 |
| 9 | **In Extenso Midi-Pyrénées** | شبكة وطنية (TPE) | Toulouse | هاتف وكالة + LinkedIn | 🔥 |
| 10 | **Groupe CF (Compagnie Fiduciaire) Toulouse** | 4 وكالات | Toulouse / Ramonville / Cornebarrieu / Fronton | mail | 🔥 |
| 11 | **Nexco Expertise** | مكتب رقمي (Pennylane Gold) | Paris 8e | mail | 🔥 |
| 12 | **Effinum — SPEE SAS** (منصة Cerfrance) | 🎯 PA | Paris (شبكة 720 وكالة) | mail + نموذج | 🔥 |
| 13 | **Pennylane** | 🎯 PA + 7 500 مكتب | Paris | نموذج شراكة | 🔥 |
| 14 | **Tiime** | 🎯 PA / TPE | Paris 9e | نموذج «Experts-comptables» | 🔥 |
| 15 | **Dext France** | 🎯 إدخال بيانات للمكاتب | Paris | هاتف تجاري | 🎯 |
| 16 | **Cegid** (Shine / experts-comptables) | 🎯 ناشر برمجيات | Lyon 9e | هاتف تجاري | 🎯 |
| 17 | **Cerfrance Drôme-Ardèche (DP)** | 🎯 شبكة AGC | Drôme/Ardèche | mail | 🎯 |
| 18 | **Cerfrance Adour Océan** | 🎯 شبكة AGC | Sud-Ouest | هاتف | 🎯 |
| 19 | **Cerfrance Provence-Alpes-Méditerranée** | 🎯 شبكة AGC | PACA | هاتف | 🎯 |
| 20 | **Cerfrance Dordogne + CEDO** | 🎯 شبكة AGC | Dordogne | mail | 🎯 |
| 21 | **CROEC Occitanie** (المجلس الجهوي للخبراء المحاسبين) | 🏛️ | Toulouse | mail | 🔥 |
| 22 | **CROEC Auvergne-Rhône-Alpes** | 🏛️ | Lyon | mail | 🔥 |
| 23 | **CCI Occitanie** | 🏛️ | Blagnac | mail | 🎯 |
| 24 | **CJEC / ANECS — La Bourse** | 🏛️ لوحة تعهيد محاسبي | Paris | مراقبة أسبوعية | 🎯 |
| 25 | **GI Life Sciences Toulouse** | 🏭 قناة توظيف | Toulouse | هاتف | 🔥 |
| 26 | **I-Cube Research** | 🏭 مشترٍ مباشر | Toulouse | mail | 🏭 |
| 27 | **EXAIL** | 🏭 مشترٍ مباشر | Toulouse | mail | 🏭 |
| 28 | **3000 Distribution** | 🏭 مشترٍ مباشر | Toulouse | mail | 🏭 |
| 29 | **expert-comptable-pennylane.fr** (مكتب رقمي) | مكتب محاسبة رقمي | Paris/عن بُعد | نموذج اتصال | 🔥 |
| 30 | **Moncomptable en ligne** | مكتب محاسبة 100% عن بُعد | Toulouse | نموذج اتصال | 🎯 |
| ⛔ | FQM Conseil · FITECO · Esker · Yooz | — | — | — | ⛔ مُستبعَد |

---

## 3) البطاقات التفصيلية

> تنسيق موحّد: **الهوية القانونية** · **القناة العامة** · **الدور المستهدف** · **لماذا هو هدف (الدليل)** ·
> **سطر الافتتاح بالفرنسية** · **التسلسل** · **مصدر التحقق**.

### الطبقة 1 — مكاتب محاسبة (نفّذ الآن)

#### 1. GROUPE T2F — T2F-BEA 🔥
- **الهوية:** Groupe T2F (T2F-BEA / T2F-Debat / T2F-Ruby / T2F-Audit). SIREN: *غير متحقق* (استخرجه بالـAPI، §7).
- **العنوان:** 7 boulevard de la Gare, 31500 Toulouse · باريس: 75 av. du Dr Calmette, 94290 Villeneuve-le-Roi.
- **القناة:** ☎ 05 61 54 39 60 · 01 45 97 43 67 · ✉ `contact@groupe-t2f.eu` · نموذج على الموقع.
- **الدور:** الشريك المسؤول عن التقنية/الشركات الناشئة: **Thibault FAURE** (منشور على موقعهم) — أو أي شريك إنتاج.
- **الدليل:** لديهم صفحة خدمة كاملة «**Facture électronique**» + مدوّنة مخصصة + عرض «**Diagnostic facture électronique**» وعروض شراكة مع Shine و Tiime (سبتمبر 2026).
- **سطر الافتتاح:** «Vous vendez un *diagnostic* facture électronique. La question suivante, c'est qui exécute le nettoyage des référentiels clients quand 300 dossiers arrivent en même temps ?»
- **التسلسل:** D0 mail → D1 هاتف (10:45) → D4 LinkedIn للشريك → D8 mail عيّنة مجانية (5 سجلات/24 سا) → D15 إغلاق.
- **المصدر:** groupe-t2f.eu (صفحة الخدمة، 02/09/2026) · annuaire officiel des experts-comptables.

#### 2. ARCOEX — AR COMPTA EXPERT 🔥
- **الهوية:** `AR COMPTA EXPERT`, sigle **ARCOEX** — **SIREN 753 097 047** · SIRET 753 097 047 00033 · NAF 69.20Z · SAS · تأسيس 2012 · **10–19 موظفاً** · CA 2020 ≈ 849 993 € · TVA FR36753097047.
- **العنوان:** 27 avenue Mercure, 31130 Quint-Fonsegrives.
- **القناة:** ✉ `contact@arcoex.fr` · ☎ 05 61 63 73 07 (fixe) / 05 62 80 11 85 (ثاني) · على موقعهم صفحة اتصال تنشر أرقام الشركاء — **افتح الصفحة واتصل من الأرقام المعلنة فيها، لا تنسخها إلى ملفك**.
- **الدور:** الشريك (associé) — الاسم المعلن على صفحتهم: *M. Amblard* و *B. Rader* (الصفحة: `arcoex.fr` → Contactez-nous).
- **الدليل:** مكتب صغير رقمي، صفحة «الفوترة الإلكترونية: ما يجب أن تعرفوه» + تشغيل iSuite/MEG (أدوات سحابية). أصغر حجم ⇒ أسرع قرار.
- **سطر الافتتاح:** «Votre page sur la facturation électronique est claire. La suite logique : qui vérifie les SIREN de vos 300 dossiers clients avant septembre 2027 ?»
- **التسلسل:** D0 هاتف (10:30) → نفس اليوم mail موجّه للشريك → D3 LinkedIn → D7 عيّنة.
- **المصدر:** `recherche-entreprises.api.gouv.fr` (بطاقة رسمية، 21/09/2026) · arcoex.fr.

#### 3. Cabinet Archipel 🔥
- **الهوية:** Archipel Lyon — SIREN *غير متحقق* · 9 quai des Célestins, 69002 Lyon · تأسيس 2013 · تقييم 4.9/5 (≈83–96 مراجعة).
- **القناة:** ✉ `contact@archipel-lyon.fr` · ☎ 04 23 32 40 36 · ساعات 9h–17h.
- **الدور:** **Gaël Gente, Expert-Comptable associé** (منشور على موقعهم) — المرجع Pennylane.
- **الدليل:** «**100% Certifié Pennylane**» + يبيعون «البارامتراج الكامل والتدريب والمتابعة». أي أن الأداة عندهم، والفجوة عندهم هي **جودة بيانات العميل الداخلة**.
- **سطر الافتتاح:** «Vous êtes 100 % Pennylane. Pennylane vous donne l'outil — il ne vérifie pas les SIREN de vos clients. C'est exactement le travail que je fais à distance, au volume.»
- **التسلسل:** D0 mail → D2 LinkedIn للشريك → D5 هاتف (11:00) → D9 عيّنة.
- **المصدر:** archipel-lyon.fr (صفحة Pennylane + À propos) · 21/09/2026.

#### 4. Cabinet Finot & Associés 🔥
- **الهوية:** Cabinet Finot & Associés — Brignais (69) · تأسيس 2010 · SIREN *غير متحقق*.
- **القناة:** ✉ `contact@finotassocies.fr` · ☎ 04 84 88 52 52 · 24 route d'Irigny, 69530 Brignais · 8h–17h.
- **الدور:** الشريك المؤسس (منشور: Gérald Finot, LinkedIn على موقعهم).
- **الدليل:** مقالات صريحة: «Facturation électronique obligatoire 2026… nous réalisons un **audit de votre système d'information, de vos flux de facturation et de la maturité numérique**» + مقال مقارنة برمجيات الفوترة. يبيعون التشخيص ⇒ يحتاجون قدرة تنفيذ.
- **سطر الافتتاح:** «Votre article sur le choix du logiciel s'arrête au logiciel. Le fichier clients, lui, reste à nettoyer — et c'est ce que personne ne veut faire en interne.»
- **التسلسل:** D0 mail → D3 LinkedIn → D6 هاتف → D10 عيّنة.
- **المصدر:** finotassocies.fr (مقالَان، 2026) · 21/09/2026.

#### 5. RYDGE Conseil (Montpellier) 🔥
- **الهوية:** **RYDGE CONSEIL — SIREN 903 309 490** (سيج Tour Trinity, Courbevoie) · 188 مؤسسة مفتوحة · CA 2024 ≈ 417.9 M€ · شبكة قديمة (ex-filiale KPMG) · وكالة Montpellier: Parc Eurêka, 251 rue Euclide.
- **القناة:** ☎ 04 67 99 14 00 (الوكالة) · فاكس 04 67 99 14 10 · أسماء منشورة في دليل عام: *Laurent Zanchetta* و *Cédric Lafond* (استعمل الصفحة العامة أولاً: `rydge.fr` → expert-comptable Montpellier).
- **الدليل:** «**Facturation électronique**» مُدرجة صراحة في كتالوج خدماتهم (`hasOfferCatalog`) — أي أنهم يبيعونها ولا يمكنهم تجاهل الكم.
- **سطر الافتتاح:** «La facturation électronique est dans votre catalogue. La charge de fiabilisation des référentiels retombe sur vos collaborateurs en pleine campagne fiscale. Je la prends à distance.»
- **التسلسل:** D0 هاتف (11:15) → mail لنفس المخاطَب → D5 LinkedIn (Page RYDGE + مسؤول الإنتاج المحلي) → D10 عيّنة.
- **تحذير:** **لا ترسل رسالة عامة للمقر في Courbevoie** — الوكالة هي المشتري الفعلي.
- **المصدر:** بطاقة API رسمية (21/09/2026) · rydge.fr · دليل ClubAlliancePro34.

#### 6. JF Occitanie (Cabinet Richer) 🔥
- **الهوية:** JF Occitanie — **Cabinet Richer, SIREN 329 912 554** · تأسيس 1984 · 3 مواقع: Nîmes (285 rue Gilles Roberval, Parc Kennedy Bât. A1), Sommières (Phynum), Montpellier (Fiduciaire Madar).
- **القناة:** ✉ `contact@jfoccitanie.fr` · ☎ 04 66 23 56 60 · 8h–12h / 13h30–17h30.
- **الدليل:** شبكة عائلية، 40 سنة، عملاء TPE/PME بكميات كبيرة؛ بنية 3 مواقع = **تكرار داخلي للعمل نفسه** في ثلاثة أماكن ⇒ فرصة «معيار واحد للبيانات».
- **سطر الافتتاح:** «Trois sites, quarante ans de dossiers : qui, chez vous, contrôle les SIREN et les contacts de facturation avant l'émission obligatoire ?»
- **التسلسل:** D0 mail → D2 هاتف (10:40) → D6 LinkedIn (مسؤول الإنتاج) → D11 عيّنة.
- **المصدر:** jfoccitanie.fr · SIREN من دليل محاسبي عام · 21/09/2026.

#### 7. Balagué Expertise 🔥
- **الهوية:** Cabinet d'Expertise Comptable Balagué — **SIREN 501 058 812** (RCS Toulouse 501 058 812) · SARL رأسمال 400 000 € · NAF 6920Z · TVA FR 61 791 349 749 · Gérant: **Philippe Balagué** · تأسيس 2007.
- **العنوان:** 11 chemin de Naucou, 31780 Castelginest + Saint-Girons (4 pl. Aristide Briand).
- **القناة:** ☎ 05 61 37 66 45 · ✉ `philippe-balague@balague-expertise.fr` (عام، منشور على صفحاتهم).
- **الدليل:** صفحة «**Facturation électronique / test**» + «**Le cabinet prend les devants et vous accompagne dans cette évolution**» — أي أنهم اختاروا لعب دور المرافق، وهذا يحتاج قدرة تنفيذ.
- **سطر الافتتاح:** «Vous avez déjà une page "test facture électronique". Le test qui compte, c'est le taux d'erreur réel de votre base clients : je peux le mesurer sur 20 fiches, gratuitement, sous 24 h.»
- **التسلسل:** D0 هاتف (10:35) → D1 mail «عيّنة 20 سجلاً» → D6 LinkedIn → D12 إغلاق.
- **المصدر:** balague-expertise.fr · دليل 36comptables · 21/09/2026.

#### 8. Exco Fiduciaire du Sud-Ouest (Exco Toulouse-Feuillants) 🔥
- **الهوية:** **SIREN 540 800 406** · SAS · تأسيس 1954 · **500–999 موظفاً** (ETI) · TVA FR85540800406 · مكتب رئيسي: 2 rue des Feuillants, 31076/31300 Toulouse · محرك: **Sébastien Dartiguelongue** (membre du directoire).
- **القناة:** ☎ 05 61 77 08 77 (Toulouse-Feuillants) · ☎ 02 43 59 12 07 (المقر التقني Laval) · ✉ `contact@exco.fr` (عام المجموعة).
- **الدليل:** شبكة إقليمية ضخمة تخدم PME/ETI + قطاع زراعي؛ العدد نفسه = مستحيل التنظيف اليدوي داخلياً.
- **سطر الافتتاح:** «Votre groupe accompagne des milliers d'exploitations et de PME : la fiabilisation des référentiels clients/fournisseurs est-elle absorbée en interne, ou déjà sous-traitée ?»
- **التسلسل:** D0 mail → D3 LinkedIn (محرك المجموعة) → D7 هاتف → D14 عرض تجريبي.
- **المصدر:** exco.fr · infonet (بطاقة قانونية) · 21/09/2026.

#### 9. In Extenso Midi-Pyrénées 🔥
- **الهوية:** **SIREN 493 489 413** · **50–99 موظفاً** (2022) · Espace Jeanne d'Arc, 9 rue Matabiau, 31000 Toulouse + 24 av. Albert Bedouce, 31400.
- **القناة:** ☎ 05 61 11 05 55 (مركز Toulouse) / 05 61 14 16 16 (Bedouce) · المجموعة: 8 place Hubert Mounier, 69002 Lyon — `communication@inextenso.fr` (للاستخدام الصحفي لا التجاري).
- **الدور:** **Frédéric Fenech** (directeur d'agence) و **Célia Meyer-Beisson** (منشورَان على `inextenso.fr`).
- **الدليل:** توجّه TPE/PME + 7 300 موظفاً في الشبكة، أي حجم ملفات هائل.
- **سطر الافتتاح:** «Deux associés, une clientèle TPE/PME : la préparation des fichiers clients pour la plateforme agréée, qui la fait aujourd'hui chez vous ?»
- **التسلسل:** D0 هاتف (وكالة Toulouse) → mail موجّه للمدير → D6 LinkedIn → D13 عيّنة.
- **المصدر:** annuaire.experts-comptables.org · inextenso.fr (fiche agence 266) · pappers.

#### 10. Groupe CF — Compagnie Fiduciaire (Toulouse) 🔥
- **الهوية:** CF Toulouse: 4 وكالات — Minimes (40 av. de Fronton, 31200), Ramonville (5 av. Pierre-Georges Latécoère, 31520), Cornebarrieu (8 route de Toulouse, 31700), Fronton (430 av. de Toulouse, 31620).
- **القناة:** ☎ 05 40 45 30 10 · 05 61 34 36 37 · 05 61 06 12 12 · 05 61 35 40 06 · نموذج «Prendre rendez-vous» على الموقع.
- **الدور:** **Yann Benchora** و **Bertrand Enjalbert** (experts-comptables associés، منشورَان على موقعهم).
- **الدليل:** نمو سريع (الوكالات جرت ترقيات 2026) + تقييم عميل يذكر «reprise d'un dossier auprès du comptable précédent» ⇒ **ملفات ببيانات موروثة متسخة** — وهذا بالضبط سوقك.
- **سطر الافتتاح:** «Quatre agences à Toulouse, des dossiers reprises d'autres cabinets : quand vos clients demanderont leur identifiant de routage, qui collecte et vérifie tout ça ?»
- **التسلسل:** D0 mail لأربع وكالات مع تخصيص سطر لكل واحدة → D3 هاتف → D8 LinkedIn → D15.
- **المصدر:** compagnie-fiduciaire.com (صفحات الوكالات + التوصيات) · 21/09/2026.

#### 11. Nexco Expertise (Paris 8e) 🔥
- **الهوية:** Nexco Expertise SAS — RCS Paris 894 279 652 · 29 rue du Colisée, 75008 Paris · Représentant légal: **Raphaël Berguig** · 250+ شركة مُرافقة.
- **القناة:** ✉ `contact@nexco.fr` · ☎ 01 59 13 35 79 · «devis sous 24h».
- **الدليل:** «**Partenaire officiel Pennylane depuis 2022**» + «Gold Partner» + يعرضون صراحة «**préparation facturation électronique 2026-2027**» + ترحيل من Cegid/Sage/Quadra ⇒ عملاء ببيانات موروثة.
- **سطر الافتتاح:** «Vous affichez 250 entreprises sur Pennylane et vous migrez depuis Sage/Cegid : qui fiabilise les SIREN et les contacts à la migration ?»
- **التسلسل:** D0 mail → D2 LinkedIn (Raphaël Berguig) → D6 هاتف → D12 عيّنة.
- **المصدر:** nexco-expertise.com · 21/09/2026.

#### 29. Cabinet digital «expert-comptable-pennylane.fr» 🔥
- **الهوية:** مكتب رقمي شريك Pennylane Gold (250+ شركة). الاسم القانوني غير معلن على الصفحة ⇒ **تحقّق قبل أي صفقة**.
- **القناة:** ☎ 09 73 03 73 08 · نموذج `expert-comptable-pennylane.fr/contact/` (البريد مخفي خلف الصفحة — استعمل النموذج) · 24h.
- **الدليل:** عرضهم كله «comptabilité 100 % en ligne» + «préparation à la facturation électronique» ⇒ لا احتكاك ثقافي مع مصدر خدمة بعيد، ولا يمانعون في العمل عن بُعد.
- **التسلسل:** D0 النموذج (يبدأ بـ«référentiel clients») → D3 LinkedIn → D7 هاتف.
- **المصدر:** expert-comptable-pennylane.fr · 21/09/2026.

#### 30. Moncomptable en ligne (Toulouse) 🎯
- **الهوية:** مكتب مقره Toulouse، تعامل 100% عن بُعد (مرجع دليل عام). بيانات قانونية غير محقّقة.
- **الدليل/الاستخدام:** **هو دليل على أن السوق يقبل خدمة محاسبية عن بُعد من كيان غير موجود في المنطقة** — أي أنه أفضل «مرجع ثقافي» لمواجهة اعتراض «لن نعهد لشخص خارج فرنسا».
- **التسلسل:** D0 نموذج اتصال → D5 متابعة.

### الطبقة 2 — المنصات المعتمدة (PA) 🎯 — تشتري «قدرة» لا «مشروعاً»

#### 12. Effinum — SPEE SAS (منصة Cerfrance) 🔥
- **الهوية:** **SPEE SAS** (العلامة Effinum) — 18 rue de l'Armorique, 75015 Paris · مُدرجة في قائمة المنصات المعتمدة لدى DGFiP (11/12/2025) · الشبكة: **720 وكالة، 13 500 متعاوناً، 320 000 شركة**.
- **القناة:** ✉ `contact@effinum.fr` · خطوط دعم جهوية (أمثلة موثّقة: 02 41 33 66 61 · 02 28 09 47 40 · 04 70 34 21 64).
- **الدليل القاتل:** لا يشتري أحد «دعم Effinum» — بل **جودة البيانات التي تدخل Effinum**. وهذا هو مركز تكلفة الشبكة بالكامل.
- **سطر الافتتاح:** «Le goulot n'est pas la plateforme : c'est la qualité des référentiels clients qui y entrent. Je peux reprendre cette étape, à distance, au volume — 300 fiches en 10 jours ouvrés.»
- **التسلسل:** D0 mail → D4 مكالمة → D9 عرض تجريبي مكتوب (شروط + تسعير) → D15 متابعة.
- **المصدر:** effinum.fr · comparateur-facturation-electronique.fr (بطاقة PA) · صفحات دعم Cerfrance الجهوية.

#### 13. Pennylane 🔥
- **الهوية:** PA + منصة، **7 500 مكتب محاسبة و 1 000 000 شركة** في نظامها (رقم إعلاني منها).
- **القناة:** نموذج الشراكة: `pennylane.com/fr/partenaires` و`pennylane.com/fr/contact-demande-de-partenariat` · الدعم: 01 73 02 46 41 (ومصدر ثانٍ يذكر 09 73 03 73 00 — تحقّق).
- **زاوية الدخول الصحيحة:** لا تسأل «هل توظفون؟» بل: «عند وصول آلاف الفواتير Factur-X شهرياً، ما نسبة الحالات التي تفشل بسبب بيانات طرف ناقصة؟ أُعيد معالجة تلك القائمة قبل الاستيراد.»
- **التسلسل:** D0 نموذج شراكة (بصيغة «fournisseur de service de fiabilisation des données») → D5 LinkedIn (Partner/Écosystème comptable) → D12 متابعة.
- **المصدر:** pennylane.com (صفحات الشراكة والدعم) · 21/09/2026.

#### 14. Tiime 🔥
- **الهوية:** Tiime — 15 rue Auber, 75009 Paris · TVA FR43823811278 (⇒ SIREN 823 811 278، **يحتاج تأكيداً رسمياً**).
- **القناة:** ✉ `contact@tiime.fr` · ☎ 01 86 65 10 43 · **صفحة مخصصة للخبراء المحاسبين**: `tiime.fr/contact-ec` (هذه هي البوابة الصحيحة، لا الدعم العام).
- **الزاوية:** Tiime تخدم أعداداً كبيرة من المستقلين وTPE ⇒ **معدل SIREN غير الصحيح في الإدخال هو تكلفة دعم مباشرة لها**.
- **التسلسل:** D0 نموذج contact-ec → D4 LinkedIn → D10 مكالمة.

#### 15. Dext France 🎯
- **القناة:** ☎ **+33 1 73 44 33 95** (المبيعات، فرنسا — من بياناتهم المهيكلة) · منصتهم PA.
- **الزاوية:** Dext تعيش على «تلقيم» المكاتب بالبيانات؛ **كل شيك بيانات عندها هو عميل محتمل لك**.

#### 16. Cegid (بما فيها Cegid pour les Experts-Comptables → Shine) 🎯
- **القناة:** مبيعات **0800 73 00 79** · مقر Lyon: 52 quai Paul Sédallian, 69279 Lyon Cedex 09 — ☎ +33 4 87 63 10 97.
- **الزاوية:** محفظة مكاتب ضخمة تنتقل إلى الفوترة الإلكترونية ⇒ **قناة توزيع** لا مشترٍ واحد.

#### 17–20. شبكة Cerfrance الجهوية 🎯 (4 جهات)
| الجهة | القناة العامة | لماذا |
|---|---|---|
| **Cerfrance Drôme-Ardèche (DP)** | ☎ 04 75 78 11 11 · ✉ `contact@dp.cerfrance.fr` | نشرت إعلان PDP الخاصة بها + شراكة Effinum |
| **Cerfrance Adour Océan** | ☎ +33 (0)5 58 05 82 00 | دورات مجانية للعملاء عن الفوترة الإلكترونية من 2025 ⇒ جمهور جاهز |
| **Cerfrance Provence-Alpes-Méditerranée** | ☎ 04 94 12 54 12 | «réunions d'information» جهوية يناير–فبراير 2026 |
| **Cerfrance Dordogne + CEDO** | ☎ 05 53 45 63 00 · ✉ `contact@cerfrance-dordogne.fr` | «réunions gratuites chaque mardi» + فيليال متخصصة في الرقمنة (CEDO) |

**نص مشترك لهذه الطبقة:** «Vous déployez Effinum auprès de milliers d'entreprises. La plateforme fait circuler la facture ; personne ne nettoie le référentiel qui la produit. Je peux prendre cette étape en sous-traitance administrative, sans jamais toucher à la comptabilité.»

### الطبقة 3 — مؤسسات وشبكات 🏛️ (تفتح مئات المكاتب بضربة واحدة)

#### 21. CROEC Occitanie — المجلس الجهوي للخبراء المحاسبين 🔥
- **الهوية:** **SIREN 892 077 629** · «Le Belvédère» 11 bd des Récollets, 31078 Toulouse Cedex 4 · **يفدرِت ~2000 خبير محاسبي و~10 000 موظف**.
- **القناة:** ✉ `cro@oec-occitanie.org` · ☎ 05 61 14 71 60 · نموذج اتصال على `oec-occitanie.org`.
- **الشخص:** **Éric Gillis** — الرئيس (منتخب ديسمبر 2024)، وجعل **الرقمنة والفوترة الإلكترونية في قلب ولايته** (تصريح منشور لـ CCI Occitanie).
- **الطلب الصحيح:** لا تطلب عميلاً — اطلب **مقعداً في ورشة/ندوة تقنية** (20 دقيقة) عن «fiabilisation des référentiels clients avant la PA». المؤسسة المهنية تُوزّع المعرفة لا الخدمات ⇒ هذا هو المدخل المشروع الوحيد.
- **التسلسل:** D0 mail → D5 هاتف السكرتارية → D12 متابعة.
- **المصدر:** occitanie.cci.fr (المقابلة) · service-public annuaire (بطاقة رسمية) · experts-comptables.fr.

#### 22. CROEC Auvergne-Rhône-Alpes 🏛️
- **الهوية:** 51 rue Montgolfier, 69451 Lyon Cedex 06 · ✉ `vmr@oecaura.fr` · ☎ 04 72 60 26 26 · الرئيس: **Damien Cartel**.
- **نفس الطلب** (ورشة/LinkedIn للجنة الرقمنة الجهوية).

#### 23. CCI Occitanie 🏛️
- **القناة:** 5 rue Dieudonné Costes, 31700 Blagnac · ☎ 05 62 74 20 00 · ✉ `contact.site@occitanie.cci.fr`.
- **الطلب:** ورشة لمرافقي الشركات (conseillers) حول «ما يجب أن يكون نظيفاً قبل المنصة» — جمهورها TPE مباشرة.

#### 24. CJEC / ANECS — «La Bourse» 🎯 (مراقبة فقط)
- **القناة:** `labourse.anecs-cjec.org` · ✉ `anecs-cjec@anecs-cjec.org` · ☎ 01 42 72 73 72.
- **واقع صريح:** العروض المنشورة **موجهة لخبراء محاسبين مُعتمدين** (مثال حقيقي: «sous-traitance ponctuelle jeune Expert-Comptable — 350 € HT/jour, Montluel/Lyon, février–avril 2027»)، وإعلان آخر في Côte d'Azur يذكر «**passage facture électronique avancé**».
- **ما تفعله فعلاً:** اقرأ القائمة **كل ثلاثاء** وابحث عن أي عرض تواصل يتضمن بريداً (بعضها يضع بريداً)، وردّ عليه. **لا تحاول نشر إعلان** — النشر مقصور على الأعضاء.

### الطبقة 4 — مشترون نهائيون مباشرون 🏭 (موجة 2027)

#### 25. GI Life Sciences (Toulouse) 🔥 — قناة توظيف مؤقت
- **القناة:** 9 place Alfonse Jourdain, «Le Cafarelli» étage 3, 31000 Toulouse · ☎ **05 34 45 03 41**.
- **الدليل القاطع (إعلانهم المنشور، 20/06/2026):** وظيفة **Assistant ADV** بعقد مؤقت 4 أشهر، 15.38 €/س، مهمتها الحرفية:
  «**Support ADV dans le déploiement de la réglementation sur la facturation électronique** · **Participation à la mise en conformité des données clients** · contribution au paramétrage et aux tests des outils ».
- **القراءة الجراحية:** وكالة توظيف **باعت** للتو «عاملاً بشرياً» لمهمة هي حرفياً خدمتك. زاويتك: «عندما يفضّل عميلكم شراء النتيجة لا الشخص، أنا أرخص وأسرع — ويمكنكم إعادة بيع خدمتي».
- **التسلسل:** D0 هاتف (10:30) لمدير الوكالة → D1 mail مع لقطة من إعلانهم → D7 متابعة.

#### 26–28. مشترون من إشارة توظيف (Toulouse)
| الجهة | الإشارة العامة | ما تفعله |
|---|---|---|
| **I-Cube Research** (31100 Toulouse) | إعلان «Approvisionneur – Gestionnaire Import/Export/**ADV** F/H» | ابحث صفحة الاتصال العامة → نموذج ويب → رسالة «ميزانية ADMIN» |
| **EXAIL** (Toulouse) | إعلان «**Assistant commercial & ADV**»: relances, facturation, impayés | ابحث `EXAIL Toulouse contact` → نموذج عام |
| **3000 Distribution** (31100 Toulouse) | إعلان «Secrétaire ADV» | نموذج عام |

**قاعدة هذه الطبقة:** لا ترسل عرضاً كاملاً. أرسل **سؤالاً واحداً**: «Qui, chez vous, contrôle les SIREN et les contacts de facturation avant le passage à la plateforme agréée ?» — ثم اعرض عيّنة 50 سجلاً بـ390 € HT.

---

## 4) قائمة ⛔ — لا اتصال بارد (علم اعتراض مسجَّل أو تعارض بنيوي)

| الجهة | السبب | ما تفعله بدلاً من ذلك |
|---|---|---|
| **FQM Conseil** (Toulouse) | بطاقة Pappers: «**s'est opposée à l'utilisation de ses données à des fins de prospection**» | احذف من كل قائمة إرسال. إن أردته: انتظر أن يملأ هو نموذج اتصال على موقعك |
| **FITECO** (بما فيه مكتبا Toulouse و Lyon) | نفس العلم على كيان المجموعة (SIREN 557 150 067) | لا بريد بارد للمجموعة. القناة الوحيدة: عرض وارد عبر Malt/Plateya أو توصية |
| **Esker** (Villeurbanne) | نفس العلم. تعارض إضافي: منصة PA كبيرة وفريقها الداخلي يفعل ذلك | لا اتصال. قناة شراكة فقط لو أُتيحت عبر طرف ثالث |
| **Yooz** (Aimargues) | نفس العلم | لا اتصال |

**قاعدة عامة:** كل هدف جديد يُفحص قبل إضافته (§1 القاعدة 1). النتيجة تُدوَّن في عمود `flag_opposition` في ملف التتبع.

---

## 5) النصوص الجاهزة (فرنسية — انسخ كما هي)

### 5.1 بريد أول لمكتب محاسبة (الخيار الافتراضي)
**Objet :** `Référentiel clients avant la plateforme agréée — qui le fiabilise chez vous ?`

> Bonjour [Prénom / Madame, Monsieur],
>
> J'ai vu que [nom du cabinet] [prépare ses clients à la facturation électronique / a publié un article sur le choix de la plateforme]. Une question, sans aucun argumentaire :
>
> **qui, chez vous, vérifie les SIREN, les contacts de facturation et les doublons du référentiel clients avant l'entrée dans la plateforme agréée ?**
>
> Je pose la question parce que c'est le seul poste qui ne se règle ni par le logiciel, ni par le choix de la PA — et c'est celui qui tombe en pleine campagne fiscale.
>
> Je fais ce travail à distance : contrôle SIREN/SIRET sur la base SIRENE, vérification des n° TVA, dédoublonnage, collecte des identifiants de routage, fichier d'import + rapport d'écarts. **Aucune saisie comptable, aucune imputation, aucune déclaration, aucun paramétrage de votre outil.**
>
> Proposition sans risque : envoyez-moi **5 fiches** (même anonymisées, SIREN seuls). Je vous les renvoie traitées sous 24 h, gratuitement. Si le taux d'erreur est faible, je vous le dis et on en reste là.
>
> Je vous écris parce que votre adresse est publiée sur [site du cabinet] à des fins de contact professionnel ; si vous ne souhaitez plus recevoir de message de ma part, répondez simplement « STOP » et je supprime vos coordonnées.
>
> [Prénom NOM] — prestataire indépendant (Algérie) · [téléphone] · [adresse e-mail] · ANAE n° [___]

### 5.2 بريد لمنصة/PA (طبقة 2)
**Objet :** `Fiabilisation des référentiels à l'entrée de vos clients — sous-traitance administrative`

> Bonjour,
>
> Vous immatriculez et embarquez des volumes importants de TPE/PME. Mon hypothèse, à corriger par vous : une part non négligeable de vos incidents d'onboarding vient moins de la plateforme que de la qualité du référentiel client (SIREN invalide, contact de facturation obsolète, doublons).
>
> Je prends cette étape en sous-traitance administrative pure : contrôle SIREN/SIRET sur SIRENE, TVA intracommunautaire, dédoublonnage, contacts, identifiants de routage, fichier prêt à l'import + rapport d'écarts.
>
> Deux questions :
> 1. Cette étape est-elle aujourd'hui absorbée en interne, ou externalisée ?
> 2. Sur quel volume et à quelle fréquence ?
>
> Si c'est utile, je fournis un test gratuit sur 20 lignes de votre choix, sous 24 h.
>
> [Prénom NOM] — prestataire indépendant · [coordonnées] · répondez « STOP » pour ne plus être contacté.

### 5.3 رسالة LinkedIn (300 حرف كحد أقصى يُقرأ)
> Bonjour [Prénom] — question directe : qui, chez vous, fiabilise le référentiel clients (SIREN, contacts de facturation, doublons) avant l'entrée en plateforme agréée ?
>
> Je le fais à distance, sans jamais toucher à la comptabilité. 5 fiches traitées gratuitement sous 24 h pour que vous jugiez sur pièce.

### 5.4 سكربت الهاتف (45 ثانية — للهاتف العام للمكتب)
> « Bonjour, je suis [Nom], je travaille à distance sur la **fiabilisation des référentiels clients** pour des cabinets d'expertise comptable, en préparation de la facturation électronique.
> Je ne vends pas de logiciel et je ne touche pas à la comptabilité.
> Est-ce que je peux parler trois minutes à la personne qui gère la **production** ou la préparation des dossiers ? »

**تجاوز السكرتارية بلا خداع:** « Ce n'est pas un appel de prospection commerciale classique : je cherche la personne qui traite le fichier clients. Vous savez à qui cela remonte ? »
**إن لم يوجد الشخص:** « Très bien. Quel est le meilleur moment pour rappeler, et à qui ? » ← ثم اكتب التاريخ في ملف التتبع.

### 5.5 المتابعة (D+8) — بالعيّنة لا بالالحاح
**Objet :** `Re : 5 fiches traitées, sans engagement`
> Bonjour [Prénom], je n'ai pas eu de retour et je ne l'interprète pas comme un refus : votre campagne passe avant.
> Une seule chose, sans engagement : envoyez-moi **5 SIREN**. Je vous les renvoie vérifiés sous 24 h avec le taux d'erreur réel. Si le taux est bon, je vous le dirai franchement.
> [Prénom NOM]

### 5.6 الرسالة الأخيرة (D+15) — الوداع المحترم
> Bonjour [Prénom], sans nouvelle, je clôture mon suivi et je ne vous relancerai plus. Le sujet reviendra au printemps 2027, quand l'obligation d'émission sera concrète : mes coordonnées restent valables. Bonne continuation. [Prénom NOM]

### 5.7 ما لا تكتبه أبداً
❌ « garantie de conformité » · ❌ « je suis expert-comptable / partenaire officiel » · ❌ « réduction de 50 % si vous signez cette semaine » · ❌ نصوص طويلة تحكي عنك · ❌ رسالة واحدة بقالب واحد مُرسلة إلى 50 مكتباً في نفس الساعة.

---

## 6) الإيقاع: 14 يوماً (بالساعة، والفارق الزمني معلوم)

**فارق التوقيت:** الجزائر = فرنسا − ساعة (حتى 25 أكتوبر 2026)؛ وبعدها = فرنسا (توقيت واحد). كل الساعات أدناه **بالساعة الفرنسية**.

| اليوم | 09:00–10:00 | 10:30–12:00 | 14:00–15:30 | بعد 17:00 |
|---|---|---|---|---|
| **D1** | تجهيز القائمة (30 هدفاً + فحص العلم) | — | 3 ساعات: 4 مكالمات (ARCOEX, Balagué, JF, T2F) | 4 بريد الأولى |
| **D2** | إعداد ملف العيّنة (20 سجلاً عاماً من SIRENE) | 4 مكالمات (Archipel, Finot, RYDGE, Exco) | 4 بريد موجّه | LinkedIn: 8 دعوات (الطبقة 1) |
| **D3** | متابعة الردود | 3 مكالمات (In Extenso, CF, Nexco) | 6 بريد (منصات + Cerfrance) | LinkedIn: 6 دعوات |
| **D4** | ترتيب الاعتراضات + تعديل النسخة | 4 مكالمات متابعة (من لم يرد) | بريد المؤسسات (CROEC ×2، CCI) | عيّنة مجانية أولى لجاهز |
| **D5** | مراقبة La Bourse (أسبوعي) | 2 مكالمات (GI Life Sciences, PME) | 4 بريد الطبقة 4 | LinkedIn: 6 |
| **D6–D8** | عيّنات مجانية (5 سجلات/24 سا لكل طالب) | متابعات هاتفية (فقط من ردّ) | إرسال العروض المؤهَّلة (390 €) | تسجيل كل شيء |
| **D9–D12** | تنفيذ العيّنات + طلب الدفع المسبق | متابعات | عرض 1,450 € لمن تجاوز العيّنة | — |
| **D13–D14** | جرد: 30 هدفاً، 10 محادثات حقيقية، 5 عروض، ≥1 محاولة دفع | | | |
| **D15** | شجرة القرار (§8) — لا تُغيَّر النتيجة لتبرير الاستمرار | | | |

**الحجم الأسبوعي المستهدف:** 22–25 بريداً · 18–20 مكالمة · 15–20 دعوة LinkedIn · 4–5 قنوات مؤسسية/منصات.

---

## 7) كيف تبني 150 هدفاً إضافياً بنفسك (روابط وبارامترات مُختبرة)

### أ) المصدر الذهبي — قائمة DGFiP للمنصات المعتمدة (كل صف فيه بريد اتصال)
الرابط: `https://www.impots.gouv.fr/je-consulte-la-liste-des-plateformes-agreees`
تُنشر **قائمتان** بثلاث صيغ (ODS/XLSX/PDF): «منصات مستوفية للشروط» و«مرشّحة في انتظار الاختبارات».
- **العيّنة الموثّقة (سبتمبر 2026):** **150 منصة معتمدة** + 16 مرشّحة.
- الأعمدة المنشورة: الاسم التجاري، العنوان، الموقع، **البريد الإلكتروني**، تاريخ التسليم.
⇒ **150 جهة، لكل واحدة بريد عام** — فلترة: استبعد من يستهدف `grands comptes` وSAP/EDI (Tradeshift، Basware، Pagero، EDICOM…) وركّز على TPE/PME (Abby، Indy، Tiime، Axonaut، Macompta، jefacture، Qweeby، VosFactures، Docoon، Kolecto…).

### ب) المكاتب — الدليل الرسمي
`https://annuaire.experts-comptables.org/tous-les-cabinets-experts-comptables-par-region`
- **Occitanie: 2 996 مكتباً** · Île-de-France 8 716 · AURA وPACA كلاهما > 3 000.
- استهدف الأقسام: **31 · 34 · 30 · 66 · 81** (أين مكتبك المستهدف أصلاً) ثم الأقسام 69 · 38 · 73.

### ج) هوية قانونية فورية + فحص العلم (API مجاني بلا مفتاح)
`https://recherche-entreprises.api.gouv.fr/search?q=<الاسم>&limit=5`
- **مُختبر ويعمل:** `?activite_principale=69.20Z&departement=31&limit=25` (كل مكاتب المحاسبة في Haute-Garonne).
- ⛔ **لا يعمل:** إضافة `tranche_effectif_salarie` ⇒ خطأ HTTP 500. استعمل الفلتر عبر `?q=` + `departement=` فقط.
- يُعيد: SIREN/SIRET، العنوان، NAF، حجم الأثر، **dirigeants**، رقم TVA.

### د) إشارة الشراء الأقوى (مشترون مباشرون) — لوحات الوظائف
ابحث حرفياً عن العبارات التي تكشف الألم:
`"facturation électronique" "données clients" assistant ADV` · `"mise en conformité des données clients"` · `"déploiement de la réforme facturation électronique"`
على: Cadremploi · Indeed · Jobijoba · Meteojob · Apec. كل إعلان = **شركة في وسط الجهد الآن** + وكالة توظيف قابلة للاتصال (كما في GI Life Sciences).

### هـ) LinkedIn — صيغ البحث الدقيقة
- `("responsable de production" OR "chef de mission") expert-comptable <région>`
- `("responsable transformation digitale" OR "responsable outils") cabinet expertise comptable`
- مجموعة `#factureélectronique` + المكاتب التي تنشر عن الإصلاح ⇒ تفاعل قبل الرسالة.
**السقف:** 20–25 دعوة/يوم · لا رسالة قبل القبول (إلا دعوة بتعليق قصير).

### و) قنوات الطلب الوارد (تبنيها مرة واحدة وتعمل وحدها)
| القناة | الرابط | ملاحظة صريحة |
|---|---|---|
| **Malt** | malt.fr | الجزائر في قائمة البلدان المفتوحة (تحقّق 17/06/2026) · **العميل يدفع مسبقاً** ⇒ يحلّ التحصيل |
| **Free-Work** | free-work.com | ⚠️ منتدى المنصة يذكر أن العمل «رسمياً» يستلزم مقراً في EU/فرنسا ⇒ **لا تعتمد عليها** (احتمال ضعيف، لا تبنِ خطة عليها) |
| **La Bourse (CJEC)** | labourse.anecs-cjec.org | مراقبة أسبوعية فقط (النشر للأعضاء) |
| **Plateya** | plateya.fr | منصة مخصصة للمساعدين الإداريين المستقلين — سجّل واعرض الخدمة بالنص نفسه |
| **5euros/Yoss/404works** | — | قنوات ثانوية، استعملها فقط إن نفد المخزون |

---

## 8) سجل التتبع + معايير التوقف

### أعمدة ملف التتبع (ملف جاهز: `FR_EINVOICING_TARGETS_2026-09-21.csv`)
`# · nom · type · siren · ville · telephone · email · role_cible · canal_1 · hook_fr · flag_opposition · statut · date_contact · objection · prochaine_action · date_action · source · verifie_le`

### معايير النجاح (مُعلنة مسبقاً — لا تُعدَّل)
| النتيجة بعد 14 يوماً | الحكم | الفعل |
|---|---|---|
| **≥1 دفعة مقدّمة مستلمة** | ✅ فرصة مثبتة | نفّذ، ثم ارفع السعر 20% |
| 0 دفعة لكن ≥3 طلبات عرض + ≥6 محادثات | 🟡 إشارة متوسطة | عدّل السعر (عيّنة 290 €) وأعد 14 يوماً مرة واحدة |
| 0 دفعة، ≥6 محادثات، اعتراض مهيمن واحد | 🟡 تشخيص | عدّل حسب الاعتراض (انظر التقرير §9.5) |
| 0 دفعة، <6 محادثات من 30 اتصالاً | 🔴 فشل الوصول | **غيّر القناة لا العرض** (الطبقة 2 قبل الطبقة 1) |
| <3 محادثات من 30 اتصالاً | 🔴 فشل كامل | **اقتل الفرصة**. انتقل للاحتياطي الأول |

### بوابات القتل الفوري (أي واحدة تكفي)
- 15 اتصالاً بلا **أي** رد على الإطلاق (بما فيه رفض) ⇒ مشكلة في العنوان/المصداقية لا في العرض.
- 3 محادثات متتالية ترفض «تقديم بيانات العملاء لمقدّم خارج EU» ⇒ أوقف وتعالج البنية (DPA + معالجة على أجهزة العميل) أو انتقل للسوق المحلي.
- طلب منك أي عميل **مسك حسابات أو تصريحاً ضريبياً** ⇒ لا تفعل، وسجّل التوقف.

---

## 9) سجل الأدلة — ما تُحقّق وما لم يُتحقّق (بصرامة)

### ✅ مُتحقَّق منه (21/09/2026)
- **قانونياً:** إصلاح B2C نافذ 11/08/2026 (مرسوم 2026-662 + DGCCRF)، و**B2B غير متأثر**: الهاتف والبريد المهنيان مسموحان بنظام opt-out (المادة L.34-5 CPCE + RGPD): تعريف + ارتباط بالنشاط + إلغاء فوري + احتفاظ 3 سنوات.
- **علم الاعتراض موجود فعلاً** كحقل في السجل الوطني (INPI `diffusionCommerciale`) ويظهر على بطاقات Pappers: ثلاثة أهداف في هذا الملف تحمله (FQM Conseil، FITECO، Esker، Yooz).
- **قائمة DGFiP**: منصتان رسميتان، 150 معتمدة + 16 مرشّحة، وبريد اتصال لكل صف.
- **الوضعية الجزائرية للسحب:** Payoneer يعمل، PayPal لا يستقبل في الجزائر، Malt تفرض دفعاً مسبقاً.
- **SIREN مؤكدة:** ARCOEX 753097047 · AR COMPTA EXPERT · FQM 933728727⛔ · Cabinet Richer/JF 329912554 · RYDGE 903309490 · Exco FSO 540800406 · In Extenso MP 493489413 · Cerfrance/CROEC Occitanie 892077629 · Esker 331518498⛔ · Yooz 808386148⛔ · Esker PDP #0005 · Yooz PDP 949747133.
- **إشارة الطلب:** إعلان GI Life Sciences (20/06/2026) يعيّن حرفياً «mise en conformité des données clients» ضمن «déploiement de la facturation électronique» — أي أن الشراء جارٍ الآن بالعملة الصعبة.

### ⚠️ لم يُتحقَّق منه (لا تبنِ عليه وعداً)
1. **SIREN لـ:** Groupe T2F · Finot & Associés · Archipel Lyon · Balagué (مصدر ثانوي فقط) · Pennylane · Effinum/SPEE.
2. **بريد المكاتب المستهدفين في الطبقة 4** (I-Cube، EXAIL، 3000 Distribution) — لم يُقرأ من موقع رسمي بعد.
3. **علم الاعتراض على:** T2F · Finot · Archipel · Balagué · Exco · In Extenso · CF · Nexco · Cerfrance الجهوية — **يجب فحصه قبل أول رسالة** (القاعدة 1).
4. **أرقام الهاتف الشخصية المنشورة على مواقع بعض المكاتب** — لم تُنسخ هنا عمداً؛ تُستخدم من الصفحة الأصلية فقط.
5. **عدد الـ PA (150)** — تقديرات مصادر متخصصة مقارنة بملفي DGFiP، لا عدّ لي مباشرة على الملف.

### ⛔ فرضيات مرفوضة (لا تُروَّج)
- «المكاتب ستشتري لأن الموعد قريب» — **غير مُختبَر**.
- «144 منصة ستشتري خدمتي» — لا دليل واحد؛ هي **قائمة عناوين** تُختبَر بالحجم الصغير.
- «المنصة نفسها ستوظفني» — لا. الطلب الصحيح هو تعاقد على مهمة/حجم، لا توظيف.

---

## 10) الخطوة التالية خلال 24 ساعة (بالترتيب، لا تُخلط)

1. **افتح الملف المرافق** `FR_EINVOICING_TARGETS_2026-09-21.csv` واستكمل أعمدة `siren` الناقصة بالـAPI (§7-ج).
2. **افحص العلم** على 20 هدفاً من الطبقة 1 (دقيقتان لكل هدف) — احذف المصاب.
3. **أرسل 4 بريدات الأولى** (ARCOEX · Finot · JF Occitanie · Archipel) بنص §5.1 مع تخصيص السطر الأول.
4. **أجرِ 4 مكالمات** الثلاثاء 10:30–12:00 (بالساعة الفرنسية) بنص §5.4.
5. **أرسل نموذج شراكة واحداً** إلى Effinum (‎contact@effinum.fr‎) بنص §5.2.
6. **أنشئ ملف العيّنة**: 20 سجلاً عاماً من SIRENE، مُعالَجاً، كدليل ملموس.
7. **لا تفتح أي قناة جديدة** قبل 20 محاولة موثّقة في الملف. الإيقاع هو الفرق بين باحث ومتوهم.

---

### المصادر الأساسية لهذا الملف (كلها عامة)
`recherche-entreprises.api.gouv.fr` · `annuaire-entreprises.data.gouv.fr` · `data.inpi.fr` · `pappers.fr` ·
`impots.gouv.fr/je-consulte-la-liste-des-plateformes-agreees` · `annuaire.experts-comptables.org` ·
`service-public.gouv.fr` / `economie.gouv.fr` (DGCCRF, مرسوم 2026-662) · `experts-comptables.fr` ·
المواقع الرسمية للجهات المُدرجة (`arcoex.fr`, `groupe-t2f.eu`, `archipel-lyon.fr`, `finotassocies.fr`,
`rydge.fr`, `jfoccitanie.fr`, `balague-expertise.fr`, `exco.fr`, `inextenso.fr`, `compagnie-fiduciaire.com`,
`nexco-expertise.com`, `effinum.fr`, `pennylane.com`, `tiime.fr`, `dext.com`, `cegid.com`, `cerfrance.*`,
`oec-occitanie.org`, `oecaura.fr`, `labourse.anecs-cjec.org`, `fr.gigroup.com`) · لوحات الوظائف
(Cadremploi, Indeed, Jobijoba, Jobintree, Meteojob).

**هذا الملف ليس رأياً قانونياً ولا ضريبياً.** أي بند موسوم «يحتاج تحققاً» يُحسم مع مختص قبل الالتزام.
