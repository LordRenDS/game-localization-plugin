---
name: game-translation-comparator
description: Workflow for cross-version game script alignment, comparative analysis of censorship and tonal shifts across Japanese, English, and Russian releases, and synthesizing definitive translations.
---

# Game Translation Comparator Workflow

## Overview

This skill establishes the standard procedure for comparative script analysis across multiple game releases (typically the **Japanese original (JP)**, **official English localizations (US/EU)**, and **existing Russian fan translations (RU)**). It enables localizers and narrative designers to identify regional censorship, tonal shifts, omitted dialogue, and legacy mistranslations, and to synthesize a superior, definitive Russian translation that honors original authorial intent.

The workflow leverages `scripts/version_diff.py` to ingest multi-format scripts, align them by dialogue key or index, and generate comparative Markdown reports.

## When to Use

- Cross-examining original Japanese game scripts against 90s/2000s English localizations (e.g. SNES/PS1 era Woolseyisms, Nintendo of America censorship).
- Auditing existing Russian fan translations for inaccuracies, syntactic translationese (*переводяз*), or missing lines.
- Detecting content cuts, softened profanity, altered religious references, and removed cultural context.
- Triangulating meaning when Japanese source text is highly ambiguous or context is sparse.
- Synthesizing a definitive Russian script that blends original Japanese nuance with natural, expressive Russian literary style.

When NOT to use:
- Day-to-day drafting of raw translations without cross-version references (use `game-text-translation`).
- Managing project glossaries and terminology databases (use `game-glossary-manager`).
- Automated pre-flight bytecode tag and line length checks (use `game-l10n-qa`).

---

## The 4-Phase Comparative Methodology

```
  ┌────────────────────────────────────────────────────────┐
  │ Phase 1: Ingestion & Multi-Version Alignment           │
  │   - Load scripts in JSON, PO, TSV, or TXT format       │
  │   - Align by key/index using scripts/version_diff.py   │
  └───────────────────────────┬────────────────────────────┘
                              │
  ┌───────────────────────────▼────────────────────────────┐
  │ Phase 2: Divergence Categorization                     │
  │   - Tag censorship, tonal shifts, and cut content      │
  │   - Diagnose legacy translation errors and bugs        │
  └───────────────────────────┬────────────────────────────┘
                              │
  ┌───────────────────────────▼────────────────────────────┐
  │ Phase 3: Synthesis & Triangulation Procedure           │
  │   - Recover original Japanese intent and character voice│
  │   - Synthesize definitive Russian translation          │
  └───────────────────────────┬────────────────────────────┘
                              │
  ┌───────────────────────────▼────────────────────────────┐
  │ Phase 4: Comparative Reporting & Documentation         │
  │   - Output Markdown diff tables and editorial logs     │
  └────────────────────────────────────────────────────────┘
```

---

### Phase 1: Ingestion & Multi-Version Alignment

The alignment engine supports comparing two, three, or more version files simultaneously. Supported formats include JSON maps/arrays, Gettext PO files, TSV tables, and plain-text line dumps.

#### CLI Command: Basic Two-Version Alignment
```powershell
python scripts/version_diff.py `
  --version JP="data/script_scenario_jp.json" `
  --version US="data/script_scenario_us.json" `
  --title "Chrono Trigger: JP vs US Alignment" `
  --output "reports/diff_jp_us.md"
```

#### CLI Command: Three-Version Triangulation (Divergent Only)
To isolate only lines where text differs or content was omitted, pass `--divergent-only`:
```powershell
python scripts/version_diff.py `
  --version JP="data/script_scenario_jp.json" `
  --version US="data/script_scenario_us.json" `
  --version RU_OLD="data/script_scenario_ru_fan.json" `
  --divergent-only `
  --title "Scenario Divergence & Censorship Analysis" `
  --output "reports/diff_divergent_scenario.md"
```

---

### Phase 2: Divergence Categorization

When analyzing aligned rows, classify discrepancies into one of four primary categories:

#### 1. Content Censorship & Regional Sanitization
Historical Western releases (notably Nintendo of America in the 16-bit era) strictly sanitized:
- **Religious Iconography**: Removing crosses, renaming spells (*Holy* -> *White*, *Death* -> *Doom*), scrubbing references to God, heaven, or hell.
- **Alcohol & Substances**: Renaming *Sake / Wine* into *Soda / Cider*; tavern bars into cafes.
- **Violence & Death**: Softening explicit threats of murder or decapitation into vague villainous boasting (*«I'll destroy you!»*).

#### 2. Tonal Flattening & Character Distortion
- Japanese scripts frequently distinguish character age, social standing, and emotional vulnerability through role language (*Yakuwarigo*).
- Rushed English localizations often flattened distinct voices (a weary samurai, an aristocratic noblewoman, a rough street delinquent) into generic action-hero banter.
- *Example*: Translating a samurai's modest *拙者 (sessha)* and *〜でござる* into standard *«I will defeat you»* strips the character's core identity.

#### 3. Cut Content & Memory-Constraint Omissions
- Early cartridge ROM size constraints forced English localizers to condense or outright delete entire lines, descriptions, and character lore to fit limited character budgets.
- Identifying these omissions restores rich world-building that Western players previously missed.

#### 4. Localization Bugs & Mistranslations
- Inverted logic: Translating negative questions literally, leading to dialogue that says the exact opposite of the original Japanese intent.
- Missing subject disambiguation: Assuming an unstated subject was "he" when context in Japanese clearly referred to "she" or "they".
- Famous retro mistranslations (*«This guy are sick»*, *«Spoony bard»*, *«Welcome to warp zone»*).

---

### Phase 3: Synthesis & Triangulation Procedure

When synthesizing the definitive Russian text, use the **Three-Source Triangulation Method**:

```
           Japanese Original (JP)
         [Authorial Intent & Lore]
                  ▲      ▲
                 /        \
                /          \
  English Localization      Existing Russian Fan
  [Pacing & Western Context] [Historical Memory & Pitfalls]
                \          /
                 ▼        ▼
       Definitive Russian Translation (RU)
       [Natural Russian Literary Voice]
```

#### The Triangulation Rules
1. **Primary Authority = Japanese Original**: The semantic truth, character motivations, and emotional weight are anchored in the Japanese source.
2. **Clarity Filter = English Adaptation**: If the Japanese text is excessively cryptic or utilizes untranslatable wordplay, examine how skilled English localizers solved the puzzle. Adopt their narrative angle only if it respects authorial intent.
3. **Critical Review = Russian Fan History**: Review what previous fan translations did. Preserve beloved, iconic terminology if it became franchise canon; aggressively discard syntactic calques (*переводяз*) and mistranslations.
4. **Natural Literary Execution**: Render the synthesized meaning into authentic Russian literary prose with proper cadences, expressive idioms, and 100% tag immutability.

---

### Phase 4: Comparative Reporting & Documentation

Use `scripts/version_diff.py` to generate clean, shareable Markdown reports with comprehensive statistics.

#### CLI Command with Row Limiting for Fast Triage
```powershell
python scripts/version_diff.py `
  --version JP="data/battle_messages_jp.json" `
  --version US="data/battle_messages_us.json" `
  --divergent-only `
  --max-rows 50 `
  --output "reports/battle_divergences.md"
```

#### Report Structure Generated
The generated Markdown report includes:
- **Metadata Header**: Timestamp, compared versions, filters applied.
- **Summary Statistics**: Total keys, identical keys, divergent keys, missing/added keys.
- **Detailed Alignment Table**:
  - Column 1: Dialogue Key / Index.
  - Column 2..N: Text per compared version.
  - Final Column: Status (`IDENTICAL`, `DIVERGENT`, `MISSING_IN_...`).

---

## Real-World Case Study Walkthrough

### Scenario: *Chrono Trigger* — Magus Castle Confrontation

#### Aligned Data Matrix

| Version | Raw Script String |
| :--- | :--- |
| **JP Original** | `魔王「黒の風が、また泣き始めた……\n誰の血を求め……誰の魂を求めるのか？」` |
| **US Official (SNES)** | `Magus: "The black wind begins to blow...\nOkay, who's going to die first?"` |
| **RU Fan (1998)** | `Магус: «Черный ветер снова дует...\nЛадно, кто умрет первым?»` |

#### Comparative Analysis
1. **JP Nuance**: Magus uses poetic, somber, tragic phrasing (*«The black wind has begun to weep once more... Whose blood does it seek? Whose soul does it crave?»*). He is a tragic prince burdened by doom.
2. **US Distortion**: Ted Woolsey shortened the line to fit SNES character limits and made Magus sound like a boastful comic-book villain (*«Okay, who's going to die first?»*).
3. **RU Fan Flaw**: Translated directly from the flawed English SNES script, propagating the translationese (*«Черный ветер снова дует»*) and losing the tragic gravitas.

#### Definitive Russian Synthesis
```text
Маг: «Чёрный ветер вновь завыл во тьме…\nЧьей крови он жаждет? Чью душу зовёт на этот раз?»
```
- Restores the tragic, aristocratic villain voice.
- Preserves the letter `ё` (*«Чёрный»*).
- Uses evocative Russian vocabulary (*«вновь завыл во тьме»*, *«чьей крови жаждет»*).
- Fits comfortably within dialogue box layout budgets.

---

## Error Remediation Guide

| Error Message / Symptom | Root Cause | Exact Remediation Step |
| :--- | :--- | :--- |
| `Error: At least 2 version files must be specified` | Only 1 or 0 `--version` arguments provided. | Pass at least two `--version NAME=PATH` arguments on the command line. |
| `Error: Invalid version argument format: '...'` | Omitted the `=` delimiter between version name and file path. | Format as `NAME=PATH` (e.g. `--version JP="data/jp.json"`). |
| `Error loading JP from data/jp.json: Version file not found` | File path is incorrect or file does not exist. | Verify file path with `Test-Path <path>` and correct typo. |
| `Keys misaligned across versions (Key 0 vs MSG_001)` | One version uses auto-indexing while another uses semantic string keys. | Convert files to common key mapping format before diffing. |
| `Report contains thousands of identical lines` | Comparative report is too cluttered to spot real divergences. | Add `--divergent-only` flag to display solely changed or cut lines. |

---

## Pre-Submission Verification Checklist

- [ ] **1. Multi-Version Input Valid**: All compared files exist, are UTF-8 encoded, and have valid syntax.
- [ ] **2. Alignment Generated**: Ran `python scripts/version_diff.py` and generated markdown report.
- [ ] **3. Divergences Triaged**: Categorized instances of censorship, tonal shift, or cut content.
- [ ] **4. Authorial Intent Verified**: Japanese original consulted to resolve ambiguities.
- [ ] **5. Natural Russian Synthesis**: Proposed translations avoid English syntactic calques.
- [ ] **6. Tag & Layout Validated**: Synthesized strings pass `l10n_validator.py`.
