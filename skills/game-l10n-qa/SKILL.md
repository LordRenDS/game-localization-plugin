---
name: game-l10n-qa
description: Comprehensive quality assurance and verification workflow for localized game scripts, enforcing zero bytecode degradation, dialogue box layout budgeting, and Russian typography rules.
---

# Game Localization Quality Assurance (L10N QA) Workflow

## Overview

This skill establishes the comprehensive quality assurance, validation, and failure triage procedure for localized game scripts. In game development and ROM hacking, localized scripts run inside strict real-time hardware environments. A single corrupted control tag, unclosed bracket, or overflowing line can crash the script virtual machine, freeze the rendering pipeline, or corrupt game memory.

The L10N QA workflow utilizes `scripts/l10n_validator.py` to enforce zero bytecode degradation, verify dialogue box layout budgets, detect unclosed tags, and enforce Russian typographical and orthographic standards.

## When to Use

- Validating translated dialogue, system menus, item descriptions, or quest journals before ROM insertion.
- Pre-commit and pre-release quality checks in automated CI/CD pipelines.
- Verifying tag parity between source (English/Japanese) and target (Russian) scripts.
- Checking character-per-line (CPL) and line-count budgets against hardware display limits.
- Auditing Russian typography (replacing ASCII quotes `"` with guillemets `«...»` and hyphens `-` with em-dashes `—`).
- Triaging validation failure reports and systematically fixing syntax errors.

When NOT to use:
- Drafting translations and adapting dialogue (use `game-text-translation`).
- Extracting or curating terminology glossaries (use `game-glossary-manager`).
- Cross-comparing versions for censorship and cut content (use `game-translation-comparator`).

---

## The 4 Core QA Verification Pillars

```
  ┌────────────────────────────────────────────────────────┐
  │ Pillar 1: Zero Bytecode Degradation & Tag Parity       │
  │   - 100% parity across {TAG}, [TAG], %s, and \n        │
  │   - Strict bracket balance (no unclosed '{' or '[')    │
  └───────────────────────────┬────────────────────────────┘
                              │
  ┌───────────────────────────▼────────────────────────────┐
  │ Pillar 2: Display Layout Budgeting & VWF Constraints   │
  │   - Line length threshold (--max-len: e.g. 32-40 chars)│
  │   - Line count threshold (--max-lines: e.g. 2-4 lines) │
  │   - Multi-page validation via {PAGE} opcode            │
  └───────────────────────────┬────────────────────────────┘
                              │
  ┌───────────────────────────▼────────────────────────────┐
  │ Pillar 3: Russian Typography & Orthographic Standards  │
  │   - Guillemets «...» and nested quotes „...“           │
  │   - Dialogue and sentence em-dashes (—)                │
  │   - Full and consistent letter 'ё' orthography         │
  └───────────────────────────┬────────────────────────────┘
                              │
  ┌───────────────────────────▼────────────────────────────┐
  │ Pillar 4: Structural File Parity & Key Completeness    │
  │   - Identical key sets in JSON dictionaries            │
  │   - msgid / msgstr pair completeness in Gettext PO     │
  │   - Identical line counts in plain text script dumps   │
  └────────────────────────────────────────────────────────┘
```

---

## Hardware Layout Budgets Reference

Different gaming platforms impose strict physical boundaries on dialogue windows. Setting improper limits results in unsightly text clipping or game-breaking crashes.

| Platform / Resolution | Typical Line Length (`--max-len`) | Max Lines (`--max-lines`) | Hardware Constraints & Font Notes |
| :--- | :--- | :--- | :--- |
| **NES / Famicom (256x240)** | 24–28 characters | 2–3 lines | Fixed 8x8 tile fonts; strict memory buffers. |
| **SNES / Super Famicom (256x224)** | 28–34 characters | 3–4 lines | Fixed-width or primitive 12px VWF. |
| **Game Boy Advance (240x160)** | 26–30 characters | 2–3 lines | Tight vertical resolution; aggressive abbreviations needed. |
| **Nintendo DS (256x192)** | 30–36 characters | 3–4 lines | Proportional VWF (NFTR). Wide Cyrillic expansion (~25%). |
| **Sony PSP / PS1 (480x272 / 320x240)**| 36–42 characters | 3–4 lines | High-res text boxes; sub-pixel VWF rendering. |
| **Modern HD / PC (1080p+)** | 45–60 characters | 2–4 lines | Subtitle ribbons or spacious text windows. |

> [!IMPORTANT]
> **VWF Cyrillic Glyph Expansion**: In proportional fonts, wide Russian letters (`Ж`, `Ш`, `Щ`, `Ы`, `Ю`, `Ф`, `М`) consume 8–12 pixels compared to 3–5 pixels for Latin `i`, `l`, `t`. When calculating `--max-len`, budget conservatively (e.g. 32 characters for Russian where English permitted 36).

---

## Step-by-Step QA Execution Procedure

### Step 1: Pre-Flight File Inspection
Verify file encoding and syntax validity before running deep validation:
```powershell
# Ensure file is UTF-8 without corruption
Get-Content -Path "data/script_ru.json" -TotalCount 10
```

### Step 2: Automated Validation Execution
Run `scripts/l10n_validator.py` with appropriate budget constraints:

#### Standard Validation Run
```powershell
python scripts/l10n_validator.py `
  --source "data/dialogue_en.json" `
  --target "data/dialogue_ru.json" `
  --max-len 36 `
  --max-lines 4
```

#### Gettext PO File Validation Run
```powershell
python scripts/l10n_validator.py `
  --source "locales/en/messages.po" `
  --target "locales/ru/messages.po" `
  --max-len 40 `
  --max-lines 3
```

#### Plain Text Line Dump Validation Run
```powershell
python scripts/l10n_validator.py `
  --source "dumps/script_01_en.txt" `
  --target "dumps/script_01_ru.txt" `
  --max-len 32 `
  --max-lines 2
```

### Step 3: CI/CD & Scripted JSON Execution
For automated build pipelines, emit machine-readable JSON reports:
```powershell
python scripts/l10n_validator.py `
  --source "data/system_en.json" `
  --target "data/system_ru.json" `
  --max-len 30 `
  --max-lines 2 `
  --json > "reports/qa_report.json"
```

### Step 4: Interpreting Exit Codes
The tool signals validation outcome through standard POSIX exit codes:
- **Exit Code `0`**: All entries passed validation. Zero errors detected.
  ```text
  [PASS] All 450 entries validated successfully.
  ```
- **Exit Code `1`**: One or more validation errors detected.
  ```text
  [FAIL] Found 3 errors across 2 entries:
    Entry 'SCENE_04_012':
      - Tag mismatch: missing '{WAIT 15}'
      - Russian typography warning: straight ASCII quotes '"' found, use guillemets « » instead
    Entry 'SCENE_04_015':
      - Line 2 exceeds max length (41 > 36)
  ```

---

## Typographical Enforcement Rules

### 1. Quotation Marks Hierarchy
- **Standard Quotes**: Guillemets `«...»` (`U+00AB` and `U+00BB`).
- **Nested Quotes**: German quotes `„...“` (`U+201E` and `U+201C`).
- **Forbidden**: Straight ASCII quotes `"` (`0x22`) and English curly quotes `“...”`.
- *Example*:
  - Correct: `«Командир крикнул: „В укрытие!“ — и выстрелил.»`
  - Incorrect: `"Командир крикнул: "В укрытие!" - и выстрелил."`

### 2. Dashes and Hyphens
- **Dialogue Dash**: Em-dash `—` (`U+2014`) preceded by newline or space:
  - Correct: `— Кто идёт?`
  - Incorrect: `- Кто идёт?`
- **Sentence Dash**: Em-dash `—` surrounded by spaces:
  - Correct: `Меч — наше главное оружие.`
  - Incorrect: `Меч - наше главное оружие.`
- **Hyphen (`-`)**: Allowed only in compound words (*кто-то*, *из-за*, *меч-кладенец*).

### 3. Orthography of Letter "Ё"
- All game dialogue, quest lore, menus, and names must consistently use `ё` / `Ё`.
- Words requiring `ё`: `ещё`, `тёмный`, `берёза`, `вертолёт`, `орден`, `звёзды`, `слёзы`, `чёрный`.
- Inconsistent mixing of `е` and `ё` is considered an editorial defect.

---

## Automated CI/CD Integration Examples

### PowerShell Validation Script
```powershell
# run_qa.ps1
$ErrorActionPreference = "Stop"

Write-Host "Running L10N QA Validator..." -ForegroundColor Cyan

$source = "data/dialogue_en.json"
$target = "data/dialogue_ru.json"

python scripts/l10n_validator.py --source $source --target $target --max-len 36 --max-lines 4
if ($LASTEXITCODE -ne 0) {
    Write-Error "L10N QA Failed! Fix validation errors before merging."
    exit 1
}

Write-Host "Running Glossary Compliance Audit..." -ForegroundColor Cyan
python scripts/glossary_tool.py audit --glossary "glossary/game_terms.json" --source $source --target $target
if ($LASTEXITCODE -ne 0) {
    Write-Error "Glossary Audit Failed! Fix terminology violations before merging."
    exit 1
}

Write-Host "All L10N QA checks PASSED successfully!" -ForegroundColor Green
exit 0
```

### Bash Validation Script
```bash
#!/usr/bin/env bash
set -e

echo "Running L10N QA validation..."
python3 scripts/l10n_validator.py \
  --source "data/dialogue_en.json" \
  --target "data/dialogue_ru.json" \
  --max-len 36 \
  --max-lines 4

echo "Auditing terminology compliance..."
python3 scripts/glossary_tool.py audit \
  --glossary "glossary/game_terms.json" \
  --source "data/dialogue_en.json" \
  --target "data/dialogue_ru.json"

echo "L10N QA passed successfully!"
```

---

## Error Remediation Protocol

| Validation Error | Technical Cause | Exact Remediation Action |
| :--- | :--- | :--- |
| `Malformed tag: unclosed '{' found near '...'` | An opening curly brace `{` lacks a matching closing brace `}`. | Locate the position and supply the closing brace: `{COLOR 1}`. |
| `Malformed tag: unexpected '}' at character index N` | A stray closing brace was inserted without an opener. | Delete the extraneous `}` character. |
| `Tag mismatch: missing '{PAGE}'` | The translator deleted a page boundary opcode during editing. | Re-insert `{PAGE}` between dialogue chunks. |
| `Tag mismatch: extra '{HERO}' in target` | A character name token was duplicated. | Remove the redundant tag occurrence. |
| `Tag mismatch: parameter mismatch '{WAIT 10}' vs '{WAIT 5}'` | Tag parameter value was inadvertently edited. | Restore original parameter value: `{WAIT 10}`. |
| `Line N exceeds max length (44 > 36)` | Russian sentence expansion breached dialogue box boundary. | Rephrase with punchy verbs, trim filler words, or split with `\n`. |
| `Line count exceeds maximum budget in page 1 (5 > 4)` | Too many lines in a single dialogue box page. | Insert `{PAGE}` after line 2 or 3 to split into two display pages. |
| `Missing key in target: 'MSG_042'` | The target JSON file dropped an entire dialogue line. | Add the missing key `MSG_042` and supply the translation. |
| `Unexpected extra key in target: 'MSG_999'` | A phantom key or draft entry exists in target. | Remove the extraneous key from the target file. |
| `Russian typography warning: straight ASCII quotes '"' found` | Typewriter quotes were used. | Replace with Russian guillemets `«...»`. |
| `Russian typography warning: hyphen '-' used as dialogue dash` | Standard hyphen `-` was used at speech start. | Replace with em-dash `—` (`— Привет!`). |

---

## Pre-Release Signoff Checklist

Before approving a localized script for build assembly or ROM repacking, certify all criteria:

- [ ] **1. Clean Exit Code**: `python scripts/l10n_validator.py` completes with exit code `0`.
- [ ] **2. 100% Tag Match**: Every tag (`{...}`, `[...]`, `%s`, `\n`) matches the source byte-for-byte.
- [ ] **3. No Structural Drift**: All keys in JSON match source; no missing or extra keys.
- [ ] **4. Layout Envelope Compliant**: Every line is $\le$ `--max-len`; every page is $\le$ `--max-lines`.
- [ ] **5. Typography Clean**: Zero ASCII quotes (`"`), zero hyphen dialogue dashes, 100% `ё`-fication.
- [ ] **6. Glossary Compliant**: `python scripts/glossary_tool.py audit` completes with exit code `0`.
