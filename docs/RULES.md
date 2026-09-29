# Project Rules for Contributors and Coding Agents

**Last reviewed:** 2026-09-29

These rules capture the current project decisions. Update them when the owner changes scope or the implementation changes.

## Scope and claims

1. Treat packaged-food label analysis as the product: label photo or barcode/name, nutrition extraction/retrieval, transparent score, and general warnings.
2. Do not add patient-specific, disease-specific, diagnostic, or treatment behavior to the current flow. Do not imply a product is medically safe or suitable.
3. Treat CNN food recognition and Random Forest health recommendation code as experimental/deferred. Do not make them required setup steps or advertise them as available without trained artifacts and an explicit scope decision.
4. Do not claim broad Indian-product or multilingual accuracy from synthetic fixtures. State the dataset and evaluation type beside every performance claim.

## Nutrition data and scoring

5. Preserve units and normalize source data before scoring. Keep internal names consistent with `scoring.py`: `sugar_g`, `sat_fat_g`, `sodium_mg`, `protein_g`, `fibre_g`, and `nova`.
6. Missing values must remain missing (`None`/absent) and appear in the score's `missing` list. Never replace missing with zero.
7. Keep scoring deterministic and return the criterion breakdown with the aggregate. If changing weights, bands, or grade boundaries, update tests and document the rationale and source.
8. Existing scoring/alert thresholds are provisional editorial values. Do not describe them as official FSSAI, WHO, Codex, Nutri-Score, or other standards until each value has a precise authoritative citation and a documented mapping.
9. Salt-to-sodium conversion currently uses sodium = salt / 2.5 by mass. Preserve the unit conversion and add a regression check if changing it.
10. Product source data can be incomplete or wrong. Keep source/provenance information where available and avoid wording that turns an upstream value into a verified fact.

## OCR, ingredients, and alerts

11. OCR is extraction, not ground truth. Do not suppress missing fields or invent values when text is ambiguous.
12. Keep image analysis focused on nutrition-label images. Clearly handle unreadable/invalid images and ensure temporary upload files are removed on success and failure.
13. Allergen matches are keyword-based hints from label/source text. Keep alerts phrased as detected/matched content; do not promise that the product is allergen-free.
14. Preference warnings are simple threshold comparisons. Keep them general and avoid medical language.

## Architecture and interfaces

15. The Python FastAPI application is the active implementation. The React/Express/MongoDB stack is a separate legacy prototype; do not silently treat it as the Python client.
16. Python and JavaScript scoring implementations differ. If integrating them, establish one canonical rubric/API contract and update both sides or remove the duplicate.
17. Preserve existing endpoint names and response fields unless making an intentional documented API change. Prefer structured, consistent error responses and HTTP statuses when evolving the API.
18. Keep training datasets, credentials, local environments, generated model weights, and user uploads out of version control unless project policy explicitly allows them.

## Change hygiene

19. Update `docs/ARCHITECTURE.md`, `docs/PRD.md`, `docs/TASKS.md`, and `PROJECT_STATUS.md` when implementation or project scope materially changes.
20. Record validation accurately. Distinguish checked-in synthetic tests, local manual checks, and live external-service checks.
21. Do not add dependencies or new data collection without documenting why they are needed and the setup impact.
