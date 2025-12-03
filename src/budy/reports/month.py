from datetime import date
from typing import Annotated, Optional

from rich.console import Console
from typer import Option, Typer

from budy.constants import MAX_YEAR, MIN_YEAR
from budy.services.report import generate_monthly_report_data
from budy.views import render_budget_status, render_warning

app = Typer(no_args_is_help=True)
console = Console()


@app.command(name="month")
def show_monthly_report(
    month: Annotated[
        Optional[int],
        Option(
            "--month",
            "-m",
            min=1,
            max=12,
            help="The month to report on (defaults to current).",
        ),
    ] = None,
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
) -> None:
    """Show the budget status report for a specific month."""
    today = date.today()
    target_month = month or today.month
    target_year = year or today.year

    report_data = generate_monthly_report_data(
        target_month=target_month, target_year=target_year
    )

    if not report_data["budget"]:
        console.print(
            render_warning(
                f"No budget found for {report_data['month_name']} {report_data['target_year']}.\n"
                f"Use [bold]budy budget add[/bold] to set one first."
            )
        )
        return

    # 1. Show the main budget panel
    console.print(
        render_budget_status(
            budget=report_data["budget"],
            total_spent=report_data["total_spent"],
            month_name=report_data["month_name"],
            target_year=report_data["target_year"],
            forecast_data=report_data["forecast"],
        )
    )


if __name__ == "__main__":
    app()
