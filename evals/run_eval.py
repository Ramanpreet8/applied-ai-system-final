"""Test harness: run the agent on predefined requests and print a pass/fail summary.
Run with: python -m evals.run_eval
"""

from tabulate import tabulate

from src.agent import run_agent
from src.guardrails import GuardrailError
from src.recommender import load_songs

CASES = [
    (
        "Pop workout -> a pop song first",
        "high energy pop workout",
        lambda result: result["recommendations"][0][0]["genre"] == "pop",
    ),
    (
        "Study request -> a lofi song first",
        "chill lofi music to study",
        lambda result: result["recommendations"][0][0]["genre"] == "lofi",
    ),
    (
        "Rock request -> a rock song first",
        "intense rock from the 2010s",
        lambda result: result["recommendations"][0][0]["genre"] == "rock",
    ),
    (
        "Clean request -> zero explicit songs",
        "clean pop party music",
        lambda result: all(
            song["explicit"] == 0
            for song, _, _ in result["recommendations"]
        ),
    ),
    (
        "Unknown mood 'sad' -> warns the user",
        "sad high energy pop",
        lambda result: any("sad" in warning for warning in result["warnings"]),
    ),
    (
        "Gibberish -> low confidence + warning",
        "polka",
        lambda result: result["confidence"] < 0.5
        and len(result["warnings"]) >= 1,
    ),
    (
        "Vague request -> agent revises strategy",
        "I need chill music to study at night",
        lambda result: any(line.startswith("REVISE") for line in result["trace"]),
    ),
    ("Empty input -> blocked by guardrail", "", "BLOCKED"),
    ("Symbols only -> blocked by guardrail", "!!! ???", "BLOCKED"),
    ("Very long input -> blocked by guardrail", "pop " * 200, "BLOCKED"),
]


def main() -> None:
    songs = load_songs("data/songs.csv")
    rows, passed, confidences = [], 0, []
    for name, request, check in CASES:
        try:
            result = run_agent(request, songs)
            ok = check(result) if callable(check) else False
            confidences.append(result["confidence"])
            detail = f"conf={result['confidence']:.2f}, mode={result['mode']}"
        except GuardrailError:
            ok = check == "BLOCKED"
            detail = "blocked"
        passed += ok
        rows.append([name, detail, "PASS" if ok else "FAIL"])

    print(tabulate(rows, headers=["Test", "Detail", "Result"], tablefmt="github"))
    print(
        f"\n{passed}/{len(CASES)} checks passed; "
        "average confidence on answered requests = "
        f"{sum(confidences) / len(confidences):.2f}"
    )


if __name__ == "__main__":
    main()
