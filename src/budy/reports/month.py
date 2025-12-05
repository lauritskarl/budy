from datetime import date
from typing import Annotated, Optional

from rich.console import Console
from sqlmodel import Session
from typer import Option, Typer

from budy.constants import MAX_YEAR, MIN_YEAR
from budy.database import engine
from budy.services.report import generate_monthly_report_data
from budy.views import render_budget_status, render_warning

app = Typer(no_args_is_help=True)
console = Console()


@app.command(name="month")
def show_monthly_report(
    month: Annotated[
        Optional[int],
        Option("--month", "-m", min=1, max=12, help="Target month."),
    ] = None,
    year: Annotated[
        Optional[int],
        Option("--year", "-y", min=MIN_YEAR, max=MAX_YEAR, help="Target year."),
    ] = None,
) -> None:
    """Show the budget status report for a specific month."""
    today = date.today()
    target_month = month or today.month
    target_year = year or today.year

    with Session(engine) as session:
        data = generate_monthly_report_data(session, target_month, target_year)

    if not data.budget:
        console.print(
            render_warning(
                f"No budget found for {data.month_name} {data.target_year}.\n"
                f"Use [bold]budy budgets add[/bold] to set one first."
            )
        )
        return

    # Views now accept DTOs or DTO fields.
    # Since render_budget_status is shared with Year report, we pass explicit fields.
    # Note: If we updated render_budget_status to take MonthlyReportData, we'd update it here.
    # For now, we pass the data from the DTO.

    forecast_dict = None
    if data.forecast:
        forecast_dict = {
            "avg_per_day": data.forecast.avg_per_day,
            "projected_total": data.forecast.projected_total,
            "projected_overage": data.forecast.projected_overage,
        }

    console.print(
        render_budget_status(
            budget=data.budget,
            total_spent=data.total_spent,
            month_name=data.month_name,
            target_year=data.target_year,
            forecast_data=forecast_dict,
        )
    )


if __name__ == "__main__":
    app()
