import os
import sys
import tempfile
import json
import subprocess
from pathlib import Path
import pytest

# Ensure repo root is on sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.l10n_validator import (
    DEFAULT_VARIABLE_TOKENS,
    check_layout_budget,
    create_parser,
    extract_tags,
    strip_non_visual_tags,
    validate_file,
    validate_line,
)


class TestTagExtraction:
    def test_extract_braced_and_bracketed_tags(self):
        text = "Hello {HERO}, take [ITEM 1] and go to {LOCATION}!"
        tags = extract_tags(text)
        assert tags == ["{HERO}", "[ITEM 1]", "{LOCATION}"]

    def test_extract_printf_and_newlines(self):
        text = "Score: %d\nName: %s\tRank: %02d\\n"
        tags = extract_tags(text)
        # Should extract %d, \n, %s, \t, %02d, \n
        assert "%d" in tags
        assert "%s" in tags
        assert "%02d" in tags
        assert "\n" in tags or "\\n" in tags


class TestTagIntegrity:
    def test_exact_tag_match(self):
        src = "Hello {HERO}!\nWelcome to {LOCATION}.\nUse [ITEM 1] to enter."
        dst = "Привет, {HERO}!\nВ добрый путь в {LOCATION}.\nВозьми [ITEM 1]."
        errors = validate_line(src, dst)
        assert errors == []

    def test_dropped_tag_detection(self):
        src = "Press {BUTTON_A} to jump and {BUTTON_B} to run."
        dst = "Нажмите {BUTTON_A}, чтобы прыгнуть, и бегите."
        errors = validate_line(src, dst)
        assert any("BUTTON_B" in err and "missing" in err.lower() for err in errors)

    def test_extra_tag_detection(self):
        src = "Hello world!"
        dst = "Привет {HERO} мир!"
        errors = validate_line(src, dst)
        assert any("HERO" in err and ("unexpected" in err.lower() or "extra" in err.lower()) for err in errors)

    def test_tag_casing_mismatch(self):
        src = "Use {COLOR 1}magic{COLOR 0} now!"
        dst = "Используй {color 1}магию{COLOR 0} сейчас!"
        errors = validate_line(src, dst)
        assert any("casing" in err.lower() and "COLOR 1" in err for err in errors)

    def test_tag_argument_corruption(self):
        src = "Get {COLOR 1}item{COLOR 0}!"
        dst = "Получи {COLOR 2}предмет{COLOR 0}!"
        errors = validate_line(src, dst)
        assert len(errors) > 0
        assert any("COLOR 1" in err or "COLOR 2" in err for err in errors)

    def test_malformed_unclosed_brace(self):
        src = "{HERO}: Let's go!"
        dst = "{HERO: Вперёд!"
        errors = validate_line(src, dst)
        assert any("malformed" in err.lower() or "unclosed" in err.lower() for err in errors)

    def test_malformed_unclosed_bracket(self):
        src = "Found [ITEM 1]!"
        dst = "Найдено [ITEM 1!"
        errors = validate_line(src, dst)
        assert any("malformed" in err.lower() or "unclosed" in err.lower() for err in errors)

    def test_tag_count_mismatch(self):
        src = "Give %s and %s to %s."
        dst = "Отдай %s и %s."
        errors = validate_line(src, dst)
        assert any("%s" in err and ("count" in err.lower() or "missing" in err.lower()) for err in errors)


class TestLayoutBudgets:
    def test_line_length_within_limit(self):
        src = "Short text."
        dst = "Короткий текст."
        errors = validate_line(src, dst, max_line_len=40)
        assert errors == []

    def test_line_length_overflow(self):
        src = "Short text."
        dst = "Это очень длинный текст, который гарантированно превышает сорок символов в длину!"
        errors = validate_line(src, dst, max_line_len=40)
        assert any("length" in err.lower() or "exceeds" in err.lower() for err in errors)

    def test_multiline_length_overflow(self):
        src = "Line one.\nLine two."
        dst = "Короткая строка.\nВторая строка невероятно длинная и не поместится ни в какое окно диалога!"
        errors = validate_line(src, dst, max_line_len=40)
        assert any("Line 2" in err or "exceeds" in err.lower() for err in errors)

    def test_line_count_within_budget(self):
        src = "A\nB\nC"
        dst = "А\nБ\nВ"
        errors = validate_line(src, dst, max_lines=4)
        assert errors == []

    def test_line_count_overflow(self):
        src = "A\nB\nC\nD"
        dst = "Строка 1\nСтрока 2\nСтрока 3\nСтрока 4\nСтрока 5"
        errors = validate_line(src, dst, max_lines=4)
        assert any("line count" in err.lower() or "budget" in err.lower() or "lines" in err.lower() for err in errors)

    def test_multipage_line_count_budget(self):
        src = "A\nB{PAGE}C\nD"
        dst = "Строка 1\nСтрока 2{PAGE}Строка 3\nСтрока 4"
        errors = validate_line(src, dst, max_lines=2)
        assert errors == []

        dst_overflow = "Строка 1\nСтрока 2\nСтрока 3{PAGE}Строка 4"
        errors_overflow = validate_line(src, dst_overflow, max_lines=2)
        assert len(errors_overflow) > 0


class TestRussianTypography:
    def test_straight_ascii_quotes_warning(self):
        src = 'He said "Hello".'
        dst = 'Он сказал "Привет".'
        errors = validate_line(src, dst)
        assert any("quote" in err.lower() or "guillemet" in err.lower() or "«" in err for err in errors)

    def test_guillemets_pass(self):
        src = 'He said "Hello".'
        dst = "Он сказал «Привет»."
        errors = validate_line(src, dst)
        assert not any("quote" in err.lower() for err in errors)

    def test_hyphen_as_dialogue_dash(self):
        src = "- Good morning!"
        dst = "- Доброе утро!"
        errors = validate_line(src, dst)
        assert any("dash" in err.lower() or "em-dash" in err.lower() or "—" in err for err in errors)

    def test_hyphen_as_sentence_dash(self):
        src = "Magic - it is real."
        dst = "Магия - она существует."
        errors = validate_line(src, dst)
        assert any("dash" in err.lower() or "em-dash" in err.lower() or "—" in err for err in errors)

    def test_em_dash_passes(self):
        src = "— Good morning!"
        dst = "— Доброе утро! Магия — она существует."
        errors = validate_line(src, dst)
        assert not any("dash" in err.lower() for err in errors)

    def test_compound_word_hyphen_not_flagged(self):
        src = "Someone came."
        dst = "Кто-то пришёл из-за угла."
        errors = validate_line(src, dst)
        assert not any("dash" in err.lower() for err in errors)


class TestValidateFile:
    def test_validate_file_json_clean(self, tmp_path):
        src_data = {"key1": "Hello {HERO}!", "key2": "Good morning."}
        dst_data = {"key1": "Привет, {HERO}!", "key2": "Доброе утро."}

        src_file = tmp_path / "src.json"
        dst_file = tmp_path / "dst.json"
        src_file.write_text(json.dumps(src_data), encoding="utf-8")
        dst_file.write_text(json.dumps(dst_data), encoding="utf-8")

        result = validate_file(str(src_file), str(dst_file))
        assert result["valid"] is True
        assert result["error_count"] == 0
        assert len(result["errors"]) == 0

    def test_validate_file_json_with_errors(self, tmp_path):
        src_data = {"key1": "Hello {HERO}!", "key2": 'He said "Run".'}
        dst_data = {"key1": "Привет {hero}!", "key2": 'Он сказал "Беги".'}

        src_file = tmp_path / "src.json"
        dst_file = tmp_path / "dst.json"
        src_file.write_text(json.dumps(src_data), encoding="utf-8")
        dst_file.write_text(json.dumps(dst_data), encoding="utf-8")

        result = validate_file(str(src_file), str(dst_file))
        assert result["valid"] is False
        assert result["error_count"] >= 2
        assert "key1" in result["errors"]
        assert "key2" in result["errors"]

    def test_validate_file_missing_key(self, tmp_path):
        src_data = {"key1": "One", "key2": "Two"}
        dst_data = {"key1": "Один"}

        src_file = tmp_path / "src.json"
        dst_file = tmp_path / "dst.json"
        src_file.write_text(json.dumps(src_data), encoding="utf-8")
        dst_file.write_text(json.dumps(dst_data), encoding="utf-8")

        result = validate_file(str(src_file), str(dst_file))
        assert result["valid"] is False
        assert any("key2" in str(err) for err in result["errors"].values())

    def test_validate_file_text(self, tmp_path):
        src_text = "Line 1 {COLOR 1}\nLine 2\n"
        dst_text = "Строка 1 {COLOR 1}\nСтрока 2\n"

        src_file = tmp_path / "src.txt"
        dst_file = tmp_path / "dst.txt"
        src_file.write_text(src_text, encoding="utf-8")
        dst_file.write_text(dst_text, encoding="utf-8")

        result = validate_file(str(src_file), str(dst_file))
        assert result["valid"] is True
        assert result["error_count"] == 0

    def test_validate_file_po(self, tmp_path):
        po_content = (
            'msgid ""\n'
            'msgstr ""\n'
            '"Content-Type: text/plain; charset=UTF-8\\n"\n\n'
            'msgid "Welcome {HERO}!"\n'
            'msgstr "Добро пожаловать, {HERO}!"\n\n'
            'msgid "Press {BUTTON_A}."\n'
            'msgstr "Нажмите {BUTTON_B}."\n'
        )
        po_file = tmp_path / "test.po"
        po_file.write_text(po_content, encoding="utf-8")

        # In PO files, src and dst can be the same file or dst is validated
        result = validate_file(str(po_file), str(po_file))
        assert result["valid"] is False
        assert result["error_count"] > 0


class TestCliInterface:
    def test_cli_pass(self, tmp_path):
        src_data = {"msg": "Hello {HERO}!"}
        dst_data = {"msg": "Привет, {HERO}!"}

        src_file = tmp_path / "src.json"
        dst_file = tmp_path / "dst.json"
        src_file.write_text(json.dumps(src_data), encoding="utf-8")
        dst_file.write_text(json.dumps(dst_data), encoding="utf-8")

        cmd = [
            sys.executable,
            str(REPO_ROOT / "scripts" / "l10n_validator.py"),
            "--source",
            str(src_file),
            "--target",
            str(dst_file),
            "--max-len",
            "40",
            "--max-lines",
            "4",
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        assert proc.returncode == 0
        assert "PASS" in proc.stdout

    def test_cli_fail(self, tmp_path):
        src_data = {"msg": "Hello {HERO}!"}
        dst_data = {"msg": "Привет, {hero}!"}

        src_file = tmp_path / "src.json"
        dst_file = tmp_path / "dst.json"
        src_file.write_text(json.dumps(src_data), encoding="utf-8")
        dst_file.write_text(json.dumps(dst_data), encoding="utf-8")

        cmd = [
            sys.executable,
            str(REPO_ROOT / "scripts" / "l10n_validator.py"),
            "--source",
            str(src_file),
            "--target",
            str(dst_file),
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        assert proc.returncode != 0
        assert "FAIL" in proc.stdout or "FAIL" in proc.stderr


class TestEnhancedFeatures:
    def test_complex_format_specifiers(self):
        text = "Score: %1$s scored %+08.2f (%.1f%%) in %lld ms with %zu items"
        tags = extract_tags(text)
        assert "%1$s" in tags
        assert "%+08.2f" in tags
        assert "%.1f" in tags
        assert "%%" in tags
        assert "%lld" in tags
        assert "%zu" in tags

    def test_complex_format_specifier_parity(self):
        src = "Player %1$s scored %2$d points (%.2f%%)."
        dst = "Игрок %1$s набрал %2$d очков (%.2f%%)."
        errors = validate_line(src, dst)
        assert errors == []

    def test_complex_format_specifier_mismatch(self):
        src = "Player %1$s scored %2$d points."
        dst = "Игрок %2$s набрал %1$d очков."
        # Casing or token mismatch between %1$s and %2$s
        errors = validate_line(src, dst)
        assert len(errors) > 0

    def test_trailing_newline_no_false_overflow(self):
        src = "Line 1\nLine 2\nLine 3\nLine 4\n"
        dst = "Строка 1\nСтрока 2\nСтрока 3\nСтрока 4\n"
        errors = validate_line(src, dst, max_lines=4)
        assert errors == []

    def test_escaped_newline_dialogue_dash(self):
        src = "First line\\n- Second line"
        dst = "Первая строка\\n- Вторая строка"
        errors = validate_line(src, dst)
        assert any("dash" in err.lower() or "—" in err for err in errors)

    def test_distinct_po_files_pairing(self, tmp_path):
        src_content = (
            'msgid ""\n'
            'msgstr ""\n\n'
            'msgid "Welcome {HERO}!"\n'
            'msgstr ""\n\n'
            'msgid "%d item"\n'
            'msgid_plural "%d items"\n'
            'msgstr[0] ""\n'
            'msgstr[1] ""\n'
        )
        dst_content = (
            'msgid ""\n'
            'msgstr ""\n\n'
            'msgid "Welcome {HERO}!"\n'
            'msgstr "Добро пожаловать, {HERO}!"\n\n'
            'msgid "%d item"\n'
            'msgid_plural "%d items"\n'
            'msgstr[0] "%d предмет"\n'
            'msgstr[1] "%d предмета"\n'
            'msgstr[2] "%d предметов"\n'
        )
        src_po = tmp_path / "messages.pot"
        dst_po = tmp_path / "ru.po"
        src_po.write_text(src_content, encoding="utf-8")
        dst_po.write_text(dst_content, encoding="utf-8")

        result = validate_file(str(src_po), str(dst_po))
        assert result["valid"] is True
        assert result["error_count"] == 0

    def test_distinct_po_files_with_plural_tag_corruption(self, tmp_path):
        src_content = (
            'msgid "%d items found"\n'
            'msgid_plural "%d items found"\n'
            'msgstr[0] ""\n'
        )
        dst_content = (
            'msgid "%d items found"\n'
            'msgid_plural "%d items found"\n'
            'msgstr[0] "%d предмет найден"\n'
            'msgstr[1] "%s предмета найдено"\n'
        )
        src_po = tmp_path / "messages.pot"
        dst_po = tmp_path / "ru.po"
        src_po.write_text(src_content, encoding="utf-8")
        dst_po.write_text(dst_content, encoding="utf-8")

        result = validate_file(str(src_po), str(dst_po))
        assert result["valid"] is False
        assert result["error_count"] > 0


class TestVariableTokenBudgeting:
    def test_strip_non_visual_tags_default_tokens(self):
        text = "{COLOR 1}Привет, {HERO_NAME}!{COLOR 0} Возьми [ITEM 1] у {LOCATION}."
        # HERO_NAME and LOCATION should be replaced with 8 X's
        # COLOR 1, COLOR 0, and [ITEM 1] should be stripped to empty string
        result = strip_non_visual_tags(text, var_token_len=8)
        assert result == "Привет, XXXXXXXX! Возьми  у XXXXXXXX."

    def test_all_default_variable_tokens_budgeted(self):
        for token in DEFAULT_VARIABLE_TOKENS:
            res = strip_non_visual_tags(f"Prefix {token} Suffix", var_token_len=6)
            assert res == "Prefix XXXXXX Suffix"

    def test_non_visual_tags_stripped_to_empty(self):
        text = "{COLOR 2}{WAIT 10}{DELAY 5}{SFX 1}{KEY_A}{CLEAR}Текст"
        result = strip_non_visual_tags(text, var_token_len=8)
        assert result == "Текст"

    def test_custom_var_tokens(self):
        text = "Hello {CUSTOM_NPC} and [SPECIAL_ITEM]!"
        result = strip_non_visual_tags(
            text,
            var_token_len=5,
            custom_var_tokens={"{CUSTOM_NPC}", "[SPECIAL_ITEM]"},
        )
        assert result == "Hello XXXXX and XXXXX!"

    def test_var_token_len_zero(self):
        text = "Hello {HERO_NAME}!"
        result = strip_non_visual_tags(text, var_token_len=0)
        assert result == "Hello !"

    def test_layout_budget_variable_token_overflow(self):
        # 35 characters + {HERO_NAME} (8 chars) = 43 chars (> 40)
        text = "Это длинное предложение для героя: {HERO_NAME}"
        errors = check_layout_budget(text, max_line_len=40, var_token_len=8)
        assert len(errors) == 1
        assert "exceeds max length (43 > 40)" in errors[0]

    def test_layout_budget_variable_token_pass_with_zero_len(self):
        # 35 characters + {HERO_NAME} (0 chars) = 35 chars (<= 40)
        text = "Это длинное предложение для героя: {HERO_NAME}"
        errors = check_layout_budget(text, max_line_len=40, var_token_len=0)
        assert errors == []

    def test_validate_line_with_var_len(self):
        src = "Hero: {HERO_NAME}"
        # 35 chars in Russian + {HERO_NAME}
        dst = "Это длинное предложение для героя: {HERO_NAME}"
        # Default var_token_len=8: 35 + 8 = 43 > 40 -> fails
        errors_default = validate_line(src, dst, max_line_len=40)
        assert any("exceeds max length" in err for err in errors_default)

        # Custom var_token_len=4: 35 + 4 = 39 <= 40 -> passes
        errors_shorter = validate_line(src, dst, max_line_len=40, var_token_len=4)
        assert errors_shorter == []

    def test_validate_file_with_var_token_budgeting(self, tmp_path):
        src_data = {"key1": "Hello {HERO_NAME}!"}
        # 35 chars + {HERO_NAME}
        dst_data = {"key1": "Это длинное предложение для героя: {HERO_NAME}"}

        src_file = tmp_path / "src.json"
        dst_file = tmp_path / "dst.json"
        src_file.write_text(json.dumps(src_data), encoding="utf-8")
        dst_file.write_text(json.dumps(dst_data), encoding="utf-8")

        res_fail = validate_file(str(src_file), str(dst_file), max_line_len=40, var_token_len=8)
        assert res_fail["valid"] is False

        res_pass = validate_file(str(src_file), str(dst_file), max_line_len=40, var_token_len=0)
        assert res_pass["valid"] is True


class TestCliVariableTokens:
    def test_cli_var_len_default_overflow(self, tmp_path):
        src_data = {"line": "Name: {HERO_NAME}"}
        # 35 chars + {HERO_NAME}
        dst_data = {"line": "Это длинное предложение для героя: {HERO_NAME}"}

        src_file = tmp_path / "src.json"
        dst_file = tmp_path / "dst.json"
        src_file.write_text(json.dumps(src_data), encoding="utf-8")
        dst_file.write_text(json.dumps(dst_data), encoding="utf-8")

        cmd = [
            sys.executable,
            str(REPO_ROOT / "scripts" / "l10n_validator.py"),
            "--source",
            str(src_file),
            "--target",
            str(dst_file),
            "--max-len",
            "40",
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        assert proc.returncode != 0
        assert "FAIL" in proc.stdout or "FAIL" in proc.stderr

    def test_cli_var_len_zero_passes(self, tmp_path):
        src_data = {"line": "Name: {HERO_NAME}"}
        dst_data = {"line": "Это длинное предложение для героя: {HERO_NAME}"}

        src_file = tmp_path / "src.json"
        dst_file = tmp_path / "dst.json"
        src_file.write_text(json.dumps(src_data), encoding="utf-8")
        dst_file.write_text(json.dumps(dst_data), encoding="utf-8")

        cmd = [
            sys.executable,
            str(REPO_ROOT / "scripts" / "l10n_validator.py"),
            "--source",
            str(src_file),
            "--target",
            str(dst_file),
            "--max-len",
            "40",
            "--var-len",
            "0",
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        assert proc.returncode == 0
        assert "PASS" in proc.stdout

    def test_cli_custom_var_tokens(self, tmp_path):
        src_data = {"line": "User: {MY_USER_TAG}"}
        # 35 chars + {MY_USER_TAG}
        dst_data = {"line": "Это длинное предложение для юзера: {MY_USER_TAG}"}

        src_file = tmp_path / "src.json"
        dst_file = tmp_path / "dst.json"
        src_file.write_text(json.dumps(src_data), encoding="utf-8")
        dst_file.write_text(json.dumps(dst_data), encoding="utf-8")

        # Without custom var token: {MY_USER_TAG} is treated as non-visual tag (0 chars), total = 35 <= 40 -> PASS
        cmd_no_custom = [
            sys.executable,
            str(REPO_ROOT / "scripts" / "l10n_validator.py"),
            "--source",
            str(src_file),
            "--target",
            str(dst_file),
            "--max-len",
            "40",
        ]
        proc1 = subprocess.run(cmd_no_custom, capture_output=True, text=True)
        assert proc1.returncode == 0

        # With --var-tokens "{MY_USER_TAG}": budgeted as 8 chars -> 35 + 8 = 43 > 40 -> FAIL
        cmd_custom = [
            sys.executable,
            str(REPO_ROOT / "scripts" / "l10n_validator.py"),
            "--source",
            str(src_file),
            "--target",
            str(dst_file),
            "--max-len",
            "40",
            "--var-tokens",
            "{MY_USER_TAG}",
        ]
        proc2 = subprocess.run(cmd_custom, capture_output=True, text=True)
        assert proc2.returncode != 0
        assert "FAIL" in proc2.stdout or "FAIL" in proc2.stderr

