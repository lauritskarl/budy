from rich.console import Console
from rich.table import Table
from typer import Typer

from budy.services.report import get_weekday_report_data
from budy.views import render_warning

app = Typer(no_args_is_help=True)
console = Console()


@app.command(name="weekday")
def show_weekday_report() -> None:
    """
    Analyze spending habits by day of the week.
    Shows which days you statistically spend the most money on.
    """
    report_data = get_weekday_report_data()

    if not report_data:
        console.print(render_warning("No transactions found to analyze."))
        return

    total_all_spent = sum(day["total_amount"] for day in report_data)
    total_all_count = sum(day["count"] for day in report_data)

    table = Table(title="Spending Habits by Day of Week", show_footer=True)
    table.add_column("Day", style="cyan", footer="TOTAL")
    table.add_column("Avg Transaction", justify="right", style="green")
    table.add_column(
        "Transaction Count",
        justify="right",
        style="dim",
        footer=str(total_all_count),
    )
    table.add_column(
        "Total Spent",
        justify="right",
        style="bold",
        footer=f"${total_all_spent / 100:,.2f}",
    )

    for day in report_data:
        if day["count"] == 0:
            table.add_row(day["day_name"], "-", "0", "-")
            continue

        table.add_row(
            day["day_name"],
            f"${day['avg_amount'] / 100:,.2f}",
            str(day["count"]),
            f"${day['total_amount'] / 100:,.2f}",
        )

    console.print(table)
