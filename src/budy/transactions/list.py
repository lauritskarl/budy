from typing import Annotated

from rich.console import Console
from typer import Option, Typer

from budy.services.transaction import get_transactions
from budy.views import render_transaction_list, render_warning

app = Typer(no_args_is_help=True)
console = Console()


@app.command(name="list")
def read_transactions(
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
    ] = 7,
) -> None:
    """Display transaction history in a table."""
    display_data = get_transactions(offset=offset, limit=limit)
    if not display_data:
        console.print(render_warning("No transactions found for the selected dates."))
        return
    console.print(render_transaction_list(display_data))


if __name__ == "__main__":
    app()
