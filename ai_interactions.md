# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agent Workflow (SF8)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

I asked the Claude agent to plan and implement a meaningful new feature for the guessing game — a **High Score tracker** that records the best score for each difficulty level (Easy / Normal / Hard). I then refined the requirement: the high scores should live only in the browser session, so **refreshing the page resets every level's high score back to 0**.

**What did the agent do?**

1. **Explored the codebase first** — read `app.py`, `logic_utils.py`, the test suite, `requirements.txt`, and `.gitignore` to understand how the game stored state before writing any code.
2. **Added high-score logic** to `logic_utils.py`: an `update_high_score(scores, difficulty, score)` helper that records a finished round's score against the best for its difficulty, returning `(updated_scores, is_record)`. It only flags a record on a *strict* beat, so ties don't falsely celebrate.
3. **Wired it into `app.py`**:
   - Initialized `st.session_state.high_scores = {"Easy": 0, "Normal": 0, "Hard": 0}` (in-memory only, so a page refresh resets it).
   - Added a "🏆 High Scores" section to the sidebar showing the best per level, with a ⬅️ marker on the active difficulty.
   - Updated the high score on a win and showed a "New high score!" message when beaten.
4. **Course-corrected on persistence** — its first version saved to a `high_scores.json` file (with corrupt-file handling and a `.gitignore` entry). When I clarified I wanted refresh-resets-to-0, it removed the file I/O entirely, reverted the `.gitignore` change, and kept the scores purely in session state.
5. **Fixed a related scoring bug** I spotted — the score was a single cumulative counter that never reset, so it climbed across every round and difficulty, polluting the per-level high score. The agent reset `score` (and `history`) to 0 on both **New Game** and **difficulty change**, making each round's score self-contained.
6. **Ran the app** (`streamlit run app.py`) after each major change so I could verify behavior in the browser.

**What did you have to verify or fix manually?**

- I had to **correct the persistence approach** — the agent initially assumed disk persistence (a JSON file) was the goal. I clarified that I wanted session-only scores that reset on refresh, and it adjusted.
- I **caught the cumulative-score bug** during manual play (the total kept adding up across levels). The agent then traced it to the never-reset `score` state and fixed it.
- I verified the final behavior in the running app: scores are per-round, the sidebar shows correct per-level bests, and a page refresh clears them to 0.

---

## Test Generation (SF7)

> Document how you used AI to help generate or improve tests.

| Edge Case | Prompt Used | AI-Suggested Test | Did It Pass? | Your Reasoning |
|-----------|-------------|-------------------|--------------|----------------|
| Handle negative numbers and decimals | help me to generate these 2 "edge case" inputs (negative numbers and decimals) to test if these "edge case" got rejected| `test_decimal_guess_is_rejected` feeds `"4.5"` and asserts `parse_guess` returns `ok=False, value=None, err!=None`; `test_negative_guess_is_rejected_by_range` feeds `"-5"`, asserts it parses cleanly (`ok=True, value=-5`) but falls outside the `(1, 50)` range. | Yes | Decimals were chosen because a player can type `"4.5"` and it must not be silently truncated to a whole-number guess; negatives were chosen because `"-5"` parses fine but is outside any valid range and shouldn't burn an attempt. |
| | | | | |
| | | | | |

---

## Linting & Style (SF9)

> Document your use of AI for linting or code style improvements.

**Prompt used:**

```
1. Add professional-grade docstrings to every function in logic_utils.py.
2. Review your code for PEP 8 style compliance and apply its suggestions
   to resolve any formatting or naming issues it identifies.
```

**Linting output before:**

No linter was installed in the environment, and an offline `pip install
pycodestyle` failed, so I had the AI check the one objective, measurable
rule programmatically (line length) and inspect the rest by hand. The
check surfaced four issues:

```
E501 line too long (80 > 79)   logic_utils.py:102   check_guess docstring
E501 line too long (82 > 79)   logic_utils.py:103   check_guess docstring
E501 line too long (82 > 79)   logic_utils.py:157   update_high_score docstring
E265 block comment should start with '# '   logic_utils.py:107   "#FIX:" had no space
```

**Changes applied:**

1. **Added Google-style docstrings to all six functions** in `logic_utils.py`
   (`get_range_for_difficulty`, `regenerate_secret`, `parse_guess`,
   `check_guess`, `update_score`, `update_high_score`). Each now documents its
   `Args:`, `Returns:` (with exact types and the meaning of every tuple
   element), and the non-obvious behavioral rules — e.g. the win-bonus formula
   and 10-point floor, the "Too High" even/odd parity quirk, and the
   strict-`>` (ties don't count) high-score rule. Related functions and the
   `DIFFICULTIES` constant are cross-referenced. No logic was changed — only
   documentation.
2. **Fixed the PEP 8 violations** the review found:
   - Reflowed the over-length `check_guess` docstring bullets (lines 102–103),
     dropping the cosmetic alignment padding so each line fits within 79 chars.
   - Shortened the `update_high_score` summary line ("a finished round's score"
     → "a round's score") to clear the 79-char limit.
   - Added the missing space to the block comment: `#FIX:` → `# FIX:` (E265).
3. **Verified the result**: the file parses with `ast.parse`, and no line
   exceeds 79 characters. Naming was already compliant (snake_case functions
   and variables, `UPPER_CASE` `DIFFICULTIES` constant), as was the two-blank-
   line spacing between top-level definitions, so no renames were needed.

---

## Model Comparison (SF11)

> Compare two AI models on the same task.

**Task given to both models:**

<!-- Describe what you asked each model to do -->

| | Model A | Model B |
|-|---------|---------|
| **Model name** | | |
| **Response summary** | | |
| **More Pythonic?** | | |
| **Clearer explanation?** | | |

**Which did you prefer and why?**

<!-- Your conclusion -->
