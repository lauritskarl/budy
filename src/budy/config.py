import tomllib
from pathlib import Path

from pydantic import BaseModel
from typer import get_app_dir

APP_NAME = "budy"


class Settings(BaseModel):
    app_name: str = APP_NAME
    currency_symbol: str = "$"
    min_year: int = 1900
    max_year: int = 2100
    username: str | None = None

    @classmethod
    def load(cls):
        """
        Loads settings from:
        1. Defaults
        2. Overrides from config file (if present)
        """
        app_dir = Path(get_app_dir(APP_NAME))
        app_dir.mkdir(parents=True, exist_ok=True)
        config_path = app_dir / "config.toml"

        config_data = {}

        if config_path.exists():
            with open(config_path, "rb") as f:
                data = tomllib.load(f)
                config_data = data

        return cls(**config_data)


settings = Settings.load()
