from datetime import date
from typing import Annotated, Optional

from rich.console import Console
from sqlmodel import Session, desc, select
from typer import Option, Typer

from budy import views
from budy.database import engine
from budy.models import Budget

app = Typer(no_args_is_help=True)
console = Console()


@app.command(name="list")
@app.command(name="ls", hidden=True)
def read_budgets(
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
        budgets = list(
            session.exec(
                select(Budget)
                .where(Budget.target_year == target_year)
                .order_by(desc(Budget.target_month))
                .offset(offset)
                .limit(limit)
            ).all()
        )

        if not budgets:
            views.render_warning(f"No budgets found for {target_year}")
            return

        views.render_budget_list(budgets, target_year)


if __name__ == "__main__":
    app()
