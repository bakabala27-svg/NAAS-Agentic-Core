#!/usr/bin/env python3
"""
Tests unitaires pour la suite Hard Currency Engine (HCE).
Couvre la validation France, Belgique Peppol, CBAM, ZATCA, EAA, CRM et Contrats.
"""

from __future__ import annotations

import contextlib
import csv
import io
import json
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from shared.research.opportunity_score import CONFIGURATION_OUTBOUND
from tools.hard_currency_engine import cli as hce_cli
from tools.hard_currency_engine.belgium_validator import (
    audit_belgian_csv,
    export_cleaned_belgian_csv,
    format_belgian_report,
    format_peppol_id,
    get_kbo_public_url,
    get_peppol_directory_url,
    validate_bce_modulo97,
    validate_belgian_postal_code,
    validate_belgian_vat,
)
from tools.hard_currency_engine.cbam_calculator import (
    CBAM_CATALOG,
    calculate_cbam,
    calculate_cbam_batch,
    generate_cbam_batch_xml,
    generate_cbam_xml,
    generate_sensitivity_table,
)
from tools.hard_currency_engine.contracts import (
    AnomalyRecord,
    AnomalySeverity,
    AuditSummary,
    CorridorType,
    FinancialArbitrage,
)
from tools.hard_currency_engine.crm_dispatcher import (
    dispatch_campaign,
    generate_personalized_dispatch,
)
from tools.hard_currency_engine.eaa_scanner import (
    audit_html_content,
    generate_declaration_accessibilite,
    remediate_html_content,
)
from tools.hard_currency_engine.france_validator import (
    audit_french_csv,
    compute_french_vat_key,
    export_cleaned_french_csv,
    format_french_report,
    luhn_ok,
    siren_check,
    sirene_lookup,
    siret_check,
    tva_fr_check,
    validate_french_postal_code,
)
from tools.hard_currency_engine.zatca_validator import (
    GENESIS_PIH,
    audit_zatca_batch,
    canonical_invoice_hash,
    decode_zatca_tlv,
    encode_zatca_tlv,
    generate_sample_zatca_ubl_xml,
    repair_zatca_chain,
    validate_uuid_v4,
    validate_zatca_invoice_type,
    validate_zatca_vat_number,
)


class TestFranceValidator(unittest.TestCase):
    def test_luhn_algorithm(self):
        self.assertTrue(luhn_ok("501058812"))
        self.assertTrue(luhn_ok("443061841"))
        self.assertFalse(luhn_ok("501058813"))

    def test_siren_and_siret(self):
        ok, clean, _msg = siren_check("501 058 812")
        self.assertTrue(ok)
        self.assertEqual(clean, "501058812")

        ok_bad, _, _ = siren_check("12345")
        self.assertFalse(ok_bad)

        ok_st, clean_st, _ = siret_check("50105881210005")
        self.assertTrue(ok_st)
        self.assertEqual(clean_st, "50105881210005")

        # Règle officielle La Poste (SIREN 356000000)
        ok_poste, _, msg_poste = siret_check("35600000000042")
        self.assertTrue(ok_poste)
        self.assertIn("La Poste", msg_poste)

    def test_french_vat_derivation(self):
        ok, formatted, _ = tva_fr_check("FR64443061841")
        self.assertTrue(ok)
        self.assertEqual(formatted, "FR64443061841")

        computed = compute_french_vat_key("443061841")
        self.assertEqual(computed, "FR64443061841")

        ok_wrong, _, msg = tva_fr_check("FR99443061841")
        self.assertFalse(ok_wrong)
        self.assertIn("Clé erronée", msg)

        # Intra-EU VAT format
        ok_eu, _, msg_eu = tva_fr_check("BE0123456749")
        self.assertTrue(ok_eu)
        self.assertIn("Intra-UE", msg_eu)
        self.assertFalse(tva_fr_check("BEABC123")[0])

    def test_french_postal_code(self):
        ok, cp_clean, _ = validate_french_postal_code("75008")
        self.assertTrue(ok)
        self.assertEqual(cp_clean, "75008")

        # Heals Excel dropped leading zero (e.g. 1000 -> 01000)
        ok_healed, cp_healed, _ = validate_french_postal_code("1000")
        self.assertTrue(ok_healed)
        self.assertEqual(cp_healed, "01000")

        self.assertFalse(validate_french_postal_code("x75008y")[0])
        self.assertFalse(siren_check("x443061841y")[0])
        self.assertFalse(siret_check("123")[0])
        self.assertFalse(siret_check("x44306184100047y")[0])
        self.assertFalse(tva_fr_check("FR64x443061841")[0])

    def test_french_audit_and_export_csv(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_in = Path(tmpdir) / "test_tiers.csv"
            csv_out = Path(tmpdir) / "test_clean.csv"
            # Encode with ISO-8859-1 (common Sage export)
            content = (
                "Raison_sociale;SIREN;SIRET;Num_TVA_intracom;Code_postal\n"
                "Google France;443061841;44306184100047;FR64443061841;75009\n"
                "Fausse Entité;123456789;12345678900012;FR40123456789;31000\n"
            )
            csv_in.write_bytes(content.encode("iso-8859-1"))

            res = audit_french_csv(csv_in)
            self.assertEqual(res["total"], 2)
            self.assertEqual(res["valides"], 1)

            export_cleaned_french_csv(res, csv_out)
            self.assertTrue(csv_out.exists())
            out_txt = csv_out.read_text(encoding="utf-8-sig")
            self.assertIn("STATUT_RFE", out_txt)
            self.assertIn("FR64443061841", out_txt)


class TestFranceValidatorCustomerPathFixes(unittest.TestCase):
    """Bugs found by the 2026-09-28 asset audit — each test was red before its fix."""

    def test_anomaly_table_keeps_siren_when_file_has_no_siret_column(self):
        # Operator precedence bug: `a or b if c else ""` dropped the SIREN whenever
        # the file had no SIRET column, so the customer report showed an empty cell.
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_in = Path(tmpdir) / "siren_only.csv"
            csv_in.write_text("nom;siren;tva\nACME;123456789;FR40123456789\n", encoding="utf-8")
            res = audit_french_csv(csv_in)
            self.assertEqual(len(res["anomalies"]), 1)
            self.assertEqual(res["anomalies"][0]["siren"], "123456789")

    def test_la_poste_siret_rule_is_sum_multiple_of_five(self):
        # INSEE: La Poste (SIREN 356000000) SIRETs do not follow Luhn; they are valid
        # when the digit sum is a multiple of 5 — not of 10.
        ok_25, _, msg = siret_check("35600000000047")  # digit sum = 25
        self.assertTrue(ok_25, msg)
        self.assertIn("La Poste", msg)
        ok_20, _, _ = siret_check("35600000000042")  # digit sum = 20
        self.assertTrue(ok_20)
        ok_21, _, _ = siret_check("35600000000043")  # digit sum = 21
        self.assertFalse(ok_21)

    def test_report_date_is_the_run_date_not_a_hardcoded_string(self):
        res = {
            "total": 1,
            "valides": 1,
            "erreurs_siren": 0,
            "erreurs_siret": 0,
            "erreurs_tva": 0,
            "doublons": 0,
            "anomalies": [],
            "annotees": [],
        }
        report = format_french_report(res, "x.csv")
        self.assertIn(date.today().isoformat(), report)
        self.assertNotIn("2026-09-24 ·", report.replace(date.today().isoformat(), ""))

    def test_offline_report_does_not_promise_an_insee_match_it_never_did(self):
        res = {
            "total": 1,
            "valides": 0,
            "erreurs_siren": 1,
            "erreurs_siret": 0,
            "erreurs_tva": 0,
            "doublons": 0,
            "anomalies": [
                {"ligne": 2, "nom": "X", "siren": "123456789", "erreurs": ["SIREN_INVALID"]}
            ],
            "annotees": [],
        }
        report = format_french_report(res, "x.csv")
        self.assertNotIn("INSEE", report)
        self.assertIn("hors ligne", report.lower())

    def test_foreign_eu_vat_checks_belgian_checksum_but_accepts_other_country_format(self):
        ok_de, _, message_de = tva_fr_check("DE123456789")
        self.assertTrue(ok_de, message_de)
        self.assertFalse(tva_fr_check("BE0123456750")[0])
        self.assertIn("Modulo 97", tva_fr_check("BE0123456750")[2])

    def test_identifier_derivation_from_siret_and_vat_is_strict(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_in = Path(tmpdir) / "derived_identifiers.csv"
            csv_in.write_text(
                "nom;siret;tva\n"
                "Siret valide;44306184100047;\n"
                "Siret mal formé;4430618410004X;\n"
                "Siren dérivé invalide;12345678900012;\n"
                "TVA valide;;FR40501058812\n"
                "TVA avec SIREN invalide;;FR40123456789\n"
                "TVA mal formée;;FR64x443061841\n"
                "Sans identifiant;;\n",
                encoding="utf-8",
            )
            result = audit_french_csv(csv_in)

        rows = {row["nom"]: row for row in result["annotees"]}
        errors = {item["nom"]: item["erreurs"] for item in result["anomalies"]}
        self.assertEqual(rows["Siret valide"]["SIREN_ASSAINI"], "443061841")
        self.assertEqual(rows["TVA valide"]["SIREN_ASSAINI"], "501058812")
        self.assertTrue(
            any(error.startswith("SIREN_DERIVE_INVALID") for error in errors["Siret mal formé"])
        )
        self.assertTrue(
            any(
                error.startswith("SIREN_DERIVE_INVALID")
                for error in errors["Siren dérivé invalide"]
            )
        )
        self.assertTrue(
            any(
                error.startswith("SIREN_DERIVE_TVA_INVALID")
                for error in errors["TVA avec SIREN invalide"]
            )
        )
        self.assertIn("SIREN_MANQUANT", errors["TVA mal formée"])
        self.assertIn("SIREN_MANQUANT", errors["Sans identifiant"])

    def test_sirene_lookup_uses_exact_identifier_and_preserves_uncertain_states(self):
        active_response = mock.MagicMock()
        active_response.__enter__.return_value.read.return_value = json.dumps(
            {
                "results": [
                    {"siren": "123456789", "etat_administratif": "C"},
                    {
                        "siren": "443061841",
                        "etat_administratif": "A",
                        "nom_complet": "Acme France",
                    },
                ]
            }
        ).encode("utf-8")
        with mock.patch(
            "tools.hard_currency_engine.france_validator.urllib.request.urlopen",
            return_value=active_response,
        ) as urlopen:
            active = sirene_lookup("443061841", timeout=3)
        self.assertEqual(
            active,
            {"trouve": True, "etat": "A", "actif": True, "nom_officiel": "ACME FRANCE"},
        )
        self.assertEqual(urlopen.call_args.kwargs["timeout"], 3)

        missing_response = mock.MagicMock()
        missing_response.__enter__.return_value.read.return_value = json.dumps(
            {"results": [{"siren": "123456789", "etat_administratif": "C"}]}
        ).encode("utf-8")
        with mock.patch(
            "tools.hard_currency_engine.france_validator.urllib.request.urlopen",
            return_value=missing_response,
        ):
            missing = sirene_lookup("443061841")
        self.assertFalse(missing["trouve"])

        unknown_status_response = mock.MagicMock()
        unknown_status_response.__enter__.return_value.read.return_value = json.dumps(
            {"results": [{"siren": "443061841", "nom_complet": "Acme France"}]}
        ).encode("utf-8")
        with mock.patch(
            "tools.hard_currency_engine.france_validator.urllib.request.urlopen",
            return_value=unknown_status_response,
        ):
            unknown_status = sirene_lookup("443061841")
        self.assertEqual(unknown_status["etat"], "?")
        self.assertIsNone(unknown_status["actif"])

    def test_online_lookup_flags_deregistered_and_unknown_companies(self):
        # The outreach templates promise detection of "radiés"; the tool must actually
        # do it. The lookup is injected so the test never touches the network.
        def fake_lookup(siren: str) -> dict:
            return {
                "443061841": {
                    "trouve": True,
                    "actif": True,
                    "etat": "A",
                    "nom_officiel": "GOOGLE FRANCE",
                },
                "501058812": {
                    "trouve": True,
                    "actif": False,
                    "etat": "C",
                    "nom_officiel": "BALAGUE",
                },
                "552032534": {"trouve": False},
            }.get(siren, {"trouve": None, "erreur": "offline"})

        with tempfile.TemporaryDirectory() as tmpdir:
            csv_in = Path(tmpdir) / "tiers.csv"
            csv_in.write_text(
                "nom;siren\nGoogle;443061841\nBalague;501058812\nDanone;552032534\nOrange;380129866\n",
                encoding="utf-8",
            )
            res = audit_french_csv(csv_in, online=True, lookup=fake_lookup)
            flat = {a["siren"]: a["erreurs"] for a in res["anomalies"]}
            self.assertNotIn("443061841", flat)
            self.assertTrue(any(e.startswith("ENTREPRISE_RADIEE") for e in flat["501058812"]))
            self.assertTrue(any(e.startswith("SIREN_INCONNU_SIRENE") for e in flat["552032534"]))
            self.assertTrue(any(e.startswith("SIRENE_INDISPONIBLE") for e in flat["380129866"]))
            self.assertEqual(res["sirene_indisponible"], 1)
            self.assertEqual(res["radiees"], 1)
            self.assertEqual(res["valides"], 1)
            offline_row = next(row for row in res["annotees"] if row["siren"] == "380129866")
            unknown_row = next(row for row in res["annotees"] if row["siren"] == "552032534")
            self.assertEqual(offline_row["STATUT_RFE"], "A_VERIFIER")
            self.assertEqual(unknown_row["STATUT_RFE"], "A_VERIFIER")
            self.assertNotEqual(offline_row["ANOMALIES_RFE"], "AUCUNE_ANOMALIE_DETECTEE")
            report = format_french_report(res, "tiers.csv")
            self.assertIn("SIRENE", report)
            self.assertNotIn("Fiches prêtes à l'émission", report)

    def test_incomplete_sirene_record_is_not_misreported_as_deregistered(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_in = Path(tmpdir) / "tiers.csv"
            csv_in.write_text("nom;siren\nAcme;443061841\n", encoding="utf-8")
            res = audit_french_csv(
                csv_in,
                online=True,
                lookup=lambda _siren: {"trouve": True, "etat": "?", "nom_officiel": "ACME"},
            )

        errors = res["anomalies"][0]["erreurs"]
        self.assertIn("SIRENE_STATUT_INDETERMINE(contrôle à relancer)", errors)
        self.assertFalse(any(error.startswith("ENTREPRISE_RADIEE") for error in errors))
        self.assertEqual(res["sirene_indeterminees"], 1)
        self.assertEqual(res["annotees"][0]["STATUT_RFE"], "A_VERIFIER")

    def test_fine_is_tied_to_the_issuance_deadline_not_stated_as_immediate(self):
        # Loi de finances 2026: 50 €/invoice (cap 15 000 €/year) sanctions *issuing*
        # outside the e-invoicing format — GE/ETI from 2026-09-01, SMEs from 2027-09-01.
        # A report sent to an SME accounting firm must not read as a fine due today.
        res = {
            "total": 1,
            "valides": 0,
            "erreurs_siren": 1,
            "erreurs_siret": 0,
            "erreurs_tva": 0,
            "doublons": 0,
            "anomalies": [],
            "annotees": [],
        }
        report = format_french_report(res, "x.csv")
        self.assertIn("émission", report)
        self.assertIn("1er septembre 2027", report)

    def test_same_siren_with_a_legal_form_suffix_is_a_duplicate(self):
        # Live run 2026-09-29 on DEMO_20_FICHES (rows 4/5): «BOULANGERIE MARTIN» and
        # «Boulangerie Martin SAS» share one SIREN, but the key was name + postcode, so
        # the pair was never flagged — while merging duplicates is a promised outcome.
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_in = Path(tmpdir) / "tiers.csv"
            csv_in.write_text(
                "nom;siren;cp\nOrange;380129866;75015\nOrange SA;380 129 866;75015\n"
                "Google;443061841;75009\n",
                encoding="utf-8",
            )
            res = audit_french_csv(csv_in)
            self.assertEqual(res["doublons"], 1, res["anomalies"])
            flat = {a["ligne"]: a["erreurs"] for a in res["anomalies"]}
            self.assertIn("DOUBLON_AVEC_LIGNE_2", flat[3])

    def test_same_name_in_another_town_with_another_siren_is_not_a_duplicate(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_in = Path(tmpdir) / "tiers.csv"
            csv_in.write_text(
                "nom;siren;cp\nOrange;380129866;75015\nOrange;443061841;69001\n",
                encoding="utf-8",
            )
            self.assertEqual(audit_french_csv(csv_in)["doublons"], 0)

    def test_name_and_postcode_still_catch_duplicates_without_an_identifier(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_in = Path(tmpdir) / "tiers.csv"
            csv_in.write_text("nom;siren;cp\nACME;;75001\nAcme;;75001\n", encoding="utf-8")
            self.assertEqual(audit_french_csv(csv_in)["doublons"], 1)

    def test_comment_lines_inside_quoted_multiline_fields_are_preserved(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_in = Path(tmpdir) / "tiers.csv"
            csv_in.write_text(
                '# début\nnom;siren\n# commentaire\n"ACME\n#Acme;443061841\nSA";443061841\n',
                encoding="utf-8",
            )
            result = audit_french_csv(csv_in)
            self.assertEqual(result["total"], 1)
            self.assertEqual(result["valides"], 1)
            self.assertEqual(result["annotees"][0]["nom"], "ACME\n#Acme;443061841\nSA")

    def test_doubled_quotes_and_comment_records_in_a_multiline_field(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_in = Path(tmpdir) / "quoted.csv"
            csv_in.write_text(
                '# début\nnom;siren\n"ACME ""North""\n# note;443061841\nSA";443061841\n# fin\n',
                encoding="utf-8",
            )
            result = audit_french_csv(csv_in)
            self.assertEqual(result["total"], 1)
            self.assertEqual(result["annotees"][0]["nom"], 'ACME "North"\n# note;443061841\nSA')


class TestBelgiumValidator(unittest.TestCase):
    def test_bce_modulo97(self):
        ok, formatted, _msg = validate_bce_modulo97("0123.456.749")
        self.assertTrue(ok)
        self.assertEqual(formatted, "0123.456.749")

        ok_short, padded, _ = validate_bce_modulo97("123456749")
        self.assertTrue(ok_short)
        self.assertEqual(padded, "0123.456.749")

        ok_bad, _, msg_bad = validate_bce_modulo97("0123.456.750")
        self.assertFalse(ok_bad)
        self.assertIn("Échec Modulo 97", msg_bad)
        self.assertFalse(validate_bce_modulo97("0123X.456.749")[0])
        self.assertIn("Longueur", validate_bce_modulo97("12345")[2])
        self.assertIn("débuter par 0 ou 1", validate_bce_modulo97("2123456749")[2])

    def test_belgian_vat_and_peppol_id(self):
        ok, vat, _ = validate_belgian_vat("BE0123456749")
        self.assertTrue(ok)
        self.assertEqual(vat, "BE0123456749")

        peppol_id = format_peppol_id("0123.456.749")
        self.assertEqual(peppol_id, "0208:0123456749")

        dir_url = get_peppol_directory_url("0123.456.749")
        self.assertIn("directory.peppol.eu", dir_url)
        self.assertIn("0208%3A0123456749", dir_url)

        kbo_url = get_kbo_public_url("0123.456.749")
        self.assertIn("kbopub.economie.fgov.be", kbo_url)
        self.assertFalse(validate_belgian_vat("BEABC0123456749")[0])
        self.assertIn("Préfixe BE manquant", validate_belgian_vat("FR0123456749")[2])
        self.assertIn("TVA invalide", validate_belgian_vat("BE0123456750")[2])
        with self.assertRaises(ValueError):
            format_peppol_id("0123X.456.749")

    def test_belgian_postal_code(self):
        ok, cp, _ = validate_belgian_postal_code("1000")
        self.assertTrue(ok)
        self.assertEqual(cp, "1000")

        ok_bad, _, _ = validate_belgian_postal_code("0500")
        self.assertFalse(ok_bad)
        self.assertFalse(validate_belgian_postal_code("B1000X")[0])

    def test_belgian_audit_and_export_csv(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_in = Path(tmpdir) / "test_be.csv"
            csv_out = Path(tmpdir) / "test_be_clean.csv"
            content = (
                "Raison_sociale;Numero_BCE;Numero_TVA;Code_postal\n"
                "Société Conforme;0123.456.749;BE0123456749;1000\n"
            )
            csv_in.write_bytes(content.encode("cp1252"))

            res = audit_belgian_csv(csv_in)
            self.assertEqual(res["total"], 1)
            self.assertEqual(res["valides"], 1)

            export_cleaned_belgian_csv(res, csv_out)
            self.assertTrue(csv_out.exists())
            out_txt = csv_out.read_text(encoding="utf-8-sig")
            self.assertIn("0208:0123456749", out_txt)
            self.assertIn("FORMAT_VALIDE_NON_VERIFIE", out_txt)
            self.assertIn("directory.peppol.eu", out_txt)

    def test_dirty_belgian_identifiers_do_not_collapse_to_valid_digits(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_in = Path(tmpdir) / "be.csv"
            csv_in.write_text(
                "Nom_entreprise;Numero_BCE;Numero_TVA;Code_postal\n"
                "Proximus;0123X.456.749;BEABC0123456749;B1000X\n",
                encoding="utf-8",
            )
            result = audit_belgian_csv(csv_in)
            row = result["annotees"][0]
            self.assertEqual(result["valides"], 0)
            self.assertEqual(result["erreurs_bce"], 1)
            self.assertEqual(result["erreurs_tva"], 1)
            self.assertEqual(row["STATUT_PEPPOL"], "A_CORRIGER")
            self.assertEqual(row["PEPPOL_ID"], "A_CORRIGER")
            self.assertEqual(row["PEPPOL_DIRECTORY_URL"], "")
            self.assertEqual(row.get("CP_ASSAINI", ""), "")

    def test_comment_lines_inside_quoted_multiline_fields_are_preserved(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_in = Path(tmpdir) / "be.csv"
            csv_in.write_text(
                "# début\nNom_entreprise;Numero_BCE;Code_postal\n# commentaire\n"
                '"ACME\n#Acme;0472.198.275\nSA";0472.198.275;1000\n',
                encoding="utf-8",
            )
            result = audit_belgian_csv(csv_in)
            self.assertEqual(result["total"], 1)
            self.assertEqual(result["valides"], 1, result["anomalies"])
            self.assertEqual(
                result["annotees"][0]["Nom_entreprise"], "ACME\n#Acme;0472.198.275\nSA"
            )
            self.assertEqual(result["annotees"][0]["ANNUAIRE_PEPPOL_STATUT"], "NON_VERIFIE")


class TestBelgiumValidatorCustomerPathFixes(unittest.TestCase):
    """Severe false positive found by the 2026-09-28 audit — red before the fix."""

    def test_nom_entreprise_header_is_not_read_as_the_bce_column(self):
        # Header regex `bce|kbo|entreprise|siren` matched `Nom_entreprise` first, so the
        # company NAME was validated as a BCE number and every real company failed.
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_in = Path(tmpdir) / "be.csv"
            csv_in.write_text(
                "Nom_entreprise,Numero_BCE,Numero_TVA,Code_postal\n"
                "Proximus,0202.239.951,BE0202239951,1030\n"
                "AB InBev,0417.497.106,BE0417497106,3000\n",
                encoding="utf-8",
            )
            res = audit_belgian_csv(csv_in)
            self.assertEqual(res["total"], 2)
            self.assertEqual(res["valides"], 2, res["anomalies"])
            self.assertEqual(res["erreurs_bce"], 0)

    def test_bce_column_is_found_under_common_dutch_and_french_headers(self):
        for header in ("Ondernemingsnummer", "N° entreprise", "KBO", "BCE", "numero_bce"):
            with tempfile.TemporaryDirectory() as tmpdir:
                csv_in = Path(tmpdir) / "be.csv"
                csv_in.write_text(
                    f"Raison sociale;{header};CP\nProximus;0202239951;1030\n", encoding="utf-8"
                )
                res = audit_belgian_csv(csv_in)
                self.assertEqual(res["valides"], 1, (header, res["anomalies"]))

    def test_bce_column_fallback_skips_company_name_and_matches_qualified_header(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_in = Path(tmpdir) / "be.csv"
            csv_in.write_text(
                "Nom entreprise,Code BCE,TVA\nProximus,0202239951,BE0202239951\n",
                encoding="utf-8",
            )
            result = audit_belgian_csv(csv_in)
            self.assertEqual(result["valides"], 1, result["anomalies"])

    def test_same_bce_with_a_legal_form_suffix_is_a_duplicate(self):
        # Live run 2026-09-29 on DEMO_BELGIUM_PEPPOL_20_FICHES (rows 13/14): one BCE,
        # names differing only by «SA», and the report said «Doublons détectés: 0».
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_in = Path(tmpdir) / "be.csv"
            csv_in.write_text(
                "Nom_entreprise;Numero_BCE;Code_postal\nProximus;0202.239.951;1030\n"
                "Proximus SA;0202239951;1030\nAB InBev;0417.497.106;3000\n",
                encoding="utf-8",
            )
            res = audit_belgian_csv(csv_in)
            self.assertEqual(res["doublons"], 1, res["anomalies"])

    def test_bce_duplicate_key_normalizes_unpadded_numbers_and_vat_fallback(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            unpadded_csv = Path(tmpdir) / "unpadded.csv"
            unpadded_csv.write_text(
                "Nom_entreprise;Numero_BCE\nProximus;202239951\nProximus SA;0202239951\n",
                encoding="utf-8",
            )
            unpadded = audit_belgian_csv(unpadded_csv)
            self.assertEqual(unpadded["doublons"], 1)

            vat_csv = Path(tmpdir) / "vat_only.csv"
            vat_csv.write_text(
                "Nom_entreprise;Numero_TVA\nProximus;BE0202239951\nProximus SA;BE0202239951\n",
                encoding="utf-8",
            )
            vat_only = audit_belgian_csv(vat_csv)

        self.assertEqual(vat_only["doublons"], 1)
        self.assertEqual(vat_only["annotees"][0]["PEPPOL_ID"], "0208:0202239951")
        self.assertEqual(vat_only["annotees"][0]["BCE_ASSAINI"], "0202.239.951")

    def test_valid_bce_and_vat_must_match(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_in = Path(tmpdir) / "mismatch.csv"
            csv_in.write_text(
                "Nom_entreprise;Numero_BCE;Numero_TVA\nProximus;0202239951;BE0417497106\n",
                encoding="utf-8",
            )
            result = audit_belgian_csv(csv_in)

        self.assertEqual(result["erreurs_bce"], 1)
        self.assertEqual(result["erreurs_tva"], 1)
        self.assertTrue(
            any(error.startswith("BCE_TVA_MISMATCH") for error in result["anomalies"][0]["erreurs"])
        )

    def test_belgian_report_has_today_and_an_anomaly_table(self):
        res = {
            "total": 1,
            "valides": 0,
            "erreurs_bce": 1,
            "erreurs_tva": 0,
            "doublons": 0,
            "anomalies": [
                {"ligne": 2, "nom": "X", "bce": "0123456750", "erreurs": ["BCE_INVALID"]}
            ],
            "annotees": [],
        }
        report = format_belgian_report(res, "be.csv")
        self.assertIn(date.today().isoformat(), report)
        self.assertIn("| 2 | X | 0123456750 | BCE_INVALID |", report)


class TestCSVDataSafety(unittest.TestCase):
    def test_both_direct_exporters_neutralize_headers_and_formula_like_cells(self):
        results = {
            "annotees": [
                {
                    "=HYPERLINK(https://example.invalid)": "safe header value",
                    "nom": "\n=1+1",
                    "fullwidth": "＝1+1",
                    "tab": "\t=1+1",
                    "negative_amount": "-12.50",
                    "numeric": -12.5,
                    "zero_width": "\u200b=1+1",
                }
            ]
        }
        exporters = (export_cleaned_french_csv, export_cleaned_belgian_csv)
        for exporter in exporters:
            with self.subTest(exporter=exporter.__name__), tempfile.TemporaryDirectory() as tmpdir:
                output = Path(tmpdir) / "clean.csv"
                exporter(results, output)
                with output.open(encoding="utf-8-sig", newline="") as handle:
                    header, row = list(csv.reader(handle, delimiter=";"))
                self.assertEqual(header[0], "'=HYPERLINK(https://example.invalid)")
                self.assertEqual(row[1], "'\n=1+1")
                self.assertEqual(row[2], "'＝1+1")
                self.assertEqual(row[3], "'\t=1+1")
                self.assertEqual(row[4], "-12.50")
                self.assertEqual(row[5], "-12.5")
                self.assertEqual(row[6], "'\u200b=1+1")

    def test_empty_exports_create_empty_utf8_files(self):
        for exporter in (export_cleaned_french_csv, export_cleaned_belgian_csv):
            with self.subTest(exporter=exporter.__name__), tempfile.TemporaryDirectory() as tmpdir:
                output = Path(tmpdir) / "empty.csv"
                result = exporter({"annotees": []}, output)
                self.assertEqual(result, output)
                self.assertEqual(output.read_bytes(), b"")


class TestCLIPathSafety(unittest.TestCase):
    def test_cli_rejects_source_aliases_before_writing_france_or_belgium_outputs(self):
        for command in ("france", "belgium"):
            with self.subTest(command=command), tempfile.TemporaryDirectory() as tmpdir:
                source = Path(tmpdir) / "source.csv"
                source.write_text("nom;siren\nACME;443061841\n", encoding="utf-8")
                original = source.read_bytes()
                alias = Path(tmpdir) / "alias.csv"
                alias.symlink_to(source)
                stderr = io.StringIO()
                with contextlib.redirect_stderr(stderr):
                    with self.assertRaises(SystemExit) as ctx:
                        hce_cli.main([command, str(source), "--csv-out", str(alias)])
                self.assertEqual(ctx.exception.code, 2)
                self.assertEqual(source.read_bytes(), original)
                self.assertTrue(stderr.getvalue())

    def test_cli_rejects_report_output_equal_to_source(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            source = Path(tmpdir) / "source.csv"
            source.write_text("nom;siren\nACME;443061841\n", encoding="utf-8")
            original = source.read_bytes()
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                with self.assertRaises(SystemExit) as ctx:
                    hce_cli.main(["france", str(source), "--out", str(source)])
            self.assertEqual(ctx.exception.code, 2)
            self.assertEqual(source.read_bytes(), original)

    def test_cli_rejects_report_and_csv_outputs_that_alias_each_other(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            source = Path(tmpdir) / "source.csv"
            output = Path(tmpdir) / "result.out"
            source.write_text("nom;siren\nACME;443061841\n", encoding="utf-8")
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                with self.assertRaises(SystemExit) as ctx:
                    hce_cli.main(
                        ["france", str(source), "--out", str(output), "--csv-out", str(output)]
                    )
            self.assertEqual(ctx.exception.code, 2)
            self.assertFalse(output.exists())

    def test_cli_rejects_hard_link_aliases(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            source = Path(tmpdir) / "source.csv"
            alias = Path(tmpdir) / "hardlink.csv"
            source.write_text("nom;siren\nACME;443061841\n", encoding="utf-8")
            alias.hardlink_to(source)
            original = source.read_bytes()
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                with self.assertRaises(SystemExit) as ctx:
                    hce_cli.main(["france", str(source), "--out", str(alias)])
            self.assertEqual(ctx.exception.code, 2)
            self.assertEqual(source.read_bytes(), original)

    def test_path_identity_error_falls_back_to_resolved_paths(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            source = Path(tmpdir) / "source.csv"
            output = Path(tmpdir) / "output.csv"
            source.write_text("source", encoding="utf-8")
            output.write_text("output", encoding="utf-8")
            with mock.patch.object(Path, "samefile", side_effect=OSError("permission denied")):
                hce_cli._ensure_distinct_paths(source, {"output": output})

    def test_cli_allows_distinct_outputs_and_dispatches_crm(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            source = Path(tmpdir) / "source.csv"
            report = Path(tmpdir) / "report.md"
            clean = Path(tmpdir) / "clean.csv"
            source.write_text("nom;siren\nACME;443061841\n", encoding="utf-8")
            original = source.read_bytes()
            with contextlib.redirect_stdout(io.StringIO()):
                hce_cli.main(["france", str(source), "--out", str(report), "--csv-out", str(clean)])
            self.assertTrue(report.exists())
            self.assertTrue(clean.exists())
            self.assertEqual(source.read_bytes(), original)

            targets = Path(tmpdir) / "targets.csv"
            targets.write_text(
                "id,corridor,nom_entite,contact_cible,role_cible,statut,hook_accroche\n"
                "1,FR_PDP,Alpha,a@alpha.fr,DAF,PROSPECT_QUALIFIE,hook a\n",
                encoding="utf-8",
            )
            drafts = Path(tmpdir) / "drafts"
            with contextlib.redirect_stdout(io.StringIO()):
                hce_cli.main(["crm", str(targets), "--output-dir", str(drafts)])
            self.assertTrue(list(drafts.glob("*.txt")))


class TestCLIQuarantine(unittest.TestCase):
    """CBAM, ZATCA and EAA were withdrawn from the customer path on 2026-09-28.

    The CBAM factor reintroduced a withdrawn 0.025 error (~71x on billets), the ZATCA
    "repair" hashes a made-up string and signs nothing, and the EAA declaration hardcodes
    place, date and findings. Keeping them one `argparse` choice away from a customer file
    is how a wrong number reaches an invoice.
    """

    def _run(self, argv: list[str]) -> int:
        err = io.StringIO()
        with mock.patch.object(sys, "argv", ["cli.py", *argv]), contextlib.redirect_stderr(err):
            with self.assertRaises(SystemExit) as ctx:
                hce_cli.main()
        return int(ctx.exception.code or 0)

    def test_withdrawn_subcommands_are_rejected(self):
        for argv in (["cbam", "--list"], ["zatca", "--ubl"], ["eaa", "x.html"]):
            self.assertEqual(self._run(argv), 2, argv)

    def test_customer_path_subcommands_still_exist(self):
        parser = hce_cli.build_parser()
        self.assertEqual(hce_cli.CUSTOMER_PATH_COMMANDS, ("france", "belgium", "crm"))
        self.assertEqual(parser.parse_args(["france", "f.csv"]).command, "france")
        self.assertEqual(parser.parse_args(["belgium", "f.csv"]).command, "belgium")
        self.assertEqual(parser.parse_args(["crm", "t.csv"]).command, "crm")


class TestCRMDispatcherHonesty(unittest.TestCase):
    def test_templates_do_not_promise_what_the_tools_cannot_do(self):
        for corridor in ("FR_PDP", "BE_PEPPOL"):
            body = generate_personalized_dispatch(
                {"id": "1", "corridor": corridor, "nom_entite": "X", "hook_accroche": "h"}
            )["corps"]
            self.assertNotIn("radiés", body)
            self.assertNotIn("ECDSA", body)
            self.assertNotIn("Participant IDs", body)

    def test_dispatch_skips_excluded_targets_and_writes_drafts(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_in = Path(tmpdir) / "targets.csv"
            csv_in.write_text(
                "id,corridor,nom_entite,contact_cible,role_cible,statut,hook_accroche\n"
                "1,FR_PDP,Alpha,a@alpha.fr,DAF,PROSPECT_QUALIFIE,hook a\n"
                "2,FR_PDP,Beta,b@beta.fr,DAF,EXCLU,hook b\n",
                encoding="utf-8",
            )
            out_dir = Path(tmpdir) / "drafts"
            files = dispatch_campaign(csv_in, out_dir)
            self.assertEqual(len(files), 1)
            self.assertIn("Alpha", files[0].name)
            self.assertIn("DRAFT", files[0].read_text(encoding="utf-8"))
            # The excluded target still gets a file — a declared withdrawal, not a silent gap.
            stub = out_dir / "02_FR_PDP_Beta.txt"
            self.assertTrue(stub.exists())
            self.assertIn("WITHDRAWN", stub.read_text(encoding="utf-8"))
            self.assertIn("EXCLU", stub.read_text(encoding="utf-8"))

    def test_a_batch_never_exceeds_one_configuration(self):
        """Atlas §0.3 (D-319): no broad marketing before knowing who buys. One run writes at
        most ``CONFIGURATION_OUTBOUND`` drafts; the rest get a declared WITHDRAWN file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_in = Path(tmpdir) / "targets.csv"
            rows = [
                f"{i},FR_PDP,Firm{i},f{i}@x.fr,DAF,PROSPECT_QUALIFIE,hook"
                for i in range(1, CONFIGURATION_OUTBOUND + 6)
            ]
            csv_in.write_text(
                "id,corridor,nom_entite,contact_cible,role_cible,statut,hook_accroche\n"
                + "\n".join(rows)
                + "\n",
                encoding="utf-8",
            )
            out_dir = Path(tmpdir) / "drafts"
            files = dispatch_campaign(csv_in, out_dir)
            self.assertEqual(len(files), CONFIGURATION_OUTBOUND)
            capped = [
                path
                for path in out_dir.glob("*.txt")
                if "plafond" in path.read_text(encoding="utf-8")
            ]
            self.assertEqual(len(capped), 5)
            self.assertTrue(all("WITHDRAWN" in p.read_text(encoding="utf-8") for p in capped))


class TestCBAMCalculator(unittest.TestCase):
    def test_cbam_steel_savings(self):
        res = calculate_cbam("72071114", tonnes=10000)
        self.assertEqual(res["code_hs"], "72071114")
        self.assertGreater(res["economie_totale"], 10000.0)
        self.assertGreater(res["penalite_evitee"], 900000.0)

    def test_cbam_new_products(self):
        self.assertIn("72083900", CBAM_CATALOG)
        self.assertIn("72131000", CBAM_CATALOG)
        res_coils = calculate_cbam("72083900", tonnes=20000)
        self.assertEqual(
            res_coils["installation"], "Tosyali Iron Steel Industry Algerie SPA (Bethioua)"
        )
        self.assertGreater(res_coils["economie_totale"], 15000.0)

    def test_cbam_xml_generation(self):
        res = calculate_cbam("31021000", tonnes=5000)
        xml = generate_cbam_xml(res, declarant_eori="FR98765432100011")
        self.assertIn("<CBAMDeclaration", xml)
        self.assertIn("<CNCode>31021000</CNCode>", xml)
        self.assertIn("<EORINumber>FR98765432100011</EORINumber>", xml)
        self.assertIn("Sorfert", xml)

    def test_cbam_batch_and_batch_xml(self):
        rows = [
            {"code_hs": "72071114", "tonnes": 5000},
            {"code_hs": "72083900", "tonnes": 10000},
            {"code_hs": "31021000", "tonnes": 3000},
        ]
        b_res = calculate_cbam_batch(rows, cert_price=80.0)
        self.assertEqual(b_res["nb_lignes"], 3)
        self.assertEqual(b_res["total_tonnes"], 18000.0)
        self.assertGreater(b_res["economie_globale_eur"], 10000.0)

        batch_xml = generate_cbam_batch_xml(b_res, declarant_eori="FR55566677700018")
        self.assertIn("<CBAMDeclaration", batch_xml)
        self.assertIn("<TotalGoodsItems>3</TotalGoodsItems>", batch_xml)
        self.assertIn("72083900", batch_xml)

        single = calculate_cbam("72071114", tonnes=1000)
        sens = generate_sensitivity_table(single)
        self.assertEqual(len(sens), 5)
        self.assertEqual(sens[0]["prix_co2"], 65.0)


class TestZATCAValidator(unittest.TestCase):
    def test_uuid_v4(self):
        self.assertTrue(validate_uuid_v4("c2b9a8f4-7e3d-4c8e-a9b1-5d2f6e8a7c3b"))
        self.assertFalse(validate_uuid_v4("not-a-uuid"))

    def test_vat_validation(self):
        ok, _ = validate_zatca_vat_number("300000000000003")
        self.assertTrue(ok)
        ok_bad, msg = validate_zatca_vat_number("100000000000002")
        self.assertFalse(ok_bad)
        self.assertIn("débuter", msg)

    def test_invoice_type(self):
        ok, label = validate_zatca_invoice_type("388", "0100000")
        self.assertTrue(ok)
        self.assertIn("Tax Invoice", label)

        ok_bad, _ = validate_zatca_invoice_type("999")
        self.assertFalse(ok_bad)

    def test_tlv_encode_decode(self):
        seller = "Tosyali Algérie"
        vat = "300000000000003"
        timestamp = "2026-09-24T12:00:00Z"
        total = "10000.00"
        vat_amount = "1500.00"

        b64 = encode_zatca_tlv(seller, vat, timestamp, total, vat_amount)
        self.assertTrue(len(b64) > 20)

        decoded = decode_zatca_tlv(b64)
        self.assertEqual(decoded[1], seller)
        self.assertEqual(decoded[2], vat)
        self.assertEqual(decoded[3], timestamp)
        self.assertEqual(decoded[4], total)
        self.assertEqual(decoded[5], vat_amount)

    def test_canonical_hash_and_chain_repair(self):
        ch = canonical_invoice_hash("<Invoice><ID>100</ID></Invoice>")
        self.assertEqual(len(ch), 44)

        # Broken chain: ICV jump from 1 to 3
        broken = [
            {
                "id": "INV-1",
                "icv": 1,
                "uuid": "c2b9a8f4-7e3d-4c8e-a9b1-5d2f6e8a7c3b",
                "pih": GENESIS_PIH,
                "invoice_hash": "47DEQpj8HBSa+/TImW+5JCeuQeRkm5NMpJWZG3hSuFU=",
            },
            {
                "id": "INV-2",
                "icv": 3,
                "uuid": "invalid",
                "pih": "WRONG_PIH",
                "invoice_hash": "broken",
            },
        ]
        audit_before = audit_zatca_batch(broken)
        self.assertFalse(audit_before["est_valide"])

        repaired, actions = repair_zatca_chain(broken)
        self.assertTrue(len(actions) > 0)
        audit_after = audit_zatca_batch(repaired)
        self.assertTrue(audit_after["est_valide"])
        self.assertEqual(repaired[1]["icv"], 2)

    def test_zatca_ubl_xml_generation(self):
        inv = {
            "id": "INV-TEST-01",
            "uuid": "c2b9a8f4-7e3d-4c8e-a9b1-5d2f6e8a7c3b",
            "icv": 1,
            "seller_vat": "300000000000003",
            "total": 12000.0,
            "vat": 1800.0,
        }
        xml = generate_sample_zatca_ubl_xml(inv)
        self.assertIn("<Invoice", xml)
        self.assertIn("<cbc:ID>INV-TEST-01</cbc:ID>", xml)
        self.assertIn("<cbc:CompanyID>300000000000003</cbc:CompanyID>", xml)
        self.assertIn("12000.00", xml)


class TestEAAScanner(unittest.TestCase):
    def test_html_audit_and_remediation(self):
        bad_html = (
            "<html><body><img src='logo.png'><input type='text'><button></button></body></html>"
        )
        res = audit_html_content(bad_html)
        self.assertFalse(res["est_conforme"])
        self.assertTrue(res["score_accessibilite"] < 100.0)
        self.assertTrue(len(res["guide_remediation"]) > 0)
        self.assertTrue(len(res["remediation_actions"]) > 0)
        self.assertIn('lang="fr"', res["code_html_assaini"])
        self.assertIn('alt=""', res["code_html_assaini"])

        remediated, fixes = remediate_html_content(bad_html)
        self.assertIn('lang="fr"', remediated)
        self.assertGreater(len(fixes), 0)

        decl = generate_declaration_accessibilite(
            "SuperRetail",
            "SuperRetail.fr",
            "https://superretail.fr",
            taux_conformite=res["score_accessibilite"],
        )
        self.assertIn("Déclaration d’accessibilité", decl)
        self.assertIn("SuperRetail", decl)


class TestCRMDispatcher(unittest.TestCase):
    def test_dispatch_generation(self):
        target = {
            "id": "1",
            "corridor": "FR_PDP",
            "nom_entite": "Pennylane",
            "role_cible": "Head of Partnerships",
            "contact_cible": "partenaires@pennylane.com",
            "hook_accroche": "Rejets Factur-X massifs constatés",
        }
        res = generate_personalized_dispatch(target)
        self.assertEqual(res["id"], "1")
        self.assertIn("Pennylane", res["objet"])
        self.assertIn("Houssam Benmerah", res["corps"])
        self.assertIn("h.benmerah@univ-eltarf.dz", res["corps"])


class TestContracts(unittest.TestCase):
    def test_audit_summary_and_arbitrage(self):
        summary = AuditSummary(corridor=CorridorType.FR_PDP, total_records=100, valid_records=85)
        rate = summary.calculate_rate()
        self.assertEqual(rate, 85.0)
        self.assertEqual(summary.invalid_records, 15)

        anomaly = AnomalyRecord(
            line_number=5,
            entity_identifier="443061841",
            error_code="SIRET_INVALID",
            message="Check Luhn failed",
            severity=AnomalySeverity.CRITICAL,
        )
        summary.anomalies.append(anomaly)
        d = summary.to_dict()
        self.assertEqual(d["anomalies_count"], 1)
        self.assertEqual(d["anomalies"][0]["severity"], "CRITIQUE")

        arb = FinancialArbitrage(
            corridor=CorridorType.EU_CBAM,
            entity_name="ArcelorMittal",
            baseline_cost_eur=150000.0,
            optimized_cost_eur=70000.0,
            net_savings_eur=80000.0,
        )
        self.assertEqual(arb.net_savings_eur, 80000.0)


if __name__ == "__main__":
    unittest.main()
