"""Guardrails: check the request BEFORE the agent works and the answer AFTER."""

MAX_REQUEST_CHARS = 300


class GuardrailError(ValueError):
    """Raised when a request is unsafe or unusable. The message is user-friendly."""


def validate_request(text, k=5):
    """Input guardrail: reject empty, non-text, too-long, or nonsense requests."""
    if not isinstance(text, str):
        raise GuardrailError("Request must be text.")

    cleaned = " ".join(text.split())
    if not cleaned:
        raise GuardrailError("Request is empty. Try: 'chill lofi music to study'.")
    if len(cleaned) > MAX_REQUEST_CHARS:
        raise GuardrailError(
            f"Request is too long (max {MAX_REQUEST_CHARS} characters)."
        )
    if not any(ch.isalpha() for ch in cleaned):
        raise GuardrailError("Request has no words I can understand.")
    if not isinstance(k, int) or not 1 <= k <= 10:
        raise GuardrailError("k (number of songs) must be a whole number from 1 to 10.")

    return cleaned


def check_output(recommendations, k):
    """Output guardrail: returns a list of problems (empty list = all good)."""
    problems = []
    if not recommendations:
        problems.append("no songs were returned")
    elif len(recommendations) < k:
        problems.append(f"only {len(recommendations)} of {k} songs available")

    artists = [song["artist"] for song, _, _ in recommendations]
    if any(artists.count(artist) > 2 for artist in set(artists)):
        problems.append("one artist dominates the list")

    return problems
