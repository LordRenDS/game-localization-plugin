#!/usr/bin/env python3
"""Game Localization Glossary Management & Compliance Engine.

Supports JSON and TSV glossary tables, candidate term extraction for Japanese
(Katakana) and English (Capitalized entities), term lookup, and translation compliance audits.
"""

import argparse
import csv
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union


# Stop words for English candidate term extraction to filter out sentence starters
ENGLISH_STOP_WORDS = {
    "A", "About", "Above", "After", "Again", "Against", "All", "Also", "Am", "An",
    "And", "Any", "Are", "Aren't", "As", "At", "Be", "Because", "Been", "Before",
    "Being", "Below", "Between", "Both", "But", "By", "Can", "Cannot", "Can't",
    "Could", "Couldn't", "Did", "Didn't", "Do", "Does", "Doesn't", "Doing", "Don't",
    "Down", "During", "Each", "Few", "For", "From", "Further", "Had", "Hadn't",
    "Has", "Hasn't", "Have", "Haven't", "Having", "He", "He'd", "He'll", "He's",
    "Her", "Here", "Here's", "Hers", "Herself", "Him", "Himself", "His", "How",
    "How's", "I", "I'd", "I'll", "I'm", "I've", "If", "In", "Into", "Is", "Isn't",
    "It", "It's", "Its", "Itself", "Just", "Let's", "Me", "More", "Most", "Mustn't",
    "My", "Myself", "No", "Nor", "Not", "Now", "Of", "Off", "On", "Once", "Only",
    "Or", "Other", "Ought", "Our", "Ours", "Ourselves", "Out", "Over", "Own",
    "Same", "Shan't", "She", "She'd", "She'll", "She's", "Should", "Shouldn't",
    "So", "Some", "Such", "Than", "That", "That's", "The", "Their", "Theirs",
    "Them", "Themselves", "Then", "There", "There's", "These", "They", "They'd",
    "They'll", "They're", "They've", "This", "Those", "Through", "To", "Too",
    "Under", "Until", "Up", "Very", "Was", "Wasn't", "We", "We'd", "We'll", "We're",
    "We've", "Were", "Weren't", "What", "What's", "When", "When's", "Where",
    "Where's", "Which", "While", "Who", "Who's", "Whom", "Why", "Why's", "With",
    "Won't", "Would", "Wouldn't", "You", "You'd", "You'll", "You're", "You've",
    "Your", "Yours", "Yourself", "Yourselves", "Take", "Use", "Equip", "Found",
    "Cast", "Get", "Got", "Obtained", "Defeat",
}


class Glossary:
    """Manages project glossaries with import/export, search, and compliance auditing."""

    def __init__(self, path: Optional[str] = None):
        self.terms: List[Dict[str, str]] = []
        if path:
            self.load_file(path)

    def load_file(self, path: str, append: bool = False) -> None:
        """Loads glossary terms from a JSON or TSV file.

        Args:
            path: Path to the glossary file.
            append: If True, appends terms instead of replacing existing ones.

        Raises:
            FileNotFoundError: If the specified file does not exist.
            ValueError: If the file content is malformed or unparseable.
        """
        file_path = Path(path)
        if not file_path.is_file():
            raise FileNotFoundError(f"Glossary file not found: {path}")

        try:
            content = file_path.read_text(encoding="utf-8-sig")
        except Exception as e:
            raise ValueError(f"Failed to read file {path}: {e}") from e

        new_terms: List[Dict[str, str]] = []
        ext = file_path.suffix.lower()

        if ext == ".json":
            try:
                data = json.loads(content)
            except Exception as e:
                raise ValueError(f"Malformed JSON in glossary file {path}: {e}") from e

            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict) and "source" in item and "ru" in item:
                        new_terms.append(self._normalize_entry(item))
            elif isinstance(data, dict):
                if "terms" in data and isinstance(data["terms"], list):
                    for item in data["terms"]:
                        if isinstance(item, dict) and "source" in item and "ru" in item:
                            new_terms.append(self._normalize_entry(item))
                else:
                    for src, val in data.items():
                        if isinstance(val, dict):
                            entry = dict(val)
                            entry["source"] = src
                            new_terms.append(self._normalize_entry(entry))
                        else:
                            new_terms.append(self._normalize_entry({"source": src, "ru": str(val)}))
            else:
                raise ValueError(f"Unsupported JSON format in {path}")
        else:
            # TSV / CSV parsing
            delimiter = "\t" if ext == ".tsv" or "\t" in content else ","
            try:
                lines = [line for line in content.splitlines() if line.strip()]
                if not lines:
                    new_terms = []
                else:
                    reader = csv.reader(lines, delimiter=delimiter)
                    rows = list(reader)
                    if not rows:
                        new_terms = []
                    else:
                        first_row = [c.strip().lower() for c in rows[0]]
                        has_header = "source" in first_row or "термин" in first_row or "ru" in first_row
                        if has_header:
                            header_map: Dict[str, int] = {}
                            for idx, col in enumerate(first_row):
                                if col in ("source", "термин", "src", "en", "ja"):
                                    header_map["source"] = idx
                                elif col in ("ru", "перевод", "target", "rus"):
                                    header_map["ru"] = idx
                                elif col in ("category", "категория", "type"):
                                    header_map["category"] = idx
                                elif col in ("gender", "род"):
                                    header_map["gender"] = idx
                                elif col in ("notes", "примечания", "note"):
                                    header_map["notes"] = idx
                                elif col in ("source_lang", "lang"):
                                    header_map["source_lang"] = idx

                            for row in rows[1:]:
                                if not row:
                                    continue
                                src_idx = header_map.get("source")
                                ru_idx = header_map.get("ru")
                                if src_idx is not None and ru_idx is not None and src_idx < len(row) and ru_idx < len(row):
                                    cat_val = row[header_map["category"]].strip() if "category" in header_map and header_map["category"] < len(row) else ""
                                    gen_val = row[header_map["gender"]].strip() if "gender" in header_map and header_map["gender"] < len(row) else ""
                                    notes_val = row[header_map["notes"]].strip() if "notes" in header_map and header_map["notes"] < len(row) else ""
                                    lang_val = row[header_map["source_lang"]].strip() if "source_lang" in header_map and header_map["source_lang"] < len(row) else ""
                                    entry = {
                                        "source": row[src_idx].strip(),
                                        "ru": row[ru_idx].strip(),
                                        "category": cat_val or "general",
                                        "gender": gen_val or "neutral",
                                        "notes": notes_val,
                                        "source_lang": lang_val or "en",
                                    }
                                    if entry["source"] and entry["ru"]:
                                        new_terms.append(entry)
                        else:
                            # Positional columns: 0=source, 1=ru, 2=category, 3=gender, 4=notes, 5=source_lang
                            for row in rows:
                                if len(row) >= 2:
                                    entry = {
                                        "source": row[0].strip(),
                                        "ru": row[1].strip(),
                                        "category": (row[2].strip() if len(row) > 2 else "") or "general",
                                        "gender": (row[3].strip() if len(row) > 3 else "") or "neutral",
                                        "notes": row[4].strip() if len(row) > 4 else "",
                                        "source_lang": (row[5].strip() if len(row) > 5 else "") or "en",
                                    }
                                    if entry["source"] and entry["ru"]:
                                        new_terms.append(entry)
            except Exception as e:
                raise ValueError(f"Failed to parse TSV/CSV glossary in {path}: {e}") from e

        if not append:
            self.terms = []

        for term in new_terms:
            self.add_term(
                source=term["source"],
                ru=term["ru"],
                category=term.get("category", "general"),
                gender=term.get("gender", "neutral"),
                notes=term.get("notes", ""),
                source_lang=term.get("source_lang", "en"),
            )

    def save_file(self, path: str, format: Optional[str] = None) -> None:
        """Saves current glossary terms to a JSON or TSV file.

        Args:
            path: Target file path.
            format: Explicit format ('json' or 'tsv'). If None, derived from path extension.
        """
        file_path = Path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        target_format = format.lower() if format else ("tsv" if file_path.suffix.lower() == ".tsv" else "json")

        if target_format == "tsv":
            headers = ["source", "ru", "category", "gender", "notes", "source_lang"]
            rows = [headers]
            for term in self.terms:
                rows.append([
                    term.get("source", ""),
                    term.get("ru", ""),
                    term.get("category", "general"),
                    term.get("gender", "neutral"),
                    term.get("notes", ""),
                    term.get("source_lang", "en"),
                ])
            with open(file_path, "w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f, delimiter="\t")
                writer.writerows(rows)
        else:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(self.terms, f, ensure_ascii=False, indent=2)
                f.write("\n")

    def add_term(
        self,
        source: str,
        ru: str,
        category: str = "general",
        gender: str = "neutral",
        notes: str = "",
        source_lang: str = "en",
    ) -> bool:
        """Adds or updates a term in the glossary.

        Args:
            source: Source language term.
            ru: Russian translation.
            category: Semantic category (character, location, item, skill, system).
            gender: Grammatical gender (masculine, feminine, neuter, neutral).
            notes: Translator notes.
            source_lang: Source language code ('en', 'ja', etc.).

        Returns:
            True if term was successfully added or updated, False if invalid.
        """
        if not source or not str(source).strip() or not ru or not str(ru).strip():
            return False

        src_clean = str(source).strip()
        ru_clean = str(ru).strip()
        cat_clean = str(category).strip() if category and str(category).strip() else "general"
        gen_clean = str(gender).strip() if gender and str(gender).strip() else "neutral"
        notes_clean = str(notes).strip() if notes else ""
        lang_clean = str(source_lang).strip() if source_lang and str(source_lang).strip() else "en"

        for term in self.terms:
            if term["source"] == src_clean and term.get("source_lang", "en") == lang_clean:
                term["ru"] = ru_clean
                term["category"] = cat_clean
                term["gender"] = gen_clean
                term["notes"] = notes_clean
                return True

        self.terms.append({
            "source": src_clean,
            "ru": ru_clean,
            "category": cat_clean,
            "gender": gen_clean,
            "notes": notes_clean,
            "source_lang": lang_clean,
        })
        return True

    def lookup(
        self,
        term: str,
        lang: str = "auto",
        case_sensitive: bool = False,
        exact: bool = True,
    ) -> List[Dict[str, str]]:
        """Looks up a term in the glossary.

        Args:
            term: Query string.
            lang: Language to match ('auto', 'en', 'ja', 'ru').
            case_sensitive: Whether to perform case-sensitive comparison.
            exact: If True, matches exact term; if False, performs substring matching.

        Returns:
            List of matching term entries.
        """
        if not term:
            return []

        query = term if case_sensitive else term.lower()
        results: List[Dict[str, str]] = []

        for entry in self.terms:
            targets: List[str] = []
            source_lang = entry.get("source_lang", "en")

            if lang == "auto":
                targets = [entry["source"], entry["ru"]]
            elif lang == "ru":
                targets = [entry["ru"]]
            elif lang in ("en", "ja"):
                if source_lang == lang:
                    targets = [entry["source"]]
            else:
                targets = [entry["source"], entry["ru"]]

            matched = False
            for target in targets:
                val = target if case_sensitive else target.lower()
                if exact:
                    if val == query:
                        matched = True
                        break
                else:
                    if query in val:
                        matched = True
                        break

            if matched:
                results.append(entry)

        return results

    def extract_candidates(self, text: str, lang: str = "auto") -> List[str]:
        """Extracts candidate terms from text."""
        return extract_candidates(text, lang=lang)

    def check_compliance(self, source_text: str, ru_text: str) -> List[Dict[str, Any]]:
        """Checks Russian translation compliance against known glossary terms."""
        return check_compliance(source_text, ru_text, glossary=self)

    def _normalize_entry(self, raw: Dict[str, Any]) -> Dict[str, str]:
        return {
            "source": str(raw.get("source", "")).strip(),
            "ru": str(raw.get("ru", "")).strip(),
            "category": str(raw.get("category", "general")).strip(),
            "gender": str(raw.get("gender", "neutral")).strip(),
            "notes": str(raw.get("notes", "")).strip(),
            "source_lang": str(raw.get("source_lang", "en")).strip(),
        }

    def __len__(self) -> int:
        return len(self.terms)

    def __iter__(self):
        return iter(self.terms)


def extract_candidates(text: str, lang: str = "auto") -> List[str]:
    """Extracts candidate glossary terms from game text.

    Supports:
    - Japanese Katakana chains (Unicode \u30A0-\u30FF, middle dot ・, long vowel ー).
    - English capitalized entity phrases ('Phoenix Down', 'Chrono Trigger', 'Iron Sword').

    Args:
        text: Source text to extract candidates from.
        lang: Target language filter ('auto', 'ja', 'en').

    Returns:
        Ordered list of unique candidate strings.
    """
    if not text or not str(text).strip():
        return []

    candidates: List[Tuple[int, str]] = []

    # 1. Japanese Katakana extraction (Fullwidth \u30A0-\u30FF and Halfwidth \uFF65-\uFF9F)
    if lang in ("auto", "ja"):
        katakana_pattern = re.compile(r'[\u30A0-\u30FF\uFF65-\uFF9F]+')
        for match in katakana_pattern.finditer(text):
            tok = match.group(0).lstrip("ーｰ").strip("・･")
            if len(tok) >= 2:
                candidates.append((match.start(), tok))

    # 2. English entity phrases extraction
    if lang in ("auto", "en"):
        leading_ignore = {
            "A", "An", "The", "This", "That", "These", "Those",
            "I", "You", "He", "She", "It", "We", "They",
            "Equip", "Use", "Take", "Cast", "Found", "Get", "Got", "Obtained", "Defeat",
            "Press", "Select", "Choose", "Buy", "Sell", "Attack", "Defend", "Escape",
        }
        # Multi-word title case phrases (e.g. Phoenix Down, Chrono Trigger, Iron Sword)
        phrase_pattern = re.compile(r"\b[A-Z][a-zA-Z0-9]*(?:[-'][a-zA-Z0-9]+)?(?:\s+[A-Z][a-zA-Z0-9]*(?:[-'][a-zA-Z0-9]+)?)+\b")
        matched_spans: List[Tuple[int, int]] = []
        for match in phrase_pattern.finditer(text):
            tok = match.group(0).strip()
            words = tok.split()
            while words and words[0] in leading_ignore:
                words.pop(0)
            if len(words) >= 2:
                phrase = " ".join(words)
                candidates.append((match.start(), phrase))
                matched_spans.append((match.start(), match.end()))
            elif len(words) == 1 and words[0] not in ENGLISH_STOP_WORDS:
                candidates.append((match.start(), words[0]))
                matched_spans.append((match.start(), match.end()))

        # Single-word proper entities not inside multi-word phrases and not stopwords
        single_pattern = re.compile(r'\b[A-Z][a-zA-Z0-9]{2,}\b')
        for match in single_pattern.finditer(text):
            start, end = match.start(), match.end()
            tok = match.group(0).strip()
            # If inside an already matched phrase, skip
            if any(s <= start and end <= e for s, e in matched_spans):
                continue
            if tok not in ENGLISH_STOP_WORDS:
                candidates.append((start, tok))

    # Sort candidates by their appearance index in text
    candidates.sort(key=lambda x: x[0])

    # Deduplicate while preserving order
    seen = set()
    result: List[str] = []
    for _, term in candidates:
        if term not in seen:
            seen.add(term)
            result.append(term)

    return result


def _matches_target_translation(expected_ru: str, target_text: str) -> bool:
    """Verifies whether expected Russian translation is present in target text."""
    expected = expected_ru.strip().lower()
    target = target_text.lower()
    if not target or not expected:
        return False

    # 1. Exact phrase / word match with word boundary checking
    phrase_pattern = re.compile(
        rf"(?<![а-яёa-z0-9]){re.escape(expected)}(?![а-яёa-z0-9])",
        re.IGNORECASE,
    )
    if phrase_pattern.search(target):
        return True

    # 2. Token-level inflection / declension matching for single Russian words
    words = expected.split()
    if len(words) == 1 and len(expected) >= 4 and re.match(r"^[а-яё]+$", expected):
        stem = expected.rstrip("аеёиоуыэюяьй")
        if len(stem) >= 3:
            # Word boundary check for Cyrillic: must start and end at Cyrillic word boundaries
            word_pattern = re.compile(
                rf"(?<![а-яё]){re.escape(stem)}[а-яё]*(?![а-яё])",
                re.IGNORECASE,
            )
            valid_endings = {
                "", "а", "я", "у", "ю", "ом", "ем", "ём", "е", "и", "ы",
                "ой", "ей", "ью", "ов", "ев", "ам", "ям", "ами", "ями",
                "ах", "ях", "о", "ь", "ья", "ьев", "ьям", "ьями", "ьях",
                "ьем", "ьём", "ье", "ью",
            }
            for m in word_pattern.finditer(target):
                matched_word = m.group(0).lower()
                suffix = matched_word[len(stem):]
                if suffix in valid_endings:
                    return True

    return False


def check_compliance(
    source_text: str,
    ru_text: str,
    glossary: Optional[Union[Glossary, List[Dict[str, str]]]] = None,
) -> List[Dict[str, Any]]:
    """Checks whether glossary terms in source text are correctly translated in ru_text.

    Args:
        source_text: Source dialogue or script text.
        ru_text: Translated Russian dialogue or script text.
        glossary: Glossary instance or list of term dictionaries.

    Returns:
        List of compliance violation warning dictionaries.
    """
    if glossary is None:
        return []

    terms = glossary.terms if isinstance(glossary, Glossary) else glossary
    if not terms or not source_text:
        return []

    # Sort terms by length descending to match longer multi-word terms first
    sorted_terms = sorted(terms, key=lambda t: len(t.get("source", "")), reverse=True)

    matched_spans: List[Tuple[int, int]] = []
    violations: List[Dict[str, Any]] = []

    for term in sorted_terms:
        source_term = term.get("source", "").strip()
        expected_ru = term.get("ru", "").strip()
        if not source_term or not expected_ru:
            continue

        # Check if source_term is in source_text
        is_ascii_word = bool(re.match(r'^[a-zA-Z0-9\s\'-]+$', source_term))
        if is_ascii_word:
            pattern = re.compile(r'\b' + re.escape(source_term) + r'\b', re.IGNORECASE)
        else:
            pattern = re.compile(re.escape(source_term), re.IGNORECASE)

        found_in_source = False
        for match in pattern.finditer(source_text):
            start, end = match.start(), match.end()
            # If this span is already inside an existing longer matched term, skip
            if any(s <= start and end <= e for s, e in matched_spans):
                continue
            matched_spans.append((start, end))
            found_in_source = True

        if not found_in_source:
            continue

        # Check if expected Russian translation exists in ru_text
        if not _matches_target_translation(expected_ru, ru_text):
            violations.append({
                "term": source_term,
                "source_term": source_term,
                "expected_ru": expected_ru,
                "expected": expected_ru,
                "category": term.get("category", "general"),
                "message": f"Glossary term '{source_term}' expected translation '{expected_ru}' not found in target text",
                "details": term,
            })

    return violations


def _format_table(rows: List[Dict[str, Any]], columns: List[str]) -> str:
    """Renders tabular data as aligned text."""
    if not rows:
        return "No entries."

    widths = {col: max(len(col), max(len(str(r.get(col, ""))) for r in rows)) for col in columns}
    header_line = " | ".join(col.ljust(widths[col]) for col in columns)
    sep_line = "-+-".join("-" * widths[col] for col in columns)
    lines = [header_line, sep_line]
    for r in rows:
        lines.append(" | ".join(str(r.get(col, "")).ljust(widths[col]) for col in columns))
    return "\n".join(lines)


def main(argv: Optional[List[str]] = None) -> int:
    """CLI entrypoint for glossary management and compliance audit."""
    parser = argparse.ArgumentParser(
        description="Game localization glossary management and candidate extraction engine"
    )
    subparsers = parser.add_subparsers(dest="subcommand", help="Subcommand to execute")

    # 1. search
    search_p = subparsers.add_parser("search", help="Search for terms in glossary")
    search_p.add_argument("query", nargs="?", default="", help="Term or keyword to search")
    search_p.add_argument("--query", "-q", dest="query_opt", default="", help="Term or keyword to search")
    search_p.add_argument("--term", "-t", dest="term_opt", default="", help="Term or keyword to search")
    search_p.add_argument("--glossary", "-g", required=True, help="Path to glossary file")
    search_p.add_argument("--lang", "-l", default="auto", choices=["auto", "en", "ja", "ru"], help="Language filter")
    search_p.add_argument("--case-sensitive", "-c", action="store_true", help="Case-sensitive search")
    search_p.add_argument("--exact", action="store_true", help="Require exact term match")
    search_p.add_argument("--format", "-f", default="table", choices=["table", "json", "tsv"], help="Output format")

    # 2. list
    list_p = subparsers.add_parser("list", help="List all terms in glossary")
    list_p.add_argument("--glossary", "-g", required=True, help="Path to glossary file")
    list_p.add_argument("--format", "-f", default="table", choices=["table", "json", "tsv"], help="Output format")

    # 3. add
    add_p = subparsers.add_parser("add", help="Add or update a term in glossary")
    add_p.add_argument("--glossary", "-g", required=True, help="Path to glossary file")
    add_p.add_argument("--source", "-s", required=True, help="Source language term")
    add_p.add_argument("--ru", "-r", required=True, help="Russian translation")
    add_p.add_argument("--category", default="general", help="Category (item, character, etc.)")
    add_p.add_argument("--gender", default="neutral", help="Grammatical gender")
    add_p.add_argument("--notes", default="", help="Translator notes")
    add_p.add_argument("--lang", "-l", default="en", help="Source language (en, ja, etc.)")

    # 4. extract
    extract_p = subparsers.add_parser("extract", help="Extract candidate terms from game text")
    extract_p.add_argument("text", nargs="?", default="", help="Text to extract candidates from")
    extract_p.add_argument("--text", dest="text_opt", default="", help="Text to extract candidates from")
    extract_p.add_argument("--source", "-s", help="Source file or text to extract candidates from")
    extract_p.add_argument("--lang", "-l", default="auto", choices=["auto", "en", "ja"], help="Candidate language")
    extract_p.add_argument("--format", "-f", default="json", choices=["json", "tsv", "table"], help="Output format")
    extract_p.add_argument("--output", "-o", help="Optional path to write extracted candidates")

    # 5. audit
    audit_p = subparsers.add_parser("audit", help="Audit translation compliance against glossary")
    audit_p.add_argument("--glossary", "-g", required=True, help="Path to glossary file")
    audit_p.add_argument("--source", "-s", required=True, help="Source text or file path")
    audit_p.add_argument("--target", "-t", required=True, help="Target (RU) text or file path")
    audit_p.add_argument("--format", "-f", default="table", choices=["table", "json", "tsv"], help="Output format")

    args = parser.parse_args(argv)
    if not args.subcommand:
        parser.print_help()
        return 1

    try:
        if args.subcommand == "search":
            glossary = Glossary()
            glossary.load_file(args.glossary)
            query = args.query_opt or args.term_opt or args.query
            if query:
                results = glossary.lookup(
                    query,
                    lang=args.lang,
                    case_sensitive=args.case_sensitive,
                    exact=args.exact if args.exact else False,
                )
            else:
                results = glossary.terms

            if args.format == "json":
                print(json.dumps(results, ensure_ascii=False, indent=2))
            elif args.format == "tsv":
                headers = ["source", "ru", "category", "gender", "notes", "source_lang"]
                print("\t".join(headers))
                for item in results:
                    print("\t".join(str(item.get(h, "")) for h in headers))
            else:
                cols = ["source", "ru", "category", "gender", "source_lang"]
                print(_format_table(results, cols))
            return 0

        elif args.subcommand == "list":
            glossary = Glossary()
            glossary.load_file(args.glossary)
            results = glossary.terms

            if args.format == "json":
                print(json.dumps(results, ensure_ascii=False, indent=2))
            elif args.format == "tsv":
                headers = ["source", "ru", "category", "gender", "notes", "source_lang"]
                print("\t".join(headers))
                for item in results:
                    print("\t".join(str(item.get(h, "")) for h in headers))
            else:
                cols = ["source", "ru", "category", "gender", "source_lang"]
                print(_format_table(results, cols))
            return 0

        elif args.subcommand == "add":
            glossary = Glossary()
            if os.path.isfile(args.glossary):
                glossary.load_file(args.glossary)

            added = glossary.add_term(
                source=args.source,
                ru=args.ru,
                category=args.category,
                gender=args.gender,
                notes=args.notes,
                source_lang=args.lang,
            )
            if not added:
                sys.stderr.write("Error: Failed to add term (empty source or translation).\n")
                return 1

            glossary.save_file(args.glossary)
            print(f"Added term: '{args.source}' -> '{args.ru}' in {args.glossary}")
            return 0

        elif args.subcommand == "extract":
            input_text = ""
            if args.source:
                if os.path.isfile(args.source):
                    input_text = Path(args.source).read_text(encoding="utf-8")
                else:
                    input_text = args.source
            elif args.text_opt or args.text:
                input_text = args.text_opt or args.text
            else:
                if not sys.stdin.isatty():
                    input_text = sys.stdin.read()

            if not input_text:
                sys.stderr.write("Error: No input text provided for candidate extraction.\n")
                return 1

            candidates = extract_candidates(input_text, lang=args.lang)

            if args.output:
                out_path = Path(args.output)
                out_path.parent.mkdir(parents=True, exist_ok=True)
                if args.format == "json":
                    out_path.write_text(json.dumps(candidates, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                elif args.format == "tsv":
                    out_path.write_text("\n".join(candidates) + "\n", encoding="utf-8")
                else:
                    out_path.write_text("\n".join(f"- {c}" for c in candidates) + "\n", encoding="utf-8")
            else:
                if args.format == "json":
                    print(json.dumps(candidates, ensure_ascii=False, indent=2))
                elif args.format == "tsv":
                    for c in candidates:
                        print(c)
                else:
                    for c in candidates:
                        print(f"- {c}")
            return 0

        elif args.subcommand == "audit":
            glossary = Glossary()
            glossary.load_file(args.glossary)

            source_text = Path(args.source).read_text(encoding="utf-8") if os.path.isfile(args.source) else args.source
            target_text = Path(args.target).read_text(encoding="utf-8") if os.path.isfile(args.target) else args.target

            violations = glossary.check_compliance(source_text, target_text)

            if violations:
                if args.format == "json":
                    print(json.dumps(violations, ensure_ascii=False, indent=2))
                elif args.format == "tsv":
                    headers = ["source_term", "expected_ru", "category", "message"]
                    print("\t".join(headers))
                    for v in violations:
                        print("\t".join(str(v.get(h, "")) for h in headers))
                else:
                    cols = ["source_term", "expected_ru", "category", "message"]
                    print("Terminology Compliance Violations Detected:")
                    print(_format_table(violations, cols))
                return 1
            else:
                print("Glossary compliance check passed: no violations detected.")
                return 0

    except FileNotFoundError as e:
        sys.stderr.write(f"File error: {e}\n")
        return 1
    except ValueError as e:
        sys.stderr.write(f"Validation error: {e}\n")
        return 1
    except Exception as e:
        sys.stderr.write(f"Unexpected error: {e}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
