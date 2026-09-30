import json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from poshanparakh.ocr_parser import parse_image, parse_nutrition
from poshanparakh.scoring import score_product
from poshanparakh.alerts import generate_alerts
from poshanparakh.ocr_parser import parse_ingredients, detect_allergens, normalize_per_100g, serving_size_g
from poshanparakh import recommender, pipeline
from poshanparakh import off_client

def test_parser_units():
    assert parse_nutrition("Energy 1000 kJ")["energy_kcal"] == 239.0
    assert parse_nutrition("Sodium 0.5 g")["sodium_mg"] == 500.0
    assert parse_nutrition("Protein 7,5 g")["protein_g"] == 7.5
    assert parse_nutrition("Total Carbohydrates 25.1 g\nof which Sugar (Sucrose) 9.0 g")["sugar_g"] == 9.0
    assert serving_size_g("Typical Value for 30 g") == 30
    assert normalize_per_100g({"sugar_g": 9.0, "sodium_mg": 100}, 30) == {"sugar_g": 30.0, "sodium_mg": 333.33}

def test_scoring_deterministic_and_adds_up():
    p = {"sugar_g": 10, "sat_fat_g": 3, "sodium_mg": 300, "protein_g": 8, "fibre_g": 4, "nova": 3}
    a, b = score_product(p), score_product(p)
    assert a == b
    assert round(sum(r["points"] for r in a["breakdown"])) == a["score"]   # all 6 criteria present -> max 100
    assert score_product({"sugar_g": 1, "sat_fat_g": 0.5, "sodium_mg": 50, "protein_g": 20, "fibre_g": 8, "nova": 1})["score"] == 100
    assert score_product({"sugar_g": 50, "sat_fat_g": 20, "sodium_mg": 3000, "protein_g": 0, "fibre_g": 0, "nova": 4})["score"] == 0

def test_missing_rescaled():
    r = score_product({"sugar_g": 1})
    assert r["score"] == 100 and len(r["missing"]) == 5

def test_ingredients_and_allergens():
    t = "INGREDIENTS: Wheat flour, Sugar, Palm oil, Milk solids.\n\nNutrition Information\nEnergy 450 kcal"
    assert parse_ingredients(t) == ["wheat flour", "sugar", "palm oil", "milk solids"]
    assert detect_allergens(t) == ["gluten", "milk"]

def test_alerts():
    a = generate_alerts({"sodium_mg": 900, "sugar_g": 3}, ["milk"],
                        {"dietary_preferences": ["low_sodium"], "allergies": ["Milk"]})
    types = [x["type"] for x in a]
    assert "allergen" in types and types.count("nutrient") == 1 and "preference" in types
    assert generate_alerts({"sodium_mg": 100, "sugar_g": 1}, [], {}) == []

def test_off_client_retries_and_normalises_salt():
    import requests
    from unittest.mock import patch

    class Response:
        def __init__(self, status_code, payload):
            self.status_code = status_code
            self.payload = payload

        def raise_for_status(self):
            if self.status_code >= 400:
                raise requests.HTTPError(response=self)

        def json(self):
            return self.payload

    payload = {"status": 1, "product": {"nutriments": {"salt_100g": 1.25}}}
    responses = [Response(503, {}), Response(200, payload)]
    with patch.object(off_client.requests, "get", side_effect=responses) as get, \
            patch.object(off_client.time, "sleep"):
        product = off_client.lookup_barcode("8901234567890", timeout=0.01)
    assert get.call_count == 2
    assert product["sodium_mg"] == 500.0

def test_recommender_roundtrip(tmp_path_str=None):
    """Code-path test on a TINY SYNTHETIC table (not the Kaggle data, so no accuracy claim is made)."""
    import tempfile, joblib, pandas as pd, sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from train_recommender import train
    df = pd.DataFrame({"age": [25, 40, 55, 30, 62, 45, 28, 50] * 5,
                       "condition": ["none", "diabetes", "hypertension", "none", "hypertension", "diabetes", "none", "diabetes"] * 5,
                       "diet": ["low_sugar" if c == "diabetes" else "low_sodium" if c == "hypertension" else "balanced"
                                for c in ["none", "diabetes", "hypertension", "none", "hypertension", "diabetes", "none", "diabetes"] * 5]})
    bundle, acc = train(df, "diet")
    path = os.path.join(tempfile.mkdtemp(), "rec.joblib"); joblib.dump(bundle, path)
    r = recommender.recommend({"age": 41, "condition": "diabetes"}, save_history=False, path=path)
    assert r["label"] == "low_sugar"
    r2 = recommender.recommend({"age": None, "condition": "never-seen"}, save_history=False, path=path)   # missing + unseen values don't crash
    assert "label" in r2
    assert "error" in recommender.recommend({"age": 1}, save_history=False, path="/nonexistent.joblib")

def test_pipeline_label_image_offline():
    here = os.path.dirname(__file__)
    res = pipeline.analyze_image(os.path.join(here, "label_1.png"), {"dietary_preferences": ["low_sugar"], "allergies": []})
    assert res["nutrition_analysis"]["score"] is not None
    assert set(["nutrition_analysis", "health_alerts", "recommendation"]) <= set(res)
    assert any("sugar" in a["message"].lower() for a in res["health_alerts"])      # label_1 has 34 g sugar

if __name__ == "__main__":
    test_parser_units(); test_scoring_deterministic_and_adds_up(); test_missing_rescaled()
    test_ingredients_and_allergens(); test_alerts(); test_recommender_roundtrip(); test_pipeline_label_image_offline()
    test_off_client_retries_and_normalises_salt()
    print("unit tests passed")
    truth = json.load(open(os.path.join(os.path.dirname(__file__), "ground_truth.json")))
    ok = tot = 0
    for i, t in enumerate(truth, 1):
        got = parse_image(os.path.join(os.path.dirname(__file__), f"label_{i}.png"))
        hit = sum(1 for k, v in t.items() if k in got and abs(got[k] - v) < 0.01)
        print(f"label_{i}: {hit}/{len(t)} fields correct", {k: (got.get(k), v) for k, v in t.items() if got.get(k) != v})
        ok += hit; tot += len(t)
    print(f"OCR field accuracy: {ok}/{tot} = {100*ok/tot:.1f}%  (roadmap target >= 80%)")
