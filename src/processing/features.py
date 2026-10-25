from pathlib import Path
import numpy as np
import pandas as pd
from src.config import settings

LAGS = [24, 48, 72, 168]
ROLL_WINDOWS = [24, 168]

def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    dt_local = df["timestamp_utc"].dt.tz_convert(settings.timezone)
    hour = dt_local.dt.hour
    dayofweek = dt_local.dt.dayofweek
    month = dt_local.dt.month
    dayofyear = dt_local.dt.dayofyear

    df["hour"] = hour
    df["dayofweek"] = dayofweek
    df["is_weekend"] = (dayofweek >= 5).astype(int)

    df["hour_sin"] = np.sin(2 * np.pi * hour / 24.0)
    df["hour_cos"] = np.cos(2 * np.pi * hour / 24.0)
    df["doy_sin"] = np.sin(2 * np.pi * dayofyear / 365.25)
    df["doy_cos"] = np.cos(2 * np.pi * dayofyear / 365.25)
    df["month"] = month
    return df

def add_lag_features(df: pd.DataFrame) -> pd.DataFrame:
    for col in ["net_load", "demand", "pv"]:
        for lag in LAGS:
            df[f"{col}_lag_{lag}h"] = df[col].shift(lag)

    shifted_net = df["net_load"].shift(24)
    for w in ROLL_WINDOWS:
        df[f"net_load_roll_mean_{w}h"] = shifted_net.rolling(w).mean()
        df[f"net_load_roll_std_{w}h"] = shifted_net.rolling(w).std()

    return df

def build_features() -> Path:
    in_path = settings.processed_dir / "dataset_hourly.parquet"
    df = pd.read_parquet(in_path).sort_values("timestamp_utc").reset_index(drop=True)

    df = add_time_features(df)
    df = add_lag_features(df)
    df = df.dropna().reset_index(drop=True)

    out_path = settings.processed_dir / "features_hourly.parquet"
    df.to_parquet(out_path, index=False)
    return out_path

if __name__ == "__main__":
    out = build_features()
    print(f"Saved: {out}")
