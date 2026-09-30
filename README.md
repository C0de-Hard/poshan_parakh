# PoshanParakh - Packaged Food Label Analyser

## Current Scope

This project analyzes packaged food products using a nutrition-label photo or a product barcode/name.

```text
Label photo or barcode/name
  -> nutrition and ingredient extraction
  -> allergen detection
  -> transparent nutrition score
  -> general product warnings
```

The current version does **not** collect user health parameters and does **not** provide patient-specific diabetic, heart-disease, hypertension, or other medical alerts.

The following are explicitly deferred and must not be treated as current requirements:

- Health profiles and personalized recommendations
- Random Forest health recommender training
- Disease-specific alerts
- Generic food-photo CNN classification

## Main Implementation

The active implementation is under `python/`:

- `app.py` - FastAPI service
- `poshanparakh/ocr_parser.py` - OpenCV and Tesseract label OCR/parsing
- `poshanparakh/scoring.py` - deterministic 0-100 nutrition score
- `poshanparakh/alerts.py` - general product nutrition and allergy warnings
- `poshanparakh/off_client.py` - Open Food Facts barcode/name lookup
- `poshanparakh/pipeline.py` - combined analysis response
- `tests/` - synthetic OCR and scoring tests

The `backend/` folder is an older Express/MongoDB prototype. The `frontend/` folder is the deployed React/Vite client for barcode/name lookup and packet-image upload; the Python FastAPI service remains the primary analysis implementation.

## Setup

From the project root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r python/requirements.txt
```

The OCR pipeline also requires the native Tesseract binary:

```bash
brew install tesseract
```

Run the tests:

```bash
cd python
../.venv/bin/python tests/test_all.py
```

Start the API:

```bash
cd python
../.venv/bin/uvicorn app:app --reload
```

Open the API documentation at:

http://127.0.0.1:8000/docs

## Current Validation

- Unit tests pass.
- Synthetic OCR accuracy is `39/40 = 97.5%`.
- The synthetic result is not real-world Indian-product accuracy.
- The `/analyze` label-image route works with the supplied synthetic fixtures.
- Open Food Facts calls require further reliable online testing because the Python client received HTTP 503 responses during validation.

## Remaining Work

1. Collect 5-10 real Indian packaged-food labels and create manually verified ground truth.
2. Measure OCR accuracy on those real labels.
3. Cite authoritative FSSAI/WHO/Codex sources for score thresholds.
4. Improve the packaged-product frontend/UI around the new barcode camera flow.
5. Test English and mixed-language Indian labels and document limitations.

The React client includes a browser barcode scanner through `@zxing/browser` and packet-image upload. It requires camera permission and a secure browser context such as `localhost` or HTTPS. Set `VITE_API_URL` only when using a different FastAPI deployment; otherwise it defaults to the current Render service.

See `PROJECT_STATUS.md` for the detailed handoff and current state.
