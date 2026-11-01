"""VibeFinder Agent: plan -> act -> verify -> revise, with a saved reasoning trace."""

import logging
import re
from typing import Dict, List

from .guardrails import check_output, validate_request
from .recommender import SCORING_MODES, recommend_songs

logger = logging.getLogger("vibefinder.agent")
CONFIDENCE_THRESHOLD = 0.50

MOOD_WORDS = {
    "happy": ["happy", "cheerful", "joyful", "upbeat", "good mood"],
    "chill": ["chill", "relax", "calm", "unwind", "mellow"],
    "intense": ["intense", "powerful", "hype"],
    "focused": ["study", "focus", "coding", "homework", "concentrate"],
    "nostalgic": ["nostalgic", "memories", "throwback"],
    "serene": ["serene", "peaceful", "sleep"],
    "sad": ["sad", "heartbroken", "cry"],
    "aggressive": ["angry", "aggressive", "rage"],
}
HIGH_ENERGY_WORDS = [
    "high energy", "energetic", "workout", "gym", "run", "running", "party",
    "dance", "hype", "pump",
]
LOW_ENERGY_WORDS = [
    "study", "sleep", "rain", "relax", "calm", "night", "unwind", "quiet",
]
CLEAN_WORDS = ["clean", "kid", "kids", "family", "no explicit", "work-safe"]
INSTRUMENTAL_WORDS = ["instrumental", "no vocals", "no lyrics", "without lyrics"]


def _has(text: str, words: List[str]) -> bool:
    return any(re.search(rf"\b{re.escape(word)}", text) for word in words)


def plan(request: str, songs: List[Dict]) -> Dict:
    """STEP 1 (Plan): turn plain English into a user-profile dictionary."""
    text = request.lower().replace("hip hop", "hip-hop")
    genres = {song["genre"] for song in songs}
    found_genre = next(
        (
            genre
            for genre in sorted(genres)
            if re.search(rf"\b{re.escape(genre)}\b", text)
        ),
        None,
    )
    found_mood = next(
        (mood for mood, words in MOOD_WORDS.items() if _has(text, words)),
        None,
    )
    energy = 0.5
    if _has(text, HIGH_ENERGY_WORDS):
        energy = 0.9
    elif _has(text, LOW_ENERGY_WORDS):
        energy = 0.3

    decade = 2020
    match = re.search(r"\b(19|20)?(\d0)s\b", text)
    if match:
        decade = int(
            f"{match.group(1) or ('19' if int(match.group(2)) > 30 else '20')}"
            f"{match.group(2)}"
        )

    return {
        "genre": found_genre,
        "mood": found_mood,
        "energy": energy,
        "target_popularity": 60,
        "preferred_decade": decade,
        "preferred_mood_tags": [found_mood] if found_mood else [],
        "target_instrumentalness": 0.9 if _has(text, INSTRUMENTAL_WORDS) else 0.3,
        "exclude_explicit": _has(text, CLEAN_WORDS),
    }


def max_possible_score(profile: Dict, mode: str) -> float:
    """Best score a perfect song could get, so we can turn a score into 0-1 confidence."""
    weights = SCORING_MODES[mode]
    total = (
        weights["genre"] + weights["mood"] + weights["energy"]
        + 0.5 + 0.5 + 0.3
    )
    total += min(0.5 * len(profile["preferred_mood_tags"]), 1.0)
    return total


def understanding(profile: Dict, songs: List[Dict]) -> float:
    """How much of the request did the planner understand? (0.4 to 1.0)"""
    known_moods = {song["mood"] for song in songs}
    score = 0.4
    score += 0.3 if profile["genre"] else 0
    score += 0.3 if profile["mood"] in known_moods else 0
    return score


def confidence(
    profile: Dict, mode: str, recommendations: List, songs: List[Dict]
) -> float:
    """STEP 3 helper: score ratio times how much the planner understood."""
    if not recommendations:
        return 0.0
    ratio = min(recommendations[0][1] / max_possible_score(profile, mode), 1.0)
    return round(ratio * understanding(profile, songs), 2)


def run_agent(request: str, songs: List[Dict], k: int = 5) -> Dict:
    """Run the full agent loop and return recommendations, confidence, warnings and a trace."""
    trace: List[str] = []
    request = validate_request(request, k)
    trace.append(f"INPUT guardrail passed: {request!r}")

    profile = plan(request, songs)
    trace.append(f"PLAN profile = { {key: val for key, val in profile.items()} }")
    warnings: List[str] = []
    known_moods = {song["mood"] for song in songs}
    if profile["mood"] and profile["mood"] not in known_moods:
        warnings.append(
            f"No song in the catalog has the mood '{profile['mood']}'; "
            "results rely on energy and other features."
        )
    if profile["genre"] is None and profile["mood"] is None:
        warnings.append(
            "No genre or mood recognised; ranking by energy and other features only."
        )

    pool = [
        song
        for song in songs
        if not (profile["exclude_explicit"] and song["explicit"])
    ]
    if len(pool) < len(songs):
        trace.append(
            f"GUARD clean-music request: removed {len(songs) - len(pool)} explicit songs"
        )

    best = None
    for attempt, mode in enumerate(
        ["genre_first", "mood_first", "energy_focused"], start=1
    ):
        recs = recommend_songs(profile, pool, k=k, mode=mode)
        conf = confidence(profile, mode, recs, songs)
        problems = check_output(recs, k)
        top_title = recs[0][0]["title"] if recs else None
        trace.append(
            f"ACT attempt {attempt} mode={mode}: top={top_title!r} "
            f"confidence={conf} problems={problems or 'none'}"
        )

        if best is None or conf > best["confidence"]:
            best = {
                "mode": mode,
                "recommendations": recs,
                "confidence": conf,
                "problems": problems,
            }
        if conf >= CONFIDENCE_THRESHOLD and not problems:
            trace.append(
                f"VERIFY attempt {attempt} accepted "
                f"(confidence >= {CONFIDENCE_THRESHOLD})"
            )
            break
        trace.append(
            f"REVISE confidence {conf} too low or problems found -> "
            "trying next strategy"
        )
    else:
        warnings.append(
            f"Low confidence ({best['confidence']}); showing the best of 3 strategies."
        )
        trace.append(
            f"VERIFY no attempt passed; using best "
            f"(mode={best['mode']}, confidence={best['confidence']})"
        )

    warnings.extend(best["problems"])
    for line in trace:
        logger.info(line)
    return {"request": request, "profile": profile, "warnings": warnings, "trace": trace, **best}
