"""Tests for the Flask HTTP layer (`app.py`)."""

import pytest

from app import app as flask_app


@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as c:
        yield c


def test_index_renders(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"Sudoku" in resp.data


def test_new_game_returns_valid_shape(client):
    resp = client.post("/api/new_game", json={"difficulty": "easy"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["difficulty"] == "easy"
    assert len(data["puzzle"]) == 9 and all(len(r) == 9 for r in data["puzzle"])
    assert len(data["solution"]) == 9


def test_new_game_rejects_bad_difficulty(client):
    resp = client.post("/api/new_game", json={"difficulty": "insane"})
    assert resp.status_code == 400


def test_check_flags_conflicts(client):
    board = [[0] * 9 for _ in range(9)]
    board[0][0] = 5
    board[0][5] = 5
    resp = client.post("/api/check", json={"board": board})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["complete"] is False
    assert [0, 0] in data["conflicts"]
    assert [0, 5] in data["conflicts"]


def test_check_rejects_bad_shape(client):
    resp = client.post("/api/check", json={"board": [[1, 2, 3]]})
    assert resp.status_code == 400


def test_hint_returns_valid_cell(client):
    game = client.post("/api/new_game", json={"difficulty": "medium"}).get_json()
    resp = client.post(
        "/api/hint",
        json={"board": game["puzzle"], "solution": game["solution"]},
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["row"] is not None
    r, c, v = data["row"], data["col"], data["value"]
    assert game["puzzle"][r][c] == 0
    assert game["solution"][r][c] == v


def test_hint_returns_null_when_full(client):
    board = [[((i + j) % 9) + 1 for j in range(9)] for i in range(9)]
    resp = client.post("/api/hint", json={"board": board, "solution": board})
    assert resp.status_code == 200
    assert resp.get_json()["row"] is None
