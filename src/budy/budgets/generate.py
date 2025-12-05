from datetime import date
from typing import Annotated, Optional

from rich.console import Console
from rich.prompt import Confirm
from sqlmodel import Session
from typer import Option, Typer

from budy.constants import MAX_YEAR, MIN_YEAR
from budy.database import engine
from budy.services.budget import (
    generate_budgets_suggestions,
    save_budget_suggestions,
)
from budy.views import render_budget_preview, render_success, render_warning

app = Typer(no_args_is_help=True)
console = Console()


@app.command(name="generate")
def generate_budgets(
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
        console.print(render_warning(f"No suggestions found for {target_year}."))
        return

    console.print(render_budget_preview(suggestions, target_year))

    if not auto_approve and not Confirm.ask("Save these budgets?"):
        console.print("[dim]Operation cancelled.[/]")
        return

    with Session(engine) as session:
        count = save_budget_suggestions(session=session, suggestions=suggestions)

    console.print(render_success(f"Successfully saved {count} budgets."))


if __name__ == "__main__":
    app()
