import pytest

from src.agent import plan, run_agent
from src.guardrails import GuardrailError, validate_request
from src.recommender import load_songs


@pytest.fixture
def songs():
    return load_songs("data/songs.csv")


def test_plan_extracts_request_preferences(songs):
    profile = plan("clean happy pop workout 2010s instrumental", songs)

    assert profile["genre"] == "pop"
    assert profile["mood"] == "happy"
    assert profile["energy"] == 0.9
    assert profile["preferred_decade"] == 2010
    assert profile["exclude_explicit"] is True
    assert profile["target_instrumentalness"] == 0.9


def test_run_agent_filters_explicit_songs_and_returns_trace(songs):
    result = run_agent("clean happy pop workout", songs, k=3)

    assert len(result["recommendations"]) == 3
    assert all(not song["explicit"] for song, _, _ in result["recommendations"])
    assert any(line.startswith("PLAN") for line in result["trace"])
    assert any(line.startswith("ACT") for line in result["trace"])
    assert any("removed" in line for line in result["trace"])


def test_run_agent_revises_when_request_is_not_understood(songs):
    result = run_agent("polka", songs, k=3)

    assert sum(line.startswith("ACT") for line in result["trace"]) == 3
    assert any("No genre or mood recognised" in warning for warning in result["warnings"])
    assert any(warning.startswith("Low confidence") for warning in result["warnings"])


def test_run_agent_handles_empty_catalog():
    result = run_agent("chill music", [], k=3)

    assert result["recommendations"] == []
    assert "no songs were returned" in result["warnings"]
    assert sum(line.startswith("ACT") for line in result["trace"]) == 3


def test_run_agent_validates_request(songs):
    with pytest.raises(GuardrailError):
        run_agent("   ", songs)


def test_plan_understands_genre_and_energy(songs):
    profile = plan("high energy pop workout", songs)

    assert profile["genre"] == "pop"
    assert profile["energy"] == 0.9


def test_confidence_is_between_zero_and_one(songs):
    assert 0.0 <= run_agent("happy pop", songs)["confidence"] <= 1.0


def test_gibberish_gets_low_confidence_and_warning(songs):
    result = run_agent("polka", songs)

    assert result["confidence"] < 0.5
    assert result["warnings"]


def test_agent_records_input_and_plan_trace(songs):
    trace = run_agent("happy pop", songs)["trace"]

    assert trace[0].startswith("INPUT")
    assert any(line.startswith("PLAN") for line in trace)


@pytest.mark.parametrize("bad", ["", " ", "!!!", "x" * 500, None, 42])
def test_guardrail_blocks_bad_input(bad):
    with pytest.raises(GuardrailError):
        validate_request(bad)


def test_guardrail_blocks_bad_k():
    with pytest.raises(GuardrailError):
        validate_request("pop", k=0)
