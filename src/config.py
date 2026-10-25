from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    drive_base: Path = Path("/content/drive/MyDrive/energy-forecast")
    timezone: str = "Europe/Warsaw"
    lat_pl_center: float = 52.0693
    lon_pl_center: float = 19.4803

    @property
    def raw_dir(self) -> Path:
        return self.drive_base / "data" / "raw"

    @property
    def processed_dir(self) -> Path:
        return self.drive_base / "data" / "processed"

    @property
    def models_dir(self) -> Path:
        return self.drive_base / "data" / "models"

settings = Settings()
