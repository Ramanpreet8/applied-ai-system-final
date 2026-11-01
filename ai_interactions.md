# AI Interactions Log

## Challenge 1: Advanced Song Features

### Prompts used

1. **Expand the dataset:** Add popularity (0–100), release decade, 2–3 pipe-separated mood tags, explicit (0/1), and instrumentalness (0.0–1.0) to every song, preserving the existing columns.
2. **Update the loader:** Parse popularity, release decade, and explicit as integers; instrumentalness as a float; and mood tags as a list split on `|`, without changing existing conversions.
3. **Update scoring and `UserProfile`:** Add up to 0.5 for popularity closeness, 0.5 for a decade match, up to 1.0 for overlapping mood tags, and up to 0.3 for instrumentalness closeness. Include a reason for each score contribution and preserve the existing score rules.
4. **Update profiles:** Supply the new preference fields in each CLI profile.
5. **Document and verify:** Record the workflow and manually check that a song's total matches its listed score reasons.

### Changes generated

- Added five columns and values for all 18 songs. The original columns and their values were preserved.
- Extended `load_songs` to convert the added numeric columns and split mood tags into lists.
- Added the new preferences to `UserProfile` and to each CLI profile.
- Added popularity, decade, mood-tag overlap, and instrumentalness contributions with readable score reasons.
- Left the existing genre, mood, and energy rules unchanged.

### Manual Verification Notes

- Ran `python3 -m src.main`; it loaded all 18 songs and returned recommendations for all five profiles.
- Checked the CSV headers, row count, popularity and explicit ranges, instrumentalness ranges, and that every mood tag field has two or three tags.
- For the High-Energy Pop profile, Sunrise City scored 6.00. Its displayed reasons add to 6.00: 1.00 genre + 1.00 mood + 1.74 energy + 0.48 popularity + 0.50 decade + 1.00 mood-tag overlap + 0.28 instrumentalness.
- The first run exposed a loader bug: instrumentalness was still a string, so scoring it against a float raised a `TypeError`. I added it to the existing float-field conversion set and reran the CLI successfully.
- I found no other issues during these checks.

---

## Challenge 2: Multiple Scoring Modes

### Design pattern chosen

I used a Strategy-style design with a dictionary of named weight configurations. The `genre_first`, `mood_first`, and `energy_focused` configurations hold the genre, mood, and energy weights. `score_song` applies the selected configuration, and `recommend_songs` passes the mode through while ranking. This keeps the scoring implementation in one place and makes a new mode a configuration entry.

### Alternatives considered

- Separate scoring functions would keep each strategy distinct, but repeat the shared feature scoring and explanation logic.
- An `if`/`else` branch for every mode is straightforward for three choices, but grows into repeated conditionals as more modes are added.
- A weight-config dictionary was the smallest modular approach for this project; separate strategy classes could be considered if modes later require substantially different logic.

### How AI contributed to the brainstorm

The AI compared configuration dictionaries, separate scoring functions, and conditional branching, including the trade-off between simplicity and extensibility. It recommended keeping the scoring algorithm shared and moving only the weights into named configurations. I used that recommendation to implement the modes and add a CLI switch.

### Verification results

Ran `python3 -m src.main --mode all` and compared the High-Energy Pop profile in all three modes. Sunrise City stayed first, while mood-first moved Rooftop Lights above Gym Hero; energy-focused raised energy similarity contributions and changed the scores. The mode weights and score sums were checked directly, and `python3 -m src.main --mode mood_first` confirmed the CLI switch.

```text
High-Energy Pop - Mode: genre_first
1. Sunrise City - Score: 7.13
   Reasons: genre match (+3.0), mood match (+1.0), energy similarity (+0.87), popularity close (+0.48), release decade match (+0.50), mood tags overlap (+1.00), instrumentalness close (+0.28)
2. Gym Hero - Score: 5.23
   Reasons: genre match (+3.0), energy similarity (+0.98), popularity close (+0.48), release decade match (+0.50), mood tags overlap (+0.00), instrumentalness close (+0.27)
3. Rooftop Lights - Score: 3.56
   Reasons: mood match (+1.0), energy similarity (+0.81), popularity close (+0.46), release decade match (+0.50), mood tags overlap (+0.50), instrumentalness close (+0.28)
4. Neon Parade - Score: 2.57
   Reasons: energy similarity (+0.86), popularity close (+0.43), release decade match (+0.50), mood tags overlap (+0.50), instrumentalness close (+0.28)
5. Iron Horizon - Score: 2.18
   Reasons: energy similarity (+0.99), popularity close (+0.42), release decade match (+0.50), mood tags overlap (+0.00), instrumentalness close (+0.27)

High-Energy Pop - Mode: mood_first
1. Sunrise City - Score: 7.13
   Reasons: genre match (+1.0), mood match (+3.0), energy similarity (+0.87), popularity close (+0.48), release decade match (+0.50), mood tags overlap (+1.00), instrumentalness close (+0.28)
2. Rooftop Lights - Score: 5.56
   Reasons: mood match (+3.0), energy similarity (+0.81), popularity close (+0.46), release decade match (+0.50), mood tags overlap (+0.50), instrumentalness close (+0.28)
3. Gym Hero - Score: 3.23
   Reasons: genre match (+1.0), energy similarity (+0.98), popularity close (+0.48), release decade match (+0.50), mood tags overlap (+0.00), instrumentalness close (+0.27)
4. Neon Parade - Score: 2.57
   Reasons: energy similarity (+0.86), popularity close (+0.43), release decade match (+0.50), mood tags overlap (+0.50), instrumentalness close (+0.28)
5. Iron Horizon - Score: 2.18
   Reasons: energy similarity (+0.99), popularity close (+0.42), release decade match (+0.50), mood tags overlap (+0.00), instrumentalness close (+0.27)

High-Energy Pop - Mode: energy_focused
1. Sunrise City - Score: 5.87
   Reasons: genre match (+0.5), mood match (+0.5), energy similarity (+2.61), popularity close (+0.48), release decade match (+0.50), mood tags overlap (+1.00), instrumentalness close (+0.28)
2. Gym Hero - Score: 4.70
   Reasons: genre match (+0.5), energy similarity (+2.94), popularity close (+0.48), release decade match (+0.50), mood tags overlap (+0.00), instrumentalness close (+0.27)
3. Rooftop Lights - Score: 4.68
   Reasons: mood match (+0.5), energy similarity (+2.43), popularity close (+0.46), release decade match (+0.50), mood tags overlap (+0.50), instrumentalness close (+0.28)
4. Neon Parade - Score: 4.29
   Reasons: energy similarity (+2.58), popularity close (+0.43), release decade match (+0.50), mood tags overlap (+0.50), instrumentalness close (+0.28)
5. Iron Horizon - Score: 4.16
   Reasons: energy similarity (+2.97), popularity close (+0.42), release decade match (+0.50), mood tags overlap (+0.00), instrumentalness close (+0.27)
```

### Manual Verification Notes

<!-- Add any additional manual checks or issues you noticed. -->

---

## Challenge 3: Diversity Penalty

### Prompt used

> Implement the diversity penalty in `recommend_songs`: pick songs one at a time, always taking the highest adjusted score, and after each pick apply a penalty to remaining songs with the same artist (-1.0) or same genre (-0.5). Add a parameter `diversity=True` (default True) so I can turn it off to compare. Add a reason like "diversity penalty: artist already recommended (-1.0)" when applied. Add a test profile in main.py that would normally return several songs by the same artist or genre, and show its top five with diversity ON vs OFF.

### Greedy re-ranking approach

The recommender scores every song with the selected scoring mode, then repeatedly recalculates each remaining song's adjusted score against the artists and genres already selected. It picks the highest adjusted score, records the applied penalties in the reasons, and updates the selected artist and genre counts. With diversity disabled, it returns the original score-sorted results without penalties.

### Manual Verification Notes

For the Low-Energy Ambient Diversity Stress Test, diversity OFF returned Midnight Coding and Focus Flow by the same artist, LoRoom, and included three lofi tracks. With diversity ON, Focus Flow was replaced by Night Drive Loop; the list gained one unique artist and one unique genre. Library Rain's adjusted score includes the visible `diversity penalty: genre already recommended (-0.5)` reason. The OFF ranking keeps unadjusted scores, and ON scores match base scores minus listed penalties within the two-decimal display rounding.

<!-- Add any other manual checks or issues you would like to record. -->

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agentic Workflow (SF8)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

<!-- Describe the goal you asked the agent to accomplish -->

**Prompts used:**

<!-- Paste the key prompts you gave the agent -->

**What did the agent generate or change?**

<!-- List the files edited, code generated, or commands run -->

**What did you verify or fix manually?**

<!-- Describe anything the agent got wrong or that required human review -->

---

## Design Pattern (SF10)

> Document how AI helped you choose or implement a design pattern.

**Which design pattern did you use?**

<!-- e.g., Strategy, Factory, Observer, etc. -->

**How did AI help you brainstorm or implement it?**

<!-- Describe the conversation or suggestions that led to your decision -->

**How does the pattern appear in your final code?**

<!-- Point to the relevant class or method -->

---

## Challenge 4: Visual Summary Table

### Prompts used

> Suggest a way to display my top recommendations as a formatted table in the terminal using the tabulate library or simple ASCII formatting. The table must include columns for Rank, Title, Artist, Score, and Reasons (the reasons for each score). Compare tabulate vs. plain ASCII and recommend one.
>
> Implement your recommendation in `main.py`. Use tabulate (add it to requirements.txt) with the "grid" format. Wrap the Reasons column so long text doesn't break the table. Print one table per user profile with the mode name in the header.

### What the AI generated

The AI recommended `tabulate` over hand-built ASCII because it formats columns and grid borders consistently with less custom code; plain ASCII would avoid a dependency but require maintaining column widths and borders manually. It added `tabulate` to the requirements, formats recommendations as grid tables with Rank, Title, Artist, Score, and Reasons columns, and wraps the reasons text to fit the terminal display. The CLI prints a separate table for each profile and active mode.

### Manual Verification Notes

Installed requirements in a temporary virtual environment and ran `python3 -m src.main`. The output contained 17 grid tables: one for each of five profiles across three modes, plus the diversity ON/OFF comparison. Checked that every table includes the five requested columns and that long Reasons values wrap within their cells. The README sample is copied from the actual High-Energy Pop / genre-first output. No implementation issues were found.

---

## Challenge 5: VibeFinder Agent CLI

### Prompt used

> Create `src/agent_cli.py`. It should accept a natural-language request from command-line arguments, load the song catalog, run the agent, print a recommendations table plus warnings and the reasoning trace, and write trace messages to `logs/agent_trace.log`. Catch `GuardrailError` for blocked requests.

### What the AI generated

Added a CLI entry point runnable with `python -m src.agent_cli "<request>"`. It prints the selected strategy, confidence, recommendation table, any warnings, and the agent trace. The logging setup creates `logs/` and appends agent trace messages to `logs/agent_trace.log`.

### Captured output

```text
$ python -m src.agent_cli "I need chill music to study at night"
Request: I need chill music to study at night
Strategy used: mood_first | Confidence: 0.51
| Rank   | Title              | Artist         | Score   |
|--------|--------------------|----------------|---------|
| 1      | Midnight Coding    | LoRoom         | 5.00    |
| 2      | Spacewalk Thoughts | Orbit Bloom    | 4.98    |
| 3      | Library Rain       | Paper Lanterns | 4.04    |
| 4      | Night Drive Loop   | Neon Echo      | 1.73    |
| 5      | Rooftop Lights     | Indigo Parade  | 1.67    |

Agent trace:
 INPUT guardrail passed: 'I need chill music to study at night'
 PLAN profile = {'genre': None, 'mood': 'chill', 'energy': 0.3, 'target_popularity': 60, 'preferred_decade': 2020, 'preferred_mood_tags': ['chill'], 'target_instrumentalness': 0.3, 'exclude_explicit': False}
 ACT attempt 1 mode=genre_first: top='Midnight Coding' confidence=0.31 problems=none
 REVISE confidence 0.31 too low or problems found -> trying next strategy
 ACT attempt 2 mode=mood_first: top='Midnight Coding' confidence=0.51 problems=none
 VERIFY attempt 2 accepted (confidence >= 0.5)
```

```text
$ python -m src.agent_cli "clean pop party music"
Request: clean pop party music
Strategy used: genre_first | Confidence: 0.56
| Rank   | Title           | Artist            | Score   |
|--------|-----------------|-------------------|---------|
| 1      | Gym Hero        | Max Pulse         | 5.04    |
| 2      | Sunrise City    | Neon Echo         | 4.53    |
| 3      | Neon Parade     | The Brass Circuit | 2.07    |
| 4      | Rooftop Lights  | Indigo Parade     | 1.99    |
| 5      | Midnight Coding | LoRoom            | 1.64    |

Agent trace:
 INPUT guardrail passed: 'clean pop party music'
 PLAN profile = {'genre': 'pop', 'mood': None, 'energy': 0.9, 'target_popularity': 60, 'preferred_decade': 2020, 'preferred_mood_tags': [], 'target_instrumentalness': 0.3, 'exclude_explicit': True}
 GUARD clean-music request: removed 3 explicit songs
 ACT attempt 1 mode=genre_first: top='Gym Hero' confidence=0.56 problems=none
 VERIFY attempt 1 accepted (confidence >= 0.5)
```

```text
$ python -m src.agent_cli "polka"
Request: polka
Strategy used: energy_focused | Confidence: 0.29
| Rank   | Title             | Artist       | Score   |
|--------|-------------------|--------------|---------|
| 1      | Midnight Coding   | LoRoom       | 3.88    |
| 2      | Island Lanterns   | Coral Avenue | 3.67    |
| 3      | Blue Hour Train   | Ellis Monroe | 3.56    |
| 4      | Night Drive Loop  | Neon Echo    | 3.43    |
| 5      | Backroad Postcard | June Wilder  | 3.43    |
WARNING: No genre or mood recognised; ranking by energy and other features only.
WARNING: Low confidence (0.29); showing the best of 3 strategies.

Agent trace:
 INPUT guardrail passed: 'polka'
 PLAN profile = {'genre': None, 'mood': None, 'energy': 0.5, 'target_popularity': 60, 'preferred_decade': 2020, 'preferred_mood_tags': [], 'target_instrumentalness': 0.3, 'exclude_explicit': False}
 ACT attempt 1 mode=genre_first: top='Midnight Coding' confidence=0.13 problems=none
 REVISE confidence 0.13 too low or problems found -> trying next strategy
 ACT attempt 2 mode=mood_first: top='Midnight Coding' confidence=0.13 problems=none
 REVISE confidence 0.13 too low or problems found -> trying next strategy
 ACT attempt 3 mode=energy_focused: top='Midnight Coding' confidence=0.29 problems=none
 REVISE confidence 0.29 too low or problems found -> trying next strategy
 VERIFY no attempt passed; using best (mode=energy_focused, confidence=0.29)
```

```text
$ python -m src.agent_cli ""
Guardrail blocked this request: Request is empty. Try: 'chill lofi music to study'.
Exit status: 1
```

### Manual verification notes

Ran all four commands against `data/songs.csv`. The chill request revised from `genre_first` to `mood_first` and was accepted at 0.51 confidence. The clean request removed three explicit songs before recommending. The unrecognized `polka` request tried all three strategies and displayed low-confidence warnings. The empty request was blocked and exited with status 1. Confirmed the valid runs were written to `logs/agent_trace.log`; the blocked empty request was rejected before an agent trace could be logged.

---

## Final Project: Agent Reasoning Traces

These are the actual trace lines from `run_agent` using the current 18-song catalog.

### Study request: revise to a strategy that passes

```text
INPUT guardrail passed: 'I need chill music to study at night'
PLAN profile = {'genre': None, 'mood': 'chill', 'energy': 0.3, 'target_popularity': 60, 'preferred_decade': 2020, 'preferred_mood_tags': ['chill'], 'target_instrumentalness': 0.3, 'exclude_explicit': False}
ACT attempt 1 mode=genre_first: top='Midnight Coding' confidence=0.31 problems=none
REVISE confidence 0.31 too low or problems found -> trying next strategy
ACT attempt 2 mode=mood_first: top='Midnight Coding' confidence=0.51 problems=none
VERIFY attempt 2 accepted (confidence >= 0.5)
```

### Clean request: filter the catalog before scoring

```text
INPUT guardrail passed: 'clean pop party music'
PLAN profile = {'genre': 'pop', 'mood': None, 'energy': 0.9, 'target_popularity': 60, 'preferred_decade': 2020, 'preferred_mood_tags': [], 'target_instrumentalness': 0.3, 'exclude_explicit': True}
GUARD clean-music request: removed 3 explicit songs
ACT attempt 1 mode=genre_first: top='Gym Hero' confidence=0.56 problems=none
VERIFY attempt 1 accepted (confidence >= 0.5)
```

### Unrecognized request: try all strategies and report low confidence

```text
INPUT guardrail passed: 'polka'
PLAN profile = {'genre': None, 'mood': None, 'energy': 0.5, 'target_popularity': 60, 'preferred_decade': 2020, 'preferred_mood_tags': [], 'target_instrumentalness': 0.3, 'exclude_explicit': False}
ACT attempt 1 mode=genre_first: top='Midnight Coding' confidence=0.13 problems=none
REVISE confidence 0.13 too low or problems found -> trying next strategy
ACT attempt 2 mode=mood_first: top='Midnight Coding' confidence=0.13 problems=none
REVISE confidence 0.13 too low or problems found -> trying next strategy
ACT attempt 3 mode=energy_focused: top='Midnight Coding' confidence=0.29 problems=none
REVISE confidence 0.29 too low or problems found -> trying next strategy
VERIFY no attempt passed; using best (mode=energy_focused, confidence=0.29)
```

### What I checked by hand

I confirmed the study request's first strategy is below the 0.50 threshold and its second strategy passes. For the clean request, I checked that the trace says three explicit songs were removed and that none of the returned songs is explicit. For “polka,” I confirmed no genre or mood was recognized, all three strategies ran, and the final low-confidence warning agrees with the 0.29 result. I also ran the four controlled reliability experiments and recorded the measured outcomes in Sections 9–12 of `model_card.md`.
