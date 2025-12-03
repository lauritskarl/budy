from datetime import date
from typing import Annotated

from rich.console import Console
from sqlmodel import Session, asc, select
from typer import Option, Typer

from budy.database import engine
from budy.models import Budget
from budy.views import render_budget_list, render_warning

app = Typer(no_args_is_help=True)
console = Console()


@app.command(name="list")
# @app.command(name="ls", hidden=True)
def read_budgets(
    target_year: Annotated[
        int,
        Option("--year", "-y", help="Filter by year."),
    ] = date.today().year,
    offset: Annotated[
        int,
        Option(
            "--offset",
            "-o",
            help="Skip the first N entries.",
        ),
    ] = 0,
    limit: Annotated[
        int,
        Option(
            "--limit",
            "-l",
            help="Limit the number of entries shown.",
        ),
    ] = 12,
) -> None:
    """Display monthly budgets in a table."""
    with Session(engine) as session:
        budgets = list(
            session.exec(
                select(Budget)
                .where(Budget.target_year == target_year)
                .order_by(asc(Budget.target_month))
                .offset(offset)
                .limit(limit)
            ).all()
        )

        budget_map = {b.target_month: b for b in budgets}
        all_months_data = []

        for month in range(1, 13):
            all_months_data.append((month, budget_map.get(month)))

        display_data = all_months_data[offset : offset + limit]

        if not display_data:
            console.print(
                render_warning(f"No months found for {target_year} in range.")
            )
            return

        console.print(render_budget_list(display_data, target_year))


if __name__ == "__main__":
    app()
