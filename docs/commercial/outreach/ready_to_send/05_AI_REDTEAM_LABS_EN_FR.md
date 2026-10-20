# رسالة اختبار المشتري — مختبرات النماذج ومورّدو الحواجز (D-320 · OPP-04)

**طلبٌ واحد:** إذنٌ مكتوب لتشغيل صنف المسبار نفسه على حاجزهم أو نموذجهم، ومشاركة النتيجة معهم سرّاً.
بلا سعر ولا وعدٍ بنتيجة. المرفق الوحيد: `docs/commercial/outreach/AI_REDTEAM_EVIDENCE_SAMPLE_2026-10-20.md`.

## قواعد الإرسال (للمالك)

- القائمة: `docs/commercial/AI_REDTEAM_TARGETS_2026-10-20.csv` (20 جهة). جهةٌ واحدة لكل رسالة، وبحدٍّ أقصى 20 رسالة لهذا الإعداد.
- قناة التواصل: صفحة التواصل الرسمية فقط. حيث يقول الملفّ `UNKNOWN`، ابحث عنها في الموقع الرسمي قبل الإرسال، ولا تستعمل عنواناً شخصياً.
- استعمل النصّ الإنجليزي، أو الفرنسي للجهات الفرنسية (Mistral AI · LightOn · Giskard · Kili Technology).
- بعد كلّ إرسال: صفٌّ في `CONTACT_LEDGER.csv` (`EMAIL_SENT` أو `FORM_SUBMITTED`)، وبعد كلّ ردٍّ: `REPLY_RECEIVED` بنصّه.
- ⛔ لا يُشغَّل أيّ فحصٍ على نظامٍ مستضاف لجهةٍ قبل إذنٍ مكتوبٍ منها، ولا يُكتب كودٌ قبل قرارٍ جديد من المالك. ردٌّ بـ«نعم» هو إشارة النجاح في D-320، لا إذنٌ بالبدء.
- ⛔ الإيقاف المسجَّل مسبقاً: 20 رسالة ثمّ صفر ردود خلال 30 يوماً من الرسالة العشرين = فشل هذا الإعداد.
- `[Signature]` يكتبه المالك بيده.

## English

**Subject: An Arabic ban rule that a guard accepts and never applies — one question**

```
Hello,

I test content filters and AI guards on Arabic and French text.

One failure class I measured on a public open-source guard (better_profanity 0.7.0):
the guard accepts an Arabic ban term, lists it in its word set, and then never flags it.
A Latin control term, added the same way, is flagged. There is no error and no warning.
The cause is the guard's character set: Arabic letters (Unicode category Lo) fall outside
it, so the Arabic rule cannot match anything.

The vendor documents that not all languages are supported, so this is a known limit of
that library, not a hidden flaw. I have not tested your system, and this result says
nothing about it. It shows that the "accepted but never enforced" class exists.

My one question: would you allow me, with your written permission, to run this class of
check on your guard, or on the safety filter you ship with your model, and send you the
result privately?

A one-page evidence note with a three-line reproduction is attached.

Best regards,
[Signature]
```

## Français

**Objet : Une règle d'interdiction en arabe acceptée puis jamais appliquée — une question**

```
Bonjour,

Je teste des filtres de contenu et des garde-fous d'IA sur des textes arabes et français.

Une classe de défaillance mesurée sur un garde-fou open source public (better_profanity 0.7.0) :
il accepte un terme interdit en arabe, l'inscrit dans sa liste de mots, puis ne le signale
jamais. Un terme témoin en lettres latines, ajouté de la même façon, est signalé. Il n'y a
ni erreur ni avertissement. La cause est le jeu de caractères du filtre : les lettres arabes
(catégorie Unicode Lo) en sont exclues, donc la règle arabe ne peut rien reconnaître.

L'éditeur indique que toutes les langues ne sont pas prises en charge : c'est une limite
connue de cette bibliothèque, pas une faille cachée. Je n'ai pas testé votre système, et ce
résultat ne dit rien de lui. Il montre seulement que la classe « acceptée mais jamais
appliquée » existe.

Ma seule question : m'autoriseriez-vous, par écrit, à faire ce type de contrôle sur votre
garde-fou, ou sur le filtre de sécurité livré avec votre modèle, et à vous transmettre le
résultat en privé ?

Une note de preuve d'une page, avec une reproduction en trois lignes, est jointe.

Cordialement,
[Signature]
```
