import calendar
from datetime import date
from typing import Annotated, Optional

from rich.console import Console
from rich.table import Table
from sqlmodel import Session, desc, select
from typer import Option, Typer

from budy.database import engine
from budy.models import Budget

app = Typer(no_args_is_help=True)
console = Console()


@app.command(name="list")
def list_budgets(
    target_year: Annotated[
        int,
        Option("--year", "-y", help="Filter by year."),
    ] = date.today().year,
    offset: Annotated[
        Optional[int],
        Option(
            "--offset",
            "-o",
            help="Skip the first N entries.",
        ),
    ] = 0,
    limit: Annotated[
        Optional[int],
        Option(
            "--limit",
            "-l",
            help="Limit the number of entries shown.",
        ),
    ] = 12,
) -> None:
    """Display monthly budgets in a table."""
    with Session(engine) as session:
        budgets = session.exec(
            select(Budget)
            .where(Budget.target_year == target_year)
            .order_by(desc(Budget.target_month))
            .offset(offset)
            .limit(limit)
        ).all()

        if not budgets:
            console.print(f"[yellow]No budgets found for {target_year}.[/yellow]")
            return

        total_budgeted = sum(b.amount for b in budgets)

        table = Table(title=f"Budget List ({target_year})", show_footer=True)

        table.add_column("ID", justify="right", style="dim")

        table.add_column(
            "Month",
            style="cyan",
            footer="Total Budgeted:",
        )

        table.add_column(
            "Amount",
            justify="right",
            style="green",
            footer=f"${total_budgeted}",
        )

        for budget in budgets:
            month_name = calendar.month_name[budget.target_month]
            table.add_row(
                str(budget.id),
                month_name,
                f"${budget.amount}",
            )

        console.print(table)


if __name__ == "__main__":
    app()
