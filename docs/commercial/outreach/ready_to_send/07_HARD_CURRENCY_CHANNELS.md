# ثلاث قنوات للعملة الصعبة — دليل المالك (D-323)

**القرار:** `.memory/decisions.md` D-323. لا كود منتج في أيّ قناة (D-321). كلّ عرضٍ يصل أو عقدٍ يُوقَّع أو دفعةٍ تستقرّ يُبلَّغ عنه ليصير صفّاً في `CONTACT_LEDGER.csv`.

## 0. طريق المال أوّلاً (يفتح القنوات كلّها)

1. **التسجيل في ANAE** على الخطّ في anae.dz.
   - الوثائق: بطاقة هوية، وإثبات سكنٍ عمره أقل من 3 أشهر، وصورة، وشهادة إن لزمت، وبريد إلكتروني ورقم جزائري ([upgrowth.dz](https://www.upgrowth.dz/auto-entrepreneur-inscription-anae)، مصدرٌ غير رسمي).
   - اختر رمز نشاطٍ يطابق العمل الفعلي، مثل «مطوّر معلوماتي» 021623 ([upgrowth.dz](https://www.upgrowth.dz/activite-anae/developpeur-informatique-021623)). تحقّق منه في القائمة الرسمية.
   - السقف 5 ملايين دينار سنوياً.
2. **حساب مهني غير تجاري بالعملة الصعبة** في بنكٍ جزائري، ببطاقة المقاول ووثيقة الهوية وإثبات السكن ([TSA، 2024-04-01](https://www.tsa-algerie.com/du-nouveau-pour-les-autoentrepreneurs-en-algerie/)).
   - اطلب من الوكالة قائمة الوثائق مكتوبة، واسأل عن «تصريح المشروع» الخاص بتصدير الخدمات الرقمية.
   - حسب المصدر نفسه، للمقاول الذاتي 100% من عائد تصدير خدماته بالعملة الصعبة (نصّ بنك الجزائر 06-2021).
3. **قاعدة واحدة:** المال الذي يأتي عبر Stripe يصل غالباً بالدينار. ما تريده عملةً صعبة يمرّ بتحويل SWIFT إلى هذا الحساب.

## 1. العمل الحر: وكلاء الذكاء الاصطناعي وأنظمة الاسترجاع وتقييمها

**المنصّات:**
- **Malt:** الجزائر مفتوحة للتسجيل، بشرط إثبات تسجيل ANAE عمره أقل من 3 أشهر، مع ترجمة محلَّفة إن كان بالعربية ([Malt](https://help.malt.com/hc/fr/articles/29511599491090-S-inscrire-sur-Malt-depuis-l-%C3%A9tranger-quels-pays)).
- **Upwork:** السحب بتحويل دولار بـ50$ لكلّ تحويل. شراء رصيد العروض (Connects) يتطلّب وسيلة دفع، وقبولها لبطاقةٍ جزائرية غير معروف.
- **Codeur:** اشتراكٌ شهري للمزايدة، والزبون يدفع لك مباشرة.

**قواعد:** حسابٌ واحد لكلّ شخصٍ حقيقي باسمه. لا وعد بنتيجة ولا نسبة ولا سعر قبل فهم المهمّة. والمبرمجون يسلّمون العمل.

**النجاح:** أوّل عقدٍ يُدفع بالعملة الصعبة ويستقرّ في الحساب. **الإيقاف:** 30 عرضاً خلال 45 يوماً من البطاقة، ثمّ صفر عقود.

### نصّ الملف — Malt (Français)

```
Ingénierie d'agents IA, de systèmes RAG et d'évaluation de LLM

Nous concevons et testons des agents IA et des systèmes RAG pour des équipes
qui doivent les mettre en production.

Ce que nous faisons :
- agents multi-étapes avec LangGraph, outils et mémoire ;
- pipelines RAG sur vos documents, avec un jeu de tests écrit à l'avance ;
- évaluation : cas de test définis avant le développement, contrôles
  déterministes, et un rapport de ce qui passe et de ce qui échoue ;
- backends FastAPI, conteneurs Docker, intégration continue.

Langues de travail : français, arabe, anglais.
Équipe basée en Algérie, travail à distance.

Pour commencer : un échange court pour cadrer une première tâche,
avec un périmètre et un prix fixés par écrit avant de démarrer.
```

### نصّ الملف — Upwork (English)

```
AI agents, RAG systems and LLM evaluation

We build and test AI agents and RAG systems for teams that need to run them
in production.

What we do:
- multi-step agents with LangGraph, tools and memory;
- RAG pipelines over your documents, with a test set written up front;
- evaluation: test cases defined before development, deterministic checks,
  and a report of what passes and what fails;
- FastAPI backends, Docker, continuous integration.

Working languages: English, French, Arabic.
Team based in Algeria, working remotely.

To start: a short call to scope a first task, with the scope and price
agreed in writing before any work begins.
```

## 2. منصّات الخبراء لمختبرات الذكاء الاصطناعي

| المنصّة | ماذا تحتاج | الدفع |
|---|---|---|
| [OpenTrain](https://www.opentrain.ai/jobs/country/algeria/) | سيرة. أفضل أدوار البرمجة تشترط ملفاً موثّقاً على Codeforces | Stripe، فيصل غالباً بالدينار |
| [Mercor](https://talent.docs.mercor.com/policies/supported-countries) | سيرة، ومقابلة آلية، والتحقق من الهوية. تتصل بك حين يُفتح مشروع | Stripe بعملة البلد |
| [Mindrift](https://mindrift.ai/faq) | سيرة واختبار تقني، وصفة مقاول ذاتي (بعد ANAE) | Payoneer بالدولار |

**قبل أيّ مهمّة:** سجّل الأجر المعروض فعلاً، وعملة أوّل دفعة حين تصل. **النجاح:** أوّل دفعة تصل. **الإيقاف:** لا عرض مشروع خلال 60 يوماً من التقدّم إلى الثلاث.

⛔ لا Outlier ولا DataAnnotation من الجزائر، لأن دفعهما عبر PayPal أو عملةٍ رقمية.

## 3. منحة معيار Lean مع الشريك

**الشرطان المسبقان، قبل أيّ طلب:**
1. يصوغ الشريك بنفسه 5 تمارين بكالوريا في Lean 4 مع mathlib، لإثبات المهارة.
2. يحصل على إذنٍ مكتوب من جامعته لأيّ عملٍ مدفوع. حسب [service-public](https://www.service-public.gouv.fr/particuliers/vosdroits/F2713)، شهادة إقامة الطالب الجزائري لا تسمح بالعمل الذاتي.

**التجربة اليدوية:**
- 30 إلى 50 نصّاً من أوراق البكالوريا العامّة، بعد التحقق من حقّ نشرها مفتوحة. المستودع لا يحمل إلا بضعة تمارين.
- لكلّ نصّ صيغة Lean، ووسمٌ «وفيّة» أو «خاطئة دلالياً» مع نوع الخطأ.
- تُنشر التجربة مفتوحة قبل الطلب.

**الجهة:** [AI for Math Fund](https://www.renaissancephilanthropy.org/ai-for-math-fund)، منحٌ أوّلية حتى 100,000$ بمراجعةٍ متواصلة. الناتج يجب أن يكون مفتوحاً، فهو تمويلٌ لمرّة واحدة لا منتجٌ يُباع.

**النجاح:** عرض منحة أو طلبٌ من المراجعين. **الإيقاف:** رفض، أو لا جواب خلال 90 يوماً.

### ملخّص المشروع (مسودة للطلب، English)

```
Project: an open benchmark of Algerian baccalaureate mathematics statements,
in Arabic and in French, formalized in Lean 4 with mathlib.

Each formal statement is labelled faithful or subtly wrong, with the error
type: missing hypothesis, changed quantifier, weakened conclusion.

Question: does autoformalization keep the meaning of the original statement
when the source text is Arabic or French?

Output: an open dataset, the Lean sources and the labelling guide.
Pilot: a small labelled set published before this application.
```

## 4. ما يبلّغ عنه المالك

كلّ تقديمٍ، وكلّ عرضٍ من زبون أو منصّة، وكلّ عقد، وكلّ دفعةٍ مع عملتها. لا تُكتب في المستودع أسماء أشخاص ولا أرقام حسابات.
