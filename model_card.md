# Model Card: Vibe Finder

## 1. Goal and Task

Vibe Finder recommends songs from a small catalog. It ranks songs using a user's favorite genre and mood, target energy, popularity, preferred release decade, preferred mood tags, and target instrumentalness. This is a classroom simulation, not a production music service.

## 2. Data Used

The catalog contains 18 songs, including pop, lofi, rock, jazz, ambient, synthwave, country, metal, classical, hip-hop, reggae, blues, folk, and funk. Each row also includes popularity, release decade, 2–3 mood tags, explicit status, and instrumentalness, alongside the original song, artist, and musical attributes. The score uses genre, mood, energy, popularity, decade, mood tags, and instrumentalness; explicit status is loaded but not scored. These sample records do not represent the full range of music or listeners.

## 3. Algorithm Summary

Choose one of three modes: genre-first weights genre/mood/energy at 3/1/1, mood-first at 1/3/1, and energy-focused at 0.5/0.5/3. An exact genre or mood match earns that mode's weight; energy similarity is `1 - abs(song energy - target energy)` times its weight. Popularity closeness adds up to 0.5, a matching release decade adds 0.5, each shared mood tag adds 0.5 up to 1.0, and instrumentalness closeness adds up to 0.3. The program adds the points, sorts songs from highest score to lowest, and returns the top five with reasons.

## 4. Observed Behavior and Biases

Changing the weights, adding features, and applying diversity penalties changed the rankings, but there are no listener ratings to show that the new rankings are more accurate. Energy has twice the maximum influence of a genre or mood match, and mood-tag overlap can add another point. Repeat-artist and repeat-genre penalties can push out a song that otherwise scored well, so they trade relevance for variety. Exact labels do not recognize related genres or moods, and the catalog has only a few examples for most labels. If a requested mood or genre is missing, recommendations rely more heavily on numerical similarities. Explicit status is not scored; tempo, valence, danceability, acousticness, listening history, and context are also ignored.

## 5. Evaluation Process

I ran the CLI for three ordinary profiles and two conflicting profiles. I checked the top-five rankings, score explanations, feature ranges, and score arithmetic. In the expanded run, High-Energy Pop's Sunrise City score is 6.00, equal to the displayed reason points: 1.00 genre, 1.00 mood, 1.74 energy, 0.48 popularity, 0.50 decade, 1.00 mood tags, and 0.28 instrumentalness. Low-Energy Intense Rock now puts Quiet Constellations first, reflecting its low energy, popularity, decade, tags, and instrumentalness matches. There are no listener ratings to prove these results are accurate.

The terminal transcript and comparisons below preserve the earlier Phase 4 baseline run, before advanced features and scoring modes were added. Current mode comparisons are in the README.

```text
Loaded songs: 18

High-Energy Pop
---------------
1. Sunrise City - Score: 3.74
   Reasons: genre match (+1.0), mood match (+1.0), energy similarity (+1.74)
2. Gym Hero - Score: 2.96
   Reasons: genre match (+1.0), energy similarity (+1.96)
3. Rooftop Lights - Score: 2.62
   Reasons: mood match (+1.0), energy similarity (+1.62)
4. Iron Horizon - Score: 1.98
   Reasons: energy similarity (+1.98)
5. Storm Runner - Score: 1.92
   Reasons: energy similarity (+1.92)

Chill Lofi
----------
1. Midnight Coding - Score: 3.96
   Reasons: genre match (+1.0), mood match (+1.0), energy similarity (+1.96)
2. Library Rain - Score: 3.90
   Reasons: genre match (+1.0), mood match (+1.0), energy similarity (+1.90)
3. Focus Flow - Score: 3.00
   Reasons: genre match (+1.0), energy similarity (+2.00)
4. Spacewalk Thoughts - Score: 2.76
   Reasons: mood match (+1.0), energy similarity (+1.76)
5. Coffee Shop Stories - Score: 1.94
   Reasons: energy similarity (+1.94)

Deep Intense Rock
-----------------
1. Storm Runner - Score: 3.98
   Reasons: genre match (+1.0), mood match (+1.0), energy similarity (+1.98)
2. Gym Hero - Score: 2.94
   Reasons: mood match (+1.0), energy similarity (+1.94)
3. Iron Horizon - Score: 1.88
   Reasons: energy similarity (+1.88)
4. Sunrise City - Score: 1.84
   Reasons: energy similarity (+1.84)
5. Neon Parade - Score: 1.82
   Reasons: energy similarity (+1.82)

Sad High-Energy Pop
-------------------
1. Gym Hero - Score: 2.94
   Reasons: genre match (+1.0), energy similarity (+1.94)
2. Sunrise City - Score: 2.84
   Reasons: genre match (+1.0), energy similarity (+1.84)
3. Storm Runner - Score: 1.98
   Reasons: energy similarity (+1.98)
4. Iron Horizon - Score: 1.88
   Reasons: energy similarity (+1.88)
5. Neon Parade - Score: 1.82
   Reasons: energy similarity (+1.82)

Low-Energy Intense Rock
-----------------------
1. Storm Runner - Score: 2.38
   Reasons: genre match (+1.0), mood match (+1.0), energy similarity (+0.38)
2. Quiet Constellations - Score: 1.76
   Reasons: energy similarity (+1.76)
3. Spacewalk Thoughts - Score: 1.64
   Reasons: energy similarity (+1.64)
4. Paper Kites - Score: 1.54
   Reasons: energy similarity (+1.54)
5. Library Rain - Score: 1.50
   Reasons: energy similarity (+1.50)
```

### Profile comparisons

- **High-Energy Pop vs. Chill Lofi:** Pop and happy songs lead in the first profile; lofi and chill songs lead in the second because genre, mood, and target energy differ.
- **High-Energy Pop vs. Deep Intense Rock:** Storm Runner leads for rock and intense matches, despite both profiles preferring high energy.
- **High-Energy Pop vs. Sad High-Energy Pop:** Removing the happy mood match changes the leader to Gym Hero, which matches pop and energy.
- **High-Energy Pop vs. Low-Energy Intense Rock:** Lower target energy brings quieter tracks into the results, though Storm Runner remains first because of its genre and mood matches.
- **Chill Lofi vs. Deep Intense Rock:** Lofi/chill matches are replaced by Storm Runner's rock/intense matches.
- **Chill Lofi vs. Sad High-Energy Pop:** Changing genre, mood, and energy shifts the list from mellow lofi to energetic pop.
- **Chill Lofi vs. Low-Energy Intense Rock:** Both target low energy, but Storm Runner leads for the rock/intense profile because of its category bonuses.
- **Deep Intense Rock vs. Sad High-Energy Pop:** The matching genres and moods change, making Gym Hero lead for pop while Storm Runner leads for rock.
- **Deep Intense Rock vs. Low-Energy Intense Rock:** The category preferences stay the same, but the low target reduces Storm Runner's energy points; its genre and mood points keep it first.
- **Sad High-Energy Pop vs. Low-Energy Intense Rock:** Different category matches and target energy produce different results; Storm Runner's two category matches outweigh its energy mismatch.

## 6. Intended and Non-Intended Use

This tool is for learning how simple scoring and ranking work. It can demonstrate how changing preferences or weights changes a ranked list. It should not be used to make claims about a person's full taste, replace a real recommendation service, or make decisions about people.

## 7. Ideas for Improvement

Add more songs and more balanced examples for each genre and mood. Use tempo, valence, danceability, and acousticness in the score. Support multiple preferences and related mood or genre matches. Test recommendations against listener feedback and add a way to increase variety.

## 8. Personal Reflection

My biggest learning moment was seeing how every scoring weight and feature changes the order of the recommendations, without proving they are more accurate. I double-checked the AI's work by adding Sunrise City's listed points by hand and caught a loader bug when instrumentalness was treated as text instead of a number. I was surprised that the expanded features moved Quiet Constellations above Storm Runner for the low-energy rock profile. Next, I would add more songs and test recommendations with real listener feedback.

## 9. Limitations and Biases of the Agent

The planner is a fixed English keyword matcher, not a general language model. It only recognizes the words and phrases listed in `MOOD_WORDS` and the energy/content keyword lists; genre matching requires the catalog label to appear exactly in the request. The catalog has only 18 hand-labeled songs and no listener feedback, so most genres and moods have very few examples. The word “sad” is recognized, but no song in the catalog has the `sad` mood, so the agent warns and falls back on other features. Confidence is a heuristic based on score ratio and recognized genre/mood, not a calibrated probability that a recommendation is relevant.

## 10. Misuse and Prevention

A user could provide misleading or irrelevant words and cause the keyword planner to build a profile that does not reflect their intent. Repeated requests could also consume resources; the 300-character input limit and `k` limit bound individual requests, but this prototype has no rate limiting. The clean-music option filters songs whose catalog `explicit` field is set, and the trace log records the request and agent decisions; log files should therefore be handled as user data. These guardrails reduce some predictable errors but do not make this a safety service. The system should not profile people, infer sensitive traits, or be presented as a real music service. A human should review recommendations before relying on them.

## 11. What Surprised Me in Reliability Testing

The “polka” experiments showed how a plausible confidence value can be produced for a request the planner did not understand. With the current implementation, “polka” receives confidence 0.29, tries all three modes, and is flagged as low confidence. In an isolated runtime experiment, counting genre and mood in the maximum score only when they were mentioned raised the result to 0.36 while retaining the understanding multiplier. Removing that multiplier too, while using the conditional denominator, raised confidence to 0.89 and caused the first strategy to be accepted despite the unrecognized request. This combined experiment confirms why the current implementation counts every category and includes an understanding factor.

With the full maximum-score denominator but without the understanding multiplier, “polka” reached 0.73 and was accepted using `energy_focused`. The genre/mood weight changes therefore let the revision loop increase its numeric confidence without increasing what the planner knew. Removing input validation in an isolated runtime run also demonstrated the guardrail's value: an empty request returned five recommendations instead of being rejected.

The threshold experiment showed that passing functional checks does not prove a good interaction. At a 0.30 threshold, the vague study request stopped after its first strategy at 0.31, so the harness's revise expectation failed and the overall score was 9/10. At 0.80, all 10 checks passed because the harness checks recommendation behavior, not whether the agent accepted without a low-confidence warning; the agent tried all strategies and returned the best available result.

## 12. AI Collaboration

I used AI assistance to implement the agent loop, CLI, guardrails, evaluation harness, tests, and documentation. I accepted the suggestion to handle empty recommendation lists safely and add edge-case tests, because directly indexing the first result would fail for an empty catalog. I also checked the experiment claims rather than copying the guide's illustrative confidence unchanged: the denominator change alone produced 0.36 in this code, while 0.89 required removing the understanding multiplier as well. The final docs distinguish those two changes and keep the working agent's measured 0.29 result.

## 13. Future Improvements

Replace the fixed keyword planner with a carefully evaluated language-model planner while retaining input validation and human review. Add more songs with balanced genre and mood coverage, incorporate tempo and valence into scoring, and compare recommendations with real listener feedback. Improve confidence calibration against those judgments, add request rate limiting and privacy-conscious log retention, and provide a human-in-the-loop review or feedback button.
