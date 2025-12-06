import tomllib
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field
from typer import get_app_dir

APP_NAME = "budy"


class BankConfig(BaseModel):
    """Configuration for a specific bank's transaction file import."""
    delimiter: str = ","
    decimal: str = "."
    encoding: str = "utf-8"
    date_col: str
    amount_col: str
    debit_credit_col: str
    debit_value: str = "D"
    receiver_col: Optional[str] = None
    description_col: Optional[str] = None


class Settings(BaseModel):
    """Application settings, loaded from defaults and optionally overridden by a config file."""
    app_name: str = APP_NAME
    currency_symbol: str = "$"
    min_year: int = 1900
    max_year: int = 2100
    first_name: str | None = None
    last_name: str | None = None
    banks: dict[str, BankConfig] = Field(
        default_factory=lambda: {
            "lhv": BankConfig(
                delimiter=",",
                decimal=".",
                date_col="Kuupäev",
                amount_col="Summa",
                debit_credit_col="Deebet/Kreedit (D/C)",
                receiver_col="Saaja/maksja nimi",
                description_col="Selgitus",
            ),
            "seb": BankConfig(
                delimiter=";",
                decimal=",",
                date_col="Kuupäev",
                amount_col="Summa",
                debit_credit_col="Deebet/Kreedit (D/C)",
                receiver_col="Saaja/maksja nimi",
                description_col="Selgitus",
            ),
            "swedbank": BankConfig(
                delimiter=";",
                decimal=",",
                date_col="Kuupäev",
                amount_col="Summa",
                debit_credit_col="Deebet/Kreedit",
                receiver_col="Saaja/Maksja",
                description_col="Selgitus",
            ),
        }
    )

    @classmethod
    def load(cls):
        """Loads settings from defaults and overrides from the config file."""
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
