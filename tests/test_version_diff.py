"""Tests for cross-version script alignment & comparative analysis tool."""

import json
from pathlib import Path
import sys
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.version_diff import (
    load_version_file,
    align_versions,
    generate_markdown_report,
    parse_version_arg,
    main,
)


class TestLoadVersionFile:
    """Tests for load_version_file supporting JSON, PO, TSV/CSV, and text dumps."""

    def test_load_json_dict(self, tmp_path):
        f = tmp_path / "script_us.json"
        data = {
            "dialogue_001": "Good morning, Crono!",
            "dialogue_002": "Did you sleep well?",
            "dialogue_003": "Wake up, sleepy head!",
        }
        f.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

        result = load_version_file(str(f))
        assert result == data

    def test_load_json_list_of_strings(self, tmp_path):
        f = tmp_path / "script_lines.json"
        data = [
            "Good morning, Crono!",
            "Did you sleep well?",
            "Wake up, sleepy head!",
        ]
        f.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

        result = load_version_file(str(f))
        assert result == {
            "0": "Good morning, Crono!",
            "1": "Did you sleep well?",
            "2": "Wake up, sleepy head!",
        }

    def test_load_json_with_bom(self, tmp_path):
        f = tmp_path / "script_bom.json"
        content = json.dumps({"key_01": "Text with BOM"}, ensure_ascii=False)
        f.write_bytes(content.encode("utf-8-sig"))

        result = load_version_file(str(f))
        assert result == {"key_01": "Text with BOM"}

    def test_load_po_file(self, tmp_path):
        f = tmp_path / "script_ru.po"
        po_content = """# Translation header
msgid ""
msgstr ""
"Project-Id-Version: Chrono Trigger\\n"
"Content-Type: text/plain; charset=UTF-8\\n"

msgid "dialogue_001"
msgstr "Доброе утро, Кроно!"

msgid "dialogue_002"
msgstr "Ты хорошо спал?"
"""
        f.write_text(po_content, encoding="utf-8")

        result = load_version_file(str(f))
        assert result == {
            "dialogue_001": "Доброе утро, Кроно!",
            "dialogue_002": "Ты хорошо спал?",
        }
        assert "" not in result  # Header msgid should be ignored

    def test_load_po_file_multiline(self, tmp_path):
        f = tmp_path / "script_multiline.po"
        po_content = """msgid "msg_long"
msgstr "First line\\n"
"Second line"
"""
        f.write_text(po_content, encoding="utf-8")

        result = load_version_file(str(f))
        assert result == {"msg_long": "First line\nSecond line"}

    def test_load_tsv_file(self, tmp_path):
        f = tmp_path / "script.tsv"
        tsv_content = "key\ttext\n001\tMorning\n002\tEvening\n"
        f.write_text(tsv_content, encoding="utf-8")

        result = load_version_file(str(f))
        assert result == {"001": "Morning", "002": "Evening"}

    def test_load_tsv_without_header(self, tmp_path):
        f = tmp_path / "script_noheader.tsv"
        tsv_content = "001\tMorning\n002\tEvening\n"
        f.write_text(tsv_content, encoding="utf-8")

        result = load_version_file(str(f))
        assert result == {"001": "Morning", "002": "Evening"}

    def test_load_csv_file(self, tmp_path):
        f = tmp_path / "script.csv"
        csv_content = 'id,translation\nintro_01,"Hello, world!"\nintro_02,"Goodbye!"\n'
        f.write_text(csv_content, encoding="utf-8")

        result = load_version_file(str(f))
        assert result == {"intro_01": "Hello, world!", "intro_02": "Goodbye!"}

    def test_load_line_dump_text(self, tmp_path):
        f = tmp_path / "dialogue.txt"
        lines = "First dialogue line\nSecond dialogue line\nThird dialogue line"
        f.write_text(lines, encoding="utf-8")

        result = load_version_file(str(f))
        assert result == {
            "0": "First dialogue line",
            "1": "Second dialogue line",
            "2": "Third dialogue line",
        }

    def test_load_nonexistent_file(self):
        with pytest.raises(FileNotFoundError):
            load_version_file("nonexistent_script_file_123.json")

    def test_load_malformed_json(self, tmp_path):
        f = tmp_path / "bad.json"
        f.write_text("{ unquoted_bad_json: ", encoding="utf-8")

        with pytest.raises(ValueError):
            load_version_file(str(f))

    def test_load_empty_file(self, tmp_path):
        f = tmp_path / "empty.txt"
        f.write_text("", encoding="utf-8")

        result = load_version_file(str(f))
        assert result == {}


class TestAlignVersions:
    """Tests for multi-version script alignment."""

    def test_align_two_versions_identical_and_divergent(self):
        version_data = {
            "JP": {
                "001": "おはよう、クロノ！",
                "002": "よく眠れた？",
                "003": "アイテム",
            },
            "US": {
                "001": "Good morning, Crono!",
                "002": "Did you sleep well?",
                "003": "アイテム",  # accidentally identical for testing
            },
        }

        records = align_versions(version_data)
        assert len(records) == 3

        # Record 0: divergent
        assert records[0]["key"] == "001"
        assert records[0]["texts"] == {
            "JP": "おはよう、クロノ！",
            "US": "Good morning, Crono!",
        }
        assert records[0]["status"] == "divergent"

        # Record 2: identical
        assert records[2]["key"] == "003"
        assert records[2]["texts"] == {"JP": "アイテム", "US": "アイテム"}
        assert records[2]["status"] == "identical"

    def test_align_three_versions(self):
        version_data = {
            "JP": {
                "d_01": "おはよう！",
                "d_02": "はい",
            },
            "US": {
                "d_01": "Morning!",
                "d_02": "Yes",
            },
            "RU_FAN": {
                "d_01": "Доброе утро!",
                "d_02": "Да",
            },
        }

        records = align_versions(version_data)
        assert len(records) == 2
        assert records[0]["status"] == "divergent"
        assert records[0]["texts"]["JP"] == "おはよう！"
        assert records[0]["texts"]["US"] == "Morning!"
        assert records[0]["texts"]["RU_FAN"] == "Доброе утро!"

    def test_missing_key_cut_content_in_us(self):
        """Content present in Japanese original was cut/omitted in US release."""
        version_data = {
            "JP": {
                "scene_01": "Original text 1",
                "scene_cut": "Content removed in US censorship",
                "scene_02": "Original text 2",
            },
            "US": {
                "scene_01": "Original text 1",
                "scene_02": "Original text 2",
            },
        }

        records = align_versions(version_data)
        assert len(records) == 3

        cut_record = next(r for r in records if r["key"] == "scene_cut")
        assert cut_record["texts"]["JP"] == "Content removed in US censorship"
        assert cut_record["texts"]["US"] is None
        assert cut_record["status"] == "missing_in_some"

    def test_missing_key_added_in_remake(self):
        """Content newly added in NDS remake, missing in SNES original."""
        version_data = {
            "SNES": {
                "intro": "Welcome",
            },
            "NDS": {
                "intro": "Welcome",
                "arena_mode": "Arena of the Ages dialogue",
            },
        }

        records = align_versions(version_data)
        assert len(records) == 2

        arena_record = next(r for r in records if r["key"] == "arena_mode")
        assert arena_record["texts"]["SNES"] is None
        assert arena_record["texts"]["NDS"] == "Arena of the Ages dialogue"
        assert arena_record["status"] == "missing_in_some"

    def test_key_ordering_preservation(self):
        """Keys should maintain order of first appearance across versions."""
        version_data = {
            "A": {"z_key": "1", "a_key": "2"},
            "B": {"m_key": "3", "a_key": "2"},
        }

        records = align_versions(version_data)
        keys = [r["key"] for r in records]
        assert keys == ["z_key", "a_key", "m_key"]

    def test_empty_input(self):
        records = align_versions({})
        assert records == []


class TestGenerateMarkdownReport:
    """Tests for generating markdown comparison reports."""

    def test_report_structure_and_headers(self):
        records = [
            {
                "key": "msg_01",
                "texts": {"JP": "はい", "US": "Yes"},
                "status": "divergent",
            },
            {
                "key": "msg_02",
                "texts": {"JP": "共通", "US": "共通"},
                "status": "identical",
            },
        ]

        md = generate_markdown_report(records, title="Chrono Diff")

        assert "# Chrono Diff" in md
        assert "| Key | JP | US | Notes/Status |" in md
        assert "| --- | --- | --- | --- |" in md
        assert "| `msg_01` | はい | Yes | ⚠️ [DIVERGENT] |" in md
        assert "| `msg_02` | 共通 | 共通 | ✅ [IDENTICAL] |" in md

    def test_pipe_character_escaping(self):
        """Pipe characters inside text must be escaped as \\| to preserve Markdown table structure."""
        records = [
            {
                "key": "menu_opt",
                "texts": {
                    "EN": "Attack | Defend | Item",
                    "RU": "Атака | Защита | Предмет",
                },
                "status": "divergent",
            }
        ]

        md = generate_markdown_report(records)
        assert "Attack \\| Defend \\| Item" in md
        assert "Атака \\| Защита \\| Предмет" in md
        # Verify line has exactly 5 pipes separating 4 columns: | col1 | col2 | col3 | col4 |
        table_lines = [line for line in md.splitlines() if "`menu_opt`" in line]
        assert len(table_lines) == 1
        # Unescaped pipes count should be 5
        unescaped_pipes = table_lines[0].replace(r"\|", "").count("|")
        assert unescaped_pipes == 5

    def test_visual_indicators(self):
        """Check visual indicators for missing and divergent items."""
        records = [
            {
                "key": "cut_scene",
                "texts": {"JP": "Some dialogue", "US": None},
                "status": "missing_in_some",
            },
            {
                "key": "diff_scene",
                "texts": {"JP": "Text A", "US": "Text B"},
                "status": "divergent",
            },
            {
                "key": "same_scene",
                "texts": {"JP": "Same", "US": "Same"},
                "status": "identical",
            },
        ]

        md = generate_markdown_report(records)
        assert "🔴 [CUT/MISSING]" in md
        assert "⚠️ [DIVERGENT]" in md
        assert "✅ [IDENTICAL]" in md

    def test_filter_divergent_only(self):
        records = [
            {
                "key": "diff_01",
                "texts": {"JP": "A", "US": "B"},
                "status": "divergent",
            },
            {
                "key": "same_02",
                "texts": {"JP": "Same", "US": "Same"},
                "status": "identical",
            },
            {
                "key": "cut_03",
                "texts": {"JP": "Cut", "US": None},
                "status": "missing_in_some",
            },
        ]

        md = generate_markdown_report(records, filter_divergent_only=True)
        assert "`diff_01`" in md
        assert "`cut_03`" in md
        assert "`same_02`" not in md

    def test_max_rows_limiting(self):
        records = [
            {
                "key": f"key_{i}",
                "texts": {"JP": f"text_{i}", "US": f"text_{i}"},
                "status": "identical",
            }
            for i in range(20)
        ]

        md = generate_markdown_report(records, max_rows=5)
        # Should only have 5 rows in table
        assert "`key_0`" in md
        assert "`key_4`" in md
        assert "`key_5`" not in md
        assert "5 of 20" in md

    def test_multiline_dialogue_escaping(self):
        records = [
            {
                "key": "multi",
                "texts": {"JP": "Line1\nLine2", "US": "LineA\nLineB"},
                "status": "divergent",
            }
        ]

        md = generate_markdown_report(records)
        # Table rows must not be broken by literal unescaped newlines
        table_lines = [line for line in md.splitlines() if "`multi`" in line]
        assert len(table_lines) == 1
        assert "<br>" in table_lines[0] or "\\n" in table_lines[0]


class TestCLI:
    """Tests for CLI interface of version_diff.py."""

    def test_parse_version_arg(self):
        name, path = parse_version_arg("JP=path/to/jp.json")
        assert name == "JP"
        assert path == "path/to/jp.json"

        name, path = parse_version_arg("RU_FAN=path/to/file=with=equals.json")
        assert name == "RU_FAN"
        assert path == "path/to/file=with=equals.json"

    def test_parse_version_arg_invalid(self):
        with pytest.raises(ValueError):
            parse_version_arg("invalid_argument_no_equals")

    def test_cli_two_versions_stdout(self, tmp_path, capsys):
        jp_file = tmp_path / "jp.json"
        us_file = tmp_path / "us.json"
        jp_file.write_text(json.dumps({"k1": "JP1", "k2": "Same"}), encoding="utf-8")
        us_file.write_text(json.dumps({"k1": "US1", "k2": "Same"}), encoding="utf-8")

        exit_code = main([
            "--version", f"JP={jp_file}",
            "--version", f"US={us_file}",
            "--title", "Test CLI Diff",
        ])

        assert exit_code == 0
        captured = capsys.readouterr()
        assert "# Test CLI Diff" in captured.out
        assert "JP1" in captured.out
        assert "US1" in captured.out

    def test_cli_output_to_file(self, tmp_path):
        jp_file = tmp_path / "jp.json"
        us_file = tmp_path / "us.json"
        out_file = tmp_path / "output_report.md"

        jp_file.write_text(json.dumps({"k1": "JP1"}), encoding="utf-8")
        us_file.write_text(json.dumps({"k1": "US1"}), encoding="utf-8")

        exit_code = main([
            "--version", f"JP={jp_file}",
            "--version", f"US={us_file}",
            "--output", str(out_file),
        ])

        assert exit_code == 0
        assert out_file.exists()
        content = out_file.read_text(encoding="utf-8")
        assert "# Script Comparison Report" in content
        assert "JP1" in content

    def test_cli_divergent_only_flag(self, tmp_path, capsys):
        jp_file = tmp_path / "jp.json"
        us_file = tmp_path / "us.json"
        jp_file.write_text(json.dumps({"k1": "JP1", "same": "X"}), encoding="utf-8")
        us_file.write_text(json.dumps({"k1": "US1", "same": "X"}), encoding="utf-8")

        exit_code = main([
            "--version", f"JP={jp_file}",
            "--version", f"US={us_file}",
            "--divergent-only",
        ])

        assert exit_code == 0
        captured = capsys.readouterr()
        assert "`k1`" in captured.out
        assert "`same`" not in captured.out

    def test_cli_three_versions(self, tmp_path, capsys):
        jp_file = tmp_path / "jp.json"
        us_file = tmp_path / "us.json"
        ru_file = tmp_path / "ru.json"
        jp_file.write_text(json.dumps({"k1": "JP1"}), encoding="utf-8")
        us_file.write_text(json.dumps({"k1": "US1"}), encoding="utf-8")
        ru_file.write_text(json.dumps({"k1": "RU1"}), encoding="utf-8")

        exit_code = main([
            "--version", f"JP={jp_file}",
            "--version", f"US={us_file}",
            "--version", f"RU={ru_file}",
        ])

        assert exit_code == 0
        captured = capsys.readouterr()
        assert "| Key | JP | US | RU | Notes/Status |" in captured.out

    def test_cli_missing_versions(self, capsys):
        exit_code = main(["--version", "JP=dummy.json"])
        assert exit_code != 0
        captured = capsys.readouterr()
        assert "error" in captured.err.lower() or "at least 2" in captured.err.lower()
