# Project Memory

**Last reviewed:** 2026-09-29

Compact handoff facts for future work. `PROJECT_STATUS.md` remains the detailed chronological/current validation record; this file records durable decisions and facts.

## Identity and active direction

- Project name: PoshanParakh, an NSUT B.Tech BTP1 packaged-food label analyser.
- Active implementation: `python/` FastAPI service and `python/poshanparakh/` analysis package.
- `backend/` and `frontend/` are an older, separate Express/React/MongoDB prototype. The frontend calls Express at port 5000 and is not wired to FastAPI.
- Supported scope: nutrition-label photo or Open Food Facts barcode/name lookup, nutrition extraction/retrieval, deterministic score, and general nutrition/allergen warnings.
- Out of scope unless explicitly changed: patient-specific health advice, disease alerts, health profiles/recommender, and generic food-photo classification.

## Important implementation facts

- Python endpoints: `POST /analyze`, `GET /barcode/{code}`, `GET /search?q=...`. Experimental `/classify` and `/recommend` endpoints exist but lack trained model artifacts.
- Python score uses sugar, saturated fat, sodium, protein, fibre, and NOVA with weights 20/15/20/15/10/20. Missing criteria are excluded and the total is rescaled; all-missing gives null.
- OCR label photo does not currently infer NOVA. OCR uses OpenCV preprocessing, Tesseract, and regex/keyword parsing.
- Open Food Facts lookups can fail due to upstream/client environment availability. Salt is converted to sodium using salt / 2.5 where direct sodium is absent.
- Python and JavaScript prototype scoring rubrics differ. Do not compare their numeric scores as if they were the same model.
- Thresholds are provisional and need authoritative citation. Allergen detection is keyword-based and is not a guarantee of allergen absence.

## Validation facts

- Synthetic OCR fixtures: 39/40 fields = 97.5%; one recorded mismatch is saturated fat 1.0 vs ground truth 1.1 on label 5.
- This synthetic figure is not real-world product accuracy.
- The root status note records a past successful FastAPI startup and synthetic API check. Live Open Food Facts success was not established; prior calls got HTTP 503.
- Setup: install `python/requirements.txt`; native Tesseract binary is required. From `python/`, run `../.venv/bin/uvicorn app:app --reload` if that local environment exists.
- Synthetic test command documented in README/status: `cd python && ../.venv/bin/python tests/test_all.py`.

## Working conventions

- Preserve missing nutrition as missing; do not invent zero values.
- Describe source and uncertainty accurately. Keep medical and accuracy claims conservative.
- When changing implementation or scope, update root `README.md`, `PROJECT_STATUS.md`, and the relevant files in this directory.
- See `RULES.md` for contributor and coding-agent constraints, `TASKS.md` for outstanding work, and `ARCHITECTURE.md` for the component map.
