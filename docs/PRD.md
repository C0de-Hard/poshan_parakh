# Product Requirements Document

**Product:** PoshanParakh
**Status:** Current prototype scope
**Last reviewed:** 2026-09-29

## 1. Product summary

PoshanParakh helps a person inspect a packaged food product using either a photo of its nutrition/ingredient label or a barcode/product name lookup. It extracts or retrieves product information, calculates a transparent deterministic nutrition score, and surfaces general nutrition and declared-allergen warnings.

This document describes the repository's implemented direction, not a claim of production readiness. The Python service is the active implementation. The React/Express/MongoDB application is an older, separate prototype and is not currently integrated with the Python API.

## 2. Problem and users

Packaged-food labels can be difficult to compare quickly. A user needs a compact view of nutrient values, how a score was calculated, ingredients that were found, and warnings that may matter when choosing a product.

Primary user: a person comparing packaged foods for general nutrition awareness. The prototype accepts preferences and allergy terms in parts of its API, but does not require an account or persist a user profile.

## 3. Goals

- Accept a nutrition-label image and extract supported nutrition fields, ingredients, and likely allergen groups.
- Accept a product barcode or name and retrieve product data from Open Food Facts when that service responds.
- Return the source product/nutrition data alongside a deterministic 0–100 score, grade, criterion breakdown, and missing-field list.
- Return general nutrient warnings and optional preference/allergen warnings with understandable messages.
- Make uncertainty visible: distinguish missing data from zero values and avoid presenting synthetic test performance as real-world accuracy.

## 4. Out of scope

- Medical advice, diagnosis, treatment, or claims of suitability for a medical condition.
- Disease-specific rules for diabetes, heart disease, hypertension, or other conditions.
- Health profiles, personalized recommendations, or use of a health dataset in the supported product flow.
- General food-photo recognition as a packaged-label analysis substitute.
- Claims that OCR works accurately across Indian products, scripts, or languages without a representative benchmark.
- A production identity, account, history, or cloud deployment system.

The repository contains experimental CNN and Random Forest code and dormant API routes for classification/recommendation. Their presence does not make those features part of the current product requirements.

## 5. Current user workflows

### A. Analyze a label photo

1. Client sends one image to `POST /analyze` as multipart field `file`.
2. Optional `prefs` and `allergies` form fields are comma-separated strings.
3. Service preprocesses the image, runs Tesseract OCR, parses recognized nutrition values, ingredients, and allergen keywords.
4. Service returns parsed product data, score and breakdown, missing criteria, and alerts.
5. NOVA/processing group is unavailable from the current image parser and is omitted from the score calculation.

### B. Look up a barcode

1. Client calls `GET /barcode/{code}`.
2. Service queries Open Food Facts, normalizes nutrients to the internal schema, and derives sodium from salt when direct sodium is absent.
3. Service returns the shared analysis structure or an error when the product is missing or upstream is unavailable.

### C. Search by product name

1. Client calls `GET /search?q={name}`.
2. Service returns analysis for the first Open Food Facts match and a compact list of additional matches.
3. If no matches are available, it returns a guidance error.

Optional preference values currently recognized by alert logic: `low_sodium`, `low_sugar`, `low_fat`, and `high_protein`. Allergy matching uses normalized allergen group names. These inputs only drive simple deterministic warnings; they are not medical personalization.

## 6. Output contract

Successful analysis currently includes:

- `product`: normalized source data (field availability depends on source).
- `ingredients`: parsed ingredient strings where available.
- `detected_allergens`: allergen group names detected or declared by the source.
- `nutrition_analysis`: `score` (nullable), `grade` (nullable), criterion `breakdown`, and `missing` criteria.
- `health_alerts`: list of `{level, type, message}` general warnings.
- `recommendation`: currently a skipped marker when no health profile was provided; this legacy-shaped field is not a supported recommendation feature.
- `other_matches`: name-search alternatives when present.

Errors are returned as an `error` string from pipeline functions. FastAPI's default handling determines HTTP status for uncaught validation/parsing failures; product-not-found errors are currently ordinary response dictionaries rather than explicit HTTP error responses.

## 7. Score behavior and interpretation

The Python scoring rubric uses six criteria: sugar (20 points), saturated fat (15), sodium (20), protein (15), fibre (10), and NOVA processing group (20). Lower sugar, saturated fat, sodium, and NOVA group contribute more points; higher protein and fibre contribute more. For available values, earned points are rescaled against the available maximum, so omitted criteria do not automatically count as zero. If no criteria are available, score and grade are null.

Grades: A ≥ 80, B ≥ 65, C ≥ 50, D ≥ 35, otherwise E. The current bands are editorial/placeholders and have not yet been replaced with a cited, validated regulatory or public-health standard. The score is an informational prototype metric, not an official rating or medical recommendation.

## 8. Quality and constraints

- Reproducible scoring for the same normalized input.
- Clearly report absent fields; never silently turn missing values into zero.
- Image processing depends on Python packages plus the native Tesseract executable.
- Barcode/name lookup depends on network access and Open Food Facts availability and coverage.
- OCR supports English keyword patterns in the current parser; photographed labels, language coverage, lighting, rotation, and layout affect extraction quality.
- The only recorded OCR accuracy is on five synthetic label fixtures: 39/40 fields (97.5%). It is not a real-product benchmark.

## 9. Acceptance criteria for the current prototype

- `POST /analyze` accepts an image and yields parsed fields and deterministic score output for supported label content.
- `/barcode/{code}` and `/search?q=...` normalize source results and gracefully return a useful error when no product is available.
- Nutrient conversion preserves units, including kJ to kcal and salt to sodium conversion where used.
- Missing score fields are enumerated and available criteria are rescaled consistently.
- Alerts are traceable to recognized general thresholds, preferences, or matching allergen groups.
- Documentation states limitations and does not overclaim synthetic evaluation.

## 10. Open product decisions

- Select and cite authoritative sources for nutrient score and warning thresholds.
- Decide the desired image size/type limits and whether a label upload UI belongs in the active client.
- Define representative real-label evaluation set, languages, annotation method, and field-level metrics.
- Decide whether a future frontend should call the Python API directly and retire or replace the old prototype.
