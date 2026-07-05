# 🧩 Sudoku — GitHub Copilot Refactor Project

A modernised, fully featured Sudoku game refactored from a legacy Flask starter
using GitHub Copilot. Includes puzzle generation with **guaranteed unique
solutions**, difficulty levels, timer, hints, live validation, dark mode, and a
persistent Top 10 leaderboard.

---

## ✨ Features

| Category            | Feature                                                                 |
| ------------------- | ----------------------------------------------------------------------- |
| Puzzle              | Backtracking generator with unique-solution validation                  |
| Difficulty          | Easy / Medium / Hard (adjusts number of prefilled cells)                |
| Feedback            | Real-time conflict highlighting, per-cell live validation               |
| Hint / Check        | Hint fills one correct cell (locked); Check flags incorrect entries     |
| Timer               | Live MM:SS timer, stops on completion                                   |
| Completion          | Congratulatory modal with time, difficulty, hints used                  |
| Scoreboard          | Top 10 fastest times persisted to `localStorage`                        |
| Theme               | Light / Dark mode toggle, remembered across sessions                    |
| Accessibility       | Semantic HTML, keyboard arrow-key navigation, aria labels               |
| Responsive          | Scales cleanly from mobile to desktop                                   |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- pip

### Setup
```bash
# 1. clone
git clone https://github.com/<your-username>/github-copilot-python.git
cd github-copilot-python

# 2. create virtual env (recommended)
python -m venv .venv
source .venv/bin/activate     # Windows: .venv\Scripts\activate

# 3. install dependencies
pip install -r requirements.txt

# 4. run the app
python app.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

---

## 🧪 Running Tests

```bash
pytest -v
```

This runs all backend tests in `tests/`. All tests must pass before deploying
or committing changes.

---

## 📁 Project Structure

```
.
├── app.py                  # Flask routes / HTTP layer
├── sudoku.py               # Pure Sudoku logic (generator, solver, validation)
├── instruction.md          # Copilot instruction / style file
├── requirements.txt
├── prompts.json            # Reusable Copilot prompt templates (bonus)
├── README.md
├── templates/
│   └── index.html
├── static/
│   ├── css/styles.css
│   └── js/app.js
├── tests/
│   ├── __init__.py
│   ├── test_sudoku.py      # Logic tests
│   └── test_app.py         # HTTP tests
└── Screenshots/            # Copilot-usage screenshots for submission
```

---

## 🧠 Design Notes

- **Server owns the solution.** The frontend calls `/api/new_game` and
  receives the puzzle + solution. All validation logic runs client-side for
  responsiveness, while `/api/check` and `/api/hint` remain the source of truth.
- **Unique-solution guarantee.** The generator removes cells one at a time and
  reverts the removal if it would produce more than one solution
  (`count_solutions(..., limit=2)` — uses MRV heuristic for speed).
- **Zero heavy dependencies.** No React/jQuery/Bootstrap — just Flask +
  vanilla ES6 + plain CSS with custom properties for theming.

---

## 🖼️ Screenshots

See the `Screenshots/` folder for:
- `initial_tests.png` – proof the test framework is set up and passing.
- `copilot_*` – Copilot prompts and responses at each milestone.

---

## 🏆 Standout Features Implemented

- ✅ Alternating 3×3 box shading
- ✅ Light / Dark mode with persistence
- ✅ Keyboard navigation
- ✅ `prompts.json` with reusable Copilot prompts
- ✅ Aria labels for screen readers
