from datetime import date
from typing import Annotated, Optional

from rich.console import Console
from sqlmodel import Session
from typer import Argument, Option, Typer

from budy.config import settings
from budy.database import engine
from budy.services.report import (
    generate_monthly_report_data,
    get_top_payees,
    get_volatility_report_data,
    get_weekday_report_data,
    get_yearly_report_data,
)
from budy.services.transaction import search_transactions
from budy.views.budget import (
    render_budget_status,
)
from budy.views.messages import (
    render_warning,
)
from budy.views.report import (
    render_payee_ranking,
    render_search_results,
    render_volatility_report,
    render_weekday_report,
    render_yearly_report,
)

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
        Option(
            "--year",
            "-y",
            min=settings.min_year,
            max=settings.max_year,
            help="Target year.",
        ),
    ] = None,
) -> None:
    """Show the budget status report for a specific month."""
    today = date.today()
    target_month = month or today.month
    target_year = year or today.year

    with Session(engine) as session:
        data = generate_monthly_report_data(
            session=session, target_month=target_month, target_year=target_year
        )

    if not data.budget:
        console.print(
            render_warning(
                message=f"No budget found for {data.month_name} {data.target_year}.\n"
                f"Use [bold]budy budgets add[/bold] to set one first."
            )
        )
        return

    console.print(render_budget_status(data=data))


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
        results = search_transactions(session=session, query=query, limit=limit)

    if not results:
        console.print(
            render_warning(message=f"No transactions found matching '{query}'.")
        )
        return

    console.print(render_search_results(results=results, query=query, limit=limit))


@app.command(name="payees")
def show_top_payees(
    year: Annotated[
        Optional[int],
        Option(
            "--year",
            "-y",
            min=settings.min_year,
            max=settings.max_year,
            help="Target year.",
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
    """Rank payees by total spending or frequency."""
    with Session(engine) as session:
        top_payees = get_top_payees(
            session=session, year=year, limit=limit, by_count=by_count
        )

    if not top_payees:
        console.print(render_warning(message="No transactions found."))
        return

    title = "Top Payees by Frequency" if by_count else "Top Payees by Amount"
    console.print(render_payee_ranking(payees=top_payees, title=title))


@app.command(name="volatility")
def show_volatility_report(
    year: Annotated[
        Optional[int],
        Option(
            "--year",
            "-y",
            min=settings.min_year,
            max=settings.max_year,
            help="Target year.",
        ),
    ] = None,
) -> None:
    """Analyze spending volatility and outliers."""
    with Session(engine) as session:
        data = get_volatility_report_data(session=session, year=year)

    if not data:
        console.print(render_warning(message="No transactions found."))
        return

    console.print(render_volatility_report(data=data, year=year))


@app.command(name="weekday")
def show_weekday_report() -> None:
    """Analyze spending habits by day of the week."""
    with Session(engine) as session:
        report_data = get_weekday_report_data(session=session)

    if not report_data:
        console.print(render_warning(message="No transactions found to analyze."))
        return

    console.print(render_weekday_report(report_data=report_data))


@app.command(name="year")
def show_yearly_report(
    year: Annotated[
        Optional[int],
        Option(
            "--year",
            "-y",
            min=settings.min_year,
            max=settings.max_year,
            help="Target year.",
        ),
    ] = None,
):
    """Show the budget status report for a specific year."""
    target_year = year or date.today().year

    with Session(engine) as session:
        monthly_reports = get_yearly_report_data(session=session, year=target_year)

    console.print(f"\n[bold underline]Yearly Overview: {target_year}[/]\n")
    console.print(
        render_yearly_report(monthly_reports=monthly_reports, year=target_year)
    )


@app.callback()
def callback():
    """View financial insights."""
    ...


if __name__ == "__main__":
    app()
