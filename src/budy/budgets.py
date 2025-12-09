from datetime import date
from typing import Annotated, Optional

from rich.console import Console
from rich.prompt import Confirm
from sqlmodel import Session
from typer import Exit, Option, Typer, confirm

from budy.config import settings
from budy.database import engine
from budy.services.budget import (
    generate_budgets_suggestions,
    get_budget,
    get_budgets,
    save_budget_suggestions,
    upsert_budget,
)
from budy.views.budget import (
    render_budget_list,
    render_budget_preview,
)
from budy.views.messages import (
    render_success,
    render_warning,
)

app = Typer(no_args_is_help=True)
console = Console()


@app.command(name="add")
def create_budget(
    amount: Annotated[
        float,
        Option(
            "--amount",
            "-a",
            min=1,
            max=9999999,
            prompt=True,
            help="Target amount.",
        ),
    ],
    month: Annotated[
        Optional[int],
        Option(
            "--month",
            "-m",
            min=1,
            max=12,
            help="Target month.",
        ),
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
    """Add a new budget to the database."""
    today = date.today()
    target_month = month or today.month
    target_year = year or today.year

    with Session(engine) as session:
        existing = get_budget(
            session=session, target_month=target_month, target_year=target_year
        )

        if existing:
            console.print(
                render_warning(
                    message=f"Budget for {target_month}/{target_year} already exists."
                )
            )
            if not confirm("Overwrite?"):
                console.print("[dim]Operation cancelled.[/]")
                raise Exit(code=0)

        budget = upsert_budget(
            session=session,
            amount=amount,
            target_month=target_month,
            target_year=target_year,
        )

    console.print(
        f"[green]✓ Saved![/] Budget for [bold]{target_month}/{target_year}[/] "
        f"set to [green]{settings.currency_symbol}{budget.amount / 100:,.2f}[/]"
    )


@app.command(name="list")
def read_budgets(
    target_year: Annotated[
        int,
        Option("--year", "-y", help="Filter by year."),
    ] = date.today().year,
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
    ] = 12,
) -> None:
    """Display monthly budgets in a table."""
    with Session(engine) as session:
        budgets = get_budgets(
            session=session,
            target_year=target_year,
            offset=offset,
            limit=limit,
        )

    if not budgets:
        console.print(render_warning(message=f"No budgets found for {target_year}."))
        return
    console.print(render_budget_list(budgets=budgets, target_year=target_year))

    # TODO:
    # indicate pagination visually so user knows if there is more hidden data


@app.command(name="generate")
def generate_budgets(
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
    force: Annotated[
        bool,
        Option(
            "--force",
            "-f",
            help="Overwrite existing budgets without asking.",
        ),
    ] = False,
    auto_approve: Annotated[
        bool,
        Option(
            "--yes",
            help="Skip confirmation prompt.",
        ),
    ] = False,
) -> None:
    """
    Auto-generate monthly budgets based on historical transaction data.
    """
    target_year = year or date.today().year

    console.print(
        f"Analyzing spending history to generate budgets for [bold]{target_year}[/]..."
    )

    with Session(engine) as session:
        suggestions = generate_budgets_suggestions(
            session=session, target_year=target_year, force=force
        )

    if not suggestions:
        console.print(
            render_warning(message=f"No suggestions found for {target_year}.")
        )
        return

    console.print(render_budget_preview(suggestions=suggestions, year=target_year))

    if not auto_approve and not Confirm.ask("Save these budgets?"):
        console.print("[dim]Operation cancelled.[/]")
        return

    with Session(engine) as session:
        count = save_budget_suggestions(session=session, suggestions=suggestions)

    console.print(render_success(message=f"Successfully saved {count} budgets."))


@app.callback()
def callback():
    """Set and manage monthly targets."""
    ...


if __name__ == "__main__":
    app()
