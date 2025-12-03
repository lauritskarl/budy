from datetime import date
from typing import Annotated, Optional

from rich.console import Console
from rich.table import Table
from typer import Option, Typer

from budy.constants import MAX_YEAR, MIN_YEAR
from budy.services.report import get_yearly_report_data
from budy.views import render_budget_status

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
            help="The year to report on (defaults to current).",
        ),
    ] = None,
):
    """Show the budget status report for a specific year."""
    current_date = date.today()
    target_year = year or current_date.year

    grid = Table.grid(padding=1)
    grid.add_column()
    grid.add_column()
    grid.add_column()

    panels = []
    monthly_reports = get_yearly_report_data(year=target_year)

    for report in monthly_reports:
        month_panel = render_budget_status(
            budget=report["budget"],
            total_spent=report["total_spent"],
            month_name=report["month_name"],
            target_year=report["target_year"],
        )
        panels.append(month_panel)

    for i in range(0, len(panels), 3):
        row_panels = panels[i : i + 3]
        while len(row_panels) < 3:
            row_panels.append("")
        grid.add_row(*row_panels)

    console.print(f"\n[bold underline]Yearly Overview: {target_year}[/]\n")
    console.print(grid)
