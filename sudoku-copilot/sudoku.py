"""Sudoku core: board generation, solving, and unique-solution validation.

This module has zero Flask/web dependencies so it can be tested in isolation.
Boards are represented as 9x9 lists of ints, where 0 means an empty cell.
"""

from __future__ import annotations

import copy
import random
from typing import List, Optional, Tuple

Board = List[List[int]]
SIZE = 9
BOX = 3

DIFFICULTY_HOLES = {
    "easy": 40,     # ~41 clues
    "medium": 48,   # ~33 clues
    "hard": 54,     # ~27 clues (very hard)
}


# ---------- validation helpers ----------

def is_safe(board: Board, row: int, col: int, num: int) -> bool:
    """Return True if placing `num` at (row, col) breaks no Sudoku rule."""
    for i in range(SIZE):
        if board[row][i] == num or board[i][col] == num:
            return False
    br, bc = (row // BOX) * BOX, (col // BOX) * BOX
    for r in range(br, br + BOX):
        for c in range(bc, bc + BOX):
            if board[r][c] == num:
                return False
    return True


def find_empty(board: Board) -> Optional[Tuple[int, int]]:
    """Return the (row, col) of the first empty cell, or None if full."""
    for r in range(SIZE):
        for c in range(SIZE):
            if board[r][c] == 0:
                return r, c
    return None


def _find_best_empty(board: Board) -> Optional[Tuple[int, int, List[int]]]:
    """Return (row, col, candidates) for the empty cell with fewest options.

    Using the Most-Constrained-Variable heuristic dramatically prunes the
    search tree, making `count_solutions` fast enough for hard puzzles.
    """
    best: Optional[Tuple[int, int, List[int]]] = None
    best_len = 10
    for r in range(SIZE):
        for c in range(SIZE):
            if board[r][c] != 0:
                continue
            options = [n for n in range(1, 10) if is_safe(board, r, c, n)]
            if not options:
                return r, c, options  # dead-end short-circuit
            if len(options) < best_len:
                best_len = len(options)
                best = (r, c, options)
                if best_len == 1:
                    return best
    return best


# ---------- solving ----------

def solve(board: Board) -> bool:
    """Solve `board` in place using backtracking. Returns True on success."""
    empty = find_empty(board)
    if not empty:
        return True
    r, c = empty
    for num in range(1, 10):
        if is_safe(board, r, c, num):
            board[r][c] = num
            if solve(board):
                return True
            board[r][c] = 0
    return False


def count_solutions(board: Board, limit: int = 2) -> int:
    """Count solutions of `board`, stopping early once `limit` is reached.

    Uses the Most-Constrained-Variable heuristic for speed. We only need to
    distinguish 0 / 1 / >=2, so early exit is fine.
    """
    best = _find_best_empty(board)
    if best is None:
        return 1
    r, c, options = best
    if not options:
        return 0
    total = 0
    for num in options:
        board[r][c] = num
        total += count_solutions(board, limit - total)
        board[r][c] = 0
        if total >= limit:
            return total
    return total


# ---------- generation ----------

def _fill_board(board: Board) -> bool:
    """Fill an empty board with a random valid Sudoku solution."""
    empty = find_empty(board)
    if not empty:
        return True
    r, c = empty
    nums = list(range(1, 10))
    random.shuffle(nums)
    for num in nums:
        if is_safe(board, r, c, num):
            board[r][c] = num
            if _fill_board(board):
                return True
            board[r][c] = 0
    return False


def generate_full_board() -> Board:
    """Return a random fully-solved 9x9 Sudoku board."""
    board: Board = [[0] * SIZE for _ in range(SIZE)]
    _fill_board(board)
    return board


def generate_puzzle(difficulty: str = "medium") -> Tuple[Board, Board]:
    """Generate a puzzle with exactly one solution.

    Args:
        difficulty: One of "easy", "medium", "hard".

    Returns:
        (puzzle, solution) — both 9x9 boards. `puzzle` has zeros for blanks.
    """
    difficulty = difficulty.lower()
    if difficulty not in DIFFICULTY_HOLES:
        raise ValueError(f"Unknown difficulty: {difficulty}")

    solution = generate_full_board()
    puzzle = copy.deepcopy(solution)

    target_holes = DIFFICULTY_HOLES[difficulty]
    cells = [(r, c) for r in range(SIZE) for c in range(SIZE)]
    random.shuffle(cells)

    holes = 0
    for r, c in cells:
        if holes >= target_holes:
            break
        saved = puzzle[r][c]
        puzzle[r][c] = 0
        # Ensure the puzzle still has exactly one solution.
        test = copy.deepcopy(puzzle)
        if count_solutions(test, limit=2) != 1:
            puzzle[r][c] = saved  # revert; would create ambiguity
        else:
            holes += 1

    return puzzle, solution


# ---------- convenience ----------

def board_conflicts(board: Board) -> List[Tuple[int, int]]:
    """Return a list of (row, col) cells that violate Sudoku rules.

    A cell is flagged if its value duplicates within its row, column, or box.
    Empty (0) cells are ignored.
    """
    conflicts: set[Tuple[int, int]] = set()

    def _scan(cells: List[Tuple[int, int]]) -> None:
        seen: dict[int, Tuple[int, int]] = {}
        for r, c in cells:
            v = board[r][c]
            if v == 0:
                continue
            if v in seen:
                conflicts.add((r, c))
                conflicts.add(seen[v])
            else:
                seen[v] = (r, c)

    for r in range(SIZE):
        _scan([(r, c) for c in range(SIZE)])
    for c in range(SIZE):
        _scan([(r, c) for r in range(SIZE)])
    for br in range(0, SIZE, BOX):
        for bc in range(0, SIZE, BOX):
            _scan([(br + dr, bc + dc) for dr in range(BOX) for dc in range(BOX)])

    return sorted(conflicts)


def is_complete(board: Board) -> bool:
    """Return True if the board is fully filled and valid."""
    if any(0 in row for row in board):
        return False
    return not board_conflicts(board)
