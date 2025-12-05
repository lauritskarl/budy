from typing import Annotated

from rich.console import Console
from sqlmodel import Session
from typer import Argument, Option, Typer

from budy.database import engine
from budy.services.transaction import search_transactions
from budy.views import render_search_results, render_warning

app = Typer(no_args_is_help=True)
console = Console()


@app.command(name="search")
def run_search(
    query: Annotated[
        str,
        Argument(help="Keyword to search for (in receiver or description)."),
    ],
    limit: Annotated[
        int,
        Option(
            "--limit",
            "-l",
            min=1,
            help="Maximum number of results to display.",
        ),
    ] = 20,
) -> None:
    """Search transactions by keyword in receiver or description."""
    with Session(engine) as session:
        results = search_transactions(session, query, limit)

    if not results:
        console.print(render_warning(f"No transactions found matching '{query}'."))
        return

    console.print(render_search_results(results, query, limit))
