import pandas as pd
import numpy as np

FEATURE_COLS_NUM = ["area_m2", "age_years", "station_walk_min"]
FEATURE_COLS_CAT = ["prefecture", "city", "ward", "station_name"]

def make_features(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    df = df.copy()
    df = df[(df["price_yen"].notna()) & (df["area_m2"].notna()) & (df["area_m2"] > 0)]
    df["log_price"] = np.log(df["price_yen"])
    df["log_area"] = np.log(df["area_m2"])
    # 年齢の二乗項
    df["age2"] = (df["age_years"].fillna(df["age_years"].median()))**2
    # 欠損処理
    for col in FEATURE_COLS_NUM + ["age2"]:
        if col not in df.columns:
            df[col] = np.nan
        df[col] = df[col].fillna(df[col].median())
    for col in FEATURE_COLS_CAT:
        if col not in df.columns:
            df[col] = ""
        df[col] = df[col].fillna("")
    X = df[["log_area","age_years","age2","station_walk_min"] + FEATURE_COLS_CAT].copy()
    y = df["log_price"].copy()
    return X, y
