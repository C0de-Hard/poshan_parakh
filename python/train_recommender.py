"""Train the Random Forest diet recommender (Algorithm 3) on the Kaggle user-health CSV.

Usage:
  python train_recommender.py --csv path/to/health_data.csv --target <recommendation_column> \
         [--drop id,name] [--numeric age,weight,height]

Categorical columns are label-encoded; numeric columns are auto-detected (or set with --numeric).
Prints hold-out accuracy - use THIS number in the report, nothing else.
"""
import argparse, json, os
import joblib, pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

def train(df: pd.DataFrame, target: str, numeric: list[str] | None = None, seed: int = 42) -> tuple[dict, float]:
    df = df.dropna(subset=[target]).copy()
    features = [c for c in df.columns if c != target]
    if numeric is None:
        numeric = [c for c in features if pd.api.types.is_numeric_dtype(df[c])]
    encoders, cat_defaults, num_defaults = {}, {}, {}
    X = pd.DataFrame(index=df.index)
    for c in features:
        if c in numeric:
            num_defaults[c] = float(df[c].median())
            X[c] = df[c].fillna(num_defaults[c]).astype(float)
        else:
            col = df[c].fillna("unknown").astype(str)
            enc = LabelEncoder().fit(col)
            encoders[c] = enc
            cat_defaults[c] = int(enc.transform([col.mode()[0]])[0])
            X[c] = enc.transform(col)
    t_enc = LabelEncoder().fit(df[target].astype(str))
    y = t_enc.transform(df[target].astype(str))
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=seed, stratify=y if pd.Series(y).value_counts().min() > 1 else None)
    rf = RandomForestClassifier(n_estimators=300, random_state=seed, n_jobs=-1).fit(Xtr.values, ytr)
    acc = accuracy_score(yte, rf.predict(Xte.values))
    print(f"hold-out accuracy: {acc:.3f} on {len(yte)} rows")
    print(classification_report(yte, rf.predict(Xte.values), target_names=t_enc.classes_, zero_division=0))
    bundle = {"model": rf, "feature_encoders": encoders, "target_encoder": t_enc, "features": features,
              "numeric": numeric, "numeric_defaults": num_defaults, "categorical_defaults": cat_defaults,
              "holdout_accuracy": acc}
    return bundle, acc

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True); ap.add_argument("--target", required=True)
    ap.add_argument("--drop", default=""); ap.add_argument("--numeric", default=None)
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "models", "recommender.joblib"))
    a = ap.parse_args()
    df = pd.read_csv(a.csv)
    if a.drop:
        df = df.drop(columns=[c for c in a.drop.split(",") if c in df.columns])
    bundle, _ = train(df, a.target, a.numeric.split(",") if a.numeric else None)
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    joblib.dump(bundle, a.out)
    print("saved", a.out, "| features:", bundle["features"])
