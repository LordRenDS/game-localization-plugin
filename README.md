# Game Localization & Text Engineering Plugin (EN/JA -> RU)

[English](README.md) | [Русский](README.ru.md)

[![Plugin: game-localization-plugin](https://img.shields.io/badge/Antigravity_Plugin-game--localization--plugin-4A90E2.svg)](#)
[![Version: 1.1.0](https://img.shields.io/badge/Version-1.1.0-success.svg)](#)
[![Tests: 114 passed](https://img.shields.io/badge/Tests-114%20passed-brightgreen.svg)](#)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](#)

A professional, production-grade toolkit for Google Antigravity designed for high-fidelity game localization from **Japanese (JA)** and **English (EN)** into **Russian (RU)**.

The plugin provides a unified system combining specialized AI subagents, structured multi-phase workflow skills, global linguistic and engine rules, and deterministic command-line automation tools. It bridges the gap between literary translation excellence (eliminating *переводяз*, realizing *Yakuwarigo*, maintaining authentic dialogue rhythm) and strict low-level game engine engineering (100% control tag parity, byte-exact formatting specifiers, text box layout budgeting, and terminology compliance).

---

## Table of Contents

1. [Features & Capabilities](#features--capabilities)
2. [Plugin Architecture](#plugin-architecture)
3. [Global Operational Rules](#global-operational-rules)
4. [Specialized Subagents](#specialized-subagents)
5. [Workflow Skills](#workflow-skills)
6. [CLI Automation Tools](#cli-automation-tools)
   - [Tag & Layout Validator (`l10n_validator.py`)](#tag--layout-validator-l10n_validatorpy)
   - [Glossary Engine (`glossary_tool.py`)](#glossary-engine-glossary_toolpy)
   - [Cross-Version Alignment Reporter (`version_diff.py`)](#cross-version-alignment-reporter-version_diffpy)
7. [Quickstart & Common Workflows](#quickstart--common-workflows)
8. [Synergy with ROM Hacking](#synergy-with-rom-hacking)
9. [Verification & Testing](#verification--testing)
10. [Installation & Deployment](#installation--deployment)

---

## Features & Capabilities

- **Literary Game Translation (JA/EN -> RU)**: Deep adaptation of Japanese role language (*Yakuwarigo*), age/social registers, keigo formality levels, and English narrative nuance without falling into translationese (*переводяз*).
- **Engine Control Tag Immutability**: Zero-tolerance protection for in-engine opcodes (`{PAGE}`, `{LINE}`, `{COLOR N}`, `{NAME N}`, `{WAIT N}`), printf format specifiers (`%s`, `%d`, `%1$s`, `%.2f`), and escape sequences.
- **Layout Budget & Font Metric Pre-Checks**: Strict per-line character limit enforcement and line-count budgeting preventing dialogue box overflow and UI clipping.
- **Automated Terminology & Lore Management**: Candidate entity extraction from Japanese Katakana chains and English title phrases, bidirectional search, and automated compliance auditing.
- **Multi-Version Comparative Forensics**: Side-by-side script alignment across multiple game releases (e.g., Japanese original, 1990s Western censored releases, modern remakes) to expose cut content, bowdlerization, and mistranslations.
- **Russian Typographical Perfection**: Automated enforcement of Russian typographical conventions, including proper quotation marks («...» / „...“), dialogue em-dashes (—), and consistent orthography with letter *ё*.

---

## Plugin Architecture

```text
game-localization-plugin/
├── plugin.json                              # Antigravity plugin manifest
├── README.md                                # Comprehensive documentation
├── rules/
│   └── AGENTS.md                            # Global localization standards and rules
├── agents/
│   ├── game-translator.md                   # Lead literary translator (JA/EN -> RU)
│   ├── localization-editor.md               # Literary editor, cadence & typography polish
│   ├── glossary-curator.md                  # Lore curator & terminology consistency auditor
│   └── translation-comparator.md            # Multi-version analyst & censorship investigator
├── skills/
│   ├── game-text-translation/
│   │   └── SKILL.md                         # 5-phase dialogue & script translation workflow
│   ├── game-glossary-manager/
│   │   └── SKILL.md                         # Term extraction, curation & audit workflow
│   ├── game-translation-comparator/
│   │   └── SKILL.md                         # Cross-version alignment & synthesis workflow
│   └── game-l10n-qa/
│       └── SKILL.md                         # Automated tag integrity & layout QA workflow
├── scripts/
│   ├── l10n_validator.py                    # Tag parity, layout budget & typography CLI
│   ├── glossary_tool.py                     # Candidate extractor & terminology audit CLI
│   └── version_diff.py                      # Multi-version script alignment & report CLI
└── tests/
    ├── __init__.py
    ├── test_l10n_validator.py               # Unit tests for tag & layout validator
    ├── test_glossary_tool.py                # Unit tests for glossary engine
    └── test_version_diff.py                 # Unit tests for version diff tool
```

---

## Global Operational Rules

When this plugin is active, [rules/AGENTS.md](file:///C:/Users/serge/.gemini/antigravity/scratch/game-localization-plugin/rules/AGENTS.md) enforces mandatory standards across all agents and tasks:

1. **Japanese to Russian (JA -> RU) Standards**:
   - **Yakuwarigo Mapping**: Express character archetypes (samurai, elder, delinquent, ojou-sama, keigo knight) through natural Russian vocabulary, syntax, and cadence rather than artificial phonetic suffixes.
   - **Pronoun Omission**: Natural Russian omits explicit subject pronouns (*«я»*, *«ты»*) when verbal inflection already clarifies the subject. Avoid translating every Japanese pronoun occurrence mechanically.
   - **Polivanov System & Canon Precedence**: Transcribe Japanese names using the Polivanov system, while giving precedence to established official canon and entrenched community consensus.
   - **Furigana & Polysemy**: Examine kanji compounds and furigana double-meanings for intentional subtext.

2. **English to Russian (EN -> RU) Standards**:
   - **Eradication of Translationese**: Remove mechanical calques, especially redundant possessives (*он вынул свой меч* -> *он обнажил меч*) and passive voice constructions (*он был атакован гоблином* -> *на него напал гоблин*).
   - **Context-Sensitive Gaming Disambiguation**: Differentiate ambiguous UI and battle terms (*Miss* -> *Промах* vs *Скучать*; *Back* -> *Назад* vs *Спина*; *Save* -> *Сохранить* vs *Спасти*; *Party* -> *Отряд* vs *Вечеринка*).

3. **Control Code Immutability**:
   - Every format token (`%s`, `%d`, `%1$s`, `%.2f`), engine tag (`{HERO}`, `{COLOR 2}`, `[ITEM %d]`), and escape sequence (`\n`, `\t`) must be preserved identically with matching casing, argument count, and syntax.

4. **Layout Budget & Font Widths**:
   - Russian text naturally expands by 20–35% compared to English or Japanese. Every line must be budgeted to prevent clipping within target dialogue windows (typically 36–42 characters per line, 3–4 lines per box).

---

## Specialized Subagents

The plugin equips Antigravity with four role-tailored subagents:

### 1. `@game-translator` ([agents/game-translator.md](file:///C:/Users/serge/.gemini/antigravity/scratch/game-localization-plugin/agents/game-translator.md))
- **Role**: Senior Literary Game Translator (JA/EN -> RU).
- **Core Function**: Translates game dialogue trees, scenarios, NPC banter, quest logs, and UI menus. Maps Japanese role language (*Yakuwarigo*) and English narrative tone into vivid, character-authentic Russian prose while ensuring 100% control tag parity and layout compliance.
- **Model**: `pro`

### 2. `@localization-editor` ([agents/localization-editor.md](file:///C:/Users/serge/.gemini/antigravity/scratch/game-localization-plugin/agents/localization-editor.md))
- **Role**: Veteran Localization Editor and Stylistic Polish Expert.
- **Core Function**: Polishes draft translations, removes stubborn translationese, adjusts spoken line rhythm for voice acting or rapid reading, resolves dynamic token agreement dilemmas (e.g., gender/case agreements around `{HERO}`), and applies publishing-grade Russian typography (`«...»`, `„...“`, `—`, `ё`).
- **Model**: `pro`

### 3. `@glossary-curator` ([agents/glossary-curator.md](file:///C:/Users/serge/.gemini/antigravity/scratch/game-localization-plugin/agents/glossary-curator.md))
- **Role**: Game Lore Master & Terminology Curator.
- **Core Function**: Scans script corpora to extract candidate terms (Japanese Katakana loanwords, English Title Case entities), categorizes entities (`character`, `location`, `item`, `skill`, `system`), tracks grammatical gender and declension notes, resolves version conflicts, and performs automated consistency audits.
- **Model**: `pro`

### 4. `@translation-comparator` ([agents/translation-comparator.md](file:///C:/Users/serge/.gemini/antigravity/scratch/game-localization-plugin/agents/translation-comparator.md))
- **Role**: Comparative Script Analyst & Localization Historian.
- **Core Function**: Cross-examines multiple script versions (Japanese original, 1990s Western localized/censored versions, modern remakes, community translations), detects bowdlerization and tonal revisions, and synthesizes optimal, canon-accurate Russian adaptations.
- **Model**: `pro`

---

## Workflow Skills

The plugin includes four step-by-step operational skills:

| Skill | Path | Description |
| :--- | :--- | :--- |
| **`game-text-translation`** | [skills/game-text-translation/SKILL.md](file:///C:/Users/serge/.gemini/antigravity/scratch/game-localization-plugin/skills/game-text-translation/SKILL.md) | 5-phase SOP for translating dialogue dumps, UI menus, and quest logs (Format Ingest -> Terminology Retrieval -> Literary Translation -> Pre-Flight QA -> Export). |
| **`game-glossary-manager`** | [skills/game-glossary-manager/SKILL.md](file:///C:/Users/serge/.gemini/antigravity/scratch/game-localization-plugin/skills/game-glossary-manager/SKILL.md) | Standard procedure for terminology lifecycle: candidate extraction, curation, JSON/TSV management, conflict resolution, and automated compliance verification. |
| **`game-translation-comparator`** | [skills/game-translation-comparator/SKILL.md](file:///C:/Users/serge/.gemini/antigravity/scratch/game-localization-plugin/skills/game-translation-comparator/SKILL.md) | SOP for multi-version script alignment, Markdown matrix report generation, divergence taxonomy analysis, and optimal adaptation synthesis. |
| **`game-l10n-qa`** | [skills/game-l10n-qa/SKILL.md](file:///C:/Users/serge/.gemini/antigravity/scratch/game-localization-plugin/skills/game-l10n-qa/SKILL.md) | Comprehensive automated QA workflow validating tag integrity, line lengths, line counts, and Russian typography with CI exit code handling. |

---

## CLI Automation Tools

The plugin includes three standalone Python utilities located in [scripts/](file:///C:/Users/serge/.gemini/antigravity/scratch/game-localization-plugin/scripts/). They can be executed directly from terminal or imported into Python scripts.

### Tag & Layout Validator (`l10n_validator.py`)
Validates that translated files maintain complete tag parity with source files, adhere to line length and line count limits, and conform to Russian typography standards.

```bash
# Basic validation with default thresholds (max 40 chars/line, max 4 lines/box, var-len 8)
python scripts/l10n_validator.py --source source.json --target translated.json

# Custom layout budget constraints with variable token budgeting
python scripts/l10n_validator.py \
  --source en_script.po \
  --target ru_script.po \
  --max-len 36 \
  --max-lines 3 \
  --var-len 10 \
  --var-tokens "{NPC_NAME},{MAP_NAME}"

# JSON report output (useful for CI/CD pipelines)
python scripts/l10n_validator.py --source src.json --target dst.json --json
```

**Key Parameters**:
- `--source`, `-s`: Path to source file (JSON, Gettext PO, or plain text).
- `--target`, `-t`: Path to target translated file.
- `--max-len`, `-l`: Maximum characters per line (default: `40`).
- `--max-lines`, `-m`: Maximum lines per dialogue box (default: `4`).
- `--var-len`: Nominal character reservation for dynamic variable tokens like `{HERO_NAME}` (default: `8`). Set to `0` to treat as zero-width.
- `--var-tokens`: Comma-separated custom tokens to add to variable tokens (e.g. `"{NPC_NAME},{LOCATION}"`).
- `--json`: Output full report as structured JSON.

---

### Glossary Engine (`glossary_tool.py`)
Extracts candidate terms from script dumps, manages bilingual/trilingual glossaries, and audits translated scripts against established project terms.

```bash
# 1. Extract candidate terms from Japanese source
python scripts/glossary_tool.py extract --source script_jp.txt --lang ja

# 2. Extract candidate terms from English source into JSON
python scripts/glossary_tool.py extract --source script_en.json --lang en --format json -o candidates.json

# 3. Add or update term in glossary
python scripts/glossary_tool.py add \
  --glossary project_glossary.json \
  --source "Masamune" \
  --ru "Масамунэ" \
  --category item \
  --gender m \
  --notes "Легендарный меч Гленна"

# 4. Search glossary terms
python scripts/glossary_tool.py search --glossary project_glossary.json --query "Масамунэ"

# 5. List all terms in TSV format
python scripts/glossary_tool.py list --glossary project_glossary.json --format tsv

# 6. Audit translated dialogue against approved glossary terms
python scripts/glossary_tool.py audit \
  --glossary project_glossary.json \
  --source script_en.json \
  --target script_ru.json
```

**Supported Subcommands**:
- `list`: Display all entries in table, JSON, or TSV format.
- `search`: Case-insensitive and substring search across source terms and translations.
- `add`: Add or update an entry with category, gender, and notes.
- `extract`: Automatic extraction of proper names, katakana loanwords, and title phrases.
- `audit`: Verifies that source terms occurring in dialogue are correctly translated in target text, accounting for Russian noun declensions and inflections.

---

### Cross-Version Alignment Reporter (`version_diff.py`)
Aligns 2 to 5 script versions and generates detailed Markdown comparison tables with visual status badges (`[IDENTICAL]`, `[DIVERGENT]`, `[CUT/MISSING]`).

```bash
# Compare Japanese source against 1995 SNES US release and DS re-release
python scripts/version_diff.py \
  --version JP=data/script_jp.json \
  --version SNES=data/script_snes_us.json \
  --version DS=data/script_ds_us.json \
  --divergent-only \
  --output comparison_report.md

# Quick stdout comparison of two files
python scripts/version_diff.py \
  --version Original=jp_dump.txt \
  --version Translated=ru_dump.txt
```

**Key Parameters**:
- `--version NAME=PATH`: Specifies a version name and its file path (supports JSON dict/list, PO, TSV, CSV, or line-based text). Repeat `--version` for each version to align.
- `--divergent-only`: Omits identical records, focusing only on altered or cut lines.
- `--output`, `-o`: File path to write the Markdown report (defaults to stdout).
- `--title`: Custom title for the Markdown report.
- `--max-rows`: Limit the maximum number of rows in the output report.

---

## Quickstart & Common Workflows

### Scenario 1: Translating a Dialogue Scene (JA -> RU)
1. Ingest Japanese dialogue file (e.g., `scene_01_jp.json`).
2. Search relevant character and location terms using `scripts/glossary_tool.py search`.
3. Task `@game-translator` to translate dialogue with awareness of character roles:
   ```text
   Translate scene_01_jp.json into Russian.
   - Preserve all {PAGE}, {LINE}, and {COLOR N} tags exactly.
   - Lucca uses intelligent, energetic conversational speech.
   - Glenn uses dignified knightly diction.
   - Follow project_glossary.json.
   ```
4. Task `@localization-editor` to polish cadence, check agreements, and format quotes.
5. Run automated pre-flight QA:
   ```bash
   python scripts/l10n_validator.py -s scene_01_jp.json -t scene_01_ru.json --max-len 38 --max-lines 3
   ```

### Scenario 2: Investigating 1990s Censorship & Cut Content
1. Prepare raw script files from both versions (`script_jp.json` and `script_us_1995.json`).
2. Generate alignment diff:
   ```bash
   python scripts/version_diff.py \
     --version JP=script_jp.json \
     --version US=script_us_1995.json \
     --divergent-only \
     --output censorship_audit.md
   ```
3. Task `@translation-comparator` to analyze divergent rows:
   ```text
   Review censorship_audit.md. Identify cut religious references, alcohol bowdlerization,
   and character voice distortions. Propose optimal Russian translations reconciling authorial intent.
   ```

### Scenario 3: Curating Project Terminology & Quality Audit
1. Extract candidate terms from source dumps:
   ```bash
   python scripts/glossary_tool.py extract --source main_scenario.json --lang en -o candidates.txt
   ```
2. Task `@glossary-curator` to review candidates, assign Russian translations, categories, and genders.
3. Save terms into `project_glossary.json`.
4. Audit translated scripts before committing:
   ```bash
   python scripts/glossary_tool.py audit -g project_glossary.json -s main_scenario.json -t main_scenario_ru.json
   ```

---

## Synergy with ROM Hacking

This plugin works in direct architectural synergy with ROM hacking toolkits, such as **`nds-romhacking-plugin` v1.1.0+**:

```
┌─────────────────────────────────┐       ┌──────────────────────────────────────┐
│  nds-romhacking-plugin v1.1.0+  │       │       game-localization-plugin       │
│                                 │       │                                      │
│  1. Extract NitroFS / overlays  │       │                                      │
│  2. Generic container parser    │       │                                      │
│     (arbitrary lang_count 1..N, │       │                                      │
│      dynamic \x02 / \x00 delim) │       │                                      │
│  3. Dump dialogue bytecode/JSON │ ────> │  4. Align multi-version scripts      │
│                                 │       │  5. Curate terminology & glossaries  │
│                                 │       │  6. Literary translation (JA/EN->RU) │
│                                 │       │  7. Polish dialogue cadence & rhythm │
│                                 │ <──── │  8. Validate tag integrity & layout  │
│  9. Reinsert localized entries  │       │     (DEFAULT_VARIABLE_TOKENS budget  │
│ 10. Rebuild NFTR font widths    │       │      nominal 8 chars / 30-48px)      │
│ 11. Repack ROM & sign integrity │       │                                      │
└─────────────────────────────────┘       └──────────────────────────────────────┘
```

### Key Integration Points:
- **Generic Binary Text Containers**: `nds-romhacking-plugin` v1.1.0+ supports arbitrary language counts (`lang_count`, from 1 to $N$) and dynamic text delimiters (`\x02` or `\x00`) across diverse commercial NDS titles. `game-localization-plugin` ingests and outputs structured JSON/PO/TXT preserving exact entry keys and multi-language parity.
- **Dynamic Variable Token Budgeting**: Both plugins share the `DEFAULT_VARIABLE_TOKENS` standard (`{HERO_NAME}`, `{PLAYER_NAME}`, `{ITEM_NAME}`, etc.). Rather than stripping tokens as zero-width, the localization validator budgets nominal character envelopes (`--var-len 8`), perfectly aligning with the ROM hacking plugin's proportional NFTR font advance metrics (`DEFAULT_HERO_NAME_WIDTH_PX = 30-48px`) to eliminate runtime dialogue clipping.
- **Zero Bytecode Degradation**: When translated scripts return to the ROM hacking pipeline for binary reinsertion, all engine opcodes, line count limits, and pointer tables remain 100% intact, preventing VM crashes and softlocks on real hardware and emulators.

---

## Verification & Testing

The plugin includes a comprehensive test suite covering all CLI tools and core algorithmic functions:

- **`test_l10n_validator.py`**: Tag extraction, bracket integrity, format specifiers, layout budget calculation, Russian typography detection, and CLI exit codes.
- **`test_glossary_tool.py`**: Term candidate extraction (Katakana, Title Case phrases, halfwidth forms), glossary loading/saving (JSON/TSV), search matching, Russian declension-aware compliance checking, and CLI subcommands.
- **`test_version_diff.py`**: Multi-format loader (JSON dict/list, PO, TSV, CSV, line text), version alignment logic, Markdown table formatting, character escaping, and CLI filtering.

To run the complete test suite:

```bash
pytest tests/ -v
```

All 114 unit tests execute in under 1 second.

---

## Installation & Deployment

To deploy this plugin into your local Antigravity installation:

```bash
# Target directory
$TARGET = "C:\Users\serge\.gemini\config\plugins\game-localization-plugin"

# Copy plugin files
Copy-Item -Path "plugin.json", "README.md" -Destination $TARGET
Copy-Item -Recurse -Path "rules", "agents", "skills", "scripts" -Destination $TARGET
```

Once installed, Antigravity will automatically discover `game-localization-plugin` and make all subagents, skills, rules, and suggested prompts available in your workspace sessions.

---

## Suggested Prompts

You can invoke the plugin immediately with prompts such as:

- *"Translate this game dialogue script from Japanese to Russian preserving tags and character voices"*
- *"Compare the Japanese script against official English release and find cut or altered dialogue"*
- *"Validate translated game text for tag integrity, line length limits, and glossary compliance"*
- *"Extract candidate terminology from this script and build a project glossary"*
