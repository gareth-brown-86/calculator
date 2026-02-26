"""Streamlit UI for the calculator."""

from __future__ import annotations

import streamlit as st

from backend import EvaluationError, evaluate_expression


def _init_state() -> None:
    st.session_state.setdefault("expression", "")
    st.session_state.setdefault("result", None)
    st.session_state.setdefault("history", [])
    st.session_state.setdefault("error", "")


def _append_token(token: str) -> None:
    st.session_state.expression += token


def _clear() -> None:
    st.session_state.expression = ""
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
    _init_state()

    st.title("Calculator")
    st.caption("Basic arithmetic with a simple UI and safe evaluation.")

    st.text_input(
        "Expression",
        key="expression",
        placeholder="e.g., 12 / (3 + 1)",
    )

    action_cols = st.columns(2)
    if action_cols[0].button("Calculate", use_container_width=True):
        _calculate()
    if action_cols[1].button("Clear", use_container_width=True):
        _clear()

    if st.session_state.error:
        st.error(st.session_state.error)
    elif st.session_state.result is not None:
        st.success(f"Result: {st.session_state.result}")

    st.subheader("Keypad")
    keypad_rows = [
        ["7", "8", "9", "/"],
        ["4", "5", "6", "*"],
        ["1", "2", "3", "-"],
        ["0", ".", "+", "("],
        [")", "C", "="],
    ]

    for row in keypad_rows:
        cols = st.columns(len(row))
        for col, token in zip(cols, row):
            if col.button(token, use_container_width=True):
                if token == "C":
                    _clear()
                elif token == "=":
                    _calculate()
                else:
                    _append_token(token)

    st.subheader("History")
    if st.session_state.history:
        for item in st.session_state.history[:10]:
            st.write(item)
    else:
        st.caption("No calculations yet.")


if __name__ == "__main__":
    main()
