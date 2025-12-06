from datetime import date, timedelta

from hypothesis import given
from hypothesis import strategies as st
from sqlmodel import Session, SQLModel
from typer.testing import CliRunner

from budy import app
from budy.database import engine
from budy.schemas import Transaction

runner = CliRunner()


def reset_db():
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)


@given(
    keyword=st.text(
        min_size=5, max_size=10, alphabet=st.characters(whitelist_categories=("L",))
    )
)
def test_search_transactions(keyword):
    """E2E: Search finds specific transactions by description."""
    reset_db()

    with Session(engine) as session:
        # Add a target transaction
        session.add(
            Transaction(
                amount=1000,
                entry_date=date.today(),
                description=f"Payment for {keyword} services",
                receiver="ServiceProv",
            )
        )
        # Add noise
        session.add(
            Transaction(
                amount=500,
                entry_date=date.today(),
                description="Lunch",
                receiver="Cafe",
            )
        )
        session.commit()

    result = runner.invoke(app, ["reports", "search", keyword])

    assert result.exit_code == 0
    assert keyword in result.stdout
    assert "Lunch" not in result.stdout


def test_payee_ranking():
    """E2E: Payees are ranked correctly by total spend."""
    reset_db()

    with Session(engine) as session:
        # "Big Spender" = 30.00 total
        for _ in range(3):
            session.add(
                Transaction(
                    amount=1000, entry_date=date.today(), receiver="Big Spender"
                )
            )

        # "Little Spender" = 5.00 total
        session.add(
            Transaction(amount=500, entry_date=date.today(), receiver="Little Spender")
        )
        session.commit()

    result = runner.invoke(app, ["reports", "payees"])

    assert result.exit_code == 0
    # Big Spender should be listed before Little Spender
    assert result.stdout.find("Big Spender") < result.stdout.find("Little Spender")


def test_weekday_report_structure():
    """E2E: Weekday report runs without errors on valid data."""
    reset_db()

    with Session(engine) as session:
        # Add a transaction for every day of the current week
        today = date.today()
        for i in range(7):
            session.add(Transaction(amount=1000, entry_date=today - timedelta(days=i)))
        session.commit()

    result = runner.invoke(app, ["reports", "weekday"])
    assert result.exit_code == 0
    assert "Spending Habits" in result.stdout


def test_volatility_report_outliers():
    """E2E: Volatility report identifies obvious outliers."""
    reset_db()

    with Session(engine) as session:
        # 20 small transactions
        for _ in range(20):
            session.add(Transaction(amount=500, entry_date=date.today()))

        # 1 massive outlier
        session.add(
            Transaction(
                amount=500000, entry_date=date.today(), description="Huge Purchase"
            )
        )
        session.commit()

    result = runner.invoke(app, ["reports", "volatility"])

    assert result.exit_code == 0
    assert "Huge Purchase" in result.stdout
    assert "Volatility Analysis" in result.stdout
