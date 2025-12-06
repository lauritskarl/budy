import csv
from datetime import date
from decimal import Decimal

from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st
from sqlmodel import Session, SQLModel, select
from typer.testing import CliRunner

from budy import app
from budy.database import engine
from budy.schemas import Transaction


def reset_db():
    """Resets the test database by dropping and recreating all tables."""
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(
    transactions=st.lists(
        st.tuples(
            st.dates(min_value=date(2000, 1, 1), max_value=date(2099, 12, 31)),
            st.decimals(
                min_value=Decimal("0.01"), max_value=Decimal("10000.00"), places=2
            ),
            st.text(
                min_size=1,
                max_size=50,
                alphabet=st.characters(
                    blacklist_categories=("Cs",), blacklist_characters="\n\r,"
                ),
            ),
            st.text(
                min_size=1,
                max_size=50,
                alphabet=st.characters(
                    blacklist_categories=("Cs",), blacklist_characters="\n\r,"
                ),
            ),
        ),
        min_size=1,
        max_size=20,
    )
)
def test_import_csv_workflow(tmp_path, transactions):
    """E2E: Import transactions from a generated CSV file matching 'lhv' format."""
    reset_db()
    runner = CliRunner()

    # Create a temporary CSV file mimicking the 'lhv' bank config (defined in budy/config.py)
    # Config: delimiter=",", date="Kuupäev", amount="Summa", d/c="Deebet/Kreedit (D/C)", value="D"
    csv_file = tmp_path / "bank_statement.csv"

    header = [
        "Kuupäev",
        "Saaja/maksja nimi",
        "Selgitus",
        "Summa",
        "Deebet/Kreedit (D/C)",
    ]

    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for dt, amt, receiver, desc in transactions:
            # Note: Polars/Budy importer handles standard ISO dates
            writer.writerow(
                [
                    dt.strftime("%Y-%m-%d"),
                    receiver,
                    desc,
                    str(amt),
                    "D",  # Must match debit_value to be imported as an expense
                ]
            )

    # Run the import command
    result = runner.invoke(
        app, ["transactions", "import", "--bank", "lhv", "--file", str(csv_file)]
    )

    assert result.exit_code == 0
    assert "Successfully imported" in result.stdout
    assert str(len(transactions)) in result.stdout

    # Verify data in DB
    with Session(engine) as session:
        db_txs = session.exec(select(Transaction)).all()
        assert len(db_txs) == len(transactions)

        # Spot check total amount
        total_imported = sum(t.amount for t in db_txs)
        expected_total = sum(int(amt * 100) for _, amt, _, _ in transactions)
        assert total_imported == expected_total
