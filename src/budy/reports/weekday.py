from rich.console import Console
from sqlmodel import Session
from typer import Typer

from budy.database import engine
from budy.services.report import get_weekday_report_data
from budy.views import render_warning, render_weekday_report

app = Typer(no_args_is_help=True)
console = Console()


@app.command(name="weekday")
def show_weekday_report() -> None:
    """Analyze spending habits by day of the week."""
    with Session(engine) as session:
        report_data = get_weekday_report_data(session)

    if not report_data:
        console.print(render_warning("No transactions found to analyze."))
        return

    console.print(render_weekday_report(report_data))
