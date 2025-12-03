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
    by_count: Annotated[
        bool,
        Option(
            "--by-count",
            "-c",
            help="Sort by transaction count instead of total amount.",
        ),
    ] = False,
) -> None:
    """
    Rank payees by total spending or frequency.
    Who is getting most of your money?
    """
    top_payees = get_top_payees(year=year, limit=limit, by_count=by_count)

    if not top_payees:
        console.print(render_warning("No transactions found."))
        return

    title = "Top Payees by Frequency" if by_count else "Top Payees by Amount"
    console.print(render_payee_ranking(top_payees, title=title))
