#!/usr/bin/env python3
"""Game text tag and layout validator.

Ensures 100% preservation of control tags, verifies text box layout budgets,
detects malformed tags, and enforces Russian localization typography standards.
"""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import re
import sys
from typing import Any

# Format specifiers matching printf formats:
# Positional (%1$s), flags (%-10s, %+5d, %04d), width, precision (%.2f), length modifiers (%lld, %zu),
# conversion specifiers (d, i, u, o, x, X, f, F, e, E, g, G, a, A, c, s, p, n), and escaped percent (%%)
FORMAT_SPECIFIER = r"%%|%(?:\d+\$)?[+\- 0#]*\d*(?:\.\d+)?[lhLzjt]*[diuoxXfFeEgGaAcspn]"

TAG_REGEX = re.compile(
    rf"(\{{[^{{}}]*\}}|\[[^\[\]]*\]|{FORMAT_SPECIFIER}|\\n|\\t|\n|\t)"
)


def extract_tags(text: str) -> list[str]:
    """Extract all control tags, format specifiers, and escape sequences from text."""
    return TAG_REGEX.findall(text)


def check_bracket_integrity(text: str) -> list[str]:
    """Check for malformed or unclosed curly and square brackets."""
    errors: list[str] = []

    # Check curly braces {}
    in_brace = False
    brace_start = -1
    for i, ch in enumerate(text):
        if ch == "{":
            if in_brace:
                snippet = text[brace_start : min(len(text), i + 10)]
                errors.append(f"Malformed tag: unclosed '{{' found near '{snippet}'")
            in_brace = True
            brace_start = i
        elif ch == "}":
            if not in_brace:
                errors.append(f"Malformed tag: unexpected '}}' at character index {i}")
            in_brace = False
    if in_brace:
        snippet = text[brace_start : min(len(text), brace_start + 15)]
        errors.append(f"Malformed tag: unclosed '{{' found in '{snippet}'")

    # Check square brackets []
    in_bracket = False
    bracket_start = -1
    for i, ch in enumerate(text):
        if ch == "[":
            if in_bracket:
                snippet = text[bracket_start : min(len(text), i + 10)]
                errors.append(f"Malformed tag: unclosed '[' found near '{snippet}'")
            in_bracket = True
            bracket_start = i
        elif ch == "]":
            if not in_bracket:
                errors.append(f"Malformed tag: unexpected ']' at character index {i}")
            in_bracket = False
    if in_bracket:
        snippet = text[bracket_start : min(len(text), bracket_start + 15)]
        errors.append(f"Malformed tag: unclosed '[' found in '{snippet}'")

    return errors


def check_russian_typography(text: str) -> list[str]:
    """Check Russian text typography rules.

    - Warns on straight ASCII double quotes '"', expecting guillemets « ».
    - Warns on hyphen '-' used as dialogue dash or sentence dash, expecting em-dash '—'.
    - Ignores hyphens inside compound words (e.g. кто-то, из-за, по-русски).
    """
    errors: list[str] = []

    # Normalize literal escaped newlines and tabs
    text_normalized = text.replace("\\n", "\n").replace("\\t", "\t")

    # Strip control tags first so quotes/dashes inside tags are not flagged
    text_clean = re.sub(r"\{[^{}]*\}|\[[^\[\]]*\]", "", text_normalized)

    # 1. Straight ASCII quotes check
    if '"' in text_clean:
        errors.append(
            "Russian typography warning: straight ASCII quotes '\"' found, use guillemets « » instead"
        )

    # 2. Dialogue dash at start of line / text
    if re.search(r"(^|\n)\s*-\s+", text_clean):
        errors.append(
            "Russian typography warning: hyphen '-' used as dialogue dash, use em-dash '—' instead"
        )
    # 3. Sentence dash between words (space hyphen space)
    elif re.search(r"\s+-\s+", text_clean):
        errors.append(
            "Russian typography warning: hyphen '-' used as dash, use em-dash '—' instead"
        )

    return errors


DEFAULT_VARIABLE_TOKENS: set[str] = {
    "{HERO_NAME}", "{PLAYER_NAME}", "{TARGET}", "{VARIABLE}",
    "{ITEM_NAME}", "{LOCATION}", "{VALUE}", "{NUMBER}",
    "{HERO}", "{PLAYER}", "{VAR_1}", "{VAR_2}", "{NAME 1}", "{NAME 2}",
}


def strip_non_visual_tags(
    text: str,
    var_token_len: int = 8,
    custom_var_tokens: set[str] | None = None,
) -> str:
    """Strip non-visual formatting tags and reserve budget for variable tokens.

    Tokens matching variable tokens are replaced with `var_token_len` characters
    (e.g. 'X' * var_token_len), while all non-visual control codes/opcodes
    ({COLOR:1}, {WAIT:10}, etc.) are stripped to ''.
    """
    var_tokens = set(DEFAULT_VARIABLE_TOKENS)
    if custom_var_tokens:
        var_tokens.update(custom_var_tokens)

    replacement = "X" * max(0, var_token_len)

    escaped_var_tokens = sorted(
        (re.escape(tok) for tok in var_tokens if tok),
        key=len,
        reverse=True,
    )
    if escaped_var_tokens:
        var_pattern = "|".join(escaped_var_tokens)
        pattern = rf"({var_pattern})|(\{{[^{{}}]*\}}|\[[^\[\]]*\])"
    else:
        pattern = r"\{[^{}]*\}|\[[^\[\]]*\]"

    def replace_match(match: re.Match[str]) -> str:
        if match.group(1):
            return replacement
        return ""

    return re.sub(pattern, replace_match, text)


def check_layout_budget(
    text: str,
    max_line_len: int = 40,
    max_lines: int = 4,
    var_token_len: int = 8,
    custom_var_tokens: set[str] | None = None,
) -> list[str]:
    """Check line length limits and line count budgets per dialogue page."""
    errors: list[str] = []

    # Pages are separated by {PAGE} opcode if present
    pages = text.replace("\\n", "\n").split("{PAGE}")
    for page_idx, page in enumerate(pages, 1):
        # Normalize {LINE} opcode to newline
        normalized_page = page.replace("{LINE}", "\n")
        # Strip trailing newlines to avoid false-positive empty line count increments
        lines = normalized_page.rstrip("\r\n").splitlines()
        if not lines and page:
            lines = [""]

        # Check line count budget per page
        if len(lines) > max_lines:
            page_info = f" in page {page_idx}" if len(pages) > 1 else ""
            errors.append(
                f"Line count exceeds maximum budget{page_info} ({len(lines)} > {max_lines})"
            )

        # Check character length per line
        for line_idx, line in enumerate(lines, 1):
            # Strip non-visual formatting tags and reserve variable tokens
            visible_line = strip_non_visual_tags(
                line, var_token_len=var_token_len, custom_var_tokens=custom_var_tokens
            )
            if len(visible_line) > max_line_len:
                line_info = f"Page {page_idx} Line {line_idx}" if len(pages) > 1 else f"Line {line_idx}"
                errors.append(
                    f"{line_info} exceeds max length ({len(visible_line)} > {max_line_len})"
                )

    return errors


def validate_line(
    src: str,
    dst: str,
    max_line_len: int = 40,
    max_lines: int = 4,
    var_token_len: int = 8,
    custom_var_tokens: set[str] | None = None,
) -> list[str]:
    """Validate a single source and translated line pair.

    Checks:
    - Malformed or unclosed bracket tags
    - Tag parity (dropped tags, extra tags, casing drift, parameter corruption)
    - Line count budget and max line length limits
    - Russian typography standards
    """
    errors: list[str] = []

    # 1. Bracket integrity
    bracket_errors = check_bracket_integrity(dst)
    errors.extend(bracket_errors)

    # 2. Tag parity
    src_tags = extract_tags(src)
    dst_tags = extract_tags(dst)

    src_counter = Counter(src_tags)
    dst_counter = Counter(dst_tags)

    if src_counter != dst_counter:
        missing_tags: list[str] = []
        extra_tags: list[str] = []

        # Find missing tags (in src more than dst)
        for tag, count in src_counter.items():
            diff = count - dst_counter.get(tag, 0)
            if diff > 0:
                missing_tags.extend([tag] * diff)

        # Find extra tags (in dst more than src)
        for tag, count in dst_counter.items():
            diff = count - src_counter.get(tag, 0)
            if diff > 0:
                extra_tags.extend([tag] * diff)

        # Detect casing mismatches (e.g. {COLOR 1} vs {color 1})
        for missing_tag in list(missing_tags):
            casing_match = next(
                (t for t in extra_tags if t.lower() == missing_tag.lower() and t != missing_tag),
                None,
            )
            if casing_match:
                errors.append(
                    f"Tag casing mismatch: expected '{missing_tag}', found '{casing_match}'"
                )
                extra_tags.remove(casing_match)
                missing_tags.remove(missing_tag)

        # Report remaining missing tags
        for tag in missing_tags:
            if tag in dst_counter:
                errors.append(
                    f"Tag count mismatch for '{tag}': expected {src_counter[tag]}, found {dst_counter[tag]}"
                )
            else:
                errors.append(f"Missing tag in target: '{tag}'")

        # Report remaining extra/unexpected tags
        for tag in extra_tags:
            if tag not in src_counter:
                errors.append(f"Unexpected extra tag in target: '{tag}'")

    # 3. Layout budget
    layout_errors = check_layout_budget(
        dst,
        max_line_len=max_line_len,
        max_lines=max_lines,
        var_token_len=var_token_len,
        custom_var_tokens=custom_var_tokens,
    )
    errors.extend(layout_errors)

    # 4. Russian typography
    typography_errors = check_russian_typography(dst)
    errors.extend(typography_errors)

    return errors


def parse_po_file(content: str) -> list[dict[str, Any]]:
    """Parse PO content into list of entry dictionaries supporting plural forms."""
    entries: list[dict[str, Any]] = []
    lines = content.splitlines()

    current_entry: dict[str, Any] | None = None
    current_field: str | None = None
    plural_idx: int | None = None

    def unescape(s: str) -> str:
        s = s.strip()
        if s.startswith('"') and s.endswith('"'):
            s = s[1:-1]
        return s.replace('\\"', '"').replace('\\n', '\n').replace('\\t', '\t')

    def flush_entry():
        nonlocal current_entry
        if current_entry and current_entry.get("msgid"):
            entries.append(current_entry)
        current_entry = None

    for raw_line in lines:
        line = raw_line.strip()
        if not line or line.startswith("#"):
            if current_entry is not None and ("msgstr" in current_entry or current_entry.get("msgstr_plural")):
                flush_entry()
            continue

        if line.startswith("msgid "):
            if current_entry is not None and ("msgstr" in current_entry or current_entry.get("msgstr_plural")):
                flush_entry()
            current_entry = {"msgid": unescape(line[6:]), "msgstr_plural": {}}
            current_field = "msgid"
            plural_idx = None
        elif line.startswith("msgid_plural "):
            if current_entry is not None:
                current_entry["msgid_plural"] = unescape(line[13:])
                current_field = "msgid_plural"
        elif line.startswith("msgstr "):
            if current_entry is not None:
                current_entry["msgstr"] = unescape(line[7:])
                current_field = "msgstr"
                plural_idx = None
        elif line.startswith("msgstr["):
            m = re.match(r"msgstr\[(\d+)\]\s*(.*)", line)
            if m and current_entry is not None:
                idx = int(m.group(1))
                val = unescape(m.group(2))
                current_entry["msgstr_plural"][idx] = val
                current_field = "msgstr_plural"
                plural_idx = idx
        elif line.startswith('"') and line.endswith('"'):
            val = unescape(line)
            if current_entry is not None and current_field:
                if current_field == "msgid":
                    current_entry["msgid"] += val
                elif current_field == "msgid_plural":
                    current_entry.setdefault("msgid_plural", "")
                    current_entry["msgid_plural"] += val
                elif current_field == "msgstr":
                    current_entry.setdefault("msgstr", "")
                    current_entry["msgstr"] += val
                elif current_field == "msgstr_plural" and plural_idx is not None:
                    current_entry["msgstr_plural"][plural_idx] += val

    flush_entry()
    return entries


def validate_file(
    src_path: str,
    dst_path: str,
    max_line_len: int = 40,
    max_lines: int = 4,
    var_token_len: int = 8,
    custom_var_tokens: set[str] | None = None,
) -> dict[str, Any]:
    """Validate translation integrity between two files (JSON, PO, or text)."""
    src_p = Path(src_path)
    dst_p = Path(dst_path)

    errors_dict: dict[str, list[str]] = {}
    total_entries = 0

    if not src_p.exists():
        return {
            "valid": False,
            "total_entries": 0,
            "passed_entries": 0,
            "failed_entries": 1,
            "error_count": 1,
            "errors": {"__file__": [f"Source file not found: {src_path}"]},
        }

    if not dst_p.exists():
        return {
            "valid": False,
            "total_entries": 0,
            "passed_entries": 0,
            "failed_entries": 1,
            "error_count": 1,
            "errors": {"__file__": [f"Target file not found: {dst_path}"]},
        }

    # 1. PO file format
    if src_p.suffix == ".po" or dst_p.suffix == ".po":
        is_distinct = (
            src_p.suffix == ".po"
            and dst_p.suffix == ".po"
            and src_p.resolve() != dst_p.resolve()
        )

        if is_distinct:
            src_entries = parse_po_file(src_p.read_text(encoding="utf-8"))
            dst_entries = parse_po_file(dst_p.read_text(encoding="utf-8"))

            src_dict = {e["msgid"]: e for e in src_entries}
            dst_dict = {e["msgid"]: e for e in dst_entries}
            total_entries = len(src_dict)

            for msgid, s_entry in src_dict.items():
                if msgid not in dst_dict:
                    errors_dict[msgid] = [f"Missing entry in target PO for msgid: '{msgid}'"]
                    continue

                d_entry = dst_dict[msgid]
                # Check singular msgstr
                if "msgstr" in d_entry:
                    line_errs = validate_line(
                        msgid,
                        d_entry["msgstr"],
                        max_line_len=max_line_len,
                        max_lines=max_lines,
                        var_token_len=var_token_len,
                        custom_var_tokens=custom_var_tokens,
                    )
                    if line_errs:
                        errors_dict[msgid] = line_errs

                # Check plural msgstr[N] forms
                if d_entry.get("msgstr_plural"):
                    for p_idx, p_val in sorted(d_entry["msgstr_plural"].items()):
                        key = f"{msgid}[{p_idx}]"
                        src_text = s_entry.get("msgid_plural") or msgid
                        line_errs = validate_line(
                            src_text,
                            p_val,
                            max_line_len=max_line_len,
                            max_lines=max_lines,
                            var_token_len=var_token_len,
                            custom_var_tokens=custom_var_tokens,
                        )
                        if line_errs:
                            errors_dict[key] = line_errs

            for msgid in dst_dict:
                if msgid not in src_dict:
                    errors_dict[msgid] = [f"Unexpected extra entry in target PO for msgid: '{msgid}'"]

        else:
            # Single PO file or one of the files is .po
            target_path = dst_p if dst_p.suffix == ".po" else src_p
            po_entries = parse_po_file(target_path.read_text(encoding="utf-8"))
            total_entries = len(po_entries)
            for idx, entry in enumerate(po_entries, 1):
                msgid = entry["msgid"]
                entry_id = f"entry_{idx}:{msgid[:15]}"
                entry_errs: list[str] = []

                if "msgstr" in entry:
                    line_errs = validate_line(
                        msgid,
                        entry["msgstr"],
                        max_line_len=max_line_len,
                        max_lines=max_lines,
                        var_token_len=var_token_len,
                        custom_var_tokens=custom_var_tokens,
                    )
                    entry_errs.extend(line_errs)

                if entry.get("msgstr_plural"):
                    for p_idx, p_val in sorted(entry["msgstr_plural"].items()):
                        src_text = entry.get("msgid_plural") or msgid
                        line_errs = validate_line(
                            src_text,
                            p_val,
                            max_line_len=max_line_len,
                            max_lines=max_lines,
                            var_token_len=var_token_len,
                            custom_var_tokens=custom_var_tokens,
                        )
                        entry_errs.extend(line_errs)

                if entry_errs:
                    errors_dict[entry_id] = entry_errs

    # 2. JSON file format
    elif src_p.suffix == ".json" and dst_p.suffix == ".json":
        src_data = json.loads(src_p.read_text(encoding="utf-8"))
        dst_data = json.loads(dst_p.read_text(encoding="utf-8"))

        if isinstance(src_data, dict) and isinstance(dst_data, dict):
            total_entries = len(src_data)
            for key, src_val in src_data.items():
                if key not in dst_data:
                    errors_dict[key] = [f"Missing key in target: '{key}'"]
                    continue

                dst_val = dst_data[key]
                line_errs = validate_line(
                    str(src_val),
                    str(dst_val),
                    max_line_len=max_line_len,
                    max_lines=max_lines,
                    var_token_len=var_token_len,
                    custom_var_tokens=custom_var_tokens,
                )
                if line_errs:
                    errors_dict[key] = line_errs

            for key in dst_data:
                if key not in src_data:
                    errors_dict[key] = [f"Unexpected extra key in target: '{key}'"]

        elif isinstance(src_data, list) and isinstance(dst_data, list):
            total_entries = max(len(src_data), len(dst_data))
            for i in range(total_entries):
                key = f"index_{i}"
                if i >= len(dst_data):
                    errors_dict[key] = [f"Missing entry at index {i}"]
                elif i >= len(src_data):
                    errors_dict[key] = [f"Unexpected extra entry at index {i}"]
                else:
                    line_errs = validate_line(
                        str(src_data[i]),
                        str(dst_data[i]),
                        max_line_len=max_line_len,
                        max_lines=max_lines,
                        var_token_len=var_token_len,
                        custom_var_tokens=custom_var_tokens,
                    )
                    if line_errs:
                        errors_dict[key] = line_errs

    # 3. Plain text format
    else:
        src_lines = src_p.read_text(encoding="utf-8").splitlines()
        dst_lines = dst_p.read_text(encoding="utf-8").splitlines()
        total_entries = len(src_lines)

        if len(src_lines) != len(dst_lines):
            errors_dict["line_count"] = [
                f"File line count mismatch: source has {len(src_lines)} lines, target has {len(dst_lines)} lines"
            ]

        for idx in range(min(len(src_lines), len(dst_lines))):
            line_id = f"line_{idx + 1}"
            line_errs = validate_line(
                src_lines[idx],
                dst_lines[idx],
                max_line_len=max_line_len,
                max_lines=max_lines,
                var_token_len=var_token_len,
                custom_var_tokens=custom_var_tokens,
            )
            if line_errs:
                errors_dict[line_id] = line_errs

    error_count = sum(len(errs) for errs in errors_dict.values())
    failed_entries = len(errors_dict)
    passed_entries = max(0, total_entries - failed_entries)

    return {
        "valid": error_count == 0,
        "total_entries": total_entries,
        "passed_entries": passed_entries,
        "failed_entries": failed_entries,
        "error_count": error_count,
        "errors": errors_dict,
    }


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser for the l10n validator CLI."""
    parser = argparse.ArgumentParser(
        description="Game text tag and layout validator (enforces tag parity, layout limits, and typography)."
    )
    parser.add_argument(
        "--source", "-s", required=True, help="Path to source file (JSON, PO, or TXT)"
    )
    parser.add_argument(
        "--target", "-t", required=True, help="Path to target translated file"
    )
    parser.add_argument(
        "--max-len",
        "-l",
        type=int,
        default=40,
        help="Maximum allowed line length in characters (default: 40)",
    )
    parser.add_argument(
        "--max-lines",
        "-m",
        type=int,
        default=4,
        help="Maximum allowed lines per text box (default: 4)",
    )
    parser.add_argument(
        "--var-len",
        type=int,
        default=8,
        help="Nominal character reservation for dynamic variable tokens like {HERO_NAME} (default: 8). Set to 0 to treat as zero-width.",
    )
    parser.add_argument(
        "--var-tokens",
        default=None,
        help="Comma-separated custom tokens to add to variable tokens (e.g. '{USER},{NPC}')",
    )
    parser.add_argument(
        "--json", action="store_true", help="Output validation report in JSON format"
    )
    return parser


def main() -> None:
    """CLI entrypoint for game text tag and layout validator."""
    parser = create_parser()
    args = parser.parse_args()

    custom_tokens: set[str] | None = None
    if args.var_tokens:
        custom_tokens = {t.strip() for t in args.var_tokens.split(",") if t.strip()}

    result = validate_file(
        args.source,
        args.target,
        max_line_len=args.max_len,
        max_lines=args.max_lines,
        var_token_len=args.var_len,
        custom_var_tokens=custom_tokens,
    )

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        if result["valid"]:
            print(
                f"[PASS] All {result['total_entries']} entries validated successfully."
            )
        else:
            print(
                f"[FAIL] Found {result['error_count']} errors across {result['failed_entries']} entries:"
            )
            for entry_id, errs in result["errors"].items():
                print(f"  Entry '{entry_id}':")
                for err in errs:
                    print(f"    - {err}")

    sys.exit(0 if result["valid"] else 1)


if __name__ == "__main__":
    main()
