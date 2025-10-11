"""Application configuration settings."""
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.utils import get_project_root


class Settings(BaseSettings):
    """Application settings loaded from environment and files."""
    model_config = SettingsConfigDict(env_file=".env")

    app_version: str = "0.0.0"
    sensebox_ids_file: str = "data/sensebox_ids.txt"
    sensebox_ids: list[str] = []

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._load_sensebox_ids()

    def _load_sensebox_ids(self):
        """Load senseBox IDs from file on startup"""
        sensebox_file = get_project_root() / self.sensebox_ids_file

        if sensebox_file.exists():
            with open(sensebox_file, encoding="utf-8") as f:
                self.sensebox_ids = [line.strip() for line in f if line.strip()]


settings = Settings()
