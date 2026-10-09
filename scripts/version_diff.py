#!/usr/bin/env python3
"""Cross-Version Script Alignment & Comparative Analysis Tool.

Loads multi-version script files (JSON, PO, TSV, CSV, or line dumps), aligns them
by dialogue key/index, detects content changes and censorship cuts, and produces
comparative Markdown reports.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import sys
from typing import Any, Optional


def _parse_po_content(content: str) -> dict[str, str]:
    """Parse Gettext PO content into a mapping of msgid to msgstr.

    Ignores empty msgid (PO header). Supports multiline strings and escape sequences.
    """
    entries: dict[str, str] = {}
    lines = content.splitlines()

    current_msgid: list[str] | None = None
    current_msgstr: list[str] | None = None
    in_msgid = False
    in_msgstr = False

    def unescape(s: str) -> str:
        s = s.strip()
        if s.startswith('"') and s.endswith('"'):
            s = s[1:-1]
        return (
            s.replace(r'\"', '"')
            .replace(r'\n', '\n')
            .replace(r'\t', '\t')
            .replace(r'\r', '\r')
            .replace(r'\\', '\\')
        )

    def flush_entry():
        nonlocal current_msgid, current_msgstr, in_msgid, in_msgstr
        if current_msgid is not None and current_msgstr is not None:
            full_msgid = "".join(current_msgid)
            full_msgstr = "".join(current_msgstr)
            if full_msgid:  # Ignore PO header with empty msgid
                entries[full_msgid] = full_msgstr
        current_msgid = None
        current_msgstr = None
        in_msgid = False
        in_msgstr = False

    for raw_line in lines:
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        if line.startswith("msgid "):
            flush_entry()
            val = unescape(line[6:])
            current_msgid = [val]
            in_msgid = True
            in_msgstr = False
        elif line.startswith("msgstr ") or line.startswith("msgstr[0] "):
            in_msgid = False
            prefix_len = 7 if line.startswith("msgstr ") else 10
            val = unescape(line[prefix_len:])
            current_msgstr = [val]
            in_msgstr = True
        elif line.startswith('"') and line.endswith('"'):
            val = unescape(line)
            if in_msgid and current_msgid is not None:
                current_msgid.append(val)
            elif in_msgstr and current_msgstr is not None:
                current_msgstr.append(val)

    flush_entry()
    return entries


def _is_header_row(col0: str, col1: str) -> bool:
    """Check if row looks like a table header (e.g. key/text, id/translation)."""
    c0 = col0.strip().lower()
    c1 = col1.strip().lower()
    key_headers = {"key", "id", "name", "msgid", "index", "code", "label"}
    val_headers = {
        "text", "value", "translation", "msgstr", "source", "target",
        "string", "dialogue", "content", "ru", "en", "jp",
    }
    return c0 in key_headers and c1 in val_headers


def load_version_file(path: str | Path) -> dict[str, str]:
    """Loads a script file and returns a mapping of key to dialogue text.

    Supports:
      - JSON mapping {key: text} or list of strings with auto-indices
      - Gettext PO files {msgid: msgstr}
      - TSV / CSV files {key: text}
      - Plain text line-by-line dumps with auto-generated integer index keys

    Args:
        path: Path to the version script file.

    Returns:
        Dictionary mapping string keys to text strings.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        ValueError: If file content is malformed or cannot be parsed.
    """
    file_path = Path(path)
    if not file_path.is_file():
        raise FileNotFoundError(f"Version file not found: {path}")

    try:
        content = file_path.read_text(encoding="utf-8-sig")
    except Exception as e:
        raise ValueError(f"Failed to read file {path}: {e}") from e

    if not content.strip():
        return {}

    ext = file_path.suffix.lower()

    # 1. JSON format
    if ext == ".json":
        try:
            data = json.loads(content)
        except Exception as e:
            raise ValueError(f"Malformed JSON in version file {path}: {e}") from e

        if isinstance(data, dict):
            res: dict[str, str] = {}
            for k, v in data.items():
                if isinstance(v, dict):
                    val = (
                        v.get("text")
                        or v.get("translation")
                        or v.get("msgstr")
                        or v.get("value")
                        or str(v)
                    )
                    res[str(k)] = str(val)
                else:
                    res[str(k)] = str(v)
            return res
        elif isinstance(data, list):
            res = {}
            for i, item in enumerate(data):
                if isinstance(item, dict):
                    key = item.get("key") or item.get("id") or str(i)
                    val = (
                        item.get("text")
                        or item.get("translation")
                        or item.get("value")
                        or item.get("msgstr")
                        or str(item)
                    )
                    res[str(key)] = str(val)
                else:
                    res[str(i)] = str(item)
            return res
        else:
            raise ValueError(
                f"Unsupported JSON structure in {path}: expected dict or list, got {type(data).__name__}"
            )

    # 2. Gettext PO format
    if ext in (".po", ".pot"):
        return _parse_po_content(content)

    # 3. TSV format
    if ext in (".tsv", ".tab"):
        reader = csv.reader(content.splitlines(), delimiter="\t")
        res = {}
        for row_idx, row in enumerate(reader):
            if not row:
                continue
            if len(row) >= 2:
                if row_idx == 0 and _is_header_row(row[0], row[1]):
                    continue
                res[row[0].strip()] = row[1].strip()
            else:
                res[str(row_idx)] = row[0].strip()
        return res

    # 4. CSV format
    if ext == ".csv":
        reader = csv.reader(content.splitlines(), delimiter=",")
        res = {}
        for row_idx, row in enumerate(reader):
            if not row:
                continue
            if len(row) >= 2:
                if row_idx == 0 and _is_header_row(row[0], row[1]):
                    continue
                res[row[0].strip()] = row[1].strip()
            else:
                res[str(row_idx)] = row[0].strip()
        return res

    # 5. Check if plain text looks like JSON
    trimmed = content.strip()
    if trimmed.startswith("{") or trimmed.startswith("["):
        try:
            data = json.loads(content)
            if isinstance(data, dict):
                return {str(k): str(v) for k, v in data.items()}
            if isinstance(data, list):
                return {str(i): str(v) for i, v in enumerate(data)}
        except Exception:
            pass

    # 6. Fallback: line-by-line text dump with integer index keys
    lines = content.splitlines()
    return {str(i): line for i, line in enumerate(lines)}


def align_versions(version_data: dict[str, dict[str, str]]) -> list[dict[str, Any]]:
    """Aligns script entries across multiple versions.

    Args:
        version_data: Mapping of version name (e.g. 'JP', 'US') to dialogue key-value map.

    Returns:
        List of aligned record dicts, each containing:
          - 'key': Dialogue key identifier
          - 'texts': Dict mapping version names to text (or None if missing)
          - 'status': 'identical', 'divergent', or 'missing_in_some'
    """
    if not version_data:
        return []

    # Preserve order of keys by first appearance across all versions
    all_keys: list[str] = []
    seen_keys: set[str] = set()
    for ver_name, ver_map in version_data.items():
        for k in ver_map.keys():
            if k not in seen_keys:
                seen_keys.add(k)
                all_keys.append(k)

    records: list[dict[str, Any]] = []
    version_names = list(version_data.keys())

    for key in all_keys:
        texts: dict[str, Optional[str]] = {}
        has_none = False

        for vname in version_names:
            val = version_data[vname].get(key, None)
            texts[vname] = val
            if val is None:
                has_none = True

        if has_none:
            status = "missing_in_some"
        else:
            unique_texts = set(texts.values())
            if len(unique_texts) <= 1:
                status = "identical"
            else:
                status = "divergent"

        records.append({
            "key": key,
            "texts": texts,
            "status": status,
        })

    return records


def _escape_cell(text: Optional[str]) -> str:
    """Escapes pipes and normalizes line breaks for Markdown table cells."""
    if text is None:
        return "*None*"
    # Normalize newlines to <br> so markdown table row isn't broken
    cell = text.replace("\r\n", "<br>").replace("\n", "<br>").replace("\r", "<br>")
    # Escape pipe characters
    cell = cell.replace("|", r"\|")
    return cell


def generate_markdown_report(
    aligned_records: list[dict[str, Any]],
    title: str = "Script Comparison Report",
    filter_divergent_only: bool = False,
    max_rows: Optional[int] = None,
) -> str:
    """Generates a formatted Markdown comparison table and summary.

    Args:
        aligned_records: List of aligned records from align_versions.
        title: Report title heading.
        filter_divergent_only: If True, omits identical records.
        max_rows: Maximum number of rows to include in the table.

    Returns:
        Formatted Markdown report string.
    """
    if not aligned_records:
        return f"# {title}\n\nNo records to display.\n"

    # Determine version names from records
    version_names: list[str] = []
    for r in aligned_records:
        for v in r.get("texts", {}).keys():
            if v not in version_names:
                version_names.append(v)

    # Calculate summary metrics
    total_records = len(aligned_records)
    identical_count = sum(1 for r in aligned_records if r.get("status") == "identical")
    divergent_count = sum(1 for r in aligned_records if r.get("status") == "divergent")
    missing_count = sum(1 for r in aligned_records if r.get("status") == "missing_in_some")

    # Filter rows if requested
    rows_to_render = []
    for r in aligned_records:
        if filter_divergent_only and r.get("status") == "identical":
            continue
        rows_to_render.append(r)

    total_filtered = len(rows_to_render)
    is_truncated = False
    if max_rows is not None and max_rows > 0 and len(rows_to_render) > max_rows:
        rows_to_render = rows_to_render[:max_rows]
        is_truncated = True

    # Build Markdown document
    lines: list[str] = [
        f"# {title}",
        "",
        "## Summary",
        f"- **Total Records:** {total_records}",
        f"- **Identical:** {identical_count}",
        f"- **Divergent:** {divergent_count}",
        f"- **Missing / Cut:** {missing_count}",
        "",
        "## Comparisons",
    ]

    # Table headers
    headers = ["Key"] + version_names + ["Notes/Status"]
    header_line = "| " + " | ".join(headers) + " |"
    sep_line = "| " + " | ".join(["---"] * len(headers)) + " |"
    lines.append(header_line)
    lines.append(sep_line)

    for r in rows_to_render:
        key_str = f"`{r['key']}`"
        status = r.get("status", "unknown")

        if status == "identical":
            status_badge = "✅ [IDENTICAL]"
        elif status == "divergent":
            status_badge = "⚠️ [DIVERGENT]"
        elif status == "missing_in_some":
            status_badge = "🔴 [CUT/MISSING]"
        else:
            status_badge = status

        row_cells = [key_str]
        for vname in version_names:
            txt = r.get("texts", {}).get(vname)
            row_cells.append(_escape_cell(txt))
        row_cells.append(status_badge)

        lines.append("| " + " | ".join(row_cells) + " |")

    if is_truncated:
        lines.append("")
        lines.append(f"*Showing {len(rows_to_render)} of {total_filtered} rows.*")

    lines.append("")
    return "\n".join(lines)


def parse_version_arg(arg: str) -> tuple[str, str]:
    """Parse version argument in NAME=PATH format."""
    if "=" not in arg:
        raise ValueError(
            f"Invalid version argument format: '{arg}'. Expected NAME=PATH (e.g. JP=jp.json)."
        )
    name, path = arg.split("=", 1)
    name = name.strip()
    path = path.strip()
    if not name or not path:
        raise ValueError(
            f"Invalid version argument: '{arg}'. Both NAME and PATH must be non-empty."
        )
    return name, path


def main(argv: Optional[list[str]] = None) -> int:
    """CLI entrypoint for cross-version script diff tool."""
    parser = argparse.ArgumentParser(
        description="Cross-Version Script Alignment & Comparative Analysis Tool"
    )
    parser.add_argument(
        "--version",
        "-v",
        action="append",
        dest="versions",
        help="Version mapping in NAME=PATH format (e.g. JP=jp.json). Specify at least 2 versions.",
    )
    parser.add_argument(
        "--output",
        "-o",
        dest="output",
        help="Path to write the Markdown report. If omitted, prints to stdout.",
    )
    parser.add_argument(
        "--divergent-only",
        action="store_true",
        dest="divergent_only",
        help="Filter out identical records and report only divergent / cut items.",
    )
    parser.add_argument(
        "--title",
        default="Script Comparison Report",
        help="Title for the Markdown comparison report.",
    )
    parser.add_argument(
        "--max-rows",
        type=int,
        default=None,
        dest="max_rows",
        help="Maximum number of comparison rows to include in the report.",
    )

    args = parser.parse_args(argv)

    if not args.versions or len(args.versions) < 2:
        sys.stderr.write(
            "Error: At least 2 version files must be specified using --version NAME=PATH.\n"
        )
        return 1

    version_data: dict[str, dict[str, str]] = {}
    for ver_arg in args.versions:
        try:
            name, path = parse_version_arg(ver_arg)
        except ValueError as e:
            sys.stderr.write(f"Error: {e}\n")
            return 1

        try:
            version_data[name] = load_version_file(path)
        except (FileNotFoundError, ValueError) as e:
            sys.stderr.write(f"Error loading {name} from {path}: {e}\n")
            return 1

    records = align_versions(version_data)
    report_md = generate_markdown_report(
        aligned_records=records,
        title=args.title,
        filter_divergent_only=args.divergent_only,
        max_rows=args.max_rows,
    )

    if args.output:
        try:
            out_path = Path(args.output)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(report_md, encoding="utf-8")
        except Exception as e:
            sys.stderr.write(f"Error writing output to {args.output}: {e}\n")
            return 1
    else:
        sys.stdout.write(report_md + "\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
