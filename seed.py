import random
from datetime import date

from rich import print
from sqlmodel import Session, select

from budy.database import engine
from budy.models import Budget, Transaction


def seed_db():
    """Populates the database with budgets and random transactions for the last 3 years."""
    with Session(engine) as session:
        today = date.today()
        current_year = today.year
        years = range(current_year - 2, current_year + 1)

        total_transactions = 0
        budgets_created = 0

        print(f"Seeding data for years: [bold]{list(years)}[/bold]...\n")

        for year in years:
            print(f"Processing [bold]{year}[/bold]...")
            for month in range(1, 13):
                existing_budget = session.exec(
                    select(Budget).where(
                        Budget.target_year == year, Budget.target_month == month
                    )
                ).first()

                if not existing_budget:
                    budget_amount = random.choice([2000, 2200, 2500, 3000])
                    budget = Budget(
                        amount=budget_amount,
                        target_month=month,
                        target_year=year,
                    )
                    session.add(budget)
                    budgets_created += 1

                num_transactions = random.randint(10, 30)

                for _ in range(num_transactions):
                    amount = random.randint(10, 150)

                    random_day = random.randint(1, 28)
                    entry_date = date(year, month, random_day)

                    transaction = Transaction(amount=amount, entry_date=entry_date)
                    session.add(transaction)
                    total_transactions += 1

        session.commit()

        print("\n[green]✓[/green] Seeding Complete!")
        print(f"Created [bold]{budgets_created}[/bold] new budgets.")
        print(f"Added [bold]{total_transactions}[/bold] random transactions.")


if __name__ == "__main__":
    seed_db()
