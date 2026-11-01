# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

## How The System Works

Real music platforms often combine collaborative filtering, which learns from listening patterns, likes, skips, and playlists from similar users, with content-based filtering, which compares a listener's preferences with song attributes. This project prioritizes a simple, explainable content-based approach: each `Song` also records popularity, release decade, detailed mood tags, explicit status, and instrumentalness, while each `UserProfile` can set targets for these features. The recommender scores genre, mood, energy, and these added attributes, then ranks songs by total score.

### Algorithm Recipe

Choose `genre_first`, `mood_first`, or `energy_focused` with `python -m src.main --mode <mode>`; the default `all` compares each mode. The modes weight genre, mood, and energy similarity as `(3, 1, 1)`, `(1, 3, 1)`, and `(0.5, 0.5, 3)`. Add up to 0.5 popularity points using `0.5 * (1 - abs(song.popularity - target_popularity) / 100)`, 0.5 for an exact release-decade match, 0.5 per overlapping mood tag up to 1.0, and up to 0.3 for instrumentalness closeness using `0.3 * (1 - abs(song.instrumentalness - target_instrumentalness))`. Recommendations are selected greedily: each repeat artist loses 1 point and each repeat genre loses 0.5, based on songs already chosen. Set `diversity=False` in `recommend_songs` to compare the unadjusted ranking. These weights and penalties can favor particular features, while the small catalog and manually assigned labels limit variety and accuracy.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

### Running the VibeFinder Agent

The agent CLI accepts a natural-language request, prints recommendations and its
plan/act/verify/revise trace, and writes the trace to `logs/agent_trace.log`.

```bash
python -m src.agent_cli "I need chill music to study at night"
```

```text
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

```bash
python -m src.agent_cli "clean pop party music"
```

```text
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

```bash
python -m src.agent_cli "polka"
```

```text
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

An empty request is rejected (the command exits with status 1):

```bash
python -m src.agent_cli ""
```

```text
Guardrail blocked this request: Request is empty. Try: 'chill lofi music to study'.
```

## Sample Recommendation Output

```text
Loaded songs: 18

High-Energy Pop - Mode: genre_first
+--------+----------------+-------------------+---------+------------------------------------------------------+
|   Rank | Title          | Artist            |   Score | Reasons                                              |
+========+================+===================+=========+======================================================+
|      1 | Sunrise City   | Neon Echo         |    7.13 | genre match (+3.0); mood match (+1.0); energy        |
|        |                |                   |         | similarity (+0.87); popularity close (+0.48);        |
|        |                |                   |         | release decade match (+0.50); mood tags overlap      |
|        |                |                   |         | (+1.00); instrumentalness close (+0.28)              |
+--------+----------------+-------------------+---------+------------------------------------------------------+
|      2 | Gym Hero       | Max Pulse         |    4.73 | genre match (+3.0); energy similarity (+0.98);       |
|        |                |                   |         | popularity close (+0.48); release decade match       |
|        |                |                   |         | (+0.50); mood tags overlap (+0.00); instrumentalness |
|        |                |                   |         | close (+0.27); diversity penalty: genre already      |
|        |                |                   |         | recommended (-0.5)                                   |
+--------+----------------+-------------------+---------+------------------------------------------------------+
|      3 | Rooftop Lights | Indigo Parade     |    3.56 | mood match (+1.0); energy similarity (+0.81);        |
|        |                |                   |         | popularity close (+0.46); release decade match       |
|        |                |                   |         | (+0.50); mood tags overlap (+0.50); instrumentalness |
|        |                |                   |         | close (+0.28)                                        |
+--------+----------------+-------------------+---------+------------------------------------------------------+
|      4 | Neon Parade    | The Brass Circuit |    2.57 | energy similarity (+0.86); popularity close (+0.43); |
|        |                |                   |         | release decade match (+0.50); mood tags overlap      |
|        |                |                   |         | (+0.50); instrumentalness close (+0.28)              |
+--------+----------------+-------------------+---------+------------------------------------------------------+
|      5 | Iron Horizon   | Black Anvil       |    2.18 | energy similarity (+0.99); popularity close (+0.42); |
|        |                |                   |         | release decade match (+0.50); mood tags overlap      |
|        |                |                   |         | (+0.00); instrumentalness close (+0.27)              |
+--------+----------------+-------------------+---------+------------------------------------------------------+

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this
