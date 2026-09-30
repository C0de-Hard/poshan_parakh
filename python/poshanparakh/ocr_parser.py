"""Algorithm 2: Tesseract OCR + regex parser for the nutrition-facts table."""
import re
import cv2
import numpy as np
import pytesseract

def preprocess(img_bgr: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    if gray.shape[1] < 1200:                       # upscale small images: OCR likes ~300 dpi
        s = 1200 / gray.shape[1]
        gray = cv2.resize(gray, None, fx=s, fy=s, interpolation=cv2.INTER_CUBIC)
    gray = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(gray)   # contrast
    return cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

def ocr_text(img_bgr: np.ndarray) -> str:
    return pytesseract.image_to_string(preprocess(img_bgr), config="--psm 6")

NUM = r"([\dOol]+(?:[.,][\dOol]+)?)"   # also accept letters OCR confuses with digits
# field -> (regex, unit-in-label handled by convert())
PATTERNS = {
    "energy_kcal": rf"(?:energy|calories)[^\d\n]{{0,15}}{NUM}\s*(kcal|cal|kj)?",
    "protein_g":   rf"protein[^\d\n]{{0,10}}{NUM}\s*(g|mg)?",
    "fat_g":       rf"total\s*fat[^\d\n]{{0,10}}{NUM}\s*(g|mg)?",
    "sat_fat_g":   rf"(?:saturated\s*fat|sat\.?\s*fat)[^\d\n]{{0,10}}{NUM}\s*(g|mg)?",
    "carbs_g":     rf"(?:total\s*)?carbohydrate[s]?[^\d\n]{{0,10}}{NUM}\s*(g|mg)?",
    "sugar_g":     rf"(?:total\s*)?(?:sugar[s]?|sucrose)[^\d\n]{{0,25}}{NUM}\s*(g|mg)?",
    "fibre_g":     rf"(?:dietary\s*)?fi(?:b|be)re?[^\d\n]{{0,10}}{NUM}\s*(g|mg)?",
    "sodium_mg":   rf"sodium[^\d\n]{{0,10}}{NUM}\s*(mg|g)?",
}

def parse_nutrition(text: str) -> dict:
    out = {}
    low = text.lower().replace("|", " ")   # lower() turns O->o, l stays l, both handled by NUM
    for key, pat in PATTERNS.items():
        m = re.search(pat, low)
        if not m:
            continue
        tok = m.group(1).translate(str.maketrans("Ool", "001")).replace(",", ".")
        unit = (m.group(2) or "").lower()
        if not unit and key not in ("energy_kcal", "sodium_mg") and tok.endswith("9") and len(tok) > 1:
            tok = tok[:-1].rstrip(".")     # OCR often reads the unit 'g' as '9' (e.g. "6.29" is "6.2 g")
        val = float(tok)
        if key == "energy_kcal" and unit == "kj":
            val = round(val / 4.184, 1)
        if key == "sodium_mg" and unit == "g":
            val *= 1000
        if key != "sodium_mg" and key != "energy_kcal" and unit == "mg":
            val /= 1000
        out[key] = val
    return out

def parse_image(path: str) -> dict:
    img = cv2.imread(path)
    if img is None:
        raise ValueError(f"cannot read image: {path}")
    return parse_nutrition(ocr_text(img))


# ---------------------------------------------------------------------------
# Ingredient / allergen extraction (feeds the health & allergy alerts)
# ---------------------------------------------------------------------------
ALLERGEN_KEYWORDS = {
    "milk":      ["milk", "whey", "casein", "butter", "cream", "cheese", "lactose", "ghee", "curd"],
    "gluten":    ["wheat", "gluten", "barley", "rye", "maida", "semolina", "suji", "oats"],
    "peanut":    ["peanut", "groundnut"],
    "tree_nut":  ["almond", "cashew", "walnut", "hazelnut", "pistachio", "tree nut"],
    "soy":       ["soy", "soya", "lecithin (soy"],
    "egg":       ["egg", "albumen"],
    "fish":      ["fish", "anchovy"],
    "shellfish": ["shrimp", "prawn", "crab", "lobster", "shellfish"],
    "sesame":    ["sesame", "til "],
}

def parse_ingredients(text: str) -> list[str]:
    """Return the comma-separated ingredient list that follows an 'Ingredients' heading (may be empty)."""
    m = re.search(r"ingredients?\s*[:\-]?\s*(.+?)(?:\n\s*\n|nutrition|contains\b|allergen|$)", text, re.I | re.S)
    if not m:
        return []
    raw = re.sub(r"\s+", " ", m.group(1)).strip(" .")
    return [p.strip().lower() for p in re.split(r"[,;]", raw) if p.strip()]

def detect_allergens(text: str) -> list[str]:
    """Keyword match on the whole OCR text (ingredients + 'contains' statement). Returns allergen group names."""
    low = " " + text.lower() + " "
    return sorted(g for g, words in ALLERGEN_KEYWORDS.items() if any(w in low for w in words))

def parse_image_full(path: str) -> dict:
    """Nutrition values + ingredients + allergens from one label photo."""
    img = cv2.imread(path)
    if img is None:
        raise ValueError(f"cannot read image: {path}")
    text = ocr_text(img)
    return {"nutrition": parse_nutrition(text), "ingredients": parse_ingredients(text),
            "allergens": detect_allergens(text), "raw_text": text}
