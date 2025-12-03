import calendar
from datetime import date
from typing import Annotated, Optional

from rich.console import Console
from rich.table import Table
from sqlmodel import Session, func, select
from typer import Option, Typer

from budy.constants import MAX_YEAR, MIN_YEAR
from budy.database import engine
from budy.models import Budget, Transaction
from budy.views import render_budget_status

app = Typer(no_args_is_help=True)
console = Console()


@app.command(name="year")
@app.command(name="y", hidden=True)
def show_yearly_report(
    year: Annotated[
        Optional[int],
        Option(
            "--year",
            "-y",
            min=MIN_YEAR,
            max=MAX_YEAR,
            help="The year to report on (defaults to current).",
        ),
    ] = None,
):
    """Show the budget status report for a specific year."""
    current_date = date.today()
    target_year = year or current_date.year

    grid = Table.grid(padding=1)
    grid.add_column()
    grid.add_column()
    grid.add_column()

    panels = []

    with Session(engine) as session:
        for target_month in range(1, 13):
            month_name = calendar.month_name[target_month]

            budget = session.exec(
                select(Budget).where(
                    Budget.target_year == target_year,
                    Budget.target_month == target_month,
                )
            ).first()

            _, last_day = calendar.monthrange(target_year, target_month)
            start_date = date(target_year, target_month, 1)
            end_date = date(target_year, target_month, last_day)

            total_spent = (
                session.scalar(
                    select(func.sum(Transaction.amount)).where(
                        Transaction.entry_date >= start_date,
                        Transaction.entry_date <= end_date,
                    )
                )
                or 0
            )

            month_panel = render_budget_status(
                budget=budget,
                total_spent=total_spent,
                month_name=month_name,
                target_year=target_year,
            )
            panels.append(month_panel)

    for i in range(0, len(panels), 3):
        row_panels = panels[i : i + 3]
        while len(row_panels) < 3:
            row_panels.append("")
        grid.add_row(*row_panels)

    console.print(f"\n[bold underline]Yearly Overview: {target_year}[/]\n")
    console.print(grid)
