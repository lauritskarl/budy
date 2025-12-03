import calendar
from typing import Annotated, Optional

from rich.console import Console
from rich.prompt import Confirm
from rich.table import Table
from sqlmodel import Session, select
from typer import Option, Typer

from budy.constants import MAX_YEAR, MIN_YEAR
from budy.database import engine
from budy.models import Budget
from budy.services import suggest_budget_amount
from budy.views import render_success, render_warning

app = Typer(no_args_is_help=True)
console = Console()


@app.command(name="generate")
@app.command(name="gen", hidden=True)
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
            # "-y",
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

    suggestions = []

    with Session(engine) as session:
        # Pre-fetch existing budgets to avoid duplicates/check overwrites
        existing_budgets = session.exec(
            select(Budget).where(Budget.target_year == target_year)
        ).all()
        existing_map = {b.target_month: b for b in existing_budgets}

        for month in range(1, 13):
            month_name = calendar.month_name[month]

            # Skip if exists and not forcing
            if month in existing_map and not force:
                continue

            suggested_amount = suggest_budget_amount(session, month, target_year)

            # If we have no data, we might not want to set a $0 budget unless explicit.
            # However, for "auto-populate", setting $0 (No Limit/Tracking only) or
            # skipping might be preferred. Let's skip pure 0s to keep it clean,
            # unless the user wants to see them.
            if suggested_amount > 0:
                suggestions.append(
                    {
                        "month": month,
                        "month_name": month_name,
                        "amount": suggested_amount,
                        "existing": existing_map.get(month),
                    }
                )

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
            current_str = "-"
            if item["existing"]:
                current_str = f"${item['existing'].amount / 100:,.2f}"

            table.add_row(
                item["month_name"], current_str, f"${item['amount'] / 100:,.2f}"
            )

        console.print(table)

        if not yes and not Confirm.ask("Save these budgets?"):
            console.print("[dim]Operation cancelled.[/]")
            return

        # Save
        count = 0
        for item in suggestions:
            month = item["month"]
            amount = item["amount"]

            if item["existing"]:
                # Update
                item["existing"].amount = amount
                session.add(item["existing"])
            else:
                # Create
                new_budget = Budget(
                    target_year=target_year, target_month=month, amount=amount
                )
                session.add(new_budget)
            count += 1

        session.commit()
        console.print(render_success(f"Successfully saved {count} budgets."))


if __name__ == "__main__":
    app()
