from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "budy"
    currency_symbol: str = "$"
    min_year: int = 1900
    max_year: int = 2100
    username: str | None = None

    # Helper to load from a TOML/JSON file in the future
    @classmethod
    def load(cls):
        # logic to read from get_app_dir(APP_NAME) / "config.toml"
        return cls()


settings = Settings.load()
