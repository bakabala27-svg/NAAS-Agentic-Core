# Rapport d'Audit Référentiels RFE France — DEMO_20_FICHES.csv
**Date :** 2026-09-29 · **Cadre Réglementaire :** Réforme Facturation Électronique (DGFiP / Factur-X)
**Périmètre du contrôle :** contrôles algorithmiques hors ligne (clés Luhn/TVA, doublons) — sans rapprochement SIRENE

## 1. Résultat des contrôles
| Indicateur | Résultat | Interprétation |
|---|---|---|
| Fiches traitées | **20** | Total du fichier |
| Fiches sans anomalie détectée dans ce périmètre | **0** (0.0%) | Contrôles algorithmiques; ni certification ni autorisation d'émettre |
| Erreurs SIREN / SIRET | **36** | À corriger ou vérifier |
| Erreurs TVA intracommunautaire | **18** | Contrôle local de format et de clé uniquement |
| Doublons détectés | **2** | À examiner avant fusion |

## 2. Repères réglementaires (France)
- Le barème publié par l'administration prévoit, pour l'émission hors format requis, 50 € par facture dans la limite de 15 000 €/an; la première infraction n'est pas sanctionnée.
- Échéances d'émission annoncées : 1er septembre 2026 pour les grandes entreprises et ETI; 1er septembre 2027 pour les PME et micro-entreprises.
- Ces échéances et montants ne constituent pas une estimation de risque pour une entreprise. Les anomalies du fichier ne prouvent ni un rejet de facture ni l'applicabilité d'une sanction.
- 20 fiches comportent au moins une anomalie dans le périmètre testé; elles sont à examiner avec les sources métier avant leur utilisation.

## 3. Plan d'action suggéré
1. Vérifier les SIREN/SIRET, numéros de TVA et codes postaux signalés auprès de sources fiables.
2. Ce rapport est hors ligne : le rapprochement SIRENE (statut, raison sociale) n'a pas été effectué; l'option `--online` le demande pour les SIREN valides.
3. Examiner les doublons proposés avant toute fusion; le rapport ne modifie pas le référentiel.

## 4. Échantillon des Anomalies
| Ligne | Nom | SIREN | Erreurs Détectées |
|---|---|---|---|
| 2 | STE EXEMPLE BETA | 123456789 | SIREN_INVALID(Échec contrôle Luhn), SIRET_INVALID(Échec contrôle Luhn), TVA_INVALID(SIREN de la TVA invalide (échec contrôle Luhn)) |
| 3 | GARAGE DUPONT & FILS | 804556219 | SIREN_INVALID(Échec contrôle Luhn), SIRET_INVALID(Échec contrôle Luhn), TVA_INVALID(SIREN de la TVA invalide (échec contrôle Luhn)) |
| 4 | BOULANGERIE MARTIN | 803245672 | SIREN_INVALID(Échec contrôle Luhn), SIRET_INVALID(Échec contrôle Luhn), TVA_INVALID(SIREN de la TVA invalide (échec contrôle Luhn)) |
| 5 | Boulangerie Martin SAS | 803245672 | SIREN_INVALID(Échec contrôle Luhn), SIRET_INVALID(Échec contrôle Luhn), TVA_INVALID(SIREN de la TVA invalide (échec contrôle Luhn)), DOUBLON_AVEC_LIGNE_4 |
| 6 | MENUISERIE LEBRUN | 902133458 | SIREN_INVALID(Échec contrôle Luhn), SIRET_INVALID(Échec contrôle Luhn), TVA_INVALID(SIREN de la TVA invalide (échec contrôle Luhn)) |
| 7 | SARL TECH SOLUTIONS | 903881245 | SIREN_INVALID(Échec contrôle Luhn), SIRET_INVALID(Échec contrôle Luhn), TVA_INVALID(Format invalide (attendu FR + 2 chiffres + 9 chiffres SIREN)) |
| 8 | PHARMACIE CENTRALE | 509447112 | SIREN_INVALID(Échec contrôle Luhn), SIRET_INVALID(Échec contrôle Luhn), TVA_INVALID(SIREN de la TVA invalide (échec contrôle Luhn)) |
| 9 | CABINET MOREL CONSEIL | 752290884 | SIREN_INVALID(Échec contrôle Luhn), SIRET_INVALID(Échec contrôle Luhn), TVA_INVALID(SIREN de la TVA invalide (échec contrôle Luhn)) |
| 10 | FLEURISTE LA ROSE | 821993507 | SIREN_INVALID(Échec contrôle Luhn) |
| 11 | TRANSPORTS DUPONT (radiée) | 891004437 | SIREN_INVALID(Échec contrôle Luhn), SIRET_INVALID(Échec contrôle Luhn), TVA_INVALID(SIREN de la TVA invalide (échec contrôle Luhn)) |
| 12 | RESTAURANT LE GOURMET | 843712609 | SIREN_INVALID(Échec contrôle Luhn), SIRET_INVALID(Échec contrôle Luhn), TVA_INVALID(SIREN de la TVA invalide (échec contrôle Luhn)) |
| 13 | AGENCE IMMO HORIZON | 884520331 | SIREN_INVALID(Échec contrôle Luhn), SIRET_INVALID(Échec contrôle Luhn), TVA_INVALID(SIREN de la TVA invalide (échec contrôle Luhn)) |
| 14 | Agence Immo Horizon | 884520331 | SIREN_INVALID(Échec contrôle Luhn), SIRET_INVALID(Échec contrôle Luhn), TVA_INVALID(SIREN de la TVA invalide (échec contrôle Luhn)), DOUBLON_AVEC_LIGNE_13 |
| 15 | PRESSING NETPLUS | 875601442 | SIREN_INVALID(Échec contrôle Luhn), SIRET_INVALID(Échec contrôle Luhn) |
| 16 | AUTO-ECOLE CONDUITE+ | 853940221 | SIREN_INVALID(Échec contrôle Luhn), SIRET_INVALID(Échec contrôle Luhn), TVA_INVALID(SIREN de la TVA invalide (échec contrôle Luhn)) |