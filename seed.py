import random
from datetime import date

from rich import print
from sqlmodel import Session, select

from budy.database import engine
from budy.models import Budget, Transaction


def seed_db():
    """Populates the database with a budget and random transactions for the current month."""
    with Session(engine) as session:
        today = date.today()
        current_month = today.month
        current_year = today.year

        # 1. Create or Get Budget
        existing_budget = session.exec(
            select(Budget).where(
                Budget.target_year == current_year, Budget.target_month == current_month
            )
        ).first()

        if not existing_budget:
            budget_amount = 2000
            budget = Budget(
                amount=budget_amount,
                target_month=current_month,
                target_year=current_year,
            )
            session.add(budget)
            print(
                f"[green]✓[/green] Created Budget: [bold]${budget_amount}[/bold] for {current_month}/{current_year}"
            )
        else:
            print(
                f"[yellow]![/yellow] Budget already exists for {current_month}/{current_year}, skipping creation."
            )

        # 2. Generate Random Transactions
        # We will generate 15 random transactions
        print("Generating random transactions...")

        for _ in range(15):
            # Random amount between $10 and $150
            amount = random.randint(10, 150)

            # Random day in the current month (avoiding day 29-31 to keep it simple across all months)
            random_day = random.randint(1, 28)
            entry_date = date(current_year, current_month, random_day)

            transaction = Transaction(amount=amount, entry_date=entry_date)
            session.add(transaction)

        session.commit()
        print(
            "[green]✓[/green] Successfully added [bold]15 random transactions[/bold]."
        )
        print("Run [bold]budy status[/bold] to see the results!")


if __name__ == "__main__":
    seed_db()
