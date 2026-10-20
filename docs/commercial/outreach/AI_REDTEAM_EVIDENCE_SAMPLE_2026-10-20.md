# عيّنة الدليل — قاعدة حظرٍ عربية تُقبَل ولا تُطبَّق (D-320 · OPP-04)

ملاحظة للمالك: ما داخل الكتلتين أدناه هو ما يُرفَق للمشتري كما هو (إنجليزي ثمّ فرنسي).
المصدر: `docs/research/EXTERNAL_GUARD_PROBE.json` (D-285). أُعيد التشغيل في 2026-10-20 في
بيئةٍ نظيفة على `better_profanity 0.7.0` فأعاد `True False`، أي النتيجة نفسها.
⛔ لا سعر ولا وعدٍ بنتيجة في هذه الورقة، ولا ادّعاء عن نظام المشتري.

## English

```
Evidence note: an Arabic ban rule that a guard accepts and never applies
Date of the run: 2026-10-20

What was tested
- better_profanity 0.7.0, a public open-source text guard, run locally.
- No network call and no hosted service were involved.

What happened
- We added two ban terms the same way: the Latin control term "zzqq" and
  the Arabic term "غبي" (a mild insult, "stupid").
- Both were accepted with no error and no warning, and both appear in the
  guard's word set.
- The guard flags "zzqq" and replaces it with "****".
- The guard does not flag "غبي" and returns it unchanged.

Why
- The guard builds its allowed characters from the Unicode categories
  Ll, Lu, Mc and Mn. Arabic letters are category Lo, so they act as word
  separators and never form a token the rule can match.
- The rule is accepted, but it cannot be enforced.

Reproduce it (about three lines)
  python3 -m venv /tmp/g && /tmp/g/bin/pip install better_profanity==0.7.0
  /tmp/g/bin/python -c "from better_profanity import profanity as p; p.add_censor_words(['zzqq','غبي']); print(p.contains_profanity('zzqq'), p.contains_profanity('غبي'))"
  Expected output: True False

What this shows
- The failure class "accepted but never enforced" exists in a real
  third-party guard, for Arabic text.

What this does not show
- Anything about your system. We have not tested it.
- A hidden flaw: the vendor documents the limit ("Not all languages are
  supported yet, such as *Chinese*.").
- Anything about French: Latin letters with accents are tokenised by this
  library, so the same failure was not shown for French text.
- A market survey: this is one external guard.
- That only a special tool finds this. A plain test (ban X, send X, check
  that it fires) also catches it. What a trajectory check adds is naming
  the broken constraint: a rule that is accepted but cannot be enforced.
```

## Français

```
Note de preuve : une règle d'interdiction en arabe acceptée puis jamais appliquée
Date de l'exécution : 2026-10-20

Ce qui a été testé
- better_profanity 0.7.0, un filtre de texte open source public, exécuté en local.
- Aucun appel réseau et aucun service hébergé.

Ce qui s'est passé
- Deux termes interdits ont été ajoutés de la même façon : le terme témoin
  latin "zzqq" et le terme arabe "غبي" (une insulte légère, « idiot »).
- Les deux ont été acceptés : le filtre n'a émis ni erreur ni
  avertissement, et les deux figurent dans sa liste de mots.
- Le filtre signale "zzqq" et le remplace par "****".
- Le filtre ne signale pas "غبي" et le renvoie tel quel.

Pourquoi
- Le filtre construit ses caractères autorisés à partir des catégories
  Unicode Ll, Lu, Mc et Mn. Les lettres arabes sont de catégorie Lo : elles
  servent de séparateurs de mots et ne forment jamais un mot que la règle
  pourrait reconnaître.
- La règle est acceptée, mais elle ne peut pas être appliquée.

Reproduire (environ trois lignes)
  python3 -m venv /tmp/g && /tmp/g/bin/pip install better_profanity==0.7.0
  /tmp/g/bin/python -c "from better_profanity import profanity as p; p.add_censor_words(['zzqq','غبي']); print(p.contains_profanity('zzqq'), p.contains_profanity('غبي'))"
  Sortie attendue : True False

Ce que cela montre
- La classe de défaillance « acceptée mais jamais appliquée » existe dans
  un vrai filtre tiers, pour du texte arabe.

Ce que cela ne montre pas
- Quoi que ce soit sur votre système : nous ne l'avons pas testé.
- Une faille cachée : l'éditeur documente la limite ("Not all languages
  are supported yet, such as *Chinese*.").
- Quoi que ce soit sur le français : cette bibliothèque découpe bien les
  lettres latines accentuées, donc le même échec n'a pas été montré en
  français.
- Une étude de marché : il s'agit d'un seul filtre externe.
- Qu'il faille un outil spécial : un test simple (interdire X, envoyer X,
  vérifier qu'il est signalé) le détecte aussi. Un contrôle de trajectoire
  ajoute le nom de la contrainte rompue : une règle acceptée qui ne peut
  pas être appliquée.
```
