from datetime import date
from decimal import Decimal

from hypothesis import given
from hypothesis import strategies as st
from sqlmodel import Session, SQLModel
from typer.testing import CliRunner

from budy import app
from budy.config import settings as app_settings
from budy.database import engine
from budy.schemas import Budget, Transaction


def reset_db():
    """Resets the test database by dropping and recreating all tables."""
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)


@given(
    year=st.integers(min_value=2020, max_value=2030),
    month=st.integers(min_value=1, max_value=12),
    budget_amount=st.integers(min_value=100, max_value=5000),
    tx_amount=st.decimals(
        min_value=Decimal("10.00"), max_value=Decimal("100.00"), places=2
    ),
)
def test_monthly_report_calculation(year, month, budget_amount, tx_amount):
    """Property: Monthly report correctly calculates 'Spent' vs 'Budget'."""
    reset_db()
    runner = CliRunner()

    with Session(engine) as session:
        session.add(
            Budget(target_year=year, target_month=month, amount=budget_amount * 100)
        )
        session.add(
            Transaction(entry_date=date(year, month, 15), amount=int(tx_amount * 100))
        )
        session.commit()

    result = runner.invoke(app, ["reports", "month", "-m", str(month), "-y", str(year)])

    assert result.exit_code == 0
    assert f"{app_settings.currency_symbol}{budget_amount:,.0f}" in result.stdout
    expected_spent = f"{app_settings.currency_symbol}{tx_amount:,.0f}"
    assert expected_spent in result.stdout
