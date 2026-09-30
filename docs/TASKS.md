# Project Tasks and Roadmap

**Status reviewed:** 2026-09-29
Checkboxes reflect repository evidence at that date. This is a current-state handoff, not a commitment to a schedule.

## Current implementation

- [x] Python FastAPI app with `/analyze`, `/barcode/{code}`, and `/search` endpoints.
- [x] Label image preprocessing and Tesseract OCR extraction for a defined English nutrient vocabulary.
- [x] Ingredient parsing and keyword allergen detection for label OCR output.
- [x] Deterministic six-criterion nutrition scoring, grade bands, breakdown, and missing-field reporting.
- [x] General nutrient and optional preference/allergen warning logic.
- [x] Open Food Facts client with bounded retries and salt-to-sodium normalization.
- [x] Synthetic label fixtures and ground truth; recorded result 39/40 = 97.5% on those fixtures.
- [x] Older React/Vite/Express/MongoDB prototype and barcode camera scanner exist as a separate stack.
- [x] Vercel frontend barcode/name lookup is connected to the deployed Python API through a response adapter and CORS allowlist.
- [x] Vercel frontend supports packet-image upload to FastAPI `/analyze` and displays the extracted score breakdown.
- [x] Setup and known state are described in root `README.md` and `PROJECT_STATUS.md`.

## Priority 1: validate the current product behavior

- [ ] Collect 5–10 real packaged-food labels representative of the intended Indian product scope, with permission to retain images.
- [ ] Annotate ground truth manually for nutrition values, units, ingredients, and declared allergens; document ambiguous labels.
- [ ] Measure per-field OCR precision/recall or exact-match accuracy on the real set, separately from synthetic results.
- [ ] Test English and representative mixed-language labels; document unsupported scripts and failure cases.
- [ ] Run Open Food Facts barcode and name lookups against live service when available; record timestamp, queries, result coverage, and failures.
- [ ] Verify salt/sodium and energy unit conversion against explicit examples from source data and labels.

## Priority 2: make scoring and warning rationale defensible

- [ ] Select authoritative sources for each score criterion and warning threshold (for example applicable FSSAI materials, WHO guidance, Codex references, or a clearly named public scoring standard).
- [ ] Record exact source, jurisdiction, per-100-g basis, category applicability, and conversion rationale for each threshold.
- [ ] Review whether positive nutrients and processing group belong in the same composite and whether current weights/bands communicate the intended meaning.
- [ ] Add tests for each band boundary, each missing-field combination, and unit conversion after the rubric is finalized.
- [ ] Add an informational disclaimer in product/API presentation that reflects the rubric's evidence and limits.

## Priority 3: define and build the active user interface

- [x] Decide to adapt the existing UI for Python barcode/name lookup; document the remaining label-upload gap.
- [ ] Add label upload and show extracted fields, ingredients, warnings, missing values, and source.
- [ ] Add clear nutrition score explanation and provisional-status treatment until thresholds are sourced.
- [ ] Consider editable OCR values or a correction path before calculating the final score.
- [ ] Add preference/allergy inputs only with clear labels and non-medical wording.
- [ ] Review responsive layout, keyboard navigation, screen-reader labels, camera errors, and loading/empty states.

## Priority 4: improve service contracts and robustness

- [ ] Use consistent HTTP status codes and structured error schemas for not found, upstream unavailable, invalid image, and unsupported upload.
- [ ] Enforce upload content type and size limits; handle corrupt images predictably.
- [ ] Add per-field extraction provenance/confidence if it can be measured and explained reliably.
- [ ] Add explicit API contract documentation/examples and keep client types aligned.
- [ ] Decide whether to remove or isolate dormant `/classify` and `/recommend` routes and the legacy `recommendation` response field.
- [ ] Add operational configuration for upstream timeouts, endpoint base URL, and service deployment only when deployment target is selected.

## Deferred pending an explicit scope decision

- [ ] Personalized health profiles or disease-specific advice.
- [ ] Random Forest recommender dataset preparation, model training, and validation.
- [ ] Generic food-photo CNN dataset/model training.
- [ ] Persistent user scan history and accounts.

These are not prerequisites for the current packaged-food label analyser. Do not start them as routine cleanup.
