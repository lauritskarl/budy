import calendar
from collections import defaultdict
from statistics import mean

from rich.console import Console
from rich.table import Table
from sqlmodel import Session, select
from typer import Typer

from budy.database import engine
from budy.models import Transaction
from budy.views import render_warning

app = Typer(no_args_is_help=True)
console = Console()


@app.command(name="weekday")
# @app.command(name="w", hidden=True)
def show_weekday_report() -> None:
    """
    Analyze spending habits by day of the week.
    Shows which days you statistically spend the most money on.
    """
    with Session(engine) as session:
        transactions = session.exec(select(Transaction)).all()

        if not transactions:
            console.print(render_warning("No transactions found to analyze."))
            return

        # Bucket data by weekday (0=Monday, 6=Sunday)
        day_buckets = defaultdict(list)
        for t in transactions:
            day_buckets[t.entry_date.weekday()].append(t.amount)

        total_all_spent = sum(t.amount for t in transactions)

        table = Table(title="Spending Habits by Day of Week", show_footer=True)
        table.add_column("Day", style="cyan", footer="TOTAL")
        table.add_column("Avg Transaction", justify="right", style="green")
        table.add_column(
            "Transaction Count",
            justify="right",
            style="dim",
            footer=str(len(transactions)),
        )
        table.add_column(
            "Total Spent",
            justify="right",
            style="bold",
            footer=f"${total_all_spent / 100:,.2f}",
        )

        # Sort by day of week (Monday first)
        for day_idx in range(7):
            day_name = calendar.day_name[day_idx]
            amounts = day_buckets[day_idx]

            if not amounts:
                table.add_row(day_name, "-", "0", "-")
                continue

            avg_amount = mean(amounts)
            total_amount = sum(amounts)
            count = len(amounts)

            table.add_row(
                day_name,
                f"${avg_amount / 100:,.2f}",
                str(count),
                f"${total_amount / 100:,.2f}",
            )

        console.print(table)
