# Game Localization & Text Engineering Guidelines (JA/EN -> RU)

When translating, editing, validating, or engineering game scripts, dialogue trees, system UI, and bytecode from Japanese (JA) or English (EN) into Russian (RU), you must strictly follow these linguistic principles, typography rules, and engineering safeguards.

---

## 1. Core Principles & Operational Mandate

- **Zero Bytecode Degradation**: Control tags, script opcodes, variables, and formatting specifiers are executable code. Never alter, re-case, translate, or strip engine tags.
- **Eradication of Translationese (*Переводяз*)**: Target Russian text must read as natural, idiomatically rich literature. Calques from English syntax (overused possessive pronouns, excessive passive voice, unnatural sentence order) or literal transliterations from Japanese sentence endings are strictly prohibited.
- **Cadence & Character Voice (*Yakuwarigo*)**: Dialogue must reflect the character's personality, social standing, age, and emotional state. Russian possesses vast lexical, syntactic, and intonational registers; utilize them instead of relying on mechanical phonetic markers.
- **Spatial & Budget Restraints**: Game text is constrained by display hardware, dialogue box dimensions, and VWF (Variable Width Font) metrics. Russian translations typically expand by 20–30% compared to English and 50–70% compared to Japanese. Every string must respect its layout envelope.
- **Typographic & Orthographic Perfection**: Adhere strictly to Russian publishing standards (proper guillemets `«...»`, nested quotation marks `„...“`, em-dashes `—`, and consistent use of the letter `ё`).

---

## 2. Japanese to Russian (JA -> RU) Translation Standards

### 2.1 Role Language (*Yakuwarigo* / 役割語)

Japanese game dialogue relies heavily on conventional character tropes signaled by grammatical markers, sentence-final particles (*shūjoshi*), and copulas. In Russian, these tropes must be conveyed through lexical choice, sentence structure, archaisms, and conversational register, never through literal pseudo-Japanese markers.

| Archetype / Tropes | Japanese Linguistic Markers | Russian Stylistic Strategy | Source Example | Natural Russian Adaptation |
| :--- | :--- | :--- | :--- | :--- |
| **Archaic / Bushi / Samurai** | `でござる (de gozaru)`, `某・拙者 (sessha)`, `主・其方 (onushi/sonata)` | Use restrained archaic Russian, elevated vocabulary, and traditional respectful syntax. Avoid cartoonish pseudo-Slavic cliches (*«гой еси»*). | 拙者には解せぬでござる… | Мне сие неведомо… / Мой разум не постигнет этого… |
| **Elderly / Sage / Hermit** | `〜じゃ (jya)`, `わし (washi)`, `〜のう (nō)`, `おる (oru)` | Colloquial older register, mild folksy phrasing, sentence contractions, soft grandfatherly or sagely cadence. | わしにはもう無理じゃのう… | Эх, стар я стал для таких подвигов… |
| **Rough Masculine / Delinquent** | `だぜ (da ze)`, `〜ぞ (zo)`, `俺 (ore)`, `〜やがる (yagaru)`, `てめえ (temē)` | Punchy colloquial speech, imperative moods, gritty street vocabulary, aggressive brevity. | てめえ、何様のつもりだ！ | Ты кем себя возомнил, паскуда?! |
| **Refined / Ojou-sama / High Noble** | `〜ですわ (desu wa)`, `〜かしら (kashira)`, `私 (watakushi)`, `ごめんあそばせ` | High register, delicate phrasing, aristocratic restraint, polite rhetorical questions. | これでよろしくて？ | Полагаю, вы останетесь довольны? |
| **Soft Feminine / Gentle Heroine** | `あたし (atashi)`, `〜わ (wa)`, `〜の (no)`, `〜かしら (kashira)` | Melodic, gentle conversational flow, subtle diminutive nuances, warm cadence without infantile slurring. | どうしたの？元気ないわね… | Что с тобой? На тебе лица нет… |
| **Formal / Keigo / Butler / Knight** | `でございます (de gozaimasu)`, `いたします (itashimasu)`, `恐れ入ります` | Strictly formal Russian etiquette, bureaucratic/courtly deference, polite second-person plural (*«вы»*). | かしこまりました。直ちに向かいます。 | Будет исполнено. Немедленно выступаю. |
| **Kansai / Regional Dialects** | `〜や (ya)`, `〜へん (hen)`, `〜やねん (ya nen)`, `おおきに (ōkini)` | Lively, expressive, non-standard colloquial Russian with vivid phrasing. Do not use caricatured Ukrainian or southern Russian dialectal tokens unless deliberately parodying. | そんなん知らんへんわ！ | Да почём мне знать-то! / А мне-то откуда ведомо! |

### 2.2 First-Person and Second-Person Pronouns Matrix

Japanese explicitly codifies social distance, age, and gender through personal pronouns. Russian expresses these nuances through verb conjugations, forms of address, and vocabulary level. Do not mechanically insert *«я»* or *«ты»* whenever a Japanese pronoun appears; Russian frequently omits subject pronouns where context is clear.

#### First-Person Pronouns (*Ichidanshou*)

| Japanese Pronoun | Typical User & Nuance | Russian Equivalence & Strategy |
| :--- | :--- | :--- |
| **私 (Watashi)** | Standard polite, neutral adult male/female. | Neutral *я*. Frequently omitted when verb ending defines subject. |
| **私 (Watakushi)** | Highly formal, humble, aristocratic, official. | Formal *я*, elevated tone, official phrasing. |
| **僕 (Boku)** | Young male, gentle boy, modest young man. | Soft *я*, youthful cadence, polite modesty. |
| **俺 (Ore)** | Confident, casual, rough or masculine male. | Energetic, direct *я*; confident, assertive tone. |
| **あたし (Atashi)** | Casual, informal female. | Casual female *я*, relaxed rhythm. |
| **あたい (Atai)** | Tough, tomboyish or working-class female. | Sharp, colloquial female *я*; gritty register. |
| **わし (Washi)** | Elderly men, rural elders. | Aged *я*, grandfatherly vocabulary (*«дед»*, *«старик»*). |
| **拙者 (Sessha)** | Samurai, ninja, traditional warrior. | Modest warrior *я*, archaic phrasing (*«покорный слуга»*). |
| **余 / 朕 (Yo / Chin)** | Emperor, sovereign ruler, absolute monarch. | Royal *мы* (*«Мы повелеваем…»*) or stately authoritative *я*. |
| **我輩 / 吾輩 (Wagahai)** | Pompous gentleman, intellectual, haughty beast. | Bombastic, self-important *я*; slightly theatrical rhetoric. |
| **我ら / 我々 (Warera / Wareware)** | Collective group, order, military platoon. | *Мы*, *наш отряд*, *наша гильдия*, *наше братство*. |

#### Second-Person Pronouns (*Nidanshou*)

| Japanese Pronoun | Typical User & Nuance | Russian Equivalence & Strategy |
| :--- | :--- | :--- |
| **あなた (Anata)** | Polite or neutral "you", or spouse addressing husband. | Polite *вы* (or affectionate *ты/дорогой* between spouses). |
| **あんた (Anta)** | Familiar, casual, slightly blunt or dismissive "you". | Informal *ты*, blunt or impatient delivery. |
| **君 (Kimi)** | Superior to subordinate, elder to youth, close male friend. | Friendly or patronizing *ты*, paternalistic address. |
| **お前 (Omae)** | Casual masculine, rough, or authoritative address. | Direct *ты*, brusque delivery (*«слышь ты»*, *«парень»*). |
| **貴様 (Kisama)** | Hostile, contemptuous, aggressive enemy address. | Contemptuous *ты* accompanied by insults or venomous sarcasm. |
| **手前 (Teme)** | Extremely vulgar, enraged threat. | Aggressive address, snarling threats (*«урод»*, *«падаль»*). |
| **主 / 其方 (Onushi / Sonata)** | Archaic feudal address (lord to vassal, elder to youth). | Archaic *ты* with titles (*«сударь»*, *«друг мой»*). |
| **貴方様 (Anata-sama)** | High reverence, formal submission. | *Господин*, *ваша милость*, *госпожа*. |

### 2.3 Japanese Honorific Suffixes Policy

The treatment of honorific suffixes depends strictly on the narrative setting of the game:

1. **Authentic Japanese Setting** (e.g., *Persona*, *Yakuza / Like a Dragon*, *Ghost of Tsushima*, *Touhou Project*, contemporary school/urban Japan):
   - **Retain suffixes**: `-сан`, `-кун`, `-тян`, `-сама`, `-сэнсэй`, `-сэмпай`, `-доно`.
   - **Orthography**: Write with a hyphen in lowercase letters attached to the name: *Кэндзи-кун*, *Ая-тян*, *Мацуда-сан*, *Ода-сама*.
   - **Grammar integration**: Suffixes may decline according to Russian grammar when natural (*сказал Кэндзи-куну*, *увидел Аю-тян*), or remain invariant if preferred by project style guide.
2. **Western Fantasy, Sci-Fi, or Secondary World Setting** (e.g., *Final Fantasy*, *Dragon Quest*, *Chrono Trigger*, *Dark Souls*, *Tales of*):
   - **Do NOT retain Japanese suffixes**: Leaving `-san` or `-chan` in a medieval European castle or space station breaks immersion and reveals translation intermediate artifacts.
   - **Adapt contextually**:
     - `-sama` $\rightarrow$ *господин*, *госпожа*, *ваша милость*, *владыка*.
     - `-sensei` $\rightarrow$ *учитель*, *наставник*, *доктор*, *магистр*.
     - `-senpai` $\rightarrow$ *старший товарищ*, *братец*, *наставник*, or address by given name.
     - `-kun / -chan` $\rightarrow$ affectionate diminutives in Russian (*Клаудушка*, *малышка*, *дружок*), vocatives (*дружище*, *братец*), or simply the character's base name.

### 2.4 Transliteration System & Canon Precedence

1. **Polivanov Baseline**: The practical Cyrillization of Japanese names must follow the Polivanov system:
   - `し (shi) -> си` (not *ши*)
   - `ち (chi) -> ти` (not *чи*)
   - `じ (ji) -> дзи` (not *джи*)
   - `つ (tsu) -> цу` (not *тсу*)
   - `しゃ / しゅ / しょ (sha/shu/sho) -> ся / сю / сё`
   - `ちゃ / ちゅ / ちょ (cha/chu/cho) -> тя / тю / тё`
   - `じゃ / じゅ / じょ (ja/ju/jo) -> дзя / дзю / дзё`
   - `ふ (fu) -> фу`
   - Double vowels: `とうきょう -> Токио / То̄кё̄`, long vowels transliterated phonetically per project convention.
2. **Strict Canon Precedence Rule**: Official localizations, established canon, and deeply rooted franchise naming conventions strictly override mechanical Polivanov transliteration:
   - *Final Fantasy VII*: **Шинра** (not *Синра*), **Клауд** (from *Cloud*, not *Кураудо*), **Сефирот** (from *Sephiroth*, not *Сэфиросу*).
   - *Metal Gear*: **Снейк** (not *Сунэ̄ку*), **Отакон** (not *Отакон*).
   - *Chrono Trigger*: **Кроно** (not *Куроно*), **Магл** (not *Ма̄гусу* / Magus).
3. **Etymological Source Language Principle**: When Katakana represents a foreign loanword (English, German, French, Latin, Norse), translate or transliterate directly from the original etymological origin, NOT phonetically from Japanese phonotactics:
   - `フェニックスの尾 (fenikkusu no o)` $\rightarrow$ **Перо феникса** (translating English *Phoenix Down*, where Japanese *尾* means tail/feather).
   - `ミスリル (misuriru)` $\rightarrow$ **Мифрил** (from Tolkien's *Mithril*, not *Мисруру*).
   - `エーテル (ēteru)` $\rightarrow$ **Эфир** (from German/Latin *Aether*, not *Этеру*).

### 2.5 Kanji / Furigana (*Gikun* / 義訓) and Dual Semantics

Japanese game scripts frequently employ *Gikun* or *Ateji*: kanji characters express a profound philosophical or visual concept, while ruby furigana specifies the phonetic reading, often a modern loanword or pun.

- **Example**: `宝具` (kanji: *Sacred Treasure*) annotated with `ノーブル・ファンタズム` (furigana: *Noble Phantasm*).
- **Example**: `宇宙` (kanji: *Space/Cosmos*) annotated with `そら` (furigana: *Sky*).
- **Translation Strategy**:
  1. Determine whether the lore requires the visual concept or the phonetic term.
  2. If both meanings carry critical narrative weight, blend them descriptively: *«Благородный Фантазм (священная реликвия)»*.
  3. If space is constrained, prioritize the spoken audio dialogue term that the voice actor actually pronounces.

---

## 3. English to Russian (EN -> RU) Translation Standards

### 3.1 Eradication of Translationese ("Переводяз") & Syntactic Anglosperms

English and Russian possess vastly different grammatical architectures. Direct syntactic calques degrade prose quality. The following patterns must be rigorously eliminated:

#### A. Overuse of Possessive Pronouns (*свой, его, её, их*)
In English, possessive pronouns are syntactically mandatory (*he put his hands in his pockets*). In Russian, possessing one's own body parts and equipment is implicit.
- **Incorrect (Calque)**: *Он вытащил свой меч и посмотрел на своего врага.*
- **Correct (Natural Russian)**: *Он обнажил меч и взглянул на врага.*
- **Incorrect (Calque)**: *Она открыла свои глаза.*
- **Correct (Natural Russian)**: *Она открыла глаза.*

#### B. Clunky Passive Voice Constructions
English technical and fantasy texts rely heavily on passive verbs (*The castle was overrun by orcs*). Russian favors active voice or impersonal reflexive constructions.
- **Incorrect (Calque)**: *Город был атакован драконом.*
- **Correct (Active)**: *На город напал дракон. / Дракон разорил город.*
- **Incorrect (Calque)**: *Это зелье может быть куплено у торговца.*
- **Correct (Natural)**: *Это зелье продаётся у купца. / Это зелье можно купить у торговца.*

#### C. Excessive Participles and Verbal Nouns
Chains of participles (*-вший, -щийся*) and heavy abstract nouns (*-ние, -ование*) turn dynamic narrative into dry legal documentation.
- **Incorrect**: *Герой, являющийся обладателем меча, совершил убийство дракона.*
- **Correct**: *Герой, владеющий мечом, сразил дракона.*

#### D. Word Order and Communicative Dynamism (*Тема и рема*)
English enforces rigid Subject-Verb-Object (SVO) order. Russian places new, emphasis-carrying information (*rheme*) toward the end of the sentence.
- **English**: *A sudden explosion shook the tower.*
- **Incorrect (Rigid SVO)**: *Внезапный взрыв потряс башню.*
- **Correct (Dynamic)**: *Башню сотряс внезапный взрыв.*

### 3.2 Context Disambiguation for Ambiguous Gaming Lexicon

Gaming source texts frequently contain polysemous single-word commands, menu labels, and battle log entries. Translating these terms without context inspection leads to legendary localization blunders.

| Term | Context A (Correct Meaning & Translation) | Context B (Alternative / Mistranslation Hazard) | Context C (Engine / System Function) |
| :--- | :--- | :--- | :--- |
| **Miss** | Combat failure: **Промах** | Emotional state: **Скучать** (*Never use in combat!*) | Title of address: **Мисс** (*Miss Fortune*) |
| **Back** | Navigation UI: **Назад** | Body anatomy: **Спина** | Tactical position: **Тыл / Задний ряд** (*Back row*) |
| **Save** | Game state persistence: **Сохранить** | Rescue / survival: **Спасти** | Religious / magic blessing: **Избавление** |
| **Cast** | Magic spell invocation: **Сотворить / Применить** | Item discard or dice: **Бросить / Метнуть** | Actor list / dramatis personae: **В ролях** |
| **Equip** | Action verb: **Экипировать / Надеть / Взять** | Menu category noun: **Снаряжение** | State attribute: **Надето** |
| **Attack** | Battle command: **Атаковать** | Character attribute: **Атака** | Event occurrence: **Нападение** |
| **Defend** | Battle command: **Защищаться** | Character attribute: **Защита** | Tactical stance: **Оборона** |
| **Party** | Companion roster: **Отряд / Группа** | Festive gathering: **Праздник / Вечеринка** | Political faction: **Партия** |
| **Check** | Inspection command: **Осмотреть / Изучить** | State verification: **Проверить** | Chess / financial: **Шах / Чек** |
| **Clear** | Stage completion: **Пройдено / Завершено** | Storage deletion: **Очистить** | Atmospheric condition: **Ясно** |
| **Critical** | Combat hit: **Критический удар (Крит)** | Health condition: **Опасное состояние** | Logic requirement: **Критически важный** |
| **Rest** | Recovery action: **Отдохнуть / Привал** | Remaining fraction: **Остаток** | Stand / support: **Подставка** |
| **Drop** | Defeated enemy reward: **Добыча / Трофей** | Action verb: **Бросить / Выбросить** | Environmental fall: **Падение** |
| **Flee / Run**| Battle retreat: **Бежать / Отступить** | System execution: **Запуск** | Physical sprint: **Бег** |

### 3.3 Speech Rhythm, Cadence, and Natural Russian Dialogue Flow

1. **Dramatic Pacing**: Match sentence length to scene tension. Fast-paced combat and urgent warnings must use short, sharp clauses. Emotional soliloquies should employ rhythmic, melodic phrasing.
2. **Idiomatic Equivalents**: Never translate English idioms literally.
   - *«It's raining cats and dogs»* $\rightarrow$ *«Льёт как из ведра»* (not *«падают кошки и собаки»*).
   - *«Bite the bullet»* $\rightarrow$ *«Стиснуть зубы»* (not *«укусить пулю»*).
   - *«Break a leg»* $\rightarrow$ *«Ни пуха ни пера»* (not *«сломай ногу»*).
3. **Conversational Interjections**: Translate *«Well...»*, *«Hey!»*, *«Damn!»*, *«Oh boy»* according to speaker persona:
   - *Ну... / Так вот... / Послушай! / Проклятье! / Тьфу ты! / Вот те раз!*

---

## 4. Engineering Integrity of Control Codes, Bytecode Tags & Format Strings

Game translation occurs inside active executable environments. Corrupted tags crash script virtual machines, truncate memory buffers, and freeze rendering pipelines.

### 4.1 Immutability of Engine Control Tags

Every tag enclosed in curly brackets `{...}`, square brackets `[...]`, angle brackets `<...>`, or percent sequences `%...` must remain byte-for-byte identical to the source.

```text
CRITICAL ENGINE TAGS LIST:
- Actors & Names:     {HERO}, {NAME 1}, {LEAD}, {CRONO}, {MARLE}
- Color Directives:   {COLOR 0}, {COLOR 2}, <color=#ff0000>, </color>
- Flow & Pagination:  {LINE}, {PAGE}, {CLEAR}, \n, \r, \f
- Script Delays:      {WAIT 10}, {PAUSE 30}, {DELAY 5}
- Audio Cues:         {SFX 12}, {BGM_FADE}, {VOICE 4}
- Button Prompts:     {KEY_A}, {BTN_START}, {PAD_UP}
- Number Containers:  [ITEM %d], [VALUE:1], [VAR 12]
```

- **Tag Integrity Commandments**:
  1. **Do not translate tag names**: `{COLOR 1}` must NOT become `{ЦВЕТ 1}`.
  2. **Do not modify casing**: `{hero}` is invalid if source specifies `{HERO}`.
  3. **Do not add or delete spaces**: `{WAIT 10}` must NOT become `{WAIT10}` or `{WAIT  10}`.
  4. **Do not drop tags**: If source contains 3 tags, the target string must contain the exact same 3 tags.

### 4.2 Formatting Specifiers & Positional Reordering

When games construct dynamic strings via `sprintf`, `printf`, or engine string formatters, format specifiers (`%s`, `%d`, `%f`, `{0}`, `{1}`) are replaced at runtime with memory variables.

#### The Word-Order Dilemma in Russian
Russian synthetic grammar often requires placing the object before the subject, or vice versa, to achieve natural emphasis:

- **Source (EN)**: `"%s defeated %s!"` (Arg 1 = Hero, Arg 2 = Boss)
- **Natural Russian Option 1 (Passive/Object First)**: `"%2$s был повержен %1$s!"`
- **Natural Russian Option 2 (Active Reorder)**: `"%1$s одолел грозного врага: %2$s!"`

#### Strict Rule on Positional Arguments
1. **Positional Specifiers (`%1$s`, `%2$d`)**: Use positional notation ONLY if verified that the game engine runtime supports POSIX / IEEE positional specifiers.
2. **Unsupported Positional Runtimes**: If working with legacy engines (e.g., custom 16-bit SNES or classic NDS assembly `sprintf`) that do NOT support `%1$s`, you **MUST NOT** change the sequence of format tokens. Maintain original sequence `%s ... %s` and restructure Russian grammar around that fixed order:
   - *«%s одерживает победу над %s!»* (Arg 1: Hero, Arg 2: Boss).

#### Gender and Grammatical Agreement with Dynamic Tokens
When `%s` represents an item, spell, or hero with dynamic gender (masculine, feminine, neuter):
- Avoid gendered verb past tenses (*«%s был найден»* fails if item is *«Книга»*).
- Use gender-neutral syntax or noun appositions:
  - **Preferred**: *«Найден предмет: %s!»* or *«Получено: %s!»*
  - **Avoid**: *«%s найден(а)!»*

### 4.3 Escape Sequences and Whitespace Preservation

- Hard line breaks `\n` and tab characters `\t` must be preserved exactly as configured by the engine.
- Trailing spaces, leading spaces, and double space dividers often serve as sprite padding in retro games; never strip them indiscriminately.

### 4.4 Dynamic Variable Tokens & VWF Budgeting (nds-romhacking-plugin v1.1.0+ Synergy)

When games insert runtime player names, stats, items, or locations via script tokens (e.g. `{HERO_NAME}`, `{PLAYER_NAME}`, `{TARGET}`, `{VARIABLE}`, `{ITEM_NAME}`, `{LOCATION}`, `{VALUE}`, `{NUMBER}`, `{HERO}`, `{PLAYER}`, `{VAR_1}`, `{VAR_2}`, `{NAME 1}`, `{NAME 2}`), these tokens are NOT zero-width formatting codes:

- **Nominal Character & Pixel Budget Reservation**:
  - In `scripts/l10n_validator.py`, all standard variable tokens in `DEFAULT_VARIABLE_TOKENS` (or customized via `--var-tokens`) reserve a configurable nominal character budget (`--var-len`, default: **8 characters**).
  - Never strip variable tokens to zero width during layout checks. A string like `"Привет, {HERO_NAME}!"` consumes $8 \text{ (base)} + 8 \text{ (token)} + 2 \text{ (punct)} = 18$ characters in layout calculations.
  - In proportional VWF engines (such as NDS NFTR fonts managed by `nds-romhacking-plugin`), tokens correspond to fixed nominal pixel width reservations (e.g., `DEFAULT_HERO_NAME_WIDTH_PX = 30-48px`), preventing dialogue box text clipping when the player chooses an 8-character Cyrillic hero name.
- **Generic NDS Binary Container Flow**:
  - In modern ROM hacking pipelines (`nds-romhacking-plugin` v1.1.0+), game text is stored in generic multi-language binary containers supporting arbitrary language counts (`lang_count`, from 1 to $N$) and dynamic text entry delimiters (e.g. `\x02` or `\x00`).
  - When round-tripping localized dialogue dumps through the L10N QA validator, ensure all entries preserve delimiter semantics and variable token parity across all active language slots.

---

## 5. Layout Budget, Line Constraints & Visual Typography

### 5.1 Text Expansion Management

Russian text is structurally longer than Japanese and English:

$$\text{Length}_{\text{RU}} \approx 1.25 \times \text{Length}_{\text{EN}}$$
$$\text{Length}_{\text{RU}} \approx 1.65 \times \text{Length}_{\text{JA}}$$

#### Compression Techniques for Russian Game Text
1. **Prefer Active Verbs**: Replace verbal nouns (*«осуществление атаки»* $\rightarrow$ *«атака»*).
2. **Eliminate Wordy Filler**: Trim pleonasms (*«в конечном итоге»* $\rightarrow$ *«в итоге»*, *«в этот самый момент»* $\rightarrow$ *«тогда»*).
3. **Select Concise Synonyms**:
   - *«Восстановление здоровья»* (24 chars) $\rightarrow$ *«Лечение»* (7 chars).
   - *«Оборонительная позиция»* (22 chars) $\rightarrow$ *«Защита»* (6 chars).
   - *«Увеличивает силу атаки»* (22 chars) $\rightarrow$ *«Повышает атаку»* (14 chars).

### 5.2 Dialogue Box Line-Wrapping and Pagination Conventions

1. **Character-Per-Line (CPL) Envelope**:
   - Classic Retro RPGs (NES, SNES, GBA, NDS): typically 28–36 characters per line.
   - High-Definition Modern RPGs: typically 45–60 characters per line.
2. **Line Count Limits**:
   - Standard dialogue boxes display 2, 3, or 4 lines simultaneously.
   - Inserting an extra `\n` without a `{PAGE}` or `{CLEAR}` tag causes text to scroll upwards, cutting off the first line, or clips off-screen entirely.
3. **Orphan Control & Visual Ragging**:
   - Never leave solitary prepositions (*в, с, к, о, из, за, на*) at the end of a line. Connect them to the following word with a non-breaking space if the engine supports it, or wrap the preposition to the next line.
   - Avoid leaving a single short word alone on the final line of a dialogue box.

### 5.3 Proportional Fonts (VWF) vs Monospaced Fonts

In Variable Width Font (VWF) rendering engines, character width is measured in pixels rather than character counts.
- **Wide Cyrillic Glyphs**: Letters `Ж`, `Ш`, `Щ`, `Ы`, `Ю`, `Ф`, `М` occupy 8–12 pixels in a 10px-tall font, whereas Latin `i`, `l`, `t` occupy only 3–5 pixels.
- A Russian line of 30 characters containing multiple wide Cyrillic glyphs will exceed screen bounds even if an English 30-character line fits comfortably.
- Always perform pixel width validation via `scripts/l10n_validator.py` or engine preview before finalizing binary insertion.

---

## 6. Russian Typographical & Orthographic Standards

### 6.1 Quotation Marks and Nested Quotes

- **Primary Quotes**: French guillemets (*«ёлочки»*): `«...»`.
- **Nested Quotes**: German quotation marks (*„лапки“*): `„...“`.
- **Strict Prohibition**: Straight ASCII typewriter quotes (`"..."`) and English curly quotes (`“...”`) are prohibited in final localized Russian game script.
  - *Correct*: `«Он прокричал: „Берегись дракона!“ — и обнажил клинок.»`
  - *Incorrect*: `"Он прокричал: "Берегись дракона!" - и обнажил клинок."`

### 6.2 Dashes, Hyphens, and Dialogue Punctuation

- **Em-Dash (`—`, U+2014)**:
  - Used for dialogue speech initiation: `— Кто здесь? — спросил рыцарь.`
  - Used for sentence breaks, parenthetical pauses, and explanatory clauses: `Меч правосудия — главное оружие паладина.`
  - Must be surrounded by single spaces when dividing sentence parts: `Свет победит — мы верим в это.`
- **En-Dash (`–`, U+2013)**:
  - Used for numerical spans and ranges without spaces: `10–20 HP`, `100–200 монет`.
- **Hyphen (`-`, ASCII 0x2D)**:
  - Used exclusively inside compound words: `меч-кладенец`, `что-то`, `темно-синий`, `Санкт-Петербург`.
- **Ellipsis (`…`, U+2026)**:
  - Prefer single unicode ellipsis `…` unless the target game font only renders three ASCII periods `...`.

### 6.3 Letter "Ё" Orthography Policy

- **Full Consistent "Ё-фикация"**: The letter `ё` (and uppercase `Ё`) must be written consistently in all narrative dialogues, UI menus, lore descriptions, and character registries.
  - *Correct*: `ещё`, `тёмный`, `берёза`, `вертолёт`, `орден`, `звёзды`, `слёзы`.
  - *Incorrect*: `еще`, `темный`, `береза`, `вертолет`, `звезды`, `слезы`.
- **Hardware Font Exception**: If and only if the underlying binary game font strictly omits the glyphs `Ё` / `ё` from its tilemap or charmap, text may be converted to `е` during final binary synthesis, but master project repositories must maintain pristine `ё` spelling.

### 6.4 Numbers, Units, and Currency

- **Space between number and unit**: Always insert a space between numbers and their measurement units or currencies: `50 HP`, `100 MP`, `500 зол.`, `12 км`.
- **Ordinal Numbers**: Use standard Russian inflection suffixes:
  - *1-й этаж*, *2-я попытка*, *3-е подземелье*, *90-е годы*.
- **Large Numbers**: Group thousands with thin spaces or dots per project convention: `10 000 золотых`.

---

## 7. Verification Checklist for Localizers and Subagents

Before submitting any translated script or commit, verify against this 6-point checklist:

- [ ] **1. Tag Parity**: Every `{TAG}`, `\n`, `%s`, and bracketed code matches the source exactly.
- [ ] **2. No Translationese**: No gratuitous *«свой»*, awkward passive verbs, or robotic SVO word orders.
- [ ] **3. Disambiguated Terms**: Gaming words (*Miss*, *Back*, *Save*, *Cast*, *Equip*) match their specific gameplay context.
- [ ] **4. Voice Consistency**: Character register respects *Yakuwarigo* or source personality traits.
- [ ] **5. Budget & Width**: Line length fits dialogue box constraints; no overflowing lines.
- [ ] **6. Typography & Orthography**: Proper guillemets `«...»`, em-dashes `—`, and complete `ё`-fication applied.
