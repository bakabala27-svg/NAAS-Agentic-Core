#!/usr/bin/env python3
"""بوابة حتمية لمسار أداة تنظيف مراجع الفوترة الفرنسية والبلجيكية.

هذه البوابة لا تدّعي صحة قانونية أو اتصالاً حياً بالمصادر الرسمية؛ تتحقق فقط من
حدود المسار المعلن، وقابلية استيراد وحداته، وعدم تسريب الوحدات المسحوبة إلى CLI.
"""

from __future__ import annotations

import ast
import compileall
import contextlib
import io
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ENGINE = ROOT / "tools" / "hard_currency_engine"
EXPECTED_COMMANDS = {"france", "belgium", "crm"}
FORBIDDEN_CLIENT_MODULES = {"cbam_calculator", "zatca_validator", "eaa_scanner"}
#: Atlas §9.3 and §5.3 (D-319): early on the owner talks to buyers himself — the engine may
#: look up public registries but never sends a message. Top-level module names.
FORBIDDEN_SEND_MODULES = {
    "smtplib",
    "sendgrid",
    "mailjet_rest",
    "yagmail",
    "mailgun",
    "postmarker",
    "brevo_python",
    "sib_api_v3_sdk",
}


def _send_imports(path: Path) -> list[str]:
    """Mail-sending modules a file imports; an unreadable file is reported, not passed."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (OSError, SyntaxError, UnicodeDecodeError) as exc:
        return [f"unreadable ({exc.__class__.__name__})"]
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            found.add(node.module.split(".")[0])
    return sorted(found & FORBIDDEN_SEND_MODULES)


def _failures() -> list[str]:
    failures: list[str] = []
    python_files = sorted(ENGINE.glob("*.py"))
    if not python_files:
        return ["HCE directory is missing or contains no Python modules"]

    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer), contextlib.redirect_stderr(buffer):
        if not compileall.compile_dir(str(ENGINE), quiet=1, legacy=True):
            failures.append("one or more HCE modules do not compile")

    for path in python_files:
        if sent := _send_imports(path):
            failures.append(
                f"{path.name} imports {', '.join(sent)} — the engine never sends a message "
                "(Atlas §9.3 · D-319)"
            )

    cli_path = ENGINE / "cli.py"
    tree = ast.parse(cli_path.read_text(encoding="utf-8"), filename=str(cli_path))
    assigned_commands = None
    imported_modules: set[str] = set()
    for node in ast.walk(tree):
        is_command_assignment = isinstance(node, (ast.Assign, ast.AnnAssign)) and (
            any(
                isinstance(target, ast.Name) and target.id == "CUSTOMER_PATH_COMMANDS"
                for target in getattr(node, "targets", [getattr(node, "target", None)])
            )
        )
        if is_command_assignment:
            value = node.value
            if isinstance(value, (ast.Tuple, ast.List)):
                assigned_commands = {
                    item.value for item in value.elts if isinstance(item, ast.Constant)
                }
        if isinstance(node, ast.ImportFrom) and node.module:
            imported_modules.add(node.module.rsplit(".", 1)[-1])

    if assigned_commands != EXPECTED_COMMANDS:
        failures.append(
            "CLI customer path drifted: "
            f"expected {sorted(EXPECTED_COMMANDS)}, got {sorted(assigned_commands or set())}"
        )
    leaked = sorted(FORBIDDEN_CLIENT_MODULES & imported_modules)
    if leaked:
        failures.append(f"retired modules exposed by customer CLI: {', '.join(leaked)}")

    required_symbols = {"build_parser", "cmd_france", "cmd_belgium", "cmd_crm"}
    symbols = {
        node.name for node in tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    missing = sorted(required_symbols - symbols)
    if missing:
        failures.append(f"CLI contract symbols missing: {', '.join(missing)}")

    return failures


def main() -> int:
    failures = _failures()
    if failures:
        for failure in failures:
            print(f"HCE QUALITY GATE: FAIL: {failure}")
        return 1
    print("HCE QUALITY GATE: PASS — bounded customer path, retired modules isolated, syntax valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
