"""Shared CSV parsing and spreadsheet-formula safety utilities.

A leading apostrophe is a risk-reduction measure, not a universal guarantee across
spreadsheet applications or save/reopen cycles. Validate exports in the receiving
application before relying on them as an operational security boundary.
"""

from __future__ import annotations

import csv
import re
import unicodedata
from pathlib import Path

_FORMULA_PREFIXES = frozenset("=+-@")
_CONTROL_PREFIXES = frozenset("\t\r\n")
_SIGNED_NUMBER = re.compile(r"[+-]?(?:[0-9]+(?:[.,][0-9]*)?|[.,][0-9]+)(?:[eE][+-]?[0-9]+)?\Z")
_IGNORABLE_PREFIX_CATEGORIES = frozenset({"Cc", "Cf"})


def neutralize_spreadsheet_cell(value: object) -> object:
    """Prefix formula-like strings with an apostrophe, leaving other values intact.

    Detection uses NFKC normalization and ignores leading whitespace and control/format
    characters, while retaining the original text after the apostrophe. Numeric values
    encoded as negative or positive strings remain unchanged; other signed expressions
    are neutralized. Non-string values are passed through without conversion.
    """
    if not isinstance(value, str):
        return value

    normalized = unicodedata.normalize("NFKC", value)
    first_significant = ""
    first_index = 0
    for index, character in enumerate(normalized):
        if character in _CONTROL_PREFIXES:
            return "'" + value
        if character.isspace() or unicodedata.category(character) in _IGNORABLE_PREFIX_CATEGORIES:
            continue
        first_index = index
        first_significant = character
        break
    else:
        return value

    if first_significant not in _FORMULA_PREFIXES:
        return value

    candidate = normalized[first_index:].strip()
    if first_significant in "+-" and _SIGNED_NUMBER.fullmatch(candidate):
        return value
    return "'" + value


def read_csv_lines_multi_encoding(csv_path: Path) -> list[str]:
    """Decode common CSV encodings and drop comment records without splitting CSV fields.

    A physical line beginning with ``#`` inside a quoted multiline field is data, not a
    comment, and is retained. Comment records are ignored only at logical record starts.
    """
    raw_bytes = csv_path.read_bytes()
    text = ""
    for encoding in ("utf-8-sig", "utf-8", "cp1252", "iso-8859-1", "latin1"):
        try:
            text = raw_bytes.decode(encoding)
            break
        except UnicodeDecodeError:
            continue
    else:
        text = raw_bytes.decode("utf-8", errors="replace")

    physical_lines = text.splitlines(keepends=True)
    first_record_line = next(
        (line for line in physical_lines if line.strip() and not line.strip().startswith("#")),
        "",
    )
    delimiter = ";" if ";" in first_record_line else ","
    return _without_record_comments(physical_lines, delimiter)


def _without_record_comments(lines: list[str], delimiter: str) -> list[str]:
    """Preserve quoted multiline records while filtering comments at record boundaries."""
    output: list[str] = []
    in_quotes = False
    at_field_start = True
    at_record_start = True

    for line in lines:
        if at_record_start and not in_quotes and line.strip().startswith("#"):
            continue
        output.append(line)

        index = 0
        while index < len(line):
            character = line[index]
            if in_quotes:
                if character == '"':
                    if index + 1 < len(line) and line[index + 1] == '"':
                        index += 2
                        continue
                    in_quotes = False
                if character not in "\r\n":
                    at_record_start = False
                    at_field_start = False
            elif character == '"' and at_field_start:
                in_quotes = True
                at_record_start = False
                at_field_start = False
            elif character == delimiter:
                at_record_start = False
                at_field_start = True
            elif character in "\r\n":
                at_record_start = True
                at_field_start = True
            else:
                at_record_start = False
                at_field_start = False
            index += 1

    return output


def write_cleaned_csv(rows: list[dict], out_path: Path) -> Path:
    """Write annotated rows as UTF-8-BOM semicolon CSV with safe headers and cells."""
    if not rows:
        out_path.write_text("", encoding="utf-8")
        return out_path

    fields = list(dict.fromkeys(field for row in rows for field in row))
    with out_path.open(mode="w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.writer(handle, delimiter=";", lineterminator="\n")
        writer.writerow([neutralize_spreadsheet_cell(field) for field in fields])
        for row in rows:
            writer.writerow([neutralize_spreadsheet_cell(row.get(field, "")) for field in fields])
    return out_path
