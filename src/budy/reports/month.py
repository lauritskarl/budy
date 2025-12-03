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
from budy.views import render_budget_status, render_warning

app = Typer(no_args_is_help=True)
console = Console()


@app.command(name="month")
# @app.command(name="m", hidden=True)
def show_monthly_report(
    month: Annotated[
        Optional[int],
        Option(
            "--month",
            "-m",
            min=1,
            max=12,
            help="The month to report on (defaults to current).",
        ),
    ] = None,
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
) -> None:
    """Show the budget status report for a specific month."""
    today = date.today()
    target_month = month or today.month
    target_year = year or today.year
    month_name = calendar.month_name[target_month]

    with Session(engine) as session:
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

        if not budget:
            console.print(
                render_warning(
                    f"No budget found for {month_name} {target_year}.\n"
                    f"Use [bold]budy budget add[/bold] to set one first."
                )
            )

        # 1. Show the main budget panel
        console.print(
            render_budget_status(
                budget=budget,
                total_spent=total_spent,
                month_name=month_name,
                target_year=target_year,
            )
        )

        # 2. Add Forecasting if we are looking at the current month
        is_current_month = (target_month == today.month) and (target_year == today.year)

        if is_current_month:
            days_passed = today.day

            # Avoid division by zero if running at 00:00 on the 1st (unlikely but safe)
            if days_passed == 0:
                days_passed = 1

            avg_per_day = total_spent / days_passed
            projected_total = avg_per_day * last_day

            grid = Table.grid(padding=(0, 2))
            grid.add_column(style="dim italic")
            grid.add_column(justify="right")

            grid.add_row("Daily Average:", f"${avg_per_day / 100:,.2f}")
            grid.add_row("Projected Total:", f"[bold]${projected_total / 100:,.2f}[/]")

            if budget and projected_total > budget.amount:
                overage = projected_total - budget.amount
                grid.add_row("Projected Overage:", f"[red]+${overage / 100:,.2f}[/]")

            console.print("\n[bold underline]Forecast[/]")
            console.print(grid)
