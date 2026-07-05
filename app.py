"""Flask entry point for the Sudoku web app.

Routes:
    GET  /               -> renders the game page.
    POST /api/new_game   -> returns a new puzzle + solution.
    POST /api/check      -> validates a submitted board.
    POST /api/hint       -> returns one correct value for an empty cell.

The solution is returned to the client so all validation can happen locally;
the server is stateless. This keeps the app trivially horizontally scalable
and simplifies testing.
"""

from __future__ import annotations

import logging
import random
from typing import Any, Dict

from flask import Flask, jsonify, render_template, request

from sudoku import (
    DIFFICULTY_HOLES,
    board_conflicts,
    generate_puzzle,
    is_complete,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

app = Flask(__name__)


@app.route("/")
def index() -> str:
    """Render the main game page."""
    return render_template("index.html")


@app.post("/api/new_game")
def new_game() -> Any:
    """Generate a new puzzle.

    Request JSON: {"difficulty": "easy" | "medium" | "hard"}
    Response JSON: {"puzzle": [[...]], "solution": [[...]], "difficulty": "..."}
    """
    data: Dict[str, Any] = request.get_json(silent=True) or {}
    difficulty = str(data.get("difficulty", "medium")).lower()
    if difficulty not in DIFFICULTY_HOLES:
        return jsonify({"error": f"Invalid difficulty '{difficulty}'"}), 400

    try:
        puzzle, solution = generate_puzzle(difficulty)
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Puzzle generation failed")
        return jsonify({"error": str(exc)}), 500

    logger.info("Generated %s puzzle", difficulty)
    return jsonify(
        {"puzzle": puzzle, "solution": solution, "difficulty": difficulty}
    )


@app.post("/api/check")
def check() -> Any:
    """Check a submitted board.

    Request JSON: {"board": [[...]]}
    Response JSON:
        {
            "complete": bool,   # solved correctly
            "conflicts": [[r, c], ...],   # cells with rule violations
        }
    """
    data: Dict[str, Any] = request.get_json(silent=True) or {}
    board = data.get("board")
    if not _is_valid_board_shape(board):
        return jsonify({"error": "Invalid board shape"}), 400

    conflicts = board_conflicts(board)
    return jsonify({"complete": is_complete(board), "conflicts": conflicts})


@app.post("/api/hint")
def hint() -> Any:
    """Return one correct value for a random empty cell.

    Request JSON: {"board": [[...]], "solution": [[...]]}
    Response JSON: {"row": r, "col": c, "value": v}  or  {"row": null} when full.
    """
    data: Dict[str, Any] = request.get_json(silent=True) or {}
    board = data.get("board")
    solution = data.get("solution")
    if not _is_valid_board_shape(board) or not _is_valid_board_shape(solution):
        return jsonify({"error": "Invalid board shape"}), 400

    empties = [
        (r, c)
        for r in range(9)
        for c in range(9)
        if board[r][c] == 0
    ]
    if not empties:
        return jsonify({"row": None, "col": None, "value": None})

    r, c = random.choice(empties)
    return jsonify({"row": r, "col": c, "value": solution[r][c]})


def _is_valid_board_shape(board: Any) -> bool:
    """Return True if `board` is a 9x9 list of ints in [0, 9]."""
    if not isinstance(board, list) or len(board) != 9:
        return False
    for row in board:
        if not isinstance(row, list) or len(row) != 9:
            return False
        for v in row:
            if not isinstance(v, int) or v < 0 or v > 9:
                return False
    return True


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
