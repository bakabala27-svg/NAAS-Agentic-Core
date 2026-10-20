"""Validate the mandatory cross-cutting code-acceptance packet."""

from __future__ import annotations

import fnmatch
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from shared.evidence.gate import report_problems

PACKET = ROOT / "docs/changes/CURRENT_CODE_ACCEPTANCE_PACKET.json"
MATRIX = ROOT / "docs/governance/SOURCE_ADOPTION_MATRIX.json"
EVIDENCE = ROOT / "docs/research/EVIDENCE_CATALOG.json"
CURRICULUM = ROOT / "docs/research/CURRICULUM_APPLICATION_MATRIX.json"
OFFERS = ROOT / "docs/commercial/OFFER_CATALOG.json"
GOVERNANCE_POLICY = ROOT / "docs/governance/ENGINEERING_GOVERNANCE_POLICY.json"
VALUE_CHAIN = ROOT / "docs/commercial/VALUE_CHAIN.json"
WORKFLOWS = ROOT / ".github/workflows"
FAILURES: list[str] = []
PACKET_REL = "docs/changes/CURRENT_CODE_ACCEPTANCE_PACKET.json"
#: A repository file a verification command cites (D-319): it must exist, and a cited gate
#: must be one CI runs again — a PASS nobody re-runs is self-declared (Atlas rules 8-9).
_CITED_FILE = re.compile(r"(?<![\w/.-])((?:scripts|tests)/[\w./-]+\.py)")


def fail(message: str) -> None:
    FAILURES.append(message)
    print(f"❌ {message}")


def passed(message: str) -> None:
    print(f"✅ {message}")


def load(path: Path, label: str) -> dict | None:
    if not path.is_file():
        fail(f"{label} missing: {path.relative_to(ROOT)}")
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"{label} invalid JSON: {exc}")
        return None
    if not isinstance(payload, dict):
        fail(f"{label} root must be an object")
        return None
    return payload


def run_git(args: list[str]) -> str:
    completed = subprocess.run(
        ["git", "-c", "core.quotepath=false", *args],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout


def current_changed_paths() -> list[str]:
    base = os.environ.get("CODE_ACCEPTANCE_BASE_SHA", "").strip()
    paths: set[str] = set()
    if base:
        paths.update(
            line.strip()
            for line in run_git(
                ["diff", "--name-only", "--diff-filter=ACMRTUXB", f"{base}...HEAD"]
            ).splitlines()
            if line.strip()
        )
    else:
        for args in (
            ["diff", "--name-only", "--diff-filter=ACMRTUXB"],
            ["diff", "--cached", "--name-only", "--diff-filter=ACMRTUXB"],
        ):
            paths.update(line.strip() for line in run_git(args).splitlines() if line.strip())
        for line in run_git(["status", "--porcelain=v1", "--untracked-files=all"]).splitlines():
            if line.startswith("?? "):
                paths.add(line[3:].strip())
    return sorted(path for path in paths if path)


def fingerprint(paths: list[str]) -> str:
    digest = hashlib.sha256()
    for relative in paths:
        if relative == PACKET_REL:
            continue
        path = ROOT / relative
        files = (
            [path]
            if path.is_file()
            else sorted(child for child in path.rglob("*") if child.is_file())
            if path.is_dir()
            else []
        )
        for file_path in files:
            digest.update(str(file_path.relative_to(ROOT)).encode("utf-8"))
            digest.update(b"\0")
            digest.update(file_path.read_bytes())
            digest.update(b"\0")
    return digest.hexdigest()


def current_deleted_paths() -> list[str]:
    """Return actual deletions; a packet must not hide a removed test or control."""
    base = os.environ.get("CODE_ACCEPTANCE_BASE_SHA", "").strip()
    paths: set[str] = set()
    if base:
        paths.update(
            line.strip()
            for line in run_git(
                ["diff", "--name-only", "--diff-filter=D", f"{base}...HEAD"]
            ).splitlines()
            if line.strip()
        )
    else:
        for args in (
            ["diff", "--name-only", "--diff-filter=D"],
            ["diff", "--cached", "--name-only", "--diff-filter=D"],
        ):
            paths.update(line.strip() for line in run_git(args).splitlines() if line.strip())
    return sorted(paths)


def current_added_paths() -> list[str]:
    """Paths the change adds; D-321 maintenance may modify product code, never add to it."""
    base = os.environ.get("CODE_ACCEPTANCE_BASE_SHA", "").strip()
    paths: set[str] = set()
    if base:
        paths.update(
            line.strip()
            for line in run_git(
                ["diff", "--name-only", "--diff-filter=A", f"{base}...HEAD"]
            ).splitlines()
            if line.strip()
        )
    else:
        for args in (
            ["diff", "--name-only", "--diff-filter=A"],
            ["diff", "--cached", "--name-only", "--diff-filter=A"],
        ):
            paths.update(line.strip() for line in run_git(args).splitlines() if line.strip())
        for line in run_git(["status", "--porcelain=v1", "--untracked-files=all"]).splitlines():
            if line.startswith("?? "):
                paths.add(line[3:].strip())
    return sorted(paths)


def _is_product_code(path: str, rules: dict) -> bool:
    product = [str(prefix) for prefix in rules.get("product_code_prefixes", [])]
    excluded = [str(prefix) for prefix in rules.get("non_product_prefixes", [])]
    return any(path.startswith(prefix) for prefix in product) and not any(
        path.startswith(prefix) for prefix in excluded
    )


def validate_demand_first(
    packet: dict,
    actual_paths: list[str],
    added_paths: list[str],
    policy: dict,
    derived_paths: list[dict],
) -> list[str]:
    """D-321 «الألم أولاً»: product code is accepted for a value-chain path whose ledger shows
    three replying entities and an evidenced payer, or as maintenance that adds no file."""
    rules = policy.get("demand_first")
    if not isinstance(rules, dict) or not rules.get("product_code_prefixes"):
        return ["policy has no demand_first.product_code_prefixes (D-321)"]
    product = [path for path in actual_paths if _is_product_code(path, rules)]
    if not product:
        return []
    trace = packet.get("commercial_trace")
    trace = trace if isinstance(trace, dict) else {}
    change_class = trace.get("change_class")
    if change_class == "MAINTENANCE_KEEP_CI_HONEST":
        failures: list[str] = []
        if not str(trace.get("maintenance_reason_ar") or "").strip():
            failures.append("D-321: maintenance of product code needs maintenance_reason_ar")
        added = sorted(path for path in added_paths if _is_product_code(path, rules))
        if added:
            failures.append(f"D-321: maintenance may not add product files: {added}")
        return failures
    if change_class != "DEMAND_LICENSED":
        return [
            f"D-321: {len(product)} product-code path(s) change (e.g. {product[:3]}) without "
            "commercial_trace.change_class DEMAND_LICENSED or MAINTENANCE_KEEP_CI_HONEST"
        ]
    ids = trace.get("value_chain_path_ids")
    named = [str(item) for item in ids] if isinstance(ids, list) else []
    by_id = {str(item.get("id")): item for item in derived_paths if isinstance(item, dict)}
    if not any(by_id.get(item, {}).get("code_licensed") is True for item in named):
        return [
            f"D-321: none of value_chain_path_ids {named} is code_licensed — three replying "
            "entities in the ledger and an evidenced payer come before product code"
        ]
    return []


def _derived_value_chain_paths() -> list[dict]:
    payload = load(VALUE_CHAIN, "value chain")
    derived = payload.get("derived") if isinstance(payload, dict) else None
    paths = derived.get("paths") if isinstance(derived, dict) else None
    return [item for item in paths if isinstance(item, dict)] if isinstance(paths, list) else []


def load_governance_policy() -> dict | None:
    return load(GOVERNANCE_POLICY, "engineering governance policy")


def validate_pre_modification(packet: dict, policy: dict) -> list[str]:
    """Validate the pre-change evidence required by the engineering constitution."""
    failures: list[str] = []
    contract = policy.get("pre_modification_packet")
    if not isinstance(contract, dict):
        return ["engineering governance policy lacks pre_modification_packet"]
    required = contract.get("required_fields")
    if not isinstance(required, list) or not required:
        return ["engineering governance policy lacks pre-modification required fields"]
    pre_modification = packet.get("pre_modification")
    if not isinstance(pre_modification, dict):
        return ["packet must contain a pre_modification evidence object"]
    for field in required:
        value = pre_modification.get(str(field))
        if value is None or value in ("", [], {}):
            failures.append(f"pre_modification missing `{field}`")

    frontier = pre_modification.get("foundational_frontier")
    allowed_frontier = set(contract.get("foundational_frontier_statuses", []))
    if not isinstance(frontier, dict):
        failures.append("pre_modification.foundational_frontier must be an object")
    elif frontier.get("status") not in allowed_frontier:
        failures.append("pre_modification.foundational_frontier has an invalid status")
    elif frontier.get("status") == "BLOCKED_PENDING_FOUNDATIONAL_REPAIR":
        failures.append("change is blocked pending foundational repair; it cannot be accepted")

    statuses = pre_modification.get("claim_statuses")
    allowed_statuses = set(policy.get("required_evidence_statuses", []))
    if not isinstance(statuses, dict) or not statuses:
        failures.append("pre_modification.claim_statuses must be a non-empty object")
    else:
        invalid = sorted(key for key, status in statuses.items() if status not in allowed_statuses)
        if invalid:
            failures.append(f"claim_statuses uses unsupported evidence statuses: {invalid}")
        forbidden_external = set(
            policy.get("platform_controls", {}).get("forbidden_local_claim_statuses", [])
        )
        branch_protection_status = statuses.get("branch_protection_live_state")
        if branch_protection_status in forbidden_external:
            failures.append(
                "pre_modification falsely claims local verification of external branch protection; "
                "record UNKNOWN until an authorized external audit is attached"
            )
    return failures


def validate_evidence_report(
    packet: dict, actual_paths: list[str], protected_patterns: list[str]
) -> list[str]:
    """The thesis report (D-318 p.18), with its level and decision computed by ``gate.py``.

    Only the evidence is declared: ``touched_files`` must equal what Git reports and
    ``protected_paths_changed`` what the policy's protected paths match (D-319).
    """
    report = packet.get("evidence_report")
    if not isinstance(report, dict):
        return ["packet must contain an evidence_report (the D-318 template, computed by gate.py)"]
    failures = [f"evidence_report: {problem}" for problem in report_problems(report)]
    scope = report.get("scope")
    touched = scope.get("touched_files") if isinstance(scope, dict) else None
    if not isinstance(touched, list) or sorted(map(str, touched)) != sorted(actual_paths):
        failures.append(
            "evidence_report.scope.touched_files must equal the paths Git reports "
            f"(excluding the packet): expected {len(actual_paths)}, "
            f"got {len(touched) if isinstance(touched, list) else touched!r}"
        )
    expected_protected = sorted(
        path
        for path in actual_paths
        if any(fnmatch.fnmatchcase(path, pattern) for pattern in protected_patterns)
    )
    declared = report.get("protected_paths_changed")
    if not isinstance(declared, list) or sorted(map(str, declared)) != expected_protected:
        failures.append(
            "evidence_report.protected_paths_changed must equal the changed paths the policy "
            f"protects: expected {expected_protected}, got {declared!r}"
        )
    return failures


def _active_lines(ci_text: str) -> list[str]:
    return [line for line in ci_text.splitlines() if not line.lstrip().startswith("#")]


def validate_verification_claims(packet: dict, ci_text: str) -> list[str]:
    """No self-declared PASS (Atlas master prompt, rules 8-9 · D-319).

    A file a verification command cites must exist, and a fitness gate claimed in it must
    run on an uncommented line of a workflow, so CI checks the claim again.
    """
    verification = packet.get("verification")
    commands = verification.get("commands", []) if isinstance(verification, dict) else []
    active = _active_lines(ci_text)
    failures: list[str] = []
    for command in commands if isinstance(commands, list) else []:
        for rel in _CITED_FILE.findall(str(command)):
            if not (ROOT / rel).is_file():
                failures.append(f"verification cites a file that does not exist: {rel}")
            elif rel.startswith("scripts/fitness/") and not any(rel in line for line in active):
                failures.append(
                    f"verification claims {rel} but no workflow runs it — a PASS CI never "
                    "re-runs is self-declared"
                )
    return failures


def validate_runtime_evidence(packet: dict) -> list[str]:
    """Atlas §8.3 (D-319): runtime evidence is a file that exists, not a name."""
    production = packet.get("production")
    paths = production.get("runtime_evidence_paths", []) if isinstance(production, dict) else []
    return [
        f"production.runtime_evidence_paths names a missing path: {path}"
        for path in (paths if isinstance(paths, list) else [])
        if not (ROOT / str(path)).exists()
    ]


def _workflow_text() -> str:
    return "\n".join(path.read_text(encoding="utf-8") for path in sorted(WORKFLOWS.glob("*.y*ml")))


def main() -> int:
    packet = load(PACKET, "code acceptance packet")
    matrix = load(MATRIX, "source adoption matrix")
    evidence = load(EVIDENCE, "evidence catalog")
    curriculum = load(CURRICULUM, "curriculum application matrix")
    offers = load(OFFERS, "offer catalog")
    governance_policy = load_governance_policy()
    if any(
        payload is None
        for payload in (packet, matrix, evidence, curriculum, offers, governance_policy)
    ):
        return 1
    assert (
        packet is not None
        and matrix is not None
        and evidence is not None
        and curriculum is not None
        and offers is not None
        and governance_policy is not None
    )

    if packet.get("status") != "READY_FOR_GATE":
        fail("packet status must be READY_FOR_GATE")
    for violation in validate_pre_modification(packet, governance_policy):
        fail(violation)
    changed_paths = packet.get("changed_paths", [])
    snapshot = packet.get("git_change_snapshot", {})
    actual_paths = current_changed_paths()
    actual_paths_excluding_packet = [path for path in actual_paths if path != PACKET_REL]
    for violation in validate_evidence_report(
        packet,
        actual_paths_excluding_packet,
        [str(pattern) for pattern in governance_policy.get("protected_paths", [])],
    ):
        fail(violation)
    snapshot_paths = (
        snapshot.get("changed_paths_excluding_packet", []) if isinstance(snapshot, dict) else []
    )
    if not isinstance(snapshot, dict) or not snapshot.get("content_sha256_excluding_packet"):
        fail("packet must contain a non-circular git_change_snapshot")
    elif sorted(str(path) for path in snapshot_paths) != actual_paths_excluding_packet:
        fail(
            f"packet changed-path snapshot is stale: recorded={len(snapshot_paths)}, actual={len(actual_paths_excluding_packet)}"
        )
    elif snapshot.get("content_sha256_excluding_packet") != fingerprint(
        actual_paths_excluding_packet
    ):
        fail("packet content fingerprint is stale; refresh the packet before accepting code")
    if not isinstance(changed_paths, list) or not changed_paths:
        fail("changed_paths must be non-empty")
    else:
        for path_value in changed_paths:
            path = ROOT / str(path_value)
            if not path.exists():
                fail(f"changed path does not exist: {path_value}")

    matrix_rows = matrix.get("sources", [])
    matrix_by_id = {
        str(row.get("source_id")): row
        for row in matrix_rows
        if isinstance(row, dict) and row.get("source_id") not in (None, "unclassified")
    }
    standards = packet.get("standards", [])
    if not isinstance(standards, list) or not standards:
        fail("packet must name standards from SOURCE_ADOPTION_MATRIX")
    else:
        for identifier in standards:
            row = matrix_by_id.get(str(identifier))
            if row is None:
                fail(f"packet names unknown standard source: {identifier}")
                continue
            if row.get("status") in {"PENDING_CLASSIFICATION", "EXTERNAL_ABSENT"}:
                fail(
                    f"packet cannot use non-active source as authority: {identifier} ({row.get('status')})"
                )
            if (
                row.get("runtime_allowed") is not False
                and row.get("status") == "MANDATORY_REFERENCE"
            ):
                fail(f"mandatory reference must remain non-runtime: {identifier}")

    evidence_rows = evidence.get("evidence", [])
    evidence_ids = {str(row.get("id")) for row in evidence_rows if isinstance(row, dict)}
    packet_evidence = packet.get("evidence", [])
    if not isinstance(packet_evidence, list) or not packet_evidence:
        fail("packet must name at least one evidence source")
    else:
        unknown = sorted({str(identifier) for identifier in packet_evidence} - evidence_ids)
        if unknown:
            fail(f"packet names unknown evidence ids: {unknown}")

    curriculum_packet = packet.get("curriculum", {})
    curriculum_rows = curriculum.get("courses", [])
    catalog_course_ids = {
        str(row.get("course_id")) for row in curriculum_rows if isinstance(row, dict)
    }
    if curriculum_packet.get("all_catalog_courses_loaded") is not True:
        fail("curriculum packet must assert all catalog courses were loaded")
    if curriculum_packet.get("catalog_course_count") != len(catalog_course_ids):
        fail("curriculum packet course count does not match application matrix")
    considered_ids = {
        str(identifier) for identifier in curriculum_packet.get("considered_course_ids", [])
    }
    if considered_ids != catalog_course_ids:
        fail(
            f"curriculum coverage mismatch: considered-only={sorted(considered_ids - catalog_course_ids)}, catalog-only={sorted(catalog_course_ids - considered_ids)}"
        )
    if curriculum_packet.get("applicability_result") != "ALL_CATALOG_COURSES_CONSIDERED":
        fail("curriculum applicability result must prove all catalog courses were considered")
    for baseline_id in curriculum_packet.get("baseline_evidence_ids", []):
        if str(baseline_id) not in evidence_ids:
            fail(f"curriculum baseline evidence is not in EVIDENCE_CATALOG: {baseline_id}")
    for field in ("catalog_path", "application_matrix_path", "unapplied_course_policy_ar", "owner"):
        if not curriculum_packet.get(field):
            fail(f"curriculum packet missing `{field}`")
    for path in (
        curriculum_packet.get("catalog_path"),
        curriculum_packet.get("application_matrix_path"),
    ):
        if path and not (ROOT / str(path)).exists():
            fail(f"curriculum packet path does not exist: {path}")

    applications = packet.get("local_application", [])
    application_ids = {str(row.get("standard")) for row in applications if isinstance(row, dict)}
    if {str(identifier) for identifier in standards} != application_ids:
        fail("every named standard must have exactly one local_application trace")
    for index, row in enumerate(applications, start=1):
        if not isinstance(row, dict):
            fail(f"local_application[{index}] must be an object")
            continue
        for field in ("standard", "paths", "gate", "application_ar"):
            if not row.get(field):
                fail(f"local_application[{index}] missing `{field}`")
        for path in row.get("paths", []):
            if not (ROOT / str(path)).exists():
                fail(f"local_application[{index}] path does not exist: {path}")

    production = packet.get("production", {})
    for field in (
        "owner",
        "status",
        "interfaces",
        "failure_behavior_ar",
        "observability_ar",
        "security_boundary_ar",
        "rollback_ar",
    ):
        if not production.get(field):
            fail(f"production section missing `{field}`")
    if not production.get("runtime_evidence_paths"):
        fail("production section must name runtime/evidence paths")
    for violation in validate_runtime_evidence(packet):
        fail(violation)

    catalog_offer_ids = {
        str(row.get("id")) for row in offers.get("offers", []) if isinstance(row, dict)
    }
    commercial = packet.get("commercial_trace", {})
    offer_ids = commercial.get("offer_ids", [])
    if not isinstance(offer_ids, list) or not offer_ids:
        fail("commercial trace must name one or more catalog offer ids")
    else:
        unknown_offers = sorted({str(identifier) for identifier in offer_ids} - catalog_offer_ids)
        if unknown_offers:
            fail(f"commercial trace names unknown offers: {unknown_offers}")
    for field in (
        "customer_problem_ar",
        "value_hypothesis_ar",
        "foreign_currency_path_ar",
        "foundation_exception_ar",
    ):
        if not commercial.get(field):
            fail(f"commercial trace missing `{field}`")

    deletions = packet.get("deletions", {})
    actual_deletions = current_deleted_paths()
    if actual_deletions:
        fail(
            "code acceptance rejects actual deleted paths; a packet cannot hide deletion: "
            f"{actual_deletions}"
        )
    if deletions.get("count") != 0 or deletions.get("paths") != []:
        fail("code acceptance requires zero declared deletions")
    verification = packet.get("verification", {})
    if verification.get("result") != "PASS" or not verification.get("commands"):
        fail("verification must include commands and PASS result")
    for violation in validate_verification_claims(packet, _workflow_text()):
        fail(violation)
    for violation in validate_demand_first(
        packet,
        actual_paths_excluding_packet,
        current_added_paths(),
        governance_policy,
        _derived_value_chain_paths(),
    ):
        fail(violation)
    if packet.get("decision") != "D-277":
        fail("packet must be governed by D-277")

    if FAILURES:
        print(f"\n❌ Code acceptance gate failed: {len(FAILURES)} violation(s)")
        return 1
    passed(
        "Code acceptance packet is complete: standards, full curriculum consideration, evidence, local application, production proof, commercial trace, and zero deletions are present."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
