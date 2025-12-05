from datetime import date
from typing import Annotated, Optional

from rich.console import Console
from sqlmodel import Session
from typer import Option, Typer

from budy.constants import MAX_YEAR, MIN_YEAR
from budy.database import engine
from budy.services.report import get_yearly_report_data
from budy.views import render_yearly_report

app = Typer(no_args_is_help=True)
console = Console()


@app.command(name="year")
def show_yearly_report(
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
):
    """Show the budget status report for a specific year."""
    target_year = year or date.today().year

    with Session(engine) as session:
        monthly_reports = get_yearly_report_data(session, target_year)

    console.print(f"\n[bold underline]Yearly Overview: {target_year}[/]\n")
    console.print(render_yearly_report(monthly_reports, target_year))
