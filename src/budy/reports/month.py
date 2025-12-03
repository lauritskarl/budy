import calendar
from datetime import date
from typing import Annotated, Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from sqlmodel import Session, func, select
from typer import Option, Typer

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
            min=1900,
            max=2100,
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
            console.print(
                f"[yellow]No budget found for {month_name} {target_year}.[/yellow]\n"
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

        remaining = budget.amount - total_spent
        percent_spent = (total_spent / budget.amount) * 100 if budget.amount > 0 else 0

        if total_spent > budget.amount:
            color = "red"
            status_msg = "OVER BUDGET"
        elif total_spent >= budget.amount * 0.9:
            color = "yellow"
            status_msg = "NEAR LIMIT"
        else:
            color = "green"
            status_msg = "ON TRACK"

        table = Table.grid(padding=(0, 2))
        table.add_column(style="cyan")
        table.add_column(justify="right")

        table.add_row("Budgeted:", f"${budget.amount:,.2f}")
        table.add_row("Spent:", f"[bold {color}]${total_spent:,.2f}[/]")
        table.add_row("Remaining:", f"${remaining:,.2f}")

        bar_width = 30
        filled_len = min(int((total_spent / budget.amount) * bar_width), bar_width)
        empty_len = bar_width - filled_len

        bar_filled = "━" * filled_len
        bar_empty = "━" * empty_len
        progress_bar = f"[{color}]{bar_filled}[/][dim]{bar_empty}[/]"

        content = Table.grid()
        content.add_row(table)
        content.add_row("")
        content.add_row(f"{progress_bar} [bold]{int(percent_spent)}%[/]")

        console.print(
            Panel(
                content,
                title=f"[b]{month_name} {target_year}[/b]",
                subtitle=f"[bold {color}]{status_msg}[/]",
                expand=False,
                border_style=color,
            )
        )
