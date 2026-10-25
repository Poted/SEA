from pathlib import Path
import pandas as pd
from src.config import settings

def process_pse_hourly(pse_path: Path | None = None) -> pd.DataFrame:
    path = pse_path or (settings.raw_dir / "pse_raw.parquet")
    df = pd.read_parquet(path)

    df["ts_end_utc"] = pd.to_datetime(df["dtime_utc"], utc=True)
    df = df.drop_duplicates(subset=["ts_end_utc"]).sort_values("ts_end_utc")

    df["timestamp_utc"] = (df["ts_end_utc"] - pd.Timedelta(minutes=15)).dt.floor("h")

    agg_cols = ["demand", "pv", "wi"]
    for col in agg_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    hourly = (
        df.groupby("timestamp_utc", as_index=False)[agg_cols]
        .mean()
        .rename(columns={"wi": "wind"})
    )

    hourly["pv"] = hourly["pv"].fillna(0.0)
    hourly["net_load"] = hourly["demand"] - hourly["pv"]
    return hourly.dropna(subset=["demand", "net_load"]).reset_index(drop=True)

def build_hourly_dataset() -> Path:
    pse_hourly = process_pse_hourly()
    weather = pd.read_parquet(settings.raw_dir / "weather_raw.parquet")
    weather["timestamp_utc"] = pd.to_datetime(weather["timestamp_utc"], utc=True)

    merged = (
        pd.merge(pse_hourly, weather, on="timestamp_utc", how="inner")
        .sort_values("timestamp_utc")
        .reset_index(drop=True)
    )

    out_path = settings.processed_dir / "dataset_hourly.parquet"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    merged.to_parquet(out_path, index=False)
    return out_path

if __name__ == "__main__":
    out = build_hourly_dataset()
    print(f"Saved: {out}")
