"""Streamlit UI for the calculator."""

from __future__ import annotations

import streamlit as st

from backend import EvaluationError, evaluate_expression

# (display_label, token) per cell; None = empty slot.
_KEYPAD: list[list[tuple[str, str] | None]] = [
    [("7", "7"), ("8", "8"), ("9", "9"), ("/", "/")],
    [("4", "4"), ("5", "5"), ("6", "6"), ("×", "*")],
    [("1", "1"), ("2", "2"), ("3", "3"), ("−", "-")],
    [("0", "0"), (".", "."), ("(", "("), (")", ")")],
    [("C", "C"), ("=", "="), ("＋", "+"), None],
]


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
        value=st.session_state.expression,
        placeholder="e.g., 12 / (3 + 1)",
        disabled=True,
    )

    action_cols = st.columns(2)
    action_cols[0].button("Calculate", use_container_width=True, on_click=_calculate)
    action_cols[1].button("Clear", use_container_width=True, on_click=_clear)

    if st.session_state.error:
        st.error(st.session_state.error)
    elif st.session_state.result is not None:
        st.success(f"Result: {st.session_state.result}")

    st.subheader("Keypad")
    for row in _KEYPAD:
        cols = st.columns(len(row))
        for col, cell in zip(cols, row):
            if cell is None:
                continue
            label, token = cell
            if token == "C":
                col.button(label, use_container_width=True, on_click=_clear)
            elif token == "=":
                col.button(label, use_container_width=True, on_click=_calculate)
            else:
                col.button(
                    label,
                    use_container_width=True,
                    on_click=_append_token,
                    args=(token,),
                )

    st.subheader("History")
    if st.session_state.history:
        for item in st.session_state.history[:10]:
            st.write(item)
    else:
        st.caption("No calculations yet.")


if __name__ == "__main__":
    main()
