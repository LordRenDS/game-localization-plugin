---
name: game-glossary-manager
description: Standard workflow for creating, maintaining, curating, and auditing game localization project glossaries in JSON and TSV formats with candidate term extraction and grammatical gender management.
---

# Game Glossary Manager Workflow

## Overview

This skill defines the complete methodology for creating, curating, maintaining, and auditing terminology glossaries for game localization projects. Consistent terminology is essential for franchise continuity, lore immersion, and preventing contradictory translations across sprawling RPG scripts, item databases, and UI systems.

The glossary management workflow utilizes `scripts/glossary_tool.py` to extract candidate entities, curate translation equivalents with grammatical metadata, resolve naming conflicts, and audit translated text against approved project terminology.

## When to Use

- Initializing a new terminology glossary for a game project from source script dumps.
- Extracting candidate entities (Japanese Katakana chains, English Title Case nouns) from dialogues and lore logs.
- Adding, updating, or reviewing localized game terms (characters, locations, items, skills, factions).
- Assigning Russian grammatical gender (`masculine`, `feminine`, `neuter`, `plural`) to terms for dynamic text agreement.
- Harmonizing conflicting terminology between different game chapters or translator team members.
- Auditing draft or legacy translations to identify terminology drift or glossary non-compliance.

When NOT to use:
- Performing raw dialogue translation and line-by-line editing (use `game-text-translation`).
- Validating bytecode tags and dialogue line lengths (use `game-l10n-qa`).
- Cross-comparing versions for regional censorship and cut content (use `game-translation-comparator`).

---

## Glossary Data Architecture

Glossaries are stored in either **JSON** or **TSV (Tab-Separated Values)** format. Both formats support UTF-8 encoding (including UTF-8 with BOM) and bidirectional conversion.

### 1. JSON Schema (`glossary.json`)
```json
[
  {
    "source": "Phoenix Down",
    "ru": "Перо феникса",
    "category": "item",
    "gender": "neuter",
    "notes": "Revives KO'd party member with small HP.",
    "source_lang": "en"
  },
  {
    "source": "クロノ",
    "ru": "Кроно",
    "category": "character",
    "gender": "masculine",
    "notes": "Main protagonist of Chrono Trigger.",
    "source_lang": "ja"
  }
]
```

### 2. TSV Schema (`glossary.tsv`)
Header row is mandatory for TSV files:
```tsv
source	ru	category	gender	notes	source_lang
Potion	Зелье	item	neuter	Restores 50 HP	en
Guardia	Гвардия	location	feminine	Kingdom of Guardia	en
マール	Марл	character	feminine	Princess Nadia	ja
```

### Standard Entity Categories
- `character`: Playable characters, companions, NPCs, bosses.
- `location`: Towns, dungeons, continents, landmarks, world map regions.
- `item`: Consumables, key items, crafting ingredients, weapons, armor.
- `skill`: Spells, techniques, abilities, passive perks.
- `enemy`: Standard monsters, beasts, enemy factions.
- `faction`: Guilds, kingdoms, political organizations, religious orders.
- `system`: Menu headers, UI buttons, status conditions, combat mechanics.
- `general`: Recurring lore concepts, cultural terminology.

---

## End-to-End Glossary Lifecycle

```
  ┌────────────────────────────────────────────────────────┐
  │ Step 1: Automated Candidate Term Extraction           │
  │   - Scan JA scripts for Katakana sequences             │
  │   - Scan EN scripts for Title Case entities            │
  └───────────────────────────┬────────────────────────────┘
                              │
  ┌───────────────────────────▼────────────────────────────┐
  │ Step 2: Curation, Canon Check & Linguistic Review      │
  │   - Verify franchise canon vs Polivanov transcription  │
  │   - Assign Russian grammatical gender and notes        │
  └───────────────────────────┬────────────────────────────┘
                              │
  ┌───────────────────────────▼────────────────────────────┐
  │ Step 3: Registering Approved Terms via CLI             │
  │   - Insert terms into JSON / TSV via glossary_tool.py  │
  └───────────────────────────┬────────────────────────────┘
                              │
  ┌───────────────────────────▼────────────────────────────┐
  │ Step 4: Harmonization & Conflict Resolution            │
  │   - Resolve homonyms, polysemous terms, and duplicates │
  └───────────────────────────┬────────────────────────────┘
                              │
  ┌───────────────────────────▼────────────────────────────┐
  │ Step 5: Automated Compliance Auditing                  │
  │   - Scan game scripts for unapproved term translations │
  └────────────────────────────────────────────────────────┘
```

---

### Step 1: Candidate Term Extraction

Extract candidate entities automatically from raw script files or dialogue dumps using `scripts/glossary_tool.py extract`.

#### Japanese Extraction (Katakana Heuristic)
Japanese scripts represent foreign loanwords, fantasy terms, and proper names in Katakana (`[\u30A1-\u30FA\u30FC]+`).
```powershell
# Extract candidate terms from a Japanese script file
python scripts/glossary_tool.py extract --source "data/script_scenario_ja.json" --lang ja --format tsv --output "glossary/candidates_ja.tsv"
```

#### English Extraction (Capitalized Entity Heuristic)
English scripts represent entities as Title Case noun phrases while filtering common English stop words (*The, An, They, After, Defeat, etc.*):
```powershell
# Extract candidate terms from an English script file
python scripts/glossary_tool.py extract --source "data/dialogue_en.json" --lang en --format json --output "glossary/candidates_en.json"
```

#### Inspect Extracted Candidates
```powershell
python scripts/glossary_tool.py search --glossary "glossary/candidates_en.json" --format table
```

---

### Step 2: Curation, Canon Verification & Russian Gender Assignment

Review extracted candidates before adding them to the production glossary:

1. **Franchise Canon vs Transcription Rules**:
   - Always check official franchise localizations first (*Final Fantasy VII*: **Шинра**, not *Синра*; *Chrono Trigger*: **Магл**, not *Магус*).
   - If no established canon exists, apply Polivanov for Japanese names (`し -> си`, `ち -> ти`, `じ -> дзи`).
   - For Katakana European loanwords, translate from the source language (*ミスリル* -> **Мифрил**; *ハイポーション* -> **Хай-зелье / Большое зелье**).

2. **Russian Grammatical Gender Assignment**:
   In Russian, surrounding adjectives and past-tense verbs must agree with the noun's gender. Annotate each noun with its gender in the glossary:
   - `masculine`: *Меч (стальной меч найден)*
   - `feminine`: *Рапира (стальная рапира найдена)*
   - `neuter`: *Зелье (целебное зелье найдено)*
   - `plural`: *Сапоги (скороходные сапоги найдены)*
   - `neutral`: Invariant loanwords or terms requiring context apposition (*«предмет: Эликсир»*).

---

### Step 3: Registering & Updating Terms via CLI

Add curated terms directly into the project glossary using `scripts/glossary_tool.py add`. The command automatically manages file creation, deduplication, and schema formatting.

#### Adding Japanese Terms
```powershell
# Add character
python scripts/glossary_tool.py add --glossary "glossary/game_terms.json" `
  --source "ルッカ" `
  --ru "Лукка" `
  --category "character" `
  --gender "feminine" `
  --lang "ja" `
  --notes "Genius inventor companion."

# Add location
python scripts/glossary_tool.py add --glossary "glossary/game_terms.json" `
  --source "ガルディア王国" `
  --ru "Королевство Гардия" `
  --category "location" `
  --gender "neuter" `
  --lang "ja" `
  --notes "Central medieval kingdom."
```

#### Adding English Terms
```powershell
# Add consumable item
python scripts/glossary_tool.py add --glossary "glossary/game_terms.json" `
  --source "Ether" `
  --ru "Эфир" `
  --category "item" `
  --gender "masculine" `
  --lang "en" `
  --notes "Restores magic points (MP)."

# Add key item
python scripts/glossary_tool.py add --glossary "glossary/game_terms.tsv" `
  --source "Pendant" `
  --ru "Кулон" `
  --category "item" `
  --gender "masculine" `
  --lang "en" `
  --notes "Marle's royal heirloom."
```

---

### Step 4: Harmonization & Conflict Resolution

When multiple translators or legacy scripts produce divergent translations for the same entity, apply this harmonization hierarchy:

```
  ┌────────────────────────────────────────────────────────┐
  │ 1. Official Franchise Canon Precedence                 │
  │    (Trumps all linguistic preference)                  │
  └───────────────────────────┬────────────────────────────┘
                              │
  ┌───────────────────────────▼────────────────────────────┐
  │ 2. Narrative Etymology & In-Universe Lore              │
  │    (e.g., Mithril over Misruru, Aether over Eteru)     │
  └───────────────────────────┬────────────────────────────┘
                              │
  ┌───────────────────────────▼────────────────────────────┐
  │ 3. UI Budget & Layout Envelope Feasibility             │
  │    (Shorter approved term if display width is narrow)  │
  └───────────────────────────┬────────────────────────────┘
                              │
  ┌───────────────────────────▼────────────────────────────┐
  │ 4. Team Consensus / Style Guide Decision Record        │
  └────────────────────────────────────────────────────────┘
```

#### Resolving Homonyms and Ambiguous Gaming Terms
Certain English source words correspond to multiple distinct Russian terms depending on category. In such cases, document them in the glossary with explicit categories and notes:
- `Attack` (Command): *Атаковать* (Category: `system`)
- `Attack` (Stat): *Атака* (Category: `system`)
- `Miss` (Battle): *Промах* (Category: `system`, Notes: Never translate as *Скучать*)
- `Back` (Menu UI): *Назад* (Category: `system`)
- `Back` (Formation): *Тыл / Задний ряд* (Category: `system`)

---

### Step 5: Compliance Auditing across Game Scripts

Verify that the translated game files strictly comply with the approved glossary terms using `scripts/glossary_tool.py audit`.

#### Running the Audit
```powershell
# Audit a JSON dialogue file against the master glossary
python scripts/glossary_tool.py audit `
  --glossary "glossary/game_terms.json" `
  --source "data/dialogue_en.json" `
  --target "data/dialogue_ru.json" `
  --format table
```

#### Interpreting Audit Output
- **Exit Code 0**: No terminology violations detected.
  ```text
  Glossary compliance check passed: no violations detected.
  ```
- **Exit Code 1**: Violations detected. Example output:
  ```text
  Terminology Compliance Violations Detected:
  | source_term  | expected_ru | category | message                                              |
  | ------------ | ----------- | -------- | ---------------------------------------------------- |
  | Phoenix Down | Перо феникса | item     | Source contains 'Phoenix Down' but target lacks 'Перо феникса' |
  ```

---

## Error Remediation Guide

| Error Message / Symptom | Root Cause | Exact Remediation Step |
| :--- | :--- | :--- |
| `File error: Glossary file not found: ...` | Specified glossary file path does not exist. | Verify file path; initialize new glossary using `python scripts/glossary_tool.py add` with target path. |
| `Validation error: Malformed JSON in glossary file` | Syntax error in JSON glossary (trailing comma, unquoted key). | Validate JSON with `python -m json.tool <path>` and fix syntax errors. |
| `Source contains '<term>' but target lacks '<expected_ru>'` | The translator used a synonym or alternative spelling not authorized by the glossary. | Open target translated file, search for the term occurrence, and replace with approved `expected_ru`. |
| `Candidate extraction returned 0 terms` | The input text contained no Katakana (for JA) or capitalized nouns (for EN). | Check `--lang` flag; ensure source text contains target language content. |
| `Grammatical disagreement in runtime text` | An adjective was written in masculine gender for a feminine or neuter item. | Update script text to match the gender recorded in the glossary's `gender` field. |

---

## Pre-Submission Verification Checklist

- [ ] **1. Header & Schema Validity**: TSV contains proper headers; JSON conforms to term schema.
- [ ] **2. Encoding**: File is cleanly encoded in UTF-8.
- [ ] **3. Entity Metadata Complete**: Every entry has valid `category`, `gender`, and `source_lang`.
- [ ] **4. Canon Precedence Verified**: Franchise names cross-referenced against official localizations.
- [ ] **5. Polivanov Orthography**: Japanese names Cyrillized following Polivanov baseline.
- [ ] **6. Audit Verification**: `python scripts/glossary_tool.py audit` passes on translated game files with exit code 0.
