from typing import Annotated, Optional

from rich.console import Console
from sqlmodel import Session
from typer import Option, Typer

from budy.constants import MAX_YEAR, MIN_YEAR
from budy.database import engine
from budy.services.report import get_volatility_report_data
from budy.views import render_volatility_report, render_warning

app = Typer(no_args_is_help=True)
console = Console()


@app.command(name="volatility")
def show_volatility_report(
    year: Annotated[
        Optional[int],
        Option(
            "--year",
            "-y",
            min=MIN_YEAR,
            max=MAX_YEAR,
            help="Target year.",
        ),
    ] = None,
) -> None:
    """Analyze spending volatility and outliers."""
    with Session(engine) as session:
        data = get_volatility_report_data(session, year)

    if not data:
        console.print(render_warning("No transactions found."))
        return

    console.print(render_volatility_report(data, year))
