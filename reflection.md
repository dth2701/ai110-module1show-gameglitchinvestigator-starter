# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

- What did the game look like the first time you ran it? 

A game is to guess a number between 1 and 100 with 8 attempts in 3 different modes. It has "Submit Guess" button to submit your number, "New Game" button to restart a game, and a "Show hint" checkbox to show the Go LOWER/Go HIGHER hints after clicking the "Submit Guess" button. Lastly, it has a "Developer Debug Info" chart to save the history of every previous times we played,
- List at least two concrete bugs you noticed at the start  
  (for example: "the hints were backwards").

I did not recognized anything at the start, only while I played the game.

**Bug Reproduction Log**

Document at least 3 bugs you found. Add rows as needed.

| Input | Expected Behavior | Actual Behavior | Console Output / Error |
|-------|-------------------|-----------------|------------------------|
| Guess 3| Go HIGHER! hint shown  | Go LOWER! hint shown, then Go HIGHER! hint shown repeated | none|
| New Game buttion| It should refresh the page but the history is still there| Does not change anything | None|
| Secret| between 1 to 100 only| Negative number shown. Ex: -35 | |

---

## 2. How did you use AI as a teammate?

- Which AI tools did you use on this project (for example: ChatGPT, Gemini, Copilot)? 

Claude

- Give one example of an AI suggestion that was correct (including what the AI suggested and how you verified the result). 

When I guessed 3 against a secret of 61, the game showed "Go LOWER!" even though I expected "Go HIGHER!". Claude traced it through the `check_guess` function and pointed out two problems: first, the secret was being turned into a string with `str()` on even attempts, which made the int-vs-string comparison fall into a `TypeError` branch that compared the numbers as text (so "3" looked "bigger" than "61"); and second, even after I fixed that, the hint messages inside `check_guess` were swapped — the "Too Low" outcome was paired with "Go LOWER!" instead of "Go HIGHER!". I verified the suggestion by passing the secret as an int and swapping the two message strings, then reran the app and guessed several low and high numbers: a low guess now correctly says "Go HIGHER!" and a high guess says "Go LOWER!".

- Give one example of an AI suggestion that was incorrect or misleading (including what the AI suggested and how you verified the result).

When I asked Claude to generate a pytest case in tests/test_game_logic.py, it failed with ModuleNotFoundError: No module named 'logic_utils'. Claude correctly explained that logic_utils.py is in the project root but I was running pytest from inside tests/, so the root wasn't on Python's import path. Its fix, though, was misleading: it told me to add an empty conftest.py at the project root. I tried it and got the same error, because running pytest from inside tests/ makes that folder the rootdir, so pytest never finds a root-level conftest.py. The suggestion just added an unnecessary file without fixing anything. The real fix was three lines at the top of the test file that add the project root to sys.path before the import.

---

## 3. Debugging and testing your fixes

- How did you decide whether a bug was really fixed? 

After making a fix, I reran the app and manually tested the specific feature that was broken — for example,  a "Too High/Low" hint . I considered the bug fixed when the behavior matched what I expected and no new errors appeared in the terminal or browser console. 

- Describe at least one test you ran (manual or using pytest)  
  and what it showed you about your code.

I ran the pytest suite in tests/test_game_logic.py, which has three cases: test_winning_guess checks that a guess of 50 against a secret of 50 returns "Win", test_guess_too_high checks that 60 against 50 returns "Too High", and test_guess_too_low checks that 40 against 50 returns "Too Low". After fixing the bugs, all three passed (3 passed). This showed me that check_guess was now returning the correct outcome for the win, high, and low cases, and confirmed the earlier bugs which are the string-vs-int comparison and the swapped hint messages. They were really gone, not just appearing fixed in one manual run.

- Did AI help you design or understand any tests? How?

Yes. The AI helped me get the tests running in the first place — when pytest failed with ModuleNotFoundError: No module named 'logic_utils', it explained that the test folder wasn't on Python's import path and showed me how to fix it. It also helped me understand why each test was structured as check_guess(guess, secret) returning an (outcome, message) tuple, so I could read the asserts and know exactly which behavior each test was protecting.
---

## 4. What did you learn about Streamlit and state?

- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?

---

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects?
  - This could be a testing habit, a prompting strategy, or a way you used Git.
- What is one thing you would do differently next time you work with AI on a coding task?
- In one or two sentences, describe how this project changed the way you think about AI generated code.
