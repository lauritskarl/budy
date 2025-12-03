from datetime import date
from typing import Annotated, Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from sqlmodel import Session, desc, select
from typer import Option, Typer

from budy.constants import MAX_YEAR, MIN_YEAR
from budy.database import engine
from budy.models import Transaction
from budy.views import render_simple_transaction_list, render_warning

app = Typer(no_args_is_help=True)
console = Console()


@app.command(name="volatility")
# @app.command(name="v", hidden=True)
def show_volatility_report(
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
) -> None:
    """
    Analyze spending volatility and outliers.
    Shows standard deviation and the largest transactions.
    """
    import statistics

    with Session(engine) as session:
        query = select(Transaction)
        if year:
            # Filter by year if provided
            query = query.where(
                Transaction.entry_date >= date(year, 1, 1),
                Transaction.entry_date <= date(year, 12, 31),
            )

        # Order by amount descending for the "Top 5" list
        transactions = session.exec(query.order_by(desc(Transaction.amount))).all()

        if not transactions:
            console.print(render_warning("No transactions found."))
            return

        amounts = [t.amount for t in transactions]

        # Statistics
        total_count = len(amounts)
        avg_val = statistics.mean(amounts)
        try:
            stdev_val = statistics.stdev(amounts)
        except statistics.StatisticsError:
            stdev_val = 0

        # Create Summary Panel
        summary_grid = Table.grid(padding=(0, 2))
        summary_grid.add_column(style="dim")
        summary_grid.add_column(justify="right", style="bold")

        summary_grid.add_row("Total Transactions:", str(total_count))
        summary_grid.add_row("Average Amount:", f"${avg_val / 100:,.2f}")
        summary_grid.add_row("Standard Deviation:", f"${stdev_val / 100:,.2f}")

        # Interpretation
        cv = (stdev_val / avg_val) if avg_val else 0
        if cv > 1.5:
            volatility_msg = "[red]High Volatility[/]"
        elif cv < 0.5:
            volatility_msg = "[green]Low Volatility[/]"
        else:
            volatility_msg = "[yellow]Moderate Volatility[/]"

        console.print(
            Panel(
                summary_grid,
                title=f"Volatility Analysis {'(' + str(year) + ')' if year else '(All Time)'}",
                subtitle=volatility_msg,
                expand=False,
            )
        )
        console.print("")

        # Reuse shared view for Top 5 list
        outliers = transactions[:5]
        console.print(
            render_simple_transaction_list(outliers, title="Top 5 Highest Transactions")
        )
