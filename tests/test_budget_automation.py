from datetime import date

from sqlmodel import Session, SQLModel
from typer.testing import CliRunner

from budy import app
from budy.database import engine
from budy.schemas import Transaction


def reset_db():
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)


def test_generate_budgets_with_history():
    """E2E: Budget generation produces suggestions when history exists."""
    reset_db()
    runner = CliRunner()

    target_year = 2025
    prev_year = 2024

    # Populate DB with consistent spending in the previous year
    with Session(engine) as session:
        for month in range(1, 13):
            # Add spending of ~200.00 per month
            # Increased from 50.00 to 200.00 to avoid rounding-to-zero logic in suggest_budget_amount
            session.add(
                Transaction(amount=20000, entry_date=date(prev_year, month, 15))
            )
        session.commit()

    # Generate budgets for the target year, answering "yes" to save
    result = runner.invoke(
        app, ["budgets", "generate", "--year", str(target_year), "--yes"]
    )

    assert result.exit_code == 0
    assert (
        f"Analyzing spending history to generate budgets for {target_year}"
        in result.stdout
    )
    assert "Suggested" in result.stdout
    assert "Successfully saved" in result.stdout

    # Verify a budget was actually created
    list_result = runner.invoke(app, ["budgets", "list", "--year", str(target_year)])
    # The heuristic might suggest 200.00 or near it
    # We just check that *some* budget amount is now set (not "Not set")
    assert "Not set" not in list_result.stdout


def test_generate_budgets_no_data():
    """E2E: Budget generation handles empty history gracefully."""
    reset_db()
    runner = CliRunner()

    result = runner.invoke(app, ["budgets", "generate", "--year", "2030"])

    assert result.exit_code == 0
    assert "No suggestions found" in result.stdout
