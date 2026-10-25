from pathlib import Path
import httpx
import pandas as pd
from src.config import settings

ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"
HOURLY_VARS = [
    "temperature_2m",
    "cloud_cover",
    "shortwave_radiation",
    "direct_normal_irradiance",
    "diffuse_radiation",
    "wind_speed_10m",
    "wind_speed_100m",
]

def fetch_weather_history(
    start_date: str = "2022-01-01",
    end_date: str = "2026-10-20",
    lat: float = settings.lat_pl_center,
    lon: float = settings.lon_pl_center,
) -> pd.DataFrame:
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": ",".join(HOURLY_VARS),
        "timezone": "UTC",
    }
    with httpx.Client(timeout=60.0) as client:
        response = client.get(ARCHIVE_URL, params=params)
        response.raise_for_status()
        data = response.json()

    df = pd.DataFrame(data["hourly"])
    df["timestamp_utc"] = pd.to_datetime(df["time"], utc=True)
    df = df.drop(columns=["time"]).sort_values("timestamp_utc").reset_index(drop=True)
    return df

def save_weather_raw(start_date: str = "2022-01-01", end_date: str = "2026-10-20") -> Path:
    df = fetch_weather_history(start_date=start_date, end_date=end_date)
    out_path = settings.raw_dir / "weather_raw.parquet"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(out_path, index=False)
    return out_path

if __name__ == "__main__":
    path = save_weather_raw()
    print(f"Saved: {path}")
