#!/usr/bin/env python3
"""
Module Belgium Validator — Hard Currency Engine
Audit et mise en conformité des référentiels clients/fournisseurs pour Peppol Belgique (B2B).
"""

from __future__ import annotations

import csv
import re
import unicodedata
from datetime import date
from pathlib import Path

from tools.hard_currency_engine.contracts import flag_duplicate
from tools.hard_currency_engine.csv_safety import (
    read_csv_lines_multi_encoding,
    write_cleaned_csv,
)


def strip_accents(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def norm(s: str) -> str:
    s = strip_accents((s or "").upper())
    return re.sub(r"[^A-Z0-9]", "", s)


#: En-têtes (normalisés : sans accents, minuscules, alphanumériques) désignant sans ambiguïté
#: la colonne du numéro d'entreprise, en français et en néerlandais.
_BCE_HEADERS = frozenset(
    {
        "bce",
        "kbo",
        "cbe",
        "nbce",
        "nkbo",
        "numerobce",
        "numerokbo",
        "kbonummer",
        "bcenummer",
        "numeroentreprise",
        "numerodentreprise",
        "nentreprise",
        "ondernemingsnummer",
        "ondernemingsnr",
        "enterprisenumber",
        "entreprise",
        "siren",
    }
)
_NAME_HEADER = re.compile(r"nom|raison|naam|name|client|fournisseur|leverancier|klant", re.I)


def _find_bce_column(fields: list[str]) -> str | None:
    """Colonne du numéro BCE/KBO — jamais une colonne de nom (`Nom_entreprise` contient
    « entreprise » et faisait valider la raison sociale comme numéro : 100 % de faux rejets)."""
    normalized = {field: re.sub(r"[^a-z0-9]", "", strip_accents(field).lower()) for field in fields}
    for field, key in normalized.items():
        if key in _BCE_HEADERS:
            return field
    for field in fields:
        if _NAME_HEADER.search(field):
            continue
        if re.search(r"bce|kbo|ondernemingsnummer|entreprise|siren", field, re.I):
            return field
    return None


def validate_bce_modulo97(raw_number: str) -> tuple[bool, str, str]:
    """Valide le format d'un numéro BCE/KBO et sa clé Modulo 97."""
    raw = (raw_number or "").strip()
    if not re.fullmatch(r"[0-9]+(?:[ .]+[0-9]+)*", raw):
        digits = re.sub(r"[^0-9]", "", raw)
        return False, digits, "Format invalide (chiffres, espaces et points uniquement)"
    digits = re.sub(r"[ .]", "", raw)
    if len(digits) == 9:
        digits = "0" + digits

    if len(digits) != 10:
        return False, digits, f"Longueur {len(digits)} ≠ 10"

    if digits[0] not in ("0", "1"):
        return False, digits, f"Le numéro doit débuter par 0 ou 1 ({digits[0]})"

    base8 = int(digits[:8])
    checksum = int(digits[8:])
    rem = base8 % 97
    expected = 97 if rem == 0 else (97 - rem)

    if checksum != expected:
        return False, digits, f"Échec Modulo 97 (trouvé={checksum:02d}, attendu={expected:02d})"

    formatted = f"{digits[:4]}.{digits[4:7]}.{digits[7:]}"
    return True, formatted, "OK"


def _validated_bce_digits(bce_number: str) -> str:
    valid, formatted, message = validate_bce_modulo97(bce_number)
    if not valid:
        raise ValueError(f"Numéro BCE invalide : {message}")
    return formatted.replace(".", "")


def format_peppol_id(bce_clean: str) -> str:
    """Construit un identifiant Peppol uniquement à partir d'un numéro BCE valide."""
    return f"0208:{_validated_bce_digits(bce_clean)}"


def get_peppol_directory_url(bce_clean: str) -> str:
    """Génère l'URL Peppol Directory pour un participant à l'identifiant validé."""
    digits = _validated_bce_digits(bce_clean)
    return f"https://directory.peppol.eu/participant/iso6523-actorid-upis%3A%3A0208%3A{digits}"


def get_kbo_public_url(bce_clean: str) -> str:
    """Génère l'URL de consultation BCE/KBO pour un numéro d'entreprise validé."""
    digits = _validated_bce_digits(bce_clean)
    return f"https://kbopub.economie.fgov.be/kbopub/zoeknummerform.html?numero={digits}"


def validate_belgian_postal_code(cp: str) -> tuple[bool, str, str]:
    """Valide un code postal belge composé exactement de quatre chiffres ASCII."""
    raw = (cp or "").strip()
    if not re.fullmatch(r"[0-9]{4}", raw):
        digits = re.sub(r"[^0-9]", "", raw)
        return False, digits, "Format invalide (4 chiffres ASCII uniquement)"
    digits = raw
    val = int(digits)
    if 1000 <= val <= 9992:
        return True, digits, "OK"
    return False, digits, f"Code postal {digits} hors plage belge (1000-9992)"


def validate_belgian_vat(vat_str: str) -> tuple[bool, str, str]:
    raw = (vat_str or "").strip().upper()
    compact = re.sub(r"[ .]", "", raw)
    if not compact.startswith("BE"):
        return False, compact, "Préfixe BE manquant"
    if not re.fullmatch(r"BE[0-9]{10}", compact):
        return False, compact, "Format invalide (BE suivi de 10 chiffres ASCII)"
    ok, num, err = validate_bce_modulo97(compact[2:])
    if not ok:
        return False, compact, f"TVA invalide: {err}"
    return True, f"BE{num.replace('.', '')}", "OK"


def _duplicate_bce_digits(value: str) -> str:
    """Return well-formed BCE digits for repeat detection, without asserting validity."""
    raw = (value or "").strip()
    if not re.fullmatch(r"[0-9]+(?:[ .]+[0-9]+)*", raw):
        return ""
    digits = re.sub(r"[ .]", "", raw)
    if len(digits) == 9:
        digits = "0" + digits
    return digits if len(digits) == 10 else ""


def _validate_belgian_row(  # noqa: PLR0912 — one pass mirrors the required-field checklist
    row: dict, cols: dict, line_no: int, seen_dedup: dict
) -> tuple[list[str], bool, bool]:
    line_errors = []
    nom_val = row.get(cols["nom"], "") if cols["nom"] else ""
    bce_val = row.get(cols["bce"], "") if cols["bce"] else ""
    tva_val = row.get(cols["tva"], "") if cols["tva"] else ""
    cp_val = row.get(cols["cp"], "") if cols["cp"] else ""
    tva_compact = re.sub(r"[ .]", "", (tva_val or "").upper().strip())

    err_bce = False
    err_tva = False
    bce_digits = ""

    if bce_val:
        ok_bce, normalized_bce, msg_bce = validate_bce_modulo97(bce_val)
        if not ok_bce:
            err_bce = True
            line_errors.append(f"BCE_INVALID({msg_bce})")
        else:
            bce_digits = normalized_bce.replace(".", "")
    elif tva_compact.startswith("BE"):
        ok_bce, normalized_bce, msg_bce = validate_bce_modulo97(tva_compact[2:])
        if not ok_bce:
            err_bce = True
            line_errors.append(f"BCE_DERIVE_TVA_INVALID({msg_bce})")
        else:
            bce_digits = normalized_bce.replace(".", "")
    else:
        err_bce = True
        line_errors.append("BCE_MANQUANT")

    if tva_val:
        ok_tva, normalized_tva, msg_tva = validate_belgian_vat(tva_val)
        if not ok_tva:
            err_tva = True
            line_errors.append(f"TVA_INVALID({msg_tva})")
        elif bce_digits and normalized_tva[2:] != bce_digits:
            err_bce = True
            err_tva = True
            line_errors.append("BCE_TVA_MISMATCH(les deux numéros valides ne correspondent pas)")

    if cp_val:
        ok_cp, _, msg_cp = validate_belgian_postal_code(cp_val)
        if not ok_cp:
            line_errors.append(f"CP_INVALID({msg_cp})")

    dedup_keys = []
    dedup_bce = _duplicate_bce_digits(bce_val)
    if not bce_val:
        vat_match = re.fullmatch(r"BE([0-9]{10})", tva_compact)
        dedup_bce = vat_match.group(1) if vat_match else ""
    if dedup_bce:
        dedup_keys.append(f"BCE:{dedup_bce}")
    name_cp_key = f"{norm(nom_val)}_{norm(cp_val)}"
    if len(name_cp_key) > 5:
        dedup_keys.append(f"NOM_CP:{name_cp_key}")
    flag_duplicate(line_errors, seen_dedup, line_no, dedup_keys)

    return line_errors, err_bce, err_tva


def _read_csv_lines_multi_encoding(csv_path: Path) -> list[str]:
    """Conserve l'API interne historique et respecte les limites des enregistrements CSV."""
    return read_csv_lines_multi_encoding(csv_path)


def export_cleaned_belgian_csv(results: dict, out_path: Path) -> Path:
    """Exporte les données annotées avec neutralisation des cellules de tableur."""
    return write_cleaned_csv(results.get("annotees", []), out_path)


def audit_belgian_csv(csv_path: Path) -> dict:
    if not csv_path.exists():
        raise FileNotFoundError(f"Fichier introuvable : {csv_path}")

    results = {
        "total": 0,
        "valides": 0,
        "erreurs_bce": 0,
        "erreurs_tva": 0,
        "doublons": 0,
        "anomalies": [],
        "annotees": [],
    }

    seen_dedup: dict[str, int] = {}
    valid_lines = _read_csv_lines_multi_encoding(csv_path)
    if not valid_lines:
        return results

    first_record_line = next((line for line in valid_lines if line.strip()), "")
    delimiter = ";" if ";" in first_record_line else ","
    reader = csv.DictReader(valid_lines, delimiter=delimiter)
    fields = reader.fieldnames or []

    cols = {
        "nom": next((c for c in fields if _NAME_HEADER.search(c)), None),
        "bce": _find_bce_column(fields),
        "tva": next((c for c in fields if re.search(r"tva|vat|btw", c, re.I)), None),
        "cp": next((c for c in fields if re.search(r"cp|postal|zip|postcode", c, re.I)), None),
    }

    for line_no, row in enumerate(reader, start=2):
        results["total"] += 1
        line_errors, err_bce, err_tva = _validate_belgian_row(row, cols, line_no, seen_dedup)
        if err_bce:
            results["erreurs_bce"] += 1
        if err_tva:
            results["erreurs_tva"] += 1
        if any("DOUBLON" in err for err in line_errors):
            results["doublons"] += 1

        nom_val = row.get(cols["nom"], "") if cols["nom"] else ""
        bce_val = row.get(cols["bce"], "") if cols["bce"] else ""

        if line_errors:
            results["anomalies"].append(
                {
                    "ligne": line_no,
                    "nom": nom_val,
                    "bce": bce_val,
                    "erreurs": line_errors,
                }
            )
        else:
            results["valides"] += 1

        row_ann = dict(row)
        tva_input = (row.get(cols["tva"], "") or "") if cols["tva"] else ""
        if bce_val:
            bce_source = bce_val
        else:
            ok_vat, normalized_vat, _ = validate_belgian_vat(tva_input)
            bce_source = normalized_vat[2:] if ok_vat else ""

        ok_mod97, formatted_bce, _ = (
            validate_bce_modulo97(bce_source) if bce_source else (False, "", "BCE manquant")
        )
        clean_bce_digits = formatted_bce.replace(".", "") if ok_mod97 else ""

        row_ann["ANOMALIES_PEPPOL"] = (
            "; ".join(line_errors) if line_errors else "AUCUNE_ANOMALIE_DETECTEE"
        )
        row_ann["PEPPOL_ID"] = format_peppol_id(clean_bce_digits) if ok_mod97 else "A_CORRIGER"
        row_ann["STATUT_PEPPOL"] = "FORMAT_VALIDE_NON_VERIFIE" if not line_errors else "A_CORRIGER"
        row_ann["ANNUAIRE_PEPPOL_STATUT"] = "NON_VERIFIE"
        row_ann["BCE_ASSAINI"] = formatted_bce if ok_mod97 else ""
        row_ann["TVA_BE_CALCULEE"] = f"BE{clean_bce_digits}" if ok_mod97 else ""
        row_ann["PEPPOL_DIRECTORY_URL"] = (
            get_peppol_directory_url(clean_bce_digits) if ok_mod97 else ""
        )
        row_ann["KBO_LOOKUP_URL"] = get_kbo_public_url(clean_bce_digits) if ok_mod97 else ""
        if cols["cp"] and row.get(cols["cp"]):
            cp_ok, healed_cp, _ = validate_belgian_postal_code(row.get(cols["cp"], ""))
            row_ann["CP_ASSAINI"] = healed_cp if cp_ok else ""
        results["annotees"].append(row_ann)

    return results


def format_belgian_report(results: dict, filename: str, report_date: date | None = None) -> str:
    total = results["total"]
    valides = results["valides"]
    pct = (valides / total * 100) if total > 0 else 0.0
    when = (report_date or date.today()).isoformat()

    lines = [
        f"# Rapport de Diagnostic Peppol Belgique — {filename}",
        f"**Date :** {when} · **Cadre :** Arrêté Royal Facturation Électronique B2B Obligatoire",
        "**Périmètre du contrôle :** contrôles algorithmiques hors ligne (Modulo 97, TVA, codes postaux, doublons) — l'inscription effective à l'annuaire Peppol se vérifie via les liens fournis dans le CSV",
        "",
        "## 1. Résultat des contrôles hors ligne",
        "| Indicateur | Valeur | Interprétation |",
        "|---|---|---|",
        f"| Total fiches auditées | **{total}** | Lignes de données traitées |",
        f"| Fiches sans anomalie détectée | **{valides}** ({pct:.1f}%) | "
        "Format/clé localement valides; inscription Peppol non vérifiée |",
        f"| Numéros BCE / KBO invalides | **{results['erreurs_bce']}** | À corriger ou vérifier |",
        f"| Numéros de TVA invalides | **{results['erreurs_tva']}** | Contrôle local de format et de clé |",
        f"| Doublons détectés | **{results['doublons']}** | À examiner avant fusion |",
        "",
        "## 2. Cadre et limites",
        "- La facturation électronique structurée B2B est obligatoire en Belgique depuis le 1er janvier 2026 "
        "pour la plupart des opérations dans le champ légal; des exceptions et mesures techniques existent.",
        "- Cet audit ne consulte pas le répertoire Peppol, ne teste pas la réception du destinataire et "
        "ne vérifie pas l'intégration avec un logiciel comptable ou une plateforme.",
        f"- {total - valides} fiches comportent au moins une anomalie dans le périmètre testé; cela ne prouve "
        "pas, à lui seul, qu'une facture sera rejetée ou qu'une sanction s'applique.",
    ]

    if results.get("anomalies"):
        lines.append("")
        lines.append("## 3. Échantillon des Anomalies")
        lines.append("| Ligne | Nom | BCE | Erreurs Détectées |")
        lines.append("|---|---|---|---|")
        for item in results["anomalies"][:15]:
            lines.append(
                f"| {item['ligne']} | {item['nom']} | {item['bce']} | {', '.join(item['erreurs'])} |"
            )
    return "\n".join(lines)
