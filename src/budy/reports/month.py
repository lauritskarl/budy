import calendar
from datetime import date
from typing import Annotated, Optional

from rich.console import Console
from sqlmodel import Session, func, select
from typer import Option, Typer

from budy import views
from budy.constants import MAX_YEAR, MIN_YEAR
from budy.database import engine
from budy.models import Budget, Transaction

app = Typer(no_args_is_help=True)
console = Console()


@app.command(name="month")
@app.command(name="m", hidden=True)
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
    current_date = date.today()
    target_month = month or current_date.month
    target_year = year or current_date.year
    month_name = calendar.month_name[target_month]

    with Session(engine) as session:
        budget = session.exec(
            select(Budget).where(
                Budget.target_year == target_year,
                Budget.target_month == target_month,
            )
        ).first()

        if not budget:
            views.render_warning(
                f"No budget found for {month_name} {target_year}.\n"
                f"Use [bold]budy budget add[/bold] to set one first."
            )
            return

        _, last_day = calendar.monthrange(target_year, target_month)
        start_date = date(target_year, target_month, 1)
        end_date = date(target_year, target_month, last_day)

        statement = select(func.sum(Transaction.amount)).where(
            Transaction.entry_date >= start_date,
            Transaction.entry_date <= end_date,
        )
        total_spent = session.exec(statement).one() or 0

        console.print(
            views.render_budget_status(budget, total_spent, month_name, target_year)
        )
