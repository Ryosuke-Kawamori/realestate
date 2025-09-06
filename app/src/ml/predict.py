from __future__ import annotations
import os, math, joblib
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import select
from ..db import SessionLocal
from ..models import Listing, Valuation
from ..config import get_settings
from .features import make_features, FEATURE_COLS_CAT

MODEL_PATH = "/app/model/model.joblib"

def load_model():
    if not os.path.exists(MODEL_PATH):
        return None
    return joblib.load(MODEL_PATH)

def score_new_listings(settings=None) -> list[dict]:
    settings = settings or get_settings()
    model_data = load_model()
    if not model_data:
        return []
    pipe = model_data["pipeline"]
    version = model_data.get("version","unknown")

    out = []
    with SessionLocal() as s:
        # 新規/更新のうち、十分なデータがあるものをスコアリング
        q = s.query(Listing).filter(Listing.price_yen.isnot(None), Listing.area_m2.isnot(None))
        rows = q.all()
        if not rows:
            return []
        df = pd.DataFrame([{
            "id": r.id,
            "price_yen": r.price_yen,
            "area_m2": r.area_m2,
            "age_years": r.age_years,
            "station_walk_min": r.station_walk_min,
            "prefecture": r.prefecture,
            "city": r.city,
            "ward": r.ward,
            "station_name": r.station_name,
        } for r in rows])

        X, y = make_features(df)
        # X には "id" が含まれていないので、id 対応用に df を参照
        preds = pipe.predict(X)
        # exp(予測log価格)
        y_pred_price = [float(math.exp(v)) for v in preds]

        # align indices
        X_idx = X.index
        for idx, y_pred in zip(X_idx, y_pred_price):
            rid = int(df.loc[idx, "id"])
            y_true = df.loc[idx, "price_yen"]
            residual = float(y_true - y_pred)
            residual_pct = float((y_true / y_pred) - 1.0)
            val = Valuation(listing_id=rid, model_version=version, y_true=y_true, y_pred=y_pred,
                            residual=residual, residual_pct=residual_pct)
            s.add(val)
            out.append({
                "listing_id": rid,
                "y_true": y_true,
                "y_pred": y_pred,
                "residual": residual,
                "residual_pct": residual_pct,
            })
        s.commit()
    return out
