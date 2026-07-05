/**
 * Sudoku Front-End
 * ----------------
 * Owns board rendering, timer, live validation, hints, dark mode,
 * and the persistent Top 10 leaderboard (localStorage).
 */

(() => {
    "use strict";

    // ---------- State ----------
    const state = {
        puzzle: null,       // initial 9x9
        solution: null,     // 9x9 solution from server
        current: null,      // 9x9 as user edits
        locked: null,       // 9x9 booleans - prefilled/hint locked
        difficulty: "medium",
        startTime: null,
        timerId: null,
        hintsUsed: 0,
        finished: false,
    };

    const STORAGE_KEY = "sudoku_top10_v1";
    const MAX_SCORES = 10;

    // ---------- DOM ----------
    const $ = (sel) => document.querySelector(sel);
    const boardEl = $("#board");
    const timerEl = $("#timer");
    const scoresBody = $("#scores-body");
    const modal = $("#win-modal");
    const winSummary = $("#win-summary");
    const nameInput = $("#player-name");

    // ---------- Board rendering ----------
    function renderBoard() {
        boardEl.innerHTML = "";
        for (let r = 0; r < 9; r++) {
            const tr = document.createElement("tr");
            for (let c = 0; c < 9; c++) {
                const td = document.createElement("td");
                // Thick borders between 3x3 boxes.
                if ((c + 1) % 3 === 0 && c !== 8) td.classList.add("box-right");
                if ((r + 1) % 3 === 0 && r !== 8) td.classList.add("box-bottom");
                // Alternating 3x3 box shading (checkerboard pattern of boxes).
                const boxIndex = Math.floor(r / 3) * 3 + Math.floor(c / 3);
                if (boxIndex % 2 === 0) td.classList.add("box-shaded");

                const input = document.createElement("input");
                input.type = "text";
                input.inputMode = "numeric";
                input.maxLength = 1;
                input.dataset.row = r;
                input.dataset.col = c;
                input.setAttribute("aria-label", `Row ${r + 1} Column ${c + 1}`);

                const val = state.puzzle[r][c];
                if (val !== 0) {
                    input.value = val;
                    input.classList.add("locked");
                    input.readOnly = true;
                }

                input.addEventListener("input", onCellInput);
                input.addEventListener("keydown", onCellKeydown);

                td.appendChild(input);
                tr.appendChild(td);
            }
            boardEl.appendChild(tr);
        }
    }

    function getInput(r, c) {
        return boardEl.querySelector(`input[data-row="${r}"][data-col="${c}"]`);
    }

    // ---------- Cell handlers ----------
    function onCellInput(e) {
        const input = e.target;
        const r = +input.dataset.row;
        const c = +input.dataset.col;
        const raw = input.value.replace(/[^1-9]/g, "");
        input.value = raw;
        state.current[r][c] = raw ? +raw : 0;
        input.classList.remove("conflict", "hint");
        liveValidate();
        maybeWin();
    }

    function onCellKeydown(e) {
        // Arrow-key navigation for accessibility.
        const r = +e.target.dataset.row;
        const c = +e.target.dataset.col;
        const moves = { ArrowUp: [-1, 0], ArrowDown: [1, 0], ArrowLeft: [0, -1], ArrowRight: [0, 1] };
        if (moves[e.key]) {
            e.preventDefault();
            const [dr, dc] = moves[e.key];
            const nr = (r + dr + 9) % 9;
            const nc = (c + dc + 9) % 9;
            getInput(nr, nc).focus();
        }
    }

    // ---------- Live validation ----------
    /** Mark cells that violate row/column/box constraints. */
    function liveValidate() {
        // Clear prior conflicts.
        boardEl.querySelectorAll("input.conflict").forEach((i) => i.classList.remove("conflict"));
        const conflicts = findConflicts(state.current);
        conflicts.forEach(([r, c]) => getInput(r, c).classList.add("conflict"));
    }

    function findConflicts(board) {
        const conflicts = new Set();
        const scan = (cells) => {
            const seen = new Map();
            for (const [r, c] of cells) {
                const v = board[r][c];
                if (!v) continue;
                if (seen.has(v)) {
                    conflicts.add(`${r},${c}`);
                    conflicts.add(seen.get(v));
                } else seen.set(v, `${r},${c}`);
            }
        };
        for (let r = 0; r < 9; r++) scan(range9().map((c) => [r, c]));
        for (let c = 0; c < 9; c++) scan(range9().map((r) => [r, c]));
        for (let br = 0; br < 9; br += 3) {
            for (let bc = 0; bc < 9; bc += 3) {
                const cells = [];
                for (let dr = 0; dr < 3; dr++)
                    for (let dc = 0; dc < 3; dc++) cells.push([br + dr, bc + dc]);
                scan(cells);
            }
        }
        return [...conflicts].map((s) => s.split(",").map(Number));
    }
    const range9 = () => [0, 1, 2, 3, 4, 5, 6, 7, 8];

    // ---------- Win detection ----------
    function isSolved() {
        for (let r = 0; r < 9; r++)
            for (let c = 0; c < 9; c++)
                if (state.current[r][c] !== state.solution[r][c]) return false;
        return true;
    }

    function maybeWin() {
        if (state.finished || !isSolved()) return;
        state.finished = true;
        stopTimer();
        winSummary.textContent = `Difficulty: ${state.difficulty} • Time: ${formatTime(elapsedSeconds())} • Hints used: ${state.hintsUsed}`;
        modal.classList.remove("hidden");
        nameInput.focus();
    }

    // ---------- Timer ----------
    function startTimer() {
        stopTimer();
        state.startTime = Date.now();
        timerEl.textContent = "0:00";
        state.timerId = setInterval(() => {
            timerEl.textContent = formatTime(elapsedSeconds());
        }, 1000);
    }

    function stopTimer() {
        if (state.timerId) clearInterval(state.timerId);
        state.timerId = null;
    }

    function elapsedSeconds() {
        return Math.floor((Date.now() - state.startTime) / 1000);
    }

    function formatTime(sec) {
        const m = Math.floor(sec / 60);
        const s = sec % 60;
        return `${m}:${s.toString().padStart(2, "0")}`;
    }

    // ---------- Server calls ----------
    async function newGame() {
        const difficulty = $("#difficulty").value;
        const res = await fetch("/api/new_game", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ difficulty }),
        });
        const data = await res.json();
        state.puzzle = data.puzzle;
        state.solution = data.solution;
        state.current = data.puzzle.map((row) => row.slice());
        state.locked = data.puzzle.map((row) => row.map((v) => v !== 0));
        state.difficulty = data.difficulty;
        state.hintsUsed = 0;
        state.finished = false;
        renderBoard();
        startTimer();
    }

    async function checkBoard() {
        const res = await fetch("/api/check", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ board: state.current }),
        });
        const data = await res.json();
        // Clear then highlight both live conflicts and cells that differ from the solution.
        boardEl.querySelectorAll("input.conflict").forEach((i) => i.classList.remove("conflict"));
        data.conflicts.forEach(([r, c]) => getInput(r, c).classList.add("conflict"));
        for (let r = 0; r < 9; r++) {
            for (let c = 0; c < 9; c++) {
                const v = state.current[r][c];
                if (v !== 0 && v !== state.solution[r][c]) getInput(r, c).classList.add("conflict");
            }
        }
        maybeWin();
    }

    async function useHint() {
        if (state.finished) return;
        const res = await fetch("/api/hint", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ board: state.current, solution: state.solution }),
        });
        const { row, col, value } = await res.json();
        if (row === null) return;
        state.current[row][col] = value;
        state.locked[row][col] = true;
        state.hintsUsed += 1;
        const inp = getInput(row, col);
        inp.value = value;
        inp.readOnly = true;
        inp.classList.add("hint", "locked");
        liveValidate();
        maybeWin();
    }

    // ---------- Scoreboard (localStorage) ----------
    function loadScores() {
        try {
            return JSON.parse(localStorage.getItem(STORAGE_KEY)) || [];
        } catch {
            return [];
        }
    }

    function saveScores(scores) {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(scores));
    }

    function addScore(entry) {
        const scores = loadScores();
        scores.push(entry);
        scores.sort((a, b) => a.seconds - b.seconds);
        saveScores(scores.slice(0, MAX_SCORES));
    }

    function renderScores() {
        const scores = loadScores();
        scoresBody.innerHTML = "";
        scores.forEach((s, i) => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td>${i + 1}</td>
                <td>${escapeHtml(s.name)}</td>
                <td>${formatTime(s.seconds)}</td>
                <td>${escapeHtml(s.difficulty)}</td>
                <td>${s.hints}</td>
            `;
            scoresBody.appendChild(tr);
        });
    }

    function escapeHtml(s) {
        return String(s).replace(/[&<>"']/g, (ch) => ({
            "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
        }[ch]));
    }

    // ---------- Dark mode ----------
    function initTheme() {
        const saved = localStorage.getItem("sudoku_theme") || "light";
        document.documentElement.setAttribute("data-theme", saved);
        $("#theme-toggle").textContent = saved === "dark" ? "☀️" : "🌙";
    }

    function toggleTheme() {
        const cur = document.documentElement.getAttribute("data-theme");
        const next = cur === "dark" ? "light" : "dark";
        document.documentElement.setAttribute("data-theme", next);
        localStorage.setItem("sudoku_theme", next);
        $("#theme-toggle").textContent = next === "dark" ? "☀️" : "🌙";
    }

    // ---------- Wire up ----------
    $("#new-game").addEventListener("click", newGame);
    $("#check").addEventListener("click", checkBoard);
    $("#hint").addEventListener("click", useHint);
    $("#theme-toggle").addEventListener("click", toggleTheme);
    $("#save-score").addEventListener("click", () => {
        const name = (nameInput.value || "Anonymous").trim().slice(0, 20);
        addScore({
            name,
            seconds: elapsedSeconds(),
            difficulty: state.difficulty,
            hints: state.hintsUsed,
        });
        renderScores();
        modal.classList.add("hidden");
    });
    $("#close-modal").addEventListener("click", () => modal.classList.add("hidden"));

    // ---------- Boot ----------
    initTheme();
    renderScores();
    newGame();
})();
