# Product and Interface Design

**Last reviewed:** 2026-09-29

## Current design status

The implemented React/Vite client under `frontend/` presents a packaged-product lookup experience, barcode camera scanner, and packet-image upload control. Its barcode/name and upload paths call the deployed Python FastAPI service through `frontend/src/lib/api.js`.

## Existing interface structure

1. **Masthead:** “Product Nutrition Scanner” heading and short explanation of barcode/name lookup.
2. **Lookup panel:** Barcode and product-name tabs; text input; lookup action.
3. **Barcode camera flow:** Camera start/stop controls, video preview with scan frame, permission/error message, and sample barcode hints. Camera scanning requires browser camera access and a secure context such as localhost or HTTPS.
4. **Result dossier:** Product name, live/cached source tag, brand/barcode, ingredient text, overall score and verdict, then criterion rows with raw values and colored score bars.
5. **Error state:** Inline message when API lookup fails.

## Visual system in the prototype

- Off-white/green-tinted paper background with a light panel and thin muted borders.
- Dark blue-green primary text and controls.
- Serif display headings paired with system sans-serif and monospace numeric values.
- Muted green, amber, and brick red tones indicate high, middle, and low score bands.
- Content uses a centered, narrow column with compact rows and minimal decoration.

The page styling is intentionally simple and information-oriented. CSS includes font-family declarations but no font download is configured, so browser/system fallback is expected unless those fonts are installed.

## Existing scanner interaction

- Selecting “Use camera” requests a video stream through `@zxing/browser`.
- A decoded barcode fills the input, stops the scanner, and immediately submits a barcode lookup.
- “Stop camera” stops ZXing controls; unmount also stops controls.
- A startup error is shown beside the scanner controls.
- Typing a barcode or product name and pressing Enter or the lookup button submits manually.

## Current interface limitations

- No editable extracted values, OCR confidence display, or correction workflow.
- No dietary preference/allergy controls in the UI even though the Python alert layer accepts these values.
- The result card uses a small client adapter to render Python barcode/name and image-analysis responses; detailed warning cards and field-level provenance are still not shown.
- It does not expose score rubric citations, missing criteria rationale, provenance at the individual nutrient level, or an explicit informational-only note.
- The score is presented as a single positive/negative verdict despite placeholder thresholds; future design should clearly explain its provisional status.
- Keyboard focus, scanner accessibility, responsive behavior, and error presentation have not been formally audited.

## Design direction for the next active client

The next client should connect directly to the Python analysis contract or to a deliberately defined adapter. It should make source and uncertainty visible, support both barcode/name lookup and label upload, and show each available nutrient beside its unit and scoring contribution. Missing fields should be shown as unavailable. General nutrition/allergen warnings should be separate from the score and phrased as informational signals. Include an explanation that score bands are provisional until authoritative thresholds are selected.

Do not design disease recommendations or imply medical suitability within the current scope.
