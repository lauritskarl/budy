from datetime import date
from typing import Annotated, Optional

from rich.console import Console
from typer import Exit, Option, Typer, confirm

from budy.constants import MAX_YEAR, MIN_YEAR
from budy.services.budget import add_or_update_budget
from budy.views import render_warning

app = Typer(no_args_is_help=True)
console = Console()


@app.command(name="add")
def create_budget(
    target_amount: Annotated[
        float,
        Option(
            "--amount",
            "-a",
            min=1,
            max=9999999,
            prompt=True,
            help="Set the budget target amount.",
        ),
    ],
    target_month: Annotated[
        Optional[int],
        Option(
            "--month",
            "-m",
            min=1,
            max=12,
            help="Set the budget target month.",
        ),
    ] = None,
    target_year: Annotated[
        Optional[int],
        Option(
            "--year",
            "-y",
            min=MIN_YEAR,
            max=MAX_YEAR,
            help="Set the budget target year.",
        ),
    ] = None,
) -> None:
    """Add a new budget to the database."""
    current_date = date.today()
    final_target_month = target_month if target_month else current_date.month
    final_target_year = target_year if target_year else current_date.year

    def confirmation_callback(message: str) -> bool:
        console.print(render_warning(message))
        return confirm("Overwrite?")

    result = add_or_update_budget(
        target_amount=target_amount,
        target_month=final_target_month,
        target_year=final_target_year,
        confirmation_callback=confirmation_callback,
    )

    if result["action"] == "cancelled":
        print("[dim]Operation cancelled.[/]")
        raise Exit(code=0)

    month_name = result["month_name"]
    year = result["year"]
    new_amount_display = result["new_amount"] / 100.0

    if result["action"] == "updated":
        old_amount_display = result["old_amount"] / 100.0
        print(
            f"[green]✓ Updated![/] {month_name} {year}: "
            f"[strike dim]${old_amount_display:,.2f}[/] -> [bold green]${new_amount_display:,.2f}[/]"
        )
    elif result["action"] == "created":
        print(
            f"[green]✓ Added![/] Budget for [bold]{month_name} {year}[/] set to [green]${new_amount_display:,.2f}[/]"
        )


if __name__ == "__main__":
    app()
