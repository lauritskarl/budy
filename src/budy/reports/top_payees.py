from collections import defaultdict
from datetime import date
from typing import Annotated, Optional

from rich.console import Console
from sqlmodel import Session, select
from typer import Option, Typer

from budy.constants import MAX_YEAR, MIN_YEAR
from budy.database import engine
from budy.models import Transaction
from budy.views import render_payee_ranking, render_warning

app = Typer(no_args_is_help=True)
console = Console()


@app.command(name="payees")
# @app.command(name="p", hidden=True)
def show_top_payees(
    year: Annotated[
        Optional[int],
        Option(
            "--year",
            "-y",
            min=MIN_YEAR,
            max=MAX_YEAR,
            help="Filter analysis by year (defaults to all time).",
        ),
    ] = None,
    limit: Annotated[
        int,
        Option(
            "--limit",
            "-l",
            help="Number of payees to show.",
        ),
    ] = 10,
) -> None:
    """
    Rank payees by total spending.
    Who is getting most of your money?
    """
    with Session(engine) as session:
        query = select(Transaction)
        if year:
            query = query.where(
                Transaction.entry_date >= date(year, 1, 1),
                Transaction.entry_date <= date(year, 12, 31),
            )

        transactions = session.exec(query).all()

        if not transactions:
            console.print(render_warning("No transactions found."))
            return

        # Aggregation Logic
        # (Receiver Name) -> [amounts...]
        grouped = defaultdict(list)

        for t in transactions:
            # Normalize name: strip whitespace, handle None, maybe uppercase for grouping
            name = (t.receiver or "Unknown").strip()
            if not name:
                name = "Unknown"
            grouped[name].append(t.amount)

        # Create summary list: (Name, Count, Total, Avg)
        summary = []
        for name, amounts in grouped.items():
            total = sum(amounts)
            count = len(amounts)
            avg = int(total / count)
            summary.append((name, count, total, avg))

        # Sort by Total Amount Descending
        summary.sort(key=lambda x: x[2], reverse=True)

        # Slice top N
        top_payees = summary[:limit]

        console.print(render_payee_ranking(top_payees))
