---
name: game-text-translation
description: Standard operating procedure for translating game dialogue, UI menus, item descriptions, and quest logs from Japanese (JA) and English (EN) into Russian (RU) with tag parity, layout budgeting, and glossary compliance.
---

# Game Text Translation Workflow (JA / EN -> RU)

## Overview

This skill establishes the end-to-end standard operating procedure (SOP) for translating game text dumps, dialogue trees, system UI menus, quest logs, and item descriptions from **Japanese (JA)** and **English (EN)** into **Russian (RU)**. It ensures complete preservation of engine bytecode, strict adherence to project glossaries, natural Russian literary cadence (eliminating *переводяз*), and adherence to hardware layout budgets.

## When to Use

- Translating raw game script extractions (JSON, Gettext PO, TSV/CSV, or plain-text line dumps).
- Localizing character dialogue, system prompts, battle logs, equipment names, and item descriptions.
- Adapting Japanese role language (*Yakuwarigo*) and personal pronouns into appropriate Russian stylistic registers.
- Eliminating English syntactic calques and passive constructions in Russian game text.
- Running automated pre-flight quality checks before committing or inserting translated strings into binary ROMs/archives.

When NOT to use:
- Building or modifying project terminology glossaries (use `game-glossary-manager`).
- Cross-comparing script differences across regional releases or censorship cuts (use `game-translation-comparator`).
- Final binary validation and batch QA reporting across entire releases (use `game-l10n-qa`).

---

## The 5-Phase Translation Procedure

```
  ┌──────────────────────────────────────────────────────────────┐
  │ Phase 1: Text Extraction & Format Identification            │
  │   - Detect container format (JSON, PO, TSV, TXT)             │
  │   - Verify UTF-8 encoding and schema structure               │
  └──────────────────────────────┬───────────────────────────────┘
                                 │
  ┌──────────────────────────────▼───────────────────────────────┐
  │ Phase 2: Context Gathering & Envelope Profiling             │
  │   - Identify speaker persona, age, social standing           │
  │   - Determine scene register and hardware layout limits      │
  └──────────────────────────────┬───────────────────────────────┘
                                 │
  ┌──────────────────────────────▼───────────────────────────────┐
  │ Phase 3: Glossary Querying & Canon Precedence                │
  │   - Query project glossary via glossary_tool.py search       │
  │   - Check Polivanov vs established franchise canon           │
  └──────────────────────────────┬───────────────────────────────┘
                                 │
  ┌──────────────────────────────▼───────────────────────────────┐
  │ Phase 4: Draft Translation (rules/AGENTS.md Compliance)      │
  │   - Map Yakuwarigo / purge translationese calques            │
  │   - Preserve 100% of engine tags, control codes, specifiers  │
  │   - Apply Russian typography («...», —, ё-фикация)           │
  └──────────────────────────────┬───────────────────────────────┘
                                 │
  ┌──────────────────────────────▼───────────────────────────────┐
  │ Phase 5: Automated Verification & Error Remediation          │
  │   - Validate tags and layout via l10n_validator.py           │
  │   - Audit terminology compliance via glossary_tool.py audit  │
  └──────────────────────────────────────────────────────────────┘
```

---

### Phase 1: Text Extraction & Format Identification

Identify the file format and structure of the input script. Supported formats include:

1. **JSON Dictionaries or Lists**:
   - Key-value mapping: `{"MSG_001": "Hello world!", "MSG_002": "..."}`
   - Object collections: `[{"id": "001", "text": "..."}, ...]`
2. **GNU Gettext PO Files**:
   - `msgid "..."` (source string) followed by `msgstr "..."` (target translation).
3. **Tab-Separated Values (TSV) or CSV**:
   - Columnar tables with `id` or `key`, followed by `source` and `target` columns.
4. **Line-Based Plain Text**:
   - One dialogue unit per line, matched by zero-based line indices.

#### Verification Command
Ensure the source file exists and is encoded in valid UTF-8:
```powershell
# Inspect the top of the source file
Get-Content -Path "data/script_en.json" -TotalCount 20
```

---

### Phase 2: Context Gathering & Envelope Profiling

Before drafting translations, collect the linguistic and technical parameters of the text chunk:

1. **Speaker Identity & Sociolinguistic Profile**:
   - Who is speaking? (Warrior, child, royalty, robot, elderly hermit, narrator).
   - What is the relationship between the speaker and the listener? (Comrade, superior, mortal enemy, stranger).
2. **Scene Dramatic Tone**:
   - Urgent combat callout, solemn funeral soliloquy, lighthearted festival banter, or cold tutorial prompt.
3. **Layout Envelope Constraints**:
   - **Max characters per line (`--max-len`)**: Typically 28–36 chars for retro handhelds (NES, SNES, GBA, NDS); 45–60 chars for high-resolution displays.
   - **Max lines per page (`--max-lines`)**: Typically 2 to 4 lines before requiring `{PAGE}` or text box clear.
   - **Pixel width expansion**: Cyrillic glyphs (`Ж`, `Ш`, `Щ`, `Ы`, `Ю`, `Ф`) are physically wider in proportional fonts (VWF) than Latin characters. Plan for a 20–30% expansion over English and 50–70% expansion over Japanese.

---

### Phase 3: Glossary Querying & Canon Precedence

Every named entity, item, spell, location, and UI label must be checked against the approved project glossary.

#### CLI Command: Search Glossary
```powershell
# Search for a term in English
python scripts/glossary_tool.py search --glossary "glossary/game_terms.json" --query "Phoenix Down"

# Search for a term in Japanese
python scripts/glossary_tool.py search --glossary "glossary/game_terms.json" --query "フェニックスの尾" --lang ja

# Search with exact case matching
python scripts/glossary_tool.py search --glossary "glossary/game_terms.tsv" --query "Potion" --exact
```

#### Naming Precedence Rules
1. **Established Franchise Canon**: Official localizations override mechanical rules (*Cloud* -> **Клауд**, *Shinra* -> **Шинра**, *Sephiroth* -> **Сефирот**).
2. **Polivanov Baseline for Japanese Names**: Follow standard Cyrillization (`し -> си`, `ち -> ти`, `じ -> дзи`, `つ -> цу`) for authentic Japanese names unless canon dictates otherwise.
3. **Etymological Source Principle**: When Katakana transcribes European loanwords, translate from the etymological origin (*フェニックスの尾* -> **Перо феникса**, not *Хвост феникса*; *エーテル* -> **Эфир**, not *Этеру*).

---

### Phase 4: Draft Translation Adhering to `rules/AGENTS.md`

#### 1. Japanese to Russian (JA -> RU) Linguistic Rules
- **Map Role Language (*Yakuwarigo*)**:
  - `〜でござる / 拙者`: Stately, archaic Russian (*«Мне сие неведомо…»*). Never use cartoonish pseudo-Slavic slurs (*«гой еси»*).
  - `〜じゃ / わし`: Folksy older cadence (*«Эх, стар я стал…»*).
  - `だぜ / てめえ`: Sharp, gritty colloquial delivery (*«Ты кем себя возомнил?!»*).
  - `ですわ / 私 (watakushi)`: Aristocratic refinement, polite rhetorical turns (*«Полагаю, вы останетесь довольны?»*).
- **Honorific Suffixes Policy**:
  - *Authentic Japanese setting* (Tokyo, feudal Japan): Retain suffixes in lowercase with hyphen (*Рюдзи-кун*, *Ода-сама*).
  - *Fantasy / Sci-Fi setting* (secondary world): Drop Japanese suffixes and adapt contextually (*господин*, *мастер*, *братец*, *дружище*).
- **Dual Semantics (*Gikun / Furigana*)**:
  - Prioritize audio dialogue for voiced lines; blend descriptively in text if envelope permits (*«Благородный Фантазм (священная реликвия)»*).

#### 2. English to Russian (EN -> RU) Linguistic Rules
- **Eliminate Translationese (*Переводяз*)**:
  - *Purge gratuitous possessive pronouns*: English *«He put his hands in his pockets»* becomes Russian *«Он сунул руки в карманы»* (never *«свои руки в свои карманы»*).
  - *Convert passive voice to active/reflexive*: *«The town was destroyed by monsters»* -> *«Чудовища разорили город»* (never *«Город был разрушен чудовищами»*).
  - *Prune participles and verbal nouns*: Replace *«совершение атаки»* with *«атака»* or *«нападение»*.
  - *Apply Theme-Rheme word order*: Place new narrative focus at the end of the clause (*«From the shadows emerged a dragon»* -> *«Из тени выступил дракон»*).
- **Disambiguate Context-Dependent Gaming Terms**:
  - `Miss`: Combat failure -> **Промах** (never *Скучать*).
  - `Back`: Navigation UI -> **Назад**; Anatomy -> **Спина**; Tactical formation -> **Тыл / Задний ряд**.
  - `Save`: System persistence -> **Сохранить**; Rescue -> **Спасти**.
  - `Equip`: Command verb -> **Экипировать / Надеть / Взять**; Menu category -> **Снаряжение**.
  - `Clear`: Completion -> **Пройдено / Завершено**; Wipe memory -> **Очистить**.

#### 3. Zero Bytecode Degradation
Every tag enclosed in `{...}`, `[...]`, `<...>`, or format specifiers `%s`, `%d`, `%1$s` must remain byte-identical:
- Do not translate tag names (`{COLOR 1}` $\ne$ `{ЦВЕТ 1}`).
- Do not alter tag casing (`{HERO}` $\ne$ `{hero}`).
- Do not drop or add tags.
- Format specifier positional ordering: Use `%1$s`, `%2$s` only if the game engine runtime supports POSIX format specifiers; otherwise preserve exact sequence `%s ... %s`.

#### 4. Typographical & Orthographic Perfection
- Primary quotes: Guillemets `«...»`. Nested quotes: German `„...“`.
- Dialogue dash: Em-dash `—` with leading space or newline (`— Кто здесь?`).
- Consistent letter `ё`: Always write `ещё`, `тёмный`, `вертолёт`, `орден`, `звёзды`.

---

### Phase 5: Automated QA & Compliance Verification

Run the automated validation tools against the translated file before staging or committing.

#### 1. Validate Tags, Typography, and Layout Envelope
```powershell
python scripts/l10n_validator.py --source "data/dialogue_en.json" --target "data/dialogue_ru.json" --max-len 38 --max-lines 4
```
Expected output on success:
```text
[PASS] All 150 entries validated successfully.
```

#### 2. Audit Terminology Compliance
```powershell
python scripts/glossary_tool.py audit --glossary "glossary/game_terms.json" --source "data/dialogue_en.json" --target "data/dialogue_ru.json"
```
Expected output on success:
```text
Glossary compliance check passed: no violations detected.
```

---

## Concrete Workflow Examples

### Example 1: Japanese Scenario Dialogue (JA -> RU)

**Source Input (`data/scene_01_ja.json`)**:
```json
{
  "SCENE_01_001": "{COLOR 2}拙者{COLOR 0}の刀が折れぬ限り、{PAGE}姫君には指一本触れさせぬでござる！"
}
```

1. **Context Analysis**:
   - Speaker: Samurai bodyguard (feudal honor, humble yet resolute).
   - Tone: Dramatic defense against impending danger.
   - Tags: `{COLOR 2}`, `{COLOR 0}`, `{PAGE}`.
2. **Linguistic Adaptation**:
   - `拙者` -> *«я»* (or self-effacing warrior phrasing); `でござる` -> restrained archaic register, noble pledge.
   - Literal calque to avoid: *«Пока мой меч де-годзару не сломан, я не позволю тронуть принцессу де-годзару!»*
   - Natural Russian: *«Покуда цел мой клинок, я и волосу не позволю упасть с головы госпожи!»*
3. **Target Output (`data/scene_01_ru.json`)**:
```json
{
  "SCENE_01_001": "{COLOR 2}Покуда цел мой клинок{COLOR 0}, {PAGE}я и волосу не позволю упасть с головы госпожи!"
}
```
4. **Validation Check**:
```powershell
python scripts/l10n_validator.py --source "data/scene_01_ja.json" --target "data/scene_01_ru.json" --max-len 42 --max-lines 2
```
All tags `{COLOR 2}`, `{COLOR 0}`, `{PAGE}` preserved; valid layout and punctuation.

---

### Example 2: English System Menu & Quest Dialogue (EN -> RU)

**Source Input (`data/quest_log_en.json`)**:
```json
{
  "QUEST_ITEM_01": "You obtained [ITEM %d]!\nEquip it now in your inventory.",
  "BATTLE_MISS_01": "Miss! The enemy evaded your attack."
}
```

1. **Context & Glossary Lookup**:
   - `[ITEM %d]`: Dynamic variable container.
   - `Equip`: Imperative verb -> *«Экипируйте»* or *«Наденьте»*.
   - `Miss`: Battle outcome -> **Промах!** (never *«Скучаю!»*).
   - Possessive *«your inventory»* and *«your attack»*: Drop *свой/вашей* in Russian.
2. **Drafting Natural Russian**:
   - `QUEST_ITEM_01`: *«Получен предмет: [ITEM %d]!\nЭкипируйте его через меню снаряжения.»*
   - `BATTLE_MISS_01`: *«Промах! Враг увернулся от удара.»*
3. **Target Output (`data/quest_log_ru.json`)**:
```json
{
  "QUEST_ITEM_01": "Получен предмет: [ITEM %d]!\nЭкипируйте его через меню снаряжения.",
  "BATTLE_MISS_01": "Промах! Враг увернулся от удара."
}
```
4. **Validation Check**:
```powershell
python scripts/l10n_validator.py --source "data/quest_log_en.json" --target "data/quest_log_ru.json" --max-len 40 --max-lines 3
```

---

## Error Remediation Guide

| Error Message / Symptom | Root Cause | Exact Remediation Step |
| :--- | :--- | :--- |
| `Tag mismatch: missing '{PAGE}'` | The translator inadvertently omitted a page boundary tag during line rewriting. | Re-insert `{PAGE}` at the appropriate dialogue sentence boundary. |
| `Tag mismatch: casing difference '{color 1}' vs '{COLOR 1}'` | Text editor autocorrected uppercase tag name. | Restore original uppercase letters: `{COLOR 1}`. |
| `Malformed tag: unclosed '{' found` | Typo in opening or closing curly brace (e.g. `{COLOR 1`). | Balance all opening and closing braces: `{COLOR 1}`. |
| `Line exceeds max length (46 > 40)` | Russian text expanded beyond character-per-line budget. | Rephrase with concise synonyms or split line using `\n` or `{LINE}`. |
| `Line count exceeds maximum budget (5 > 4)` | Dialogue box overflow; text will clip or scroll off screen. | Insert a `{PAGE}` tag to paginate the text into two successive boxes. |
| `Russian typography warning: straight ASCII quotes '"' found` | Standard typewriter quotes `"` were typed instead of guillemets. | Replace outer quotes with `«...»` and inner quotes with `„...“`. |
| `Russian typography warning: hyphen '-' used as dash` | ASCII hyphen `-` used instead of em-dash `—` for speech or clause breaks. | Replace with em-dash `—` surrounded by spaces (`Свет — наш щит`). |
| `Terminology compliance violation: 'Potion' expected 'Зелье'` | Non-standard term used instead of approved glossary entry. | Update translation to use the approved term from `glossary_tool.py`. |

---

## Pre-Submission Verification Checklist

Before marking any translation task complete, verify each item:

- [ ] **1. File Format Integrity**: Output file matches the exact schema and encoding of the source file.
- [ ] **2. 100% Tag Parity**: Every `{TAG}`, `[TAG]`, `%s`, and `\n` matches source casing and arguments.
- [ ] **3. No Translationese**: Eliminated superfluous *«свой»*, *«был сделан»*, and robotic SVO structures.
- [ ] **4. Disambiguation Audited**: Polysemous terms (*Miss, Back, Cast, Save, Clear*) match gaming context.
- [ ] **5. Layout Budget Respected**: No lines exceed `--max-len`; no dialogue pages exceed `--max-lines`.
- [ ] **6. Typographical Compliance**: French guillemets `«...»`, em-dashes `—`, and complete `ё`-fication applied.
- [ ] **7. Automated Tools Passed**: `scripts/l10n_validator.py` and `scripts/glossary_tool.py audit` exited with code 0.
