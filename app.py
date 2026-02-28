"""Streamlit UI for the calculator."""

from __future__ import annotations

import html as html_mod

import streamlit as st
import streamlit.components.v1 as components

from backend import EvaluationError, evaluate_expression

# Keypad layout: (display_label, token) per cell.
_KEYPAD: list[list[tuple[str, str]]] = [
    [("C", "C"), ("⌫", "⌫"), ("(", "("), (")", ")")],
    [("7", "7"), ("8", "8"), ("9", "9"), ("/", "/")],
    [("4", "4"), ("5", "5"), ("6", "6"), ("×", "*")],
    [("1", "1"), ("2", "2"), ("3", "3"), ("−", "-")],
    [("0", "0"), (".", "."), ("＋", "+"), ("=", "=")],
]

_CSS = """\
<style>
/* ═══════════════════════════════════════════════
   Calculator – Visual Theme (Phase 5, revised)
   Catppuccin Mocha-inspired palette
   ═══════════════════════════════════════════════ */

/* ── Page background ── */
.stApp { background: #181825 !important; }
/* Hide Streamlit's deploy button & hamburger */
header[data-testid="stHeader"] { background: transparent !important; }

/* ── Calculator "device" card (block-container as card) ── */
section.main > div.block-container {
    max-width: 26rem;
    padding: 1.5rem 1.25rem 1.5rem;
    background: #1e1e2e;
    border-radius: 20px;
    box-shadow:
        0 8px 32px rgba(0, 0, 0, 0.45),
        0 2px 8px rgba(0, 0, 0, 0.25);
}

/* ── Title ── */
h1 {
    font-size: 1.5rem !important;
    font-weight: 700 !important;
    letter-spacing: -0.02em;
    margin-bottom: 0.75rem !important;
    margin-top: 0 !important;
}

/* ── Expression input (the "screen") ── */
div[data-testid="stTextInput"] {
    margin-bottom: 0 !important;
}
div[data-testid="stTextInput"] input {
    background: #11111b !important;
    color: #cdd6f4 !important;
    font-family: 'SF Mono', 'Fira Code', 'Consolas', monospace !important;
    font-size: 1.6rem !important;
    text-align: right !important;
    border: 2px solid #313244 !important;
    border-radius: 14px 14px 0 0 !important;
    padding: 0.9rem 1rem !important;
    -webkit-text-fill-color: #cdd6f4 !important;
    caret-color: #89b4fa !important;
}
div[data-testid="stTextInput"] input::placeholder {
    color: #585b70 !important;
    -webkit-text-fill-color: #585b70 !important;
}
div[data-testid="stTextInput"] input:focus {
    border-color: #89b4fa !important;
    box-shadow: 0 0 0 1px #89b4fa !important;
}
/* Hide label (kept for a11y) */
div[data-testid="stTextInput"] label { display: none !important; }
/* Hide 'Press Enter to apply' helper */
div[data-testid="stTextInput"] div[data-testid="InputInstructions"] { display: none !important; }

/* ── Result bar ── */
.calc-result-bar {
    background: #11111b;
    border-radius: 0 0 14px 14px;
    border: 2px solid #313244;
    border-top: none;
    padding: 0.2rem 1rem 0.6rem;
    margin-top: 0;
    margin-bottom: 0.75rem;
    height: 2.8rem;
    overflow: hidden;
    text-align: right;
    font-family: 'SF Mono', 'Fira Code', 'Consolas', monospace;
}
.calc-result-bar .value { font-size: 1.7rem; font-weight: 700; color: #a6e3a1; }
.calc-result-bar .error { font-size: 0.95rem; color: #f38ba8; }

/* ── Keypad: tighten vertical spacing between rows ── */
div[data-testid="stVerticalBlock"] { gap: 0.4rem !important; }
div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlockSeparator"] {
    display: none !important;
}

/* ── Keypad: tighten horizontal gap between buttons ── */
div[data-testid="stHorizontalBlock"] { gap: 0.45rem !important; }

/* ── Keypad buttons (shared) ── */
div.stButton > button {
    height: 3.4rem;
    border-radius: 12px;
    font-size: 1.25rem;
    font-weight: 600;
    border: none !important;
    transition: transform 0.06s ease, filter 0.06s ease;
    width: 100%;
}
div.stButton > button:hover  { filter: brightness(1.15); }
div.stButton > button:active { transform: scale(0.94); }

/* ── Number buttons (default secondary) ── */
div.stButton > button[kind="secondary"] {
    background: #313244 !important;
    color: #cdd6f4 !important;
}

/* ── Operator buttons: target by aria-label ── */
div.stButton > button[aria-label="×"],
div.stButton > button[aria-label="/"],
div.stButton > button[aria-label="−"],
div.stButton > button[aria-label="＋"],
div.stButton > button[aria-label="("],
div.stButton > button[aria-label=")"],
div.stButton > button[aria-label="."] {
    background: #45475a !important;
    color: #f9e2af !important;
}

/* ── Utility buttons: C and backspace ── */
div.stButton > button[aria-label="C"],
div.stButton > button[aria-label="⌫"] {
    background: #45475a !important;
    color: #f38ba8 !important;
}

/* ── Equals (primary) ── */
div.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #89b4fa, #74c7ec) !important;
    color: #1e1e2e !important;
    font-size: 1.35rem;
}

/* ── History expander ── */
div[data-testid="stExpander"] {
    border: 1px solid #313244 !important;
    border-radius: 14px !important;
    overflow: hidden;
    margin-top: 0.25rem;
}
div[data-testid="stExpander"] summary {
    font-size: 0.9rem;
    font-weight: 600;
    color: #6c7086;
}
.history-entry {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.4rem 0;
    border-bottom: 1px solid #313244;
    font-family: 'SF Mono', 'Fira Code', 'Consolas', monospace;
    font-size: 0.82rem;
    color: #6c7086;
}
.history-expr {
    flex: 1;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

/* ═══════════════════════════════════════════════
   Responsive – small screens
   ═══════════════════════════════════════════════ */
@media (max-width: 480px) {
    section.main > div.block-container {
        max-width: 100%;
        padding: 0.75rem 0.75rem 1.25rem;
    }
    div[data-testid="stTextInput"] input {
        font-size: 1.3rem !important;
        padding: 0.65rem 0.75rem !important;
    }
    .calc-result-bar .value { font-size: 1.4rem; }
    div.stButton > button {
        height: 3rem;
        font-size: 1.1rem;
        border-radius: 10px;
    }
    h1 { font-size: 1.25rem !important; }
}
</style>
"""


def _init_state() -> None:
    st.session_state.setdefault("expression", "")
    st.session_state.setdefault("_expr_input", "")
    st.session_state.setdefault("result", None)
    st.session_state.setdefault("history", [])
    st.session_state.setdefault("error", "")


def _set_expr(value: str) -> None:
    """Set expression in both canonical state and the widget key."""
    st.session_state.expression = value
    st.session_state._expr_input = value


def _sync_expression() -> None:
    """Sync the text-input widget value and auto-calculate (Enter key)."""
    st.session_state.expression = st.session_state._expr_input
    if st.session_state.expression.strip():
        _calculate()


def _append_token(token: str) -> None:
    _set_expr(st.session_state.expression + token)


def _backspace() -> None:
    _set_expr(st.session_state.expression[:-1])


def _clear() -> None:
    _set_expr("")
    st.session_state.result = None
    st.session_state.error = ""


def _load_expression(expr: str) -> None:
    """Load a previous expression from history."""
    _set_expr(expr)
    st.session_state.result = None
    st.session_state.error = ""


def _calculate() -> None:
    try:
        result = evaluate_expression(st.session_state.expression)
        st.session_state.result = result
        st.session_state.history.insert(0, f"{st.session_state.expression} = {result}")
        st.session_state.error = ""
    except EvaluationError as exc:
        st.session_state.result = None
        st.session_state.error = str(exc)


def main() -> None:
    st.set_page_config(page_title="Calculator", page_icon="🧮")
    st.markdown(_CSS, unsafe_allow_html=True)
    _init_state()

    st.title("Calculator")

    # ── Display ──────────────────────────────────────────────
    st.text_input(
        "Expression",
        placeholder="Type or tap…",
        key="_expr_input",
        on_change=_sync_expression,
        label_visibility="collapsed",
    )

    if st.session_state.error:
        result_html = (
            f'<span class="error">{html_mod.escape(st.session_state.error)}</span>'
        )
    elif st.session_state.result is not None:
        result_html = f'<span class="value">= {st.session_state.result}</span>'
    else:
        result_html = ""
    st.markdown(
        f'<div class="calc-result-bar">{result_html}</div>',
        unsafe_allow_html=True,
    )

    # ── Keypad ───────────────────────────────────────────────
    for row in _KEYPAD:
        cols = st.columns(len(row))
        for col, (label, token) in zip(cols, row):
            with col:
                if token == "C":
                    st.button(label, use_container_width=True, on_click=_clear)
                elif token == "⌫":
                    st.button(label, use_container_width=True, on_click=_backspace)
                elif token == "=":
                    st.button(
                        label,
                        use_container_width=True,
                        on_click=_calculate,
                        type="primary",
                    )
                else:
                    st.button(
                        label,
                        use_container_width=True,
                        on_click=_append_token,
                        args=(token,),
                    )

    # ── History ──────────────────────────────────────────────
    with st.expander("History", expanded=False):
        if st.session_state.history:
            for idx, item in enumerate(st.session_state.history[:10]):
                # Extract expression part (before " = ")
                expr_part = item.split(" = ", 1)[0] if " = " in item else item
                hist_cols = st.columns([5, 1])
                hist_cols[0].markdown(
                    f'<div class="history-entry">'
                    f'<span class="history-expr">{html_mod.escape(item)}</span>'
                    f"</div>",
                    unsafe_allow_html=True,
                )
                hist_cols[1].button(
                    "↩",
                    key=f"hist_{idx}",
                    use_container_width=True,
                    on_click=_load_expression,
                    args=(expr_part,),
                    help="Load this expression",
                )
        else:
            st.caption("No calculations yet.")

    # ── Auto-focus the expression input so keyboard works without clicking ──
    components.html(
        """
        <script>
        const input = window.parent.document.querySelector(
            'div[data-testid="stTextInput"] input'
        );
        if (input) {
            input.focus();
            // Place cursor at end of current value
            const len = input.value.length;
            input.setSelectionRange(len, len);
        }
        </script>
        """,
        height=0,
    )


if __name__ == "__main__":
    main()
