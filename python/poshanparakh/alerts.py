"""Health / allergy alerts: compares a product with the user's dietary preferences and allergies.

Thresholds are per 100 g and follow the UK traffic-light 'high' bands (sugar >22.5 g, sat. fat >5 g,
sodium >600 mg ~ 1.5 g salt). TODO for final report: cite FSSAI / WHO values for these.
"""

PREFERENCE_RULES = {
    # preference -> (nutrient key, limit, message)
    "low_sodium": ("sodium_mg", 300, "High sodium for a low-sodium diet"),
    "low_sugar":  ("sugar_g", 5, "High sugar for a low-sugar diet"),
    "low_fat":    ("sat_fat_g", 1.5, "High saturated fat for a low-fat diet"),
    "high_protein": ("protein_g", 12, None),   # inverse rule, handled below
}
TRAFFIC_HIGH = {"sugar_g": 22.5, "sat_fat_g": 5, "sodium_mg": 600}
LABEL = {"sugar_g": "sugar", "sat_fat_g": "saturated fat", "sodium_mg": "sodium"}
UNIT = {"sugar_g": "g", "sat_fat_g": "g", "sodium_mg": "mg"}

def generate_alerts(nutrition: dict, allergens_found: list[str] | None = None, profile: dict | None = None) -> list[dict]:
    """Returns [{'level': 'warning'|'info', 'type': ..., 'message': ...}]. Deterministic."""
    profile = profile or {}
    alerts = []
    for key, limit in TRAFFIC_HIGH.items():
        v = nutrition.get(key)
        if v is not None and v > limit:
            alerts.append({"level": "warning", "type": "nutrient",
                           "message": f"High {LABEL[key]}: {v:g} {UNIT[key]}/100g (above {limit:g})"})
    for pref in profile.get("dietary_preferences", []):
        rule = PREFERENCE_RULES.get(pref)
        if not rule:
            continue
        key, limit, msg = rule
        v = nutrition.get(key)
        if v is None:
            continue
        if pref == "high_protein":
            if v < limit:
                alerts.append({"level": "info", "type": "preference",
                               "message": f"Low protein ({v:g} g/100g) for a high-protein preference"})
        elif v > limit:
            alerts.append({"level": "warning", "type": "preference", "message": f"{msg}: {v:g} {UNIT[key]}/100g"})
    user_allergies = {a.lower() for a in profile.get("allergies", [])}
    for a in sorted(user_allergies & {x.lower() for x in (allergens_found or [])}):
        alerts.append({"level": "warning", "type": "allergen", "message": f"Contains {a}: matches your allergy list"})
    return alerts
