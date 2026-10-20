# رسالة اختبار المشتري — مواقع التجارة الإلكترونية الفرنسية غير الممتثلة للإتاحة (D-322 · OPP-13)

**سؤالٌ واحد عن السلوك الحالي:** من يصحّح المعايير غير الممتثلة التي تذكرها الجهة في تصريح الإتاحة الذي نشرته بنفسها، وما الذي يعطّل هذا العمل اليوم.
بلا سعر ولا وعدٍ بنتيجة ولا ادّعاءٍ قانوني. الدليل الوحيد الذي تذكره الرسالة هو تصريح الجهة نفسها.

## قواعد الإرسال (للمالك)

- القائمة: `docs/commercial/EAA_FR_ECOMMERCE_TARGETS_2026-10-20.csv` (20 جهة). جهةٌ واحدة لكل رسالة، وبحدٍّ أقصى 20 رسالة لهذا الإعداد. ابدأ من أعلى القائمة: الجهات المتوسطة وأحدث التصريحات أوّلاً.
- قناة التواصل: العمود `public_contact_channel` فقط، وهو استمارةٌ عامّة أو عنوانٌ وظيفيّ ذكرته الجهة في تصريحها. لا عنوان شخصياً.
- قبل الإرسال افتح رابط `source_url` وتأكّد أنّ التصريح ما زال كما هو. إن تغيّر فسجّل ذلك ولا ترسل الرسالة كما هي.
- يجوز ذكر تاريخ تصريح الجهة في السطر الأول، ولا تُنقل نسبتها: الرسالة بلا أرقام نسبٍ (`buyer_claims`).
- بعد كلّ إرسال: صفٌّ في `CONTACT_LEDGER.csv` (`EMAIL_SENT` أو `FORM_SUBMITTED`)، وبعد كلّ ردٍّ: `REPLY_RECEIVED` بنصّه.
- ⛔ لا يُفحص موقع جهةٍ قبل طلبٍ مكتوبٍ منها. والقراءة اليدوية، إن طُلبت، يقوم بها المالك بيده على معايير RGAA. ⛔ لا تُستعمل `tools/hard_currency_engine/eaa_scanner.py`، فهي مسحوبةٌ من مسار العميل (D-297 §4). ⛔ ولا تُكتب للجهة أيّ «déclaration» أو «attestation»: التصريح القانوني تكتبه الجهة نفسها.
- ⛔ لا يُكتب كودٌ قبل قرارٍ جديد من المالك (D-321). ردٌّ يطلب القراءة أو سعراً هو إشارة النجاح في D-322، لا إذنٌ بالبناء.
- ⛔ الإيقاف المسجَّل مسبقاً: 20 رسالة ثمّ صفر ردود خلال 30 يوماً من الرسالة العشرين = فشل هذا الإعداد.
- `[Signature]` يكتبه المالك بيده.

## Français

**Objet : Les critères non conformes de votre déclaration d'accessibilité — une question**

```
Bonjour,

Votre déclaration d'accessibilité, publiée sur votre site, liste des critères RGAA
qui ne sont pas encore conformes.

J'étudie ce que font les boutiques en ligne après leur déclaration d'accessibilité :
qui corrige les critères restants, avec quels moyens, et ce qui bloque.

Ma seule question : aujourd'hui, qui est chargé de corriger ces critères chez vous,
et qu'est-ce qui ralentit ce travail ?

Si c'est utile, et seulement avec votre accord écrit, je peux relire à la main une
page de votre parcours de commande et vous envoyer la liste des critères qui y
bloquent. Je ne rédige ni déclaration ni attestation de conformité.

Cordialement,
[Signature]
```
