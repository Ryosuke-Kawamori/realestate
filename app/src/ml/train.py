from __future__ import annotations
import os, joblib
import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import Session
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.linear_model import Ridge
from sklearn.metrics import r2_score, mean_absolute_error
from ..db import SessionLocal
from ..models import Listing
from .features import make_features, FEATURE_COLS_CAT

MODEL_PATH = "/app/model/model.joblib"
MODEL_VERSION = "ridge_v1"

def load_training_df(session: Session) -> pd.DataFrame:
    q = session.query(Listing)
    rows = q.all()
    data = []
    for r in rows:
        data.append({
            "price_yen": r.price_yen,
            "area_m2": r.area_m2,
            "age_years": r.age_years,
            "station_walk_min": r.station_walk_min,
            "prefecture": r.prefecture,
            "city": r.city,
            "ward": r.ward,
            "station_name": r.station_name,
        })
    return pd.DataFrame(data)

def train_and_save() -> dict:
    with SessionLocal() as s:
        df = load_training_df(s)
    if df.empty or df["price_yen"].dropna().empty:
        return {"status":"no_data"}

    X, y = make_features(df)

    cat_cols = FEATURE_COLS_CAT
    num_cols = [c for c in X.columns if c not in cat_cols]
    pre = ColumnTransformer([
        ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=True), cat_cols)
    ], remainder="passthrough")
    model = Ridge(alpha=1.0, random_state=42)
    pipe = Pipeline([("pre", pre), ("model", model)])

    pipe.fit(X, y)
    pred = pipe.predict(X)
    r2 = r2_score(y, pred)
    mae = mean_absolute_error(y, pred)

    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump({"pipeline": pipe, "version": MODEL_VERSION}, MODEL_PATH)

    return {"status":"ok","r2":r2,"mae":mae,"version":MODEL_VERSION}

if __name__ == "__main__":
    print(train_and_save())
