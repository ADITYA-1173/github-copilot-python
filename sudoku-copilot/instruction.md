# Copilot Instruction File

This file tells GitHub Copilot how to assist on this repository. Follow these
rules when generating or editing code.

## Project Overview
A Flask-based Sudoku web app. Backend generates puzzles with a **unique
solution** at three difficulty levels; frontend provides an interactive board
with timer, hints, checking, dark mode, and a persistent Top 10 leaderboard.

## Tech Stack
- **Backend:** Python 3.10+, Flask
- **Frontend:** Vanilla HTML5 + CSS3 + ES6 JavaScript (no frameworks)
- **Persistence:** `localStorage` for the Top 10 leaderboard
- **Testing:** `pytest`

## Code Style
### Python
- Follow **PEP 8**, 4-space indent, max line length ~100.
- Use **type hints** on all public functions.
- Write **docstrings** (Google style) for every module, class, and function.
- Prefer small, pure functions. Isolate side effects.
- Use `logging` (not `print`) for diagnostics.
- Raise specific exceptions; never `except:` bare.

### JavaScript
- Use `const`/`let`, never `var`.
- Prefer arrow functions and template literals.
- Keep DOM logic separate from game logic.
- Use `data-*` attributes rather than parsing IDs.

### CSS
- Use CSS custom properties (variables) for theming.
- Mobile-first, responsive breakpoints.
- Support both light and dark modes via a `[data-theme="dark"]` selector.
- Alternate 3×3 sub-grid backgrounds using `:nth-child`.

## Architecture Rules
- Keep Sudoku logic in `sudoku.py` — no Flask imports there.
- Keep HTTP routes thin in `app.py`; they call into `sudoku.py`.
- The frontend never trusts client-side board state for scoring — the server
  owns the solution.
- Every new feature must have a corresponding test in `tests/`.

## Naming
- `snake_case` for Python identifiers, `camelCase` for JS, `kebab-case` for CSS
  classes and file names.
- Prefix private helpers with `_`.

## Testing Standards
- Run tests with: `pytest -v`
- Every backend function should have at least one happy-path and one edge-case
  test.
- Do not commit code until `pytest` is green.

## Accessibility & UX
- All interactive elements must be reachable by keyboard.
- Use semantic HTML (`<button>`, `<label>`, `<table>`).
- Provide `aria-label` on icon-only buttons.
- Ensure color contrast passes WCAG 2.1 AA in both themes.

## Do Not
- Do not introduce heavy dependencies (React, jQuery, Bootstrap) — keep the
  bundle tiny.
- Do not hard-code puzzles; always generate them.
- Do not store the solution in the DOM or in `localStorage`.
