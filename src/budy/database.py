from pathlib import Path

from sqlmodel import create_engine
from typer import get_app_dir

APP_NAME = "budy"

app_dir = get_app_dir(APP_NAME)

app_dir_path = Path(app_dir)
app_dir_path.mkdir(parents=True, exist_ok=True)

sqlite_file_name = app_dir_path / "budy.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)
