"""Playwright end-to-end tests for the calculator UI."""

from __future__ import annotations

import time

import pytest
from playwright.sync_api import Page, sync_playwright


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _wait_for_expression(page: Page, expected: str, timeout_ms: int = 3000) -> float:
    """Poll the Expression input until it shows *expected*; return elapsed seconds."""
    expression_input = page.get_by_label("Expression")
    start = time.monotonic()
    deadline = start + timeout_ms / 1000
    while time.monotonic() < deadline:
        if expression_input.input_value() == expected:
            return time.monotonic() - start
        page.wait_for_timeout(50)
    raise AssertionError(
        f"Expression did not become '{expected}' within {timeout_ms}ms "
        f"(got '{expression_input.input_value()}')"
    )


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def page(streamlit_url: str):
    """Launch a Chromium page pointed at the running Streamlit app."""
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        _page = browser.new_page()
        _page.set_default_timeout(10_000)
        _page.goto(streamlit_url, wait_until="domcontentloaded")
        _page.wait_for_timeout(1500)
        yield _page
        browser.close()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_playwright_keypad_flow(page: Page) -> None:
    page.get_by_role("button", name="8").click()
    _wait_for_expression(page, "8")

    page.get_by_role("button", name="/").click()
    _wait_for_expression(page, "8/")

    page.get_by_role("button", name="2").click()
    _wait_for_expression(page, "8/2")

    page.get_by_role("button", name="=").click()
    page.wait_for_timeout(500)


def test_playwright_keypad_latency(page: Page) -> None:
    """Each keypad press should update the expression within 2 seconds."""
    max_latency = 2.0

    tokens = [("3", "3"), (".", "3."), ("9", "3.9")]
    for button_name, expected_expr in tokens:
        page.get_by_role("button", name=button_name).click()
        latency = _wait_for_expression(page, expected_expr)
        assert (
            latency < max_latency
        ), f"Pressing '{button_name}' took {latency:.2f}s (limit {max_latency}s)"
