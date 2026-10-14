import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.glossary_tool import (
    Glossary,
    extract_candidates,
    check_compliance,
    main,
)


class TestGlossaryLoadingSaving:
    def test_load_json_glossary(self, tmp_path):
        glossary_file = tmp_path / "glossary.json"
        data = [
            {
                "source": "Potion",
                "ru": "Зелье",
                "category": "item",
                "gender": "neutral",
                "notes": "Heals 50 HP",
                "source_lang": "en",
            },
            {
                "source": "Phoenix Down",
                "ru": "Перо феникса",
                "category": "item",
                "gender": "neutral",
                "notes": "Revives an ally",
                "source_lang": "en",
            },
        ]
        glossary_file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

        g = Glossary()
        g.load_file(str(glossary_file))

        assert len(g.terms) == 2
        assert g.terms[0]["source"] == "Potion"
        assert g.terms[0]["ru"] == "Зелье"
        assert g.terms[1]["source"] == "Phoenix Down"
        assert g.terms[1]["ru"] == "Перо феникса"

    def test_load_json_glossary_dict_wrapper(self, tmp_path):
        glossary_file = tmp_path / "glossary_wrapper.json"
        data = {
            "terms": [
                {
                    "source": "Iron Sword",
                    "ru": "Железный меч",
                    "category": "equipment",
                    "gender": "masculine",
                    "notes": "",
                    "source_lang": "en",
                }
            ]
        }
        glossary_file.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

        g = Glossary()
        g.load_file(str(glossary_file))
        assert len(g.terms) == 1
        assert g.terms[0]["source"] == "Iron Sword"
        assert g.terms[0]["ru"] == "Железный меч"

    def test_save_json_glossary(self, tmp_path):
        glossary_file = tmp_path / "saved_glossary.json"
        g = Glossary()
        g.add_term("Fire Arrow", "Огненная стрела", category="skill", gender="feminine", notes="Fire attack", source_lang="en")
        g.save_file(str(glossary_file))

        assert glossary_file.exists()
        loaded = json.loads(glossary_file.read_text(encoding="utf-8"))
        assert len(loaded) == 1
        assert loaded[0]["source"] == "Fire Arrow"
        assert loaded[0]["ru"] == "Огненная стрела"

    def test_load_tsv_glossary(self, tmp_path):
        tsv_file = tmp_path / "glossary.tsv"
        content = (
            "source\tru\tcategory\tgender\tnotes\tsource_lang\n"
            "Potion\tЗелье\titem\tneutral\tHeals 50 HP\ten\n"
            "ポーション\tЗелье\titem\tneutral\tHeals 50 HP\tja\n"
        )
        tsv_file.write_text(content, encoding="utf-8")

        g = Glossary()
        g.load_file(str(tsv_file))
        assert len(g.terms) == 2
        assert g.terms[0]["source"] == "Potion"
        assert g.terms[1]["source"] == "ポーション"
        assert g.terms[1]["source_lang"] == "ja"

    def test_load_tsv_two_columns_without_header(self, tmp_path):
        tsv_file = tmp_path / "simple.tsv"
        content = "Excalibur\tЭкскалибур\nChrono\tКроно\n"
        tsv_file.write_text(content, encoding="utf-8")

        g = Glossary()
        g.load_file(str(tsv_file))
        assert len(g.terms) == 2
        assert g.terms[0]["source"] == "Excalibur"
        assert g.terms[0]["ru"] == "Экскалибур"

    def test_save_tsv_glossary(self, tmp_path):
        tsv_file = tmp_path / "saved.tsv"
        g = Glossary()
        g.add_term("Grand Dream", "Гранд Дрим", category="weapon", gender="masculine", notes="Legendary sword", source_lang="en")
        g.save_file(str(tsv_file))

        assert tsv_file.exists()
        lines = tsv_file.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 2
        header = lines[0].split("\t")
        assert header[0] == "source"
        assert header[1] == "ru"
        data_row = lines[1].split("\t")
        assert data_row[0] == "Grand Dream"
        assert data_row[1] == "Гранд Дрим"

    def test_load_tsv_trailing_empty_columns_preserved(self, tmp_path):
        tsv_file = tmp_path / "trailing_tabs.tsv"
        content = (
            "source\tru\tcategory\tgender\tnotes\tsource_lang\n"
            "Potion\tЗелье\tconsumable\t\t\t\n"
        )
        tsv_file.write_text(content, encoding="utf-8")

        g = Glossary()
        g.load_file(str(tsv_file))
        assert len(g.terms) == 1
        assert g.terms[0]["source"] == "Potion"
        assert g.terms[0]["ru"] == "Зелье"
        assert g.terms[0]["category"] == "consumable"
        assert g.terms[0]["gender"] == "neutral"
        assert g.terms[0]["notes"] == ""
        assert g.terms[0]["source_lang"] == "en"

    def test_load_missing_file_raises_error(self):
        g = Glossary()
        with pytest.raises(FileNotFoundError):
            g.load_file("nonexistent_glossary_file.json")

    def test_load_malformed_json_raises_error(self, tmp_path):
        bad_json = tmp_path / "bad.json"
        bad_json.write_text("{invalid json", encoding="utf-8")
        g = Glossary()
        with pytest.raises(ValueError):
            g.load_file(str(bad_json))


class TestGlossaryLookupAndAdd:
    def test_add_valid_term(self):
        g = Glossary()
        added = g.add_term("Potion", "Зелье", category="item", gender="neutral", notes="Restore HP", source_lang="en")
        assert added is True
        assert len(g.terms) == 1
        assert g.terms[0]["source"] == "Potion"

    def test_add_empty_term_rejected(self):
        g = Glossary()
        assert g.add_term("", "Зелье") is False
        assert g.add_term("Potion", "") is False
        assert g.add_term("   ", "   ") is False
        assert len(g.terms) == 0

    def test_add_term_updates_existing(self):
        g = Glossary()
        g.add_term("Potion", "Зелье", category="item", notes="v1", source_lang="en")
        g.add_term("Potion", "Малое зелье", category="consumable", notes="v2", source_lang="en")
        assert len(g.terms) == 1
        assert g.terms[0]["ru"] == "Малое зелье"
        assert g.terms[0]["category"] == "consumable"
        assert g.terms[0]["notes"] == "v2"

    def test_lookup_exact_and_case_sensitive(self):
        g = Glossary()
        g.add_term("Potion", "Зелье", source_lang="en")

        # Exact case match
        res_exact = g.lookup("Potion", case_sensitive=True)
        assert len(res_exact) == 1
        assert res_exact[0]["ru"] == "Зелье"

        # Case mismatch with case_sensitive=True
        res_mismatch = g.lookup("potion", case_sensitive=True)
        assert len(res_mismatch) == 0

        # Case-insensitive match
        res_case_ins = g.lookup("potion", case_sensitive=False)
        assert len(res_case_ins) == 1
        assert res_case_ins[0]["ru"] == "Зелье"

    def test_lookup_by_target_ru(self):
        g = Glossary()
        g.add_term("Potion", "Зелье", source_lang="en")
        g.add_term("ポーション", "Зелье", source_lang="ja")

        res_ru = g.lookup("Зелье", lang="ru")
        assert len(res_ru) == 2

    def test_lookup_by_source_lang_filter(self):
        g = Glossary()
        g.add_term("Potion", "Зелье", source_lang="en")
        g.add_term("ポーション", "Зелье", source_lang="ja")

        res_en = g.lookup("Potion", lang="en")
        assert len(res_en) == 1
        assert res_en[0]["source"] == "Potion"

        res_ja_fail = g.lookup("Potion", lang="ja")
        assert len(res_ja_fail) == 0

        res_ja = g.lookup("ポーション", lang="ja")
        assert len(res_ja) == 1
        assert res_ja[0]["source"] == "ポーション"

    def test_lookup_not_found(self):
        g = Glossary()
        g.add_term("Potion", "Зелье")
        assert g.lookup("Elixir") == []


class TestCandidateExtraction:
    def test_extract_japanese_katakana_candidates(self):
        text = "ポーションとエクスカリバー、そしてブレイブ・ハートを手に入れた。"
        candidates = extract_candidates(text, lang="ja")
        assert "ポーション" in candidates
        assert "エクスカリバー" in candidates
        assert "ブレイブ・ハート" in candidates

    def test_extract_english_entity_phrases(self):
        text = "You found the Phoenix Down and Chrono Trigger in the chest. Also take the Iron Sword and Fire Arrow."
        candidates = extract_candidates(text, lang="en")
        assert "Phoenix Down" in candidates
        assert "Chrono Trigger" in candidates
        assert "Iron Sword" in candidates
        assert "Fire Arrow" in candidates

    def test_extract_candidates_auto_multilingual(self):
        text = "Equip Iron Sword and use ポーション with ブレイブ・ハート!"
        candidates = extract_candidates(text, lang="auto")
        assert "Iron Sword" in candidates
        assert "ポーション" in candidates
        assert "ブレイブ・ハート" in candidates

    def test_extract_candidates_deduplication(self):
        text = "ポーション, ポーション and Potion, Phoenix Down and Phoenix Down."
        candidates = extract_candidates(text, lang="auto")
        assert candidates.count("ポーション") == 1
        assert candidates.count("Phoenix Down") == 1

    def test_extract_halfwidth_katakana_candidates(self):
        text = "ﾎﾟｰｼｮﾝ and ｴｸｽｶﾘﾊﾞｰ are classic items."
        candidates = extract_candidates(text, lang="ja")
        assert "ﾎﾟｰｼｮﾝ" in candidates
        assert "ｴｸｽｶﾘﾊﾞｰ" in candidates

    def test_extract_candidates_empty_or_no_match(self):
        assert extract_candidates("", lang="auto") == []
        assert extract_candidates("hello world normal text", lang="ja") == []


class TestComplianceChecking:
    def test_compliance_pass_exact(self):
        g = Glossary()
        g.add_term("Phoenix Down", "Перо феникса")
        g.add_term("Potion", "Зелье")

        src = "Use a Phoenix Down and a Potion right now!"
        dst = "Используй Перо феникса и Зелье прямо сейчас!"

        warnings = g.check_compliance(src, dst)
        assert warnings == []

    def test_compliance_pass_case_insensitive_russian(self):
        g = Glossary()
        g.add_term("Potion", "Зелье")

        src = "Take the Potion."
        dst = "Возьми это зелье."

        warnings = g.check_compliance(src, dst)
        assert warnings == []

    def test_compliance_violation_missing_term(self):
        g = Glossary()
        g.add_term("Phoenix Down", "Перо феникса")

        src = "Use a Phoenix Down on Crono!"
        dst = "Используй хвост феникса на Кроно!"  # Incorrect translation

        warnings = g.check_compliance(src, dst)
        assert len(warnings) == 1
        assert warnings[0]["source_term"] == "Phoenix Down"
        assert warnings[0]["expected_ru"] == "Перо феникса"
        assert "expected" in warnings[0]["message"].lower() or "not found" in warnings[0]["message"].lower()

    def test_compliance_violation_multiple_terms(self):
        g = Glossary()
        g.add_term("Iron Sword", "Железный меч", category="equipment")
        g.add_term("Fire Arrow", "Огненная стрела", category="skill")

        src = "He equipped Iron Sword and cast Fire Arrow."
        dst = "Он вооружился клинком и метнул огонь."  # Both terms missed

        warnings = g.check_compliance(src, dst)
        assert len(warnings) == 2
        terms_flagged = [w["source_term"] for w in warnings]
        assert "Iron Sword" in terms_flagged
        assert "Fire Arrow" in terms_flagged

    def test_compliance_japanese_source(self):
        g = Glossary()
        g.add_term("ポーション", "Зелье", source_lang="ja")

        src_pass = "ポーションを使え。"
        dst_pass = "Используй Зелье."
        assert g.check_compliance(src_pass, dst_pass) == []

        src_fail = "ポーションを使え。"
        dst_fail = "Используй эликсир."
        warnings = g.check_compliance(src_fail, dst_fail)
        assert len(warnings) == 1
        assert warnings[0]["source_term"] == "ポーション"
        assert warnings[0]["expected_ru"] == "Зелье"

    def test_compliance_standalone_function(self):
        g = Glossary()
        g.add_term("Excalibur", "Экскалибур")

        warnings = check_compliance("Found Excalibur!", "Нашел меч!", glossary=g)
        assert len(warnings) == 1
        assert warnings[0]["source_term"] == "Excalibur"

    def test_compliance_cyrillic_stem_boundary_no_false_positives(self):
        g = Glossary()
        g.add_term("Potion", "Зелье")

        src = "Drink the Potion."

        # 'зеленый' should not falsely satisfy 'Зелье'
        warnings_zeleny = g.check_compliance(src, "Вокруг зеленый луг.")
        assert len(warnings_zeleny) == 1
        assert warnings_zeleny[0]["source_term"] == "Potion"

        # 'безземелье' should not falsely satisfy 'Зелье'
        warnings_bez = g.check_compliance(src, "Кругом царило безземелье.")
        assert len(warnings_bez) == 1

        # Valid declensions should pass
        assert g.check_compliance(src, "Выпей немного зелья.") == []
        assert g.check_compliance(src, "Пользуйся этим зельем.") == []


class TestCliInterface:
    def test_cli_add_and_search(self, tmp_path):
        glossary_file = tmp_path / "cli_glossary.json"

        # CLI add
        ret_add = main([
            "add",
            "--glossary", str(glossary_file),
            "--source", "Chrono Trigger",
            "--ru", "Хроно Триггер",
            "--category", "system",
            "--gender", "masculine",
            "--notes", "Game Title",
        ])
        assert ret_add == 0
        assert glossary_file.exists()

        # CLI search
        ret_search = main([
            "search", "Chrono",
            "--glossary", str(glossary_file),
            "--format", "json",
        ])
        assert ret_search == 0

        # CLI search with --query flag
        ret_query_flag = main([
            "search",
            "--glossary", str(glossary_file),
            "--query", "Chrono",
            "--format", "json",
        ])
        assert ret_query_flag == 0

        # CLI list subcommand
        ret_list_tsv = main([
            "list",
            "--glossary", str(glossary_file),
            "--format", "tsv",
        ])
        assert ret_list_tsv == 0

        ret_list_json = main([
            "list",
            "--glossary", str(glossary_file),
            "--format", "json",
        ])
        assert ret_list_json == 0

    def test_cli_extract(self, capsys):
        ret = main([
            "extract",
            "ポーション and Phoenix Down",
            "--lang", "auto",
            "--format", "json",
        ])
        assert ret == 0
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert "ポーション" in data
        assert "Phoenix Down" in data

    def test_cli_audit_pass(self, tmp_path):
        glossary_file = tmp_path / "audit_glossary.json"
        g = Glossary()
        g.add_term("Iron Sword", "Железный меч")
        g.save_file(str(glossary_file))

        ret = main([
            "audit",
            "--glossary", str(glossary_file),
            "--source", "Take the Iron Sword.",
            "--target", "Возьми Железный меч.",
        ])
        assert ret == 0

    def test_cli_audit_fail(self, tmp_path):
        glossary_file = tmp_path / "audit_glossary.json"
        g = Glossary()
        g.add_term("Iron Sword", "Железный меч")
        g.save_file(str(glossary_file))

        ret = main([
            "audit",
            "--glossary", str(glossary_file),
            "--source", "Take the Iron Sword.",
            "--target", "Возьми стальной клинок.",
        ])
        assert ret == 1

    def test_cli_file_based_audit(self, tmp_path):
        glossary_file = tmp_path / "audit_glossary.json"
        g = Glossary()
        g.add_term("Phoenix Down", "Перо феникса")
        g.save_file(str(glossary_file))

        src_file = tmp_path / "source.txt"
        tgt_file = tmp_path / "target.txt"

        src_file.write_text("Use Phoenix Down!", encoding="utf-8")
        tgt_file.write_text("Используй Перо феникса!", encoding="utf-8")

        ret = main([
            "audit",
            "--glossary", str(glossary_file),
            "--source", str(src_file),
            "--target", str(tgt_file),
        ])
        assert ret == 0

    def test_cli_missing_glossary_exits_with_error(self):
        ret = main([
            "audit",
            "--glossary", "nonexistent_glossary.json",
            "--source", "Hello",
            "--target", "Привет",
        ])
        assert ret == 1
