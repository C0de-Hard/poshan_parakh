"""Algorithm 3: Random Forest diet recommendation (inference side).

Training is done by train_recommender.py, which saves models/recommender.joblib containing:
  {"model", "feature_encoders" (dict col->LabelEncoder), "target_encoder", "features" (ordered list),
   "numeric" (list of numeric cols), "recommendation_text" (optional dict label->text)}
"""
import csv, datetime, os
import joblib
import numpy as np

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "recommender.joblib")
HISTORY_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "recommendation_history.csv")

_bundles: dict = {}

def load(path: str = MODEL_PATH) -> dict | None:
    """Step 2-3: load trained model + encoders. Returns None if not trained yet."""
    if path not in _bundles:
        if not os.path.exists(path):
            return None
        _bundles[path] = joblib.load(path)
    return _bundles[path]

def _encode_row(profile: dict, b: dict) -> list[float]:
    """Steps 4-5: encode categorical + numeric inputs; missing/unseen values fall back to a safe default."""
    row = []
    for col in b["features"]:
        v = profile.get(col)
        if col in b["numeric"]:
            try:
                row.append(float(v))
            except (TypeError, ValueError):
                row.append(b["numeric_defaults"].get(col, 0.0))      # missing -> training median
        else:
            enc = b["feature_encoders"][col]
            classes = list(enc.classes_)
            sv = str(v) if v is not None else None
            if sv in classes:
                row.append(float(enc.transform([sv])[0]))
            else:                                                     # missing/unseen -> most common class
                row.append(float(b["categorical_defaults"].get(col, 0)))
    return row

def recommend(profile: dict, save_history: bool = True, path: str = MODEL_PATH) -> dict:
    """Steps 6-9. Returns {'label', 'text', 'confidence'} or {'error': ...} if the model is not trained."""
    b = load(path)
    if b is None:
        return {"error": "recommender model not trained yet - run python/train_recommender.py"}
    x = np.array([_encode_row(profile, b)])
    proba = b["model"].predict_proba(x)[0]
    idx = int(np.argmax(proba))
    label = str(b["target_encoder"].inverse_transform([b["model"].classes_[idx]])[0])
    text = b.get("recommendation_text", {}).get(label, label)
    result = {"label": label, "text": text, "confidence": round(float(proba[idx]), 3)}
    if save_history:
        _append_history(profile, result)
    return result

def _append_history(profile: dict, result: dict, history_path: str = HISTORY_PATH) -> None:
    new = not os.path.exists(history_path)
    os.makedirs(os.path.dirname(history_path), exist_ok=True)
    with open(history_path, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["timestamp", "profile", "label", "confidence"])
        w.writerow([datetime.datetime.now().isoformat(timespec="seconds"), profile, result["label"], result["confidence"]])
