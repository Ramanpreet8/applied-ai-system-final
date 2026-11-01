import pytest

from src.guardrails import GuardrailError, check_output, validate_request


def test_validate_request_normalizes_whitespace():
    assert validate_request("  hi   there  ") == "hi there"


@pytest.mark.parametrize(
    ("text", "k", "message"),
    [
        (None, 5, "Request must be text."),
        ("  \n ", 5, "Request is empty."),
        ("123 !?", 5, "Request has no words"),
        ("a" * 301, 5, "Request is too long"),
        ("music", 0, "k (number of songs)"),
        ("music", 11, "k (number of songs)"),
        ("music", 1.5, "k (number of songs)"),
    ],
)
def test_validate_request_rejects_invalid_input(text, k, message):
    with pytest.raises(GuardrailError) as error:
        validate_request(text, k)
    assert message in str(error.value)


def test_check_output_reports_missing_and_insufficient_recommendations():
    assert check_output([], 5) == ["no songs were returned"]
    assert check_output([({"artist": "A"}, 1, [])], 2) == [
        "only 1 of 2 songs available"
    ]


def test_check_output_reports_artist_dominance():
    recommendations = [
        ({"artist": "A"}, 1, []),
        ({"artist": "A"}, 1, []),
        ({"artist": "A"}, 1, []),
        ({"artist": "B"}, 1, []),
    ]

    assert check_output(recommendations, 4) == ["one artist dominates the list"]


def test_check_output_returns_no_problems_for_valid_results():
    recommendations = [
        ({"artist": "A"}, 1, []),
        ({"artist": "A"}, 1, []),
        ({"artist": "B"}, 1, []),
    ]

    assert check_output(recommendations, 3) == []
