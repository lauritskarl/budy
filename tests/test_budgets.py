from hypothesis import given
from hypothesis import strategies as st
from sqlmodel import SQLModel
from typer.testing import CliRunner

from budy import app
from budy.config import settings as app_settings
from budy.database import engine


def reset_db():
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)


@given(
    amount=st.integers(min_value=1, max_value=9999999),
    month=st.integers(min_value=1, max_value=12),
    year=st.integers(min_value=app_settings.min_year, max_value=app_settings.max_year),
)
def test_add_and_list_budget(amount, month, year):
    """Property: Budgets can be added and immediately retrieved."""
    reset_db()
    runner = CliRunner()

    result = runner.invoke(
        app, ["budgets", "add", "-m", str(month), "-y", str(year), "-a", str(amount)]
    )
    assert result.exit_code == 0
    assert "Saved!" in result.stdout

    result_list = runner.invoke(app, ["budgets", "list", "-y", str(year)])
    assert result_list.exit_code == 0
    assert f"{app_settings.currency_symbol}{amount:,.0f}" in result_list.stdout


@given(
    month=st.integers(min_value=1, max_value=12),
    year=st.integers(min_value=app_settings.min_year, max_value=app_settings.max_year),
)
def test_budget_collision(month, year):
    """Property: Adding a duplicate budget triggers a prompt/warning."""
    reset_db()
    runner = CliRunner()

    runner.invoke(
        app, ["budgets", "add", "-m", str(month), "-y", str(year), "-a", "500"]
    )

    result = runner.invoke(
        app,
        ["budgets", "add", "-m", str(month), "-y", str(year), "-a", "600"],
        input="n\n",
    )

    assert "already exists" in result.stdout
