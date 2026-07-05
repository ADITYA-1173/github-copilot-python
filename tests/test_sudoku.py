"""Tests for the pure Sudoku logic (`sudoku.py`)."""

import copy

import pytest

from sudoku import (
    DIFFICULTY_HOLES,
    board_conflicts,
    count_solutions,
    generate_full_board,
    generate_puzzle,
    is_complete,
    is_safe,
    solve,
)


# --------- helpers ---------
def _is_full_valid(board):
    if any(0 in row for row in board):
        return False
    for i in range(9):
        if sorted(board[i]) != list(range(1, 10)):
            return False
        if sorted(board[r][i] for r in range(9)) != list(range(1, 10)):
            return False
    for br in range(0, 9, 3):
        for bc in range(0, 9, 3):
            block = [board[br + r][bc + c] for r in range(3) for c in range(3)]
            if sorted(block) != list(range(1, 10)):
                return False
    return True


# --------- is_safe / solve ---------
def test_is_safe_detects_row_conflict():
    board = [[0] * 9 for _ in range(9)]
    board[0][0] = 5
    assert not is_safe(board, 0, 4, 5)
    assert is_safe(board, 0, 4, 3)


def test_solve_solves_a_known_puzzle():
    puzzle = [
        [5, 3, 0, 0, 7, 0, 0, 0, 0],
        [6, 0, 0, 1, 9, 5, 0, 0, 0],
        [0, 9, 8, 0, 0, 0, 0, 6, 0],
        [8, 0, 0, 0, 6, 0, 0, 0, 3],
        [4, 0, 0, 8, 0, 3, 0, 0, 1],
        [7, 0, 0, 0, 2, 0, 0, 0, 6],
        [0, 6, 0, 0, 0, 0, 2, 8, 0],
        [0, 0, 0, 4, 1, 9, 0, 0, 5],
        [0, 0, 0, 0, 8, 0, 0, 7, 9],
    ]
    assert solve(puzzle)
    assert _is_full_valid(puzzle)


# --------- generation ---------
def test_generate_full_board_is_valid():
    board = generate_full_board()
    assert _is_full_valid(board)


@pytest.mark.parametrize("difficulty", ["easy", "medium", "hard"])
def test_generate_puzzle_has_unique_solution(difficulty):
    puzzle, solution = generate_puzzle(difficulty)
    assert _is_full_valid(solution)
    # Puzzle must be a subset of solution.
    for r in range(9):
        for c in range(9):
            assert puzzle[r][c] in (0, solution[r][c])
    # Uniqueness: exactly one solution.
    assert count_solutions(copy.deepcopy(puzzle), limit=2) == 1


def test_generate_puzzle_holes_scale_with_difficulty():
    easy, _ = generate_puzzle("easy")
    hard, _ = generate_puzzle("hard")
    easy_holes = sum(row.count(0) for row in easy)
    hard_holes = sum(row.count(0) for row in hard)
    assert hard_holes >= easy_holes


def test_generate_puzzle_invalid_difficulty():
    with pytest.raises(ValueError):
        generate_puzzle("impossible")


# --------- conflicts & completion ---------
def test_board_conflicts_flags_duplicate_row():
    board = [[0] * 9 for _ in range(9)]
    board[0][0] = 4
    board[0][5] = 4
    conflicts = board_conflicts(board)
    assert (0, 0) in conflicts and (0, 5) in conflicts


def test_board_conflicts_empty_board_has_none():
    assert board_conflicts([[0] * 9 for _ in range(9)]) == []


def test_is_complete_true_for_solved_board():
    board = generate_full_board()
    assert is_complete(board)


def test_is_complete_false_for_partial_board():
    board = generate_full_board()
    board[0][0] = 0
    assert not is_complete(board)


def test_difficulty_constants_defined():
    for k in ("easy", "medium", "hard"):
        assert k in DIFFICULTY_HOLES
