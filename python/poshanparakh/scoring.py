"""Transparent 0-100 score. Fixed rules, no randomness: same input -> same score.

Each criterion has a max of points; points always sum to 100 in total.
Thresholds follow the Nutri-Score / UK traffic-light style per-100g bands.
(Team should cite FSSAI / Codex values for the final report.)
"""
from dataclasses import dataclass

# (label, key, max_points, direction, bands) ; bands = [(upper_limit, fraction_of_max_points)]
CRITERIA = [
    ("Sugar (g/100g)", "sugar_g", 20, "lower", [(5, 1.0), (15, 0.6), (22.5, 0.3), (float("inf"), 0.0)]),
    ("Saturated fat (g/100g)", "sat_fat_g", 15, "lower", [(1.5, 1.0), (5, 0.6), (10, 0.3), (float("inf"), 0.0)]),
    ("Sodium (mg/100g)", "sodium_mg", 20, "lower", [(120, 1.0), (600, 0.6), (1200, 0.3), (float("inf"), 0.0)]),
    ("Protein (g/100g)", "protein_g", 15, "higher", [(2, 0.0), (6, 0.4), (12, 0.8), (float("inf"), 1.0)]),
    ("Fibre (g/100g)", "fibre_g", 10, "higher", [(1, 0.0), (3, 0.5), (6, 0.8), (float("inf"), 1.0)]),
    ("Processing (NOVA 1-4)", "nova", 20, "lower", [(1, 1.0), (2, 0.75), (3, 0.4), (4, 0.0)]),
]

def grade(score: int) -> str:
    return "A" if score >= 80 else "B" if score >= 65 else "C" if score >= 50 else "D" if score >= 35 else "E"

def score_product(nutrition: dict) -> dict:
    """nutrition: keys sugar_g, sat_fat_g, sodium_mg, protein_g, fibre_g, nova (any may be missing).
    Missing criteria are dropped and the total is rescaled to 100, and listed in 'missing'."""
    rows, earned, possible, missing = [], 0.0, 0, []
    for label, key, max_pts, direction, bands in CRITERIA:
        v = nutrition.get(key)
        if v is None:
            missing.append(label)
            continue
        frac = next(f for limit, f in bands if v <= limit)
        pts = round(max_pts * frac, 1)
        earned += pts
        possible += max_pts
        rows.append({"criterion": label, "value": v, "points": pts, "max_points": max_pts})
    total = round(100 * earned / possible) if possible else None
    return {"score": total, "grade": grade(total) if total is not None else None,
            "breakdown": rows, "missing": missing}
