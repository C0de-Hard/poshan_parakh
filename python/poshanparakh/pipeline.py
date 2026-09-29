"""PoshanParakh pipeline. Both input paths end in the same scoring + alert modules and return one
structured JSON-serialisable dict with the three outputs from the report.
profile = {"dietary_preferences": ["low_sodium", ...], "allergies": ["milk", ...], "health_profile": {...RF features...}}
  nutrition_analysis, health_alerts, recommendation.
"""
from .alerts import generate_alerts
from .food_classifier import classify_food
from .ocr_parser import parse_image_full
from .off_client import lookup_barcode, search_name
from .recommender import recommend
from .scoring import score_product

def _clean_allergens(tags: list[str]) -> list[str]:
    return [t.split(":")[-1].replace("-", "_") for t in tags or []]

def _assemble(product: dict, allergens: list[str], profile: dict | None, ingredients: list[str] | None = None) -> dict:
    out = {
        "product": product,
        "ingredients": ingredients or [],
        "detected_allergens": allergens,
        "nutrition_analysis": score_product(product),          # score, grade, criterion-wise breakdown, missing
        "health_alerts": generate_alerts(product, allergens, profile),
    }
    hp = (profile or {}).get("health_profile")      # feature dict for the Random Forest (age, weight, ...)
    out["recommendation"] = recommend(hp) if hp else {"skipped": "no health_profile given"}
    return out

def analyze_barcode(code: str, profile: dict | None = None) -> dict:
    """Input Path 1: Open Food Facts lookup by barcode. Falls back to an error asking for a label photo."""
    prod = lookup_barcode(code)
    if prod is None:
        return {"error": "product not found or API unreachable; upload the label photo instead"}
    ing = [i.strip().lower() for i in (prod.get("ingredients_text") or "").split(",") if i.strip()]
    return _assemble(prod, _clean_allergens(prod.get("allergens")), profile, ing)

def analyze_name(query: str, profile: dict | None = None) -> dict:
    """Input Path 1 (name): analyse the best OFF match and list the alternatives."""
    hits = search_name(query)
    if not hits:
        return {"error": "no product found; try a barcode or upload the label photo"}
    best = hits[0]
    ing = [i.strip().lower() for i in (best.get("ingredients_text") or "").split(",") if i.strip()]
    res = _assemble(best, _clean_allergens(best.get("allergens")), profile, ing)
    res["other_matches"] = [{"name": h["name"], "brand": h["brand"], "barcode": h.get("barcode")} for h in hits[1:]]
    return res

def analyze_image(path: str, profile: dict | None = None) -> dict:
    """Input Path 2: label photo -> OCR -> parsing -> shared scoring. NOVA is unknown from a photo."""
    parsed = parse_image_full(path)
    nutrition = parsed["nutrition"] | {"source": "ocr"}
    return _assemble(nutrition, parsed["allergens"], profile, parsed["ingredients"])

def analyze_food_photo(path: str) -> dict:
    """Algorithm 1: what food is in this photo (CNN)."""
    return classify_food(path)
