# Rapport de Diagnostic Peppol Belgique — DEMO_BELGIUM_PEPPOL_20_FICHES.csv
**Date :** 2026-09-29 · **Cadre :** Arrêté Royal Facturation Électronique B2B Obligatoire
**Périmètre du contrôle :** contrôles algorithmiques hors ligne (Modulo 97, TVA, codes postaux, doublons) — l'inscription effective à l'annuaire Peppol se vérifie via les liens fournis dans le CSV

## 1. Résultat des contrôles hors ligne
| Indicateur | Valeur | Interprétation |
|---|---|---|
| Total fiches auditées | **20** | Lignes de données traitées |
| Fiches sans anomalie détectée | **3** (15.0%) | Format/clé localement valides; inscription Peppol non vérifiée |
| Numéros BCE / KBO invalides | **16** | À corriger ou vérifier |
| Numéros de TVA invalides | **14** | Contrôle local de format et de clé |
| Doublons détectés | **2** | À examiner avant fusion |

## 2. Cadre et limites
- La facturation électronique structurée B2B est obligatoire en Belgique depuis le 1er janvier 2026 pour la plupart des opérations dans le champ légal; des exceptions et mesures techniques existent.
- Cet audit ne consulte pas le répertoire Peppol, ne teste pas la réception du destinataire et ne vérifie pas l'intégration avec un logiciel comptable ou une plateforme.
- 17 fiches comportent au moins une anomalie dans le périmètre testé; cela ne prouve pas, à lui seul, qu'une facture sera rejetée ou qu'une sanction s'applique.

## 3. Échantillon des Anomalies
| Ligne | Nom | BCE | Erreurs Détectées |
|---|---|---|---|
| 5 | Boulangerie Saint-Aubain SA | 0435.889.195 | DOUBLON_AVEC_LIGNE_4 |
| 6 | Menuiserie Mosane SPRL | 0465.191.244 | BCE_INVALID(Échec Modulo 97 (trouvé=44, attendu=14)), TVA_INVALID(TVA invalide: Échec Modulo 97 (trouvé=44, attendu=14)) |
| 7 | Tech Solutions Bruxelles | 0892.456.789 | BCE_INVALID(Échec Modulo 97 (trouvé=89, attendu=15)), TVA_INVALID(TVA invalide: Échec Modulo 97 (trouvé=89, attendu=15)) |
| 8 | Pharmacie du Centre | 0402.891.234 | BCE_INVALID(Échec Modulo 97 (trouvé=34, attendu=80)), TVA_INVALID(TVA invalide: Échec Modulo 97 (trouvé=34, attendu=80)) |
| 9 | Transport & Logistique Hainaut | 0451.923.473 | BCE_INVALID(Échec Modulo 97 (trouvé=73, attendu=93)), TVA_INVALID(TVA invalide: Échec Modulo 97 (trouvé=73, attendu=93)) |
| 10 | Boucherie des Ardennes | 0821.993.570 | BCE_INVALID(Échec Modulo 97 (trouvé=70, attendu=39)) |
| 11 | Societe Radiée SPRL (Ancienne) | 0891.004.422 | BCE_INVALID(Échec Modulo 97 (trouvé=22, attendu=85)), TVA_INVALID(TVA invalide: Échec Modulo 97 (trouvé=22, attendu=85)) |
| 12 | Restaurant Leffe Dinant | 0843.712.656 | BCE_INVALID(Échec Modulo 97 (trouvé=56, attendu=31)), TVA_INVALID(TVA invalide: Échec Modulo 97 (trouvé=56, attendu=31)) |
| 13 | Immobiliere Namuroise | 0884.520.318 | BCE_INVALID(Échec Modulo 97 (trouvé=18, attendu=33)), TVA_INVALID(TVA invalide: Échec Modulo 97 (trouvé=18, attendu=33)) |
| 14 | Immobilière Namuroise SA | 0884.520.318 | BCE_INVALID(Échec Modulo 97 (trouvé=18, attendu=33)), TVA_INVALID(TVA invalide: Échec Modulo 97 (trouvé=18, attendu=33)), DOUBLON_AVEC_LIGNE_13 |
| 15 | Nettoyage Industriel Wallonie | 0875.601.442 | BCE_INVALID(Échec Modulo 97 (trouvé=42, attendu=79)) |
| 16 | Auto-Ecole Conduite Pro | 0853.940.245 | BCE_INVALID(Échec Modulo 97 (trouvé=45, attendu=90)), TVA_INVALID(TVA invalide: Échec Modulo 97 (trouvé=45, attendu=90)) |
| 17 | Electricite & Câblage Sambre | 0904.018.876 | BCE_INVALID(Échec Modulo 97 (trouvé=76, attendu=18)), TVA_INVALID(TVA invalide: Échec Modulo 97 (trouvé=76, attendu=18)) |
| 18 | Brasserie Artisanale d'Ecaussinnes | 0862.774.020 | BCE_INVALID(Échec Modulo 97 (trouvé=20, attendu=22)), TVA_INVALID(TVA invalide: Échec Modulo 97 (trouvé=20, attendu=22)) |
| 19 | Studio Graphique & Print | 0899.201.388 | BCE_INVALID(Échec Modulo 97 (trouvé=88, attendu=81)), TVA_INVALID(TVA invalide: Échec Modulo 97 (trouvé=88, attendu=81)) |