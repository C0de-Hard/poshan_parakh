"""Input Path 1: Open Food Facts barcode lookup (no API key, CC0/ODbL data)."""
import time

import requests

URL = "https://world.openfoodfacts.org/api/v2/product/{code}.json"
HEADERS = {"User-Agent": "PoshanParakh-NSUT-BTP/0.1 (student project)"}

def _get_json(url: str, *, params: dict | None = None, timeout: float = 10, attempts: int = 3) -> dict | None:
    """Fetch JSON while tolerating short-lived upstream failures."""
    for attempt in range(attempts):
        try:
            response = requests.get(url, params=params, headers=HEADERS, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except (requests.RequestException, ValueError):
            if attempt < attempts - 1:
                time.sleep(0.25 * (attempt + 1))
    return None

def lookup_barcode(code: str, timeout: float = 10) -> dict | None:
    """Return normalised nutrition dict, or None if the product is missing / API unreachable."""
    data = _get_json(URL.format(code=code), timeout=timeout)
    if data is None:
        return None
    if data.get("status") != 1:
        return None
    return normalise(data["product"])

def normalise(p: dict) -> dict:
    n = p.get("nutriments", {})
    sodium_g = n.get("sodium_100g")
    if sodium_g is None and n.get("salt_100g") is not None:
        sodium_g = n["salt_100g"] / 2.5             # salt g -> sodium g
    return {
        "name": p.get("product_name"), "brand": p.get("brands"),
        "sugar_g": n.get("sugars_100g"), "sat_fat_g": n.get("saturated-fat_100g"),
        "protein_g": n.get("proteins_100g"), "fibre_g": n.get("fiber_100g"),
        "sodium_mg": sodium_g * 1000 if sodium_g is not None else None,
        "energy_kcal": n.get("energy-kcal_100g"),
        "nova": p.get("nova_group"), "allergens": p.get("allergens_tags", []),
        "nutriscore": p.get("nutriscore_grade"), "ingredients_text": p.get("ingredients_text"),
        "source": "openfoodfacts",
    }


SEARCH_URL = "https://world.openfoodfacts.org/cgi/search.pl"

def search_name(query: str, limit: int = 5, timeout: float = 10) -> list[dict]:
    """Input Path 1 (product name): first `limit` OFF matches, normalised. [] if none / unreachable."""
    params = {"search_terms": query, "search_simple": 1, "action": "process", "json": 1, "page_size": limit}
    data = _get_json(SEARCH_URL, params=params, timeout=timeout)
    if data is None:
        return []
    products = data.get("products", [])
    return [normalise(p) | {"barcode": p.get("code")} for p in products[:limit]]
