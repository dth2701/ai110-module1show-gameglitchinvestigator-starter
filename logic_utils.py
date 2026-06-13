import random

# Difficulties we track a best score for. A score for anything outside this set
# is ignored so a stray difficulty can never leak into the high-score table.
DIFFICULTIES = ("Easy", "Normal", "Hard")


def get_range_for_difficulty(difficulty: str):
    """Return the inclusive guessing range for a difficulty level.

    Args:
        difficulty: The difficulty name, expected to be one of "Easy",
            "Normal", or "Hard". Any unrecognized value falls back to the
            "Hard" range so the game always has a valid bound.

    Returns:
        tuple[int, int]: A ``(low, high)`` pair giving the inclusive lower and
        upper bounds the secret number may take:

        * "Easy"   -> ``(1, 20)``
        * "Normal" -> ``(1, 50)``
        * "Hard"   -> ``(1, 100)``
        * unknown  -> ``(1, 100)``
    """
    if difficulty == "Easy":
        return 1, 20
    if difficulty == "Normal":
        return 1, 50
    if difficulty == "Hard":
        return 1, 100
    return 1, 100


def regenerate_secret(difficulty: str):
    """Generate a new random secret number for the given difficulty.

    Uses :func:`get_range_for_difficulty` to determine the valid bounds, then
    draws a uniformly random integer within that inclusive range. Call this
    whenever a new round starts or the difficulty changes mid-game so the
    secret always matches the active range.

    Args:
        difficulty: The difficulty name (see :func:`get_range_for_difficulty`
            for accepted values and fallback behavior).

    Returns:
        int: A random integer in the inclusive range for ``difficulty``.
    """
    low, high = get_range_for_difficulty(difficulty)
    return random.randint(low, high)


def parse_guess(raw: str):
    """Parse raw user input into an integer guess.

    Performs presence and type validation without enforcing range limits;
    callers are responsible for checking that an accepted guess falls within
    the active difficulty's bounds.

    Args:
        raw: The unparsed input as received from the UI. May be ``None`` or an
            empty string when the user submits nothing.

    Returns:
        tuple[bool, int | None, str | None]: A ``(ok, guess, error)`` triple:

        * ``ok`` is ``True`` only when ``raw`` parsed cleanly to an integer.
        * ``guess`` is the parsed integer when ``ok`` is ``True``, else
          ``None``.
        * ``error`` is a user-facing message when ``ok`` is ``False``, else
          ``None``.

        Failure messages are ``"Enter a guess."`` for missing/empty input and
        ``"That is not a number."`` for non-numeric input.
    """
    if raw is None:
        return False, None, "Enter a guess."

    if raw == "":
        return False, None, "Enter a guess."

    try:
        value = int(raw)
    except Exception:
        return False, None, "That is not a number."

    return True, value, None


def check_guess(guess, secret):
    """Compare a guess against the secret and classify the result.

    Args:
        guess: The player's guessed value.
        secret: The hidden target value for the current round.

    Returns:
        tuple[str, str]: An ``(outcome, message)`` pair where ``outcome`` is
        one of:

        * ``"Win"`` -> guess equals the secret; message ``"🎉 Correct!"``.
        * ``"Too High"`` -> guess exceeds the secret; message
          ``"📉 Go LOWER!"``.
        * ``"Too Low"`` -> guess is below the secret; message
          ``"📈 Go HIGHER!"``.

        The message is a ready-to-display hint corresponding to the outcome.
    """
    # FIX: Refactored logic into logic_utils.py using agent mode
    if guess == secret:
        return "Win", "🎉 Correct!"

    if guess > secret:
        return "Too High", "📉 Go LOWER!"
    return "Too Low", "📈 Go HIGHER!"


def update_score(current_score: int, outcome: str, attempt_number: int):
    """Compute the new running score after a single guess.

    Scoring rules by outcome:

    * ``"Win"``: award ``100 - 10 * (attempt_number + 1)`` points, floored at a
      minimum of 10, so earlier wins are worth more but a win is never worth
      fewer than 10 points.
    * ``"Too High"``: add 5 points on even ``attempt_number`` values and
      subtract 5 on odd ones.
    * ``"Too Low"``: subtract 5 points.
    * Any other outcome leaves the score unchanged.

    Args:
        current_score: The player's score prior to this guess.
        outcome: The result classification, typically from
            :func:`check_guess` (``"Win"``, ``"Too High"``, or ``"Too Low"``).
        attempt_number: The zero-based index of the current attempt, used to
            scale the win bonus and decide the "Too High" parity adjustment.

    Returns:
        int: The updated score after applying the rule for ``outcome``.
    """
    if outcome == "Win":
        points = 100 - 10 * (attempt_number + 1)
        if points < 10:
            points = 10
        return current_score + points

    if outcome == "Too High":
        if attempt_number % 2 == 0:
            return current_score + 5
        return current_score - 5

    if outcome == "Too Low":
        return current_score - 5

    return current_score


def update_high_score(scores: dict, difficulty: str, score: int):
    """Record a round's score against the stored best for its difficulty.

    Only difficulties listed in :data:`DIFFICULTIES` are tracked; a score for
    any other difficulty is ignored so a stray value can never leak into the
    high-score table.

    Args:
        scores: Mapping of difficulty name to its best recorded score. Updated
            in place when a new record is set.
        difficulty: The difficulty the score was achieved on. Must be a member
            of :data:`DIFFICULTIES` to be considered.
        score: The score earned in the finished round.

    Returns:
        tuple[dict, bool]: An ``(updated_scores, is_record)`` pair. The same
        ``scores`` dict is returned (mutated in place) for convenience.
        ``is_record`` is ``True`` only when ``score`` strictly beats the prior
        best for ``difficulty``, so ties do not falsely celebrate a new record.
        Untracked difficulties return ``(scores, False)`` unchanged.
    """
    if difficulty not in DIFFICULTIES:
        return scores, False

    previous_best = scores.get(difficulty, 0)
    if score > previous_best:
        scores[difficulty] = score
        return scores, True

    return scores, False
