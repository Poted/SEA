from pathlib import Path
from datetime import date, timedelta
import httpx
import pandas as pd
from src.config import settings

PSE_API_URL = "https://api.raporty.pse.pl/api/his-wlk-cal"

def fetch_pse_chunk(client: httpx.Client, start_d: date, end_d: date) -> list[dict]:
    filter_str = f"doba ge '{start_d.isoformat()}' and doba le '{end_d.isoformat()}'"
    url = PSE_API_URL
    params = {"$filter": filter_str, "$first": 10000}
    records = []

    while url:
        resp = client.get(url, params=params)
        resp.raise_for_status()
        payload = resp.json()
        records.extend(payload.get("value", []))
        url = payload.get("nextLink")
        params = None

    return records

def fetch_pse_history(
    start_date: str = "2024-07-01",
    end_date: str = "2026-10-20",
    chunk_days: int = 30,
) -> pd.DataFrame:
    current = date.fromisoformat(start_date)
    end = date.fromisoformat(end_date)
    all_records = []

    with httpx.Client(timeout=60.0) as client:
        while current <= end:
            chunk_end = min(current + timedelta(days=chunk_days - 1), end)
            chunk_data = fetch_pse_chunk(client, current, chunk_end)
            all_records.extend(chunk_data)
            current = chunk_end + timedelta(days=1)

    return pd.DataFrame(all_records)

def save_pse_raw(start_date: str = "2024-07-01", end_date: str = "2026-10-20") -> Path:
    df = fetch_pse_history(start_date=start_date, end_date=end_date)
    out_path = settings.raw_dir / "pse_raw.parquet"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(out_path, index=False)
    return out_path

if __name__ == "__main__":
    path = save_pse_raw()
    print(f"Saved: {path}")
