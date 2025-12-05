from datetime import date
from typing import Annotated, Optional

from rich.console import Console
from sqlmodel import Session
from typer import Exit, Option, Typer, confirm

from budy.constants import MAX_YEAR, MIN_YEAR
from budy.database import engine
from budy.services.budget import get_budget, upsert_budget
from budy.views import render_warning

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
            min=MIN_YEAR,
            max=MAX_YEAR,
            help="Target year.",
        ),
    ] = None,
) -> None:
    """Add a new budget to the database."""
    today = date.today()
    target_month = month or today.month
    target_year = year or today.year

    with Session(engine) as session:
        existing = get_budget(session, target_month, target_year)

        if existing:
            console.print(
                render_warning(
                    f"Budget for {target_month}/{target_year} already exists."
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
        f"set to [green]${budget.amount / 100:,.2f}[/]"
    )


if __name__ == "__main__":
    app()
