# Calculator

A Streamlit-based calculator with a simple UI and a safe Python backend.

## Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Tests

```bash
pytest
```

## Frontend Tests

```bash
pip install -r requirements.txt
python -m playwright install chromium
```

- Streamlit native widget tests:

```bash
pytest tests/test_streamlit_app.py -v
```

- Playwright rendered UI test:

```bash
pytest tests/test_playwright_ui.py -v
```

- Visual regression (first run creates baseline):

```bash
UPDATE_SNAPSHOTS=1 pytest tests/test_visual_regression.py -v
pytest tests/test_visual_regression.py -v
```
