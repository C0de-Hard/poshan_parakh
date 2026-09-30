# PoshanParakh - Project Status / Handoff

Updated: 30 Sep 2026

## Project

NSUT B.Tech BTP1 project for an AI-powered food label analyser.

The main implementation is the Python application under `python/`. The existing `backend/` and `frontend/` directories are an older React/Express/MongoDB prototype and were not extended or modified.

## Authoritative Current Scope

This project is a packaged-food label analyser. Its required workflow is:

```text
Nutrition-label photo or product barcode/name
  -> nutrition and ingredient extraction
  -> product nutrition score
  -> general product warnings
```

The current version does **not** collect or use user health parameters. It does **not** provide diabetic, heart-disease, hypertension, or other patient-specific alerts. It does **not** require the health CSV, Random Forest recommender, or generic food-photo CNN.

Treat the following as future or optional work only:

- User health profiles and personalized recommendations
- Disease-specific alerts
- Random Forest health recommender training
- Generic food-image classification

Any AI or developer working on this repository should preserve this packaged-food-only scope unless the project owner explicitly changes it.

## Current Layout

```text
food-rating-project/
├── python/
│   ├── app.py
│   ├── requirements.txt
│   ├── train_cnn.py
│   ├── train_recommender.py
│   ├── poshanparakh/
│   │   ├── alerts.py
│   │   ├── food_classifier.py
│   │   ├── ocr_parser.py
│   │   ├── off_client.py
│   │   ├── pipeline.py
│   │   ├── recommender.py
│   │   └── scoring.py
│   └── tests/
│       ├── ground_truth.json
│       ├── label_1.png ... label_5.png
│       ├── make_labels.py
│       └── test_all.py
├── backend/       Older Express prototype, unchanged
├── frontend/      Older React/Vite prototype, unchanged
├── .venv/         Local Python virtual environment
└── PROJECT_STATUS.md
```

## Work Completed

- Inspected both extracted folders that were previously inside `idkk`.
- Confirmed they were complementary rather than duplicates:
  - One contained the main Python application, API, training scripts, requirements, and test runner.
  - The other contained `scoring.py`, package initialization, and synthetic OCR test assets.
- Merged both trees into the root `python/` directory.
- Removed the temporary `idkk` folder after verifying the merged layout.
- Created `.venv` using Python 3.13.
- Installed all packages from `python/requirements.txt`, including FastAPI, OpenCV, Pillow, scikit-learn, PyTorch, and torchvision.
- Installed the native Tesseract OCR binary with Homebrew.
- Did not modify the application source code, the older web prototype, or the scoring logic.
- Started the FastAPI service successfully at `http://127.0.0.1:8000`.
- Verified the Swagger docs endpoint responds with HTTP 200.
- Added a browser barcode scanner to the older React frontend using `@zxing/browser`.
- Verified the frontend production build and browser scanner start/stop flow.
- Added bounded retries and HTTP-status validation to the Python Open Food Facts client, with regression coverage for transient failures and salt-to-sodium conversion.
- Connected the Vercel frontend to the Render FastAPI service for barcode/name lookup and packet-image upload, including a Python-response adapter and CORS allowlist.
- Added an upload control for packet label images and fixed the camera video element to autoplay with a visible preview area.
- Added serving-size detection and per-100-g normalization for labels such as `Typical Value for 30 g`, including multiline `Sugar (Sucrose)` extraction.
- Added optional pretrained MobileNetV3-Small visual context output; it is advisory only and does not replace OCR or provide nutrition values.

## Validation Completed

Command:

```bash
cd python
../.venv/bin/python tests/test_all.py
```

Result:

- Unit tests passed.
- Synthetic OCR accuracy: `39/40 = 97.5%`.
- The roadmap target of at least 80% was met.
- Recommender smoke test hold-out accuracy: `1.000` on 8 synthetic rows.
- One expected synthetic OCR difference remained: the parser read `sat_fat_g` as `1.0` while the ground truth is `1.1` on label 5.

Live API checks:

- `POST /analyze` passed with `python/tests/label_1.png`, `prefs=low_sugar`, and `allergies=milk`.
- The image analysis returned score `36`, grade `D`, and the expected high-sugar and high-saturated-fat alerts.
- `POST /classify` responds correctly with `food CNN not trained yet` because no model files exist.
- `POST /recommend` responds correctly with `recommender model not trained yet` because no model file exists.
- `GET /search?q=maggi` and the tested barcode route did not return a product through the Python client. Direct inspection showed HTTP 503 responses from Open Food Facts to Python `requests`; this is an external API/client-environment issue, not a local route crash.

FastAPI import check also passed:

```text
PoshanParakh API
```

## Remaining Work For Current Scope

- Collect 5-10 real Indian packaged-food label photos and manually record ground-truth nutrition values.
- Benchmark OCR field accuracy on those real labels. The existing `39/40 = 97.5%` result is synthetic only.
- Open Food Facts barcode and name lookup now retry short-lived failures, but still need a live validation when the upstream service is available. Do not claim these routes are working until a real response is captured.
- Replace placeholder scoring thresholds with cited FSSAI, WHO, Codex, or other authoritative sources.
- Improve the frontend/UI around packaged-product lookup, label upload, score breakdown, ingredients, and general warnings.
- Test representative Indian products with English and mixed-language labels and document coverage limits.

## Explicitly Deferred

- Health parameters and patient profiles
- Diabetic, heart-disease, hypertension, or other disease-specific alerts
- Health CSV selection and Random Forest recommender training
- Generic food-photo CNN training
- Claims that the system works on all or most Indian products without a real benchmark

The FastAPI service should be started with:

```bash
cd python
../.venv/bin/uvicorn app:app --reload
```

Then open `http://127.0.0.1:8000/docs`.

- The older React/Express prototype still requires its own Node servers if it is run separately. It is not the main PoshanParakh implementation.
