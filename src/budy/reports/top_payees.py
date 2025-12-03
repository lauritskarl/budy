from typing import Annotated, Optional

from rich.console import Console
from typer import Option, Typer

from budy.constants import MAX_YEAR, MIN_YEAR
from budy.services.report import get_top_payees
from budy.views import render_payee_ranking, render_warning

app = Typer(no_args_is_help=True)
console = Console()


@app.command(name="payees")
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
    top_payees = get_top_payees(year=year, limit=limit)

    if not top_payees:
        console.print(render_warning("No transactions found."))
        return

    console.print(render_payee_ranking(top_payees))
