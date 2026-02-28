// Calculator – client-side logic.
// Handles keypad clicks, keyboard input, and API calls.

(function () {
    "use strict";

    const exprInput = document.getElementById("expression");
    const resultBar = document.getElementById("result-bar");
    const historyList = document.getElementById("history-list");

    const history = [];

    // ── Keypad button handler ─────────────────────────────────────────────

    document.querySelector(".keypad").addEventListener("click", (e) => {
        const btn = e.target.closest("button");
        if (!btn) return;

        const token = btn.dataset.token;
        const action = btn.dataset.action;

        if (token) {
            appendToken(token);
        } else if (action === "clear") {
            clearAll();
        } else if (action === "backspace") {
            backspace();
        } else if (action === "equals") {
            calculate();
        }

        // Keep focus on the input so keyboard always works
        exprInput.focus();
    });

    // ── Keyboard handler ──────────────────────────────────────────────────

    // Let the input field handle normal typing. We only need to intercept
    // Enter (to evaluate) and Escape (to clear).
    exprInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter") {
            e.preventDefault();
            calculate();
        } else if (e.key === "Escape") {
            e.preventDefault();
            clearAll();
        }
    });

    // Global key listener: if the user presses a calculator key while focus
    // is NOT on the input, redirect it there.
    document.addEventListener("keydown", (e) => {
        // Don't interfere if user is already in the input
        if (document.activeElement === exprInput) return;

        const allowed = /^[0-9+\-*/().=]$/;
        if (allowed.test(e.key)) {
            e.preventDefault();
            exprInput.focus();
            if (e.key === "=") {
                calculate();
            } else {
                appendToken(e.key);
            }
        } else if (e.key === "Enter") {
            e.preventDefault();
            exprInput.focus();
            calculate();
        } else if (e.key === "Escape") {
            e.preventDefault();
            exprInput.focus();
            clearAll();
        } else if (e.key === "Backspace") {
            e.preventDefault();
            exprInput.focus();
            backspace();
        }
    });

    // ── Core actions ──────────────────────────────────────────────────────

    function appendToken(token) {
        const start = exprInput.selectionStart;
        const end = exprInput.selectionEnd;
        const val = exprInput.value;
        exprInput.value = val.slice(0, start) + token + val.slice(end);
        const newPos = start + token.length;
        exprInput.setSelectionRange(newPos, newPos);
    }

    function backspace() {
        const start = exprInput.selectionStart;
        const end = exprInput.selectionEnd;
        const val = exprInput.value;
        if (start !== end) {
            exprInput.value = val.slice(0, start) + val.slice(end);
            exprInput.setSelectionRange(start, start);
        } else if (start > 0) {
            exprInput.value = val.slice(0, start - 1) + val.slice(start);
            exprInput.setSelectionRange(start - 1, start - 1);
        }
    }

    function clearAll() {
        exprInput.value = "";
        resultBar.innerHTML = "";
    }

    async function calculate() {
        const expr = exprInput.value.trim();
        if (!expr) return;

        try {
            const res = await fetch("/api/evaluate", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ expression: expr }),
            });
            const data = await res.json();

            if (data.error) {
                resultBar.innerHTML = `<span class="error">${escapeHtml(data.error)}</span>`;
            } else {
                resultBar.innerHTML = `<span class="value">= ${escapeHtml(data.result)}</span>`;
                addHistory(expr, data.result);
            }
        } catch {
            resultBar.innerHTML = `<span class="error">Network error.</span>`;
        }
    }

    // ── History ───────────────────────────────────────────────────────────

    function addHistory(expr, result) {
        history.unshift({ expr, result });
        if (history.length > 10) history.pop();
        renderHistory();
    }

    function renderHistory() {
        if (history.length === 0) {
            historyList.innerHTML = `<p class="history-empty">No calculations yet.</p>`;
            return;
        }
        historyList.innerHTML = history
            .map(
                (h) =>
                    `<div class="history-entry">
                        <span class="history-expr">${escapeHtml(h.expr)} = ${escapeHtml(h.result)}</span>
                        <button class="history-load" data-expr="${escapeAttr(h.expr)}" title="Load expression">↩</button>
                    </div>`
            )
            .join("");
    }

    historyList.addEventListener("click", (e) => {
        const btn = e.target.closest(".history-load");
        if (!btn) return;
        exprInput.value = btn.dataset.expr;
        resultBar.innerHTML = "";
        exprInput.focus();
        const len = exprInput.value.length;
        exprInput.setSelectionRange(len, len);
    });

    // ── Helpers ───────────────────────────────────────────────────────────

    function escapeHtml(s) {
        const div = document.createElement("div");
        div.textContent = s;
        return div.innerHTML;
    }

    function escapeAttr(s) {
        return s.replace(/&/g, "&amp;").replace(/"/g, "&quot;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
    }
})();
