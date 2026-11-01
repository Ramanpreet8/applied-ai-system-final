"""Command-line front end for the agent: python -m src.agent_cli "chill lofi to study"."""

import logging
import sys
from pathlib import Path

from tabulate import tabulate

from .agent import run_agent
from .guardrails import GuardrailError
from .recommender import load_songs

Path("logs").mkdir(exist_ok=True)
logging.basicConfig(
    filename="logs/agent_trace.log",
    level=logging.INFO,
    format="%(asctime)s %(message)s",
)


def show(result: dict) -> None:
    """Pretty-print one agent result."""
    print(f"\nRequest: {result['request']}")
    print(
        f"Strategy used: {result['mode']} | "
        f"Confidence: {result['confidence']:.2f}"
    )
    rows = [
        [rank, song["title"], song["artist"], f"{score:.2f}"]
        for rank, (song, score, _) in enumerate(result["recommendations"], 1)
    ]
    print(
        tabulate(
            rows,
            headers=["Rank", "Title", "Artist", "Score"],
            tablefmt="github",
            disable_numparse=True,
        )
    )
    for warning in result["warnings"]:
        print(f"WARNING: {warning}")
    print("\nAgent trace:")
    for line in result["trace"]:
        print(f" {line}")


def main() -> None:
    songs = load_songs("data/songs.csv")
    request = " ".join(sys.argv[1:])
    try:
        show(run_agent(request, songs))
    except GuardrailError as error:
        print(f"Guardrail blocked this request: {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
