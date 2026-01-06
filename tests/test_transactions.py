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


@given(
    amount=st.decimals(
        min_value=Decimal("0.01"), max_value=Decimal("9999999"), places=2
    ),
    txn_date=st.dates(min_value=date(1900, 1, 1), max_value=date(2100, 12, 31)),
    new_amount=st.decimals(
        min_value=Decimal("0.01"), max_value=Decimal("9999999"), places=2
    ),
)
def test_update_transaction(amount, txn_date, new_amount):
    """Property: Updating a transaction works."""
    reset_db()
    runner = CliRunner()

    # Create
    with Session(engine) as session:
        txn = Transaction(amount=int(amount * 100), entry_date=txn_date)
        session.add(txn)
        session.commit()
        session.refresh(txn)
        txn_id = txn.id

    # Update
    result = runner.invoke(
        app, ["transactions", "update", str(txn_id), "--amount", str(new_amount)]
    )
    assert result.exit_code == 0
    assert "Updated" in result.stdout

    # Verify
    with Session(engine) as session:
        updated_txn = session.get(Transaction, txn_id)
        assert updated_txn is not None
        assert updated_txn.amount == int(new_amount * 100)


@given(
    amount=st.decimals(
        min_value=Decimal("0.01"), max_value=Decimal("9999999"), places=2
    ),
)
def test_delete_transaction(amount):
    """Property: Deleting a transaction works."""
    reset_db()
    runner = CliRunner()

    # Create
    with Session(engine) as session:
        txn = Transaction(amount=int(amount * 100), entry_date=date.today())
        session.add(txn)
        session.commit()
        session.refresh(txn)
        txn_id = txn.id

    # Delete with force
    result = runner.invoke(app, ["transactions", "delete", str(txn_id), "--force"])
    assert result.exit_code == 0
    assert "Deleted" in result.stdout

    # Verify
    with Session(engine) as session:
        deleted_txn = session.get(Transaction, txn_id)
        assert deleted_txn is None
