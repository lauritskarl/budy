from typer.testing import CliRunner
from sqlmodel import Session, SQLModel
from budy import app
from budy.database import engine
from budy.schemas import Transaction, Category
from datetime import date

runner = CliRunner()


def reset_db():
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)


def test_export_transactions(tmp_path):
    reset_db()

    # 1. Create data
    with Session(engine) as session:
        # Create category
        cat = Category(name="Groceries", color="green")
        session.add(cat)
        session.commit()
        session.refresh(cat)

        # Create transactions
        t1 = Transaction(
            amount=1000,
            entry_date=date(2023, 1, 1),
            category_id=cat.id,
            receiver="Store A",
        )
        t2 = Transaction(
            amount=2000, entry_date=date(2023, 1, 2), receiver="Store B"
        )  # No category
        session.add(t1)
        session.add(t2)
        session.commit()

    # 2. Export to CSV
    csv_file = tmp_path / "export.csv"
    result = runner.invoke(
        app, ["transactions", "export", "--output", str(csv_file), "--format", "csv"]
    )
    assert result.exit_code == 0
    assert "Exported" in result.stdout
    assert csv_file.exists()

    content = csv_file.read_text()
    assert "Store A" in content
    assert "Store B" in content
    assert "Groceries" in content
    assert "10.0" in content  # 1000 cents -> 10.00
    assert "20.0" in content

    # 3. Export to JSON
    json_file = tmp_path / "export.json"
    result = runner.invoke(
        app, ["transactions", "export", "--output", str(json_file), "--format", "json"]
    )
    assert result.exit_code == 0
    assert json_file.exists()

    content = json_file.read_text()
    assert '"receiver":"Store A"' in content
    assert '"category":"Groceries"' in content
