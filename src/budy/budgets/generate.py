from typing import Annotated, Optional

from rich.console import Console
from rich.prompt import Confirm
from rich.table import Table
from typer import Option, Typer

from budy.constants import MAX_YEAR, MIN_YEAR
from budy.services.budget import (
    generate_budgets_suggestions,
    save_budget_suggestions,
)
from budy.views import render_success, render_warning

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
            help="The year to generate budgets for.",
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
    yes: Annotated[
        bool,
        Option(
            "--yes",
            help="Automatically confirm saving suggestions.",
        ),
    ] = False,
) -> None:
    """
    Auto-generate monthly budgets based on historical transaction data.
    Calculates suggestions using recent spending trends and seasonal history.
    """
    from datetime import date

    target_year = year or date.today().year

    console.print(
        f"Analyzing spending history to generate budgets for [bold]{target_year}[/]..."
    )

    suggestions = generate_budgets_suggestions(target_year, force)

    if not suggestions:
        console.print(
            render_warning(
                f"No suggestions could be calculated for {target_year} (or budgets already exist)."
            )
        )
        return

    # Preview Table
    table = Table(title=f"Suggested Budgets ({target_year})")
    table.add_column("Month", style="cyan")
    table.add_column("Current", justify="right", style="dim")
    table.add_column("Suggested", justify="right", style="green")

    for item in suggestions:
        item["year"] = target_year
        current_str = "-"
        if item["existing"]:
            current_str = f"${item['existing'].amount / 100:,.2f}"

        table.add_row(item["month_name"], current_str, f"${item['amount'] / 100:,.2f}")

    console.print(table)

    if not yes and not Confirm.ask("Save these budgets?"):
        console.print("[dim]Operation cancelled.[/]")
        return

    count = save_budget_suggestions(suggestions)
    console.print(render_success(f"Successfully saved {count} budgets."))


if __name__ == "__main__":
    app()
