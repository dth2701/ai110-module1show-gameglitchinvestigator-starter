import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from logic_utils import check_guess, parse_guess

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
