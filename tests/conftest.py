import os

import pytest
from sqlmodel import Session, SQLModel
from typer.testing import CliRunner

os.environ["BUDY_DB_URL"] = "sqlite:///:memory:"

from budy import database


@pytest.fixture(name="session")
def session_fixture():
    SQLModel.metadata.create_all(database.engine)

    with Session(database.engine) as session:
        yield session

    SQLModel.metadata.drop_all(database.engine)


@pytest.fixture(name="runner")
def runner_fixture():
    return CliRunner()
