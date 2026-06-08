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

def test_negative_number_is_accepted():
    # A negative number should parse cleanly so it can be range-checked downstream
    ok, value, err = parse_guess("-5")
    assert ok is True
    assert value == -5
    assert err is None

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
