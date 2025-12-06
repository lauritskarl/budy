from datetime import date
from decimal import Decimal

from hypothesis import given
from hypothesis import strategies as st
from sqlmodel import Session, SQLModel
from typer.testing import CliRunner

from budy import app
from budy.config import settings as app_settings
from budy.database import engine
from budy.schemas import Transaction


def reset_db():
    """Helper to clean the database for every Hypothesis example."""
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)


@given(
    amount=st.decimals(
        min_value=Decimal("0.01"), max_value=Decimal("9999999"), places=2
    ),
    txn_date=st.dates(min_value=date(1900, 1, 1), max_value=date(2100, 12, 31)),
)
def test_add_transaction(amount, txn_date):
    """Property: Adding any valid transaction works and formats output correctly."""
    reset_db()
    runner = CliRunner()

    date_str = txn_date.strftime("%Y-%m-%d")
    amount_str = str(amount)

    result = runner.invoke(
        app, ["transactions", "add", "-a", amount_str, "-d", date_str]
    )

    assert result.exit_code == 0
    assert "Added!" in result.stdout
    assert f"{app_settings.currency_symbol}{amount:,.2f}" in result.stdout


@given(
    transactions=st.lists(
        st.tuples(
            st.decimals(min_value=Decimal("0.01"), max_value=Decimal("1000"), places=2),
            st.dates(min_value=date.today(), max_value=date.today()),
        ),
        max_size=5,
    )
)
def test_list_transactions(transactions):
    """Property: The list command should never crash, regardless of DB state."""
    reset_db()
    runner = CliRunner()

    with Session(engine) as session:
        for amt, dt in transactions:
            session.add(Transaction(amount=int(amt * 100), entry_date=dt))
        session.commit()

    result = runner.invoke(app, ["transactions", "list"])

    assert result.exit_code == 0
    assert "Transaction History" in result.stdout

    if transactions:
        last_amt = transactions[-1][0]
        assert f"{app_settings.currency_symbol}{last_amt:,.2f}" in result.stdout
    else:
        assert f"{app_settings.currency_symbol}0.00" in result.stdout
