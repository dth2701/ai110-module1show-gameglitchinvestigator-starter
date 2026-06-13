import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from logic_utils import (
    check_guess,
    parse_guess,
    get_range_for_difficulty,
    regenerate_secret,
)

def test_winning_guess():
    # If the secret is 50 and guess is 50, it should be a win
    outcome, message = check_guess(50, 50)
    assert outcome == "Win"

def test_guess_too_high():
    # If secret is 50 and guess is 60, hint should be "Too High"
    outcome, message = check_guess(60, 50)
    assert outcome == "Too High"

def test_guess_too_low():
    # If secret is 50 and guess is 40, hint should be "Too Low"
    outcome, message = check_guess(40, 50)
    assert outcome == "Too Low"

# Invalid input used to slip through and burn an attempt. parse_guess
# must reject these so app.py never increments the attempt counter for them.

def test_empty_input_is_rejected():
    # An empty string should NOT be treated as a valid guess
    ok, value, err = parse_guess("")
    assert ok is False
    assert value is None
    assert err is not None

def test_whitespace_only_input_is_rejected():
    # "   " is not a number; must be rejected, not counted as a guess
    ok, value, err = parse_guess("   ")
    assert ok is False
    assert value is None

def test_non_numeric_input_is_rejected():
    # Letters are not a valid guess
    ok, value, err = parse_guess("abc")
    assert ok is False
    assert value is None

def test_valid_number_is_accepted():
    # A real number should parse cleanly so it can be range-checked downstream
    ok, value, err = parse_guess("42")
    assert ok is True
    assert value == 42
    assert err is None


def test_decimal_guess_is_rejected():
    ok, value, err = parse_guess("4.5")
    assert ok is False
    assert value is None
    assert err is not None


def test_negative_guess_is_rejected_by_range():
    ok, value, err = parse_guess("-5")
    assert ok is True   
    assert value == -5
    low, high = get_range_for_difficulty("Normal")  # (1, 50)
    assert not (low <= value <= high) 

# Changing difficulty mid-game changes the range, so the secret must be
# regenerated within the new range. Otherwise a Hard secret (e.g. 80) can
# survive a switch to Easy (1-20) and make the game unwinnable.

def test_ranges_match_each_difficulty():
    assert get_range_for_difficulty("Easy") == (1, 20)
    assert get_range_for_difficulty("Normal") == (1, 50)
    assert get_range_for_difficulty("Hard") == (1, 100)

def test_unknown_difficulty_falls_back_to_full_range():
    assert get_range_for_difficulty("???") == (1, 100)

def test_old_hard_secret_is_out_of_easy_range():
    # This is the bug: a valid Hard secret can be outside the Easy range.
    # It proves regeneration is necessary, not optional.
    low, high = get_range_for_difficulty("Easy")
    assert not (low <= 80 <= high)

def test_regenerated_secret_is_always_within_new_range():
    # Run many times because regenerate_secret is randomized; every draw
    # must land inside the selected difficulty's range.
    for difficulty in ["Easy", "Normal", "Hard"]:
        low, high = get_range_for_difficulty(difficulty)
        for _ in range(500):
            secret = regenerate_secret(difficulty)
            assert low <= secret <= high

def test_switching_to_easy_yields_guessable_secret():
    # Regression for the reported bug: after switching Hard -> Easy, the new
    # secret must be reachable within Easy's range on every draw.
    easy_low, easy_high = get_range_for_difficulty("Easy")
    for _ in range(500):
        new_secret = regenerate_secret("Easy")
        assert easy_low <= new_secret <= easy_high


# ---------------------------------------------------------------------------
# Edge-case inputs that can still break the game.
# Three categories a player can realistically type: decimals, extremely large
# values, and negative / out-of-range integers. Each is checked for GRACEFUL
# handling — a clean rejection or a safe, range-checkable int, but never a
# crash and never a guess the player did not actually type.
# ---------------------------------------------------------------------------

# --- Edge case 1: Decimal / float strings --------------------------------
# Regression for the silent-truncation glitch: parse_guess used to do
# int(float(raw)) for any input containing ".", so "3.9" became the guess 3
# and ".5" became 0 with no warning. A decimal is not a whole-number guess,
# so it must now be rejected with a clear error and never counted as a guess.

def test_decimal_input_is_rejected():
    ok, value, err = parse_guess("3.9")
    assert ok is False
    assert value is None
    assert err is not None

def test_decimal_with_trailing_zero_is_rejected():
    # "10.0" is still text typed as a decimal; reject for a consistent contract.
    ok, value, err = parse_guess("10.0")
    assert ok is False
    assert value is None

def test_leading_dot_decimal_is_rejected_not_zero():
    # ".5" must not become the guess 0; it must be a clean rejection (no crash).
    ok, value, err = parse_guess(".5")
    assert ok is False
    assert value is None

def test_negative_decimal_is_rejected():
    # "-2.5" must not be truncated to -2.
    ok, value, err = parse_guess("-2.5")
    assert ok is False
    assert value is None


# --- Edge case 2: Extremely large values ---------------------------------
# Python ints are unbounded, so parse_guess accepts a 20-digit number without
# crashing. That is fine at the parse layer; the game's range check is what
# rejects it. These tests pin both halves of that contract.

def test_extremely_large_value_parses_without_crashing():
    big = "9" * 20
    ok, value, err = parse_guess(big)
    assert ok is True
    assert value == int(big)
    assert err is None

def test_extremely_large_value_is_out_of_every_range():
    # However it parses, a 20-digit guess must never fall inside a playable
    # range, so the game's range check will reject it before counting it.
    huge = int("9" * 20)
    for difficulty in ["Easy", "Normal", "Hard"]:
        low, high = get_range_for_difficulty(difficulty)
        assert not (low <= huge <= high)


# --- Edge case 3: Negative / out-of-range integers -----------------------
# Negatives and zero parse cleanly, so the range check is the only thing
# stopping them from burning an attempt. Pin that contract so a future
# refactor can't quietly let an out-of-range guess through.

def test_negative_guess_is_out_of_playable_range():
    low, high = get_range_for_difficulty("Normal")  # (1, 50)
    ok, value, err = parse_guess("-5")
    assert ok is True                    # parses cleanly...
    assert not (low <= value <= high)    # ...but is out of range and must be rejected

def test_zero_is_below_every_range():
    ok, value, err = parse_guess("0")
    assert ok is True
    assert value == 0
    for difficulty in ["Easy", "Normal", "Hard"]:
        low, _high = get_range_for_difficulty(difficulty)
        assert low > 0                   # ranges start at 1, so 0 is always rejected
