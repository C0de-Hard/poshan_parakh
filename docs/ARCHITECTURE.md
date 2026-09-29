# Architecture

**Last reviewed:** 2026-09-29

## System boundary

The repository contains two generations of implementation. The supported project direction is the Python/FastAPI service under `python/`. The React/Vite client under `frontend/` now calls the Python barcode/name endpoints through a small response adapter. The Express/MongoDB service under `backend/` remains a separate legacy prototype.

```text
Current analysis service
  label image ──> FastAPI /analyze ──> OpenCV/Tesseract ──> parser ─┐
  barcode ──────> FastAPI /barcode ──> Open Food Facts ─────────────┤
  product name ─> FastAPI /search ───> Open Food Facts ──────────────┘
                                                  shared normalization
                                                   ├─ scoring
                                                   ├─ general alerts
                                                   └─ JSON analysis

Connected lookup client
  React/Vite ──> Python /barcode or /search ──> Open Food Facts
       └─ response adapter ──> existing score dossier

Legacy prototype (separate runtime)
  React/Vite ──> Express routes ──> Open Food Facts
                       ├─ MongoDB product cache (optional)
                       └─ parallel JavaScript scoring rubric
```

## Python service modules

- `python/app.py`: FastAPI app, request parsing, temporary upload storage, and endpoint definitions.
- `python/poshanparakh/pipeline.py`: orchestration for image, barcode, and name flows; assembles normalized response fields.
- `python/poshanparakh/ocr_parser.py`: OpenCV grayscale/upscale/CLAHE/Otsu preprocessing; Tesseract `--psm 6`; regex extraction, ingredient splitting, and keyword allergen detection.
- `python/poshanparakh/off_client.py`: HTTP client for Open Food Facts, bounded retries, normalization, and salt-to-sodium conversion.
- `python/poshanparakh/scoring.py`: deterministic six-criterion point model and A–E grade mapping.
- `python/poshanparakh/alerts.py`: general high-nutrient, dietary-preference, and allergen warnings.
- `python/poshanparakh/food_classifier.py`, `recommender.py`, `train_cnn.py`, and `train_recommender.py`: experimental/deferred paths. Model artifacts and suitable real datasets are not present in the repository.

## Python request paths

| Endpoint | Input | Processing | Result |
| --- | --- | --- | --- |
| `GET /barcode/{code}` | Barcode; optional `prefs`, `allergies` query values | Open Food Facts lookup and normalization, then shared analysis | Analysis object or pipeline error object |
| `GET /search?q=...` | Product name; optional `prefs`, `allergies` | Search up to five results, analyze first, expose remaining match summaries | Analysis object or pipeline error object |
| `POST /analyze` | Multipart `file`; optional `prefs`, `allergies` fields | Temporary file, OCR and parse, shared analysis, temporary-file deletion in `finally` | Analysis object |
| `POST /classify` | Multipart `file` | Experimental image CNN inference | Error until model weights/classes exist |
| `POST /recommend` | JSON `health_profile` | Experimental Random Forest inference | Error until recommender artifact exists |

The last two endpoints are documented for repository transparency, not current product scope. The app currently imports the recommender at module import time, so installed package compatibility still matters even though no trained model is checked in.

## Internal data flow and normalization

The score/alert layer expects keys `sugar_g`, `sat_fat_g`, `sodium_mg`, `protein_g`, `fibre_g`, and `nova`. OCR yields most nutrients but not NOVA. Open Food Facts values are converted from per-100-g nutrient fields; sodium is read directly where available or estimated from `salt_100g / 2.5`, then represented as mg. External data is not independently verified.

The pipeline returns a common shape for all three supported product-analysis inputs. Barcode/name results can contain product identity and declared allergens; image results contain extracted nutrition, ingredient strings, and keyword-detected allergen groups. Ingredient parsing from external data currently splits on commas, which may not preserve nested/composite ingredient structure.

## Web clients and legacy prototype

- `frontend/src/`: React UI, barcode camera scanner (`@zxing/browser`), name/barcode lookup form, score dossier, and Python response adapter.
- `frontend/src/lib/api.js`: uses `VITE_API_URL` when supplied, otherwise the deployed Render URL; maps Python `nutrition_analysis` fields into the existing dossier shape.
- `backend/server.js`: Express API on port 5000 by default; attempts MongoDB connection.
- `backend/routes/products.js` and `backend/controllers/productController.js`: Open Food Facts lookup and optional Mongo cache.
- `backend/lib/scoring.js`: separate JavaScript rubric and response breakdown. Its criteria/bands differ from the Python scoring model; results must not be treated as equivalent.
- `backend/routes/scores.js` and `ScoreRecord.js`: scan-history persistence endpoints, not called by the frontend.

The frontend barcode/name flow is now wired to the Python service. Label-image upload is still not exposed in the frontend, and the Express/MongoDB prototype remains independently deployable rather than part of the active path.

## Persistence, external dependencies, and configuration

- Python analysis does not persist uploaded images or scan results. Upload temp files are deleted after `/analyze` and `/classify` calls complete, including exceptions.
- Open Food Facts is the external data source; lookup depends on upstream connectivity and record completeness.
- Python OCR requires Tesseract installed at OS level. Install Python dependencies from `python/requirements.txt`.
- Legacy backend optionally depends on MongoDB via `backend/config/db.js` and environment configuration; its product cache is best-effort.
- `.gitignore` excludes `.venv`, `node_modules`, `.env`, Python caches, and build output. Do not commit credentials or model/data artifacts without an explicit data policy.

## Known architectural risks

1. Python and JavaScript score rubrics are different; the frontend does not currently present Python results.
2. FastAPI endpoints do not consistently translate pipeline error dictionaries into HTTP error status codes.
3. Input image size/content validation and OCR execution limits are not explicitly enforced in `app.py`.
4. Open Food Facts data and service availability are outside local control; retry logic is bounded but live success is not guaranteed.
5. OCR keyword/regex extraction can miss values or match unintended text; no confidence or provenance is returned per field.
6. The `recommendation` field and experimental routes preserve older work and can confuse API consumers about supported scope.
