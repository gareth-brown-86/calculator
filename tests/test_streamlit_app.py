"""Streamlit AppTest-based widget tests (no browser required)."""

from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest

_APP_PATH = str(Path(__file__).resolve().parents[1] / "app.py")


def _click_button(app: AppTest, label: str) -> AppTest:
    """Find a button by its display label, click it, and return the re-run app."""
    for button in app.button:
        if button.label == label:
            button.click()
            return app.run()
    raise AssertionError(f"Button '{label}' not found")


def test_streamlit_app_renders() -> None:
    app = AppTest.from_file(_APP_PATH).run()
    assert app.title[0].value == "Calculator"


def test_streamlit_keypad_calculation() -> None:
    app = AppTest.from_file(_APP_PATH).run()
    for label in ("8", "/", "2", "="):
        app = _click_button(app, label)
    assert app.session_state["result"] == 4


def test_enter_key_triggers_calculation() -> None:
    """Typing an expression and pressing Enter (submitting text_input) should compute."""
    app = AppTest.from_file(_APP_PATH).run()
    # Simulate typing into the text input and pressing Enter
    app.text_input(key="_expr_input").set_value("10+5").run()
    assert app.session_state["result"] == 15
    assert app.session_state["expression"] == "10+5"
