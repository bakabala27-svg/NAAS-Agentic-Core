#!/usr/bin/env python3
"""
Module France Validator — Hard Currency Engine
Audit et assainissement des référentiels clients/fournisseurs pour la réforme de la facturation électronique française (RFE).
"""

from __future__ import annotations

import csv
import json
import re
import unicodedata
import urllib.parse
import urllib.request
from collections.abc import Callable
from datetime import date
from pathlib import Path

from tools.hard_currency_engine.contracts import flag_duplicate
from tools.hard_currency_engine.csv_safety import (
    read_csv_lines_multi_encoding,
    write_cleaned_csv,
)

#: Base publique « Recherche d'entreprises » (INSEE/DINUM) — la seule source qui dit si une
#: entreprise est radiée. Sans elle, le contrôle est purement algorithmique (clés Luhn/TVA).
SIRENE_API_URL = "https://recherche-entreprises.api.gouv.fr/search"

#: Une entreprise est active quand `etat_administratif == "A"` ; « C » = cessée/radiée.
_SIRENE_ACTIVE = "A"


def strip_accents(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def norm(s: str) -> str:
    s = strip_accents((s or "").upper())
    return re.sub(r"[^A-Z0-9]", "", s)


def _numeric_identifier_digits(value: str) -> tuple[str, bool]:
    """Accept ASCII digits and grouping spaces/dots; reject other characters."""
    raw = (value or "").strip()
    if re.fullmatch(r"[0-9]+(?:[ .]+[0-9]+)*", raw):
        return re.sub(r"[ .]", "", raw), True
    return re.sub(r"[^0-9]", "", raw), False


def luhn_ok(digits: str) -> bool:
    """Vérification de l'algorithme de Luhn officiel."""
    if not re.fullmatch(r"[0-9]+", digits):
        return False
    total, length = 0, len(digits)
    for i, ch in enumerate(digits):
        d = int(ch)
        if (length - i) % 2 == 0:
            d *= 2
            if d > 9:
                d -= 9
        total += d
    return total % 10 == 0


def siren_check(siren: str) -> tuple[bool, str, str]:
    """Validation d'un SIREN (9 chiffres, Luhn) sans suppression de caractères inconnus."""
    digits, syntax_ok = _numeric_identifier_digits(siren)
    if not syntax_ok:
        return False, digits, "Format invalide (chiffres, espaces et points uniquement)"
    if len(digits) != 9:
        return False, digits, f"Longueur {len(digits)} ≠ 9"
    if not luhn_ok(digits):
        return False, digits, "Échec contrôle Luhn"
    return True, digits, "OK"


def siret_check(siret: str) -> tuple[bool, str, str]:
    """Validation d'un SIRET (14 chiffres, Luhn, avec règle officielle La Poste)."""
    digits, syntax_ok = _numeric_identifier_digits(siret)
    if not syntax_ok:
        return False, digits, "Format invalide (chiffres, espaces et points uniquement)"
    if len(digits) != 14:
        return False, digits, f"Longueur {len(digits)} ≠ 14"
    if digits.startswith("356000000"):
        # Règle INSEE : les SIRET de La Poste ne suivent pas Luhn ; ils sont valides
        # lorsque la somme des chiffres est un multiple de 5 (et non de 10).
        sum_digits = sum(int(ch) for ch in digits)
        if sum_digits % 5 == 0:
            return True, digits, "OK (La Poste)"
        return False, digits, "Échec contrôle somme La Poste (multiple de 5 attendu)"
    if not luhn_ok(digits):
        return False, digits, "Échec contrôle Luhn"
    return True, digits, "OK"


def tva_fr_check(tva: str) -> tuple[bool, str, str]:  # noqa: PLR0911 — EU formats need explicit branches
    """Validation du numéro de TVA intracommunautaire français ou intra-UE."""
    t = re.sub(r"[ .]", "", (tva or "").upper().strip())
    if not t:
        return False, t, "TVA vide"
    if not t.startswith("FR"):
        eu_match = re.fullmatch(r"([A-Z]{2})([A-Z0-9]{2,12})", t)
        if eu_match and eu_match.group(1) in (
            "AT",
            "BE",
            "BG",
            "CY",
            "CZ",
            "DE",
            "DK",
            "EE",
            "ES",
            "FI",
            "GR",
            "HR",
            "HU",
            "IE",
            "IT",
            "LT",
            "LU",
            "LV",
            "MT",
            "NL",
            "PL",
            "PT",
            "RO",
            "SE",
            "SI",
            "SK",
        ):
            country = eu_match.group(1)
            if country == "BE":
                belgian_number = eu_match.group(2)
                if not re.fullmatch(r"[01][0-9]{9}", belgian_number):
                    return False, t, "Format invalide (TVA BE attendue sur 10 chiffres)"
                remainder = int(belgian_number[:8]) % 97
                expected = 97 if remainder == 0 else 97 - remainder
                if int(belgian_number[8:]) != expected:
                    return False, t, "Clé Modulo 97 belge invalide"
                return True, t, "OK (Intra-UE BE, contrôle Modulo 97)"
            return True, t, f"OK (Intra-UE {country})"
        return False, t, "Format invalide (attendu FR + 2 chiffres + 9 chiffres SIREN)"
    m = re.fullmatch(r"FR([0-9]{2})([0-9]{9})", t)
    if not m:
        return False, t, "Format invalide (attendu FR + 2 chiffres + 9 chiffres SIREN)"
    key, siren = m.group(1), m.group(2)
    if not luhn_ok(siren):
        return False, t, "SIREN de la TVA invalide (échec contrôle Luhn)"
    expected_key = str((12 + 3 * (int(siren) % 97)) % 97).zfill(2)
    if key != expected_key:
        return False, t, f"Clé erronée ({key} ≠ attendu {expected_key})"
    return True, t, "OK"


def validate_french_postal_code(cp: str) -> tuple[bool, str, str]:
    """Valide un code postal français sans convertir du texte arbitraire en chiffres."""
    raw_input = (cp or "").strip()
    if not re.fullmatch(r"[0-9]{4,5}", raw_input):
        digits = re.sub(r"[^0-9]", "", raw_input)
        return False, digits, "Format invalide (4 ou 5 chiffres ASCII uniquement)"
    raw = raw_input
    if len(raw) == 4:
        raw = "0" + raw
    dept = raw[:2]
    dom_tom = ("971", "972", "973", "974", "975", "976", "977", "978", "984", "986", "987", "988")
    valid_depts = {"20", *(f"{i:02d}" for i in range(1, 96))}
    if dept in valid_depts or raw[:3] in dom_tom:
        return True, raw, "OK"
    return False, raw, f"Département {dept} inconnu"


def compute_french_vat_key(siren: str) -> str:
    """Calcule une clé TVA FR uniquement à partir d'un SIREN valide."""
    valid, digits, _ = siren_check(siren)
    if not valid:
        return ""
    key = str((12 + 3 * (int(digits) % 97)) % 97).zfill(2)
    return f"FR{key}{digits}"


def sirene_lookup(siren: str, timeout: int = 10) -> dict:
    """Interroge la base publique Recherche d'entreprises pour un SIREN.

    Retourne ``{"trouve": True, "actif": bool, "etat": str, "nom_officiel": str}``,
    ``{"trouve": False}`` si le SIREN est inconnu, ou ``{"trouve": None, "erreur": …}``
    quand le réseau est indisponible — le rapport dit alors « indisponible », jamais « OK ».
    """
    query = urllib.parse.urlencode({"q": siren, "limit": 1})
    request = urllib.request.Request(
        f"{SIRENE_API_URL}?{query}", headers={"User-Agent": "hard-currency-engine/1.0"}
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
    except Exception as exc:  # réseau/quota indisponible → dégradation explicite
        return {"trouve": None, "erreur": str(exc)[:120]}
    results = data.get("results") or []
    entry = next(
        (item for item in results if str(item.get("siren") or "") == siren),
        None,
    )
    if entry is None:
        return {"trouve": False, "erreur": "aucun SIREN exact dans les résultats"}
    etat = entry.get("etat_administratif") or ""
    return {
        "trouve": True,
        "etat": etat or "?",
        "actif": True if etat == _SIRENE_ACTIVE else (False if etat == "C" else None),
        "nom_officiel": (entry.get("nom_complet") or "").upper(),
    }


def _sirene_flags(clean_siren: str, lookup: Callable[[str], dict]) -> tuple[list[str], str, str]:
    """Return explicit SIRENE findings without turning missing data into a positive result."""
    info = lookup(clean_siren)
    if not isinstance(info, dict) or info.get("trouve") is None:
        return ["SIRENE_INDISPONIBLE(contrôle à relancer)"], "INDISPONIBLE", ""
    if info.get("trouve") is False:
        return ["SIREN_INCONNU_SIRENE(aucune correspondance exacte; à vérifier)"], "INCONNU", ""
    nom = info.get("nom_officiel") or ""
    if info.get("actif") is True:
        return [], "ACTIVE", nom
    if info.get("actif") is False:
        return [f"ENTREPRISE_RADIEE(etat={info.get('etat', '?')})"], "RADIEE", nom
    return ["SIRENE_STATUT_INDETERMINE(contrôle à relancer)"], "INDETERMINE", nom


def _read_csv_lines_multi_encoding(csv_path: Path) -> list[str]:
    """Conserve le nom historique et délègue la lecture à la sécurité CSV partagée."""
    return read_csv_lines_multi_encoding(csv_path)


def export_cleaned_french_csv(results: dict, out_path: Path) -> Path:
    """Exporte les lignes annotées après neutralisation des en-têtes et cellules."""
    return write_cleaned_csv(results.get("annotees", []), out_path)


def _validate_french_row(  # noqa: PLR0912, PLR0915 — one pass mirrors the regulatory checklist
    row: dict, cols: dict, line_no: int, seen_dedup: dict
) -> tuple[list[str], bool, bool, bool]:
    line_errors = []
    nom_val = row.get(cols["nom"], "") if cols["nom"] else ""
    siren_val = row.get(cols["siren"], "") if cols["siren"] else ""
    siret_val = row.get(cols["siret"], "") if cols["siret"] else ""
    tva_val = row.get(cols["tva"], "") if cols["tva"] else ""
    cp_val = row.get(cols["cp"], "") if cols["cp"] else ""

    has_siren_err = False
    has_siret_err = False
    has_tva_err = False

    if siren_val:
        ok_s, _, msg_s = siren_check(siren_val)
        if not ok_s:
            has_siren_err = True
            line_errors.append(f"SIREN_INVALID({msg_s})")
    elif siret_val:
        siret_digits, syntax_ok = _numeric_identifier_digits(siret_val)
        if not syntax_ok:
            has_siren_err = True
            line_errors.append("SIREN_DERIVE_INVALID(Format SIRET invalide)")
        else:
            siren_from_siret = siret_digits[:9]
            ok_s, _, msg_s = siren_check(siren_from_siret)
            if not ok_s:
                has_siren_err = True
                line_errors.append(f"SIREN_DERIVE_INVALID({msg_s})")
    elif tva_val and tva_val.upper().startswith("FR"):
        tva_compact = re.sub(r"[ .]", "", tva_val.upper().strip())
        if re.fullmatch(r"FR[0-9]{11}", tva_compact):
            siren_from_tva = tva_compact[4:]
            ok_s, _, msg_s = siren_check(siren_from_tva)
            if not ok_s:
                has_siren_err = True
                line_errors.append(f"SIREN_DERIVE_TVA_INVALID({msg_s})")
        else:
            has_siren_err = True
            line_errors.append("SIREN_MANQUANT")
    else:
        has_siren_err = True
        line_errors.append("SIREN_MANQUANT")

    if siret_val:
        ok_st, _, msg_st = siret_check(siret_val)
        if not ok_st:
            has_siret_err = True
            line_errors.append(f"SIRET_INVALID({msg_st})")

    if tva_val:
        ok_tva, _, msg_tva = tva_fr_check(tva_val)
        if not ok_tva:
            has_tva_err = True
            line_errors.append(f"TVA_INVALID({msg_tva})")

    if cp_val:
        ok_cp, _, msg_cp = validate_french_postal_code(cp_val)
        if not ok_cp:
            line_errors.append(f"CP_INVALID({msg_cp})")

    dedup_keys = []
    siren_key = _duplicate_siren_digits(row, cols)
    if siren_key:
        dedup_keys.append(f"SIREN:{siren_key}")
    name_cp_key = f"{norm(nom_val)}_{norm(cp_val)}"
    if len(name_cp_key) > 5:
        dedup_keys.append(f"NOM_CP:{name_cp_key}")
    flag_duplicate(line_errors, seen_dedup, line_no, dedup_keys)

    return line_errors, has_siren_err, has_siret_err, has_tva_err


def audit_french_csv(
    csv_path: Path,
    *,
    online: bool = False,
    lookup: Callable[[str], dict] | None = None,
) -> dict:
    """Audit complet d'un fichier CSV de tiers pour le marché français.

    ``online=True`` rapproche chaque SIREN syntaxiquement valide de la base SIRENE publique
    (entreprises radiées, SIREN inconnus). ``lookup`` permet d'injecter la fonction de
    recherche (tests hors réseau) ; par défaut ``sirene_lookup``.
    """
    if not csv_path.exists():
        raise FileNotFoundError(f"Fichier introuvable : {csv_path}")

    results = {
        "total": 0,
        "valides": 0,
        "erreurs_siren": 0,
        "erreurs_siret": 0,
        "erreurs_tva": 0,
        "doublons": 0,
        "online": online,
        "radiees": 0,
        "sirene_inconnues": 0,
        "sirene_indisponible": 0,
        "sirene_indeterminees": 0,
        "anomalies": [],
        "annotees": [],
    }
    resolver = lookup or sirene_lookup

    seen_dedup: dict[str, int] = {}
    valid_lines = _read_csv_lines_multi_encoding(csv_path)
    if not valid_lines:
        return results

    first_record_line = next((line for line in valid_lines if line.strip()), "")
    delimiter = ";" if ";" in first_record_line else ","
    reader = csv.DictReader(valid_lines, delimiter=delimiter)
    fields = reader.fieldnames or []

    cols = {
        "nom": next(
            (c for c in fields if re.search(r"nom|raison|client|fournisseur", c, re.I)), None
        ),
        "siren": next((c for c in fields if re.search(r"siren", c, re.I)), None),
        "siret": next((c for c in fields if re.search(r"siret", c, re.I)), None),
        "tva": next((c for c in fields if re.search(r"tva|vat", c, re.I)), None),
        "cp": next((c for c in fields if re.search(r"cp|postal|zip", c, re.I)), None),
    }

    for line_no, row in enumerate(reader, start=2):
        _process_french_row(row, cols, line_no, seen_dedup, results, online, resolver)

    return results


def _duplicate_siren_digits(row: dict, cols: dict) -> str:
    """Return only well-formed identifier digits for duplicate matching, not validity claims."""
    siren_val = row.get(cols["siren"], "") if cols["siren"] else ""
    siret_val = row.get(cols["siret"], "") if cols["siret"] else ""
    tva_val = (row.get(cols["tva"], "") or "") if cols["tva"] else ""

    if siren_val:
        digits, syntax_ok = _numeric_identifier_digits(siren_val)
        return digits if syntax_ok and len(digits) == 9 else ""
    if siret_val:
        digits, syntax_ok = _numeric_identifier_digits(siret_val)
        return digits[:9] if syntax_ok and len(digits) == 14 else ""
    tva_compact = re.sub(r"[ .]", "", (tva_val or "").upper().strip())
    if re.fullmatch(r"FR[0-9]{11}", tva_compact):
        return tva_compact[4:]
    return ""


def _clean_siren(row: dict, cols: dict) -> str:
    """SIREN validé, dérivé par priorité du SIREN, SIRET puis numéro de TVA FR."""
    siren_val = row.get(cols["siren"], "") if cols["siren"] else ""
    siret_val = row.get(cols["siret"], "") if cols["siret"] else ""
    tva_val = (row.get(cols["tva"], "") or "") if cols["tva"] else ""

    if siren_val:
        valid, digits, _ = siren_check(siren_val)
        return digits if valid else ""
    if siret_val:
        valid, digits, _ = siret_check(siret_val)
        return digits[:9] if valid else ""
    if tva_val:
        valid, normalized_tva, _ = tva_fr_check(tva_val)
        if valid and normalized_tva.startswith("FR"):
            return normalized_tva[4:]
    return ""


def _process_french_row(
    row: dict,
    cols: dict,
    line_no: int,
    seen_dedup: dict,
    results: dict,
    online: bool,
    resolver: Callable[[str], dict],
) -> None:
    """Valide une ligne, la compte, l'annote et l'ajoute à `results` (mutation volontaire)."""
    results["total"] += 1
    line_errors, err_siren, err_siret, err_tva = _validate_french_row(
        row, cols, line_no, seen_dedup
    )
    has_local_errors = bool(line_errors)
    results["erreurs_siren"] += int(err_siren)
    results["erreurs_siret"] += int(err_siret)
    results["erreurs_tva"] += int(err_tva)
    results["doublons"] += int(any("DOUBLON" in err for err in line_errors))

    nom_val = row.get(cols["nom"], "") if cols["nom"] else ""
    siren_val = row.get(cols["siren"], "") if cols["siren"] else ""
    clean_s = _clean_siren(row, cols)
    siren_ok = len(clean_s) == 9 and luhn_ok(clean_s)

    sirene_statut, sirene_nom = "", ""
    if online and siren_ok:
        sirene_errors, sirene_statut, sirene_nom = _sirene_flags(clean_s, resolver)
        line_errors.extend(sirene_errors)
        counter = {
            "RADIEE": "radiees",
            "INCONNU": "sirene_inconnues",
            "INDISPONIBLE": "sirene_indisponible",
            "INDETERMINE": "sirene_indeterminees",
        }
        if sirene_statut in counter:
            results[counter[sirene_statut]] += 1

    if line_errors:
        results["anomalies"].append(
            {
                "ligne": line_no,
                "nom": nom_val,
                # Précédence : l'ancien `a or b if c else ""` renvoyait "" dès que la
                # colonne SIRET manquait, même avec un SIREN présent.
                "siren": re.sub(r"\D", "", siren_val or "") or clean_s,
                "erreurs": line_errors,
            }
        )
    else:
        results["valides"] += 1

    row_ann = dict(row)
    row_ann["ANOMALIES_RFE"] = "; ".join(line_errors) if line_errors else "AUCUNE_ANOMALIE_DETECTEE"
    if sirene_statut in {"INDISPONIBLE", "INDETERMINE", "INCONNU"} and not has_local_errors:
        row_ann["STATUT_RFE"] = "A_VERIFIER"
    elif line_errors:
        row_ann["STATUT_RFE"] = "A_CORRIGER"
    else:
        row_ann["STATUT_RFE"] = "CONTROLES_LOCAUX_VALIDES"
    row_ann["SIREN_ASSAINI"] = clean_s if siren_ok else ""
    row_ann["TVA_FR_CALCULEE"] = compute_french_vat_key(clean_s) if siren_ok else ""
    if cols["cp"] and row.get(cols["cp"]):
        cp_ok, healed_cp, _ = validate_french_postal_code(row.get(cols["cp"], ""))
        row_ann["CP_ASSAINI"] = healed_cp if cp_ok else ""
    if online:
        row_ann["SIRENE_STATUT"] = sirene_statut or "NON_VERIFIE"
        row_ann["SIRENE_NOM_OFFICIEL"] = sirene_nom
    results["annotees"].append(row_ann)


def format_french_report(results: dict, filename: str, report_date: date | None = None) -> str:
    total = results["total"]
    valides = results["valides"]
    pct = (valides / total * 100) if total > 0 else 0.0
    online = bool(results.get("online"))
    when = (report_date or date.today()).isoformat()
    perimetre = (
        "contrôles algorithmiques + rapprochement SIRENE (base publique)"
        if online
        else "contrôles algorithmiques hors ligne (clés Luhn/TVA, doublons) — sans rapprochement SIRENE"
    )

    lines = [
        f"# Rapport d'Audit Référentiels RFE France — {filename}",
        f"**Date :** {when} · **Cadre Réglementaire :** Réforme Facturation Électronique (DGFiP / Factur-X)",
        f"**Périmètre du contrôle :** {perimetre}",
        "",
        "## 1. Résultat des contrôles",
        "| Indicateur | Résultat | Interprétation |",
        "|---|---|---|",
        f"| Fiches traitées | **{total}** | Total du fichier |",
        (
            f"| Fiches sans anomalie détectée dans ce périmètre | **{valides}** ({pct:.1f}%) | "
            "Contrôles algorithmiques; ni certification ni autorisation d'émettre |"
        ),
        f"| Erreurs SIREN / SIRET | **{results['erreurs_siren'] + results['erreurs_siret']}** | À corriger ou vérifier |",
        f"| Erreurs TVA intracommunautaire | **{results['erreurs_tva']}** | Contrôle local de format et de clé uniquement |",
        f"| Doublons détectés | **{results['doublons']}** | À examiner avant fusion |",
    ]
    if online:
        lines += [
            f"| SIREN au statut cessé dans SIRENE | **{results.get('radiees', 0)}** | Vérifier le statut et le tiers |",
            f"| Aucun résultat exact SIRENE | **{results.get('sirene_inconnues', 0)}** | Vérifier auprès du tiers |",
            f"| SIRENE indisponible | **{results.get('sirene_indisponible', 0)}** | Contrôle à relancer |",
            f"| Statut SIRENE incomplet | **{results.get('sirene_indeterminees', 0)}** | Vérification manuelle requise |",
        ]
    lines += [
        "",
        "## 2. Repères réglementaires (France)",
        "- Le barème publié par l'administration prévoit, pour l'émission hors format requis, "
        "50 € par facture dans la limite de 15 000 €/an; la première infraction n'est pas sanctionnée.",
        "- Échéances d'émission annoncées : 1er septembre 2026 pour les grandes entreprises et ETI; "
        "1er septembre 2027 pour les PME et micro-entreprises.",
        "- Ces échéances et montants ne constituent pas une estimation de risque pour une entreprise. "
        "Les anomalies du fichier ne prouvent ni un rejet de facture ni l'applicabilité d'une sanction.",
        f"- {total - valides} fiches comportent au moins une anomalie dans le périmètre testé; "
        "elles sont à examiner avec les sources métier avant leur utilisation.",
        "",
        "## 3. Plan d'action suggéré",
        "1. Vérifier les SIREN/SIRET, numéros de TVA et codes postaux signalés auprès de sources fiables.",
        (
            "2. Confirmer auprès du tiers tout statut SIRENE cessé, inconnu ou indéterminé."
            if online
            else "2. Ce rapport est hors ligne : le rapprochement SIRENE (statut, raison sociale) "
            "n'a pas été effectué; l'option `--online` le demande pour les SIREN valides."
        ),
        "3. Examiner les doublons proposés avant toute fusion; le rapport ne modifie pas le référentiel.",
    ]

    if results["anomalies"]:
        lines.append("")
        lines.append("## 4. Échantillon des Anomalies")
        lines.append("| Ligne | Nom | SIREN | Erreurs Détectées |")
        lines.append("|---|---|---|---|")
        for item in results["anomalies"][:15]:
            lines.append(
                f"| {item['ligne']} | {item['nom']} | {item['siren']} | {', '.join(item['erreurs'])} |"
            )

    return "\n".join(lines)
