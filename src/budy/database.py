import os
from pathlib import Path

from sqlmodel import create_engine
from typer import get_app_dir

from budy.config import settings

target_db_url = os.getenv("BUDY_DB_URL")
connect_args = {"check_same_thread": False}
pool_class = None

if not target_db_url:
    app_dir = get_app_dir(settings.app_name)
    app_dir_path = Path(app_dir)
    app_dir_path.mkdir(parents=True, exist_ok=True)
    sqlite_file_name = app_dir_path / "budy.db"
    target_db_url = f"sqlite:///{sqlite_file_name}"

if ":memory:" in target_db_url:
    from sqlalchemy.pool import StaticPool

    pool_class = StaticPool

engine = create_engine(target_db_url, connect_args=connect_args, poolclass=pool_class)
