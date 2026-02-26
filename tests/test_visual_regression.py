"""Visual regression test – compares a screenshot against a stored baseline."""

from __future__ import annotations

import os
from pathlib import Path

import pytest
from PIL import Image, ImageChops
from playwright.sync_api import sync_playwright

_BASELINE_DIR = Path(__file__).resolve().parent / "visual_baseline"
_OUTPUT_DIR = Path(__file__).resolve().parent / "visual_output"


def _diff_ratio(actual_path: Path, baseline_path: Path) -> float:
    """Return 0.0–1.0 indicating how much two images differ."""
    with Image.open(actual_path) as actual, Image.open(baseline_path) as baseline:
        if actual.size != baseline.size:
            return 1.0
        diff = ImageChops.difference(actual, baseline)
        histogram = diff.histogram()
        changed = sum(value * (idx % 256) for idx, value in enumerate(histogram))
        total = actual.size[0] * actual.size[1] * 255 * len(actual.getbands())
        return changed / total if total else 0.0


def test_visual_regression_calculator_home(streamlit_url: str) -> None:
    _BASELINE_DIR.mkdir(parents=True, exist_ok=True)
    _OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    baseline_path = _BASELINE_DIR / "calculator_home.png"
    output_path = _OUTPUT_DIR / "calculator_home.png"

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 900})
        page.set_default_timeout(10_000)
        page.goto(streamlit_url, wait_until="domcontentloaded")
        page.get_by_text("Calculator").first.wait_for(timeout=10_000)
        page.screenshot(path=str(output_path), full_page=True)
        browser.close()

    if not baseline_path.exists() or os.getenv("UPDATE_SNAPSHOTS") == "1":
        output_path.replace(baseline_path)
        pytest.skip(
            "Baseline snapshot created/updated. Re-run without UPDATE_SNAPSHOTS."
        )

    ratio = _diff_ratio(output_path, baseline_path)
    assert ratio <= 0.01, f"Visual regression too large: {ratio:.4f} > 0.01"
